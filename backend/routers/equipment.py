"""
Router: Module 9 — Equipment Logger
POST /api/equipment/action
"""
import argparse
import os
import sys
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

_TOOLS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
if _TOOLS_ROOT not in sys.path:
    sys.path.insert(0, _TOOLS_ROOT)

from models.responses import ModuleResponse
from utils import capture_output, read_output_files

router = APIRouter()


class EquipmentRequest(BaseModel):
    action: Optional[str] = "list"          # add, update, log_maintenance, list, generate_report
    equipment_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    purchase_date: Optional[str] = None
    last_service: Optional[str] = None
    next_service: Optional[str] = None
    notes: Optional[str] = None


@router.post("/equipment/action", response_model=ModuleResponse)
def equipment_action(body: EquipmentRequest):
    try:
        from equipment import log_equipment

        profile = log_equipment.load_profile()
        equipment = log_equipment.load_equipment()

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "equipment")
        )
        os.makedirs(output_dir, exist_ok=True)

        args = argparse.Namespace(
            action=body.action or "list",
            equipment_id=body.equipment_id or None,
            name=body.name or None,
            type=body.type or None,
            purchase_date=body.purchase_date or None,
            last_service=body.last_service or None,
            next_service=body.next_service or None,
            notes=body.notes or None,
        )

        action = args.action

        def run():
            print(f"\nEquipment action: {action}")
            print()

            if action == "add":
                log_equipment.action_add(args, equipment)
            elif action == "update":
                log_equipment.action_update(args, equipment)
            elif action == "log_maintenance":
                log_equipment.action_log_maintenance(args, equipment)
            elif action == "list":
                log_equipment.action_list(equipment)
            elif action == "generate_report":
                if not equipment:
                    print("No equipment in log. Use action=add to begin.")
                else:
                    log_equipment.action_generate_report(equipment, profile)
            else:
                print(f"Unknown action: {action}")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("equipment")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
