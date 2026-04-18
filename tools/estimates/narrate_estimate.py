#!/usr/bin/env python3
"""
Translate a repair estimate into plain-language customer explanations.

Accepts a full estimate as a JSON array of line items and produces a single,
copy-paste-ready customer-facing document in one pass.

Usage:
    python tools/estimates/narrate_estimate.py \
        --customer "David Chen" \
        --vehicle "2017 Honda CR-V" \
        --items '[{"part":"Front Brake Pads & Rotors","part_cost":180,"labor_hours":1.5,"labor_cost":142.50,"urgency":"high","notes":"Pads at 2mm, rotors scored"},{"part":"Serpentine Belt","part_cost":45,"labor_hours":0.5,"labor_cost":47.50,"urgency":"medium","notes":""},{"part":"Cabin Air Filter","part_cost":22,"labor_hours":0.25,"labor_cost":23.75,"urgency":"low","notes":""}]'

Urgency levels: safety-critical | high | medium | low
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
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'estimates')

# ---------------------------------------------------------------------------
# Repair knowledge base — plain-language explanations for common repairs.
# Keyed by lowercase keyword fragments found in the part/service name.
# ---------------------------------------------------------------------------
REPAIR_KB = {
    "brake pad": {
        "plain_name": "Brake Pad Replacement",
        "what_it_is": (
            "Your brake pads are the friction material that presses against "
            "the metal rotors to slow and stop your car. They are designed to "
            "wear down over time — that's normal. When they wear too thin, "
            "they lose the ability to stop your vehicle quickly and safely."
        ),
        "why_needed": (
            "Your technician measured the brake pad thickness and found it "
            "has worn below the safe minimum. At this point, braking "
            "performance is reduced and the metal backing can begin to "
            "contact the rotor, causing damage."
        ),
        "if_ignored": {
            "safety-critical": (
                "Dangerously thin pads can fail without warning. Stopping "
                "distances increase dramatically. This is a safety issue — "
                "do not drive this vehicle until repaired."
            ),
            "high": (
                "Continuing to drive will quickly wear the pads down to bare "
                "metal. Metal-on-metal contact will gouge and warp the rotors, "
                "turning a $180 parts cost into a $400+ repair. Your stopping "
                "distance is already longer than it should be."
            ),
            "medium": (
                "You have a little more time, but not much. Within the next "
                "month or two, worn pads will begin damaging the rotors and "
                "your stopping distance will increase noticeably."
            ),
            "low": (
                "You're not in danger yet, but scheduling sooner rather than "
                "later prevents rotor damage and keeps your repair costs lower."
            ),
        },
        "time_estimate": "1.5 – 2 hours per axle",
    },
    "rotor": {
        "plain_name": "Brake Rotor Replacement",
        "what_it_is": (
            "Brake rotors are the large metal discs your brake pads clamp "
            "onto to stop the vehicle. They must be flat and within a "
            "minimum thickness to work correctly. When they become too thin, "
            "warped, or scored, braking becomes uneven and noisy."
        ),
        "why_needed": (
            "The rotors have worn below their minimum safe thickness, are "
            "showing scoring from worn brake pads, or are warped from heat "
            "cycles. Resurfacing is no longer an option — replacement is needed."
        ),
        "if_ignored": {
            "safety-critical": (
                "Severely compromised rotors cannot reliably stop the vehicle. "
                "Do not drive until this is repaired."
            ),
            "high": (
                "Driving on bad rotors will accelerate wear on the new brake "
                "pads you'd otherwise install, and can lead to brake fade or "
                "failure in hard-stop situations. Address this now."
            ),
            "medium": (
                "Warped rotors cause vibration and uneven braking. This will "
                "not improve on its own — schedule within 30–60 days."
            ),
            "low": (
                "Rotors are marginal. Replacing them at the next brake job "
                "will save you from a separate repair visit later."
            ),
        },
        "time_estimate": "1 – 1.5 hours per axle",
    },
    "serpentine belt": {
        "plain_name": "Serpentine Belt Replacement",
        "what_it_is": (
            "The serpentine belt is a long rubber belt that wraps around "
            "several pulleys under the hood and drives critical systems: "
            "the alternator (which charges the battery), the power steering "
            "pump, the water pump, and the AC compressor. If it snaps, "
            "your vehicle will stop running — sometimes without warning."
        ),
        "why_needed": (
            "Your technician found visible cracking, fraying, or glazing on "
            "the belt. This is a sign that the rubber has aged and is at "
            "risk of breaking."
        ),
        "if_ignored": {
            "safety-critical": (
                "A broken serpentine belt disables your alternator and — on "
                "many vehicles — the water pump. You will lose power steering "
                "and your engine will overheat. This can strand you and "
                "lead to severe engine damage."
            ),
            "high": (
                "A cracked belt can snap at any time, including on the highway. "
                "This will strand you and may cause engine overheating. "
                "Replacing it now costs around $100–$150; towing plus repairs "
                "after a breakdown can easily exceed $500."
            ),
            "medium": (
                "The belt is cracking but hasn't failed yet. You have some "
                "time — plan to replace it within 30–60 days before it becomes "
                "a roadside emergency."
            ),
            "low": (
                "The belt is showing early wear. Replacing it proactively "
                "at your next service visit is the smart, cost-effective choice."
            ),
        },
        "time_estimate": "30 – 45 minutes",
    },
    "cabin air filter": {
        "plain_name": "Cabin Air Filter Replacement",
        "what_it_is": (
            "The cabin air filter cleans the air that flows through your "
            "car's heating and air conditioning system before it reaches "
            "you and your passengers. Over time it gets clogged with dust, "
            "pollen, and debris."
        ),
        "why_needed": (
            "The filter is clogged or has reached its service interval. "
            "A clogged filter reduces airflow from your vents and allows "
            "allergens and odors to pass through."
        ),
        "if_ignored": {
            "safety-critical": "N/A for this item.",
            "high": (
                "Severely blocked filters can reduce airflow significantly "
                "and put extra strain on the blower motor."
            ),
            "medium": (
                "Air quality inside the vehicle deteriorates and allergy "
                "sufferers will notice. HVAC efficiency drops."
            ),
            "low": (
                "This is routine maintenance. Schedule it at your next "
                "oil change — it takes about 15 minutes."
            ),
        },
        "time_estimate": "15 – 20 minutes",
    },
    "engine air filter": {
        "plain_name": "Engine Air Filter Replacement",
        "what_it_is": (
            "The engine air filter keeps dust and debris out of your engine. "
            "Clean air is essential for combustion — a clogged filter "
            "starves the engine of air, hurting fuel economy and performance."
        ),
        "why_needed": (
            "The filter is visibly dirty or has reached its mileage "
            "interval. Clean filters keep your engine running efficiently."
        ),
        "if_ignored": {
            "safety-critical": "N/A for this item.",
            "high": (
                "A severely clogged filter noticeably hurts fuel economy "
                "and can cause rough idle or hesitation."
            ),
            "medium": (
                "Fuel economy will decrease and engine performance may "
                "feel sluggish. Replace within 30 days."
            ),
            "low": (
                "Routine maintenance. Easy to combine with an oil change "
                "to minimize labor."
            ),
        },
        "time_estimate": "10 – 15 minutes",
    },
    "oil change": {
        "plain_name": "Oil & Filter Change",
        "what_it_is": (
            "Engine oil lubricates every moving part inside your engine, "
            "absorbs heat, and carries away microscopic metal particles and "
            "contaminants. Over time and miles, oil breaks down and becomes "
            "less effective at protecting your engine."
        ),
        "why_needed": (
            "The oil has reached its service interval by mileage or time. "
            "Fresh oil and a new filter restore full engine protection."
        ),
        "if_ignored": {
            "safety-critical": (
                "Severely degraded oil can cause catastrophic engine damage. "
                "Do not drive until the oil is changed."
            ),
            "high": (
                "Old oil accelerates engine wear and can lead to sludge "
                "buildup. Engine repairs from neglected oil changes can "
                "run into the thousands."
            ),
            "medium": (
                "You're past due — schedule this within the next few weeks "
                "to avoid unnecessary engine wear."
            ),
            "low": (
                "Routine service due. Easy to stay ahead of — keep the "
                "interval and your engine will thank you."
            ),
        },
        "time_estimate": "30 – 45 minutes",
    },
    "transmission fluid": {
        "plain_name": "Transmission Fluid Service",
        "what_it_is": (
            "Transmission fluid lubricates the gears and clutches inside "
            "your transmission and acts as a hydraulic fluid to control "
            "gear shifts. It degrades over time and loses its protective "
            "and performance properties."
        ),
        "why_needed": (
            "The fluid has discolored, smells burnt, or has reached its "
            "service interval. Fresh fluid restores smooth shifting and "
            "protects the transmission from heat damage."
        ),
        "if_ignored": {
            "safety-critical": (
                "Severely degraded fluid can cause immediate transmission "
                "failure. Do not drive until serviced."
            ),
            "high": (
                "Burnt or oxidized fluid causes rough shifting and accelerates "
                "wear on internal components. A transmission replacement "
                "can cost $2,500–$5,000+. Fluid service is a small price "
                "for big protection."
            ),
            "medium": (
                "Degraded fluid shortens transmission life. Address within "
                "30–60 days to avoid compounding the problem."
            ),
            "low": (
                "Proactive maintenance. Keep the interval and you'll "
                "significantly extend the life of your transmission."
            ),
        },
        "time_estimate": "45 – 60 minutes",
    },
    "coolant": {
        "plain_name": "Coolant Flush & Fill",
        "what_it_is": (
            "Coolant (antifreeze) flows through your engine and radiator "
            "to prevent overheating in summer and freezing in winter. "
            "Over time it becomes acidic and loses its protective additives, "
            "which can corrode cooling system components."
        ),
        "why_needed": (
            "The coolant has degraded or reached its service interval. "
            "Fresh coolant restores proper freeze/boil-over protection "
            "and prevents corrosion inside the radiator and engine block."
        ),
        "if_ignored": {
            "safety-critical": (
                "A compromised cooling system can lead to sudden overheating "
                "and engine damage. Do not drive until serviced."
            ),
            "high": (
                "Acidic coolant corrodes the radiator, water pump, and "
                "heater core — all expensive repairs. Overheating can "
                "warp the cylinder head."
            ),
            "medium": (
                "Schedule within 30–60 days. The longer degraded coolant "
                "circulates, the more corrosion builds up inside the system."
            ),
            "low": (
                "Routine interval service. Inexpensive now, very expensive "
                "if ignored long-term."
            ),
        },
        "time_estimate": "45 – 60 minutes",
    },
    "tire": {
        "plain_name": "Tire Service",
        "what_it_is": (
            "Your tires are the only part of your vehicle that touches the "
            "road. Tire tread provides traction for stopping, turning, and "
            "handling in wet or slippery conditions. Worn or improperly "
            "inflated tires affect every aspect of vehicle safety."
        ),
        "why_needed": (
            "Tread depth is at or below the safe minimum, or the tires "
            "show uneven wear, cracking, or bulging that makes them unsafe "
            "or unreliable."
        ),
        "if_ignored": {
            "safety-critical": (
                "Bald or structurally compromised tires are a blowout and "
                "loss-of-control risk. Do not drive on these tires."
            ),
            "high": (
                "Severely worn tires significantly increase stopping "
                "distances in wet conditions and risk a blowout at highway "
                "speeds. Replace before your next trip."
            ),
            "medium": (
                "Tires are marginal. Wet-weather grip is noticeably reduced. "
                "Plan to replace within 30 days."
            ),
            "low": (
                "Tires are approaching the end of their life. Budget for "
                "replacement at your next visit."
            ),
        },
        "time_estimate": "30 – 60 minutes (varies by service)",
    },
    "battery": {
        "plain_name": "Battery Replacement",
        "what_it_is": (
            "Your car battery provides the electrical power to start the "
            "engine and stabilizes the voltage for all your vehicle's "
            "electronics. Batteries have a typical life of 3–5 years."
        ),
        "why_needed": (
            "The battery tested below the minimum cold cranking amp (CCA) "
            "rating or showed signs of sulfation, swelling, or corrosion. "
            "A weak battery will eventually leave you stranded."
        ),
        "if_ignored": {
            "safety-critical": (
                "A failed battery means you will not be able to start "
                "your vehicle. Replace before the next drive."
            ),
            "high": (
                "A weak battery can fail to start the car without warning, "
                "often at the worst possible time. It can also damage the "
                "alternator if it forces it to overcharge constantly."
            ),
            "medium": (
                "The battery is marginal — fine for now, but monitor it "
                "closely and plan to replace it within 30 days."
            ),
            "low": (
                "Battery is showing age. Have it re-tested at your next visit "
                "and budget for replacement soon."
            ),
        },
        "time_estimate": "20 – 30 minutes",
    },
    "alignment": {
        "plain_name": "Wheel Alignment",
        "what_it_is": (
            "Wheel alignment adjusts the angles of your tires so they make "
            "contact with the road correctly and point in the right direction. "
            "Misalignment is caused by potholes, curb strikes, or normal "
            "wear over time."
        ),
        "why_needed": (
            "The vehicle is pulling to one side, the steering wheel is "
            "off-center, or uneven tire wear indicates the alignment is "
            "out of specification."
        ),
        "if_ignored": {
            "safety-critical": "N/A for this item in most cases.",
            "high": (
                "Severe misalignment accelerates tire wear dramatically — "
                "tires that should last 40,000 miles may wear out in 15,000. "
                "It also affects handling and fuel economy."
            ),
            "medium": (
                "Uneven tire wear will continue and worsen. "
                "Address within 30–60 days."
            ),
            "low": (
                "Routine alignment keeps your tires wearing evenly and "
                "saves money on premature tire replacement."
            ),
        },
        "time_estimate": "45 – 60 minutes",
    },
    "spark plug": {
        "plain_name": "Spark Plug Replacement",
        "what_it_is": (
            "Spark plugs ignite the air-fuel mixture in each cylinder to "
            "power the engine. Worn plugs misfire, causing rough idle, "
            "poor fuel economy, and reduced power. Most modern vehicles "
            "use long-life iridium or platinum plugs rated for 60,000–100,000 miles."
        ),
        "why_needed": (
            "The plugs are at or past their service interval. Worn plugs "
            "don't fire as efficiently, which costs you fuel economy and "
            "smoothness."
        ),
        "if_ignored": {
            "safety-critical": "N/A unless misfires are severe.",
            "high": (
                "Misfiring plugs can damage the catalytic converter — a "
                "$900–$2,500 repair — in addition to reducing fuel economy "
                "and causing rough running."
            ),
            "medium": (
                "You'll notice worse fuel economy and possible rough idle. "
                "Address within 30–60 days."
            ),
            "low": (
                "Routine interval. Replacing plugs on schedule prevents "
                "misfires and maximizes fuel efficiency."
            ),
        },
        "time_estimate": "1 – 2 hours (varies by engine layout)",
    },
}

URGENCY_LABELS = {
    "safety-critical": "🚨 SAFETY-CRITICAL — Do not drive until repaired",
    "high":            "🔴 HIGH — Strongly recommended this visit",
    "medium":          "🟡 MEDIUM — Address within 30–60 days",
    "low":             "🟢 LOW — Routine maintenance, schedule at next visit",
}

URGENCY_ORDER = {"safety-critical": 0, "high": 1, "medium": 2, "low": 3}


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if not os.path.exists(path):
        print("ERROR: shop_profile.json not found.", file=sys.stderr)
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_kb_entry(part_name: str) -> dict:
    """Match part name against knowledge base. Returns closest match or default."""
    name_lower = part_name.lower()
    for key, info in REPAIR_KB.items():
        if key in name_lower:
            return info
    return None


def format_currency(value) -> str:
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def parse_items(raw: str) -> list:
    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse --items as JSON: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(items, list):
        print("ERROR: --items must be a JSON array.", file=sys.stderr)
        sys.exit(1)
    return items


def narrate_item(item: dict, index: int, W: int) -> list:
    """Return list of text lines for a single estimate item."""
    part_name = item.get('part', f'Service Item {index + 1}')
    part_cost  = float(item.get('part_cost', 0) or 0)
    labor_cost = float(item.get('labor_cost', 0) or 0)
    labor_hrs  = float(item.get('labor_hours', 0) or 0)
    urgency    = item.get('urgency', 'medium').lower().strip()
    notes      = item.get('notes', '')
    total_cost = part_cost + labor_cost

    kb = find_kb_entry(part_name)
    urgency_label = URGENCY_LABELS.get(urgency, URGENCY_LABELS['medium'])

    lines = []
    lines.append("  " + "─" * (W - 4))
    lines.append(f"  ITEM {index + 1}:  {(kb['plain_name'] if kb else part_name).upper()}")
    lines.append(f"  {urgency_label}")
    lines.append("  " + "─" * (W - 4))

    # What it is
    lines.append("")
    lines.append("  WHAT THIS IS:")
    if kb:
        for chunk in _wrap(kb['what_it_is'], W - 4):
            lines.append(f"    {chunk}")
    else:
        lines.append(f"    {part_name} — your technician identified this as needing service.")
        if notes:
            lines.append(f"    Technician note: {notes}")

    # Why it's needed
    lines.append("")
    lines.append("  WHY YOUR VEHICLE NEEDS THIS:")
    if kb:
        for chunk in _wrap(kb['why_needed'], W - 4):
            lines.append(f"    {chunk}")
        if notes:
            lines.append(f"    Technician found: {notes}")
    else:
        lines.append(f"    Your technician identified this during inspection.")
        if notes:
            lines.append(f"    Specifically: {notes}")

    # What happens if ignored
    lines.append("")
    lines.append("  WHAT HAPPENS IF YOU WAIT:")
    if kb:
        consequence = kb['if_ignored'].get(urgency, kb['if_ignored'].get('medium', ''))
        for chunk in _wrap(consequence, W - 4):
            lines.append(f"    {chunk}")
    else:
        defer_map = {
            "safety-critical": "This is a safety concern. Do not defer.",
            "high":   "Deferring this repair will likely lead to a more expensive fix.",
            "medium": "Ignoring this will cause the problem to worsen over time.",
            "low":    "This is routine — safe to schedule at your convenience.",
        }
        lines.append(f"    {defer_map.get(urgency, defer_map['medium'])}")

    # Time estimate
    if kb and kb.get('time_estimate'):
        lines.append("")
        lines.append(f"  ESTIMATED REPAIR TIME:  {kb['time_estimate']}")

    # Cost breakdown
    lines.append("")
    lines.append("  COST BREAKDOWN:")
    if part_cost > 0 and labor_cost > 0:
        lines.append(f"    Parts   : {format_currency(part_cost)}")
        lines.append(f"    Labor   : {format_currency(labor_cost)}"
                     + (f"  ({labor_hrs} hrs)" if labor_hrs else ""))
        lines.append(f"    ─────────────────────")
        lines.append(f"    Total   : {format_currency(total_cost)}")
    elif part_cost > 0:
        lines.append(f"    Parts   : {format_currency(part_cost)}")
        lines.append(f"    Total   : {format_currency(part_cost)}")
    elif labor_cost > 0:
        lines.append(f"    Labor   : {format_currency(labor_cost)}"
                     + (f"  ({labor_hrs} hrs)" if labor_hrs else ""))
        lines.append(f"    Total   : {format_currency(labor_cost)}")
    else:
        lines.append(f"    Contact us for exact pricing on this item.")

    lines.append("")
    return lines


def _wrap(text: str, width: int) -> list:
    """Simple word-wrap."""
    words = text.split()
    lines = []
    current = []
    current_len = 0
    for word in words:
        if current_len + len(word) + (1 if current else 0) > width:
            lines.append(' '.join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += len(word) + (1 if len(current) > 1 else 0)
    if current:
        lines.append(' '.join(current))
    return lines


def build_document(profile: dict, args) -> str:
    items    = parse_items(args.items)
    shop     = profile.get('shop_name', 'Your Auto Shop')
    phone    = profile.get('phone', '')
    website  = profile.get('website', '')
    tagline  = profile.get('tagline', '')
    today    = datetime.now().strftime('%B %d, %Y')
    customer = args.customer or 'Valued Customer'
    vehicle  = args.vehicle or ''

    W = 68  # document width

    # Sort items: safety-critical first, then high, medium, low
    items_sorted = sorted(items, key=lambda x: URGENCY_ORDER.get(x.get('urgency','medium').lower(), 2))

    # Compute totals
    grand_total   = sum(float(i.get('part_cost', 0) or 0) + float(i.get('labor_cost', 0) or 0) for i in items)
    high_items    = [i for i in items if i.get('urgency','').lower() in ('safety-critical','high')]
    safety_items  = [i for i in items if i.get('urgency','').lower() == 'safety-critical']

    lines = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append("=" * W)
    lines.append("  YOUR REPAIR ESTIMATE — EXPLAINED IN PLAIN ENGLISH".center(W))
    lines.append(f"  Prepared by {shop}".center(W))
    lines.append("=" * W)
    info_parts = []
    if phone:   info_parts.append(phone)
    if website: info_parts.append(website)
    if info_parts:
        lines.append(f"  {' | '.join(info_parts)}".center(W))
    lines.append(f"  {today}".center(W))
    lines.append("=" * W)

    # ── Personalized intro ─────────────────────────────────────────────────────
    lines.append("")
    intro_vehicle = f" for your {vehicle}" if vehicle else ""
    lines.append(f"  Dear {customer},")
    lines.append("")
    intro = (
        f"Below is a plain-language explanation of each item on your estimate"
        f"{intro_vehicle}. We believe you deserve to understand every "
        "service we recommend — what it is, why it matters, and what to "
        "expect if it's deferred. We've grouped the most urgent items first. "
        "Questions? Please ask — we're here to help you make the right decision "
        "for your situation and your budget."
    )
    for chunk in _wrap(intro, W - 4):
        lines.append(f"  {chunk}")
    lines.append("")

    if safety_items:
        lines.append("  " + "━" * (W - 4))
        lines.append("  ⚠️  SAFETY NOTICE: One or more items on this estimate are")
        lines.append("  safety-critical. Please review those items first.")
        lines.append("  " + "━" * (W - 4))
        lines.append("")

    # ── Estimate overview ──────────────────────────────────────────────────────
    lines.append("  ESTIMATE OVERVIEW")
    lines.append("  " + "─" * (W - 4))
    lines.append(f"  {'#':<4} {'Item':<36} {'Urgency':<18} {'Total':>8}")
    lines.append("  " + "─" * (W - 4))
    for i, item in enumerate(items_sorted, 1):
        name      = item.get('part', f'Item {i}')
        kb        = find_kb_entry(name)
        disp_name = (kb['plain_name'] if kb else name)[:36]
        urg       = item.get('urgency', 'medium')
        total     = float(item.get('part_cost', 0) or 0) + float(item.get('labor_cost', 0) or 0)
        urg_short = {'safety-critical': '🚨 SAFETY-CRIT', 'high': '🔴 HIGH',
                     'medium': '🟡 MEDIUM', 'low': '🟢 LOW'}.get(urg.lower(), urg.upper())
        lines.append(f"  {i:<4} {disp_name:<36} {urg_short:<18} {format_currency(total):>8}")
    lines.append("  " + "─" * (W - 4))
    lines.append(f"  {'':4} {'ESTIMATE TOTAL':<36} {'':18} {format_currency(grand_total):>8}")
    lines.append("")

    # ── Detailed item explanations ─────────────────────────────────────────────
    lines.append("=" * W)
    lines.append("  DETAILED EXPLANATIONS".center(W))
    lines.append("=" * W)
    lines.append("")

    for i, item in enumerate(items_sorted):
        lines.extend(narrate_item(item, i, W))

    # ── "What if I wait?" section for high/safety items ───────────────────────
    if high_items:
        lines.append("=" * W)
        lines.append("  WHAT HAPPENS IF I WAIT?".center(W))
        lines.append("  Applies to items rated HIGH or SAFETY-CRITICAL".center(W))
        lines.append("=" * W)
        lines.append("")
        for item in high_items:
            part_name = item.get('part', 'This item')
            urgency   = item.get('urgency', 'high').lower()
            kb        = find_kb_entry(part_name)
            disp_name = kb['plain_name'] if kb else part_name
            consequence = ''
            if kb:
                consequence = kb['if_ignored'].get(urgency, kb['if_ignored'].get('high', ''))
            else:
                consequence = (
                    "Deferring this repair increases the risk of a more "
                    "expensive failure and may affect vehicle safety."
                )
            urg_label = URGENCY_LABELS.get(urgency, '')
            lines.append(f"  {disp_name.upper()}")
            lines.append(f"  {urg_label}")
            for chunk in _wrap(consequence, W - 4):
                lines.append(f"  {chunk}")
            lines.append("")

    # ── Grand total ───────────────────────────────────────────────────────────
    lines.append("=" * W)
    lines.append("  ESTIMATE TOTAL SUMMARY".center(W))
    lines.append("=" * W)
    lines.append("")
    for item in items_sorted:
        name  = item.get('part', 'Item')
        kb    = find_kb_entry(name)
        dname = (kb['plain_name'] if kb else name)
        total = float(item.get('part_cost', 0) or 0) + float(item.get('labor_cost', 0) or 0)
        lines.append(f"  {dname:<42}  {format_currency(total):>8}")
    lines.append("  " + "─" * (W - 4))
    lines.append(f"  {'TOTAL ESTIMATE':<42}  {format_currency(grand_total):>8}")
    lines.append("")
    lines.append("  * Prices shown include parts and labor. Tax not included.")
    lines.append("  * Final price may vary if additional issues are found during repair.")
    lines.append("")

    # ── Closing ───────────────────────────────────────────────────────────────
    lines.append("=" * W)
    closing = (
        "We know repair decisions aren't always easy. If you have questions "
        "about any item on this estimate — or want to talk through what to "
        "prioritize — please ask your service advisor. We're here to help "
        "you make the best decision for your vehicle and your budget. "
        "There's no pressure."
    )
    for chunk in _wrap(closing, W - 4):
        lines.append(f"  {chunk}")
    lines.append("")
    lines.append(f"  {shop}")
    if phone:
        lines.append(f"  {phone}")
    if tagline:
        lines.append(f'  "{tagline}"')
    lines.append("=" * W)

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Narrate a repair estimate in plain English")
    parser.add_argument('--customer', default='',  help="Customer name (optional, personalizes the letter)")
    parser.add_argument('--vehicle',  default='',  help="Year Make Model (optional)")
    parser.add_argument('--items',    required=True,
                        help="JSON array of line items. Each: {part, part_cost, labor_hours, labor_cost, urgency, notes}")
    parser.add_argument('--output',   default='narrated_estimate.txt', help="Output filename")
    args = parser.parse_args()

    profile = load_profile()
    doc     = build_document(profile, args)

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)
    filepath = os.path.join(os.path.abspath(OUTPUT_DIR), args.output)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(doc)

    print(doc)
    print(f"\n✅ Saved: output/estimates/{args.output}")


if __name__ == '__main__':
    main()
