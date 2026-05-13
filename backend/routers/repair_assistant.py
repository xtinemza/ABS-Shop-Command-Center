"""
Router: Repair Assistant — AI-Powered Diagnostics
POST /api/repair-assistant/diagnose
KB: obd_codes.json + vehicles KB | AI: Gemini 2.5 Flash generates dual output
(mechanic view + service advisor plain-language script)
"""
import json
import os
import sys

from fastapi import APIRouter, Depends
from auth import get_current_user
from supabase_client import supabase
from pydantic import BaseModel
from typing import Optional, List

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from models.responses import ModuleResponse
from kb_loader import kb

router = APIRouter()


class RepairRequest(BaseModel):
    vehicle_year: Optional[str] = ""
    vehicle_make: Optional[str] = ""
    vehicle_model: Optional[str] = ""
    mileage: Optional[str] = ""
    symptoms: str = ""
    obd_codes: Optional[str] = ""   # comma-separated, e.g. "P0300, P0171"


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


def _call_gemini(client, system: str, prompt: str, max_tokens: int = 2000) -> tuple:
    try:
        model = client.GenerativeModel(
            model_name="gemini-2.5-flash",
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


def _parse_obd_codes(raw: str) -> list:
    if not raw:
        return []
    codes = [c.strip().upper() for c in raw.replace(",", " ").split() if c.strip()]
    return list(dict.fromkeys(codes))  # deduplicate, preserve order


def _get_obd_context(codes: list) -> str:
    obd_kb = kb("obd_codes")
    if not obd_kb or not codes:
        return ""
    parts = []
    unknown = []
    for code in codes:
        data = obd_kb.get(code)
        if data:
            causes = ", ".join(data.get("causes", [])[:4])
            tests  = ", ".join(data.get("tests", [])[:3])
            parts.append(
                f"  {code} — {data['name']} (severity: {data.get('severity','?')})\n"
                f"    System: {data.get('system','?')}\n"
                f"    Common causes: {causes}\n"
                f"    Diagnostic tests: {tests}\n"
                f"    Advisor summary: {data.get('advisor_summary','')}"
            )
        else:
            unknown.append(code)
    result = "\n".join(parts)
    if unknown:
        result += f"\n  Unknown codes (research needed): {', '.join(unknown)}"
    return result


def _get_vehicle_context(year: str, make: str, model: str, mileage: str) -> str:
    if not any([year, make, model]):
        return ""
    vehicles_kb = kb("vehicles")
    if not vehicles_kb:
        return f"Vehicle: {year} {make} {model}" + (f" | Mileage: {mileage}" if mileage else "")

    # Try to find a matching vehicle entry
    search_key = f"{make} {model}".lower().strip()
    vehicle_data = None
    for key, val in vehicles_kb.items():
        if key.lower() == search_key or key.lower() == model.lower():
            vehicle_data = val
            break
        if make.lower() in key.lower() and model.lower() in key.lower():
            vehicle_data = val
            break

    lines = [f"Vehicle: {year} {make} {model}"]
    if mileage:
        lines.append(f"Mileage: {mileage}")
    if vehicle_data:
        if isinstance(vehicle_data, dict):
            engine = vehicle_data.get("engine") or vehicle_data.get("engines")
            if engine:
                lines.append(f"Engine: {engine}")
            common_issues = vehicle_data.get("common_issues") or vehicle_data.get("known_issues")
            if common_issues and isinstance(common_issues, list):
                lines.append(f"Known issues for this vehicle: {', '.join(str(i) for i in common_issues[:5])}")
            intervals = vehicle_data.get("service_intervals") or vehicle_data.get("intervals")
            if intervals and isinstance(intervals, dict):
                interval_str = "; ".join(f"{k}: {v}" for k, v in list(intervals.items())[:4])
                lines.append(f"Service intervals: {interval_str}")
    return "\n".join(lines)


def _try_vector_search(symptoms: str, codes: list, make: str, model: str) -> str:
    """Attempt pgvector similarity search; returns empty string if table doesn't exist."""
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return ""
        genai.configure(api_key=api_key)

        query_text = f"{make} {model}: {symptoms}. Codes: {', '.join(codes)}"

        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query_text,
        )
        embedding = result["embedding"]

        # pgvector query — fails silently if table doesn't exist
        res = supabase.rpc(
            "match_repair_knowledge",
            {"query_embedding": embedding, "match_count": 5}
        ).execute()

        if not res.data:
            return ""

        snippets = []
        for row in res.data:
            content = row.get("content", "")
            if content:
                snippets.append(content[:400])

        return "\n---\n".join(snippets) if snippets else ""
    except Exception:
        return ""


