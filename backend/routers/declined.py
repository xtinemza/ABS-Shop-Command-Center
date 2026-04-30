"""
Router: Module 4 — Declined Services Follow-Up
POST /api/declined/generate
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


class DeclinedRequest(BaseModel):
    service: Optional[str] = "Recommended Service"
    urgency: Optional[str] = "medium"
    touches: Optional[str] = "1,2,3,4"
    offer: Optional[str] = "10% off when you schedule this service"


@router.post("/declined/generate", response_model=ModuleResponse)
def generate_declined(body: DeclinedRequest, user=Depends(get_current_user)): 
    try:
        from declined_services import generate_campaign

        profile = generate_campaign.load_profile()
        service = body.service or "Recommended Service"
        urgency_key = body.urgency or "medium"
        offer = body.offer or "10% off when you schedule this service"
        touches_str = body.touches or "1,2,3,4"

        # Parse touch list
        try:
            touch_nums = [int(t.strip()) for t in touches_str.split(",") if t.strip()]
        except ValueError:
            touch_nums = [1, 2, 3, 4]

        # Validate urgency
        valid_urgencies = ["low", "medium", "high", "safety-critical"]
        if urgency_key not in valid_urgencies:
            urgency_key = "medium"

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "declined_services")
        )
        os.makedirs(output_dir, exist_ok=True)

        service_slug = generate_campaign.slugify(service)

        def run():
            print(f"\nGenerating declined services follow-up campaign")
            print(f"   Service  : {service}")
            print(f"   Urgency  : {urgency_key}")
            print(f"   Touches  : {touch_nums}")
            print()
            generated = []
            for touch_num in touch_nums:
                channels_dict = generate_campaign.build_touch(
                    touch_num, profile, service, urgency_key, offer
                )
                if channels_dict is None:
                    print(f"  Unknown touch number: {touch_num}")
                    continue
                timing = generate_campaign.TOUCH_TIMING.get(touch_num, f"Touch {touch_num}")
                print(f"  Touch {touch_num} — {timing}")
                for channel, content in channels_dict.items():
                    filename = f"{service_slug}_touch{touch_num}_{channel}.txt"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, "w", encoding="utf-8") as fh:
                        fh.write(content)
                    print(f"    Saved output/declined_services/{filename}")
                    generated.append(filename)
            print(f"\nDone - {len(generated)} file(s) saved to output/declined_services/")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("declined_services")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
