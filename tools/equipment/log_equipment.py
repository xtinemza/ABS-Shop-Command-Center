#!/usr/bin/env python3
"""
Equipment Maintenance & Calibration Logger — Module 9: Equipment Logger
Shop Command Center

Track shop equipment with purchase dates, maintenance schedules, service history,
and generate compliance-ready status reports.

Usage:
  # Add equipment
  python tools/equipment/log_equipment.py --action add \\
      --name "BendPak 2-Post Lift" --type "Vehicle Lift" \\
      --equipment_id "LIFT-001" \\
      --purchase_date "2022-03-15" \\
      --last_service "2024-01-15" \\
      --next_service "2024-04-15" \\
      --notes "90-day lubrication/inspection. Serial: BP-XPR10AS-1234"

  # Update a record
  python tools/equipment/log_equipment.py --action update \\
      --equipment_id "LIFT-001" \\
      --last_service "2024-10-15" --next_service "2025-01-15" \\
      --notes "Replaced hydraulic seal on post A."

  # Log a maintenance event
  python tools/equipment/log_equipment.py --action log_maintenance \\
      --equipment_id "LIFT-001" \\
      --last_service "2024-10-15" --next_service "2025-01-15" \\
      --notes "Full lubrication. Cables inspected. No issues."

  # List all equipment
  python tools/equipment/log_equipment.py --action list

  # Generate full status report
  python tools/equipment/log_equipment.py --action generate_report
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
from datetime import datetime, timedelta

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')
DATA_FILE    = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'equipment_log.json')
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'equipment')

TODAY = datetime.now()
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


def load_equipment():
    path = os.path.abspath(DATA_FILE)
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_equipment(data):
    path = os.path.abspath(DATA_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def find_equipment(equipment, equipment_id):
    """Return (index, record) or (None, None) if not found."""
    for i, item in enumerate(equipment):
        if item.get('equipment_id', '').upper() == equipment_id.upper():
            return i, item
    return None, None


def parse_date(date_str):
    """Parse YYYY-MM-DD string, return datetime or None."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), '%Y-%m-%d')
    except ValueError:
        return None


def service_status(next_service_str):
    """Return (status_label, days_delta) based on next_service date."""
    next_dt = parse_date(next_service_str)
    if not next_dt:
        return 'UNKNOWN', None
    delta = (next_dt - TODAY).days
    if delta < 0:
        return 'OVERDUE', delta
    elif delta <= 30:
        return 'DUE SOON', delta
    else:
        return 'CURRENT', delta


# ─────────────────────────────────────────────────────────────────────────────
# Actions
# ─────────────────────────────────────────────────────────────────────────────

def action_add(args, equipment):
    """Add a new piece of equipment to the log."""
    if not args.name:
        print("ERROR: --name is required for --action add", file=sys.stderr)
        sys.exit(1)
    if not args.equipment_id:
        print("ERROR: --equipment_id is required for --action add", file=sys.stderr)
        sys.exit(1)

    # Check for duplicate ID
    _, existing = find_equipment(equipment, args.equipment_id)
    if existing:
        print(f"ERROR: Equipment ID '{args.equipment_id}' already exists. Use --action update.", file=sys.stderr)
        sys.exit(1)

    record = {
        'equipment_id':  args.equipment_id,
        'name':          args.name,
        'type':          args.type or '',
        'purchase_date': args.purchase_date or '',
        'last_service':  args.last_service or '',
        'next_service':  args.next_service or '',
        'notes':         args.notes or '',
        'date_added':    TODAY_STR,
        'maintenance_history': []
    }

    # Seed maintenance history if we have a last_service date
    if args.last_service:
        record['maintenance_history'].append({
            'date':  args.last_service,
            'notes': args.notes or 'Initial service log entry.',
            'logged_on': TODAY_STR,
        })

    equipment.append(record)
    save_equipment(equipment)

    status, delta = service_status(args.next_service)
    print(f"\n  Added: {args.name} [{args.equipment_id}]")
    if args.type:
        print(f"  Type : {args.type}")
    if args.last_service:
        print(f"  Last Service : {args.last_service}")
    if args.next_service:
        print(f"  Next Service : {args.next_service} — {status}" +
              (f" ({abs(delta)} days)" if delta is not None else ""))
    print(f"\n  Saved to data/equipment_log.json")
    return record


