"""
Router: Module 17 — Customer Milestones
POST /api/milestones/generate
"""
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


class MilestoneRequest(BaseModel):
    milestone_type: Optional[str] = "anniversary"   # anniversary, visit_count, mileage
    customer_name: Optional[str] = "Customer"
    customer_phone: Optional[str] = ""
    milestone_value: Optional[str] = "1 year"       # "1 year", "10th visit", "100,000 miles"
    vehicle: Optional[str] = ""
    last_service: Optional[str] = ""
    offer: Optional[str] = ""


@router.post("/milestones/generate", response_model=ModuleResponse)
def generate_milestone(body: MilestoneRequest):
    try:
        from milestones import generate_outreach

        profile = generate_outreach.load_profile()
        shop = profile.get("shop_name") or "[Shop Name]"
        phone = profile.get("phone") or "[Phone]"
        website = profile.get("website") or ""
        owner = profile.get("owner_name") or f"The Team at {shop}"
        review_link = (profile.get("review_links") or {}).get("google", "")

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "milestones")
        )
        os.makedirs(output_dir, exist_ok=True)

        # Normalize milestone type
        legacy_map = {
            "1_year_anniversary": ("anniversary", "1 year"),
            "2_year_anniversary": ("anniversary", "2 years"),
            "5_year_anniversary": ("anniversary", "5 years"),
            "5th_visit": ("visit_count", "5th visit"),
            "10th_visit": ("visit_count", "10th visit"),
            "birthday": ("anniversary", "birthday"),
        }
        milestone_type = body.milestone_type or "anniversary"
        milestone_value = body.milestone_value or "1 year"
        if milestone_type in legacy_map:
            milestone_type, default_val = legacy_map[milestone_type]
            if not milestone_value:
                milestone_value = default_val

        customer_name = body.customer_name or "Customer"
        customer_phone = body.customer_phone or ""
        vehicle = body.vehicle or ""
        last_service = body.last_service or ""
        offer = body.offer or ""

        last_service_fmt = generate_outreach.format_last_service(last_service)
        customer_slug = generate_outreach.safe_filename(customer_name)

        def run():
            print(f"\nGenerating milestone outreach")
            print(f"   Milestone : {milestone_type} — {milestone_value}")
            print(f"   Customer  : {customer_name}")
            print(f"   Vehicle   : {vehicle or 'Not specified'}")
            print()

            if milestone_type == "anniversary":
                sms_text, sms_fits, email_subject, email_body, phone_script = (
                    generate_outreach.generate_anniversary(
                        profile, customer_name, customer_phone, milestone_value,
                        vehicle, last_service_fmt, offer, shop, phone, website, owner, review_link
                    )
                )
            elif milestone_type == "visit_count":
                sms_text, sms_fits, email_subject, email_body, phone_script = (
                    generate_outreach.generate_visit_count(
                        profile, customer_name, customer_phone, milestone_value,
                        vehicle, last_service_fmt, offer, shop, phone, website, owner, review_link
                    )
                )
            elif milestone_type == "mileage":
                sms_text, sms_fits, email_subject, email_body, phone_script = (
                    generate_outreach.generate_mileage(
                        profile, customer_name, customer_phone, milestone_value,
                        vehicle, last_service_fmt, offer, shop, phone, website, owner, review_link
                    )
                )
            else:
                print(f"  Unknown milestone type: {milestone_type}")
                return

            generated = []

            # SMS
            sms_file = os.path.join(output_dir, f"milestone_{milestone_type}_{customer_slug}_sms.txt")
            sms_note = f"({len(sms_text)}/160 chars)"
            sms_content = f"SMS — {milestone_type.upper()} MILESTONE: {customer_name}\n{'=' * 55}\n{sms_text}\n\n{sms_note}\n"
            if not sms_fits:
                sms_content += "(Warning: may be over 160 chars after personalization)\n"
            with open(sms_file, "w", encoding="utf-8") as fh:
                fh.write(sms_content)
            generated.append(("SMS", f"milestone_{milestone_type}_{customer_slug}_sms.txt"))
            print(f"  Saved output/milestones/milestone_{milestone_type}_{customer_slug}_sms.txt")

            # Email
            email_file = os.path.join(output_dir, f"milestone_{milestone_type}_{customer_slug}_email.txt")
            email_content = (
                f"EMAIL — {milestone_type.upper()} MILESTONE: {customer_name.upper()}\n{'=' * 55}\n"
                f"SUBJECT: {email_subject}\n{'─' * 55}\n\n{email_body}\n"
            )
            with open(email_file, "w", encoding="utf-8") as fh:
                fh.write(email_content)
            generated.append(("Email", f"milestone_{milestone_type}_{customer_slug}_email.txt"))
            print(f"  Saved output/milestones/milestone_{milestone_type}_{customer_slug}_email.txt")

            # Phone script (major milestones only)
            if phone_script:
                script_file = os.path.join(output_dir, f"milestone_{milestone_type}_{customer_slug}_phone.txt")
                with open(script_file, "w", encoding="utf-8") as fh:
                    fh.write(phone_script)
                generated.append(("Phone Script", f"milestone_{milestone_type}_{customer_slug}_phone.txt"))
                print(f"  Saved output/milestones/milestone_{milestone_type}_{customer_slug}_phone.txt")

            print(f"\nDone - {len(generated)} file(s) saved to output/milestones/")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("milestones")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
