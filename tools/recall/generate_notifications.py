#!/usr/bin/env python3
"""
Generate customer recall notifications — Module 8: Recall Notifications
Shop Command Center

Produces four ready-to-use outputs for each recall:
  1. SMS alert (under 160 characters)
  2. Email (full explanation, subject line, call-to-action)
  3. Phone script (structured call guide for service advisor)
  4. Shop note (internal file record)

Usage:
  python tools/recall/generate_notifications.py \\
      --customer "Sarah Mitchell" \\
      --vehicle "2019 Toyota Camry" \\
      --recall_campaign "19V123000" \\
      --component "Fuel Pump" \\
      --description "The fuel pump may crack, causing the engine to stall or fail to start." \\
      --consequence "An engine stall while driving increases the risk of a crash." \\
      --remedy "Toyota will replace the fuel pump at no charge to the owner." \\
      --urgency high

Urgency levels: low | medium | high
  low    — Not immediately dangerous. Schedule when convenient.
  medium — Should be addressed soon. (default)
  high   — Safety-critical. Customer should minimize driving until repaired.
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
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'recall')


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


URGENCY_LABELS = {
    'low':    'Informational — no immediate safety risk',
    'medium': 'Safety Concern — schedule soon',
    'high':   'SAFETY CRITICAL — please address immediately',
}

URGENCY_SMS_PREFIX = {
    'low':    'RECALL NOTICE',
    'medium': 'SAFETY RECALL',
    'high':   'URGENT SAFETY RECALL',
}

URGENCY_EMAIL_OPENING = {
    'low': (
        "We're reaching out with an important update about your vehicle. "
        "The National Highway Traffic Safety Administration (NHTSA) has issued a recall "
        "that applies to your {vehicle}."
    ),
    'medium': (
        "We're contacting you about a safety recall that applies to your {vehicle}. "
        "NHTSA has issued a recall notice and we want to make sure you have all the information "
        "you need to keep your vehicle safe."
    ),
    'high': (
        "We're reaching out urgently about a safety recall affecting your {vehicle}. "
        "The National Highway Traffic Safety Administration (NHTSA) has issued a SAFETY-CRITICAL "
        "recall, and we strongly recommend you address this as soon as possible."
    ),
}

URGENCY_EMAIL_ACTION = {
    'low': (
        "We recommend scheduling an appointment at your convenience so we can inspect your vehicle "
        "and arrange the recall repair. This is not an emergency, but it should be addressed."
    ),
    'medium': (
        "We recommend scheduling an appointment soon so we can inspect your vehicle and coordinate "
        "the recall repair. Most recall work is scheduled within 1–2 weeks."
    ),
    'high': (
        "We strongly recommend you minimize driving your vehicle until this recall is addressed. "
        "Please contact us as soon as possible to schedule an inspection and repair. "
        "We will prioritize your appointment."
    ),
}


def build_sms(args, profile):
    """Under 160 characters. Tight and actionable."""
    shop  = profile.get('shop_name', 'Your Shop')
    phone = profile.get('phone', '')
    prefix = URGENCY_SMS_PREFIX.get(args.urgency, 'SAFETY RECALL')

    # Try the full version first, then trim if needed
    full = (
        f"{prefix}: Your {args.vehicle} has an open recall "
        f"(#{args.recall_campaign}) — {args.component}. "
        f"Repair is FREE. Call {shop}: {phone}"
    )
    if len(full) <= 160:
        return full

    # Trimmed version
    trimmed = (
        f"{prefix}: Your {args.vehicle} has recall #{args.recall_campaign}. "
        f"Repair FREE. Call {phone}"
    )
    if len(trimmed) > 160:
        trimmed = trimmed[:157] + "..."
    return trimmed


def build_email(args, profile):
    """Full professional email with subject line."""
    shop       = profile.get('shop_name', 'Your Shop')
    phone      = profile.get('phone', '')
    owner      = profile.get('owner_name', 'Your Service Team')
    website    = profile.get('website', '')
    today      = datetime.now().strftime('%B %d, %Y')
    customer   = args.customer

    urgency_label = URGENCY_LABELS.get(args.urgency, URGENCY_LABELS['medium'])

    opening = URGENCY_EMAIL_OPENING.get(args.urgency, URGENCY_EMAIL_OPENING['medium'])
    opening = opening.format(vehicle=args.vehicle)

    action = URGENCY_EMAIL_ACTION.get(args.urgency, URGENCY_EMAIL_ACTION['medium'])

    if args.urgency == 'high':
        subject = f"URGENT Safety Recall — Your {args.vehicle} | {shop}"
    elif args.urgency == 'low':
        subject = f"Recall Notice for Your {args.vehicle} | {shop}"
    else:
        subject = f"Safety Recall Notice — Your {args.vehicle} | {shop}"

    website_line = f"\nWebsite: {website}" if website else ""

    email = f"""Subject: {subject}

