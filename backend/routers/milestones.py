"""
Router: Module 17 — Customer Milestones
POST /api/milestones/generate
KB: milestones | Gemini: generates anniversary, visit, and mileage outreach
"""
import os, sys
from typing import Optional
from fastapi import APIRouter, Depends
from auth import get_current_user
from pydantic import BaseModel

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from models.responses import ModuleResponse
from kb_loader import kb
from gemini_client import load_profile, get_gemini, call_gemini, shop_context

router = APIRouter()


class MilestoneRequest(BaseModel):
    milestone_type:  Optional[str] = "anniversary"
    customer_name:   Optional[str] = ""
    customer_phone:  Optional[str] = ""
    milestone_value: Optional[str] = "1 year"
    vehicle:         Optional[str] = ""
    last_service:    Optional[str] = ""
    offer:           Optional[str] = ""


MILESTONE_CONTEXT = {
    "anniversary": "The customer has been with the shop for a significant amount of time. Celebrate loyalty, express genuine gratitude, invite them back.",
    "visit_count": "The customer has reached a visit milestone. Recognize their loyalty and make them feel like a VIP.",
    "mileage":     "The customer's vehicle has hit a major mileage milestone. Great hook for recommending a comprehensive inspection.",
}


@router.post("/milestones/generate", response_model=ModuleResponse)
def generate_milestone(body: MilestoneRequest, user=Depends(get_current_user)):
    try:
        profile  = load_profile(user.id)
        ctx      = shop_context(profile)

        shop_name = profile.get("shop_name") or "our shop"
        phone     = profile.get("phone") or ""
        owner     = profile.get("owner_name") or f"The Team at {shop_name}"
        review    = (profile.get("review_links") or {}).get("google", "")

        # Normalize milestone type
        mtype = (body.milestone_type or "anniversary").lower()
        legacy = {
            "1_year_anniversary": "anniversary", "2_year_anniversary": "anniversary",
            "5_year_anniversary": "anniversary", "5th_visit": "visit_count",
            "10th_visit": "visit_count", "birthday": "anniversary",
        }
        mtype = legacy.get(mtype, mtype)
        if mtype not in MILESTONE_CONTEXT:
            mtype = "anniversary"

        mvalue   = (body.milestone_value or "1 year").strip()
        customer = (body.customer_name or "").strip()
        vehicle  = (body.vehicle or "").strip()
        last_svc = (body.last_service or "").strip()
        offer    = (body.offer or "").strip()

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You write customer milestone outreach messages for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"Milestone context: {MILESTONE_CONTEXT[mtype]}\n\n"
            f"RULES:\n"
            f"- Warm and genuinely personal — this is a relationship message, not a sales pitch\n"
            f"- Use the real shop name: {shop_name} | Phone: {phone} | Owner: {owner}\n"
            f"- SMS must be under 160 characters\n"
            f"- Email must have a subject line, warm greeting, 2–3 short paragraphs, and sign-off\n"
            f"- Phone script: conversational, under 60 seconds\n"
            + (f"- Include Google review link: {review}\n" if review else "")
            + (f"- Include this offer: {offer}\n" if offer else "")
            + f"- Each piece must be ready to send with zero editing\n"
        )

        prompt = (
            f"Milestone type: {mtype.replace('_', ' ').title()}\n"
            f"Milestone value: {mvalue}\n"
            + (f"Customer name: {customer}\n" if customer else "")
            + (f"Vehicle: {vehicle}\n" if vehicle else "")
            + (f"Last service date: {last_svc}\n" if last_svc else "")
            + "\nGenerate all three outreach pieces:\n\n"
            + "## SMS\n(under 160 characters — warm, personal, includes shop name and phone)\n\n"
            + "## EMAIL\n(subject line + full body)\n\n"
            + "## PHONE SCRIPT\n(conversational, under 60 seconds)"
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1200)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        label = f"{customer} — {mvalue} {mtype}".strip(" —") if customer else f"{mvalue} {mtype}"
        content_map = {"milestone_outreach.txt": text}
        output_log  = f"Generated {mtype.replace('_', ' ')} milestone outreach: {label}"

        return ModuleResponse(success=True, output=output_log, files=["milestone_outreach.txt"],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
