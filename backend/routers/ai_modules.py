"""
Router: AI-Powered Modules (Repair Intel + Marketing)
Uses Claude API — requires ANTHROPIC_API_KEY env variable.
"""
import csv
import io
import json
import os
import sys
import re
import hashlib
import time
from typing import Optional

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

# Import static knowledge base
_BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)
from knowledge_base import find_vehicle, vehicle_context, price_context, VEHICLES as _STATIC_VEHICLES
from marketing_templates import (find_social, find_cta, find_promo,
                                  _fill, _hashtag, SOCIAL, CTA, PROMO,
                                  SOCIAL_SERVICES, CTA_GOALS, PROMO_SERVICES)

# ── Persistent paths ─────────────────────────────────────────────────────────
_LEARNED_PATH = os.path.join(_DATA_DIR, "learned_vehicles.json")
_PRICES_PATH  = os.path.join(_DATA_DIR, "parts_prices.json")

def _load_learned() -> dict:
    try:
        if os.path.exists(_LEARNED_PATH):
            with open(_LEARNED_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_learned(key: str, data: dict):
    learned = _load_learned()
    learned[key] = data
    os.makedirs(os.path.dirname(_LEARNED_PATH), exist_ok=True)
    with open(_LEARNED_PATH, "w", encoding="utf-8") as f:
        json.dump(learned, f, indent=2)

def _load_shop_prices() -> list:
    try:
        if os.path.exists(_PRICES_PATH):
            with open(_PRICES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def _prices_context() -> str:
    """Shop-specific prices if uploaded, else fall back to generic KB ranges."""
    rows = _load_shop_prices()
    if rows:
        items = []
        for r in rows[:60]:                        # cap at 60 to stay token-lean
            svc   = r.get("service", "")
            price = r.get("price", "")
            pn    = r.get("part_number", "")
            if svc:
                label = svc
                if price:  label += f": ${price}"
                if pn:     label += f" (P/N {pn})"
                items.append(label)
        if items:
            return "SHOP PRICE LIST: " + " | ".join(items)
    return f"PRICE GUIDE (general ranges): {price_context()}"


def _find_vehicle_any(query: str) -> dict | None:
    """Check static KB first, then learned vehicles."""
    v = find_vehicle(query)
    if v:
        return v
    q = query.lower()
    for key, data in _load_learned().items():
        if all(p in q for p in key.split()):
            return data
    return None

# ── Simple response cache (saves credits on repeated identical queries) ───────
# Stores {cache_key: (response_text, timestamp)}
_CACHE: dict = {}
_CACHE_TTL = 60 * 60  # 1 hour

def _cache_get(key: str):
    entry = _CACHE.get(key)
    if entry and (time.time() - entry[1]) < _CACHE_TTL:
        return entry[0]
    return None

def _cache_set(key: str, value: str):
    # Keep cache from growing unbounded — evict oldest if over 200 entries
    if len(_CACHE) >= 200:
        oldest = min(_CACHE, key=lambda k: _CACHE[k][1])
        del _CACHE[oldest]
    _CACHE[key] = (value, time.time())

def _cache_key(system: str, user: str) -> str:
    return hashlib.md5(f"{system}||{user}".encode()).hexdigest()

# Max characters accepted from user input (prevents token bloat)
MAX_INPUT_CHARS = 800

_DATA_DIR = "/data" if os.path.isdir("/data") else os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)
PROFILE_PATH = os.path.join(_DATA_DIR, "shop_profile.json")

router = APIRouter()


# ── Helpers ─────────────────────────────────────────────────────────────────

def _load_profile() -> dict:
    try:
        if os.path.exists(PROFILE_PATH):
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _get_client():
    try:
        import anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return None, "AI features are not yet enabled for this platform. Please contact support."
        return anthropic.Anthropic(api_key=api_key), None
    except ImportError:
        return None, "The 'anthropic' package is not installed."


def _shop_ctx(profile: dict) -> str:
    parts = [f"Shop: {profile.get('shop_name', 'Independent Auto Repair Shop')}"]
    for k, label in [("owner_name", "Owner"), ("location", "Location"),
                     ("phone", "Phone"), ("hours", "Hours"), ("tagline", "Tagline"),
                     ("tone", "Tone")]:
        if profile.get(k):
            parts.append(f"{label}: {profile[k]}")
    svcs = profile.get("services", [])
    if svcs:
        parts.append(f"Services: {', '.join(svcs) if isinstance(svcs, list) else svcs}")
    return " | ".join(parts)


def _call_claude(client, system: str, user: str, max_tokens: int = 900) -> tuple:
    # Truncate user input to cap token spend
    user = user[:MAX_INPUT_CHARS]

    # Return cached response if available
    key = _cache_key(system, user)
    cached = _cache_get(key)
    if cached:
        return cached, None

    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = msg.content[0].text
        _cache_set(key, text)
        return text, None
    except Exception as e:
        err = str(e)
        if "credit balance is too low" in err or "insufficient_quota" in err:
            return None, "AI credits have been exhausted. Please contact support to restore service."
        if "invalid_api_key" in err or "authentication_error" in err:
            return None, "AI service is not configured correctly. Please contact support."
        if "overloaded" in err:
            return None, "AI service is temporarily overloaded. Please try again in a moment."
        return None, "AI service error. Please try again."


def _ok(text: str, key: str):
    return {"success": True, "output": text, "files": [],
            "content": {f"{key}.txt": text}, "error": None}

def _err(msg: str):
    return {"success": False, "output": "", "files": [], "content": {}, "error": msg}


# ── Knowledge Base endpoints ─────────────────────────────────────────────────

@router.get("/knowledge-base/learned")
def get_learned_vehicles():
    """Return all auto-learned vehicles saved from AI queries."""
    return {"success": True, "vehicles": _load_learned()}

@router.delete("/knowledge-base/learned/{key}")
def delete_learned_vehicle(key: str):
    """Remove a learned vehicle entry (key = url-encoded 'make model')."""
    learned = _load_learned()
    norm = key.replace("-", " ").lower()
    if norm in learned:
        del learned[norm]
        os.makedirs(os.path.dirname(_LEARNED_PATH), exist_ok=True)
        with open(_LEARNED_PATH, "w", encoding="utf-8") as f:
            json.dump(learned, f, indent=2)
        return {"success": True}
    return {"success": False, "error": "Vehicle not found"}


@router.get("/knowledge-base/parts-prices")
def get_parts_prices():
    """Return the shop's uploaded parts & prices list."""
    rows = _load_shop_prices()
    return {"success": True, "rows": rows, "count": len(rows)}


@router.post("/knowledge-base/parts-prices/upload")
async def upload_parts_prices(file: UploadFile = File(...)):
    """Accept a CSV upload, parse it, and save to /data/parts_prices.json."""
    try:
        raw = await file.read()
        text = raw.decode("utf-8-sig")          # strip BOM if present
        reader = csv.DictReader(io.StringIO(text))
        rows = []
        for row in reader:
            norm = {k.lower().strip().replace(" ", "_"): (v or "").strip()
                    for k, v in row.items()}
            service = (norm.get("service") or norm.get("name") or
                       norm.get("description") or norm.get("item") or "").strip()
            if not service:
                continue
            rows.append({
                "service":     service,
                "price":       norm.get("price") or norm.get("total") or norm.get("amount") or "",
                "part_number": norm.get("part_number") or norm.get("part#") or norm.get("sku") or "",
                "labor_hours": norm.get("labor_hours") or norm.get("labor") or norm.get("hours") or "",
                "part_cost":   norm.get("part_cost") or norm.get("parts_cost") or "",
                "notes":       norm.get("notes") or norm.get("note") or "",
            })
        os.makedirs(os.path.dirname(_PRICES_PATH), exist_ok=True)
        with open(_PRICES_PATH, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
        return {"success": True, "count": len(rows),
                "message": f"{len(rows)} items loaded from {file.filename}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/knowledge-base/marketing-templates")
def get_marketing_templates():
    """Return available template service types for display in the KB panel."""
    return {
        "success": True,
        "social":  SOCIAL_SERVICES,
        "cta":     CTA_GOALS,
        "promo":   PROMO_SERVICES,
    }


@router.delete("/knowledge-base/parts-prices")
def clear_parts_prices():
    """Remove the uploaded parts & prices list."""
    try:
        if os.path.exists(_PRICES_PATH):
            os.remove(_PRICES_PATH)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Request models ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: Optional[str] = ""

class SocialMediaRequest(BaseModel):
    platform: Optional[str] = "all"
    service_type: Optional[str] = ""
    tone: Optional[str] = "professional"
    promo: Optional[str] = ""

class CTACopyRequest(BaseModel):
    goal: Optional[str] = "book"
    service_type: Optional[str] = ""
    urgency: Optional[str] = "medium"
    format: Optional[str] = "all"

class PromoRequest(BaseModel):
    offer: Optional[str] = ""
    service_type: Optional[str] = ""
    expiry: Optional[str] = ""
    channels: Optional[str] = "all"

class BlogRequest(BaseModel):
    topic: Optional[str] = ""
    audience: Optional[str] = "car owners"
    keywords: Optional[str] = ""
    length: Optional[str] = "1000"


# ── Repair Intel endpoints ───────────────────────────────────────────────────

@router.post("/repair-auto/generate")
def repair_auto(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    q = body.query or ""
    veh = _find_vehicle_any(q)
    kb = f" VEHICLE SPECS FROM KB: {vehicle_context(veh)}." if veh else ""
    prices = f" {_prices_context()}."
    system = f"Auto repair estimator. Shop: {_shop_ctx(profile)}.{kb}{prices} Reply with 4 sections: DIAGNOSIS SUMMARY, RECOMMENDED SERVICES (part, cost, labor hrs at $120/hr), CUSTOMER EXPLANATION (plain language, risk of delay), URGENCY LEVEL (Safety Critical/High/Medium/Low + one reason). Use KB specs — do not fabricate part numbers."
    text, err = _call_claude(client, system, q or "Describe the vehicle (year/make/model/mileage) and complaint.")
    if err: return _err(err)
    return _ok(text, "repair_auto_estimate")


_SPEC_SCHEMA = '{"name":"Make Model (years)","engines":["engine string"],"oil":"spec","oil_cap":"X qt","coolant":"type","spark_plug":"part number","torque":{"Lug Nuts":"X ft-lb","Drain Plug":"X ft-lb"},"intervals":{"Oil Change":"X,000 mi"},"known_issues":["issue"]}'

@router.post("/componentcare/query")
def componentcare(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    q = body.query or ""
    veh = _find_vehicle_any(q)

    if veh:
        # Known vehicle — inject exact specs, short focused answer
        kb = f" VERIFIED SPECS: {vehicle_context(veh)}. Use these exact figures."
        system = f"Vehicle technical assistant. Shop: {_shop_ctx(profile)}.{kb} Answer concisely with headers and bullets."
        text, err = _call_claude(client, system, q or "What vehicle and question can I help with?")
    else:
        # Unknown vehicle — answer AND silently extract specs to grow the KB
        system = (
            f"Vehicle technical assistant. Shop: {_shop_ctx(profile)}. "
            "Answer the question with headers and bullets. "
            "If a specific vehicle (make/model/year) is mentioned, also append its specs as JSON "
            f"between <<<SPECS>>> and <<<END>>> tags using this schema: {_SPEC_SCHEMA}. "
            "Only include fields you are confident about. "
            "If no specific vehicle is mentioned, omit the JSON block entirely."
        )
        text, err = _call_claude(client, system, q or "What vehicle and question can I help with?", max_tokens=1100)
        if not err and text:
            match = re.search(r'<<<SPECS>>>(.*?)<<<END>>>', text, re.DOTALL)
            if match:
                try:
                    specs = json.loads(match.group(1).strip())
                    name = specs.get("name", "")
                    parts = name.replace("(", "").replace(")", "").split()
                    if len(parts) >= 2:
                        key = f"{parts[0]} {parts[1]}".lower()
                        if key not in _STATIC_VEHICLES:   # don't overwrite static KB
                            _save_learned(key, specs)
                except Exception:
                    pass
                # Strip the JSON block from the displayed response
                text = re.sub(r'\s*<<<SPECS>>>.*?<<<END>>>', '', text, flags=re.DOTALL).strip()

    if err: return _err(err)
    return _ok(text, "componentcare_answer")


@router.post("/fleetmaint/generate")
def fleetmaint(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    q = body.query or ""
    veh = _find_vehicle_any(q)
    kb = f" VEHICLE SPECS: {vehicle_context(veh)}." if veh else ""
    prices = f" {_prices_context()}."
    system = f"Fleet maintenance advisor. Shop: {_shop_ctx(profile)}.{kb}{prices} Provide: PREDICTIVE ALERTS, 6-MONTH SCHEDULE (month-by-month), COST FORECAST, PRIORITY ORDER (Safety Critical→Revenue→Reliability→Convenience)."
    text, err = _call_claude(client, system, q or "Describe the vehicle or fleet (year/make/model/mileage/usage).")
    if err: return _err(err)
    return _ok(text, "fleet_maintenance_plan")


@router.post("/prev-advisor/generate")
def prev_advisor(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    q = body.query or ""
    veh = _find_vehicle_any(q)
    kb = f" OEM INTERVALS FROM KB: {vehicle_context(veh)}." if veh else ""
    system = f"Preventive maintenance advisor. Shop: {_shop_ctx(profile)}.{kb} Output: IMMEDIATE (overdue/urgent), UPCOMING (due within 3k mi/3 months), LONG-TERM (6-12 months), INSPECTION CHECKLIST. Flag severe-duty conditions."
    text, err = _call_claude(client, system, q or "Describe the vehicle (year/make/model/mileage) and service history.")
    if err: return _err(err)
    return _ok(text, "preventive_maintenance_checklist")


@router.post("/enviromaint/generate")
def enviromaint(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    q = body.query or ""
    veh = _find_vehicle_any(q)
    kb = f" VEHICLE SPECS: {vehicle_context(veh)}." if veh else ""
    system = f"Climate-aware maintenance advisor. Shop: {_shop_ctx(profile)}.{kb} Provide: ENVIRONMENT IMPACT (how climate stresses this vehicle), ADJUSTED INTERVALS (OEM modified for climate), SEASONAL CHECKLIST, COMMON CLIMATE FAILURES."
    text, err = _call_claude(client, system, q or "Describe the vehicle and environment (city/state, climate, driving conditions).")
    if err: return _err(err)
    return _ok(text, "climate_maintenance_plan")


# ── Marketing endpoints ──────────────────────────────────────────────────────

@router.post("/social-media/generate")
def social_media(body: SocialMediaRequest):
    profile = _load_profile()
    shop_name = profile.get("shop_name", "our shop")
    phone     = profile.get("phone", "")
    tag       = _hashtag(shop_name)
    promo_line = f"💥 {body.promo}\n\n" if body.promo else ""
    kw = dict(shop_name=shop_name, phone=phone, hashtag=tag, promo_line=promo_line)

    # ── Try template first ──────────────────────────────────────────────────
    tmpl = find_social(body.service_type or "") or SOCIAL["general"]
    want = (body.platform or "all").lower()
    parts = []
    if want in ("all", "instagram")       and "instagram" in tmpl:
        parts.append(f"📸 INSTAGRAM\n\n{_fill(tmpl['instagram'], **kw)}")
    if want in ("all", "facebook")        and "facebook"  in tmpl:
        parts.append(f"👍 FACEBOOK\n\n{_fill(tmpl['facebook'], **kw)}")
    if want in ("all", "google", "google business") and "google" in tmpl:
        parts.append(f"🔍 GOOGLE BUSINESS\n\n{_fill(tmpl['google'], **kw)}")
    if parts:
        return _ok("\n\n─────────────────────\n\n".join(parts), "social_media_posts")

    # ── Fall back to AI for unusual platform or highly custom request ───────
    client, err = _get_client()
    if err: return _err(err)
    platforms = body.platform if body.platform != "all" else "Facebook, Instagram, Google Business"
    system = (f"Social media copywriter for auto repair shop. Shop: {_shop_ctx(profile)}. "
              f"Tone: {body.tone}. Local, authentic, never corporate. "
              f"Include shop name ({shop_name}) and phone ({phone}) naturally. "
              "Instagram: <150 words + hashtags. Facebook: <200 words. Google Business: 1-2 sentences. Label each platform.")
    user = f"Platform(s): {platforms}\nService/Topic: {body.service_type or 'general update'}" + (f"\nPromo: {body.promo}" if body.promo else "")
    text, err = _call_claude(client, system, user)
    if err: return _err(err)
    return _ok(text, "social_media_posts")


@router.post("/cta-copy/generate")
def cta_copy(body: CTACopyRequest):
    profile = _load_profile()
    shop_name = profile.get("shop_name", "us")
    phone     = profile.get("phone", "")
    kw = dict(shop_name=shop_name, phone=phone, service=body.service_type or "auto repair")

    # ── Try template first ──────────────────────────────────────────────────
    tmpl = find_cta(body.goal or "") or CTA["general"]
    want = (body.format or "all").lower()
    parts = []
    if want in ("all", "button", "button text"):
        parts.append(f"BUTTON TEXT\n{_fill(tmpl['button'], **kw)}")
    if want in ("all", "headline", "page headline"):
        parts.append(f"PAGE HEADLINE\n{_fill(tmpl['headline'], **kw)}")
    if want in ("all", "email", "email cta", "email cta line"):
        parts.append(f"EMAIL CTA\n{_fill(tmpl['email'], **kw)}")
    if want in ("all", "sms", "sms cta"):
        parts.append(f"SMS CTA\n{_fill(tmpl['sms'], **kw)}")
    if parts:
        return _ok("\n\n".join(parts), "cta_copy")

    # ── Fall back to AI for custom format requests ──────────────────────────
    client, err = _get_client()
    if err: return _err(err)
    formats = body.format if body.format != "all" else "Button text, Page headline, Email CTA, SMS CTA (<30 chars)"
    system = (f"Conversion copywriter for auto shop. Shop: {_shop_ctx(profile)}. "
              f"Direct, action-oriented CTAs. Use shop name ({shop_name}) and phone ({phone}). Label each format.")
    user = f"Formats: {formats}\nService: {body.service_type or 'auto repair'}\nGoal: {body.goal}\nUrgency: {body.urgency}"
    text, err = _call_claude(client, system, user)
    if err: return _err(err)
    return _ok(text, "cta_copy")


@router.post("/promo-builder/generate")
def promo_builder(body: PromoRequest):
    profile = _load_profile()
    shop_name = profile.get("shop_name", "our shop")
    phone     = profile.get("phone", "")
    offer     = body.offer or "special offer"
    expiry    = body.expiry or "limited time"
    kw = dict(shop_name=shop_name, phone=phone, offer=offer, expiry=expiry)

    # ── Try template first (promo always has a general fallback) ────────────
    tmpl = find_promo(body.service_type or "", body.offer or "") or PROMO["general"]
    want = (body.channels or "all").lower()
    parts = []
    if want in ("all", "sms"):
        parts.append(f"SMS (under 160 chars)\n{_fill(tmpl['sms'], **kw)}")
    if want in ("all", "email"):
        subj = _fill(tmpl["email_subject"], **kw)
        body_text = _fill(tmpl["email_body"], **kw)
        parts.append(f"EMAIL\nSubject: {subj}\n\n{body_text}")
    if want in ("all", "social", "social media"):
        parts.append(f"SOCIAL MEDIA\n{_fill(tmpl['social'], **kw)}")
    if parts:
        return _ok("\n\n─────────────────────\n\n".join(parts), "promo_content")

    # ── Fall back to AI for unusual channel combos ──────────────────────────
    client, err = _get_client()
    if err: return _err(err)
    channels_label = body.channels if body.channels != "all" else "SMS (<160 chars), Email (subject + body), Social Media caption"
    system = (f"Promo copywriter for auto shop. Shop: {_shop_ctx(profile)}. "
              f"Urgency without pushiness. Always include: {shop_name}, {phone}, expiry. Label each channel.")
    user = f"Offer: {offer}\nService: {body.service_type or 'general'}\nExpiry: {expiry}\nChannels: {channels_label}"
    text, err = _call_claude(client, system, user)
    if err: return _err(err)
    return _ok(text, "promo_content")


@router.post("/blog-post/generate")
def blog_post(body: BlogRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    shop_name = profile.get("shop_name", "our shop")
    system = f"SEO blog writer for auto shop ({shop_name}). Shop: {_shop_ctx(profile)}. Audience: {body.audience}. Conversational but authoritative. Structure: meta title, meta description, H1, intro, 3 H2 sections, conclusion with soft CTA. No fabricated stats."
    user = f"Write a ~{body.length}-word post: {body.topic or 'auto maintenance tips'}" + (f"\nKeywords: {body.keywords}" if body.keywords else "")
    text, err = _call_claude(client, system, user, max_tokens=2200)
    if err: return _err(err)
    return _ok(text, "blog_post")