def action_update(args, equipment):
    """Update an existing equipment record."""
    if not args.equipment_id:
        print("ERROR: --equipment_id is required for --action update", file=sys.stderr)
        sys.exit(1)

    idx, record = find_equipment(equipment, args.equipment_id)
    if record is None:
        print(f"ERROR: No equipment found with ID '{args.equipment_id}'", file=sys.stderr)
        sys.exit(1)

    updated_fields = []
    if args.name:
        record['name'] = args.name
        updated_fields.append('name')
    if args.type:
        record['type'] = args.type
        updated_fields.append('type')
    if args.purchase_date:
        record['purchase_date'] = args.purchase_date
        updated_fields.append('purchase_date')
    if args.last_service:
        record['last_service'] = args.last_service
        updated_fields.append('last_service')
    if args.next_service:
        record['next_service'] = args.next_service
        updated_fields.append('next_service')
    if args.notes:
        record['notes'] = args.notes
        updated_fields.append('notes')

    record['last_updated'] = TODAY_STR
    equipment[idx] = record
    save_equipment(equipment)

    print(f"\n  Updated: {record['name']} [{args.equipment_id}]")
    print(f"  Fields updated: {', '.join(updated_fields) if updated_fields else 'none'}")
    if args.next_service:
        status, delta = service_status(args.next_service)
        print(f"  Next Service: {args.next_service} — {status}" +
              (f" ({abs(delta)} days)" if delta is not None else ""))
    print(f"\n  Saved to data/equipment_log.json")
    return record


def action_log_maintenance(args, equipment):
    """Record a maintenance event for a piece of equipment."""
    if not args.equipment_id:
        print("ERROR: --equipment_id is required for --action log_maintenance", file=sys.stderr)
        sys.exit(1)
    if not args.last_service:
        print("ERROR: --last_service (date of maintenance) is required", file=sys.stderr)
        sys.exit(1)

    idx, record = find_equipment(equipment, args.equipment_id)
    if record is None:
        print(f"ERROR: No equipment found with ID '{args.equipment_id}'", file=sys.stderr)
        sys.exit(1)

    # Append to maintenance history
    history_entry = {
        'date':      args.last_service,
        'notes':     args.notes or 'Maintenance performed.',
        'logged_on': TODAY_STR,
    }
    if 'maintenance_history' not in record:
        record['maintenance_history'] = []
    record['maintenance_history'].append(history_entry)

    # Update service dates on the main record
    record['last_service']  = args.last_service
    if args.next_service:
        record['next_service'] = args.next_service
    if args.notes:
        record['notes'] = args.notes
    record['last_updated'] = TODAY_STR

    equipment[idx] = record
    save_equipment(equipment)

    print(f"\n  Maintenance logged: {record['name']} [{args.equipment_id}]")
    print(f"  Service Date : {args.last_service}")
    if args.next_service:
        status, delta = service_status(args.next_service)
        print(f"  Next Service : {args.next_service} — {status}" +
              (f" ({abs(delta)} days)" if delta is not None else ""))
    print(f"  Notes        : {args.notes or 'Maintenance performed.'}")
    print(f"  History total: {len(record['maintenance_history'])} events")
    print(f"\n  Saved to data/equipment_log.json")
    return record


def action_list(equipment):
    """Print all equipment with status."""
    if not equipment:
        print("\n  No equipment in log. Use --action add to begin.")
        return

    overdue  = []
    due_soon = []
    current  = []
    unknown  = []

    for item in equipment:
        status, delta = service_status(item.get('next_service', ''))
        entry = (item, status, delta)
        if status == 'OVERDUE':
            overdue.append(entry)
        elif status == 'DUE SOON':
            due_soon.append(entry)
        elif status == 'CURRENT':
            current.append(entry)
        else:
            unknown.append(entry)

    print("=" * 62)
    print(f"  EQUIPMENT LOG — {len(equipment)} items")
    print(f"  As of {TODAY.strftime('%B %d, %Y')}")
    print("=" * 62)

    def print_section(label, entries):
        if not entries:
            return
        print(f"\n{label}")
        print("─" * 62)
        for item, status, delta in entries:
            print(f"\n  [{item.get('equipment_id','?')}] {item['name']}")
            if item.get('type'):
                print(f"       Type        : {item['type']}")
            if item.get('last_service'):
                print(f"       Last Service: {item['last_service']}")
            if item.get('next_service'):
                if delta is not None and delta < 0:
                    print(f"       Next Service: {item['next_service']} — OVERDUE by {abs(delta)} days")
                elif delta is not None:
                    print(f"       Next Service: {item['next_service']} — {delta} days away")
                else:
                    print(f"       Next Service: {item['next_service']}")
            if item.get('notes'):
                notes_short = item['notes'][:80] + ('...' if len(item['notes']) > 80 else '')
                print(f"       Notes       : {notes_short}")
            hist_count = len(item.get('maintenance_history', []))
            if hist_count:
                print(f"       History     : {hist_count} maintenance event(s) on file")

    print_section("  OVERDUE — ACTION REQUIRED", overdue)
    print_section("  DUE SOON — Within 30 days", due_soon)
    print_section("  CURRENT — Up to date", current)
    print_section("  STATUS UNKNOWN — No service date set", unknown)

    print(f"\n{'=' * 62}")
    print(f"  Summary: {len(overdue)} overdue | {len(due_soon)} due soon | "
          f"{len(current)} current | {len(unknown)} unknown")
    print("=" * 62)


