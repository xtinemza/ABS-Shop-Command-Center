"""
Router: Module 5 — Vehicle Service History
POST /api/service-history/generate
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


class ServiceHistoryRequest(BaseModel):
    customer: Optional[str] = "Customer Name"
    vehicle: Optional[str] = "Vehicle Year Make Model"
    mileage: Optional[int] = 50000
    records: Optional[str] = "[]"
    vin: Optional[str] = ""


@router.post("/service-history/generate", response_model=ModuleResponse)
def generate_service_history(body: ServiceHistoryRequest):
    try:
        from service_history import generate_report

        profile = generate_report.load_profile()

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "service_history")
        )
        os.makedirs(output_dir, exist_ok=True)

        # Build a namespace object to mimic argparse args
        args = argparse.Namespace(
            customer=body.customer or "Customer Name",
            vehicle=body.vehicle or "Vehicle",
            mileage=body.mileage or 0,
            records=body.records or "[]",
            vin=body.vin or "",
        )

        def run():
            print(f"\nGenerating vehicle service history report")
            print(f"   Customer : {args.customer}")
            print(f"   Vehicle  : {args.vehicle}")
            print(f"   Mileage  : {args.mileage:,}")
            print()

            report_text = generate_report.build_report(profile, args)

            import re
            safe_name = re.sub(r"[^a-z0-9_]", "_", args.customer.lower().strip()).strip("_")
            filename = f"{safe_name}_service_history.txt"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(report_text)
            print(f"  Saved output/service_history/{filename}")
            print(f"\nDone - report saved to output/service_history/")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("service_history")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
