"""
Router: AI-Powered Modules (Repair Intel + Marketing)
Uses Claude API — requires ANTHROPIC_API_KEY env variable.
"""
import json
import os
import hashlib
import time
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

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
    system = f"Auto repair estimator. Shop: {_shop_ctx(profile)}. Given vehicle+complaint, reply with 4 sections: DIAGNOSIS SUMMARY (likely causes), RECOMMENDED SERVICES (part, cost, labor hrs at $120/hr), CUSTOMER EXPLANATION (plain language, risk of delay), URGENCY LEVEL (Safety Critical/High/Medium/Low + one reason). Be specific, no fabricated part numbers."
    text, err = _call_claude(client, system, body.query or "Describe the vehicle (year/make/model/mileage) and complaint.")
    if err: return _err(err)
    return _ok(text, "repair_auto_estimate")


@router.post("/componentcare/query")
def componentcare(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    system = f"Vehicle technical assistant for an auto shop. Shop: {_shop_ctx(profile)}. Answer questions on maintenance intervals, torque specs (always include ft-lb/in-lb), fluid types/capacities, TSBs, diagnostics, OEM vs aftermarket. Always state make/model/year/engine. Use headers and bullets."
    text, err = _call_claude(client, system, body.query or "What vehicle and question can I help with?")
    if err: return _err(err)
    return _ok(text, "componentcare_answer")


@router.post("/fleetmaint/generate")
def fleetmaint(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    system = f"Fleet maintenance advisor. Shop: {_shop_ctx(profile)}. Given vehicle/fleet info, provide: PREDICTIVE ALERTS (overdue/due soon), 6-MONTH SCHEDULE (month-by-month with mileage triggers), COST FORECAST (parts+labor), PRIORITY ORDER (Safety Critical→Revenue→Reliability→Convenience). Be practical."
    text, err = _call_claude(client, system, body.query or "Describe the vehicle or fleet (year/make/model/mileage/usage).")
    if err: return _err(err)
    return _ok(text, "fleet_maintenance_plan")


@router.post("/prev-advisor/generate")
def prev_advisor(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    system = f"Preventive maintenance advisor. Shop: {_shop_ctx(profile)}. Given vehicle info, output: IMMEDIATE (overdue/urgent), UPCOMING (due within 3k miles/3 months), LONG-TERM (6-12 month outlook), INSPECTION CHECKLIST. Use OEM schedules. Flag severe-duty conditions (towing, extreme temps, short trips)."
    text, err = _call_claude(client, system, body.query or "Describe the vehicle (year/make/model/mileage) and service history.")
    if err: return _err(err)
    return _ok(text, "preventive_maintenance_checklist")


@router.post("/enviromaint/generate")
def enviromaint(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    system = f"Climate-aware maintenance advisor. Shop: {_shop_ctx(profile)}. Given vehicle + environment, provide: ENVIRONMENT IMPACT (how climate stresses this vehicle), ADJUSTED INTERVALS (OEM modified for climate), SEASONAL CHECKLIST, COMMON CLIMATE FAILURES."
    text, err = _call_claude(client, system, body.query or "Describe the vehicle and environment (city/state, climate, driving conditions).")
    if err: return _err(err)
    return _ok(text, "climate_maintenance_plan")


# ── Marketing endpoints ──────────────────────────────────────────────────────

@router.post("/social-media/generate")
def social_media(body: SocialMediaRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    shop_name = profile.get("shop_name", "our shop")
    phone = profile.get("phone", "")
    platforms = body.platform if body.platform != "all" else "Facebook, Instagram, Google Business"
    system = f"Social media copywriter for auto repair shop. Shop: {_shop_ctx(profile)}. Tone: {body.tone}. Local, authentic, never corporate. Include shop name ({shop_name}) and phone ({phone}) naturally. Instagram: <150 words + hashtags. Facebook: <200 words. Google Business: 1-2 sentences. Label each platform."
    user = f"Platform(s): {platforms}\nService/Topic: {body.service_type or 'general update'}" + (f"\nPromo: {body.promo}" if body.promo else "")
    text, err = _call_claude(client, system, user)
    if err: return _err(err)
    return _ok(text, "social_media_posts")


@router.post("/cta-copy/generate")
def cta_copy(body: CTACopyRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    shop_name = profile.get("shop_name", "us")
    phone = profile.get("phone", "")
    formats = body.format if body.format != "all" else "Button text, Page headline, Email CTA, SMS CTA (<30 chars)"
    system = f"Conversion copywriter for auto shop. Shop: {_shop_ctx(profile)}. Direct, action-oriented CTAs. Use shop name ({shop_name}) and phone ({phone}). Label each format."
    user = f"Formats: {formats}\nService: {body.service_type or 'auto repair'}\nGoal: {body.goal}\nUrgency: {body.urgency}"
    text, err = _call_claude(client, system, user)
    if err: return _err(err)
    return _ok(text, "cta_copy")


@router.post("/promo-builder/generate")
def promo_builder(body: PromoRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err: return _err(err)
    shop_name = profile.get("shop_name", "our shop")
    phone = profile.get("phone", "")
    channels_label = body.channels if body.channels != "all" else "SMS (<160 chars), Email (subject + body), Social Media caption"
    system = f"Promo copywriter for auto shop. Shop: {_shop_ctx(profile)}. Urgency without pushiness. Always include: {shop_name}, {phone}, expiry. Label each channel."
    user = f"Offer: {body.offer or 'seasonal discount'}\nService: {body.service_type or 'general'}\nExpiry: {body.expiry or 'limited time'}\nChannels: {channels_label}"
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
    text, err = _call_claude(client, system, user, max_tokens=1800)
    if err: return _err(err)
    return _ok(text, "blog_post")
