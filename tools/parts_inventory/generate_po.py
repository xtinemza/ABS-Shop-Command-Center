#!/usr/bin/env python3
"""
Purchase Order Generator — Module 11: Parts Inventory
Shop Command Center

Generate formatted Purchase Orders for parts reordering. Two modes:

  Mode 1 — Auto-generate PO from low-stock items for a specific vendor:
    python tools/parts_inventory/generate_po.py --vendor "AutoZone Commercial"

  Mode 2 — Manual PO with specific line items (JSON):
    python tools/parts_inventory/generate_po.py \\
        --vendor "AutoZone Commercial" \\
        --items '[{"part_number": "MF-51394", "part_name": "Oil Filter FL-820S", "quantity": 12, "unit_cost": 6.49}]' \\
        --notes "Urgent — needed for fleet account this week"

  Mode 3 — Auto-generate POs for ALL vendors with low stock:
    python tools/parts_inventory/generate_po.py --all_vendors

Each PO is saved as: output/parts_inventory/PO_<Vendor>_<YYYYMMDD>.txt
"""

import argparse
import json
import os
import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import random
from datetime import datetime

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')
DATA_FILE    = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'parts_inventory.json')
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'parts_inventory')

TODAY     = datetime.now()
TODAY_STR = TODAY.strftime('%Y-%m-%d')
TODAY_FMT = TODAY.strftime('%B %d, %Y')


# ─────────────────────────────────────────────────────────────────────────────
# Data helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_inventory():
    path = os.path.abspath(DATA_FILE)
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def generate_po_number():
    """Generate a unique PO number: PO-YYYYMMDD-XXX"""
    date_part = TODAY.strftime('%Y%m%d')
    seq = random.randint(100, 999)
    return f"PO-{date_part}-{seq}"


def safe_vendor_filename(vendor):
    """Make a vendor name safe for use in a filename."""
    safe = vendor.replace(' ', '_').replace('/', '-').replace('\\', '-')
    safe = ''.join(c for c in safe if c.isalnum() or c in ('_', '-'))
    return safe[:40]


# ─────────────────────────────────────────────────────────────────────────────
# PO rendering
# ─────────────────────────────────────────────────────────────────────────────

