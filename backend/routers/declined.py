"""
Router: Module 4 — Declined Services Follow-Up
POST /api/declined/generate
KB: declined.json | Gemini: generates multi-touch follow-up campaigns
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


class DeclinedRequest(BaseModel):
    service:  str = ""
    urgency:  Optional[str] = "medium"
    touches:  Optional[str] = "1,2,3"
    customer_name: Optional[str] = ""
    price:    Optional[str] = ""
    discount: Optional[str] = ""


@router.post("/declined/generate", response_model=ModuleResponse)
def generate_declined(body: DeclinedRequest, user=Depends(get_current_user)):
    try:
        if not body.service.strip():
            return ModuleResponse(success=False, output="", files=[],
                                  error="Please enter the declined service name.")

        profile    = load_profile(user.id)
        ctx        = shop_context(profile)
        dec_kb     = kb("declined")

        shop_name  = profile.get("shop_name") or "our shop"
        phone      = profile.get("phone") or ""
        service    = body.service.strip()
        urgency    = (body.urgency or "medium").lower().replace("-", "_").replace(" ", "_")
        customer   = (body.customer_name or "").strip()
        price      = (body.price or "").strip()
        discount   = (body.discount or "").strip()

        # Parse touches
        try:
            touch_nums = sorted(set(int(t.strip()) for t in (body.touches or "1,2,3").split(",") if t.strip().isdigit()))
        except Exception:
            touch_nums = [1, 2, 3]
        touch_nums = touch_nums[:4]

        # Pull KB urgency rules
        urgency_data = {}
        if dec_kb:
            urgency_data = dec_kb.get("urgency_levels", {}).get(urgency, {})
        tone       = urgency_data.get("tone", "Caring and helpful")
        offer_disc = urgency_data.get("offer_discount", urgency != "safety_critical")
        cadence    = urgency_data.get("follow_up_cadence_days", [1, 7, 21])

        msg_rules = ""
        if dec_kb:
            rules = dec_kb.get("message_rules", [])
            msg_rules = "\n".join(f"- {r}" for r in rules)

        # Determine offer text
        offer_text = ""
        if offer_disc and urgency != "safety_critical":
            offer_text = discount or urgency_data.get("default_discount", "10% off")

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You write declined service follow-up messages for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"Tone for {urgency.replace('_', ' ')} urgency: {tone}\n\n"
            f"Message rules:\n{msg_rules}\n\n"
            f"RULES:\n"
            f"- Always name the specific service: {service}\n"
            f"- Use the real shop name: {shop_name} and phone: {phone}\n"
            f"- SMS must be under 160 characters\n"
            f"- Never make customer feel judged for declining\n"
            f"- Safety critical items: never offer a discount — focus on risk\n"
            f"- Each touch must be ready to copy-paste\n"
        )

        touches_desc = []
        for i, num in enumerate(touch_nums):
            day = cadence[i] if i < len(cadence) else cadence[-1] if cadence else (num * 7)
            touches_desc.append(f"Touch {num} (Day {day}): {'First follow-up — remind and educate' if num == 1 else 'Second — add value or discount' if num == 2 else 'Third — mild urgency, reiterate risk' if num == 3 else 'Final — phone script for liability documentation'}")

        touches_list = "\n".join(f"  {t}" for t in touches_desc)

        prompt = (
            f"Declined service: {service}\n"
            f"Urgency level: {urgency.replace('_', ' ').title()}\n"
            + (f"Customer name: {customer}\n" if customer else "")
            + (f"Original estimate price: {price}\n" if price else "")
            + (f"Discount offer: {offer_text}\n" if offer_text else "No discount for this urgency level.\n")
            + f"\nGenerate these follow-up touches:\n{touches_list}\n\n"
            + "For each touch, write:\n"
            + "  - SMS (under 160 chars)\n"
            + "  - Email (with subject line and body)\n"
            + "  - Phone script (for Touch 3+ only)\n\n"
            + "Label each section: ## TOUCH 1 — SMS, ## TOUCH 1 — EMAIL, etc."
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1800)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        content_map = {"declined_followup.txt": text}
        output_log  = f"Generated {len(touch_nums)}-touch follow-up for: {service} ({urgency.replace('_', ' ')} urgency)"

        return ModuleResponse(success=True, output=output_log, files=["declined_followup.txt"],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
