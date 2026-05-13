"""
Router: Module 14 — Seasonal Campaigns
POST /api/seasonal/generate
KB + Gemini: seasonal.json provides campaign structure, Gemini generates fresh copy.
"""
import json
import os
import sys
from typing import Optional

from fastapi import APIRouter, Depends
from auth import get_current_user
from supabase_client import supabase
from pydantic import BaseModel

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from models.responses import ModuleResponse
from kb_loader import kb

router = APIRouter()

VALID_SEASONS = {"winter", "spring", "summer", "fall", "holiday"}


class SeasonalRequest(BaseModel):
    season: Optional[str] = "winter"
    campaign_type: Optional[str] = ""
    discount: Optional[str] = ""
    expiry: Optional[str] = ""


def _load_profile(user_id: str) -> dict:
    try:
        res = supabase.table("shop_profiles").select("shop_info").eq("id", user_id).execute()
        return res.data[0].get("shop_info", {}) if res.data else {}
    except Exception:
        return {}


def _get_gemini():
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return None, "AI features are not yet enabled. Please contact support."
        genai.configure(api_key=api_key)
        return genai, None
    except ImportError:
        return None, "The 'google-generativeai' package is not installed."


def _call_gemini(client, system: str, prompt: str, max_tokens: int = 1200) -> tuple:
    try:
        model = client.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=system,
            generation_config={"max_output_tokens": max_tokens},
        )
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        err = str(e)
        if "quota" in err.lower() or "resource_exhausted" in err.lower():
            return None, "AI service quota reached. Please try again in a moment."
        if "api_key" in err.lower() or "permission" in err.lower():
            return None, "AI service is not configured correctly. Please contact support."
        return None, "AI service error. Please try again."


@router.post("/seasonal/generate", response_model=ModuleResponse)
def generate_seasonal(body: SeasonalRequest, user=Depends(get_current_user)):
    try:
        profile = _load_profile(user.id)
        shop_name  = profile.get("shop_name") or "our shop"
        phone      = profile.get("phone") or ""
        website    = profile.get("website") or ""
        owner      = profile.get("owner_name") or f"The Team at {shop_name}"
        location   = profile.get("location") or ""
        review_link = (profile.get("review_links") or {}).get("google", "")

        season = (body.season or "winter").lower()
        if season not in VALID_SEASONS:
            season = "winter"

        # Load seasonal KB context
        seasonal_kb = kb("seasonal")
        season_data = seasonal_kb.get(season, seasonal_kb.get("seasons", {}).get(season, {}))

        # Build campaign context from KB
        services_hint = ""
        if season_data:
            primary = season_data.get("primary_services", season_data.get("services", []))
            if primary:
                services_hint = f"Key services to promote: {', '.join(primary[:6])}"
            hook = season_data.get("hook", "")
            urgency = season_data.get("urgency_note", "")
        else:
            # Fallback hints when KB entry is minimal
            season_hints = {
                "winter": {"hook": "Cold weather is tough on vehicles.", "services": "battery, coolant, tires, wipers, heater"},
                "spring": {"hook": "Winter was hard on your car — spring is the perfect time to undo the damage.", "services": "AC, alignment, brakes, fluids, filters"},
                "summer": {"hook": "Before you hit the road, make sure your car can handle it.", "services": "AC, cooling system, tires, belts, safety inspection"},
                "fall":   {"hook": "Shorter days and wet roads demand your safety systems are sharp.", "services": "brakes, tires, battery, lights, wipers"},
                "holiday": {"hook": "Don't let a breakdown ruin your holiday plans.", "services": "full inspection, oil change, battery, tire pressure, fluids"},
            }
            hint = season_hints.get(season, season_hints["winter"])
            hook = hint["hook"]
            services_hint = f"Key services to promote: {hint['services']}"
            urgency = ""

        # Build offer string
        offer_parts = []
        if body.discount:
            offer_parts.append(f"Offer: {body.discount}")
        if body.expiry:
            offer_parts.append(f"Expires: {body.expiry}")
        offer_str = " | ".join(offer_parts) if offer_parts else "No specific offer — promote the season and services"

        campaign_name = body.campaign_type or f"{season.title()} Campaign"

        client, err = _get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You are a marketing copywriter for an independent auto repair shop.\n"
            f"Shop: {shop_name} | Phone: {phone} | Website: {website} | Location: {location} | Owner: {owner}\n"
            f"Campaign: {campaign_name} ({season.upper()} season)\n"
            f"Campaign hook: {hook}\n"
            f"{services_hint}\n"
            f"{urgency}\n"
            f"{offer_str}\n\n"
            f"RULES:\n"
            f"- Use the real shop name ({shop_name}), phone ({phone}), and location ({location}) — never placeholders\n"
            f"- Warm, caring tone — never fear-based\n"
            f"- Never fabricate statistics or prices unless given them\n"
            f"- SMS must be under 160 characters\n"
            f"- Each piece must be ready to copy-paste with zero editing\n"
        )

        prompt = (
            f"Write all four campaign pieces for the {season} season:\n\n"
            f"1. SMS (under 160 chars — include shop name, phone, and offer if given)\n\n"
            f"2. EMAIL (include subject line, then full email body with greeting, 2–3 paragraphs, sign-off)\n\n"
            f"3. SOCIAL MEDIA POST (150–200 words, emojis welcome, include hashtags)\n\n"
            f"4. STAFF BRIEFING (internal — campaign hook, key services to push, upsell tip, offer details if any)\n\n"
            f"Label each section clearly."
        )

        text, err = _call_gemini(client, system, prompt, max_tokens=1400)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        # Save output files
        _TOOLS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
        output_dir = os.path.abspath(os.path.join(_TOOLS_ROOT, "..", "output", "seasonal"))
        os.makedirs(output_dir, exist_ok=True)

        # Parse and save individual files
        sections = {"sms": "", "email": "", "social": "", "staff_briefing": ""}
        current = None
        lines_by_section = {k: [] for k in sections}

        for line in text.splitlines():
            ll = line.lower().strip()
            if ll.startswith("1.") or "sms" in ll[:20]:
                current = "sms"
            elif ll.startswith("2.") or "email" in ll[:20]:
                current = "email"
            elif ll.startswith("3.") or "social" in ll[:20]:
                current = "social"
            elif ll.startswith("4.") or "staff" in ll[:20] or "briefing" in ll[:20]:
                current = "staff_briefing"
            elif current:
                lines_by_section[current].append(line)

        saved_files = []
        file_map = {
            "sms":            f"{season}_sms.txt",
            "email":          f"{season}_email.txt",
            "social":         f"{season}_social.txt",
            "staff_briefing": f"{season}_staff_briefing.txt",
        }

        for key, filename in file_map.items():
            content = "\n".join(lines_by_section[key]).strip()
            if not content:
                content = text  # fallback: write full output to each file
            header = f"{campaign_name.upper()} — {key.upper().replace('_', ' ')}\n{'=' * 55}\n\n"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(header + content)
            saved_files.append(filename)

        # Build content map
        content_map = {}
        for filename in saved_files:
            filepath = os.path.join(output_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as fh:
                    content_map[filename] = fh.read()
            except Exception:
                pass

        output_log = f"Generated {len(saved_files)} campaign files for {season.upper()}:\n"
        output_log += "\n".join(f"  output/seasonal/{f}" for f in saved_files)

        return ModuleResponse(
            success=True,
            output=output_log,
            files=saved_files,
            content=content_map,
            error=None,
        )

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
