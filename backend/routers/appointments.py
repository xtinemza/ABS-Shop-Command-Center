"""
Router: Module 1 — Appointment Reminders
POST /api/appointments/generate
KB: appointments.json | Gemini: generates personalized multi-channel touchpoint copy
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

TOUCHPOINTS = {
    "booking_confirmation": "Booking Confirmation — sent immediately after scheduling",
    "day_before_reminder":  "Day-Before Reminder — sent 24 hours before the appointment",
    "morning_reminder":     "Morning-Of Reminder — sent 2 hours before (SMS only)",
    "day_after_thank_you":  "Post-Visit Thank-You — sent 24 hours after service completion",
    "review_request":       "Review Request — sent 48 hours after service completion",
    "thirty_day_followup":  "30-Day Follow-Up — check-in one month after service",
    "six_month_maintenance":"6-Month Maintenance Nudge — proactive scheduling prompt",
}

CHANNEL_INSTRUCTIONS = {
    "sms":          "SMS: max 160 characters, warm and brief, one clear action, include shop name and phone",
    "email":        "Email: include subject line, then full body with greeting, 2–3 short paragraphs, and warm sign-off",
    "phone_script": "Phone Script: conversational, under 60 seconds, include customer name placeholder, date/time, and callback number",
}


class AppointmentRequest(BaseModel):
    touchpoint:    Optional[str] = "all"
    customer_name: Optional[str] = ""
    service_type:  Optional[str] = "General Service"
    channels:      Optional[str] = "all"


@router.post("/appointments/generate", response_model=ModuleResponse)
def generate_appointments(body: AppointmentRequest, user=Depends(get_current_user)):
    try:
        profile  = load_profile(user.id)
        ctx      = shop_context(profile)
        appt_kb  = kb("appointments")

        touchpoint   = (body.touchpoint or "all").strip()
        service_type = (body.service_type or "General Service").strip()
        customer     = (body.customer_name or "").strip()
        channels_raw = (body.channels or "all").strip()

        # Resolve channels
        all_channels = ["sms", "email", "phone_script"]
        if channels_raw == "all":
            channels = all_channels
        else:
            channels = [c.strip() for c in channels_raw.split(",") if c.strip() in all_channels]
            if not channels:
                channels = all_channels

        # Resolve touchpoints
        if touchpoint == "all":
            selected_touchpoints = list(TOUCHPOINTS.keys())
        else:
            selected_touchpoints = [touchpoint] if touchpoint in TOUCHPOINTS else list(TOUCHPOINTS.keys())

        # Pull KB context
        channel_rules = ""
        if appt_kb:
            rules = appt_kb.get("channel_rules", {})
            svc_notes = appt_kb.get("service_type_notes", {})
            best_practices = appt_kb.get("reminder_best_practices", [])
            svc_note = svc_notes.get(service_type.lower().replace(" ", "_"), "")
            channel_rules = (
                f"SMS rule: {rules.get('sms', {}).get('tone', '')}, max 160 chars\n"
                f"Email rule: {rules.get('email', {}).get('body_tone', '')}\n"
                f"Phone rule: {rules.get('phone_script', {}).get('tone', '')}\n"
                + (f"Service note: {svc_note}\n" if svc_note else "")
                + (f"Best practices: {'; '.join(best_practices[:3])}" if best_practices else "")
            )

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        shop_name = profile.get("shop_name") or "our shop"
        phone     = profile.get("phone") or ""

        system = (
            f"You are a warm, skilled copywriter for {shop_name}, an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"You write appointment messages that feel like they came from a real person who knows the customer — "
            f"genuine, specific, and local. Never corporate, never robotic, never generic.\n\n"
            f"Channel rules:\n{channel_rules}\n\n"
            f"CRITICAL RULES:\n"
            f"- NEVER write [Shop Name] or any bracket placeholders for the shop — always write: {shop_name}\n"
            f"- NEVER write [Phone Number] — always write: {phone}\n"
            f"- Only use [DATE], [TIME], [CUSTOMER NAME] as placeholders for live appointment data\n"
            f"- SMS: under 160 characters, punchy, one clear action\n"
            f"- Email: ALWAYS write a COMPLETE email — subject line, full greeting, 2–3 warm paragraphs with real substance, "
            f"and a proper sign-off. Do NOT stop at 'Hi [CUSTOMER NAME],' — write the entire body\n"
            f"- Phone script: natural conversation, not a script someone reads robotically\n"
            f"- Every single piece must be ready to send as-is with zero editing\n"
        )

        channel_list = "\n".join(f"  - {CHANNEL_INSTRUCTIONS[c]}" for c in channels)
        tp_list = "\n".join(
            f"  {i+1}. {TOUCHPOINTS[tp]}" for i, tp in enumerate(selected_touchpoints)
        )

        prompt = (
            f"Service type: {service_type}\n"
            + (f"Customer name: {customer}\n" if customer else "")
            + f"\nWrite the following appointment touchpoints for {shop_name}:\n{tp_list}\n\n"
            f"For each touchpoint, generate these channels:\n{channel_list}\n\n"
            f"Label each section clearly (e.g. '## BOOKING CONFIRMATION — EMAIL').\n\n"
            f"IMPORTANT: Write COMPLETE messages. For emails, write the full body — not just a subject line and greeting. "
            f"Each email should have 2–3 real paragraphs that explain the purpose, build rapport, and include a clear next step. "
            f"Make every message feel like it came from a real person at {shop_name} who genuinely cares about the customer's car and safety."
        )

        text, err = call_gemini(client, system, prompt, max_tokens=4000)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        content_map = {"appointment_messages.txt": text}
        output_log = (
            f"Generated appointment reminders for: {service_type}\n"
            f"Touchpoints: {', '.join(selected_touchpoints)}\n"
            f"Channels: {', '.join(channels)}"
        )

        return ModuleResponse(success=True, output=output_log, files=["appointment_messages.txt"],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
