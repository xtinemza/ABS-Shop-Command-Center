"""
Router: AI-Powered Modules (Repair Intel + Marketing)
Uses Claude API — requires ANTHROPIC_API_KEY env variable.
"""
import json
import os
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

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
            return None, (
                "ANTHROPIC_API_KEY is not set. "
                "Add it in your Render dashboard → Environment → Add Environment Variable."
            )
        return anthropic.Anthropic(api_key=api_key), None
    except ImportError:
        return None, "The 'anthropic' package is not installed. Run: pip install anthropic"


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


def _call_claude(client, system: str, user: str, max_tokens: int = 2048) -> tuple:
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return msg.content[0].text, None
    except Exception as e:
        return None, str(e)


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
    if err:
        return _err(err)
    shop = _shop_ctx(profile)
    system = f"""You are a repair estimation assistant for an independent auto repair shop.
Shop context: {shop}

When given a vehicle and complaint, respond with these clearly labeled sections:

DIAGNOSIS SUMMARY
List the most likely causes based on the symptoms described.

RECOMMENDED SERVICES
For each repair: part name, estimated part cost, labor hours, labor cost (use shop's rate if known, else $120/hr).

CUSTOMER EXPLANATION
Plain-language version the service advisor reads to the customer. Explain the why, the risk of waiting, and the value of fixing it now.

URGENCY LEVEL
Safety Critical / High / Medium / Low — with a one-sentence reason.

Be specific. Use real automotive knowledge. Do not fabricate part numbers."""

    text, err = _call_claude(client, system,
        body.query or "Please describe the vehicle (year, make, model, mileage) and the complaint.")
    if err:
        return _err(err)
    return _ok(text, "repair_auto_estimate")


