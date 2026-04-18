#!/usr/bin/env python3
"""
Parts Inventory Tracker — Module 11: Parts Inventory
Shop Command Center

Track parts with stock levels, reorder thresholds, vendor info, and cost.
Generate reorder alerts and full inventory reports.

Usage:
  # Add a part
  python tools/parts_inventory/track_inventory.py --action add \\
      --part_number "MF-51394" \\
      --part_name "Oil Filter - Motorcraft FL-820S" \\
      --category "oil_filters" \\
      --quantity 12 \\
      --reorder_point 4 \\
      --preferred_vendor "AutoZone Commercial" \\
      --cost 6.49

  # Update quantity
  python tools/parts_inventory/track_inventory.py --action update \\
      --part_number "MF-51394" --quantity 8

  # Check what needs reordering
  python tools/parts_inventory/track_inventory.py --action reorder_check

  # List full inventory
  python tools/parts_inventory/track_inventory.py --action list

  # Generate full report (saved to output/parts_inventory/)
  python tools/parts_inventory/track_inventory.py --action report
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
from datetime import datetime

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')
DATA_FILE    = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'parts_inventory.json')
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'parts_inventory')

TODAY     = datetime.now()
TODAY_STR = TODAY.strftime('%Y-%m-%d')


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


def save_inventory(data):
    path = os.path.abspath(DATA_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def find_part(inventory, part_number):
    """Return (index, record) or (None, None) if not found."""
    pn_upper = part_number.strip().upper()
    for i, item in enumerate(inventory):
        if item.get('part_number', '').strip().upper() == pn_upper:
            return i, item
    return None, None


def stock_status(quantity, reorder_point):
    """Return a status label."""
    if quantity == 0:
        return 'OUT OF STOCK'
    elif quantity <= reorder_point:
        return 'LOW - REORDER'
    else:
        return 'OK'


def status_icon(quantity, reorder_point):
    s = stock_status(quantity, reorder_point)
    return {'OUT OF STOCK': '[OUT]', 'LOW - REORDER': '[LOW]', 'OK': '[ OK]'}.get(s, '[???]')


# ─────────────────────────────────────────────────────────────────────────────
# Actions
# ─────────────────────────────────────────────────────────────────────────────

def action_add(args, inventory):
    """Add a new part to the inventory."""
    required = ['part_number', 'part_name']
    for field in required:
        if not getattr(args, field, None):
            print(f"ERROR: --{field} is required for --action add", file=sys.stderr)
            sys.exit(1)

    # Reject duplicate part numbers
    idx, existing = find_part(inventory, args.part_number)
    if existing:
        print(f"ERROR: Part number '{args.part_number}' already exists.", file=sys.stderr)
        print(f"  Existing: {existing['part_name']} — Qty: {existing['quantity']}", file=sys.stderr)
        print(f"  Use --action update to change quantity or other fields.", file=sys.stderr)
        sys.exit(1)

    record = {
        'part_number':       args.part_number.strip(),
        'part_name':         args.part_name.strip(),
        'category':          args.category.strip() if args.category else 'general',
        'quantity':          max(0, args.quantity),
        'reorder_point':     max(0, args.reorder_point),
        'preferred_vendor':  args.preferred_vendor.strip() if args.preferred_vendor else '',
        'cost':              round(max(0.0, args.cost), 2),
        'date_added':        TODAY_STR,
        'last_updated':      TODAY_STR,
    }

    inventory.append(record)
    save_inventory(inventory)

    status = stock_status(record['quantity'], record['reorder_point'])
    print(f"\n  Added: {record['part_name']} [{record['part_number']}]")
    print(f"  Category  : {record['category']}")
    print(f"  Quantity  : {record['quantity']} (Reorder at: {record['reorder_point']})")
    print(f"  Status    : {status}")
    print(f"  Vendor    : {record['preferred_vendor']}")
    print(f"  Unit Cost : ${record['cost']:.2f}")
    print(f"  Inventory total: {len(inventory)} parts")
    print(f"\n  Saved to data/parts_inventory.json")


def action_update(args, inventory):
    """Update an existing part record."""
    if not args.part_number:
        print("ERROR: --part_number is required for --action update", file=sys.stderr)
        sys.exit(1)

    idx, record = find_part(inventory, args.part_number)
    if record is None:
        print(f"ERROR: Part number '{args.part_number}' not found.", file=sys.stderr)
        print("  Run --action list to see all part numbers on file.", file=sys.stderr)
        sys.exit(1)

    updated = []
    if args.quantity is not None and args.quantity >= 0:
        record['quantity'] = args.quantity
        updated.append(f"quantity → {args.quantity}")
    if args.reorder_point is not None and args.reorder_point >= 0:
        record['reorder_point'] = args.reorder_point
        updated.append(f"reorder_point → {args.reorder_point}")
    if args.part_name:
        record['part_name'] = args.part_name.strip()
        updated.append(f"part_name → {args.part_name}")
    if args.category:
        record['category'] = args.category.strip()
        updated.append(f"category → {args.category}")
    if args.preferred_vendor:
        record['preferred_vendor'] = args.preferred_vendor.strip()
        updated.append(f"preferred_vendor → {args.preferred_vendor}")
    if args.cost is not None and args.cost > 0:
        record['cost'] = round(args.cost, 2)
        updated.append(f"cost → ${args.cost:.2f}")

    record['last_updated'] = TODAY_STR
    inventory[idx] = record
    save_inventory(inventory)

    status = stock_status(record['quantity'], record['reorder_point'])
    print(f"\n  Updated: {record['part_name']} [{args.part_number}]")
    if updated:
        for u in updated:
            print(f"    {u}")
    print(f"  Current status: {status} (Qty: {record['quantity']}, Reorder at: {record['reorder_point']})")
    print(f"\n  Saved to data/parts_inventory.json")


def action_reorder_check(inventory):
    """List all parts at or below their reorder point."""
    out_of_stock = [p for p in inventory if p['quantity'] == 0]
    low_stock    = [p for p in inventory if 0 < p['quantity'] <= p['reorder_point']]
    at_threshold = [p for p in inventory if p['quantity'] == p['reorder_point'] and p['quantity'] > 0]

    if not out_of_stock and not low_stock:
        print(f"\n  All {len(inventory)} parts are above their reorder points.")
        print("  No reorder action needed at this time.")
        return

    print("=" * 65)
    print("  REORDER ALERT")
    print(f"  {TODAY.strftime('%B %d, %Y')}")
    print("=" * 65)

    if out_of_stock:
        print(f"\n  [OUT OF STOCK] — {len(out_of_stock)} parts  ← ORDER IMMEDIATELY")
        print("─" * 65)
        for p in sorted(out_of_stock, key=lambda x: x['part_name']):
            print(f"\n  {p['part_name']}")
            print(f"    Part # : {p['part_number']}")
            print(f"    Vendor : {p['preferred_vendor']}")
            print(f"    Cost   : ${p['cost']:.2f} each")
            suggest_qty = p['reorder_point'] * 3 if p['reorder_point'] > 0 else 6
            print(f"    Suggest: Order {suggest_qty} units (${suggest_qty * p['cost']:.2f})")

    if low_stock:
        print(f"\n  [LOW STOCK] — {len(low_stock)} parts  ← Schedule reorder")
        print("─" * 65)
        for p in sorted(low_stock, key=lambda x: x['quantity']):
            needed = (p['reorder_point'] * 2) - p['quantity']
            print(f"\n  {p['part_name']}")
            print(f"    Part # : {p['part_number']}")
            print(f"    Stock  : {p['quantity']} (Reorder at: {p['reorder_point']})")
            print(f"    Vendor : {p['preferred_vendor']}")
            print(f"    Cost   : ${p['cost']:.2f} each")
            print(f"    Suggest: Order {max(needed,1)} more to reach 2× reorder point (${max(needed,1) * p['cost']:.2f})")

    print(f"\n{'=' * 65}")
    total_affected = len(out_of_stock) + len(low_stock)
    est_cost = sum(
        (p['reorder_point'] * 3 if p['quantity'] == 0 else (p['reorder_point'] * 2 - p['quantity'])) * p['cost']
        for p in out_of_stock + low_stock
    )
    print(f"  {total_affected} parts need attention | Est. reorder cost: ${est_cost:,.2f}")
    print(f"\n  Run generate_po.py to create a Purchase Order.")
    print("=" * 65)


def action_list(inventory):
    """Print full inventory."""
    if not inventory:
        print("\n  No parts in inventory. Use --action add to begin.")
        return

    # Group by category
    by_category = {}
    for p in inventory:
        cat = p.get('category', 'general')
        by_category.setdefault(cat, []).append(p)

    # Status counts
    out   = sum(1 for p in inventory if p['quantity'] == 0)
    low   = sum(1 for p in inventory if 0 < p['quantity'] <= p['reorder_point'])
    ok    = sum(1 for p in inventory if p['quantity'] > p['reorder_point'])

    print("=" * 65)
    print(f"  PARTS INVENTORY — {len(inventory)} parts")
    print(f"  {TODAY.strftime('%B %d, %Y')}")
    print("=" * 65)
    print(f"  Status: {out} out of stock | {low} low | {ok} OK")

    for cat, parts in sorted(by_category.items()):
        print(f"\n  {'─'*60}")
        print(f"  {cat.upper().replace('_',' ')}")
        print(f"  {'─'*60}")
        for p in sorted(parts, key=lambda x: x['part_name']):
            icon = status_icon(p['quantity'], p['reorder_point'])
            print(f"\n  {icon} {p['part_name']}")
            print(f"         P/N: {p['part_number']}  |  "
                  f"Qty: {p['quantity']}  |  "
                  f"Reorder: {p['reorder_point']}  |  "
                  f"Cost: ${p['cost']:.2f}  |  "
                  f"Vendor: {p['preferred_vendor']}")

    print(f"\n{'=' * 65}")
    inventory_value = sum(p['quantity'] * p['cost'] for p in inventory)
    print(f"  Total inventory value: ${inventory_value:,.2f}")
    print("=" * 65)


def action_report(inventory, profile):
    """Generate a full inventory report saved to output/parts_inventory/."""
    shop    = profile.get('shop_name', 'Your Shop')
    owner   = profile.get('owner_name', '')
    phone   = profile.get('phone', '')
    address = profile.get('address', '')
    today   = TODAY.strftime('%B %d, %Y')

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

    out_of_stock = [p for p in inventory if p['quantity'] == 0]
    low_stock    = [p for p in inventory if 0 < p['quantity'] <= p['reorder_point']]
    ok_stock     = [p for p in inventory if p['quantity'] > p['reorder_point']]

    inventory_value = sum(p['quantity'] * p['cost'] for p in inventory)
    reorder_value   = sum(
        (p['reorder_point'] * 2 - p['quantity']) * p['cost']
        for p in low_stock
    ) + sum(
        p['reorder_point'] * 3 * p['cost']
        for p in out_of_stock
    )

    # Group by category
    by_category = {}
    for p in inventory:
        cat = p.get('category', 'general')
        by_category.setdefault(cat, []).append(p)

    lines = []
    lines.append("=" * 70)
    lines.append("  PARTS INVENTORY STATUS REPORT")
    lines.append(f"  {shop}")
    if address:
        lines.append(f"  {address}")
    if phone:
        lines.append(f"  {phone}")
    lines.append(f"  Report Date  : {today}")
    lines.append(f"  Total SKUs   : {len(inventory)}")
    lines.append("=" * 70)

    lines.append("\n  SUMMARY")
    lines.append("─" * 70)
    lines.append(f"  {'Parts tracked':<35}: {len(inventory)}")
    lines.append(f"  {'Out of stock':<35}: {len(out_of_stock)}" +
                 (" ← ORDER IMMEDIATELY" if out_of_stock else " ✓"))
    lines.append(f"  {'Low stock (at/below reorder point)':<35}: {len(low_stock)}" +
                 (" ← REORDER SOON" if low_stock else " ✓"))
    lines.append(f"  {'Adequately stocked':<35}: {len(ok_stock)}")
    lines.append(f"  {'Current inventory value':<35}: ${inventory_value:,.2f}")
    if out_of_stock or low_stock:
        lines.append(f"  {'Estimated reorder spend':<35}: ${reorder_value:,.2f}")

    # Out of stock
    if out_of_stock:
        lines.append("\n\n  OUT OF STOCK — ORDER IMMEDIATELY")
        lines.append("─" * 70)
        for p in sorted(out_of_stock, key=lambda x: x['part_name']):
            suggest = p['reorder_point'] * 3 if p['reorder_point'] > 0 else 6
            lines.append(f"\n  {p['part_name']}")
            lines.append(f"    Part #         : {p['part_number']}")
            lines.append(f"    Category       : {p.get('category','—')}")
            lines.append(f"    Reorder Point  : {p['reorder_point']}")
            lines.append(f"    Preferred Vendor: {p['preferred_vendor']}")
            lines.append(f"    Unit Cost      : ${p['cost']:.2f}")
            lines.append(f"    Suggested Order: {suggest} units (${suggest * p['cost']:.2f})")

    # Low stock
    if low_stock:
        lines.append("\n\n  LOW STOCK — REORDER SOON")
        lines.append("─" * 70)
        for p in sorted(low_stock, key=lambda x: x['quantity']):
            needed = max(1, (p['reorder_point'] * 2) - p['quantity'])
            lines.append(f"\n  {p['part_name']}")
            lines.append(f"    Part #          : {p['part_number']}")
            lines.append(f"    Category        : {p.get('category','—')}")
            lines.append(f"    On Hand         : {p['quantity']} (Reorder at: {p['reorder_point']})")
            lines.append(f"    Preferred Vendor: {p['preferred_vendor']}")
            lines.append(f"    Unit Cost       : ${p['cost']:.2f}")
            lines.append(f"    Suggested Order : {needed} units (${needed * p['cost']:.2f})")

    # Full inventory by category
    lines.append("\n\n  COMPLETE INVENTORY BY CATEGORY")
    lines.append("─" * 70)

    for cat, parts in sorted(by_category.items()):
        cat_value = sum(p['quantity'] * p['cost'] for p in parts)
        lines.append(f"\n  {cat.upper().replace('_',' ')}  ({len(parts)} SKUs — value: ${cat_value:,.2f})")
        lines.append(f"  {'─'*65}")
        lines.append(f"  {'Part Name':<38} {'P/N':<14} {'Qty':>4} {'RP':>4} {'Cost':>7}  Status")
        lines.append(f"  {'─'*65}")
        for p in sorted(parts, key=lambda x: x['part_name']):
            status = stock_status(p['quantity'], p['reorder_point'])
            name   = p['part_name'][:37]
            pn     = p['part_number'][:13]
            lines.append(
                f"  {name:<38} {pn:<14} {p['quantity']:>4} {p['reorder_point']:>4} "
                f"${p['cost']:>6.2f}  {status}"
            )

    # Sign-off
    lines.append("\n\n" + "=" * 70)
    lines.append("  REPORT SIGN-OFF")
    lines.append("─" * 70)
    lines.append(f"\n  This report was generated on {today} by {shop} Shop Command Center.")
    lines.append(f"\n  Reviewed by: {'_' * 30}  Date: {'_' * 12}")
    if owner:
        lines.append(f"  Shop Manager: {owner}")
    lines.append(f"  Shop: {shop}")
    if phone:
        lines.append(f"  Phone: {phone}")
    lines.append("\n" + "=" * 70)

    content = "\n".join(lines)

    report_filename = f"inventory_report_{TODAY_STR}.txt"
    report_path = os.path.join(os.path.abspath(OUTPUT_DIR), report_filename)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)

    current_path = os.path.join(os.path.abspath(OUTPUT_DIR), 'inventory_report.txt')
    with open(current_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(content)
    print(f"\n  Reports saved:")
    print(f"    output/parts_inventory/{report_filename}")
    print(f"    output/parts_inventory/inventory_report.txt  (current copy)")

    if out_of_stock or low_stock:
        print(f"\n  ACTION NEEDED: {len(out_of_stock)+len(low_stock)} parts require reordering.")
        print(f"  Run: python tools/parts_inventory/generate_po.py --vendor \"<vendor name>\"")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Parts Inventory Tracker — Module 11"
    )
    parser.add_argument('--action', required=True,
                        choices=['add', 'update', 'reorder_check', 'list', 'report'],
                        help="Action: add | update | reorder_check | list | report")

    parser.add_argument('--part_number',      default='',    help="Part number (exact, from vendor catalog)")
    parser.add_argument('--part_name',        default='',    help="Descriptive part name")
    parser.add_argument('--category',         default='',    help="Category: oil_filters, brake_pads, belts, fluids, etc.")
    parser.add_argument('--quantity',         type=int,   default=None, help="Quantity on hand")
    parser.add_argument('--reorder_point',    type=int,   default=0,    help="Reorder when quantity reaches this level")
    parser.add_argument('--preferred_vendor', default='',    help="Primary vendor name")
    parser.add_argument('--cost',             type=float, default=None, help="Unit cost (your cost)")

    args = parser.parse_args()

    profile   = load_profile()
    inventory = load_inventory()

    if args.action == 'add':
        if args.quantity is None:
            args.quantity = 0
        if args.cost is None:
            args.cost = 0.0
        action_add(args, inventory)

    elif args.action == 'update':
        action_update(args, inventory)

    elif args.action == 'reorder_check':
        action_reorder_check(inventory)

    elif args.action == 'list':
        action_list(inventory)

    elif args.action == 'report':
        if not inventory:
            print("No parts in inventory. Use --action add to begin.")
            sys.exit(0)
        action_report(inventory, profile)


if __name__ == '__main__':
    main()
