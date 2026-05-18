"""
Router: Module 10 — SOP Library
GET  /api/sop/          — list built-in + custom SOPs
POST /api/sop/          — save custom SOPs to Supabase
POST /api/sop/generate  — Gemini generates SOP content
"""
import os, sys
from typing import Optional
from fastapi import APIRouter, Depends
from auth import get_current_user
from supabase_client import supabase
from pydantic import BaseModel

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from models.responses import ModuleResponse
from gemini_client import load_profile, get_gemini, call_gemini, shop_context

router = APIRouter()

# 17 built-in procedures — always visible for every new shop
PROCEDURES = {
    "customer_check_in":         {"title": "Customer Check-In Procedure",             "category": "front-office"},
    "vehicle_inspection":        {"title": "Multi-Point Vehicle Inspection",           "category": "mechanics"},
    "estimate_presentation":     {"title": "Repair Estimate Presentation",             "category": "front-office"},
    "customer_approval":         {"title": "Customer Approval & Authorization",        "category": "front-office"},
    "parts_ordering":            {"title": "Parts Ordering Procedure",                 "category": "inventory"},
    "vehicle_delivery":          {"title": "Vehicle Delivery & Customer Walkthrough",  "category": "front-office"},
    "quality_control":           {"title": "Quality Control & Final Inspection",       "category": "mechanics"},
    "test_drive":                {"title": "Pre- and Post-Repair Test Drive",          "category": "mechanics"},
    "warranty_claim":            {"title": "Warranty Claim Filing Procedure",          "category": "inventory"},
    "complaint_handling":        {"title": "Customer Complaint Resolution",            "category": "front-office"},
    "hazmat_disposal":           {"title": "Hazardous Materials Disposal Compliance",  "category": "operations"},
    "closing_procedure":         {"title": "End-of-Day Shop Closing Procedure",        "category": "operations"},
    "opening_procedure":         {"title": "Shop Opening & Morning Setup",             "category": "operations"},
    "tech_assignment":           {"title": "Technician Job Assignment Workflow",       "category": "mechanics"},
    "upsell_presentation":       {"title": "Service Recommendation & Upsell Script",  "category": "front-office"},
    "loaner_vehicle":            {"title": "Loaner Vehicle Check-Out & Return",        "category": "front-office"},
    "end_of_day_reconciliation": {"title": "End-of-Day Financial Reconciliation",      "category": "operations"},
}


class SopRequest(BaseModel):
    procedure:    Optional[str] = ""    # built-in key, "all", or ""
    category:     Optional[str] = ""
    title:        Optional[str] = ""    # title for custom SOP
    custom:       Optional[str] = ""    # free-form description for custom SOP
    custom_rules: Optional[str] = ""    # shop-specific additions


@router.get("/sop/")
def get_custom_sops(user=Depends(get_current_user)):
    built_in = {k: {"title": v["title"], "category": v["category"]} for k, v in PROCEDURES.items()}
    try:
        res    = supabase.table("profiles").select("sops").eq("id", user.id).execute()
        custom = res.data[0].get("sops", {}) if res.data else {}
    except Exception:
        custom = {}
    return {"built_in": built_in, "custom": custom}


@router.post("/sop/")
def save_custom_sops(sops: dict, user=Depends(get_current_user)):
    try:
        supabase.table("profiles").update({"sops": sops}).eq("id", user.id).execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/sop/generate", response_model=ModuleResponse)
def generate_sop(body: SopRequest, user=Depends(get_current_user)):
    try:
        profile      = load_profile(user.id)
        ctx          = shop_context(profile)
        shop_name    = profile.get("shop_name") or "our shop"
        procedure    = (body.procedure or "").strip()
        custom       = (body.custom or "").strip()
        title        = (body.title or "").strip()
        custom_rules = (body.custom_rules or "").strip()

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        base_system = (
            f"You generate detailed standard operating procedures for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"Write thorough, step-by-step SOPs a real shop employee can follow without guessing.\n"
            f"Use numbered steps. Include who is responsible for each step.\n"
            f"Shop: {shop_name}\n"
            + (f"Shop-specific rules: {custom_rules}\n" if custom_rules else "")
        )

        # Generate all 17 SOPs in one pass
        if procedure == "all":
            prompt = (
                f"Generate all 17 shop SOPs for {shop_name}.\n\n"
                + "\n".join(f"## {v['title']}" for v in PROCEDURES.values())
                + "\n\nFor EACH SOP write:\n"
                + "**Purpose** | **Applies To** | **Steps** (numbered, with responsible party) | **Quality Check**\n"
                + "Separate each SOP with a divider line."
            )
            text, err = call_gemini(client, base_system, prompt, max_tokens=4000)
            if err:
                return ModuleResponse(success=False, output="", files=[], error=err)
            return ModuleResponse(success=True, output=f"Generated all 17 SOPs for {shop_name}",
                                  files=["all_sops.txt"],
                                  content={"all_sops.txt": text}, error=None)

        # Custom free-form SOP
        if custom:
            proc_title = title or "Custom Procedure"
            proc_desc  = custom
        elif procedure and procedure in PROCEDURES:
            proc_title = PROCEDURES[procedure]["title"]
            proc_desc  = f"Standard {proc_title} for an independent auto repair shop"
        elif procedure:
            proc_title = procedure.replace("_", " ").title()
            proc_desc  = f"Standard {proc_title} for an independent auto repair shop"
        else:
            return ModuleResponse(success=False, output="", files=[],
                                  error="Provide a procedure key, a custom description, or use 'all'.")

        prompt = (
            f"Generate a complete Standard Operating Procedure (SOP) for:\n"
            f"**{proc_title}**\n\n"
            f"Context: {proc_desc}\n\n"
            f"Structure:\n"
            f"## {proc_title.upper()} — SOP\n"
            f"**Shop:** {shop_name}\n"
            f"**Purpose:** [1–2 sentences]\n"
            f"**Applies To:** [who follows this SOP]\n"
            f"**Frequency:** [when performed]\n\n"
            f"## PROCEDURE STEPS\n"
            f"(Numbered steps, responsible party in [brackets])\n\n"
            f"## QUALITY CHECKS\n"
            f"## COMMON MISTAKES TO AVOID\n"
            f"## TOOLS & MATERIALS NEEDED"
        )

        text, err = call_gemini(client, base_system, prompt, max_tokens=1400)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        safe_key    = (procedure or title or "custom").lower().replace(" ", "_")[:40]
        filename    = f"sop_{safe_key}.txt"
        content_map = {filename: text}
        output_log  = f"Generated SOP: {proc_title}"

        return ModuleResponse(success=True, output=output_log, files=[filename],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
