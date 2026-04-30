"""
Router: Module 16 — Technician Productivity
POST /api/tech/summary
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


class TechSummaryRequest(BaseModel):
    period: Optional[str] = "week"    # week, day, month
    date: Optional[str] = ""
    technicians: Optional[str] = "[]"  # JSON array of tech data objects


@router.post("/tech/summary", response_model=ModuleResponse)
def tech_summary(body: TechSummaryRequest, user=Depends(get_current_user)): 
    try:
        from tech_productivity import generate_summary

        profile = generate_summary.load_profile()
        shop_name = profile.get("shop_name") or "Your Shop"

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "tech_productivity")
        )
        os.makedirs(output_dir, exist_ok=True)

        from datetime import datetime
        period = body.period or "week"
        date_str = body.date or datetime.now().strftime("%Y-%m-%d")
        technicians_json = body.technicians or "[]"

        def run():
            import json as _json

            print(f"\nGenerating technician productivity report")
            print(f"   Period : {period}")
            print(f"   Date   : {date_str}")
            print()

            try:
                techs = _json.loads(technicians_json)
            except Exception as e:
                print(f"  ERROR: Could not parse technicians JSON: {e}")
                return

            if not techs:
                # Try saved data
                all_data = generate_summary.load_tech_data()
                techs = [t for t in all_data if t.get("period") == period and t.get("date") == date_str]
                if not techs:
                    techs = all_data
                if not techs:
                    print("  No technician data. Provide technicians JSON to generate a report.")
                    return

            plabel = generate_summary.period_label(period, date_str)
            pslug = generate_summary.period_slug(period, date_str)

            report = generate_summary.build_report(techs, period, date_str, shop_name, plabel)
            print(report)

            filename = f"productivity_report_{pslug}.txt"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(report)
            print(f"\nSaved: output/tech_productivity/{filename}")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("tech_productivity")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
