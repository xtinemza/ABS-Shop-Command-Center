"""
Router: Module 6 — Estimate Narrator
POST /api/estimates/generate
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


class EstimateRequest(BaseModel):
    customer: Optional[str] = ""
    vehicle: Optional[str] = ""
    items: Optional[str] = "[]"


@router.post("/estimates/generate", response_model=ModuleResponse)
def generate_estimate(body: EstimateRequest, user=Depends(get_current_user)): 
    try:
        from estimates import narrate_estimate

        profile = narrate_estimate.load_profile()
        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "estimates")
        )
        os.makedirs(output_dir, exist_ok=True)

        args = argparse.Namespace(
            customer=body.customer or "",
            vehicle=body.vehicle or "",
            items=body.items or "[]",
            output="narrated_estimate.txt",
        )

        def run():
            print(f"\nGenerating narrated estimate")
            print(f"   Customer : {args.customer or 'Not specified'}")
            print(f"   Vehicle  : {args.vehicle or 'Not specified'}")
            print()

            doc = narrate_estimate.build_document(profile, args)
            filename = "narrated_estimate.txt"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(doc)
            print(f"  Saved output/estimates/{filename}")
            print(f"\nDone - estimate saved.")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("estimates")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
