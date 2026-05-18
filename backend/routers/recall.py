"""
Router: Module 8 — Recall Notifications
GET  /api/recall/nhtsa-lookup  — live NHTSA API lookup (no AI tokens used)
POST /api/recall/check         — Gemini generates a recall lookup guide
POST /api/recall/notify        — Gemini generates customer notification messages
"""
import os, sys, json as _json, urllib.request, urllib.parse, logging
from typing import Optional
from fastapi import APIRouter, Depends
from auth import get_current_user
from pydantic import BaseModel

logger = logging.getLogger(__name__)

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from models.responses import ModuleResponse
from gemini_client import load_profile, get_gemini, call_gemini, shop_context

router = APIRouter()

_NHTSA_BASE = "https://api.nhtsa.gov/recalls"

URGENCY_GUIDE = {
    "high":   "🔴 SAFETY CRITICAL — contact customer immediately; do not drive vehicle.",
    "medium": "🟠 HIGH PRIORITY — schedule repair within 2 weeks.",
    "low":    "🟡 MONITOR — schedule at next service appointment.",
}


class RecallCheckRequest(BaseModel):
    make:     Optional[str] = ""
    model:    Optional[str] = ""
    year:     Optional[str] = ""
    vin:      Optional[str] = ""
    customer: Optional[str] = ""


class RecallNotifyRequest(BaseModel):
    customer:        Optional[str] = "Customer"
    vehicle:         Optional[str] = "Your Vehicle"
    recall_campaign: Optional[str] = ""
    component:       Optional[str] = ""
    description:     Optional[str] = ""
    consequence:     Optional[str] = ""
    remedy:          Optional[str] = ""
    urgency:         Optional[str] = "medium"


@router.get("/recall/nhtsa-lookup")
def nhtsa_lookup(
    vin:   Optional[str] = None,
    make:  Optional[str] = None,
    model: Optional[str] = None,
    year:  Optional[str] = None,
    user=Depends(get_current_user),
):
    """Live NHTSA recall lookup — VIN or make/model/year. Uses zero AI tokens."""
    try:
        if vin and vin.strip():
            vin_clean = vin.strip().upper()
            if len(vin_clean) != 17:
                return {"success": False, "error": "VIN must be exactly 17 characters.", "recalls": []}
            url = f"{_NHTSA_BASE}/recallsByVehicleId?vin={urllib.parse.quote(vin_clean)}"
        elif make and model and year:
            params = urllib.parse.urlencode({
                "make": make.strip(), "model": model.strip(), "modelYear": year.strip()
            })
            url = f"{_NHTSA_BASE}/recallsByVehicle?{params}"
        else:
            return {"success": False, "error": "Provide a VIN, or make + model + year.", "recalls": []}

        req = urllib.request.Request(
            url, headers={"Accept": "application/json", "User-Agent": "ShopCommandCenter/1.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = _json.loads(resp.read().decode())

        results = data.get("results", [])
        recalls = [
            {
                "campaign":    r.get("NHTSACampaignNumber", ""),
                "component":   r.get("Component", ""),
                "description": r.get("Summary", "") or r.get("Conequence", ""),
                "consequence": r.get("Conequence", "") or r.get("Consequence", ""),
                "remedy":      r.get("Remedy", ""),
                "report_date": r.get("ReportReceivedDate", ""),
            }
            for r in results
        ]
        logger.info("NHTSA lookup returned %d recalls (vin=%s make=%s model=%s year=%s)",
                    len(recalls), vin, make, model, year)
        return {"success": True, "count": len(recalls), "recalls": recalls}

    except urllib.error.URLError as e:
        logger.warning("NHTSA API unreachable: %s", e)
        return {"success": False, "error": "Could not reach the NHTSA API. Check your connection.", "recalls": []}
    except Exception as exc:
        logger.error("NHTSA lookup error: %s", exc)
        return {"success": False, "error": "Recall lookup failed. Please try again.", "recalls": []}


@router.post("/recall/check", response_model=ModuleResponse)
def check_recall(body: RecallCheckRequest, user=Depends(get_current_user)):
    try:
        profile   = load_profile(user.id)
        ctx       = shop_context(profile)
        shop_name = profile.get("shop_name") or "our shop"
        phone     = profile.get("phone") or ""

        make     = (body.make or "").strip()
        model    = (body.model or "").strip()
        year     = (body.year or "").strip()
        vin      = (body.vin or "").strip()
        customer = (body.customer or "").strip()

        vehicle_desc = " ".join(filter(None, [year, make, model])) or vin or "the vehicle"

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You help auto repair shops communicate recall information clearly to customers.\n"
            f"{ctx}\n\n"
            f"Generate a clear, professional recall lookup guide the shop can use as a reference.\n"
            f"Shop: {shop_name} | Phone: {phone}\n"
        )

        prompt = (
            f"Generate a recall lookup reference guide for: {vehicle_desc}\n"
            + (f"Customer: {customer}\n" if customer else "")
            + (f"VIN: {vin}\n" if vin else "")
            + "\nStructure:\n"
            + "## RECALL CHECK — [VEHICLE]\n"
            + "## HOW TO CHECK FOR OPEN RECALLS\n"
            + "  (NHTSA.gov steps, VIN decoder, manufacturer portal)\n"
            + "## WHAT TO DO IF A RECALL IS FOUND\n"
            + "## SCHEDULING RECALL WORK\n"
            + "## SHOP CONTACT"
        )

        text, err = call_gemini(client, system, prompt, max_tokens=800)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        label       = customer or vehicle_desc
        content_map = {"recall_lookup_guide.txt": text}

        return ModuleResponse(success=True, output=f"Generated recall lookup guide: {label}",
                              files=["recall_lookup_guide.txt"], content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))


