#!/usr/bin/env python3
"""
Generate welcome kit components for new customers.

Usage:
    # Generate all 6 components at once
    python tools/welcome_kit/generate_kit.py \\
        --component all \\
        --discount "10% off your next service, max $50, valid 90 days" \\
        --referral_offer "$25 off for you and the friend you refer" \\
        --service_performed "oil change and tire rotation"

    # Generate individual components
    python tools/welcome_kit/generate_kit.py --component thank_you_letter \\
        --service_performed "brake pad replacement"
    python tools/welcome_kit/generate_kit.py --component shop_overview
    python tools/welcome_kit/generate_kit.py --component maintenance_guide
    python tools/welcome_kit/generate_kit.py --component new_customer_offer \\
        --discount "10% off next visit, max $50"
    python tools/welcome_kit/generate_kit.py --component referral_card \\
        --referral_offer "$25 off for both"
    python tools/welcome_kit/generate_kit.py --component welcome_email \\
        --discount "10% off" --referral_offer "$25 off for both"

Components: thank_you_letter  shop_overview  maintenance_guide
            new_customer_offer  referral_card  welcome_email  all
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

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'welcome_kit')

COMPONENT_ORDER = [
    "thank_you_letter",
    "shop_overview",
    "maintenance_guide",
    "new_customer_offer",
    "referral_card",
    "welcome_email",
]

# ---------------------------------------------------------------------------
# Profile helpers
# ---------------------------------------------------------------------------

def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def pval(profile, key, default='[Not Set]'):
    return profile.get(key) or default


def get_services_text(profile):
    services = profile.get('services', [])
    if services:
        if len(services) == 1:
            return services[0]
        return ', '.join(services[:-1]) + ', and ' + services[-1]
    return 'general automotive repair and maintenance'


def get_services_list(profile):
    services = profile.get('services', [])
    if services:
        return '\n'.join(f'  - {s}' for s in services)
    return '  - General automotive repair and maintenance'


# ---------------------------------------------------------------------------
# Template builders
# Each returns a complete, formatted string ready to save.
# ---------------------------------------------------------------------------

def build_thank_you_letter(profile, service_performed):
    shop_name   = pval(profile, 'shop_name',  'Your Auto Shop')
    owner_name  = pval(profile, 'owner_name', 'The Owner')
    phone       = pval(profile, 'phone',       '(555) 555-5555')
    address     = pval(profile, 'address') or pval(profile, 'location', '123 Main St')
    business_type = pval(profile, 'business_type', 'auto repair shop')

    service_line = (
        f"for your {service_performed} today"
        if service_performed
        else "for your recent service"
    )

    return f"""\
{shop_name.upper()}
WELCOME LETTER

Dear {{{{customer_name}}}},

Thank you for choosing {shop_name} {service_line}. We know you have plenty of \
options, and we genuinely appreciate that you gave us the opportunity to earn \
your trust.

I started {shop_name} because I believe every driver deserves straightforward, \
honest service from people who actually care about keeping them safe on the road. \
That's not a marketing line — it's how this shop operates, every day, for every \
vehicle that comes through our doors.

Here's what you can always count on from us:

  - Honest diagnostics: We tell you what your vehicle actually needs — \
not what generates the most revenue.
  - Plain-language explanations: We'll show you what we found and explain it \
in terms that make sense, not shop jargon.
  - No surprise charges: Every estimate is approved by you before we start work.
  - Quality that lasts: We use quality parts and stand behind our workmanship.

If you ever have a question about your vehicle between visits — even if it's just \
a noise you can't place — call us at {phone}. That's what we're here for.

Welcome to the {shop_name} family. We look forward to being your shop for years \
to come.

Sincerely,

