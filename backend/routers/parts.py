"""
Router: Module 11 — Parts Inventory
POST /api/parts/inventory
POST /api/parts/po
GET  /api/parts/catalog
POST /api/parts/catalog
"""
import argparse
import json
import os
import sys
from typing import List, Optional

from fastapi import APIRouter, Depends
from auth import get_current_user
from supabase_client import supabase

from pydantic import BaseModel

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

_TOOLS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
if _TOOLS_ROOT not in sys.path:
    sys.path.insert(0, _TOOLS_ROOT)

from models.responses import ModuleResponse
from utils import capture_output, read_output_files

_DATA_DIR = "/data" if os.path.isdir("/data") else os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CATALOG_PATH = os.path.join(_DATA_DIR, "parts_catalog.json")

router = APIRouter()


class CatalogItem(BaseModel):
    brand: Optional[str] = ""
    part_name: Optional[str] = ""
    part_number: Optional[str] = ""
    category: Optional[str] = ""
    unit_cost: Optional[str] = ""
    vendor: Optional[str] = ""


class CatalogRequest(BaseModel):
    items: List[CatalogItem]


@router.get("/parts/catalog")
def get_catalog()user=Depends(get_current_user)):
    try:
        if not os.path.exists(CATALOG_PATH):
            return {"success": True, "items": [], "count": 0}
        with open(CATALOG_PATH, "r", encoding="utf-8") as fh:
            items = json.load(fh)
        return {"success": True, "items": items, "count": len(items)}
    except Exception as exc:
        return {"success": False, "items": [], "error": str(exc)}


@router.post("/parts/catalog")
def save_catalog(body: CatalogItem, user=Depends(get_current_user)): 
    try:
        items = [item.dict() for item in body.items]
        os.makedirs(os.path.dirname(CATALOG_PATH), exist_ok=True)
        with open(CATALOG_PATH, "w", encoding="utf-8") as fh:
            json.dump(items, fh, indent=2, ensure_ascii=False)
        return {"success": True, "count": len(items), "message": f"Saved {len(items)} parts to catalog"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


class PartsInventoryRequest(BaseModel):
    action: Optional[str] = "list"       # add, update, reorder_check, list, report
    part_number: Optional[str] = ""
    part_name: Optional[str] = ""
    category: Optional[str] = ""
    quantity: Optional[int] = None
    reorder_point: Optional[int] = 0
    preferred_vendor: Optional[str] = ""
    cost: Optional[float] = None


class PartsPORequest(BaseModel):
    vendor: Optional[str] = ""
    items: Optional[str] = ""    # JSON array of line items
    notes: Optional[str] = ""


@router.post("/parts/inventory", response_model=ModuleResponse)
def parts_inventory(body: CatalogItem, user=Depends(get_current_user)): 
    try:
        from parts_inventory import track_inventory

        profile = track_inventory.load_profile()
        inventory = track_inventory.load_inventory()

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "parts_inventory")
        )
        os.makedirs(output_dir, exist_ok=True)

        args = argparse.Namespace(
            action=body.action or "list",
            part_number=body.part_number or "",
            part_name=body.part_name or "",
            category=body.category or "",
            quantity=body.quantity if body.quantity is not None else (0 if body.action == "add" else None),
            reorder_point=body.reorder_point or 0,
            preferred_vendor=body.preferred_vendor or "",
            cost=body.cost if body.cost is not None else (0.0 if body.action == "add" else None),
        )

        def run():
            action = args.action
            print(f"\nParts inventory action: {action}")
            print()

            if action == "add":
                track_inventory.action_add(args, inventory)
            elif action == "update":
                track_inventory.action_update(args, inventory)
            elif action == "reorder_check":
                track_inventory.action_reorder_check(inventory)
            elif action == "list":
                track_inventory.action_list(inventory)
            elif action == "report":
                if not inventory:
                    print("No parts in inventory. Use action=add to begin.")
                else:
                    track_inventory.action_report(inventory, profile)
            else:
                print(f"Unknown action: {action}")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("parts_inventory")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))


@router.post("/parts/po", response_model=ModuleResponse)
def generate_po(body: CatalogItem, user=Depends(get_current_user)): 
    try:
        from parts_inventory import generate_po as po_module

        profile = po_module.load_profile()
        inventory = po_module.load_inventory()

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "parts_inventory")
        )
        os.makedirs(output_dir, exist_ok=True)

        vendor = body.vendor or ""
        items_str = body.items or ""
        notes = body.notes or ""

        def run():
            print(f"\nGenerating Purchase Order")
            print(f"   Vendor : {vendor or 'All vendors with low stock'}")
            print()

            if items_str:
                import json as _json
                try:
                    line_items = _json.loads(items_str)
                except Exception as e:
                    print(f"  ERROR: Could not parse items JSON: {e}")
                    return
            else:
                # Auto-generate from low-stock for vendor
                if vendor:
                    vendor_lower = vendor.strip().lower()
                    vendor_parts = [
                        p for p in inventory
                        if vendor_lower in p.get("preferred_vendor", "").lower()
                        and p["quantity"] <= p["reorder_point"]
                    ]
                    if not vendor_parts:
                        print(f"  No low-stock parts found for vendor: {vendor}")
                        return
                    line_items = []
                    for p in vendor_parts:
                        target = p["reorder_point"] * 2
                        order_qty = max(1, target - p["quantity"])
                        line_items.append({
                            "part_number": p["part_number"],
                            "part_name": p["part_name"],
                            "quantity": order_qty,
                            "unit_cost": p["cost"],
                        })
                else:
                    # All vendors
                    low_parts = [p for p in inventory if p["quantity"] <= p["reorder_point"]]
                    if not low_parts:
                        print("  No low-stock parts found.")
                        return
                    by_vendor = {}
                    for p in low_parts:
                        v = p.get("preferred_vendor", "Unknown Vendor")
                        by_vendor.setdefault(v, []).append(p)
                    for v, parts in by_vendor.items():
                        line_items_v = []
                        for p in parts:
                            target = p["reorder_point"] * 2
                            order_qty = max(1, target - p["quantity"])
                            line_items_v.append({
                                "part_number": p["part_number"],
                                "part_name": p["part_name"],
                                "quantity": order_qty,
                                "unit_cost": p["cost"],
                            })
                        po_number = po_module.generate_po_number()
                        content = po_module.build_po(v, line_items_v, profile, po_number, notes)
                        vendor_safe = po_module.safe_vendor_filename(v)
                        from datetime import datetime
                        filename = f"PO_{vendor_safe}_{datetime.now().strftime('%Y%m%d')}.txt"
                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, "w", encoding="utf-8") as fh:
                            fh.write(content)
                        print(f"  Saved output/parts_inventory/{filename}")
                    print(f"\nDone - POs generated for all vendors.")
                    return

            if not line_items:
                print("  No line items to include in PO.")
                return

            po_number = po_module.generate_po_number()
            content = po_module.build_po(vendor or "Manual Order", line_items, profile, po_number, notes)
            vendor_safe = po_module.safe_vendor_filename(vendor or "Manual")
            from datetime import datetime
            filename = f"PO_{vendor_safe}_{datetime.now().strftime('%Y%m%d')}.txt"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(content)
            print(content)
            print(f"\nSaved output/parts_inventory/{filename}")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("parts_inventory")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
