"""
Router: Module 7 — Inspection Forms
POST /api/inspection/generate
"""
import argparse
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


class InspectionRequest(BaseModel):
    mode: Optional[str] = "form"          # "form" or "report"
    type: Optional[str] = "multi_point"   # multi_point, pre_purchase, seasonal
    customer: Optional[str] = ""
    vehicle: Optional[str] = ""
    mileage: Optional[int] = None
    results: Optional[str] = ""           # JSON array for report mode


@router.post("/inspection/generate", response_model=ModuleResponse)
def generate_inspection(body: InspectionRequest, user=Depends(get_current_user)): 
    try:
        from inspection import generate_forms

        profile = generate_forms.load_profile()
        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "inspection")
        )
        os.makedirs(output_dir, exist_ok=True)

        mode = body.mode or "form"
        form_type = body.type or "multi_point"

        args = argparse.Namespace(
            mode=mode,
            type=form_type,
            customer=body.customer or "",
            vehicle=body.vehicle or "",
            mileage=str(body.mileage) if body.mileage else None,
            results=body.results or "",
            output="",
        )

        def run():
            print(f"\nGenerating inspection {mode}")
            print(f"   Type     : {form_type}")
            print(f"   Customer : {args.customer or 'Not specified'}")
            print(f"   Vehicle  : {args.vehicle or 'Not specified'}")
            print()

            if mode == "form":
                if form_type not in generate_forms.FORM_TEMPLATES:
                    print(f"  Unknown form type: {form_type}. Using multi_point.")
                    args.type = "multi_point"
                content = generate_forms.generate_blank_form(profile, args)
                filename = f"inspection_form_{form_type}.txt"
            else:
                content, counts = generate_forms.generate_report(profile, args)
                filename = "inspection_report.txt"

            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(content)
            print(f"  Saved output/inspection/{filename}")
            print(f"\nDone - inspection {mode} saved.")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("inspection")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