{owner_name}
{shop_name}
{phone}
{address}
"""


def build_shop_overview(profile):
    shop_name     = pval(profile, 'shop_name',  'Your Auto Shop')
    owner_name    = pval(profile, 'owner_name', 'The Owner')
    phone         = pval(profile, 'phone',       '(555) 555-5555')
    address       = pval(profile, 'address') or pval(profile, 'location', '123 Main St')
    location      = pval(profile, 'location',    'the local area')
    website       = pval(profile, 'website',     'yourshop.com')
    hours         = pval(profile, 'hours',       'Call for hours')
    business_type = pval(profile, 'business_type', 'auto repair shop')
    tagline       = profile.get('tagline', '')
    services_text = get_services_text(profile)
    services_list = get_services_list(profile)

    tagline_line = f'\n"{tagline}"\n' if tagline else ''

    return f"""\
{shop_name.upper()}
ABOUT US
{tagline_line}
WHO WE ARE
{shop_name} is a locally owned and operated {business_type} serving {location} \
and the surrounding communities. We specialize in {services_text}. Every vehicle \
we work on gets the same attention we'd give our own — because our reputation \
depends on it.

WHAT MAKES US DIFFERENT
Chain shops run on volume. They move vehicles through as fast as possible, \
and the person checking you in is often a sales manager, not a mechanic. At \
{shop_name}, you deal with people who know cars. Our technicians diagnose the \
problem before recommending a fix, and we only recommend what your vehicle \
actually needs. If we find something that can wait, we'll tell you — and we'll \
tell you how long it can wait.

We've built this shop one customer at a time by doing the job right the first \
time and being straight with people. That's it. No gimmicks, no pressure, \
no upselling on services your vehicle doesn't need.

OUR SERVICES
{services_list}

HOURS & LOCATION
Hours:    {hours}
Address:  {address}
Phone:    {phone}
Website:  {website}

BOOK YOUR NEXT APPOINTMENT
Call us at {phone} or visit {website} to schedule online. We'll have you in \
and out as quickly as possible — and we'll always call before doing any work \
beyond what was originally discussed.

{shop_name} — serving {location} with honest automotive service.
"""


def build_maintenance_guide(profile):
    shop_name = pval(profile, 'shop_name',  'Your Auto Shop')
    phone     = pval(profile, 'phone',       '(555) 555-5555')
    address   = pval(profile, 'address') or pval(profile, 'location', '123 Main St')

    return f"""\
{shop_name.upper()}
VEHICLE MAINTENANCE SCHEDULE

Regular maintenance is the single most effective way to avoid unexpected \
breakdowns and keep repair costs manageable. The intervals below follow general \
industry guidelines — your specific vehicle's owner manual may vary, and we're \
always happy to pull up the manufacturer schedule for your year, make, and model \
at no charge.

────────────────────────────────────────────────────────────────
EVERY 3,000–5,000 MILES  |  or every 3–6 months
────────────────────────────────────────────────────────────────
  - Engine oil and filter change
  - Tire pressure check and adjustment
  - Tire rotation (extends tire life by 20–30%)
  - Fluid level top-off check: coolant, brake fluid, power steering, washer fluid
  - Visual inspection: lights, wipers, belts, hoses

────────────────────────────────────────────────────────────────
EVERY 15,000–30,000 MILES  |  or annually
────────────────────────────────────────────────────────────────
  - Engine air filter replacement
  - Cabin air filter replacement (affects A/C and heat performance)
  - Brake pad and rotor inspection
  - Battery load test and terminal cleaning
  - Tire alignment check
  - Full multi-point inspection

────────────────────────────────────────────────────────────────
EVERY 30,000–60,000 MILES  |  or every 2–3 years
────────────────────────────────────────────────────────────────
  - Transmission fluid service
  - Coolant system flush
  - Spark plug inspection and replacement
  - Drive belt inspection (serpentine, timing)
  - Power steering fluid flush
  - Fuel system cleaning and injector service

────────────────────────────────────────────────────────────────
EVERY 60,000–100,000 MILES
────────────────────────────────────────────────────────────────
  - Timing belt/chain inspection (critical — failure causes major engine damage)
  - Complete brake system inspection and fluid flush
  - Suspension component inspection: shocks, struts, ball joints, tie rod ends
  - Differential fluid service (4WD/AWD vehicles)
  - Coolant system pressure test
  - Full major-service inspection

────────────────────────────────────────────────────────────────
SEASONAL REMINDERS
────────────────────────────────────────────────────────────────
  Spring:  A/C system check, wiper blades, tire condition after winter
  Summer:  Cooling system, battery test (heat degrades batteries faster)
  Fall:    Heater/defroster, tire tread depth, all exterior lights
  Winter:  Battery cold-cranking amps, antifreeze concentration, \
tire pressure (drops ~1 psi per 10°F)

