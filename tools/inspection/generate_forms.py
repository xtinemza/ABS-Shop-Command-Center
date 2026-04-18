#!/usr/bin/env python3
"""
Generate vehicle inspection forms (blank) and customer-facing inspection reports (completed).

MODE: form — Generates a printable multi-point inspection checklist.
MODE: report — Takes JSON results and generates a color-coded customer report.

Usage — blank form:
    python tools/inspection/generate_forms.py \
        --mode form \
        --type multi_point \
        --customer "Sarah Mitchell" \
        --vehicle "2019 Toyota Camry SE" \
        --mileage 67000

Usage — completed report:
    python tools/inspection/generate_forms.py \
        --mode report \
        --customer "David Chen" \
        --vehicle "2017 Honda CR-V" \
        --mileage 84200 \
        --results '[{"category":"Brakes","item":"Front brake pads","status":"needs_attention","notes":"2mm remaining"},{"category":"Battery & Electrical","item":"Battery voltage","status":"urgent","notes":"285 CCA vs 550 rated"}]'

Status values: good | fair | needs_attention | urgent | not_inspected
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
from collections import defaultdict

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'inspection')

# ---------------------------------------------------------------------------
# Status display config
# ---------------------------------------------------------------------------
STATUS_DISPLAY = {
    "good":            ("✅ GOOD",            0),
    "fair":            ("⚠️  FAIR",            1),
    "needs_attention": ("🔴 NEEDS ATTENTION", 2),
    "urgent":          ("🚨 URGENT",          3),
    "not_inspected":   ("⬜ NOT INSPECTED",   4),
}

STATUS_SORT = {k: v[1] for k, v in STATUS_DISPLAY.items()}

# ---------------------------------------------------------------------------
# Blank form templates
# ---------------------------------------------------------------------------
FORM_TEMPLATES = {
    "multi_point": {
        "title": "MULTI-POINT VEHICLE INSPECTION",
        "categories": {
            "BRAKES": [
                "Front brake pad thickness",
                "Rear brake pad thickness",
                "Front rotors — condition & thickness",
                "Rear rotors — condition & thickness",
                "Brake lines & hoses",
                "Brake fluid level & condition",
                "Parking brake operation",
                "ABS warning light status",
            ],
            "TIRES & WHEELS": [
                "Front left — tread depth & condition",
                "Front right — tread depth & condition",
                "Rear left — tread depth & condition",
                "Rear right — tread depth & condition",
                "Tire pressure (all 4 + spare)",
                "Wear pattern (even/uneven)",
                "Spare tire condition & pressure",
                "Wheel alignment indicators",
            ],
            "FLUIDS": [
                "Engine oil — level & condition",
                "Engine coolant — level & condition",
                "Transmission fluid — level & condition",
                "Brake fluid — level & condition",
                "Power steering fluid — level",
                "Windshield washer fluid — level",
                "Differential fluid (if applicable)",
            ],
            "BELTS & HOSES": [
                "Serpentine / drive belt — condition",
                "Timing belt (if externally visible)",
                "Upper coolant hose",
                "Lower coolant hose",
                "Heater hoses",
                "AC hoses (if visible)",
            ],
            "BATTERY & ELECTRICAL": [
                "Battery voltage (load test)",
                "Battery terminals & cable condition",
                "Headlights — low beam",
                "Headlights — high beam",
                "Tail lights & brake lights",
                "Turn signals (front & rear)",
                "Hazard lights",
                "Reverse lights",
                "Interior lights & dome light",
                "Horn operation",
            ],
            "SUSPENSION & STEERING": [
                "Front shocks / struts — condition",
                "Rear shocks / struts — condition",
                "Tie rod ends",
                "Ball joints",
                "Control arm bushings",
                "Steering play & response",
                "CV joints & boots",
                "Sway bar links & bushings",
            ],
            "EXHAUST SYSTEM": [
                "Exhaust leaks (manifold to tip)",
                "Muffler condition",
                "Exhaust hangers & brackets",
                "Catalytic converter",
                "Flex pipe condition (if equipped)",
            ],
            "UNDER HOOD": [
                "Engine air filter",
                "Cabin air filter",
                "Wiring & connectors — visible damage",
                "Engine mounts",
                "Visible fluid leaks — top of engine",
                "PCV valve & hose",
            ],
            "UNDER VEHICLE": [
                "Engine oil leaks",
                "Transmission fluid leaks",
                "Differential leaks",
                "Frame / subframe — corrosion or damage",
                "CV axles — boots & condition",
                "Transfer case (4WD/AWD vehicles)",
            ],
            "EXTERIOR & INTERIOR": [
                "Windshield & glass — chips / cracks",
                "Wiper blades — condition",
                "Mirrors — condition & adjustment",
                "Door locks & handles",
                "Seat belts — operation & condition",
                "Dashboard warning lights",
            ],
        },
    },
    "pre_purchase": {
        "title": "PRE-PURCHASE VEHICLE INSPECTION",
        "categories": {
            "EXTERIOR BODY": [
                "Overall paint condition & gloss",
                "Color match between panels",
                "Signs of rust or corrosion",
                "Panel gaps & alignment",
                "Evidence of previous collision repair / repaint",
                "Glass — chips, cracks, seals",
                "Trim, moldings & emblems",
                "Undercarriage rust / frame damage",
            ],
            "ENGINE & MECHANICAL": [
                "Cold start behavior & idle quality",
                "Acceleration response",
                "Unusual noises at idle",
                "Engine oil — level, condition, smell",
                "Coolant — level, color, smell",
                "Visible leaks (top & bottom)",
                "Check engine / warning lights",
                "Engine mounts",
            ],
            "TRANSMISSION & DRIVETRAIN": [
                "Automatic: smooth shifts 1–2, 2–3, 3–4",
                "Manual: clutch engagement, bite point",
                "Reverse operation",
                "4WD / AWD engagement (if equipped)",
                "Differential condition",
                "CV joints & boots",
            ],
            "BRAKES": [
                "Front pad thickness (%)",
                "Rear pad thickness (%)",
                "Front rotor condition",
                "Rear rotor condition",
                "Brake fluid — level & color",
                "Brake feel (firm / soft / spongy)",
                "Parking brake operation",
                "ABS function",
            ],
            "TIRES": [
                "Front left — tread depth (mm or 32nds)",
                "Front right — tread depth",
                "Rear left — tread depth",
                "Rear right — tread depth",
                "Tire DOT age code",
                "Matching brand / size all four",
                "Wear pattern — even?",
                "Spare condition & pressure",
            ],
            "ELECTRICAL & HVAC": [
                "All exterior lights functioning",
                "All interior gauges working",
                "Air conditioning — cools properly",
                "Heater — heats properly",
                "Defroster (front & rear)",
                "Power windows & locks",
                "Radio & infotainment",
                "Charging ports / outlets",
            ],
            "UNDERCARRIAGE": [
                "Frame rails — rust / damage",
                "Exhaust — leaks, hangers, condition",
                "Suspension components",
                "Shock / strut condition",
                "Bushing condition",
                "Brake hardware",
            ],
            "TEST DRIVE OBSERVATIONS": [
                "Cold start to operating temp — smooth?",
                "Acceleration — hesitation or surging?",
                "Braking — straight? Vibration?",
                "Steering — pulls? Play? Vibration?",
                "Highway stability",
                "Unusual noises (clunk, squeal, rattle)",
                "Vibrations at speed",
                "Transmission shifts — all gears OK?",
            ],
        },
    },
    "seasonal": {
        "title": "SEASONAL VEHICLE INSPECTION",
        "categories": {
            "WINTER / COLD WEATHER PREP": [
                "Battery load test (cold CCA rating)",
                "Coolant freeze point (target: -34°F or below)",
                "Heater output & blower operation",
                "Front & rear defrosters",
                "Wiper blades — winter-ready?",
                "Washer fluid — winter grade?",
                "Tire tread depth (minimum 4/32\" for snow)",
                "Tire pressure (check cold PSI)",
                "Belts — cold-weather cracking?",
                "Coolant hoses — soft or swollen?",
                "4WD / AWD system operation",
                "Emergency kit present (blanket, jumper cables, etc.)",
            ],
            "SPRING / SUMMER PREP": [
                "AC performance — cools to target temp?",
                "AC refrigerant level (sight glass check)",
                "Cabin air filter — replace for pollen season?",
                "Coolant level & condition",
                "Tire pressure (adjust for heat expansion)",
                "Battery condition (heat kills batteries too)",
                "Serpentine belt — heat cracking?",
                "Wiper blades — clear vision in rain?",
                "Brake inspection — post-winter check",
            ],
            "ALL SEASONS / GENERAL": [
                "Engine oil — level & condition",
                "Transmission fluid",
                "Brake fluid",
                "Power steering fluid",
                "All exterior lights functioning",
                "Tire tread depth & condition",
                "Brake pads & rotors",
                "Suspension components",
            ],
        },
    },
}

# ---------------------------------------------------------------------------
# Plain-language explanations for common inspection items (used in reports)
# ---------------------------------------------------------------------------
ITEM_PLAIN_LANGUAGE = {
    "brake pad": "brake pads (the friction material that stops your vehicle)",
    "rotor": "brake rotors (the metal discs the pads clamp onto)",
    "brake fluid": "brake fluid (the hydraulic fluid that powers your brakes)",
    "serpentine": "serpentine belt (drives your alternator, power steering, and AC)",
    "battery": "battery (starts your engine and powers your electronics)",
    "coolant": "coolant/antifreeze (prevents overheating and freezing)",
    "oil": "engine oil (lubricates all moving engine parts)",
    "transmission fluid": "transmission fluid (keeps your gearbox shifting smoothly)",
    "tire": "tire tread (provides grip for stopping and cornering)",
    "shock": "shocks/struts (control your suspension and ride quality)",
    "strut": "shocks/struts (control your suspension and ride quality)",
    "cv joint": "CV joints (transfer power from the transmission to the wheels)",
    "tie rod": "tie rod ends (connect your steering to your wheels)",
    "ball joint": "ball joints (connect your suspension to the steering knuckle)",
    "air filter": "engine air filter (keeps debris out of your engine)",
    "cabin air": "cabin air filter (cleans the air inside your vehicle)",
    "wiper": "wiper blades (visibility in rain and snow)",
}

# Consequence language by status
CONSEQUENCE_BY_STATUS = {
    "urgent": (
        "This item requires immediate attention. Driving with this condition "
        "may pose a safety risk or could cause further damage to your vehicle."
    ),
    "needs_attention": (
        "This item should be addressed at your earliest convenience to prevent "
        "further wear or a more expensive repair."
    ),
    "fair": (
        "This item is within an acceptable range but trending toward needing "
        "service. We recommend monitoring it at your next visit."
    ),
}


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if not os.path.exists(path):
        print("ERROR: shop_profile.json not found.", file=sys.stderr)
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _wrap(text: str, width: int) -> list:
    words = text.split()
    lines, current, current_len = [], [], 0
    for word in words:
        if current_len + len(word) + (1 if current else 0) > width:
            lines.append(' '.join(current))
            current, current_len = [word], len(word)
        else:
            current.append(word)
            current_len += len(word) + (1 if len(current) > 1 else 0)
    if current:
        lines.append(' '.join(current))
    return lines


# ════════════════════════════════════════════════════════════════════════════
# FORM MODE
# ════════════════════════════════════════════════════════════════════════════

def generate_blank_form(profile: dict, args) -> str:
    shop    = profile.get('shop_name', 'Your Auto Shop')
    phone   = profile.get('phone', '')
    address = profile.get('address', '')
    today   = datetime.now().strftime('%B %d, %Y')

    form_type = args.type or 'multi_point'
    if form_type not in FORM_TEMPLATES:
        print(f"ERROR: Unknown form type '{form_type}'. Choose: {', '.join(FORM_TEMPLATES.keys())}", file=sys.stderr)
        sys.exit(1)

    template = FORM_TEMPLATES[form_type]
    W = 68

    lines = []

    # Header
    lines.append("=" * W)
    lines.append(f"  {template['title']}".center(W))
    lines.append(f"  {shop}".center(W))
    lines.append("=" * W)
    if address:
        lines.append(f"  {address}".center(W))
    if phone:
        lines.append(f"  {phone}".center(W))
    lines.append("")

    # Vehicle info block
    cust_pre   = args.customer or ''
    veh_pre    = args.vehicle or ''
    mi_pre     = f"{int(args.mileage):,}" if args.mileage else ''

    lines.append(f"  Customer  : {cust_pre:<30}  Date      : {today}")
    lines.append(f"  Vehicle   : {veh_pre:<30}  Mileage   : {mi_pre}")
    lines.append(f"  VIN       : {'':40}")
    lines.append(f"  License   : {'':20}  Technician: {'':15}")
    lines.append("")
    lines.append("  RATING KEY:")
    lines.append("    ✅ GOOD  |  ⚠️  FAIR  |  🔴 NEEDS ATTENTION  |  🚨 URGENT  |  ⬜ NOT INSPECTED")
    lines.append("")

    total_items = 0
    for category, items in template['categories'].items():
        lines.append("  " + "─" * (W - 4))
        lines.append(f"  ▶  {category}")
        lines.append("  " + "─" * (W - 4))
        for item in items:
            total_items += 1
            lines.append(f"  ☐  {item:<44}  ✅ ⚠️  🔴 🚨 ⬜")
            lines.append(f"       Notes: {'_' * 48}")
        lines.append("")

    # Footer / signature block
    lines.append("=" * W)
    lines.append("  TECHNICIAN NOTES & OVERALL ASSESSMENT")
    lines.append("  " + "─" * (W - 4))
    lines.append("")
    lines.append("  " + "_" * (W - 4))
    lines.append("  " + "_" * (W - 4))
    lines.append("  " + "_" * (W - 4))
    lines.append("")
    lines.append(f"  Technician Signature: {'_' * 30}  Date: {'_' * 12}")
    lines.append("")
    lines.append(f"  Advisor Signature   : {'_' * 30}  Date: {'_' * 12}")
    lines.append("")
    lines.append("=" * W)
    lines.append(f"  {shop}  |  {phone}  |  {address}".center(W))
    lines.append("=" * W)

    return '\n'.join(lines), total_items, len(template['categories'])


# ════════════════════════════════════════════════════════════════════════════
# REPORT MODE
# ════════════════════════════════════════════════════════════════════════════

def generate_report(profile: dict, args) -> str:
    shop    = profile.get('shop_name', 'Your Auto Shop')
    phone   = profile.get('phone', '')
    address = profile.get('address', '')
    website = profile.get('website', '')
    tagline = profile.get('tagline', '')
    today   = datetime.now().strftime('%B %d, %Y')

    customer = args.customer or 'Valued Customer'
    vehicle  = args.vehicle or 'Your Vehicle'
    mileage  = int(args.mileage) if args.mileage else 0
    mi_str   = f"{mileage:,}" if mileage else 'N/A'

    # Parse results
    try:
        results = json.loads(args.results)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse --results JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(results, list):
        print("ERROR: --results must be a JSON array.", file=sys.stderr)
        sys.exit(1)

    # Normalize statuses
    for r in results:
        r['status'] = r.get('status', 'not_inspected').lower().strip().replace(' ', '_')
        if r['status'] not in STATUS_DISPLAY:
            r['status'] = 'not_inspected'

    # Count by status
    counts = {k: 0 for k in STATUS_DISPLAY}
    for r in results:
        counts[r['status']] = counts.get(r['status'], 0) + 1

    # Group by category
    by_category = defaultdict(list)
    for r in results:
        by_category[r.get('category', 'General')].append(r)

    # Priority items: urgent and needs_attention
    priority = [r for r in results if r['status'] in ('urgent', 'needs_attention')]
    priority.sort(key=lambda x: STATUS_SORT.get(x['status'], 9))

    W = 68

    lines = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append("=" * W)
    lines.append("  VEHICLE INSPECTION REPORT".center(W))
    lines.append(f"  {shop}".center(W))
    lines.append("=" * W)
    info_parts = []
    if phone:   info_parts.append(phone)
    if website: info_parts.append(website)
    if info_parts:
        lines.append(f"  {' | '.join(info_parts)}".center(W))
    lines.append(f"  {today}".center(W))
    lines.append("=" * W)
    lines.append("")

    # ── Customer & Vehicle ─────────────────────────────────────────────────────
    lines.append(f"  Customer  : {customer}")
    lines.append(f"  Vehicle   : {vehicle}")
    lines.append(f"  Mileage   : {mi_str} miles")
    lines.append(f"  Inspected : {today}")
    lines.append("")

    # ── Summary scorecard ──────────────────────────────────────────────────────
    lines.append("  INSPECTION SUMMARY")
    lines.append("  " + "─" * (W - 4))
    lines.append(f"  ✅ GOOD             :  {counts.get('good', 0):>3} items — no action needed")
    lines.append(f"  ⚠️  FAIR             :  {counts.get('fair', 0):>3} items — monitor at next visit")
    lines.append(f"  🔴 NEEDS ATTENTION  :  {counts.get('needs_attention', 0):>3} items — service recommended")
    lines.append(f"  🚨 URGENT           :  {counts.get('urgent', 0):>3} items — address immediately")
    if counts.get('not_inspected', 0):
        lines.append(f"  ⬜ NOT INSPECTED   :  {counts.get('not_inspected', 0):>3} items")
    lines.append("")

    # Overall assessment
    if counts.get('urgent', 0) > 0:
        assessment = (
            f"⚠️  ACTION REQUIRED: {counts['urgent']} item(s) need immediate attention. "
            "Please review the PRIORITY section below before driving."
        )
    elif counts.get('needs_attention', 0) > 0:
        assessment = (
            f"This vehicle is in fair condition overall. {counts['needs_attention']} item(s) "
            "need service — we recommend addressing these at your earliest convenience."
        )
    elif counts.get('fair', 0) > 0:
        assessment = (
            "This vehicle is in good shape overall. A few items to keep an eye on — "
            "we'll check them again at your next visit."
        )
    else:
        assessment = (
            "Great news — this vehicle passed all inspection points. "
            "Keep up with your regular maintenance schedule and you're good to go."
        )

    for chunk in _wrap(assessment, W - 4):
        lines.append(f"  {chunk}")
    lines.append("")

    # ── Priority items ─────────────────────────────────────────────────────────
    if priority:
        lines.append("=" * W)
        lines.append("  PRIORITY ITEMS — ACTION REQUIRED".center(W))
        lines.append("=" * W)
        lines.append("")
        for r in priority:
            item_name = r.get('item', 'Unknown item')
            status    = r['status']
            notes     = r.get('notes', '')
            disp, _   = STATUS_DISPLAY.get(status, ("UNKNOWN", 9))

            # Plain language name lookup
            plain = item_name
            for key, plain_val in ITEM_PLAIN_LANGUAGE.items():
                if key in item_name.lower():
                    plain = plain_val
                    break

            lines.append(f"  {disp}  —  {item_name}")
            if plain != item_name:
                lines.append(f"  What this is: {plain}")
            if notes:
                lines.append(f"  Technician finding: {notes}")
            consequence = CONSEQUENCE_BY_STATUS.get(status, '')
            if consequence:
                for chunk in _wrap(consequence, W - 6):
                    lines.append(f"    {chunk}")
            lines.append("")

    # ── Full findings by category ──────────────────────────────────────────────
    lines.append("=" * W)
    lines.append("  COMPLETE INSPECTION FINDINGS".center(W))
    lines.append("=" * W)
    lines.append("")

    for category, items in by_category.items():
        # Sort within category: worst first
        items_sorted = sorted(items, key=lambda x: STATUS_SORT.get(x['status'], 9))
        lines.append(f"  ▶  {category.upper()}")
        lines.append("  " + "─" * (W - 4))
        for r in items_sorted:
            item_name = r.get('item', 'Unknown')
            status    = r['status']
            notes     = r.get('notes', '')
            disp, _   = STATUS_DISPLAY.get(status, ("UNKNOWN", 9))
            lines.append(f"  {disp}  {item_name}")
            if notes:
                lines.append(f"           Note: {notes}")
        lines.append("")

    # ── Recommendations ────────────────────────────────────────────────────────
    if priority:
        lines.append("=" * W)
        lines.append("  RECOMMENDED SERVICES".center(W))
        lines.append("=" * W)
        lines.append("")
        lines.append("  Based on today's inspection, we recommend the following services:")
        lines.append("")

        # Sort: urgent first
        urgent_items  = [r for r in priority if r['status'] == 'urgent']
        attention_items = [r for r in priority if r['status'] == 'needs_attention']

        if urgent_items:
            lines.append("  IMMEDIATE (address before next drive):")
            for r in urgent_items:
                lines.append(f"    • {r.get('item', 'Unknown item')}")
                if r.get('notes'):
                    lines.append(f"      Finding: {r['notes']}")
            lines.append("")

        if attention_items:
            lines.append("  SOON (within 30–60 days):")
            for r in attention_items:
                lines.append(f"    • {r.get('item', 'Unknown item')}")
                if r.get('notes'):
                    lines.append(f"      Finding: {r['notes']}")
            lines.append("")

        fair_items = [r for r in results if r['status'] == 'fair']
        if fair_items:
            lines.append("  MONITOR (discuss at next visit):")
            for r in fair_items:
                lines.append(f"    • {r.get('item', 'Unknown item')}")
            lines.append("")

    # ── Footer ────────────────────────────────────────────────────────────────
    lines.append("=" * W)
    closing = (
        "Questions about anything on this report? We'd love to walk you through it. "
        "Ask your service advisor — no question is too small."
    )
    for chunk in _wrap(closing, W - 4):
        lines.append(f"  {chunk}")
    lines.append("")
    lines.append(f"  {shop}".center(W))
    if address:
        lines.append(f"  {address}".center(W))
    if phone:
        lines.append(f"  {phone}".center(W))
    if website:
        lines.append(f"  {website}".center(W))
    if tagline:
        lines.append(f'  "{tagline}"'.center(W))
    lines.append("=" * W)

    return '\n'.join(lines), counts


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Generate inspection forms and customer reports")
    parser.add_argument('--mode',     required=True, choices=['form', 'report'],
                        help="'form' = blank checklist, 'report' = completed customer report")
    parser.add_argument('--type',     default='multi_point',
                        choices=['multi_point', 'pre_purchase', 'seasonal'],
                        help="Inspection form type (form mode only)")
    parser.add_argument('--customer', default='',   help="Customer name")
    parser.add_argument('--vehicle',  default='',   help="Year Make Model")
    parser.add_argument('--mileage',  default=None, help="Current mileage")
    parser.add_argument('--results',  default='',   help="JSON array of inspection results (report mode)")
    parser.add_argument('--output',   default='',   help="Custom output filename (optional)")
    args = parser.parse_args()

    profile = load_profile()
    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

    if args.mode == 'form':
        content, total_items, num_categories = generate_blank_form(profile, args)

        filename = args.output if args.output else f"{args.type}_form.txt"
        filepath = os.path.join(os.path.abspath(OUTPUT_DIR), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(content)
        print(f"\n✅ Blank inspection form generated.")
        print(f"   Type     : {args.type.replace('_', ' ').title()}")
        if args.vehicle:
            print(f"   Vehicle  : {args.vehicle}")
        print(f"   Sections : {num_categories}")
        print(f"   Items    : {total_items}")
        print(f"   Saved to : output/inspection/{filename}")

    elif args.mode == 'report':
        if not args.results:
            print("ERROR: --results is required for report mode.", file=sys.stderr)
            sys.exit(1)
        if not args.customer or not args.vehicle:
            print("ERROR: --customer and --vehicle are required for report mode.", file=sys.stderr)
            sys.exit(1)

        content, counts = generate_report(profile, args)

        filename = args.output if args.output else 'inspection_report.txt'
        filepath = os.path.join(os.path.abspath(OUTPUT_DIR), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(content)
        print(f"\n✅ Inspection report generated.")
        print(f"   Customer          : {args.customer}")
        print(f"   Vehicle           : {args.vehicle}")
        print(f"   ✅ Good           : {counts.get('good', 0)}")
        print(f"   ⚠️  Fair           : {counts.get('fair', 0)}")
        print(f"   🔴 Needs Attention: {counts.get('needs_attention', 0)}")
        print(f"   🚨 Urgent         : {counts.get('urgent', 0)}")
        print(f"   Saved to          : output/inspection/{filename}")


if __name__ == '__main__':
    main()