def action_generate_report(equipment, profile):
    """Generate a full Equipment Status Report saved to output/equipment/."""
    shop    = profile.get('shop_name', 'Your Shop')
    owner   = profile.get('owner_name', '')
    phone   = profile.get('phone', '')
    address = profile.get('address', '')
    today   = TODAY.strftime('%B %d, %Y')
    today_s = TODAY_STR

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

    overdue  = []
    due_soon = []
    current  = []
    unknown  = []

    for item in equipment:
        status, delta = service_status(item.get('next_service', ''))
        entry = (item, status, delta)
        if status == 'OVERDUE':
            overdue.append(entry)
        elif status == 'DUE SOON':
            due_soon.append(entry)
        elif status == 'CURRENT':
            current.append(entry)
        else:
            unknown.append(entry)

    lines = []
    lines.append("=" * 70)
    lines.append("  EQUIPMENT STATUS & MAINTENANCE COMPLIANCE REPORT")
    lines.append(f"  {shop}")
    if address:
        lines.append(f"  {address}")
    if phone:
        lines.append(f"  {phone}")
    lines.append(f"  Report Date : {today}")
    lines.append(f"  Total Items : {len(equipment)}")
    lines.append("=" * 70)

    # Executive summary
    lines.append("\n  EXECUTIVE SUMMARY")
    lines.append("─" * 70)
    lines.append(f"  {'Items logged':<30}: {len(equipment)}")
    lines.append(f"  {'Overdue maintenance':<30}: {len(overdue)}" +
                 (" ← ACTION REQUIRED" if overdue else " ✓"))
    lines.append(f"  {'Due within 30 days':<30}: {len(due_soon)}" +
                 (" ← SCHEDULE NOW" if due_soon else " ✓"))
    lines.append(f"  {'Current / up to date':<30}: {len(current)}")
    lines.append(f"  {'No service date set':<30}: {len(unknown)}")

    # ── Overdue section ──
    if overdue:
        lines.append("\n\n  OVERDUE MAINTENANCE — IMMEDIATE ACTION REQUIRED")
        lines.append("─" * 70)
        for item, status, delta in overdue:
            lines.append(f"\n  [{item.get('equipment_id','?')}] {item['name']} ({item.get('type','')})")
            lines.append(f"    Last Service  : {item.get('last_service','—')}")
            lines.append(f"    Was Due       : {item.get('next_service','—')}")
            lines.append(f"    Overdue By    : {abs(delta)} days")
            if item.get('notes'):
                lines.append(f"    Notes         : {item['notes']}")

    # ── Due soon section ──
    if due_soon:
        lines.append("\n\n  UPCOMING MAINTENANCE — Schedule within 30 days")
        lines.append("─" * 70)
        for item, status, delta in due_soon:
            lines.append(f"\n  [{item.get('equipment_id','?')}] {item['name']} ({item.get('type','')})")
            lines.append(f"    Last Service  : {item.get('last_service','—')}")
            lines.append(f"    Next Due      : {item.get('next_service','—')} ({delta} days)")
            if item.get('notes'):
                lines.append(f"    Notes         : {item['notes']}")

    # ── Full equipment listing ──
    lines.append("\n\n  COMPLETE EQUIPMENT LISTING")
    lines.append("─" * 70)

    for item in equipment:
        status, delta = service_status(item.get('next_service', ''))
        status_icon = {
            'OVERDUE':  '[OVERDUE]',
            'DUE SOON': '[DUE SOON]',
            'CURRENT':  '[CURRENT]',
            'UNKNOWN':  '[NO DATE]',
        }.get(status, '[?]')

        lines.append(f"\n  {status_icon} [{item.get('equipment_id','?')}] {item['name']}")
        lines.append(f"    Type          : {item.get('type','—')}")
        lines.append(f"    Purchase Date : {item.get('purchase_date','—')}")
        lines.append(f"    Last Service  : {item.get('last_service','—')}")
        lines.append(f"    Next Service  : {item.get('next_service','—')}")
        if item.get('notes'):
            lines.append(f"    Notes         : {item['notes']}")

        # Maintenance history
        history = item.get('maintenance_history', [])
        if history:
            lines.append(f"    Service History ({len(history)} events):")
            for h in sorted(history, key=lambda x: x.get('date',''), reverse=True)[:5]:
                lines.append(f"      {h.get('date','?')}: {h.get('notes','')}")
            if len(history) > 5:
                lines.append(f"      ... and {len(history)-5} earlier events.")

    # ── Unknown section ──
    if unknown:
        lines.append("\n\n  NO SERVICE DATE — Review Needed")
        lines.append("─" * 70)
        for item, status, delta in unknown:
            lines.append(f"  [{item.get('equipment_id','?')}] {item['name']}")
            lines.append(f"    Last Service  : {item.get('last_service','—')}")
            lines.append(f"    Action        : Set a next_service date to enable tracking.")

    # ── Sign-off block ──
    lines.append("\n\n" + "=" * 70)
    lines.append("  COMPLIANCE SIGN-OFF")
    lines.append("─" * 70)
    lines.append(f"\n  This report was generated on {today} by {shop} Shop Command Center.")
    lines.append(f"  It reflects the current equipment maintenance status as recorded")
    lines.append(f"  in data/equipment_log.json.")
    lines.append(f"\n  Reviewed by: {'_' * 30}  Date: {'_' * 12}")
    lines.append(f"  Title:       {'_' * 30}")
    if owner:
        lines.append(f"\n  Shop Manager: {owner}")
    lines.append(f"  Shop: {shop}")
    if phone:
        lines.append(f"  Phone: {phone}")
    lines.append("\n" + "=" * 70)

    content = "\n".join(lines)

    # Save
    report_filename = f"equipment_status_report_{today_s}.txt"
    report_path = os.path.join(os.path.abspath(OUTPUT_DIR), report_filename)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Also save a current copy without date stamp for easy access
    current_path = os.path.join(os.path.abspath(OUTPUT_DIR), 'equipment_status_report.txt')
    with open(current_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(content)
    print(f"\n  Report saved:")
    print(f"    output/equipment/{report_filename}")
    print(f"    output/equipment/equipment_status_report.txt  (current copy)")

    return content


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Equipment Maintenance & Calibration Logger — Module 9"
    )
    parser.add_argument('--action', required=True,
                        choices=['add', 'update', 'log_maintenance', 'list', 'generate_report'],
                        help="Action to perform")

    # Equipment identification
    parser.add_argument('--equipment_id',  help="Unique equipment ID (e.g. LIFT-001)")
    parser.add_argument('--name',          help="Equipment name")
    parser.add_argument('--type',          help="Equipment type (e.g. Vehicle Lift, Tire Machine)")

    # Dates
    parser.add_argument('--purchase_date', help="Purchase date (YYYY-MM-DD)")
    parser.add_argument('--last_service',  help="Date of most recent service (YYYY-MM-DD)")
    parser.add_argument('--next_service',  help="Next scheduled service date (YYYY-MM-DD)")

    # Notes
    parser.add_argument('--notes', help="Free-form notes (serial number, technician, findings, etc.)")

    args = parser.parse_args()

    profile   = load_profile()
    equipment = load_equipment()

    if args.action == 'add':
        action_add(args, equipment)

    elif args.action == 'update':
        action_update(args, equipment)

    elif args.action == 'log_maintenance':
        action_log_maintenance(args, equipment)

    elif args.action == 'list':
        action_list(equipment)

    elif args.action == 'generate_report':
        if not equipment:
            print("No equipment in log. Use --action add to begin.")
            sys.exit(0)
        action_generate_report(equipment, profile)


if __name__ == '__main__':
    main()
