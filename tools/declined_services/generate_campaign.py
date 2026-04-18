#!/usr/bin/env python3
"""
Generate a multi-touch declined services follow-up campaign.

Usage:
    python tools/declined_services/generate_campaign.py \\
        --service "Brake Pad Replacement" \\
        --urgency safety-critical \\
        --offer "15% off brake service this week, max $75"

    python tools/declined_services/generate_campaign.py \\
        --service "Transmission Flush" \\
        --urgency medium \\
        --offer "10% off, max $50"

    python tools/declined_services/generate_campaign.py \\
        --service "Battery Replacement" \\
        --urgency high \\
        --offer "$20 off" \\
        --touches 1,2

Urgency levels:
    low             - Cosmetic or minor convenience (e.g., cabin air filter)
    medium          - Performance/longevity impact (e.g., transmission flush)
    high            - Reliability risk (e.g., worn tires, weak battery)
    safety-critical - Immediate safety concern (e.g., metal-on-metal brakes)

Touch sequence:
    Touch 1  - Same day    - Educational, no selling
    Touch 2  - 3 days      - Consequence context, honest urgency
    Touch 3  - 2 weeks     - Incentive offer
    Touch 4  - 30 days     - Final check-in, easy CTA
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
import re

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'declined_services')

SMS_LIMIT = 160

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


def slugify(text):
    return re.sub(r'[^a-z0-9_]', '_', text.lower().strip()).strip('_')


# ---------------------------------------------------------------------------
# Urgency context blocks
# Each urgency level provides content snippets used in the templates.
# ---------------------------------------------------------------------------

URGENCY_CONTEXT = {
    "low": {
        "label":          "Low Priority",
        "t1_why":         (
            "This service is a routine maintenance item that affects your comfort and "
            "convenience — things like air quality in the cabin or minor wear items. "
            "It won't leave you stranded, but staying on top of it keeps your vehicle "
            "at its best."
        ),
        "t1_defer_risk":  (
            "Deferring this service won't cause immediate problems, but it can affect "
            "your driving comfort and may lead to slightly accelerated wear on related "
            "components over time."
        ),
        "t1_signs":       (
            "Reduced air quality inside the vehicle, minor odors, or the indicator "
            "light if your vehicle has one."
        ),
        "t2_consequence": (
            "Continued deferral means reduced performance of the affected system. "
            "This is a relatively small service that's easy to handle on your "
            "next visit — no rush, but worth planning for."
        ),
        "t2_timing":      "at your convenience",
        "t4_close":       (
            "No pressure — just wanted to make sure you had all the information. "
            "We're here whenever you're ready."
        ),
    },
    "medium": {
        "label":          "Medium Priority",
        "t1_why":         (
            "This service directly affects your vehicle's long-term reliability and "
            "efficiency. Skipping it doesn't cause an immediate failure, but deferring "
            "it too long typically leads to higher repair costs down the road as related "
            "components work harder than they should."
        ),
        "t1_defer_risk":  (
            "Continuing to defer this service can lead to accelerated wear on connected "
            "components. What starts as a $150–$200 maintenance item can turn into a "
            "$600–$900 repair if the surrounding parts are damaged in the process."
        ),
        "t1_signs":       (
            "Changes in shifting, fuel economy, or performance; warning lights; or "
            "unusual smells — especially when the vehicle is under load."
        ),
        "t2_consequence": (
            "The longer this service is deferred, the more the related components have "
            "to compensate — which means higher wear and a higher repair bill when you "
            "do get it done. Taking care of it now is the more cost-effective path."
        ),
        "t2_timing":      "in the next few weeks",
        "t4_close":       (
            "This service is still worth taking care of — it'll protect your investment "
            "and keep things running smoothly. We're here whenever it works for you."
        ),
    },
    "high": {
        "label":          "High Priority",
        "t1_why":         (
            "This service has a direct impact on your vehicle's reliability. A failure "
            "in this area typically doesn't give much warning — and when it does fail, "
            "it can leave you stranded or require significantly more expensive repairs. "
            "We flagged it because we'd want to know if it were our vehicle."
        ),
        "t1_defer_risk":  (
            "Continued use without addressing this increases the likelihood of an "
            "unexpected failure. The repair cost at that point is usually 2–3× higher "
            "than the maintenance cost now, and a roadside breakdown adds towing and "
            "downtime on top of that."
        ),
        "t1_signs":       (
            "Warning lights, unusual sounds, changes in handling or performance, or "
            "the vehicle not starting reliably. If you notice any of these, call us "
            "right away rather than waiting for a scheduled appointment."
        ),
        "t2_consequence": (
            "This is a service we'd recommend addressing soon — not because we're "
            "trying to add to your bill, but because the cost of waiting is measurably "
            "higher than the cost of acting now. We've seen this play out many times "
            "and we'd rather help you avoid the bigger expense."
        ),
        "t2_timing":      "soon — ideally within the next few weeks",
        "t4_close":       (
            "We genuinely want to make sure you're safe and not caught off guard by "
            "a breakdown. If cost is a concern, call us — we may be able to work with "
            "you on timing or financing. We're on your side."
        ),
    },
    "safety-critical": {
        "label":          "Safety-Critical",
        "t1_why":         (
            "We want to be straightforward with you: this service affects your ability "
            "to safely control your vehicle. We noted it during your visit because it's "
            "the kind of thing we'd tell a family member — not something to put off "
            "indefinitely. You deserve to know the full picture."
        ),
        "t1_defer_risk":  (
            "Continuing to drive without addressing this increases the risk of a "
            "safety-related failure. This isn't a scare tactic — it's the honest "
            "assessment from our technician who inspected your vehicle. The specific "
            "risk is that the affected system may not respond as expected when you "
            "need it most, such as during emergency braking or evasive maneuvers."
        ),
        "t1_signs":       (
            "Warning lights related to braking, steering, or stability; unusual "
            "sounds when braking or turning; pulling to one side; longer stopping "
            "distances; or any handling that feels 'off' compared to normal. "
            "If you notice any of these, please call us before driving further."
        ),
        "t2_consequence": (
            "We want to be direct: this is a safety item, and we'd be doing you a "
            "disservice if we didn't say so plainly. The risk isn't just to your "
            "vehicle — it's to you, your passengers, and other drivers. "
            "We strongly recommend scheduling this service soon."
        ),
        "t2_timing":      "as soon as possible",
        "t4_close":       (
            "We're still concerned about this one. If cost is the barrier, please "
            "call us — we want to find a way to help you get this taken care of. "
            "Your safety matters more than a single transaction."
        ),
    },
}


# ---------------------------------------------------------------------------
# Template builders
# ---------------------------------------------------------------------------

def build_touch_1(profile, service, urgency_key):
    ctx       = URGENCY_CONTEXT[urgency_key]
    shop_name = pval(profile, 'shop_name',  'Your Auto Shop')
    owner_name= pval(profile, 'owner_name', 'The Owner')
    phone     = pval(profile, 'phone',       '(555) 555-5555')
    website   = pval(profile, 'website',     'yourshop.com')

    safety_note = (
        "\n⚠️  SAFETY NOTE: This is a safety-critical service. If you notice "
        "any changes in braking, steering, or handling before your next visit, "
        f"please call us at {phone} before driving further.\n"
        if urgency_key == "safety-critical" else ""
    )

    sms = (
        f"Hi {{{{customer_name}}}}, thanks for visiting {shop_name} today. "
        f"We recommended {service} — here's why it matters: {phone}"
    )

    email = f"""\
