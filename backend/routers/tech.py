"""
Router: Module 16 — Technician Productivity
POST /api/tech-productivity/generate
Gemini: generates weekly tech efficiency summaries and coaching notes
"""
import os, sys
from typing import Optional
from fastapi import APIRouter, Depends
from auth import get_current_user
from pydantic import BaseModel

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from models.responses import ModuleResponse
from gemini_client import load_profile, get_gemini, call_gemini, shop_context

router = APIRouter()


class TechSummaryRequest(BaseModel):
    period:      Optional[str] = "week"
    date:        Optional[str] = ""
    technicians: Optional[str] = ""   # free-text or JSON: name, hours_flagged, hours_billed, revenue


@router.post("/tech-productivity/generate", response_model=ModuleResponse)
def tech_summary(body: TechSummaryRequest, user=Depends(get_current_user)):
    try:
        profile  = load_profile(user.id)
        ctx      = shop_context(profile)
        shop_name = profile.get("shop_name") or "our shop"

        period      = (body.period or "week").strip()
        date_str    = (body.date or "").strip()
        tech_data   = (body.technicians or "").strip()

        if not tech_data:
            return ModuleResponse(success=False, output="", files=[],
                                  error="Please provide technician data (hours flagged, hours billed, revenue).")

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You generate technician productivity summaries for the owner/manager of an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"RULES:\n"
            f"- Be direct and data-focused — this is an internal management report\n"
            f"- Calculate efficiency rate: billed hours / flagged hours × 100%\n"
            f"- Flag anyone below 85% efficiency — include a coaching note\n"
            f"- Highlight top performers\n"
            f"- Include a shop-wide summary row\n"
            f"- Add one actionable recommendation per underperforming tech\n"
            f"- Tone: professional and constructive — coach, don't criticize\n"
        )

        prompt = (
            f"Generate a technician productivity report for {shop_name}.\n"
            f"Period: {period}" + (f" ending {date_str}" if date_str else "") + "\n\n"
            f"Technician data:\n{tech_data}\n\n"
            "Structure:\n"
            "## PRODUCTIVITY SUMMARY — [PERIOD]\n"
            "## PER-TECHNICIAN BREAKDOWN\n"
            "  (name, hours flagged, hours billed, efficiency %, revenue, status: ✓/⚠)\n"
            "## SHOP TOTALS\n"
            "## COACHING NOTES\n"
            "  (one note per tech below 85% efficiency)\n"
            "## MANAGER ACTION ITEMS"
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1200)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        content_map = {"productivity_report.txt": text}
        output_log  = f"Generated tech productivity report — {period}" + (f" ({date_str})" if date_str else "")

        return ModuleResponse(success=True, output=output_log, files=["productivity_report.txt"],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
