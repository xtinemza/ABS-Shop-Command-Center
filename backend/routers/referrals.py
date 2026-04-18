"""
Router: Module 15 — Referral Tracking
POST /api/referrals/track
POST /api/referrals/rewards
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


class ReferralTrackRequest(BaseModel):
    action: Optional[str] = "list"          # add, list, update, report
    referrer_name: Optional[str] = ""
    referrer_phone: Optional[str] = ""
    referred_name: Optional[str] = ""
    referred_phone: Optional[str] = ""
    service_date: Optional[str] = ""
    service: Optional[str] = ""
    reward_issued: Optional[str] = ""
    notes: Optional[str] = ""
    referral_id: Optional[str] = ""
    filter: Optional[str] = ""             # pending_rewards, etc.


class ReferralRewardsRequest(BaseModel):
    referrer_name: Optional[str] = "Referrer"
    referrer_phone: Optional[str] = ""
    reward_type: Optional[str] = "discount"
    reward_value: Optional[str] = "$25 off your next service"
    referred_by: Optional[str] = ""
    referred_name: Optional[str] = ""
    referred_phone: Optional[str] = ""
    referee_reward: Optional[str] = ""


@router.post("/referrals/track", response_model=ModuleResponse)
def track_referrals(body: ReferralTrackRequest):
    try:
        from referrals import track_referrals as tr_module
        from datetime import datetime

        referrals = tr_module.load_referrals()
        profile = tr_module.load_profile()

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "referrals")
        )
        os.makedirs(output_dir, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")

        def run():
            action = body.action or "list"
            print(f"\nReferral action: {action}")
            print()

            if action == "add":
                existing_ids = [r.get("id", "R-000") for r in referrals]
                next_num = len(referrals) + 1
                ref_id = f"R-{next_num:03d}"

                record = {
                    "id": ref_id,
                    "referrer_name": body.referrer_name or "",
                    "referrer_phone": body.referrer_phone or "",
                    "referred_name": body.referred_name or "",
                    "referred_phone": body.referred_phone or "",
                    "service_date": body.service_date or today,
                    "service": body.service or "",
                    "reward_issued": "no",
                    "notes": body.notes or "",
                    "date_logged": today,
                }
                referrals.append(record)
                tr_module.save_referrals(referrals)
                print(f"  Referral {ref_id} added")
                print(f"  Referrer : {body.referrer_name}")
                print(f"  Referred : {body.referred_name}")
                print(f"  Date     : {body.service_date or today}")

            elif action == "update":
                ref_id = body.referral_id or ""
                for ref in referrals:
                    if ref.get("id", "").upper() == ref_id.upper():
                        if body.reward_issued:
                            ref["reward_issued"] = body.reward_issued
                        if body.notes:
                            ref["notes"] = body.notes
                        tr_module.save_referrals(referrals)
                        print(f"  Referral {ref_id} updated")
                        break
                else:
                    print(f"  Referral {ref_id} not found.")

            elif action == "list":
                filter_val = body.filter or ""
                if filter_val == "pending_rewards":
                    display = [r for r in referrals if r.get("reward_issued", "no").lower() != "yes"]
                    label = "Pending Rewards"
                else:
                    display = referrals
                    label = "All Referrals"
                print(f"  {label}: {len(display)} records")
                for r in display[-20:]:
                    print(f"\n  {r.get('id','?')}  {r.get('referrer_name','')} → {r.get('referred_name','')}")
                    print(f"  Date: {r.get('service_date','')} | Reward: {r.get('reward_issued','no')}")

            elif action == "report":
                total = len(referrals)
                rewarded = sum(1 for r in referrals if r.get("reward_issued", "no").lower() == "yes")
                pending = total - rewarded
                referrer_counts = {}
                for r in referrals:
                    name = r.get("referrer_name", "Unknown")
                    referrer_counts[name] = referrer_counts.get(name, 0) + 1
                top = sorted(referrer_counts.items(), key=lambda x: -x[1])[:5]

                report_lines = [
                    f"REFERRAL PROGRAM REPORT",
                    f"{'=' * 50}",
                    f"Total Referrals  : {total}",
                    f"Rewards Issued   : {rewarded}",
                    f"Pending Rewards  : {pending}",
                    f"",
                    f"TOP REFERRERS:",
                ]
                for name, count in top:
                    report_lines.append(f"  {name:<30} {count} referral(s)")
                report_text = "\n".join(report_lines)

                filename = "referral_report.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as fh:
                    fh.write(report_text)
                print(report_text)
                print(f"\n  Saved output/referrals/{filename}")

            else:
                print(f"  Unknown action: {action}")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("referrals")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))


@router.post("/referrals/rewards", response_model=ModuleResponse)
def generate_referral_rewards(body: ReferralRewardsRequest):
    try:
        from referrals import generate_rewards

        profile = generate_rewards.load_profile()

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "referrals")
        )
        os.makedirs(output_dir, exist_ok=True)

        args = argparse.Namespace(
            referrer_name=body.referrer_name or "Referrer",
            referrer_phone=body.referrer_phone or "",
            referred_name=body.referred_name or body.referred_by or "",
            referred_phone=body.referred_phone or "",
            reward_type=body.reward_type or "discount",
            reward_value=body.reward_value or "$25 off your next service",
            referee_reward=body.referee_reward or "",
            # Legacy compat
            referrer=body.referrer_name or "",
            referee=body.referred_name or "",
            reward=body.reward_value or "",
            referred_by=body.referred_by or "",
        )

        old_argv = sys.argv
        try:
            sys.argv = [
                "generate_rewards.py",
                "--referrer_name", args.referrer_name,
                "--referred_name", args.referred_name or "New Customer",
                "--reward_value", args.reward_value,
                "--reward_type", args.reward_type,
            ]
            if args.referrer_phone:
                sys.argv += ["--referrer_phone", args.referrer_phone]
            if args.referee_reward:
                sys.argv += ["--referee_reward", args.referee_reward]

            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    generate_rewards.main()
                except SystemExit:
                    pass
            stdout = buf.getvalue()
            error = None
        except Exception as exc:
            stdout = ""
            error = str(exc)
        finally:
            sys.argv = old_argv

        file_paths, content_map = read_output_files("referrals")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
