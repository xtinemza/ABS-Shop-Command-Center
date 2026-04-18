#!/usr/bin/env python3
"""
Generate a branded vehicle service history report.

Usage (JSON records — preferred):
    python tools/service_history/generate_report.py \
        --customer "Sarah Mitchell" \
        --vehicle "2019 Toyota Camry SE" \
        --mileage 67000 \
        --vin "4T1B11HK9KU123456" \
        --records '[{"date":"01/15/2024","mileage":62000,"service":"Oil & Filter Change","tech":"Mike T.","cost":45,"notes":"Synthetic 5W-30"}]'

Usage (semicolon-delimited plain text):
    python tools/service_history/generate_report.py \
        --customer "Sarah Mitchell" \
        --vehicle "2019 Toyota Camry SE" \
        --mileage 67000 \
        --records "01/15/2024, 62000, Oil & Filter Change, Mike T., 45, Synthetic 5W-30; 04/20/2024, 64500, Front Brake Pads & Rotors, Dave R., 350, Replaced both sides"
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
from datetime import datetime, date

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'service_history')

# ---------------------------------------------------------------------------
# Standard mileage-interval maintenance items.
# Each entry: (service_name, interval_miles, first_due_miles, urgency_label)
# ---------------------------------------------------------------------------
MAINTENANCE_SCHEDULE = [
    ("Oil & Filter Change",           5_000,   5_000,  "SOON"),
    ("Tire Rotation & Balance",       7_500,   7_500,  "ROUTINE"),
    ("Cabin Air Filter",             15_000,  15_000,  "ROUTINE"),
    ("Engine Air Filter",            20_000,  20_000,  "ROUTINE"),
    ("Fuel System Service",          30_000,  30_000,  "MONITOR"),
    ("Transmission Fluid Service",   30_000,  30_000,  "MONITOR"),
    ("Coolant Flush",                60_000,  60_000,  "MONITOR"),
    ("Spark Plugs (iridium)",        90_000,  90_000,  "MONITOR"),
    ("Timing Belt Inspection",       60_000,  60_000,  "SOON"),
    ("Brake Fluid Flush",            30_000,  30_000,  "MONITOR"),
    ("Power Steering Fluid",         50_000,  50_000,  "MONITOR"),
    ("Multi-Point Inspection",       12_000,   1_000,  "ROUTINE"),
]

# Services that reset the mileage clock (keywords to detect in history)
SERVICE_KEYWORDS = {
    "oil":                 "Oil & Filter Change",
    "tire rotation":       "Tire Rotation & Balance",
    "cabin air":           "Cabin Air Filter",
    "engine air":          "Engine Air Filter",
    "fuel system":         "Fuel System Service",
    "transmission fluid":  "Transmission Fluid Service",
    "coolant":             "Coolant Flush",
    "spark plug":          "Spark Plugs (iridium)",
    "timing belt":         "Timing Belt Inspection",
    "brake fluid":         "Brake Fluid Flush",
    "power steering":      "Power Steering Fluid",
    "inspection":          "Multi-Point Inspection",
}


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if not os.path.exists(path):
        print("ERROR: shop_profile.json not found.", file=sys.stderr)
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_records(raw: str) -> list:
    """
    Accept either:
      - A JSON array string: [{"date":..., "mileage":..., "service":..., ...}]
      - A semicolon-separated plain-text string:
        "date, mileage, service, tech, cost, notes; ..."
    Returns a list of dicts with keys: date, mileage, service, tech, cost, notes.
    Sorts by mileage ascending.
    """
    raw = raw.strip()
    records = []

    # --- Try JSON first ---
    if raw.startswith('['):
        try:
            raw_list = json.loads(raw)
            for r in raw_list:
                records.append({
                    'date':    str(r.get('date', '')).strip(),
                    'mileage': int(r.get('mileage', 0)),
                    'service': str(r.get('service', '')).strip(),
                    'tech':    str(r.get('tech', '')).strip(),
                    'cost':    float(str(r.get('cost', 0)).replace('$', '').replace(',', '').strip() or 0),
                    'notes':   str(r.get('notes', '')).strip(),
                })
            records.sort(key=lambda x: x['mileage'])
            return records
        except (json.JSONDecodeError, ValueError) as e:
            print(f"WARNING: Could not parse records as JSON ({e}). Trying plain text.", file=sys.stderr)

    # --- Fall back to semicolon-delimited plain text ---
    for entry in raw.split(';'):
        parts = [p.strip() for p in entry.strip().split(',')]
        if len(parts) < 3:
            continue
        try:
            mileage_raw = parts[1].replace('mi', '').replace(',', '').strip()
            mileage = int(float(mileage_raw)) if mileage_raw else 0
        except ValueError:
            mileage = 0
        try:
            cost = float(parts[4].replace('$', '').replace(',', '').strip()) if len(parts) > 4 and parts[4] else 0.0
        except ValueError:
            cost = 0.0
        records.append({
            'date':    parts[0],
            'mileage': mileage,
            'service': parts[2],
            'tech':    parts[3] if len(parts) > 3 else '',
            'cost':    cost,
            'notes':   parts[5] if len(parts) > 5 else '',
        })

    records.sort(key=lambda x: x['mileage'])
    return records


def last_mileage_for_service(records: list, service_name: str) -> int:
    """Find the highest mileage at which a service matching service_name was performed."""
    keyword = service_name.lower()
    best = 0
    for r in records:
        svc = r['service'].lower()
        if any(k in svc for k in SERVICE_KEYWORDS if SERVICE_KEYWORDS[k] == service_name):
            if r['mileage'] > best:
                best = r['mileage']
    return best


def compute_upcoming(records: list, current_mileage: int) -> list:
    """Return list of (urgency, service, due_detail) tuples for services due soon."""
    upcoming = []
    for svc_name, interval, _first, urgency in MAINTENANCE_SCHEDULE:
        last_done = last_mileage_for_service(records, svc_name)
        if last_done == 0:
            # Never done — base due mileage on first_due from current
            next_due = ((current_mileage // interval) + 1) * interval
        else:
            next_due = last_done + interval

        miles_until_due = next_due - current_mileage

        # Show items due within the next 3,000 miles or overdue
        if miles_until_due <= 3_000:
            if miles_until_due <= 0:
                detail = f"OVERDUE by {abs(miles_until_due):,} miles (due at {next_due:,} mi)"
                urg = "OVERDUE"
            elif miles_until_due <= 500:
                detail = f"Due NOW — within {miles_until_due:,} miles ({next_due:,} mi)"
                urg = "URGENT"
            elif miles_until_due <= 1_500:
                detail = f"Due soon — within ~{miles_until_due:,} miles ({next_due:,} mi)"
                urg = "SOON"
            else:
                detail = f"Coming up — within ~{miles_until_due:,} miles ({next_due:,} mi)"
                urg = urgency
            upcoming.append((urg, svc_name, detail))

    return upcoming


def system_health(records: list, current_mileage: int) -> list:
    """
    Return list of (system, status, note) based on service history.
    Conservative: "Unable to Assess" when data is insufficient.
    """
    systems = []

    def has_service(*keywords):
        for r in records:
            svc = r['service'].lower()
            for kw in keywords:
                if kw in svc:
                    return True, r
        return False, None

    # Engine Oil
    found, rec = has_service('oil change', 'oil & filter', 'oil filter')
    if found:
        miles_since = current_mileage - rec['mileage']
        if miles_since < 4_000:
            status, note = "✅ GOOD", f"Last changed at {rec['mileage']:,} mi — {miles_since:,} miles ago"
        elif miles_since < 6_000:
            status, note = "⚠️  MONITOR", f"Oil change due soon (last at {rec['mileage']:,} mi)"
        else:
            status, note = "🔴 ATTENTION", f"Oil overdue — last changed {miles_since:,} miles ago"
    else:
        status, note = "❓ UNABLE TO ASSESS", "No oil change records on file"
    systems.append(("Engine Oil", status, note))

    # Brakes
    found, rec = has_service('brake pad', 'brake rotor', 'brake service', 'brakes')
    if found:
        miles_since = current_mileage - rec['mileage']
        status = "✅ GOOD" if miles_since < 20_000 else "⚠️  MONITOR"
        note = f"Brake service at {rec['mileage']:,} mi — {miles_since:,} miles ago"
    else:
        status, note = "❓ UNABLE TO ASSESS", "No brake service records on file"
    systems.append(("Brakes", status, note))

    # Tires
    found, rec = has_service('tire rotation', 'tires', 'tire balance', 'new tires')
    if found:
        miles_since = current_mileage - rec['mileage']
        status = "✅ GOOD" if miles_since < 7_000 else "⚠️  MONITOR"
        note = f"Tire service at {rec['mileage']:,} mi — {miles_since:,} miles ago"
    else:
        status, note = "❓ UNABLE TO ASSESS", "No tire service records on file"
    systems.append(("Tires & Wheels", status, note))

    # Transmission
    found, rec = has_service('transmission fluid', 'transmission service')
    if found:
        miles_since = current_mileage - rec['mileage']
        status = "✅ GOOD" if miles_since < 25_000 else "⚠️  MONITOR"
        note = f"Trans fluid at {rec['mileage']:,} mi — {miles_since:,} miles ago"
    else:
        status, note = "❓ UNABLE TO ASSESS", "No transmission fluid records on file"
    systems.append(("Transmission", status, note))

    # Cooling System
    found, rec = has_service('coolant', 'radiator flush', 'cooling system')
    if found:
        miles_since = current_mileage - rec['mileage']
        status = "✅ GOOD" if miles_since < 40_000 else "⚠️  MONITOR"
        note = f"Coolant service at {rec['mileage']:,} mi — {miles_since:,} miles ago"
    else:
        status, note = "❓ UNABLE TO ASSESS", "No coolant service records on file"
    systems.append(("Cooling System", status, note))

    return systems


def build_report(profile: dict, args) -> str:
    records = parse_records(args.records)
    shop     = profile.get('shop_name', 'Your Auto Shop')
    phone    = profile.get('phone', '')
    address  = profile.get('address', '')
    website  = profile.get('website', '')
    tagline  = profile.get('tagline', '')
    today    = datetime.now().strftime('%B %d, %Y')

    total_cost = sum(r['cost'] for r in records)
    last_svc   = records[-1] if records else None
    first_svc  = records[0] if records else None

    # Determine last service date string
    last_date_str  = last_svc['date'] if last_svc else 'N/A'
    first_date_str = first_svc['date'] if first_svc else 'N/A'

    upcoming = compute_upcoming(records, args.mileage)
    health   = system_health(records, args.mileage)

    W = 65  # report width

    lines = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append("=" * W)
    lines.append(f"  VEHICLE SERVICE HISTORY REPORT".center(W))
    lines.append(f"  {shop}".center(W))
    lines.append("=" * W)
    if address:
        lines.append(f"  {address}".center(W))
    parts = []
    if phone:   parts.append(phone)
    if website: parts.append(website)
    if parts:
        lines.append(f"  {' | '.join(parts)}".center(W))
    lines.append(f"  Report Generated: {today}".center(W))
    lines.append("=" * W)

    # ── Customer & Vehicle Info ────────────────────────────────────────────────
    lines.append("")
    lines.append("  VEHICLE & CUSTOMER INFORMATION")
    lines.append("  " + "─" * (W - 2))
    lines.append(f"  Customer Name   : {args.customer}")
    lines.append(f"  Vehicle         : {args.vehicle}")
    if args.vin:
        lines.append(f"  VIN             : {args.vin}")
    lines.append(f"  Current Mileage : {args.mileage:,} miles")
    lines.append(f"  History On File : {first_date_str} through {last_date_str}")
    lines.append("")

    # ── Service Timeline ───────────────────────────────────────────────────────
    lines.append("  SERVICE TIMELINE  (chronological)")
    lines.append("  " + "─" * (W - 2))

    # Column widths
    col_date   = 12
    col_mi     = 10
    col_svc    = 28
    col_tech   = 12

    header = (
        f"  {'DATE':<{col_date}} {'MILEAGE':>{col_mi}}  "
        f"{'SERVICE':<{col_svc}} {'TECH':<{col_tech}}  {'COST':>8}"
    )
    lines.append(header)
    lines.append("  " + "─" * (W - 2))

    for r in records:
        mi_str   = f"{r['mileage']:,}" if r['mileage'] else ''
        cost_str = f"${r['cost']:,.2f}" if r['cost'] else ''
        tech_str = (r['tech'][:col_tech]) if r['tech'] else ''
        svc_str  = r['service']

        # Wrap long service names
        if len(svc_str) > col_svc:
            svc_first = svc_str[:col_svc]
            svc_rest  = svc_str[col_svc:]
        else:
            svc_first = svc_str
            svc_rest  = ''

        row = (
            f"  {r['date']:<{col_date}} {mi_str:>{col_mi}}  "
            f"{svc_first:<{col_svc}} {tech_str:<{col_tech}}  {cost_str:>8}"
        )
        lines.append(row)

        if svc_rest:
            pad = " " * (2 + col_date + 1 + col_mi + 2)
            lines.append(f"{pad}{svc_rest}")

        if r['notes']:
            pad = " " * (2 + col_date + 1 + col_mi + 2)
            lines.append(f"{pad}Note: {r['notes']}")

    lines.append("  " + "─" * (W - 2))

    # ── Summary Stats ─────────────────────────────────────────────────────────
    lines.append("")
    lines.append("  SUMMARY")
    lines.append("  " + "─" * (W - 2))
    lines.append(f"  Total services documented : {len(records)}")
    lines.append(f"  Total maintenance spend   : ${total_cost:,.2f}")
    lines.append(f"  First service on record   : {first_date_str}")
    lines.append(f"  Most recent service       : {last_date_str}")
    if last_svc:
        miles_since_last = args.mileage - last_svc['mileage']
        lines.append(f"  Miles since last service  : {miles_since_last:,}")
    lines.append("")

    # ── Vehicle Health Summary ─────────────────────────────────────────────────
    lines.append("  VEHICLE SYSTEM HEALTH SUMMARY")
    lines.append("  " + "─" * (W - 2))
    lines.append("  Based on service records on file. Not a substitute for inspection.")
    lines.append("")
    for system, status, note in health:
        lines.append(f"  {system:<22} {status}")
        lines.append(f"  {'':22} {note}")
        lines.append("")

    # ── Upcoming Recommended Services ─────────────────────────────────────────
    lines.append("  UPCOMING RECOMMENDED SERVICES")
    lines.append("  " + "─" * (W - 2))
    lines.append("  Based on standard manufacturer intervals — general guidance only.")
    lines.append("")

    if upcoming:
        urgency_order = {'OVERDUE': 0, 'URGENT': 1, 'SOON': 2, 'MONITOR': 3, 'ROUTINE': 4}
        upcoming.sort(key=lambda x: urgency_order.get(x[0], 9))
        for urgency, svc_name, detail in upcoming:
            tag = f"[{urgency}]"
            lines.append(f"  {tag:<12} {svc_name}")
            lines.append(f"  {'':12} {detail}")
            lines.append("")
    else:
        lines.append("  No services due within the next 3,000 miles. Keep it up!")
        lines.append("")

    # ── Notes ─────────────────────────────────────────────────────────────────
    lines.append("  TECHNICIAN NOTES")
    lines.append("  " + "─" * (W - 2))
    lines.append("")
    lines.append("  " + "_" * (W - 4))
    lines.append("  " + "_" * (W - 4))
    lines.append("  " + "_" * (W - 4))
    lines.append("")

    # ── Footer ────────────────────────────────────────────────────────────────
    lines.append("=" * W)
    lines.append(f"  {shop}".center(W))
    if address:
        lines.append(f"  {address}".center(W))
    if phone:
        lines.append(f"  {phone}".center(W))
    if website:
        lines.append(f"  {website}".center(W))
    if tagline:
        lines.append("")
        lines.append(f'  "{tagline}"'.center(W))
    lines.append("")
    lines.append("  Thank you for trusting us with your vehicle.".center(W))
    lines.append("  Questions? Give us a call — we're happy to help.".center(W))
    lines.append("=" * W)

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate a vehicle service history report")
    parser.add_argument('--customer', required=True,       help="Customer full name")
    parser.add_argument('--vehicle',  required=True,       help="Year Make Model (e.g. '2019 Toyota Camry SE')")
    parser.add_argument('--mileage',  required=True, type=int, help="Current vehicle mileage")
    parser.add_argument('--vin',      default='',          help="VIN number (optional)")
    parser.add_argument('--records',  required=True,       help="Service records as JSON array or semicolon-delimited text")
    parser.add_argument('--output',   default='',          help="Custom output filename (optional)")
    args = parser.parse_args()

    profile = load_profile()
    report  = build_report(profile, args)

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

    filename = args.output if args.output else 'service_history_report.txt'
    filepath = os.path.join(os.path.abspath(OUTPUT_DIR), filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)

    print(report)
    print(f"\n✅ Saved: output/service_history/{filename}")


if __name__ == '__main__':
    main()
