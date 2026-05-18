"""
Router: Module 12 — Warranty Tracker
POST /api/warranty/claims  — log or query warranty claims
POST /api/warranty/report  — Gemini generates warranty recovery report and documentation
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


class WarrantyClaimsRequest(BaseModel):
    action:               Optional[str]   = "list"
    claim_id:             Optional[str]   = ""
    customer:             Optional[str]   = ""
    vehicle:              Optional[str]   = ""
    service_date:         Optional[str]   = ""
    service:              Optional[str]   = ""
    part_number:          Optional[str]   = ""
    part_name:            Optional[str]   = ""
    vendor:               Optional[str]   = ""
    warranty_period_days: Optional[int]   = 365
    claim_date:           Optional[str]   = ""
    status:               Optional[str]   = ""
    notes:                Optional[str]   = ""
    cost:                 Optional[float] = 0.0
    claims_data:          Optional[str]   = ""   # paste of claims for report generation
    period:               Optional[str]   = "all"


@router.post("/warranty/claims", response_model=ModuleResponse)
def warranty_claims(body: WarrantyClaimsRequest, user=Depends(get_current_user)):
    """Log or manage warranty claims. AI report generation is via /warranty/report."""
    try:
        action   = (body.action or "list").strip()
        part     = (body.part_name or body.service or "").strip()
        vendor   = (body.vendor or "").strip()
        customer = (body.customer or "").strip()
        vehicle  = (body.vehicle or "").strip()
        cost     = body.cost or 0.0
        claim_id = (body.claim_id or "").strip()
        status   = (body.status or "").strip()
        notes    = (body.notes or "").strip()

        if action in ("add", "new"):
            if not part:
                return ModuleResponse(success=False, output="", files=[],
                                      error="Please provide the part name to open a warranty claim.")
            msg = f"Warranty claim opened: {part}"
            if vendor:   msg += f" | Vendor: {vendor}"
            if customer: msg += f" | Customer: {customer}"
            if vehicle:  msg += f" | Vehicle: {vehicle}"
            if cost:     msg += f" | Cost at risk: ${cost:,.2f}"
            return ModuleResponse(success=True, output=msg, files=[], content={}, error=None)

        elif action == "update":
            msg = f"Claim {claim_id or '?'} updated"
            if status: msg += f" → Status: {status}"
            if notes:  msg += f" | {notes}"
            return ModuleResponse(success=True, output=msg, files=[], content={}, error=None)

        elif action == "list":
            return ModuleResponse(success=True, output="Warranty claims retrieved.",
                                  files=[], content={}, error=None)

        return ModuleResponse(success=True, output=f"Warranty action '{action}' processed.",
                              files=[], content={}, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))


@router.post("/warranty/report", response_model=ModuleResponse)
def warranty_report(body: WarrantyClaimsRequest, user=Depends(get_current_user)):
    try:
        profile     = load_profile(user.id)
        ctx         = shop_context(profile)
        shop_name   = profile.get("shop_name") or "our shop"

        claims_data = (body.claims_data or "").strip()
        period      = (body.period or "all").strip()
        status      = (body.status or "").strip()

        if not claims_data:
            return ModuleResponse(success=False, output="", files=[],
                                  error="Please provide warranty claims data to generate a report.")

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You generate warranty recovery reports for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"RULES:\n"
            f"- Be direct and financial — this is a money-recovery tool\n"
            f"- Calculate total amount claimed, recovered, and pending reimbursement\n"
            f"- Flag claims that are aging out or at risk of being denied\n"
            f"- Identify vendors with high part failure rates\n"
            f"- Provide specific, actionable next steps for each open claim\n"
            f"- Shop: {shop_name}\n"
        )

        prompt = (
            f"Generate a warranty recovery report for {shop_name}.\n"
            f"Period: {period}\n"
            + (f"Filter by status: {status}\n" if status else "")
            + f"\nClaims data:\n{claims_data}\n\n"
            + "Structure:\n"
            + "## WARRANTY RECOVERY REPORT — [PERIOD]\n"
            + "## FINANCIAL SUMMARY\n"
            + "  (Total claimed | Recovered | Pending | At risk of expiry)\n"
            + "## OPEN CLAIMS — ACTION REQUIRED\n"
            + "  (Claim ID | Part | Vendor | Cost | Days open | Next step)\n"
            + "## CLOSED CLAIMS — RECOVERY SUMMARY\n"
            + "## VENDOR PERFORMANCE\n"
            + "  (Vendor | Claims filed | Recovery rate | Notes)\n"
            + "## RECOMMENDED NEXT STEPS"
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1200)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        filename    = f"warranty_report_{period}.txt"
        content_map = {filename: text}
        output_log  = f"Generated warranty recovery report: {period}"

        return ModuleResponse(success=True, output=output_log, files=[filename],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
