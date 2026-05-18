"""
Router: Module 11 — Parts Inventory
GET  /api/parts/catalog    — get parts catalog
POST /api/parts/catalog    — save parts catalog
POST /api/parts/inventory  — log inventory action or generate inventory report via Gemini
POST /api/parts/po         — Gemini generates a professional purchase order
"""
import os, sys, json as _json
from typing import List, Optional
from fastapi import APIRouter, Depends
from auth import get_current_user
from pydantic import BaseModel

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

_DATA_DIR    = "/data" if os.path.isdir("/data") else os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)
CATALOG_PATH = os.path.join(_DATA_DIR, "parts_catalog.json")

from models.responses import ModuleResponse
from gemini_client import load_profile, get_gemini, call_gemini, shop_context

router = APIRouter()


class CatalogItem(BaseModel):
    brand:       Optional[str] = ""
    part_name:   Optional[str] = ""
    part_number: Optional[str] = ""
    category:    Optional[str] = ""
    unit_cost:   Optional[str] = ""
    vendor:      Optional[str] = ""


class CatalogRequest(BaseModel):
    items: List[CatalogItem]


class PartsInventoryRequest(BaseModel):
    action:           Optional[str]   = "list"    # add, update, reorder_check, list, report
    part_number:      Optional[str]   = ""
    part_name:        Optional[str]   = ""
    category:         Optional[str]   = ""
    quantity:         Optional[int]   = None
    reorder_point:    Optional[int]   = 0
    preferred_vendor: Optional[str]   = ""
    cost:             Optional[float] = None
    inventory_data:   Optional[str]   = ""   # free-text/JSON of current inventory for report mode


class PartsPORequest(BaseModel):
    vendor:         Optional[str] = ""
    items:          Optional[str] = ""    # JSON array of line items, or free-text
    notes:          Optional[str] = ""
    low_stock_data: Optional[str] = ""   # free-text description of what's low


@router.get("/parts/catalog")
def get_catalog(user=Depends(get_current_user)):
    try:
        if not os.path.exists(CATALOG_PATH):
            return {"success": True, "items": [], "count": 0}
        with open(CATALOG_PATH, "r", encoding="utf-8") as fh:
            items = _json.load(fh)
        return {"success": True, "items": items, "count": len(items)}
    except Exception as exc:
        return {"success": False, "items": [], "error": str(exc)}


