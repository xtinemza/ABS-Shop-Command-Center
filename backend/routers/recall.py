"""
Router: Module 8 — Recall Notifications
GET  /api/recall/nhtsa-lookup  — live NHTSA API lookup by VIN or make/model/year
POST /api/recall/check         — generates a manual lookup guide
POST /api/recall/notify        — generates customer notification templates
"""
import argparse
import os
import sys
import urllib.request
import urllib.parse
import json as _json
import logging
from typing import Optional, List

from fastapi import APIRouter, Depends
from auth import get_current_user
from supabase_client import supabase

from pydantic import BaseModel

logger = logging.getLogger(__name__)

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


_NHTSA_BASE = "https://api.nhtsa.gov/recalls"

@router.get("/recall/nhtsa-lookup")
def nhtsa_lookup(
    vin: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    year: Optional[str] = None,
    user=Depends(get_current_user),
):
    """
    Live NHTSA recall lookup.
    - Provide `vin` for VIN-based lookup, OR
    - Provide `make` + `model` + `year` for vehicle-based lookup.
    Returns structured recall records from the NHTSA public API.
    """
    try:
        if vin and vin.strip():
            vin_clean = vin.strip().upper()
            if len(vin_clean) != 17:
                return {"success": False, "error": "VIN must be exactly 17 characters.", "recalls": []}
            url = f"{_NHTSA_BASE}/recallsByVehicleId?vin={urllib.parse.quote(vin_clean)}"
        elif make and model and year:
            params = urllib.parse.urlencode({
                "make": make.strip(),
                "model": model.strip(),
                "modelYear": year.strip(),
            })
            url = f"{_NHTSA_BASE}/recallsByVehicle?{params}"
        else:
            return {"success": False, "error": "Provide a VIN, or make + model + year.", "recalls": []}

        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "ShopCommandCenter/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = _json.loads(resp.read().decode())

        results = data.get("results", [])
        recalls = [
            {
                "campaign": r.get("NHTSACampaignNumber", ""),
                "component": r.get("Component", ""),
                "description": r.get("Summary", "") or r.get("Conequence", ""),
                "consequence": r.get("Conequence", "") or r.get("Consequence", ""),
                "remedy": r.get("Remedy", ""),
                "report_date": r.get("ReportReceivedDate", ""),
            }
            for r in results
        ]
        logger.info("NHTSA lookup returned %d recalls for query: vin=%s make=%s model=%s year=%s",
                    len(recalls), vin, make, model, year)
        return {"success": True, "count": len(recalls), "recalls": recalls}

    except urllib.error.URLError as e:
        logger.warning("NHTSA API unreachable: %s", e)
        return {"success": False, "error": "Could not reach the NHTSA API. Check your internet connection.", "recalls": []}
    except Exception as exc:
        logger.error("NHTSA lookup error: %s", exc)
        return {"success": False, "error": "Recall lookup failed. Please try again.", "recalls": []}


@router.post("/recall/check", response_model=ModuleResponse)
def check_recall(body: RecallCheckRequest, user=Depends(get_current_user)): 
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
def notify_recall(body: RecallCheckRequest, user=Depends(get_current_user)): 
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