Dear {customer},

{opening}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECALL DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Vehicle:          {args.vehicle}
NHTSA Campaign #: {args.recall_campaign}
Component:        {args.component}
Priority:         {urgency_label}

WHAT IS THE ISSUE?
{args.description}

WHY DOES IT MATTER?
{args.consequence}

WHAT WILL BE DONE?
{args.remedy}

COST TO YOU: This recall repair is performed at NO CHARGE to the vehicle owner.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT SHOULD YOU DO?
{action}

To schedule your appointment, contact us:

  {shop}
  Phone: {phone}{website_line}

Our team is ready to help you get this taken care of quickly and at no cost to you.

You can also verify this recall at the official NHTSA website:
  https://www.nhtsa.gov/recalls (search by VIN or year/make/model)

Your safety is our top priority.

Sincerely,

{owner}
{shop}
{phone}

───────────────────────────────────
This notice was sent on {today} by {shop}.
We are notifying customers whose vehicles are affected by NHTSA recall {args.recall_campaign}.
───────────────────────────────────"""

    return email


def build_phone_script(args, profile):
    """Structured phone call script for the service advisor."""
    shop    = profile.get('shop_name', 'Your Shop')
    phone   = profile.get('phone', '')
    customer = args.customer

    urgency_note = ""
    if args.urgency == 'high':
        urgency_note = (
            "\n[URGENCY NOTE] This is a safety-critical recall. "
            "Emphasize that we recommend the customer limit driving until the repair is made. "
            "Offer the earliest available appointment."
        )

    script = f"""════════════════════════════════════════════════════
PHONE SCRIPT — RECALL NOTIFICATION CALL
{shop}
Campaign #: {args.recall_campaign} | Vehicle: {args.vehicle}
════════════════════════════════════════════════════
{urgency_note}

[OPENING]
"Hi, may I speak with {customer}?
... Hi {customer}, this is [YOUR NAME] calling from {shop}.
Do you have just two minutes? I'm calling about an important
safety matter regarding your {args.vehicle}."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[IF THEY SAY YES — CONTINUE]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[EXPLAIN THE RECALL]
"We've been notified that NHTSA — the National Highway Traffic
Safety Administration — has issued a safety recall affecting
your {args.vehicle}.

The recall number is {args.recall_campaign}, and it involves
the {args.component}.

Here's what they found: {args.description}

The concern is: {args.consequence}

