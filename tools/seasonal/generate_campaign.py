#!/usr/bin/env python3
"""
Generate seasonal marketing campaigns for auto repair shops.

Produces SMS blast, email campaign, social media post, and staff briefing
using the shop's real name, phone, website, and contact details.

Usage:
    python tools/seasonal/generate_campaign.py --season winter --discount "Free battery test" --expiry "Nov 30"
    python tools/seasonal/generate_campaign.py --season spring --discount "10% off AC" --expiry "April 30"
    python tools/seasonal/generate_campaign.py --season summer
    python tools/seasonal/generate_campaign.py --season fall --discount "$20 off tire rotation"
    python tools/seasonal/generate_campaign.py --season holiday --discount "Free inspection with oil change"
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
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'seasonal')

SMS_LIMIT = 160


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if not os.path.exists(path):
        print("ERROR: shop_profile.json not found.", file=sys.stderr)
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ── Campaign Content Library ──────────────────────────────────────────────────

CAMPAIGNS = {
    "winter": {
        "name": "Winter Ready",
        "hook": "Cold weather is coming — let's make sure your car is too.",
        "services": [
            "Battery test (cold weakens batteries by up to 50%)",
            "Coolant/antifreeze check and freeze-point test",
            "Heater and defroster inspection",
            "Tire tread depth and pressure check",
            "Wiper blade inspection and replacement",
        ],
        "upsell_tip": "Winter is the best time to upsell battery replacements, wiper blades, and coolant flushes.",
        "sms_template": (
            "Winter's coming. Is your car ready? {shop} is doing "
            "battery, coolant & tire checks{offer_fragment}. "
            "Book now: {phone}"
        ),
        "email_subject": "Is Your Car Ready for Winter? — {shop}",
        "email_body": (
            "Hi there,\n\n"
            "Cold weather puts extra stress on your vehicle — and the last thing you want "
            "is a breakdown on a freezing morning.\n\n"
            "Before temperatures drop, we recommend checking:\n\n"
            "  Battery — Cold air can cut battery capacity in half. A weak battery won't "
            "make it through winter.\n"
            "  Coolant / Antifreeze — Needs to be at the right concentration to prevent "
            "freezing in your engine.\n"
            "  Heater & Defroster — Don't find out they're broken on the coldest day of the year.\n"
            "  Tires — Worn tread on wet or icy roads means longer stopping distances.\n"
            "  Wiper Blades — Cracked blades can't clear snow and ice when you need them most.\n"
            "{offer_section}"
            "Call us at {phone} or book online at {website}.\n\n"
            "Stay warm and drive safe,\n"
            "{owner}\n"
            "{shop}\n"
            "{phone}"
        ),
        "social_template": (
            "Winter is harder on your car than you think. Battery, coolant, tires, "
            "heater — we check it all.{offer_line} "
            "Call {phone} to schedule your winter checkup. — {shop}"
        ),
        "staff_services": "battery, coolant flush, wiper blades, heater core inspection, tire rotation",
    },

    "spring": {
        "name": "Spring Checkup",
        "hook": "Winter was tough on your car. Spring is the perfect time to undo the damage.",
        "services": [
            "AC system test and recharge check",
            "Wheel alignment (potholes cause drift)",
            "Brake inspection",
            "Fluid level and condition check",
            "Air filter and cabin filter replacement",
        ],
        "upsell_tip": "Alignment is a high-margin service and a natural upsell after pothole season.",
        "sms_template": (
            "Spring checkup time at {shop}! AC test, alignment, brakes & fluids. "
            "{offer_fragment}Call {phone} to book."
        ),
        "email_subject": "Spring Vehicle Checkup — {shop}",
        "email_body": (
            "Hi there,\n\n"
            "Winter takes a toll — salt, potholes, and cold air stress every major system "
            "in your vehicle.\n\n"
            "Spring is the right time to:\n\n"
            "  AC System — Test it before summer heat arrives. A recharge now beats "
            "a breakdown in July.\n"
            "  Wheel Alignment — Pothole season sends cars out of alignment. Misaligned "
            "wheels wear tires unevenly and cost you money.\n"
            "  Brakes — Salt and moisture accelerate brake wear. Get them checked.\n"
            "  Fluids — Brake fluid, power steering, coolant — all deserve a look after winter.\n"
            "  Filters — Air and cabin filters trap a winter's worth of salt, dirt, and debris.\n"
            "{offer_section}"
            "Ready to schedule? Call {phone} or visit {website}.\n\n"
            "Here's to a smoother spring,\n"
            "{owner}\n"
            "{shop}\n"
            "{phone}"
        ),
        "social_template": (
            "Potholes, salt, and cold air — winter isn't kind to your car. "
            "Spring checkup at {shop}: AC, alignment, brakes, and fluids.{offer_line} "
            "Call {phone}."
        ),
        "staff_services": "alignment, AC inspection, brake inspection, fluid flush, cabin air filter",
    },

    "summer": {
        "name": "Summer Road Trip Ready",
        "hook": "Before you hit the road this summer, let's make sure your car can handle it.",
        "services": [
            "AC service and refrigerant check",
            "Cooling system and radiator inspection",
            "Tire pressure check and rotation",
            "Belt and hose inspection (heat accelerates wear)",
            "Full safety inspection for road trips",
        ],
        "upsell_tip": "Road trip packages bundle multiple services and offer great value to customers planning summer travel.",
        "sms_template": (
            "Road trip season! {shop} is doing summer safety checks — AC, coolant, tires & more. "
            "{offer_fragment}Call {phone}."
        ),
        "email_subject": "Road Trip Ready? Let's Make Sure — {shop}",
        "email_body": (
            "Hi there,\n\n"
            "Summer means road trips, longer commutes, and hot roads. Your car works harder "
            "when it's hot — and it pays to be prepared.\n\n"
            "Our summer checkup covers:\n\n"
            "  AC System — Blowing cold? We'll check the refrigerant charge and test the "
            "whole system so you're not suffering in July.\n"
            "  Cooling System — Overheating is the #1 cause of summer breakdowns. "
            "We inspect the radiator, coolant level, and water pump.\n"
            "  Tires — Hot pavement on under-inflated or worn tires increases blowout risk. "
            "We check pressure and tread depth.\n"
            "  Belts & Hoses — Heat accelerates rubber deterioration. A snapped belt "
            "on the highway ruins a road trip fast.\n"
            "  Safety Inspection — Lights, brakes, wipers — everything you need for confident driving.\n"
            "{offer_section}"
            "Book your summer checkup: {phone} or {website}.\n\n"
            "Happy travels,\n"
            "{owner}\n"
            "{shop}\n"
            "{phone}"
        ),
        "social_template": (
            "Summer road trip season is here. Don't let a breakdown ruin it. "
            "AC, coolant, tires, belts — summer checkup at {shop}.{offer_line} "
            "Book now: {phone}"
        ),
        "staff_services": "AC service, cooling system flush, tire rotation, belt inspection, full safety check",
    },

    "fall": {
        "name": "Fall Safety Check",
        "hook": "Shorter days and wet roads mean your safety systems need to be in top shape.",
        "services": [
            "Brake inspection (wet leaves increase stopping distance)",
            "Tire tread and pressure check before rain season",
            "Lights and bulb check (days get shorter)",
            "Battery test before cold weather",
            "Windshield wiper inspection",
        ],
        "upsell_tip": "Fall is ideal for tire swap appointments (summer to all-season/winter tires) and battery replacement before winter stress.",
        "sms_template": (
            "Fall safety check at {shop}! Brakes, tires, lights & battery — "
            "before the cold hits.{offer_fragment} Call {phone}."
        ),
        "email_subject": "Fall Vehicle Safety Check — {shop}",
        "email_body": (
            "Hi there,\n\n"
            "As the days get shorter and temperatures start to drop, your vehicle needs "
            "to be ready for what's coming.\n\n"
            "Our fall safety check covers:\n\n"
            "  Brakes — Wet leaves and rain extend stopping distances. "
            "If your brakes are worn, fall is when it shows.\n"
            "  Tires — Check tread depth before rain season. Worn tires on wet roads "
            "are a serious safety risk.\n"
            "  Lights — With sunset coming earlier, all your lights need to be working. "
            "We check headlights, taillights, turn signals, and brake lights.\n"
            "  Battery — Cold weather is coming. Better to know now if your battery "
            "is weak than to find out on a cold morning.\n"
            "  Wipers — Ready for fall rain? Streaking wipers cut visibility fast.\n"
            "{offer_section}"
            "Schedule your fall safety check: {phone} or {website}.\n\n"
            "Drive safe this season,\n"
            "{owner}\n"
            "{shop}\n"
            "{phone}"
        ),
        "social_template": (
            "Shorter days, rain, early frost — your car needs to be ready. "
            "Fall safety check at {shop}: brakes, tires, lights & battery.{offer_line} "
            "Call {phone}."
        ),
        "staff_services": "brake inspection, tire rotation, light check, battery test, wiper replacement",
    },

    "holiday": {
        "name": "Holiday Travel Safety",
        "hook": "Don't let a breakdown ruin your holidays. A quick vehicle check can prevent it.",
        "services": [
            "Full multi-point safety inspection",
            "Oil change if due",
            "Tire pressure check (drops in cold weather)",
            "All fluid top-offs",
            "Battery and charging system test",
        ],
        "upsell_tip": "Holiday campaigns are time-sensitive. Emphasize the booking deadline — spots fill up before holiday closures.",
        "sms_template": (
            "Holiday travel coming up? {shop} offers a quick pre-trip safety check. "
            "{offer_fragment}Book before we fill up: {phone}."
        ),
        "email_subject": "Holiday Travel Safety Checklist — {shop}",
        "email_body": (
            "Hi there,\n\n"
            "The holidays are coming — and for many of us, that means long drives to see family.\n\n"
            "A breakdown far from home during the holidays is stressful, expensive, and avoidable. "
            "A quick pre-trip check covers the basics:\n\n"
            "  Oil & Filter — If you're due, do it before you go. Long highway miles on "
            "old oil adds wear.\n"
            "  Tire Pressure — Cold weather drops tire pressure. Properly inflated tires "
            "get better fuel economy and handle better.\n"
            "  Fluids — Coolant, brake fluid, power steering, washer fluid — all topped off.\n"
            "  Battery — Cold weather reduces battery output. A weak battery might start "
            "fine at home but struggle in colder climates.\n"
            "  Brakes — If you've noticed any noise or softness, have them looked at before the trip.\n"
            "{offer_section}"
            "Spots are limited before the holiday rush — book now: {phone} or {website}.\n\n"
            "Safe travels and happy holidays,\n"
            "{owner}\n"
            "{shop}\n"
            "{phone}"
        ),
        "social_template": (
            "Holiday road trip coming up? Don't let your car be the reason you're late. "
            "Quick pre-holiday safety check at {shop}.{offer_line} "
            "Book before we fill up: {phone}."
        ),
        "staff_services": "oil change, tire pressure, fluid top-off, battery test, full safety inspection",
    },
}


def build_offer_fragments(discount, expiry):
    """Return the offer text variations for different channels."""
    if not discount:
        return {
            'offer_fragment': '',
            'offer_section': '',
            'offer_line': '',
            'offer_display': None,
        }

    expiry_str = f" Expires {expiry}." if expiry else ""
    offer_display = discount
    if expiry:
        offer_display += f" (Expires {expiry})"

    return {
        'offer_fragment': f"{discount}. ",
        'offer_section': f"\nThis month's offer: {discount}{expiry_str}\n\n",
        'offer_line': f" Special offer: {discount}.",
        'offer_display': offer_display,
    }


def trim_sms(text, limit=SMS_LIMIT):
    """Trim SMS text to fit within character limit."""
    if len(text) <= limit:
        return text, True
    # Try trimming trailing sentence
    trimmed = text[:limit - 3].rsplit(' ', 1)[0] + '...'
    return trimmed, False


def main():
    parser = argparse.ArgumentParser(description="Generate seasonal marketing campaign")
    parser.add_argument('--season', required=True,
                        choices=list(CAMPAIGNS.keys()),
                        help="Season: winter, spring, summer, fall, holiday")
    parser.add_argument('--campaign_type', default='',
                        help="Optional custom campaign name/subtitle")
    parser.add_argument('--discount', default='',
                        help="Special offer text, e.g. 'Free battery test with any service'")
    parser.add_argument('--expiry', default='',
                        help="Offer expiration, e.g. 'November 30'")
    args = parser.parse_args()

    profile = load_profile()
    shop = profile.get('shop_name') or '[Shop Name]'
    phone = profile.get('phone') or '[Phone]'
    website = profile.get('website') or '[Website]'
    owner = profile.get('owner_name') or f"The Team at {shop}"
    review_link = (profile.get('review_links') or {}).get('google', '')

    campaign = CAMPAIGNS[args.season]
    campaign_name = args.campaign_type or campaign['name']
    offers = build_offer_fragments(args.discount, args.expiry)

    # Expiry date sanity check
    if args.expiry:
        try:
            expiry_year = datetime.now().year
            check = datetime.strptime(f"{args.expiry} {expiry_year}", "%B %d %Y")
            if check.date() < datetime.now().date():
                print(f"WARNING: Offer expiry '{args.expiry}' appears to be in the past. "
                      f"Verify the date.", file=sys.stderr)
        except ValueError:
            pass  # expiry in non-standard format, skip check

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)
    generated = []

    # ── SMS ────────────────────────────────────────────────────────────────────
    sms_raw = campaign['sms_template'].format(
        shop=shop,
        phone=phone,
        offer_fragment=offers['offer_fragment']
    )
    sms_text, sms_fits = trim_sms(sms_raw)
    sms_note = f"  ({len(sms_text)}/160 chars)" + ("" if sms_fits else " [trimmed to fit]")

    sms_file = os.path.join(os.path.abspath(OUTPUT_DIR), f"{args.season}_sms.txt")
    with open(sms_file, 'w', encoding='utf-8') as f:
        f.write(f"SMS BLAST — {campaign_name.upper()}\n")
        f.write("=" * 55 + "\n")
        f.write(sms_text + "\n")
        f.write(f"\n{sms_note}\n")
        if args.expiry:
            f.write(f"Offer expires: {args.expiry}\n")
    generated.append(('SMS', f"output/seasonal/{args.season}_sms.txt"))

    # ── EMAIL ──────────────────────────────────────────────────────────────────
    subject = campaign['email_subject'].format(shop=shop)
    body = campaign['email_body'].format(
        shop=shop,
        phone=phone,
        website=website,
        owner=owner,
        offer_section=offers['offer_section']
    )

    email_content = (
        f"EMAIL — {campaign_name.upper()}\n"
        f"{'=' * 55}\n"
        f"SUBJECT: {subject}\n"
        f"{'─' * 55}\n\n"
        f"{body}\n"
    )
    if review_link:
        email_content += (
            f"\n[P.S. — Happy with our service? Leave us a review: {review_link}]\n"
        )

    email_file = os.path.join(os.path.abspath(OUTPUT_DIR), f"{args.season}_email.txt")
    with open(email_file, 'w', encoding='utf-8') as f:
        f.write(email_content)
    generated.append(('Email', f"output/seasonal/{args.season}_email.txt"))

    # ── SOCIAL MEDIA ───────────────────────────────────────────────────────────
    social_text = campaign['social_template'].format(
        shop=shop,
        phone=phone,
        offer_line=offers['offer_line']
    )
    social_char_note = f"({len(social_text)} chars)"

    social_file = os.path.join(os.path.abspath(OUTPUT_DIR), f"{args.season}_social.txt")
    with open(social_file, 'w', encoding='utf-8') as f:
        f.write(f"SOCIAL MEDIA CAPTION — {campaign_name.upper()}\n")
        f.write("=" * 55 + "\n")
        f.write("FOR: Facebook / Instagram\n")
        f.write("─" * 55 + "\n\n")
        f.write(social_text + "\n\n")
        f.write(f"{social_char_note}\n")
        f.write("\nHASHTAG SUGGESTIONS:\n")
        f.write(f"#AutoRepair #CarCare #{args.season.capitalize()}Driving "
                f"#VehicleSafety #{shop.replace(' ', '')}\n")
    generated.append(('Social', f"output/seasonal/{args.season}_social.txt"))

    # ── STAFF BRIEFING ─────────────────────────────────────────────────────────
    today_str = datetime.now().strftime('%B %d, %Y')
    services_list = '\n'.join(f"    - {s}" for s in campaign['services'])

    briefing = (
        f"STAFF BRIEFING — {campaign_name.upper()}\n"
        f"{'=' * 55}\n"
        f"INTERNAL USE ONLY — Do not send to customers\n"
        f"{'─' * 55}\n\n"
        f"Campaign: {campaign_name}\n"
        f"Prepared: {today_str}\n"
        f"Shop: {shop}\n\n"
        f"CAMPAIGN HOOK:\n"
        f"  \"{campaign['hook']}\"\n\n"
        f"KEY SERVICES TO PROMOTE:\n"
        f"{services_list}\n\n"
        f"UPSELL TIP:\n"
        f"  {campaign['upsell_tip']}\n\n"
        f"FRONT DESK TALKING POINTS:\n"
        f"  - When customers call to book, mention the {args.season} campaign.\n"
        f"  - Ask: \"Have you had your {campaign['staff_services'].split(',')[0].strip()} "
        f"checked recently?\"\n"
        f"  - Suggest a multi-point inspection for customers coming in for single services.\n"
    )

    if args.discount:
        briefing += (
            f"\nCURRENT OFFER:\n"
            f"  {offers['offer_display']}\n"
            f"  Make sure every customer is informed of this offer.\n"
        )
        if args.expiry:
            briefing += f"  EXPIRES: {args.expiry} — push bookings before then.\n"

    briefing += (
        f"\nCHANNELS DEPLOYED:\n"
        f"  - SMS blast (copy in output/seasonal/{args.season}_sms.txt)\n"
        f"  - Email campaign (copy in output/seasonal/{args.season}_email.txt)\n"
        f"  - Social media post (copy in output/seasonal/{args.season}_social.txt)\n\n"
        f"{'=' * 55}\n"
    )

    briefing_file = os.path.join(os.path.abspath(OUTPUT_DIR), f"{args.season}_staff_briefing.txt")
    with open(briefing_file, 'w', encoding='utf-8') as f:
        f.write(briefing)
    generated.append(('Staff Briefing', f"output/seasonal/{args.season}_staff_briefing.txt"))

    # ── Summary Output ─────────────────────────────────────────────────────────
    print(f"\n{'=' * 58}")
    print(f"  CAMPAIGN GENERATED: {campaign_name.upper()}")
    print(f"  Season: {args.season.capitalize()} | Shop: {shop}")
    if args.discount:
        print(f"  Offer: {args.discount}")
    if args.expiry:
        print(f"  Expires: {args.expiry}")
    print(f"{'─' * 58}")
    for label, path in generated:
        print(f"  {label:<20} → {path}")
    print(f"{'─' * 58}")
    print(f"\n  SMS PREVIEW  {sms_note}")
    print(f"  {'─' * 50}")
    print(f"  {sms_text}")
    print(f"\n{'=' * 58}\n")


if __name__ == '__main__':
    main()
