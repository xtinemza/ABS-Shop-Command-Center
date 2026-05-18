"""
Router: Module 7 — Vehicle Intake & Inspection Forms
POST /api/inspection/generate
KB: inspection.json | Gemini: generates inspection forms and customer-facing urgency reports
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
from kb_loader import kb
from gemini_client import load_profile, get_gemini, call_gemini, shop_context

router = APIRouter()

INSPECTION_TYPES = {
    "multi_point": "Multi-Point Inspection (MPI) — comprehensive bumper-to-bumper assessment",
    "pre_purchase": "Pre-Purchase Inspection — thorough evaluation for a vehicle being considered for purchase",
    "seasonal": "Seasonal Inspection — focused on weather-readiness (winter prep or summer prep)",
}


class InspectionRequest(BaseModel):
    mode:     Optional[str] = "form"         # "form" = blank form | "report" = filled report from results
    type:     Optional[str] = "multi_point"
    customer: Optional[str] = ""
    vehicle:  Optional[str] = ""
    mileage:  Optional[str] = ""
    results:  Optional[str] = ""            # technician findings for report mode


@router.post("/inspection/generate", response_model=ModuleResponse)
def generate_inspection(body: InspectionRequest, user=Depends(get_current_user)):
    try:
        profile  = load_profile(user.id)
        ctx      = shop_context(profile)
        insp_kb  = kb("inspection")

        shop_name = profile.get("shop_name") or "our shop"
        phone     = profile.get("phone") or ""
        mode      = (body.mode or "form").strip()
        itype     = (body.type or "multi_point").strip()
        customer  = (body.customer or "").strip()
        vehicle   = (body.vehicle or "").strip()
        mileage   = (body.mileage or "").strip()
        results   = (body.results or "").strip()

        type_desc = INSPECTION_TYPES.get(itype, INSPECTION_TYPES["multi_point"])

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        if mode == "form":
            # Generate a blank inspection checklist form
            system = (
                f"You generate professional vehicle inspection forms for an independent auto repair shop.\n"
                f"{ctx}\n\n"
                f"Create a thorough, technician-ready inspection checklist that is easy to fill out on paper or a tablet.\n"
                f"Use condition ratings: ✓ Good | ⚠ Fair | ✗ Poor | N/A\n"
                f"Group items by system. Include a notes column for each item.\n"
                f"Shop: {shop_name} | Phone: {phone}\n"
            )
            prompt = (
                f"Generate a {type_desc} checklist form.\n"
                + (f"Vehicle: {vehicle}\n" if vehicle else "")
                + (f"Customer: {customer}\n" if customer else "")
                + (f"Mileage: {mileage}\n" if mileage else "")
                + "\nStructure:\n"
                + "## VEHICLE INTAKE FORM (header with shop name, date, customer, vehicle, mileage, advisor)\n"
                + "## INSPECTION CHECKLIST (grouped by system: Engine, Brakes, Tires & Wheels, "
                + "Suspension & Steering, Fluids, Electrical, Interior/Exterior, HVAC)\n"
                + "## TECHNICIAN SIGN-OFF (tech name, date, recommendations summary)"
            )
        else:
            # Generate a customer-facing urgency report from filled-in results
            if not results:
                return ModuleResponse(success=False, output="", files=[],
                                      error="Please provide inspection results to generate a report.")
            system = (
                f"You generate customer-facing vehicle inspection reports for an independent auto repair shop.\n"
                f"{ctx}\n\n"
                f"Translate technician findings into a clear, honest report the customer can understand.\n"
                f"Use urgency color coding: 🔴 Safety Critical | 🟠 High Priority | 🟡 Schedule Soon | 🟢 Good\n"
                f"Be transparent and educational — help the customer understand, never pressure them.\n"
                f"Shop: {shop_name} | Phone: {phone}\n"
            )
            prompt = (
                f"Generate a customer-facing inspection report.\n"
                + (f"Customer: {customer}\n" if customer else "")
                + (f"Vehicle: {vehicle}\n" if vehicle else "")
                + (f"Mileage: {mileage}\n" if mileage else "")
                + f"\nTechnician findings:\n{results}\n\n"
                + "Structure:\n"
                + "## VEHICLE INSPECTION REPORT — [VEHICLE]\n"
                + "## FINDINGS SUMMARY (color-coded urgency list)\n"
                + "## WHAT THIS MEANS (plain-language explanation for each item flagged)\n"
                + "## RECOMMENDED NEXT STEPS\n"
                + "## SHOP CONTACT"
            )

        text, err = call_gemini(client, system, prompt, max_tokens=1800)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        filename = "inspection_report.txt" if mode == "report" else "inspection_form.txt"
        label    = f"{customer} — {vehicle}".strip(" —") or itype.replace("_", " ").title()
        content_map = {filename: text}
        output_log  = f"Generated inspection {mode}: {label}"

        return ModuleResponse(success=True, output=output_log, files=[filename],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
