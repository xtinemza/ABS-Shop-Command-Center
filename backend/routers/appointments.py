"""
Router: Module 1 — Appointment Reminders
POST /api/appointments/generate
"""
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

_TOOLS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
if _TOOLS_ROOT not in sys.path:
    sys.path.insert(0, _TOOLS_ROOT)

from models.responses import ModuleResponse
from utils import capture_output, read_output_files

router = APIRouter()


class AppointmentRequest(BaseModel):
    touchpoint: Optional[str] = "all"
    service_type: Optional[str] = "General Service"
    channels: Optional[str] = "sms,email,phone_script"


@router.post("/appointments/generate", response_model=ModuleResponse)
def generate_appointments(body: AppointmentRequest, user=Depends(get_current_user)): 
    try:
        from appointments import generate_reminders

        profile = generate_reminders.load_profile()
        channels = [c.strip() for c in (body.channels or "sms,email,phone_script").split(",")]
        touchpoint = body.touchpoint or "all"
        service_type = body.service_type or "General Service"

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "appointments")
        )
        os.makedirs(output_dir, exist_ok=True)

        touchpoints = (
            generate_reminders.TOUCHPOINT_ORDER
            if touchpoint == "all"
            else [touchpoint]
        )

        def run():
            print(f"\nGenerating appointment reminders")
            print(f"   Service type : {service_type}")
            print(f"   Touchpoints  : {'all (6)' if touchpoint == 'all' else touchpoint}")
            print(f"   Channels     : {', '.join(channels)}")
            print()
            all_generated = []
            for tp in touchpoints:
                print(f"  {tp}")
                generated = generate_reminders.generate_touchpoint(
                    tp, service_type, channels, profile, output_dir
                )
                all_generated.extend(generated)
            print(f"\nDone - {len(all_generated)} file(s) saved to output/appointments/")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("appointments")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