@router.post("/recall/notify", response_model=ModuleResponse)
def notify_recall(body: RecallNotifyRequest, user=Depends(get_current_user)):
    try:
        profile   = load_profile(user.id)
        ctx       = shop_context(profile)
        shop_name = profile.get("shop_name") or "our shop"
        phone     = profile.get("phone") or ""
        owner     = profile.get("owner_name") or f"The Team at {shop_name}"

        customer    = (body.customer or "Customer").strip()
        vehicle     = (body.vehicle or "Your Vehicle").strip()
        campaign    = (body.recall_campaign or "").strip()
        component   = (body.component or "").strip()
        description = (body.description or "").strip()
        consequence = (body.consequence or "").strip()
        remedy      = (body.remedy or "Manufacturer will repair at no charge.").strip()
        urgency     = (body.urgency or "medium").strip().lower()
        urgency_lbl = URGENCY_GUIDE.get(urgency, URGENCY_GUIDE["medium"])

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You write vehicle recall notifications for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"RULES:\n"
            f"- Be clear and direct — this is a safety matter\n"
            f"- Do NOT cause panic, but convey appropriate urgency\n"
            f"- Educate the customer — explain the recall in plain language\n"
            f"- Position the shop as the customer's safety advocate\n"
            f"- Shop: {shop_name} | Phone: {phone} | Owner: {owner}\n"
            f"- SMS must be under 160 characters\n"
            f"- All pieces must be ready to send with zero editing\n"
        )

        prompt = (
            f"Generate recall notification messages.\n\n"
            f"Customer: {customer}\n"
            f"Vehicle: {vehicle}\n"
            f"Urgency: {urgency_lbl}\n"
            + (f"Recall Campaign #: {campaign}\n" if campaign else "")
            + (f"Component: {component}\n" if component else "")
            + (f"Issue: {description}\n" if description else "")
            + (f"Risk if ignored: {consequence}\n" if consequence else "")
            + f"Remedy: {remedy}\n\n"
            + "## SMS\n(under 160 characters — urgent, clear, shop name + phone)\n\n"
            + "## EMAIL\n(subject line + clear explanation + call to action)\n\n"
            + "## PHONE SCRIPT\n(conversational, under 60 seconds, calm and helpful)\n\n"
            + "## SHOP INTERNAL NOTE\n(one paragraph for the service file)"
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1200)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        safe_campaign = (campaign or "recall").replace("/", "-").replace(" ", "_")
        filename      = f"recall_notification_{safe_campaign}.txt"
        content_map   = {filename: text}
        output_log    = f"Generated recall notifications: {customer} — {vehicle}"

        return ModuleResponse(success=True, output=output_log, files=[filename],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
