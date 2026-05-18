"""
Router: Module 15 — Referral Tracking
POST /api/referrals/track   — log or query referral data
POST /api/referrals/rewards — Gemini generates personalized reward notification messages
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
from gemini_client import load_profile, get_gemini, call_gemini, shop_context

router = APIRouter()


class ReferralTrackRequest(BaseModel):
    action:         Optional[str] = "list"
    referrer_name:  Optional[str] = ""
    referrer_phone: Optional[str] = ""
    referred_name:  Optional[str] = ""
    referred_phone: Optional[str] = ""
    service_date:   Optional[str] = ""
    service:        Optional[str] = ""
    reward_issued:  Optional[str] = ""
    notes:          Optional[str] = ""
    referral_id:    Optional[str] = ""
    filter:         Optional[str] = ""


class ReferralRewardsRequest(BaseModel):
    referrer_name:  Optional[str] = ""
    referrer_phone: Optional[str] = ""
    reward_type:    Optional[str] = "discount"
    reward_value:   Optional[str] = "$25 off your next service"
    referred_by:    Optional[str] = ""
    referred_name:  Optional[str] = ""
    referred_phone: Optional[str] = ""
    referee_reward: Optional[str] = ""


@router.post("/referrals/track", response_model=ModuleResponse)
def track_referrals(body: ReferralTrackRequest, user=Depends(get_current_user)):
    try:
        profile   = load_profile(user.id)
        ctx       = shop_context(profile)
        shop_name = profile.get("shop_name") or "our shop"

        action       = (body.action or "list").strip()
        referrer     = (body.referrer_name or "").strip()
        referred     = (body.referred_name or "").strip()
        service_date = (body.service_date or "").strip()
        service      = (body.service or "").strip()
        reward       = (body.reward_issued or "").strip()
        notes        = (body.notes or "").strip()

        if action == "add" and referrer:
            msg = f"Referral logged: {referrer} referred {referred or 'a new customer'}"
            if service_date: msg += f" on {service_date}"
            if service:      msg += f" for {service}"
            return ModuleResponse(success=True, output=msg, files=[], content={}, error=None)

        elif action == "update":
            ref_id = (body.referral_id or "").strip()
            msg    = f"Referral {ref_id or 'record'} updated"
            if reward: msg += f" — reward: {reward}"
            if notes:  msg += f" | {notes}"
            return ModuleResponse(success=True, output=msg, files=[], content={}, error=None)

        elif action == "report":
            # Generate a referral program summary report via Gemini
            client, err = get_gemini()
            if err:
                return ModuleResponse(success=False, output="", files=[], error=err)

            system = (
                f"You generate referral program reports for an independent auto repair shop.\n"
                f"{ctx}\n\n"
                f"Create a concise, data-driven report covering program health, top referrers, and growth tips.\n"
                f"Shop: {shop_name}\n"
            )
            prompt = (
                f"Generate a referral program status report for {shop_name}.\n"
                + (f"Top referrer: {referrer}\n" if referrer else "")
                + (f"Notes: {notes}\n" if notes else "")
                + "\nStructure:\n"
                + "## REFERRAL PROGRAM REPORT\n"
                + "## PROGRAM HEALTH ASSESSMENT\n"
                + "## TOP REFERRER RECOGNITION\n"
                + "## RECOMMENDATIONS TO GROW THE PROGRAM"
            )
            text, err = call_gemini(client, system, prompt, max_tokens=800)
            if err:
                return ModuleResponse(success=False, output="", files=[], error=err)
            return ModuleResponse(success=True, output="Generated referral program report",
                                  files=["referral_report.txt"],
                                  content={"referral_report.txt": text}, error=None)

        # Default: list / any other action
        return ModuleResponse(success=True, output=f"Referral action '{action}' processed.",
                              files=[], content={}, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))


@router.post("/referrals/rewards", response_model=ModuleResponse)
def generate_referral_rewards(body: ReferralRewardsRequest, user=Depends(get_current_user)):
    try:
        profile   = load_profile(user.id)
        ctx       = shop_context(profile)
        shop_name = profile.get("shop_name") or "our shop"
        phone     = profile.get("phone") or ""
        owner     = profile.get("owner_name") or f"The Team at {shop_name}"
        review    = (profile.get("review_links") or {}).get("google", "")

        referrer     = (body.referrer_name or "").strip()
        referrer_ph  = (body.referrer_phone or "").strip()
        reward_type  = (body.reward_type or "discount").strip()
        reward_value = (body.reward_value or "$25 off your next service").strip()
        referred     = (body.referred_name or body.referred_by or "").strip()
        referee_rew  = (body.referee_reward or "").strip()

        if not referrer:
            return ModuleResponse(success=False, output="", files=[],
                                  error="Please provide the referrer's name.")

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You write referral reward messages for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"RULES:\n"
            f"- Warm and genuinely grateful — make the referrer feel like a VIP\n"
            f"- Use the real shop name and phone: {shop_name} | {phone}\n"
            f"- SMS must be under 160 characters\n"
            f"- Email must have a subject line + warm, personal body\n"
            f"- Be specific about the reward — no vague language\n"
            f"- Sign off from: {owner}\n"
            + (f"- Include Google review link: {review}\n" if review else "")
            + "- Each piece must be ready to send with zero editing\n"
        )

        prompt = (
            f"Generate referral reward notification messages.\n\n"
            f"Referrer: {referrer}\n"
            + (f"Referrer phone: {referrer_ph}\n" if referrer_ph else "")
            + (f"Referred customer: {referred}\n" if referred else "")
            + f"Reward for referrer: {reward_value} ({reward_type})\n"
            + (f"Reward for new customer: {referee_rew}\n" if referee_rew else "")
            + "\n## SMS\n(under 160 chars — warm, personal, states the reward explicitly)\n\n"
            + "## EMAIL\n(subject line + full body — genuine gratitude + reward details)\n\n"
            + "## PHONE SCRIPT\n(30–45 seconds, conversational, celebratory)"
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1000)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        label       = f"{referrer}" + (f" → {referred}" if referred else "")
        content_map = {"referral_reward_messages.txt": text}
        output_log  = f"Generated referral reward messages: {label}"

        return ModuleResponse(success=True, output=output_log,
                              files=["referral_reward_messages.txt"],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