────────────────────────────────────────────────────────────────
NOT SURE WHAT YOUR VEHICLE NEEDS?
────────────────────────────────────────────────────────────────
Call {shop_name} at {phone} and give us your year, make, model, and current \
mileage. We'll tell you exactly what's coming up on the manufacturer's schedule \
— no appointment needed, no charge.

{shop_name}  |  {phone}  |  {address}
"""


def build_new_customer_offer(profile, discount):
    shop_name = pval(profile, 'shop_name',  'Your Auto Shop')
    phone     = pval(profile, 'phone',       '(555) 555-5555')
    website   = pval(profile, 'website',     'yourshop.com')
    address   = pval(profile, 'address') or pval(profile, 'location', '123 Main St')

    return f"""\
{shop_name.upper()}
NEW CUSTOMER OFFER

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{discount}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for choosing {shop_name}. This offer is our way of saying we \
appreciate you giving us the chance to earn your trust — and we look forward \
to taking care of your vehicle for years to come.

HOW TO REDEEM
  1. Call {phone} or visit {website} to book your next appointment.
  2. Mention this offer when you schedule — we'll add it to your file.
  3. That's it. No coupon to print. No code to remember.

TERMS & CONDITIONS
  - Valid for new customers on their second visit only.
  - One offer per customer. Not transferable.
  - Cannot be combined with other discounts or promotions.
  - Valid at {shop_name} ({address}) only.
  - Expires 90 days from your first visit date.

Questions? Call us at {phone} — we're happy to help.

{shop_name}
{phone}  |  {address}  |  {website}
"""


def build_referral_card(profile, referral_offer):
    shop_name = pval(profile, 'shop_name',  'Your Auto Shop')
    phone     = pval(profile, 'phone',       '(555) 555-5555')
    website   = pval(profile, 'website',     'yourshop.com')
    address   = pval(profile, 'address') or pval(profile, 'location', '123 Main St')

    return f"""\
{shop_name.upper()}
REFER A FRIEND — GET REWARDED

Know someone who needs a mechanic they can actually trust? Send them to \
{shop_name} and you'll both benefit.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE OFFER:  {referral_offer}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW IT WORKS
  Step 1:  Tell your friend about {shop_name}.
  Step 2:  Have them mention YOUR NAME when they book their first appointment.
  Step 3:  After their first service is complete, you BOTH receive your reward.
  Step 4:  Repeat — there is no limit to how many friends you can refer.

YOUR REFERRAL INFORMATION
  Your Name: {{{{customer_name}}}}

  When your friend books, they should say:
  "I was referred by {{{{customer_name}}}}."

TO BOOK AN APPOINTMENT
  Call:     {phone}
  Online:   {website}
  Address:  {address}

QUESTIONS?
Call us at {phone} and ask for {shop_name}'s referral program — we'll look \
up your account and confirm everything is on file.

{shop_name}  |  {phone}  |  {address}
"""


def build_welcome_email(profile, discount, referral_offer, service_performed):
    shop_name     = pval(profile, 'shop_name',  'Your Auto Shop')
    owner_name    = pval(profile, 'owner_name', 'The Owner')
    phone         = pval(profile, 'phone',       '(555) 555-5555')
    address       = pval(profile, 'address') or pval(profile, 'location', '123 Main St')
    location      = pval(profile, 'location',    'the local area')
    website       = pval(profile, 'website',     'yourshop.com')
    business_type = pval(profile, 'business_type', 'auto repair shop')
    services_text = get_services_text(profile)

    service_line = (
        f"for your {service_performed}"
        if service_performed
        else "for your recent service visit"
    )

    return f"""\
Subject: Welcome to {shop_name}, {{{{customer_name}}}}! Here's Your New Customer Package

Hi {{{{customer_name}}}},

Thank you for choosing {shop_name} {service_line}. We're glad you found us, \
and we want to make sure you have everything you need to get the most out of \
your vehicle — and out of your relationship with our shop.

───────────────────────────────────────
ABOUT {shop_name.upper()}
───────────────────────────────────────
We're a locally owned {business_type} serving {location}. We specialize in \
{services_text}. Unlike chain shops, every vehicle gets hands-on attention from \
experienced technicians, and we only recommend work your vehicle actually needs. \
No upselling. No surprises. Just honest service.

