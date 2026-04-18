"""
Router: Module 14 — Seasonal Campaigns
POST /api/seasonal/generate
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


class SeasonalRequest(BaseModel):
    season: Optional[str] = "winter"   # winter, spring, summer, fall, holiday
    campaign_type: Optional[str] = ""
    discount: Optional[str] = ""
    expiry: Optional[str] = ""


@router.post("/seasonal/generate", response_model=ModuleResponse)
def generate_seasonal(body: SeasonalRequest):
    try:
        from seasonal import generate_campaign

        profile = generate_campaign.load_profile()
        shop = profile.get("shop_name") or "[Shop Name]"
        phone = profile.get("phone") or "[Phone]"
        website = profile.get("website") or "[Website]"
        owner = profile.get("owner_name") or f"The Team at {shop}"
        review_link = (profile.get("review_links") or {}).get("google", "")

        season = body.season or "winter"
        if season not in generate_campaign.CAMPAIGNS:
            season = "winter"

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "seasonal")
        )
        os.makedirs(output_dir, exist_ok=True)

        import argparse
        args = argparse.Namespace(
            season=season,
            campaign_type=body.campaign_type or "",
            discount=body.discount or "",
            expiry=body.expiry or "",
        )

        def run():
            print(f"\nGenerating seasonal campaign: {season.upper()}")
            print()

            campaign = generate_campaign.CAMPAIGNS[season]
            campaign_name = args.campaign_type or campaign["name"]
            offers = generate_campaign.build_offer_fragments(args.discount, args.expiry)

            # Build services list
            services_list = "\n".join(f"  - {s}" for s in campaign["services"])

            # SMS
            sms_text = campaign["sms_template"].format(
                shop=shop,
                phone=phone,
                website=website,
                offer_fragment=offers["offer_fragment"],
            )
            sms_text, _ = generate_campaign.trim_sms(sms_text)
            sms_note = f"({len(sms_text)}/160 chars)"

            sms_content = (
                f"SMS — {campaign_name.upper()}\n{'=' * 55}\n{sms_text}\n\n{sms_note}\n"
            )
            if args.expiry:
                sms_content += f"Offer expires: {args.expiry}\n"
            sms_file = os.path.join(output_dir, f"{season}_sms.txt")
            with open(sms_file, "w", encoding="utf-8") as fh:
                fh.write(sms_content)
            print(f"  Saved output/seasonal/{season}_sms.txt")

            # Email
            subject = campaign["email_subject"].format(shop=shop)
            body_text = campaign["email_body"].format(
                shop=shop, phone=phone, website=website, owner=owner,
                offer_section=offers["offer_section"]
            )
            email_content = (
                f"EMAIL — {campaign_name.upper()}\n{'=' * 55}\n"
                f"SUBJECT: {subject}\n{'─' * 55}\n\n{body_text}\n"
            )
            if review_link:
                email_content += f"\n[P.S. Leave us a review: {review_link}]\n"
            email_file = os.path.join(output_dir, f"{season}_email.txt")
            with open(email_file, "w", encoding="utf-8") as fh:
                fh.write(email_content)
            print(f"  Saved output/seasonal/{season}_email.txt")

            # Social
            social_text = campaign["social_template"].format(
                shop=shop, phone=phone, offer_line=offers["offer_line"]
            )
            social_file = os.path.join(output_dir, f"{season}_social.txt")
            with open(social_file, "w", encoding="utf-8") as fh:
                fh.write(f"SOCIAL MEDIA — {campaign_name.upper()}\n{'=' * 55}\n{social_text}\n")
            print(f"  Saved output/seasonal/{season}_social.txt")

            # Staff briefing
            briefing = (
                f"STAFF BRIEFING — {campaign_name.upper()}\n{'=' * 55}\n\n"
                f"CAMPAIGN HOOK:\n  \"{campaign['hook']}\"\n\n"
                f"KEY SERVICES TO PROMOTE:\n{services_list}\n\n"
                f"UPSELL TIP:\n  {campaign['upsell_tip']}\n"
            )
            if args.discount:
                briefing += f"\nCURRENT OFFER:\n  {offers['offer_display']}\n"
                if args.expiry:
                    briefing += f"  EXPIRES: {args.expiry}\n"
            briefing_file = os.path.join(output_dir, f"{season}_staff_briefing.txt")
            with open(briefing_file, "w", encoding="utf-8") as fh:
                fh.write(briefing)
            print(f"  Saved output/seasonal/{season}_staff_briefing.txt")

            print(f"\nDone - 4 campaign files saved to output/seasonal/")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("seasonal")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
