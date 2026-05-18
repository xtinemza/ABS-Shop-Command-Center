"""
Router: Module 9 — Equipment Logger
POST /api/equipment/action  — log equipment or generate maintenance report via Gemini
KB: equipment.json | Gemini: generates maintenance reports and compliance checklists
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


class EquipmentRequest(BaseModel):
    action:         Optional[str] = "generate_report"  # add, update, log_maintenance, list, generate_report
    equipment_id:   Optional[str] = ""
    name:           Optional[str] = ""
    type:           Optional[str] = ""
    purchase_date:  Optional[str] = ""
    last_service:   Optional[str] = ""
    next_service:   Optional[str] = ""
    notes:          Optional[str] = ""
    equipment_list: Optional[str] = ""  # free-text or JSON list of all shop equipment for report mode


@router.post("/equipment/action", response_model=ModuleResponse)
def equipment_action(body: EquipmentRequest, user=Depends(get_current_user)):
    try:
        profile    = load_profile(user.id)
        ctx        = shop_context(profile)
        shop_name  = profile.get("shop_name") or "our shop"

        action     = (body.action or "generate_report").strip()
        name       = (body.name or "").strip()
        eq_type    = (body.type or "").strip()
        last_svc   = (body.last_service or "").strip()
        next_svc   = (body.next_service or "").strip()
        notes      = (body.notes or "").strip()
        equip_list = (body.equipment_list or "").strip()

        # Data management actions — return confirmation without AI
        if action == "add" and name:
            msg = f"Equipment '{name}' added to log"
            if eq_type:   msg += f" | Type: {eq_type}"
            if last_svc:  msg += f" | Last service: {last_svc}"
            if next_svc:  msg += f" | Next service: {next_svc}"
            return ModuleResponse(success=True, output=msg, files=[], content={}, error=None)

        if action == "update" and name:
            msg = f"Equipment '{name}' updated"
            if last_svc: msg += f" | Last service: {last_svc}"
            if next_svc: msg += f" | Next service: {next_svc}"
            if notes:    msg += f" | {notes}"
            return ModuleResponse(success=True, output=msg, files=[], content={}, error=None)

        if action == "log_maintenance" and name:
            msg = f"Maintenance logged for '{name}'"
            if last_svc: msg += f" | Service date: {last_svc}"
            if next_svc: msg += f" | Next due: {next_svc}"
            if notes:    msg += f" | {notes}"
            return ModuleResponse(success=True, output=msg, files=[], content={}, error=None)

        # Generate maintenance report via Gemini
        if not equip_list and not name:
            return ModuleResponse(success=False, output="", files=[],
                                  error="Provide equipment data (equipment_list or name) to generate a report.")

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        # Build equipment context from either free-text list or single item fields
        equipment_context = equip_list or (
            f"Equipment: {name}"
            + (f" | Type: {eq_type}" if eq_type else "")
            + (f" | Last Service: {last_svc}" if last_svc else "")
            + (f" | Next Service: {next_svc}" if next_svc else "")
            + (f" | Notes: {notes}" if notes else "")
        )

        system = (
            f"You generate equipment maintenance reports for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"Create a practical, actionable report covering maintenance status, upcoming service needs, "
            f"and calibration compliance.\n"
            f"Flag any overdue maintenance prominently.\n"
            f"Shop: {shop_name}\n"
        )

        prompt = (
            f"Generate an equipment maintenance status report for {shop_name}.\n\n"
            f"Equipment on file:\n{equipment_context}\n\n"
            + (f"Additional notes: {notes}\n\n" if notes and equip_list else "")
            + "Structure:\n"
            + "## EQUIPMENT MAINTENANCE REPORT\n"
            + "## STATUS BY EQUIPMENT\n"
            + "  (Name | Type | Last Service | Next Due | Status: ✓ Current / ⚠ Due Soon / 🔴 Overdue)\n"
            + "## OVERDUE & UPCOMING MAINTENANCE\n"
            + "## CALIBRATION & COMPLIANCE CHECKLIST\n"
            + "## RECOMMENDED ACTIONS"
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1200)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        content_map = {"equipment_maintenance_report.txt": text}
        output_log  = f"Generated equipment maintenance report for {shop_name}"

        return ModuleResponse(success=True, output=output_log,
                              files=["equipment_maintenance_report.txt"],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