Subject: About the {service} We Recommended — {shop_name}

Hi {{{{customer_name}}}},

Thank you for bringing your {{{{vehicle}}}} to {shop_name} today. We wanted to \
follow up on the {service} our technician recommended, and make sure you have \
the full picture — no pressure, just information.

WHY WE RECOMMENDED THIS SERVICE
{ctx['t1_why']}

WHAT CAN HAPPEN IF IT'S DEFERRED
{ctx['t1_defer_risk']}

SIGNS TO WATCH FOR
{ctx['t1_signs']}
{safety_note}
This message isn't a sales pitch — it's the same information we'd share with \
a family member. If you have questions about what we found or want to see the \
actual inspection notes, call us at {phone} or stop by any time.

We'll be in touch.

{owner_name}
{shop_name}
{phone} | {website}
"""

    phone_script = f"""\
[GREET] Hi {{{{customer_name}}}}, this is {{{{agent_name}}}} from {shop_name}. \
How are you?

[PURPOSE] I'm calling as a follow-up to your visit today. I wanted to make \
sure you had some useful information about the {service} our technician flagged.

[INFO] Here's the short version: {ctx['t1_why']}

The signs to watch for are {ctx['t1_signs']}

[PAUSE] Does that make sense? Any questions about what we found?

[IF YES — WANTS MORE INFO] Happy to walk you through the inspection notes. \
Want me to send you a text with everything in writing?