@router.post("/parts/catalog")
def save_catalog(body: CatalogRequest, user=Depends(get_current_user)):
    try:
        items = [item.dict() for item in body.items]
        os.makedirs(os.path.dirname(CATALOG_PATH), exist_ok=True)
        with open(CATALOG_PATH, "w", encoding="utf-8") as fh:
            _json.dump(items, fh, indent=2, ensure_ascii=False)
        return {"success": True, "count": len(items), "message": f"Saved {len(items)} parts to catalog"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@router.post("/parts/inventory", response_model=ModuleResponse)
def parts_inventory(body: PartsInventoryRequest, user=Depends(get_current_user)):
    try:
        profile        = load_profile(user.id)
        ctx            = shop_context(profile)
        shop_name      = profile.get("shop_name") or "our shop"

        action         = (body.action or "list").strip()
        part_name      = (body.part_name or "").strip()
        part_number    = (body.part_number or "").strip()
        quantity       = body.quantity
        reorder        = body.reorder_point or 0
        vendor         = (body.preferred_vendor or "").strip()
        inventory_data = (body.inventory_data or "").strip()

        # Add / update — confirm without AI
        if action == "add" and part_name:
            msg = f"Part '{part_name}' added to inventory"
            if part_number:         msg += f" (#{part_number})"
            if quantity is not None: msg += f" | Qty: {quantity}"
            if reorder:             msg += f" | Reorder at: {reorder}"
            if vendor:              msg += f" | Vendor: {vendor}"
            return ModuleResponse(success=True, output=msg, files=[], content={}, error=None)

        if action == "update" and (part_name or part_number):
            msg = f"Inventory updated: {part_name or part_number}"
            if quantity is not None: msg += f" | New qty: {quantity}"
            return ModuleResponse(success=True, output=msg, files=[], content={}, error=None)

        # Report / reorder_check — use Gemini
        if action in ("report", "reorder_check"):
            if not inventory_data:
                return ModuleResponse(success=False, output="", files=[],
                                      error="Provide inventory_data to generate an inventory report.")

            client, err = get_gemini()
            if err:
                return ModuleResponse(success=False, output="", files=[], error=err)

            system = (
                f"You generate parts inventory status reports for an independent auto repair shop.\n"
                f"{ctx}\n\n"
                f"Identify critical low-stock, dead inventory, and reorder recommendations by vendor.\n"
                f"Be specific — include part names, numbers, and quantities.\n"
                f"Shop: {shop_name}\n"
            )

            prompt = (
                f"Generate an inventory status report for {shop_name}.\n\n"
                f"Inventory data:\n{inventory_data}\n\n"
                + "Structure:\n"
                + "## INVENTORY STATUS REPORT\n"
                + "## 🔴 CRITICAL — REORDER NOW (at or below minimum threshold)\n"
                + "## 🟡 LOW STOCK — ORDER SOON (within 1 week)\n"
                + "## ✓ WELL STOCKED\n"
                + "## DEAD INVENTORY ALERTS (no movement 90+ days)\n"
                + "## RECOMMENDED PURCHASE ORDERS BY VENDOR"
            )

            text, err = call_gemini(client, system, prompt, max_tokens=1200)
            if err:
                return ModuleResponse(success=False, output="", files=[], error=err)

            content_map = {"inventory_report.txt": text}
            return ModuleResponse(success=True, output="Generated inventory report",
                                  files=["inventory_report.txt"], content=content_map, error=None)

        return ModuleResponse(success=True, output=f"Inventory action '{action}' processed.",
                              files=[], content={}, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))


@router.post("/parts/po", response_model=ModuleResponse)
def generate_po(body: PartsPORequest, user=Depends(get_current_user)):
    try:
        profile    = load_profile(user.id)
        ctx        = shop_context(profile)
        shop_name  = profile.get("shop_name") or "our shop"
        phone      = profile.get("phone") or ""
        address    = profile.get("address") or ""

        vendor     = (body.vendor or "").strip()
        items_str  = (body.items or "").strip()
        notes      = (body.notes or "").strip()
        low_stock  = (body.low_stock_data or "").strip()

        if not items_str and not low_stock:
            return ModuleResponse(success=False, output="", files=[],
                                  error="Provide line items or low_stock_data to generate a PO.")

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        order_context = items_str or low_stock

        system = (
            f"You generate professional purchase orders for an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"Format as a complete, ready-to-send PO with all required fields.\n"
            f"Shop: {shop_name} | Phone: {phone} | Address: {address}\n"
        )

        prompt = (
            f"Generate a purchase order for {shop_name}.\n"
            + (f"Vendor: {vendor}\n" if vendor else "Vendor: [determine from items if possible]\n")
            + f"\nItems / Low stock data:\n{order_context}\n"
            + (f"\nSpecial instructions: {notes}\n" if notes else "")
            + "\nStructure:\n"
            + "## PURCHASE ORDER\n"
            + "  PO Number: [auto-generate sequential]\n"
            + "  Date: [today's date]\n"
            + f"  Ship To: {shop_name} | {address}\n"
            + "  Vendor: [vendor name + contact if known]\n\n"
            + "## LINE ITEMS\n"
            + "  | Part Number | Description | Qty | Unit Cost | Line Total |\n\n"
            + "## ORDER SUBTOTAL\n"
            + "## DELIVERY INSTRUCTIONS\n"
            + f"## AUTHORIZED BY: {shop_name}"
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1000)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        from datetime import datetime
        vendor_safe = (vendor or "vendor").lower().replace(" ", "_")[:20]
        filename    = f"PO_{vendor_safe}_{datetime.now().strftime('%Y%m%d')}.txt"
        content_map = {filename: text}
        output_log  = f"Generated purchase order for {vendor or 'vendor'}"

        return ModuleResponse(success=True, output=output_log, files=[filename],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
