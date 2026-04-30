"""
Router: Module 3 — Wait Time Communications
POST /api/wait-time/generate
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


class WaitTimeRequest(BaseModel):
    status: Optional[str] = "all"
    service_type: Optional[str] = "General Service"
    channels: Optional[str] = "sms,email,phone_script"


@router.post("/wait-time/generate", response_model=ModuleResponse)
def generate_wait_time(body: WaitTimeRequest, user=Depends(get_current_user)): 
    try:
        from wait_time import generate_templates

        profile = generate_templates.load_profile()
        channels = [c.strip() for c in (body.channels or "sms,email,phone_script").split(",")]
        status = body.status or "all"
        service_type = body.service_type or "General Service"

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "wait_time")
        )
        os.makedirs(output_dir, exist_ok=True)

        statuses = (
            generate_templates.STATUS_ORDER if status == "all" else [status]
        )

        def run():
            print(f"\nGenerating wait time communication templates")
            print(f"   Service type : {service_type}")
            print(f"   Status types : {'all (5)' if status == 'all' else status}")
            print(f"   Channels     : {', '.join(channels)}")
            print()
            all_generated = []
            for s in statuses:
                print(f"  {s}")
                generated = generate_templates.generate_status(
                    s, service_type, channels, profile, output_dir
                )
                all_generated.extend(generated)
            print(f"\nDone - {len(all_generated)} file(s) saved to output/wait_time/")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("wait_time")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