@router.post("/componentcare/query")
def componentcare(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err:
        return _err(err)
    shop = _shop_ctx(profile)
    system = f"""You are a vehicle technical knowledge assistant for an auto repair shop.
Shop context: {shop}

Answer technical questions about:
- Maintenance intervals and OEM schedules
- Torque specifications (always include units: ft-lb or in-lb)
- Fluid types, capacities, and specifications
- Common TSBs and known failure patterns
- Diagnostic steps and procedures
- OEM vs aftermarket part recommendations

Always specify make, model, year, and engine variant when giving specs.
Format answers with clear headers and bullet points."""

    text, err = _call_claude(client, system,
        body.query or "What vehicle and question can I help with?")
    if err:
        return _err(err)
    return _ok(text, "componentcare_answer")


@router.post("/fleetmaint/generate")
def fleetmaint(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err:
        return _err(err)
    shop = _shop_ctx(profile)
    system = f"""You are a predictive fleet maintenance advisor for an auto repair shop.
Shop context: {shop}

Given vehicle or fleet info, provide:

PREDICTIVE ALERTS
Services likely overdue or due soon based on mileage/usage patterns.

6-MONTH MAINTENANCE SCHEDULE
Month-by-month breakdown of recommended services with estimated mileage triggers.

COST FORECAST
Realistic cost estimates for the period (parts + labor).

PRIORITY ORDER
Rank items: Safety Critical → Revenue Protection → Reliability → Convenience.

Be fleet-management focused and practical."""

    text, err = _call_claude(client, system,
        body.query or "Please describe the vehicle or fleet (year, make, model, mileage, usage).")
    if err:
        return _err(err)
    return _ok(text, "fleet_maintenance_plan")


@router.post("/prev-advisor/generate")
def prev_advisor(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err:
        return _err(err)
    shop = _shop_ctx(profile)
    system = f"""You are a preventive maintenance advisor for an auto repair shop.
Shop context: {shop}

Given vehicle info (make, model, year, mileage, last services), provide:

IMMEDIATE — Overdue or due now (flag as urgent)
UPCOMING — Due within 3,000 miles or 3 months
LONG-TERM OUTLOOK — 6–12 month horizon
TECH INSPECTION CHECKLIST — Items to eyeball at next visit

Use OEM maintenance schedules as baseline. Note if vehicle is in a severe duty environment (towing, extreme temps, short trips)."""

    text, err = _call_claude(client, system,
        body.query or "Please describe the vehicle (year, make, model, mileage) and its service history.")
    if err:
        return _err(err)
    return _ok(text, "preventive_maintenance_checklist")


@router.post("/enviromaint/generate")
def enviromaint(body: QueryRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err:
        return _err(err)
    shop = _shop_ctx(profile)
    system = f"""You are a climate-aware vehicle maintenance advisor for an auto repair shop.
Shop context: {shop}

Given a vehicle and its operating environment, provide:

ENVIRONMENT IMPACT PROFILE
How the specific climate stresses this vehicle type.

ADJUSTED MAINTENANCE INTERVALS
OEM intervals modified for the environment (e.g. more frequent oil changes in desert heat, rust checks in salt states).

SEASONAL CHECKLIST
Specific items to inspect for this region and season.

COMMON CLIMATE FAILURES
Failure patterns common in this environment for this vehicle class."""

    text, err = _call_claude(client, system,
        body.query or "Please describe the vehicle and its environment (city/state, climate, driving conditions).")
    if err:
        return _err(err)
    return _ok(text, "climate_maintenance_plan")


# ── Marketing endpoints ──────────────────────────────────────────────────────

@router.post("/social-media/generate")
def social_media(body: SocialMediaRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err:
        return _err(err)
    shop_name = profile.get("shop_name", "our shop")
    phone = profile.get("phone", "")
    shop = _shop_ctx(profile)
    platforms = body.platform if body.platform != "all" else "Facebook, Instagram, and Google Business"

    system = f"""You are a social media copywriter for an independent auto repair shop.
Shop context: {shop}
Tone: {body.tone}. Write authentic, local, trust-building posts. Never sound corporate.
Always include the shop name ({shop_name}) and phone ({phone}) where natural.
Instagram: under 150 words + hashtags. Facebook: up to 200 words. Google Business: 1-2 sentences."""

    user = f"""Write social media posts for: {platforms}
Service/Topic: {body.service_type or 'general shop update'}
{f"Current promotion: {body.promo}" if body.promo else ""}

Label each platform with a header. Include relevant hashtags at the end of Instagram post."""

    text, err = _call_claude(client, system, user)
    if err:
        return _err(err)
    return _ok(text, "social_media_posts")


@router.post("/cta-copy/generate")
def cta_copy(body: CTACopyRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err:
        return _err(err)
    shop_name = profile.get("shop_name", "us")
    phone = profile.get("phone", "")
    shop = _shop_ctx(profile)

    system = f"""You are a conversion copywriter for an independent auto repair shop.
Shop context: {shop}
Write high-converting CTAs that are direct and action-oriented.
Use shop name ({shop_name}) and phone ({phone}). No fluff — every word drives the action."""

    formats = body.format if body.format != "all" else "Button text, Page headline, Email CTA line, SMS CTA (under 30 chars)"
    user = f"""Write CTA copy for these formats: {formats}
Service: {body.service_type or 'auto repair'}
Goal: {body.goal}
Urgency: {body.urgency}
Label each format with a clear header."""

    text, err = _call_claude(client, system, user)
    if err:
        return _err(err)
    return _ok(text, "cta_copy")


@router.post("/promo-builder/generate")
def promo_builder(body: PromoRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err:
        return _err(err)
    shop_name = profile.get("shop_name", "our shop")
    phone = profile.get("phone", "")
    shop = _shop_ctx(profile)

    system = f"""You are a promotional copywriter for an independent auto repair shop.
Shop context: {shop}
Create urgency without being pushy. Always include: shop name ({shop_name}), phone ({phone}), expiry date.
Channels: {body.channels}."""

    channels_label = body.channels if body.channels != "all" else "SMS (under 160 chars with expiry), Email (subject line + body), Social Media caption"
    user = f"""Write promotional content:
Offer: {body.offer or 'seasonal discount'}
Service: {body.service_type or 'general services'}
Expiry: {body.expiry or 'limited time'}
Channels: {channels_label}

Label each channel with a header."""

    text, err = _call_claude(client, system, user)
    if err:
        return _err(err)
    return _ok(text, "promo_content")


@router.post("/blog-post/generate")
def blog_post(body: BlogRequest):
    profile = _load_profile()
    client, err = _get_client()
    if err:
        return _err(err)
    shop_name = profile.get("shop_name", "our shop")
    shop = _shop_ctx(profile)

    system = f"""You are an SEO blog writer for an independent auto repair shop.
Shop context: {shop}
Write educational, trust-building automotive content for {body.audience}.
Tone: conversational but authoritative. Never talk down to readers.
Structure: meta title + meta description, H1, intro paragraph, 3-4 H2 sections with practical content, conclusion with soft CTA mentioning {shop_name}.
Never fabricate statistics — say 'studies suggest' or 'industry consensus' if citing data."""

    user = f"""Write a ~{body.length}-word blog post about: {body.topic or 'auto maintenance tips'}
{f"Target SEO keywords: {body.keywords}" if body.keywords else ""}
Start with the meta title and meta description, then the full post."""

    text, err = _call_claude(client, system, user, max_tokens=4096)
    if err:
        return _err(err)
    return _ok(text, "blog_post")
