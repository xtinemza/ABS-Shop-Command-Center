"""
Router: Module 12 — Warranty Tracker
POST /api/warranty/claims
POST /api/warranty/report
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


class WarrantyClaimsRequest(BaseModel):
    action: Optional[str] = "list"     # add, update, list
    claim_id: Optional[str] = ""
    customer: Optional[str] = ""
    vehicle: Optional[str] = ""
    service_date: Optional[str] = ""   # install_date
    service: Optional[str] = ""        # part name
    part_number: Optional[str] = ""
    part_name: Optional[str] = ""      # alias for service/part
    vendor: Optional[str] = ""
    warranty_period_days: Optional[int] = 365
    claim_date: Optional[str] = ""     # failure_date
    status: Optional[str] = ""
    notes: Optional[str] = ""
    cost: Optional[float] = 0.0


class WarrantyReportRequest(BaseModel):
    period: Optional[str] = "all"      # month, quarter, year, all
    status: Optional[str] = ""         # open, closed, ""


@router.post("/warranty/claims", response_model=ModuleResponse)
def warranty_claims(body: WarrantyClaimsRequest, user=Depends(get_current_user)): 
    try:
        from warranty import track_claims
        from datetime import datetime

        claims = track_claims.load_claims()
        profile = track_claims.load_profile()

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "warranty")
        )
        os.makedirs(output_dir, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        part_name = body.part_name or body.service or ""

        args = argparse.Namespace(
            action=body.action or "list",
            claim_id=body.claim_id or "",
            part=part_name,
            part_number=body.part_number or "",
            vendor=body.vendor or "",
            install_date=body.service_date or today,
            failure_date=body.claim_date or today,
            warranty_period_days=body.warranty_period_days or 365,
            cost=body.cost or 0.0,
            vehicle=body.vehicle or "",
            customer=body.customer or "",
            description=body.notes or "",
            status=body.status or "",
            notes=body.notes or "",
            reimbursement=0.0,
        )

        def run():
            action = args.action
            print(f"\nWarranty claims action: {action}")
            print()

            if action in ("add", "new"):
                args.action = "add"
                track_claims.main.__globals__["claims"] = claims
                # Call the add logic directly
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                # Build claim ID
                existing_ids = [c["id"] for c in claims if c["id"].startswith("WC-")]
                next_num = len(existing_ids) + 1
                claim_id = f"WC-{next_num:03d}"

                claim = {
                    "id": claim_id,
                    "part": args.part,
                    "part_number": args.part_number,
                    "vendor": args.vendor,
                    "install_date": args.install_date,
                    "failure_date": args.failure_date,
                    "warranty_period_days": args.warranty_period_days,
                    "cost": args.cost,
                    "vehicle": args.vehicle,
                    "customer": args.customer,
                    "description": args.description,
                    "status": "New",
                    "reimbursement": 0.0,
                    "created_date": today,
                    "history": [{
                        "date": now_str,
                        "status": "New",
                        "note": f"Claim opened. Part: {args.part}. Vehicle: {args.vehicle}."
                    }]
                }
                claims.append(claim)
                track_claims.save_claims(claims)
                print(f"  Claim {claim_id} added for {args.part} | {args.vendor}")
                print(f"  Vehicle: {args.vehicle}")
                print(f"  Cost: ${args.cost:,.2f}")

            elif action == "update":
                track_claims.main.__globals__["claims"] = claims
                for claim in claims:
                    if claim["id"].upper() == args.claim_id.upper():
                        old_status = claim["status"]
                        if args.status:
                            claim["status"] = args.status
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                        note = args.notes or f"Status: {old_status} -> {claim['status']}"
                        claim["history"].append({"date": now_str, "status": claim["status"], "note": note})
                        track_claims.save_claims(claims)
                        print(f"  Claim {claim['id']} updated to status: {claim['status']}")
                        break
                else:
                    print(f"  Claim {args.claim_id} not found.")

            elif action == "list":
                if not claims:
                    print("  No warranty claims on file.")
                    return
                status_filter = args.status.lower() if args.status else ""
                if status_filter in ("open", "active"):
                    display = [c for c in claims if c["status"] in track_claims.OPEN_STATUSES]
                elif status_filter in ("closed", "resolved"):
                    display = [c for c in claims if c["status"] in track_claims.CLOSED_STATUSES]
                else:
                    display = claims
                print(f"  {len(display)} claims")
                for c in display:
                    age = track_claims.days_old(c["created_date"])
                    flag = track_claims.age_flag(age)
                    print(f"\n  {c['id']}  |  {c['status']}{flag}")
                    print(f"  Part    : {c['part']}")
                    print(f"  Vendor  : {c['vendor']}")
                    print(f"  Cost    : ${c['cost']:,.2f}")
                    print(f"  Opened  : {c['created_date']}  ({age} days ago)")

            else:
                print(f"  Unknown action: {action}")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("warranty")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))


@router.post("/warranty/report", response_model=ModuleResponse)
def warranty_report(body: WarrantyClaimsRequest, user=Depends(get_current_user)): 
    try:
        from warranty import generate_warranty_report

        profile = generate_warranty_report.load_profile()
        claims = generate_warranty_report.load_claims()

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "warranty")
        )
        os.makedirs(output_dir, exist_ok=True)

        args = argparse.Namespace(
            period=body.period or "all",
            status=body.status or "",
        )

        def run():
            print(f"\nGenerating warranty report")
            print(f"   Period : {args.period}")
            print()
            generate_warranty_report.main_logic(claims, profile, args, output_dir)

        # Try calling main_logic if it exists, else use main()
        if hasattr(generate_warranty_report, "main_logic"):
            stdout, error = capture_output(run)
        else:
            # Fall back: call main() via sys.argv substitution
            import io
            buf = io.StringIO()
            old_argv = sys.argv
            try:
                sys.argv = ["generate_warranty_report.py", "--period", args.period]
                if args.status:
                    sys.argv += ["--status", args.status]
                with __import__("contextlib").redirect_stdout(buf):
                    try:
                        generate_warranty_report.main()
                    except SystemExit:
                        pass
                stdout = buf.getvalue()
                error = None
            except Exception as exc:
                stdout = buf.getvalue()
                error = str(exc)
            finally:
                sys.argv = old_argv

        file_paths, content_map = read_output_files("warranty")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