[IF NO — WANTS TO SCHEDULE] Great — I can get you on the schedule right now. \
[Check availability and book the appointment. Confirm date and time before ending \
the call.]

[IF NO — NOT READY] Totally understood. Just wanted to make sure you had the \
information. We'll send you a quick follow-up in a few days.

[CLOSE] Thanks for your time today, {{{{customer_name}}}}. Call us at {phone} \
anytime — we're always happy to answer questions. Drive safe!
"""

    return {"sms": sms, "email": email, "phone_script": phone_script}


def build_touch_2(profile, service, urgency_key):
    ctx       = URGENCY_CONTEXT[urgency_key]
    shop_name = pval(profile, 'shop_name',  'Your Auto Shop')
    owner_name= pval(profile, 'owner_name', 'The Owner')
    phone     = pval(profile, 'phone',       '(555) 555-5555')
    website   = pval(profile, 'website',     'yourshop.com')

    safety_header = (
        "⚠️  SAFETY-CRITICAL SERVICE — Please read before your next drive.\n\n"
        if urgency_key == "safety-critical" else ""
    )

    sms = (
        f"Hi {{{{customer_name}}}}, following up on the {service} from your "
        f"visit. Worth addressing {ctx['t2_timing']}. "
        f"Call {phone} — {shop_name}."
    )

    email = f"""\
Subject: A Follow-Up on Your {service} — {shop_name}

Hi {{{{customer_name}}}},
{safety_header}
This is a brief follow-up on the {service} we recommended during your last \
visit to {shop_name}.

THE HONEST PICTURE
{ctx['t2_consequence']}

TIMING
We recommend taking care of this {ctx['t2_timing']}.

WHAT'S INVOLVED
  - Service:          {service}
  - Typical duration: {{{{est_duration}}}}
  - Estimated cost:   {{{{estimated_cost}}}}

TO SCHEDULE
  Call:   {phone}
  Online: {website}

If you have any questions — about what we found, what the repair involves, \
or what happens if you wait — just call us. We'd rather answer your questions \
than have you make a decision without the full picture.

{owner_name}
{shop_name}
{phone}
"""

    phone_script = f"""\
[GREET] Hi {{{{customer_name}}}}, this is {{{{agent_name}}}} calling from \
{shop_name}. I appreciate you taking my call.

[PURPOSE] I'm following up on the {service} we noted on your vehicle during \
your last visit.

[CONTEXT] {ctx['t2_consequence']}

[RECOMMENDATION] We'd recommend taking care of this {ctx['t2_timing']}.

[PAUSE] How does your schedule look? I can check what availability we have.

[IF READY TO BOOK] Great — let me get you on the schedule. \
[Offer 2–3 time slots. Confirm the appointment before ending the call. \
Read back the date, time, and service.]

[IF NOT READY] I understand. I'll send you a quick text with the details and \
a link to book online whenever you're ready. Just know we're here if you have \
questions.

[CLOSE] Thanks, {{{{customer_name}}}}. Please don't hesitate to call us at \
{phone} with any questions. We're always happy to help!
"""

    return {"sms": sms, "email": email, "phone_script": phone_script}


def build_touch_3(profile, service, urgency_key, offer):
    ctx       = URGENCY_CONTEXT[urgency_key]
    shop_name = pval(profile, 'shop_name',  'Your Auto Shop')
    owner_name= pval(profile, 'owner_name', 'The Owner')
    phone     = pval(profile, 'phone',       '(555) 555-5555')
    website   = pval(profile, 'website',     'yourshop.com')

    sms = (
        f"Hi {{{{customer_name}}}}, we'd like to make your {service} easier — "
        f"{offer}. Call {phone} to book. — {shop_name}"
    )

    email = f"""\
Subject: A Little Something to Make It Easier — {service} at {shop_name}

Hi {{{{customer_name}}}},

It's been a couple of weeks since your last visit, and we wanted to reach out \
one more time about the {service} our technician recommended for your \
{{{{vehicle}}}}.

We know that extra services aren't always easy to work into the budget right \
away, so we'd like to offer you something to make it a little easier:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{offer}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TO REDEEM: Just mention this when you call or book online. No coupon needed.

HOW TO BOOK:
  Call:   {phone}
  Online: {website}

This offer is valid for the next 14 days. We want to help you take care of \
this in a way that works for you — not pressure you into anything.

If you have any questions about the service or the cost, call us. \
We're happy to walk through it with you.

Thank you for being a customer, {{{{customer_name}}}}.

