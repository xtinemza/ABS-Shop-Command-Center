"""
Router: Module 8 — Recall Notifications
POST /api/recall/check
POST /api/recall/notify
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


class RecallCheckRequest(BaseModel):
    make: Optional[str] = ""
    model: Optional[str] = ""
    year: Optional[str] = ""
    vin: Optional[str] = ""
    customer: Optional[str] = ""


class RecallNotifyRequest(BaseModel):
    customer: Optional[str] = "Customer"
    vehicle: Optional[str] = "Your Vehicle"
    recall_campaign: Optional[str] = "RECALL-001"
    component: Optional[str] = "Vehicle Component"
    description: Optional[str] = "See NHTSA recall details."
    remedy: Optional[str] = "Manufacturer will repair at no charge."
    consequence: Optional[str] = ""
    urgency: Optional[str] = "medium"


@router.post("/recall/check", response_model=ModuleResponse)
def check_recall(body: RecallCheckRequest):
    try:
        from recall import check_recalls

        profile = check_recalls.load_profile()
        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "recall")
        )
        os.makedirs(output_dir, exist_ok=True)

        args = argparse.Namespace(
            make=body.make or "",
            model=body.model or "",
            year=body.year or "",
            vin=body.vin or "",
            customer=body.customer or "Customer",
            recall_campaign=None,
            component=None,
            description=None,
            consequence=None,
            remedy=None,
            no_recalls=False,
        )

        def run():
            print(f"\nGenerating recall lookup guide")
            guide = check_recalls.generate_lookup_guide(args, profile)
            filename = "recall_lookup_guide.txt"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(guide)
            print(guide)
            print(f"\nSaved output/recall/{filename}")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("recall")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))


@router.post("/recall/notify", response_model=ModuleResponse)
def notify_recall(body: RecallNotifyRequest):
    try:
        from recall import generate_notifications
        from datetime import datetime

        profile = generate_notifications.load_profile()
        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "recall")
        )
        os.makedirs(output_dir, exist_ok=True)

        args = argparse.Namespace(
            customer=body.customer or "Customer",
            vehicle=body.vehicle or "Your Vehicle",
            recall_campaign=body.recall_campaign or "RECALL-001",
            component=body.component or "Vehicle Component",
            description=body.description or "See NHTSA recall details.",
            consequence=body.consequence or "See NHTSA recall details for full consequence description.",
            remedy=body.remedy or "Manufacturer will repair at no charge.",
            urgency=body.urgency or "medium",
        )

        def run():
            print(f"\nGenerating recall notifications")
            print(f"   Customer  : {args.customer}")
            print(f"   Vehicle   : {args.vehicle}")
            print(f"   Campaign  : {args.recall_campaign}")
            print(f"   Urgency   : {args.urgency}")
            print()

            safe_campaign = args.recall_campaign.replace("/", "-").replace(" ", "_")

            outputs = {
                f"recall_notification_sms_{safe_campaign}.txt": generate_notifications.build_sms(args, profile),
                f"recall_notification_email_{safe_campaign}.txt": generate_notifications.build_email(args, profile),
                f"recall_notification_phone_{safe_campaign}.txt": generate_notifications.build_phone_script(args, profile),
                f"recall_notification_shop_note_{safe_campaign}.txt": generate_notifications.build_shop_note(args, profile),
            }

            for filename, content in outputs.items():
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as fh:
                    fh.write(content)
                print(f"  Saved output/recall/{filename}")

            print(f"\nDone - {len(outputs)} notification files saved.")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("recall")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