@router.post("/repair-assistant/diagnose", response_model=ModuleResponse)
def diagnose(body: RepairRequest, user=Depends(get_current_user)):
    try:
        profile = _load_profile(user.id)
        shop_name = profile.get("shop_name") or "our shop"

        if not body.symptoms.strip() and not body.obd_codes.strip():
            return ModuleResponse(
                success=False, output="", files=[], error="Please provide symptoms, OBD codes, or both."
            )

        codes = _parse_obd_codes(body.obd_codes or "")
        obd_context = _get_obd_context(codes)
        vehicle_context = _get_vehicle_context(
            body.vehicle_year, body.vehicle_make, body.vehicle_model, body.mileage
        )

        # Optional: pull from repair knowledge base (pgvector)
        rag_context = _try_vector_search(
            body.symptoms, codes, body.vehicle_make or "", body.vehicle_model or ""
        )

        client, err = _get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            "You are an expert automotive diagnostic assistant working alongside mechanics at an independent auto repair shop.\n"
            "Your job is to analyze symptoms and OBD codes, then produce two outputs:\n"
            "1. A technical MECHANIC DIAGNOSIS section (for the technician)\n"
            "2. A plain-language ADVISOR SCRIPT section (for the service advisor to read to the customer)\n\n"
            "MECHANIC DIAGNOSIS must include:\n"
            "  - Ranked list of most likely causes (most probable first, with brief reasoning)\n"
            "  - Specific diagnostic tests to run in priority order\n"
            "  - Parts likely needed (generic names, not part numbers)\n"
            "  - Estimated labor hours for the most probable repair\n"
            "  - Any related services to inspect while in there (upsell opportunities)\n"
            "  - Severity: CRITICAL / HIGH / MEDIUM / LOW\n\n"
            "ADVISOR SCRIPT must include:\n"
            "  - A plain-English explanation of what was found (no jargon)\n"
            "  - Why the repair matters (consequence of not fixing)\n"
            "  - What the repair involves (brief, non-technical)\n"
            "  - Urgency recommendation\n"
            "  - A suggested phrase to open the conversation with the customer\n\n"
            "Rules:\n"
            "  - Never fabricate specific prices — say 'we'll provide a firm quote after diagnosis'\n"
            "  - If symptoms and codes point to multiple possible causes, list all of them ranked by probability\n"
            "  - Be specific about tests — 'compression test cyl 3' is better than 'check engine'\n"
            "  - The advisor script should be warm, calm, and clear — the customer should leave feeling informed, not scared\n"
        )

        prompt_parts = ["Diagnose the following vehicle issue:\n"]

        if vehicle_context:
            prompt_parts.append(f"VEHICLE INFORMATION:\n{vehicle_context}\n")

        if body.symptoms.strip():
            prompt_parts.append(f"REPORTED SYMPTOMS:\n{body.symptoms.strip()}\n")

        if obd_context:
            prompt_parts.append(f"OBD TROUBLE CODES:\n{obd_context}\n")

        if rag_context:
            prompt_parts.append(f"RELATED REPAIR KNOWLEDGE:\n{rag_context}\n")

        prompt_parts.append(
            "\nProvide your full diagnosis with both sections clearly labeled:\n"
            "## MECHANIC DIAGNOSIS\n[technical content here]\n\n"
            "## ADVISOR SCRIPT\n[customer-facing content here]"
        )

        prompt = "\n".join(prompt_parts)

        text, err = _call_gemini(client, system, prompt, max_tokens=2000)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        # Split into mechanic / advisor sections
        mechanic_text = ""
        advisor_text = ""

        lower = text.lower()
        mechanic_idx = lower.find("## mechanic diagnosis")
        advisor_idx  = lower.find("## advisor script")

        if mechanic_idx >= 0 and advisor_idx >= 0:
            mechanic_text = text[mechanic_idx:advisor_idx].strip()
            advisor_text  = text[advisor_idx:].strip()
        elif mechanic_idx >= 0:
            mechanic_text = text[mechanic_idx:].strip()
        elif advisor_idx >= 0:
            advisor_text = text[advisor_idx:].strip()
        else:
            mechanic_text = text
            advisor_text  = text

        # Build content map
        vehicle_label = " ".join(filter(None, [body.vehicle_year, body.vehicle_make, body.vehicle_model])) or "Vehicle"
        codes_label   = ", ".join(codes) if codes else "No codes"

        content_map = {
            "mechanic_diagnosis.txt": mechanic_text or text,
            "advisor_script.txt":     advisor_text  or text,
        }

        output_log = (
            f"Diagnosis complete for {vehicle_label}\n"
            f"Codes analyzed: {codes_label}\n"
            f"Symptoms: {body.symptoms[:100]}{'...' if len(body.symptoms) > 100 else ''}"
        )

        return ModuleResponse(
            success=True,
            output=output_log,
            files=["mechanic_diagnosis.txt", "advisor_script.txt"],
            content=content_map,
            error=None,
        )

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
