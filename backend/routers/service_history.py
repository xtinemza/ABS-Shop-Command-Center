"""
Router: Module 5 — Vehicle Service History
POST /api/service-history/generate
Gemini: generates a branded service history report from customer-provided records
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


class ServiceHistoryRequest(BaseModel):
    customer:  Optional[str] = ""
    vehicle:   Optional[str] = ""
    mileage:   Optional[str] = ""
    records:   Optional[str] = ""   # free-text or JSON list of service records
    vin:       Optional[str] = ""


@router.post("/service-history/generate", response_model=ModuleResponse)
def generate_service_history(body: ServiceHistoryRequest, user=Depends(get_current_user)):
    try:
        profile  = load_profile(user.id)
        ctx      = shop_context(profile)

        shop_name = profile.get("shop_name") or "our shop"
        phone     = profile.get("phone") or ""
        customer  = (body.customer or "").strip()
        vehicle   = (body.vehicle or "").strip()
        mileage   = (body.mileage or "").strip()
        records   = (body.records or "").strip()
        vin       = (body.vin or "").strip()

        if not records:
            return ModuleResponse(success=False, output="", files=[],
                                  error="Please provide service records to generate the report.")

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You generate branded vehicle service history reports for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"RULES:\n"
            f"- Format as a clean, professional report the customer can keep or share when selling the vehicle\n"
            f"- Group services chronologically\n"
            f"- Include a Vehicle Health Summary section at the end\n"
            f"- Include upcoming service recommendations based on the history\n"
            f"- Use {shop_name} branding throughout — never generic placeholders\n"
            f"- Phone: {phone}\n"
            f"- Close with a note about the shop's warranty on parts and labor\n"
        )

        prompt = (
            f"Generate a complete Vehicle Service History Report.\n\n"
            + (f"Customer: {customer}\n" if customer else "")
            + (f"Vehicle: {vehicle}\n" if vehicle else "")
            + (f"Current Mileage: {mileage}\n" if mileage else "")
            + (f"VIN: {vin}\n" if vin else "")
            + f"\nService Records:\n{records}\n\n"
            + "Structure the report as:\n"
            + "## VEHICLE SERVICE HISTORY — [VEHICLE]\n"
            + "## SERVICE TIMELINE (chronological, with dates, mileage, services, cost)\n"
            + "## VEHICLE HEALTH SUMMARY\n"
            + "## UPCOMING RECOMMENDATIONS\n"
            + "## SHOP CONTACT & WARRANTY"
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1600)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        label = f"{customer} — {vehicle}".strip(" —") or "Vehicle"
        content_map = {"service_history_report.txt": text}
        output_log  = f"Generated service history report: {label}"

        return ModuleResponse(success=True, output=output_log, files=["service_history_report.txt"],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