The good news is, the manufacturer is covering this completely.
{args.remedy}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[KEY POINT — SAY THIS CLEARLY]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"This repair is at absolutely no cost to you — it's covered
under the manufacturer's recall program."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[URGENCY LANGUAGE — adjust by level]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{'[HIGH URGENCY] "We do recommend you try to limit driving the vehicle until we can get this addressed. It affects a safety system and we want to make sure you and your family are protected."' if args.urgency == 'high' else ''}
{'[MEDIUM] "We'd recommend getting this scheduled within the next few weeks."' if args.urgency == 'medium' else ''}
{'[LOW] "There's no immediate rush, but we do want to get it handled for you."' if args.urgency == 'low' else ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[SCHEDULE THE APPOINTMENT]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Do you have time this week or next that works for you?
We'll get you in and out as efficiently as possible."

[IF YES] → Schedule the appointment. Read back date/time to confirm.
          "Perfect. I have you down for [DATE] at [TIME].
          We'll send you a reminder the day before."

[IF NOT NOW] → "No problem. I'll send you a text and email
               with all the details so you have the recall
               number and everything in writing. Please
               reach out when you're ready and we'll
               get you right in."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[CLOSING]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Thanks so much, {customer}. Your safety is our priority.
If you have any questions before your appointment, don't
hesitate to call us at {phone}.
Have a great day!"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[IF VOICEMAIL]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Hi {customer}, this is [YOUR NAME] from {shop} calling
at {phone}. I'm reaching out about an important safety recall
that affects your {args.vehicle} — recall number {args.recall_campaign}.
The good news is the repair is completely free. Please give us
a call when you get a chance so we can get you scheduled.
Thanks, and have a great day."

════════════════════════════════════════════════════
After this call: Log the attempt and outcome in the
customer file. If no answer: follow up with SMS and email.
════════════════════════════════════════════════════"""

    return script


def build_shop_note(args, profile):
    """Internal shop file note — for the customer record."""
    shop  = profile.get('shop_name', 'Your Shop')
    today = datetime.now().strftime('%B %d, %Y %I:%M %p')
    urgency_label = URGENCY_LABELS.get(args.urgency, URGENCY_LABELS['medium'])

    note = f"""══════════════════════════════════════════
INTERNAL SHOP NOTE — RECALL NOTIFICATION
══════════════════════════════════════════
Date/Time  : {today}
Shop       : {shop}
Customer   : {args.customer}
Vehicle    : {args.vehicle}
──────────────────────────────────────────
RECALL INFORMATION
──────────────────────────────────────────
Campaign # : {args.recall_campaign}
Component  : {args.component}
Priority   : {urgency_label}

Defect     : {args.description}
Consequence: {args.consequence}
Remedy     : {args.remedy}
──────────────────────────────────────────
NOTIFICATION STATUS
──────────────────────────────────────────
[ ] SMS sent
[ ] Email sent
[ ] Phone call attempted
[ ] Appointment scheduled: _______________
[ ] Recall repair completed: _____________
[ ] Customer declined — reason: __________
──────────────────────────────────────────
NOTES:


══════════════════════════════════════════
NHTSA Source: https://www.nhtsa.gov/recalls
Campaign {args.recall_campaign} — {args.vehicle}
══════════════════════════════════════════"""

    return note


def main():
    parser = argparse.ArgumentParser(
        description="Generate customer recall notifications — Module 8"
    )
    parser.add_argument('--customer',        required=True, help="Customer full name")
    parser.add_argument('--vehicle',         required=True, help="Vehicle description (e.g. '2019 Toyota Camry')")
    parser.add_argument('--recall_campaign', required=True, help="NHTSA Campaign Number (e.g. 19V123000)")
    parser.add_argument('--component',       required=True, help="Component affected (e.g. 'Fuel Pump')")
    parser.add_argument('--description',     required=True, help="What is the defect")
    parser.add_argument('--consequence',     default='',    help="Consequence if not repaired")
    parser.add_argument('--remedy',          required=True, help="What the manufacturer will do")
    parser.add_argument('--urgency',         default='medium',
                        choices=['low', 'medium', 'high'],
                        help="Urgency level: low | medium | high")

    args = parser.parse_args()

    if not args.consequence:
        args.consequence = "See NHTSA recall details for full consequence description."

    profile = load_profile()
    shop    = profile.get('shop_name', 'Your Shop')

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

    safe_campaign = args.recall_campaign.replace('/', '-').replace(' ', '_')
    today_str     = datetime.now().strftime('%Y%m%d')

    # Build all four outputs
    outputs = {
        f"recall_notification_sms_{safe_campaign}.txt":          build_sms(args, profile),
        f"recall_notification_email_{safe_campaign}.txt":        build_email(args, profile),
        f"recall_notification_phone_{safe_campaign}.txt":        build_phone_script(args, profile),
        f"recall_notification_shop_note_{safe_campaign}.txt":    build_shop_note(args, profile),
    }

    saved = []
    for filename, content in outputs.items():
        filepath = os.path.join(os.path.abspath(OUTPUT_DIR), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        saved.append(filename)

    # Verify SMS length
    sms_content = outputs[f"recall_notification_sms_{safe_campaign}.txt"]
    sms_len     = len(sms_content)
    sms_status  = "OK" if sms_len <= 160 else f"WARNING — {sms_len} chars (over 160)"

    print("=" * 60)
    print(f"  RECALL NOTIFICATIONS GENERATED")
    print(f"  {shop}")
    print("=" * 60)
    print(f"\n  Customer   : {args.customer}")
    print(f"  Vehicle    : {args.vehicle}")
    print(f"  Campaign # : {args.recall_campaign}")
    print(f"  Urgency    : {args.urgency.upper()} — {URGENCY_LABELS[args.urgency]}")
    print()
    print("  Files saved to output/recall/:")
    for filename in saved:
        tag = ""
        if 'sms' in filename:
            tag = f"  [{sms_len} chars — {sms_status}]"
        print(f"    ✓ {filename}{tag}")
    print()
    print("  NEXT STEPS:")
    print("    1. Copy SMS text → send via your messaging platform")
    print("    2. Copy email → send via your email client")
    print("    3. Hand phone script to service advisor")
    print("    4. Add shop note to customer file")
    print("=" * 60)

    # Print SMS so agent can verify it
    print(f"\n  SMS PREVIEW ({sms_len} chars):")
    print(f"  {sms_content}")


if __name__ == '__main__':
    main()