{owner_name}
{shop_name}
{phone} | {website}
"""

    phone_script = f"""\
[GREET] Hi {{{{customer_name}}}}, this is {{{{agent_name}}}} from {shop_name}. \
How are you doing?

[PURPOSE] I'm calling because we wanted to make it easier for you to get the \
{service} taken care of on your {{{{vehicle}}}}.

[OFFER] We'd like to offer you {offer}. We want to be a resource for you, \
not a source of pressure — so consider this our way of making it as easy \
as possible.

[PAUSE] Would you like to go ahead and get that scheduled?

[IF YES] Great — let me find you a time. [Offer 2–3 options. Confirm the \
appointment. Read back date, time, and service before hanging up. Note the \
discount on the work order.]

[IF NO — COST CONCERN] I understand. Is there anything we can do to help work \
around that? We want to find a solution that works for you.

[IF NO — NOT INTERESTED NOW] Totally fine. The offer stands for two weeks if \
you change your mind. Call us at {phone} anytime.

[CLOSE] Thanks for your time, {{{{customer_name}}}}. We appreciate you and \
we're here whenever you need us. Take care!
"""

    return {"sms": sms, "email": email, "phone_script": phone_script}


def build_touch_4(profile, service, urgency_key):
    ctx        = URGENCY_CONTEXT[urgency_key]
    shop_name  = pval(profile, 'shop_name',  'Your Auto Shop')
    owner_name = pval(profile, 'owner_name', 'The Owner')
    phone      = pval(profile, 'phone',       '(555) 555-5555')
    website    = pval(profile, 'website',     'yourshop.com')
    review_link = profile.get('review_links', {}).get('google', '')

    review_section = (
        f"\nP.S. — If you've had a good experience with us overall, we'd "
        f"really appreciate a quick Google review: {review_link}\n"
        if review_link and urgency_key not in ("safety-critical",) else ""
    )

    sms = (
        f"Hi {{{{customer_name}}}}, last check-in on your {service} from "
        f"{shop_name}. We're here when you're ready: {phone}"
    )

    email = f"""\
Subject: Last Check-In — {service} for Your {{{{vehicle}}}} | {shop_name}

Hi {{{{customer_name}}}},

This is our last follow-up message about the {service} we recommended for \
your {{{{vehicle}}}}. We don't want to overdo it — we just want to make sure \
you have everything you need to make the right call for you.

WHERE THINGS STAND
{ctx['t4_close']}

WHEN YOU'RE READY
  Call:   {phone}
  Online: {website}

There's no deadline and no pressure from us. If you have questions — even \
down the road — don't hesitate to reach out. We keep records on your vehicle, \
so we'll know exactly what we found and what we discussed.

Thank you for trusting {shop_name} with your vehicle, {{{{customer_name}}}}. \
We appreciate you.{review_section}
{owner_name}
{shop_name}
{phone} | {website}
"""

    phone_script = f"""\
[GREET] Hi {{{{customer_name}}}}, this is {{{{agent_name}}}} from {shop_name}. \
I promise this is my last call about this!

[PURPOSE] I just wanted to do one final check-in about the {service} we \
recommended during your last visit. I know you've heard from us a few times, \
and I appreciate your patience.

[CLOSE LOOP] {ctx['t4_close']}

[PAUSE] Is there anything we can do to help make this happen — or any \
questions I can answer?

[IF YES — READY TO BOOK] Wonderful! Let me get you on the schedule right \
now. [Offer availability. Confirm appointment. Read back details. \
Mark campaign as converted in the CRM.]

[IF NO — FINAL PASS] That's completely understood. We've got all the notes \
on file for your vehicle, so whenever you're ready — whether it's next week \
or next year — just call us at {phone} and we'll pick right up where we \
left off.