def build_po(vendor, line_items, profile, po_number, notes=''):
    """
    Build a formatted Purchase Order document.

    line_items: list of dicts with keys:
        part_number, part_name, quantity, unit_cost
    """
    shop    = profile.get('shop_name', 'Your Shop')
    address = profile.get('address', '')
    phone   = profile.get('phone', '')
    owner   = profile.get('owner_name', '')
    website = profile.get('website', '')

    # Calculate totals
    for item in line_items:
        item['line_total'] = round(item['quantity'] * item['unit_cost'], 2)

    grand_total = sum(item['line_total'] for item in line_items)
    total_units = sum(item['quantity'] for item in line_items)

    lines = []

    # ── Header ──
    lines.append("=" * 72)
    lines.append("  PURCHASE ORDER")
    lines.append("=" * 72)

    lines.append(f"\n  {'FROM (Ship To)':<30}  {'TO (Vendor)'}")
    lines.append(f"  {'─'*30}  {'─'*36}")
    lines.append(f"  {shop:<30}  {vendor}")
    if address:
        lines.append(f"  {address:<30}")
    if phone:
        lines.append(f"  {phone:<30}")
    if owner:
        lines.append(f"  Attn: {owner:<24}")
    if website:
        lines.append(f"  {website:<30}")

    lines.append(f"\n  {'─'*72}")
    lines.append(f"  PO NUMBER  : {po_number}")
    lines.append(f"  PO DATE    : {TODAY_FMT}")
    lines.append(f"  REQUESTED  : {owner if owner else shop}")
    lines.append(f"  SHIP TO    : {shop}{' — ' + address if address else ''}")
    if notes:
        lines.append(f"  NOTES      : {notes}")
    lines.append(f"  {'─'*72}")

    # ── Line items table ──
    lines.append(f"\n  {'LINE ITEMS'}")
    lines.append(f"  {'─'*72}")

    col_pn   = 14
    col_desc = 34
    col_qty  = 6
    col_unit = 10
    col_tot  = 10

    header = (
        f"  {'Part Number':<{col_pn}}  "
        f"{'Description':<{col_desc}}  "
        f"{'Qty':>{col_qty}}  "
        f"{'Unit Cost':>{col_unit}}  "
        f"{'Line Total':>{col_tot}}"
    )
    lines.append(header)
    lines.append(f"  {'─'*72}")

    for item in line_items:
        pn   = str(item.get('part_number', '')).strip()[:col_pn]
        desc = str(item.get('part_name', '')).strip()[:col_desc]
        qty  = item.get('quantity', 0)
        unit = item.get('unit_cost', 0.0)
        tot  = item.get('line_total', 0.0)

        row = (
            f"  {pn:<{col_pn}}  "
            f"{desc:<{col_desc}}  "
            f"{qty:>{col_qty}}  "
            f"${unit:>{col_unit-1}.2f}  "
            f"${tot:>{col_tot-1}.2f}"
        )
        lines.append(row)

        # If description was truncated, show remainder on next line
        full_desc = str(item.get('part_name', '')).strip()
        if len(full_desc) > col_desc:
            overflow = full_desc[col_desc:]
            lines.append(f"  {'':<{col_pn}}  {overflow:<{col_desc}}")

    lines.append(f"  {'─'*72}")

    # ── Totals ──
    lines.append(f"  {'':>{col_pn + col_desc + 8}}  {'TOTAL UNITS':>10}  {total_units:>{col_tot}}")
    lines.append(f"  {'':>{col_pn + col_desc + 8}}  {'SUBTOTAL':>10}  ${grand_total:>{col_tot-1},.2f}")
    lines.append(f"  {'':>{col_pn + col_desc + 8}}  {'TAX':>10}  {'[VERIFY]':>{col_tot}}")
    lines.append(f"  {'':>{col_pn + col_desc + 8}}  {'GRAND TOTAL':>10}  {'[AFTER TAX]':>{col_tot}}")
    lines.append(f"  {'─'*72}")
    lines.append(f"  Subtotal before tax: ${grand_total:,.2f}  |  {len(line_items)} line items  |  {total_units} total units")

    # ── Terms & conditions ──
    lines.append(f"\n  TERMS & DELIVERY")
    lines.append(f"  {'─'*72}")
    lines.append(f"  Payment Terms  : Net 30 days [CUSTOMIZE]")
    lines.append(f"  Delivery       : Standard / As available [CUSTOMIZE if urgent]")
    lines.append(f"  Contact        : {phone if phone else '[shop phone]'}")
    lines.append(f"  Ship To        : {shop}{', ' + address if address else ''}")

    # ── Authorization ──
    lines.append(f"\n  AUTHORIZATION")
    lines.append(f"  {'─'*72}")
    lines.append(f"\n  This Purchase Order authorizes the vendor to ship the items listed")
    lines.append(f"  above to {shop}. Payment will be processed per agreed terms.")
    lines.append(f"\n  Authorized By  : {'_' * 30}   Date: {'_' * 12}")
    lines.append(f"  Title          : {'_' * 30}")
    if owner:
        lines.append(f"  Shop Manager   : {owner}")
    lines.append(f"  Shop           : {shop}")
    if phone:
        lines.append(f"  Phone          : {phone}")

    lines.append(f"\n  Vendor Confirmation #: {'_' * 20}   Confirmed By: {'_' * 18}")

    lines.append(f"\n{'=' * 72}")
    lines.append(f"  {shop} — Purchase Order {po_number}")
    lines.append(f"  Issued: {TODAY_FMT}")
    lines.append("=" * 72)

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Purchase Order Generator — Module 11"
    )
    parser.add_argument('--vendor',      default='',
                        help="Vendor name (required unless --all_vendors)")
    parser.add_argument('--items',       default='',
                        help="JSON list of line items: [{part_number, part_name, quantity, unit_cost}, ...]")
    parser.add_argument('--notes',       default='',
                        help="Optional notes to include on the PO")
    parser.add_argument('--all_vendors', action='store_true',
                        help="Generate a separate PO for every vendor that has low-stock items")
    parser.add_argument('--restock_multiplier', type=int, default=2,
                        help="Restock to (reorder_point × this). Default: 2")

    args = parser.parse_args()

    profile   = load_profile()
    inventory = load_inventory()

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

    # ── Mode 3: All vendors ──
    if args.all_vendors:
        low_parts = [p for p in inventory if p['quantity'] <= p['reorder_point']]
        if not low_parts:
            print("  All parts are above their reorder points. No POs needed.")
            sys.exit(0)

        # Group by vendor
        by_vendor = {}
        for p in low_parts:
            vendor = p.get('preferred_vendor', 'Unknown Vendor')
            by_vendor.setdefault(vendor, []).append(p)

        saved_pos = []
        for vendor, parts in by_vendor.items():
            line_items = []
            for p in parts:
                target   = p['reorder_point'] * args.restock_multiplier
                order_qty = max(1, target - p['quantity'])
                line_items.append({
                    'part_number': p['part_number'],
                    'part_name':   p['part_name'],
                    'quantity':    order_qty,
                    'unit_cost':   p['cost'],
                })

            po_number = generate_po_number()
            content   = build_po(vendor, line_items, profile, po_number, args.notes)

            vendor_safe = safe_vendor_filename(vendor)
            date_safe   = TODAY.strftime('%Y%m%d')
            filename    = f"PO_{vendor_safe}_{date_safe}.txt"
            filepath    = os.path.join(os.path.abspath(OUTPUT_DIR), filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            subtotal = sum(item['quantity'] * item['unit_cost'] for item in line_items)
            saved_pos.append((vendor, filename, po_number, len(line_items), subtotal))
            print(content)
            print()

        print("=" * 65)
        print(f"  {len(saved_pos)} Purchase Orders generated:")
        for vendor, filename, po_num, items, subtotal in saved_pos:
            print(f"    {po_num}  {vendor}  ({items} items, ${subtotal:,.2f})")
            print(f"    → output/parts_inventory/{filename}")
        grand = sum(s for _, _, _, _, s in saved_pos)
        print(f"\n  Total estimated spend: ${grand:,.2f} (before tax)")
        print("=" * 65)
        return

    # ── Mode 1 or 2: Specific vendor ──
    if not args.vendor:
        print("ERROR: --vendor is required (or use --all_vendors)", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # Mode 2: Manual line items from --items JSON
    if args.items:
        try:
            line_items = json.loads(args.items)
        except json.JSONDecodeError as e:
            print(f"ERROR: Could not parse --items JSON: {e}", file=sys.stderr)
            print("  Expected format: '[{\"part_number\": \"X\", \"part_name\": \"Y\", \"quantity\": 4, \"unit_cost\": 9.99}]'",
                  file=sys.stderr)
            sys.exit(1)

        # Validate required fields
        for i, item in enumerate(line_items):
            for field in ('part_number', 'part_name', 'quantity', 'unit_cost'):
                if field not in item:
                    print(f"ERROR: Item {i+1} is missing field '{field}'", file=sys.stderr)
                    sys.exit(1)

    # Mode 1: Auto-generate from low-stock items for this vendor
    else:
        vendor_parts = [
            p for p in inventory
            if p.get('preferred_vendor', '').strip().lower() == args.vendor.strip().lower()
            and p['quantity'] <= p['reorder_point']
        ]

        if not vendor_parts:
            # Try case-insensitive partial match
            vendor_lower = args.vendor.strip().lower()
            vendor_parts = [
                p for p in inventory
                if vendor_lower in p.get('preferred_vendor', '').lower()
                and p['quantity'] <= p['reorder_point']
            ]

        if not vendor_parts:
            print(f"\n  No low-stock parts found for vendor: {args.vendor}")
            print("  All parts from this vendor may be adequately stocked.")
            print("  Use --items to create a manual PO, or --all_vendors to see all low-stock vendors.")
            sys.exit(0)

        line_items = []
        for p in vendor_parts:
            target    = p['reorder_point'] * args.restock_multiplier
            order_qty = max(1, target - p['quantity'])
            line_items.append({
                'part_number': p['part_number'],
                'part_name':   p['part_name'],
                'quantity':    order_qty,
                'unit_cost':   p['cost'],
            })

    # Build and save the PO
    po_number = generate_po_number()
    content   = build_po(args.vendor, line_items, profile, po_number, args.notes)

    vendor_safe = safe_vendor_filename(args.vendor)
    date_safe   = TODAY.strftime('%Y%m%d')
    filename    = f"PO_{vendor_safe}_{date_safe}.txt"
    filepath    = os.path.join(os.path.abspath(OUTPUT_DIR), filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(content)

    subtotal = sum(item['quantity'] * item['unit_cost'] for item in line_items)
    print(f"\n  Purchase Order saved: output/parts_inventory/{filename}")
    print(f"  PO Number : {po_number}")
    print(f"  Vendor    : {args.vendor}")
    print(f"  Items     : {len(line_items)}")
    print(f"  Subtotal  : ${subtotal:,.2f} (before tax)")
    print(f"\n  Next steps:")
    print(f"    1. Review PO and adjust quantities if needed")
    print(f"    2. Get manager authorization signature")
    print(f"    3. Call or email vendor to place the order")
    print(f"    4. When parts arrive, update inventory: track_inventory.py --action update")


if __name__ == '__main__':
    main()
