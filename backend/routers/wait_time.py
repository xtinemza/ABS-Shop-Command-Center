"""
Router: Module 3 — Wait Time Communications
POST /api/wait-time/generate
KB: wait_time.json | Gemini: generates in-service status update messages
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

STATUSES = {
    "all":                  "All status updates (checked-in, in-progress, needs approval, parts delay, ready, extended delay)",
    "checked_in":           "Vehicle Checked In — sent immediately on drop-off",
    "in_progress":          "Work In Progress — tech has started the job",
    "needs_approval":       "Additional Work Found — needs customer go/no-go before proceeding",
    "parts_delay":          "Parts Delay — ordered part won't arrive same day",
    "ready_for_pickup":     "Vehicle Ready — all work complete, customer can pick up",
    "extended_delay":       "Extended Delay — job cannot be completed same day as promised",
    "drop_off_confirmation":"Drop-Off Confirmation — vehicle received",
    "inspection_update":    "Inspection Update — findings ready to review",
    "repair_in_progress":   "Repair In Progress — active work underway",
    "delayed_notification": "Delay Notification — timeline has changed",
}


class WaitTimeRequest(BaseModel):
    status:        Optional[str] = "all"
    service_type:  Optional[str] = ""
    customer_name: Optional[str] = ""
    eta:           Optional[str] = ""
    amount_due:    Optional[str] = ""


@router.post("/wait-time/generate", response_model=ModuleResponse)
def generate_wait_time(body: WaitTimeRequest, user=Depends(get_current_user)):
    try:
        profile  = load_profile(user.id)
        ctx      = shop_context(profile)
        wt_kb    = kb("wait_time")

        shop_name = profile.get("shop_name") or "our shop"
        phone     = profile.get("phone") or ""

        status       = (body.status or "all").strip()
        service_type = (body.service_type or "").strip()
        customer     = (body.customer_name or "").strip()
        eta          = (body.eta or "").strip()
        amount_due   = (body.amount_due or "").strip()

        time_context = ""
        if wt_kb and service_type:
            estimates = wt_kb.get("service_time_estimates", {})
            key = service_type.lower().replace(" ", "_").replace("-", "_")
            est = estimates.get(key, "")
            if est:
                time_context = f"Typical time for {service_type}: {est}"

        comm_rules = ""
        if wt_kb:
            rules = wt_kb.get("communication_rules", [])
            comm_rules = "\n".join(f"- {r}" for r in rules[:4])

        generate_all = status == "all"

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You write in-service status update messages for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"These messages are sent to customers while their vehicle is being serviced. "
            f"They should be clear, reassuring, and proactive.\n\n"
            f"Communication rules:\n{comm_rules}\n\n"
            f"RULES:\n"
            f"- SMS messages must be under 160 characters\n"
            f"- Always use the real shop name: {shop_name} and phone: {phone}\n"
            f"- Ready-for-pickup messages must include total amount due and closing hours placeholder\n"
            f"- Needs-approval messages must include the specific issue found and cost\n"
            f"- Use [CUSTOMER NAME], [AMOUNT], [TIME], [SERVICE] as the only live placeholders\n"
        )

        if generate_all:
            status_keys = ["checked_in", "in_progress", "needs_approval",
                           "parts_delay", "ready_for_pickup", "extended_delay"]
            status_lines = "\n".join(
                f"  {i+1}. {STATUSES[s]} (label: ## {s.upper()})"
                for i, s in enumerate(status_keys)
            )
            prompt = (
                (f"Service type: {service_type}\n" if service_type else "")
                + (f"Customer name: {customer}\n" if customer else "")
                + (f"ETA / completion time: {eta}\n" if eta else "")
                + (f"Amount due: {amount_due}\n" if amount_due else "")
                + (f"{time_context}\n" if time_context else "")
                + f"\nGenerate one SMS message for each status type:\n{status_lines}\n\n"
                + "Each SMS must be under 160 characters and feel like a real person sent it."
            )
        else:
            status_label = STATUSES.get(status, status)
            prompt = (
                f"Status type: {status_label}\n"
                + (f"Service type: {service_type}\n" if service_type else "")
                + (f"Customer name: {customer}\n" if customer else "")
                + (f"ETA / completion time: {eta}\n" if eta else "")
                + (f"Amount due: {amount_due}\n" if amount_due else "")
                + (f"{time_context}\n" if time_context else "")
                + f"\nGenerate 3 SMS variations and one phone script for this status.\n"
                + f"Label: ## SMS VARIATIONS and ## PHONE SCRIPT"
            )

        text, err = call_gemini(client, system, prompt, max_tokens=1200)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        content_map = {"wait_time_messages.txt": text}
        output_log  = f"Generated wait-time messages — Status: {status}" + (f" | {service_type}" if service_type else "")

        return ModuleResponse(success=True, output=output_log, files=["wait_time_messages.txt"],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
