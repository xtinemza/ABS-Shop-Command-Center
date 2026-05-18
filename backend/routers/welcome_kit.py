"""
Router: Module 2 — New Customer Welcome Kit
POST /api/welcome-kit/generate
KB: welcome_kit.json | Gemini: generates personalized welcome kit components
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

COMPONENTS = {
    "welcome_letter":      "A warm, personal welcome letter (3–4 paragraphs) from the shop owner",
    "first_visit_discount":"A discount coupon block — clear offer, value, expiry, and how to redeem",
    "referral_card":       "A referral offer card — both referrer and referee rewards, redemption instructions",
    "what_to_expect":      "A 'What to Expect' section — 4–5 bullet points covering the shop's service promise",
    "follow_up_sms":       "A follow-up SMS (under 160 chars) to send 3 days after the first visit",
}


class WelcomeKitRequest(BaseModel):
    component:        Optional[str] = "all"
    discount:         Optional[str] = ""
    referral_offer:   Optional[str] = ""
    service_performed:Optional[str] = ""
    customer_name:    Optional[str] = ""


@router.post("/welcome-kit/generate", response_model=ModuleResponse)
def generate_welcome_kit(body: WelcomeKitRequest, user=Depends(get_current_user)):
    try:
        profile  = load_profile(user.id)
        ctx      = shop_context(profile)
        kit_kb   = kb("welcome_kit")

        shop_name = profile.get("shop_name") or "our shop"
        phone     = profile.get("phone") or ""
        owner     = profile.get("owner_name") or f"The Team at {shop_name}"
        address   = profile.get("address") or profile.get("location") or ""

        component  = (body.component or "all").strip()
        discount   = body.discount or kit_kb.get("default_offers", {}).get("first_visit_discount", {}).get("amount", "10%") if kit_kb else "10%"
        referral   = body.referral_offer or "$25 off for you, $25 off for your referral"
        service    = body.service_performed or ""
        customer   = body.customer_name or ""

        if component == "all":
            selected = list(COMPONENTS.keys())
        else:
            selected = [component] if component in COMPONENTS else list(COMPONENTS.keys())

        # Pull KB tone guidance
        tone_guide = ""
        if kit_kb:
            tg = kit_kb.get("tone_guidelines", {})
            tone_guide = (
                f"Voice: {tg.get('voice', 'warm and local')}\n"
                f"Avoid: {', '.join(tg.get('avoid', []))}\n"
                f"Must include: {', '.join(tg.get('must_include', []))}"
            )

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You are writing new customer welcome kit content for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"Tone: {tone_guide or 'Warm, local, trustworthy — like a neighbor who knows cars. Never corporate.'}\n\n"
            f"RULES:\n"
            f"- Use the real shop name: {shop_name}\n"
            f"- Owner sign-off: {owner}\n"
            f"- Phone: {phone} | Address: {address}\n"
            f"- Never use generic placeholders — fill in all real shop details\n"
            f"- Content must be ready to print or email with zero editing\n"
        )

        comp_list = "\n".join(f"  {i+1}. {COMPONENTS[c]} (label: ## {c.upper()})" for i, c in enumerate(selected))

        prompt = (
            (f"Customer name: {customer}\n" if customer else "")
            + (f"Service just performed: {service}\n" if service else "")
            + f"Discount offer: {discount} off first service\n"
            + f"Referral offer: {referral}\n\n"
            + f"Generate the following welcome kit components:\n{comp_list}\n\n"
            + f"Label each section with ## COMPONENT_NAME. Make every word feel like it came from "
            + f"a real local shop owner who genuinely cares about the customer."
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1800)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        content_map = {"welcome_kit.txt": text}
        output_log = f"Generated welcome kit for {shop_name}\nComponents: {', '.join(selected)}"

        return ModuleResponse(success=True, output=output_log, files=["welcome_kit.txt"],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