Phone:    {phone}
Address:  {address}
Website:  {website}

───────────────────────────────────────
YOUR MAINTENANCE QUICK GUIDE
───────────────────────────────────────
Staying on schedule is the best way to keep repair costs low:

  Every 3,000–5,000 mi:   Oil change, tire rotation, fluid check
  Every 15,000–30,000 mi: Air filters, brake inspection, battery test
  Every 30,000–60,000 mi: Transmission service, coolant flush, spark plugs
  Every 60,000–100,000 mi: Timing belt, full brake overhaul, suspension inspection

Not sure what's due? Call us at {phone} with your mileage and we'll check \
the manufacturer schedule for free.

───────────────────────────────────────
YOUR NEW CUSTOMER OFFER
───────────────────────────────────────
{discount}

Valid for 90 days. Mention it when you book — no coupon needed.

───────────────────────────────────────
REFERRAL PROGRAM
───────────────────────────────────────
{referral_offer}

Just have your friend mention your name when they book. There's no limit on \
referrals — every one earns you both a reward.

───────────────────────────────────────
STAY IN TOUCH
───────────────────────────────────────
We'll send you reminders when maintenance is coming up and check in after \
each visit. If you ever have a question about your vehicle between visits, \
don't hesitate to call or email — we're here to help.

Thank you again, {{{{customer_name}}}}. We look forward to being your shop.

{owner_name}
{shop_name}
{phone}  |  {website}
{address}
"""


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

COMPONENT_ORDER = [
    "thank_you_letter",
    "shop_overview",
    "maintenance_guide",
    "new_customer_offer",
    "referral_card",
    "welcome_email",
]


def build_component(name, profile, discount, referral_offer, service_performed):
    if name == "thank_you_letter":
        return build_thank_you_letter(profile, service_performed)
    elif name == "shop_overview":
        return build_shop_overview(profile)
    elif name == "maintenance_guide":
        return build_maintenance_guide(profile)
    elif name == "new_customer_offer":
        return build_new_customer_offer(profile, discount)
    elif name == "referral_card":
        return build_referral_card(profile, referral_offer)
    elif name == "welcome_email":
        return build_welcome_email(profile, discount, referral_offer, service_performed)
    else:
        return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate welcome kit components for new customers."
    )
    parser.add_argument(
        '--component',
        required=True,
        choices=COMPONENT_ORDER + ['all'],
        help="Which component to generate, or 'all' for the complete kit."
    )
    parser.add_argument(
        '--discount',
        default="10% off your next service visit — up to $50 in savings. Valid for 90 days.",
        help="New customer discount offer text."
    )
    parser.add_argument(
        '--referral_offer',
        default="$25 off your next service for you, and $25 off for the friend you refer.",
        help="Referral program offer text."
    )
    parser.add_argument(
        '--service_performed',
        default='',
        help="Service from the first visit — used to personalize the thank-you letter."
    )
    args = parser.parse_args()

    profile = load_profile()
    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)
    output_dir = os.path.abspath(OUTPUT_DIR)

    components = COMPONENT_ORDER if args.component == 'all' else [args.component]

    print(f"\n🔧 Generating welcome kit components")
    print(f"   Shop         : {pval(profile, 'shop_name', '[Not Set]')}")
    print(f"   Discount     : {args.discount}")
    print(f"   Referral     : {args.referral_offer}")
    if args.service_performed:
        print(f"   Service      : {args.service_performed}")
    print()

    generated = []
    for name in components:
        content = build_component(
            name, profile, args.discount, args.referral_offer, args.service_performed
        )
        if content is None:
            print(f"  ⚠️  Unknown component: {name}", file=sys.stderr)
            continue

        filename  = f"{name}.txt"
        filepath  = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(content)

        word_count = len(content.split())
        print(f"  ✅ output/welcome_kit/{filename}  ({word_count} words)")
        generated.append(filename)

    print(f"\n{'─'*50}")
    print(f"✅ Done — {len(generated)} component(s) saved to output/welcome_kit/")
    if args.component == 'all':
        print("   Print: thank_you_letter, shop_overview, maintenance_guide, "
              "new_customer_offer, referral_card")
        print("   Email: welcome_email (ready to send)")


if __name__ == '__main__':
    main()