[CLOSE] Thank you for being a customer, {{{{customer_name}}}}. It genuinely \
means a lot. Have a great day and drive safe!
"""

    return {"sms": sms, "email": email, "phone_script": phone_script}


# ---------------------------------------------------------------------------
# Touch builders dispatch
# ---------------------------------------------------------------------------

def build_touch(touch_num, profile, service, urgency_key, offer):
    if touch_num == 1:
        return build_touch_1(profile, service, urgency_key)
    elif touch_num == 2:
        return build_touch_2(profile, service, urgency_key)
    elif touch_num == 3:
        return build_touch_3(profile, service, urgency_key, offer)
    elif touch_num == 4:
        return build_touch_4(profile, service, urgency_key)
    return None


TOUCH_TIMING = {
    1: "Same day (end of visit) — Educational",
    2: "3 days after visit    — Consequence context",
    3: "2 weeks after visit   — Incentive offer",
    4: "30 days after visit   — Final check-in",
}

ALL_CHANNELS = ["sms", "email", "phone_script"]


def check_sms_length(content, touch_num, urgency_key):
    sample = content
    subs = {
        '{{customer_name}}': 'Christopher',
        '{{vehicle}}':       '2019 Toyota Camry',
        '{{agent_name}}':    'Marcus',
        '{{est_duration}}':  '1–2 hours',
        '{{estimated_cost}}': '$180–$220',
    }
    for ph, val in subs.items():
        sample = sample.replace(ph, val)
    if len(sample) > SMS_LIMIT:
        print(f"  ⚠️  Touch {touch_num} SMS may exceed 160 chars "
              f"(~{len(sample)} chars). Review and tighten.", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a multi-touch declined services follow-up campaign."
    )
    parser.add_argument(
        '--service',
        required=True,
        help="The declined service (e.g., 'Brake Pad Replacement', 'Transmission Flush')."
    )
    parser.add_argument(
        '--urgency',
        default='medium',
        choices=['low', 'medium', 'high', 'safety-critical'],
        help="Urgency level — affects tone and safety language. Default: medium."
    )
    parser.add_argument(
        '--offer',
        default='Complimentary multi-point inspection with your service when you book this month.',
        help="Touch 3 incentive offer text."
    )
    parser.add_argument(
        '--touches',
        default='1,2,3,4',
        help="Comma-separated touch numbers to generate (default: 1,2,3,4)."
    )
    parser.add_argument(
        '--channels',
        default='sms,email,phone_script',
        help="Comma-separated channels (default: sms,email,phone_script)."
    )
    args = parser.parse_args()

    profile  = load_profile()
    channels = [c.strip() for c in args.channels.split(',')]

    try:
        touch_nums = [int(t.strip()) for t in args.touches.split(',')]
        for t in touch_nums:
            if t not in (1, 2, 3, 4):
                raise ValueError(f"Invalid touch number: {t}")
    except ValueError as e:
        print(f"ERROR: --touches must be comma-separated numbers 1–4. {e}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)
    output_dir = os.path.abspath(OUTPUT_DIR)

    service_slug = slugify(args.service)
    urgency_ctx  = URGENCY_CONTEXT[args.urgency]

    print(f"\n🔧 Generating declined services campaign")
    print(f"   Service  : {args.service}")
    print(f"   Urgency  : {args.urgency} ({urgency_ctx['label']})")
    print(f"   Offer    : {args.offer}")
    print(f"   Touches  : {', '.join(str(t) for t in touch_nums)}")
    print(f"   Channels : {', '.join(channels)}")
    print(f"   Shop     : {pval(profile, 'shop_name', '[Not Set]')}")
    print()

    if args.urgency == 'safety-critical':
        print("  ⚠️  SAFETY-CRITICAL: Touch 1 includes plain-language safety information.")
        print("      Review Touch 1 before sending to ensure accuracy for this vehicle.\n")

    all_generated = []

    for touch_num in touch_nums:
        print(f"📋 Touch {touch_num} — {TOUCH_TIMING[touch_num]}")
        templates = build_touch(touch_num, profile, args.service, args.urgency, args.offer)
        if not templates:
            print(f"  ⚠️  Could not build Touch {touch_num}", file=sys.stderr)
            continue

        for channel in channels:
            content = templates.get(channel)
            if content is None:
                print(f"  ⚠️  No '{channel}' for Touch {touch_num}", file=sys.stderr)
                continue

            if channel == 'sms':
                check_sms_length(content, touch_num, args.urgency)

            filename = f"{service_slug}_touch{touch_num}_{channel}.txt"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as fh:
                fh.write(content)

            print(f"  ✅ output/declined_services/{filename}")
            all_generated.append(filename)

    print(f"\n{'─'*55}")
    print(f"✅ Done — {len(all_generated)} file(s) saved to output/declined_services/")
    print()
    print("Send schedule:")
    for t in touch_nums:
        print(f"  Touch {t}: {TOUCH_TIMING[t]}")
    print()
    print("Placeholder guide (fill these at send time):")
    print("  {{customer_name}}  {{vehicle}}  {{agent_name}}")
    print("  {{est_duration}}   {{estimated_cost}}")


if __name__ == '__main__':
    main()
