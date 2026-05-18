"""
Router: Module 6 — Estimate Narrator
POST /api/estimates/generate
KB: estimates.json | Gemini: translates technical estimates into plain language
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


class EstimateRequest(BaseModel):
    customer:  Optional[str] = ""
    vehicle:   Optional[str] = ""
    items:     Optional[str] = ""   # free-text or JSON list of line items
    notes:     Optional[str] = ""


@router.post("/estimates/generate", response_model=ModuleResponse)
def generate_estimate(body: EstimateRequest, user=Depends(get_current_user)):
    try:
        if not body.items and not body.notes:
            return ModuleResponse(success=False, output="", files=[],
                                  error="Please provide at least one estimate line item or notes.")

        profile  = load_profile(user.id)
        ctx      = shop_context(profile)
        est_kb   = kb("estimates")

        shop_name = profile.get("shop_name") or "our shop"
        phone     = profile.get("phone") or ""
        customer  = (body.customer or "").strip()
        vehicle   = (body.vehicle or "").strip()
        items     = (body.items or "").strip()
        notes     = (body.notes or "").strip()

        # Build KB context
        translations = ""
        narrative_structure = ""
        warranty_text = ""
        advisor_scripts = ""
        if est_kb:
            trans = est_kb.get("plain_language_translations", {})
            if trans:
                translations = "Plain-language part translations:\n" + "\n".join(
                    f"  {k}: {v}" for k, v in list(trans.items())[:10]
                )
            struct = est_kb.get("estimate_narrative_structure", [])
            if struct:
                narrative_structure = "Narrative structure per item: " + " → ".join(struct)
            warranty_text = est_kb.get("formatting_rules", {}).get("warranty_text", "")
            scripts = est_kb.get("service_advisor_scripts", {})
            if scripts:
                intros = scripts.get("intro", [])
                advisor_scripts = "Advisor intro examples:\n" + "\n".join(f'  "{s}"' for s in intros[:2])

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        system = (
            f"You are a service advisor translator for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"Your job: take technical repair items and write clear, honest, plain-language narratives "
            f"that help customers understand what was found, why it matters, and what happens if they wait.\n\n"
            f"{translations}\n\n"
            f"{narrative_structure}\n\n"
            f"RULES:\n"
            f"- Never use technical jargon without explaining it in plain English first\n"
            f"- Group items by urgency: Safety Critical → High Priority → Schedule Soon → Maintenance\n"
            f"- Include the warranty line: {warranty_text}\n"
            f"- Shop: {shop_name} | Phone: {phone}\n"
            f"- The customer should feel informed and respected, never pressured\n"
            f"- End with a Service Advisor Script section — opening phrases to use when presenting the estimate\n"
        )

        prompt = (
            (f"Customer: {customer}\n" if customer else "")
            + (f"Vehicle: {vehicle}\n" if vehicle else "")
            + f"\nEstimate items / findings:\n{items}\n"
            + (f"\nAdditional notes: {notes}\n" if notes else "")
            + "\nGenerate:\n"
            + "## CUSTOMER ESTIMATE NARRATIVE\n"
            + "  (grouped by urgency, plain language, ready to hand to customer or read aloud)\n\n"
            + "## SERVICE ADVISOR SCRIPT\n"
            + "  (how to open the conversation, how to present each urgency group, closing phrases)\n"
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1600)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        label = f"{customer} — {vehicle}".strip(" —") or "Estimate"
        content_map = {"estimate_narrative.txt": text}
        output_log  = f"Generated estimate narrative for: {label}"

        return ModuleResponse(success=True, output=output_log, files=["estimate_narrative.txt"],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
