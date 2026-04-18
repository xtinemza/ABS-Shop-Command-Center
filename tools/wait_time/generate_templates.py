#!/usr/bin/env python3
"""
Generate in-service status update templates for every stage of the customer visit.

Usage:
    # Generate all 5 status types × 3 channels (15 files)
    python tools/wait_time/generate_templates.py \\
        --status all \\
        --service_type "Brake Service"

    # Generate a single status
    python tools/wait_time/generate_templates.py \\
        --status drop_off_confirmation \\
        --service_type "Oil Change"

    # Generate with specific channels only
    python tools/wait_time/generate_templates.py \\
        --status ready_for_pickup \\
        --service_type "Transmission Service" \\
        --channels sms,email

Status types:
    drop_off_confirmation   inspection_update   repair_in_progress
    ready_for_pickup        delayed_notification
    all  (generates all 5 = 15 files)

Channels: sms, email, phone_script
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
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'wait_time')

SMS_LIMIT = 160

STATUS_ORDER = [
    "drop_off_confirmation",
    "inspection_update",
    "repair_in_progress",
    "ready_for_pickup",
    "delayed_notification",
]

ALL_CHANNELS = ["sms", "email", "phone_script"]

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


# ---------------------------------------------------------------------------
# Templates
#
# Profile tokens:  {shop_name}  {phone}  {address}  {hours}  {website}
# Runtime tokens:  {{customer_name}}  {{vehicle}}  {{service_type}}
#                  {{tech_name}}  {{est_time}}  {{work_summary}}  {{total}}
#                  {{finding}}  {{finding_cost}}  {{delay_reason}}
#                  {{new_est_time}}  {{close_time}}
# ---------------------------------------------------------------------------

TEMPLATES = {

    "drop_off_confirmation": {
        "sms": (
            "Hi {{customer_name}}, we've checked in your {{vehicle}} at {shop_name}. "
            "Est. ready: {{est_time}}. We'll update you if anything changes. "
            "Questions? {phone}"
        ),
        "email": (
            "Subject: Your {{vehicle}} is Checked In — {shop_name}\n\n"
            "Hi {{customer_name}},\n\n"
            "We have your {{vehicle}} and it's in the queue. Here's a quick summary "
            "of where things stand:\n\n"
            "  Service:              {{service_type}}\n"
            "  Technician:           {{tech_name}}\n"
            "  Estimated completion: {{est_time}}\n\n"
            "What happens next:\n"
            "1. Our technician will complete a multi-point inspection before starting "
            "your {{service_type}}.\n"
            "2. If we find anything beyond what was already discussed, we will call "
            "or text you before doing anything additional — no surprises.\n"
            "3. We'll send you an update when the vehicle is ready for pickup.\n\n"
            "Need to reach us in the meantime? Call {phone} and reference your name — "
            "we'll pull up your vehicle right away.\n\n"
            "{shop_name}\n"
            "{phone} | {address}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{tech_name}} from {shop_name}.\n\n"
            "[PURPOSE] I'm calling to let you know we've got your {{vehicle}} checked "
            "in and it's in the queue for your {{service_type}}.\n\n"
            "[INFO] Our estimated completion time is {{est_time}}. Before we start, "
            "we'll do a quick multi-point inspection. If we notice anything else "
            "while we have the vehicle, we'll call you before touching it.\n\n"
            "[PAUSE] Any questions before we get started?\n\n"
            "[CLOSE] Perfect. We'll be in touch when it's ready. Call us at "
            "{phone} if you need anything. Thanks, {{customer_name}}!"
        ),
    },

    "inspection_update": {
        "sms": (
            "Hi {{customer_name}}, inspection on your {{vehicle}} is done. We found "
            "something — calling you now to walk through it. Or call {phone}."
        ),
        "email": (
            "Subject: Inspection Complete — We Have Findings to Discuss | {shop_name}\n\n"
            "Hi {{customer_name}},\n\n"
            "Our technician has completed the multi-point inspection on your {{vehicle}} "
            "and we wanted to share what we found.\n\n"
            "ORIGINALLY REQUESTED SERVICE:\n"
            "  {{service_type}} — this work is proceeding as planned.\n\n"
            "ADDITIONAL FINDING:\n"
            "  What we found:   {{finding}}\n"
            "  Why it matters:  {{finding_explanation}}\n"
            "  Estimated cost:  {{finding_cost}}\n\n"
            "IMPORTANT: We will NOT proceed with the additional work without your "
            "approval. This finding is separate from your original service.\n\n"
            "TO APPROVE OR DECLINE:\n"
            "  - Call us at {phone} — we'll walk you through it and answer any questions.\n"
            "  - Reply to this email with 'Approved' or 'Declined' and we'll proceed "
            "accordingly.\n\n"
            "If you'd like photos or a more detailed explanation, just say the word — "
            "we're happy to show you what we're seeing.\n\n"
            "{shop_name}\n"
            "{phone} | {address}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{tech_name}} at {shop_name}.\n\n"
            "[PURPOSE] We've finished the inspection on your {{vehicle}} and I wanted "
            "to walk you through what we found.\n\n"
            "[INFO] Your {{service_type}} is all set — no issues there. But during the "
            "inspection, we also found {{finding}}. Here's why that matters: "
            "{{finding_explanation}}.\n\n"
            "The estimated cost for that additional work would be {{finding_cost}}.\n\n"
            "[PAUSE] I want to be clear — we won't touch that without your go-ahead. "
            "What would you like to do?\n\n"
            "[IF APPROVED] Great, we'll add that to the work order. Updated ETA is "
            "{{new_est_time}}. We'll call you when everything is done.\n\n"
            "[IF DECLINED] Totally understood. We'll complete the {{service_type}} "
            "as originally discussed and have it ready by {{est_time}}. "
            "[Document the declined service in the vehicle record for follow-up.]\n\n"
            "[CLOSE] Thanks, {{customer_name}}. Call us at {phone} if you have "
            "any other questions."
        ),
    },

    "repair_in_progress": {
        "sms": (
            "Update from {shop_name}: Your {{vehicle}} {{service_type}} is in "
            "progress. Est. ready: {{est_time}}. Call {phone} with questions."
        ),
        "email": (
            "Subject: Work in Progress — Your {{vehicle}} | {shop_name}\n\n"
            "Hi {{customer_name}},\n\n"
            "Quick update on your {{vehicle}}:\n\n"
            "  Status:    Your {{service_type}} is currently in progress.\n"
            "  Tech:      {{tech_name}}\n"
            "  Est. done: {{est_time}}\n\n"
            "Everything is on track. We'll send you another message the moment "
            "your vehicle is ready for pickup.\n\n"
            "If you need to reach us before then — for any reason — call {phone} "
            "and we'll get you an update right away.\n\n"
            "{shop_name}\n"
            "{phone}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{tech_name}} from {shop_name}.\n\n"
            "[PURPOSE] Just a quick progress update — your {{service_type}} is "
            "underway on your {{vehicle}}.\n\n"
            "[INFO] We're tracking to have it ready by {{est_time}}. Everything looks "
            "good so far — no surprises.\n\n"
            "[PAUSE] Is there anything you need from us in the meantime?\n\n"
            "[CLOSE] We'll call you as soon as it's ready. Thanks, {{customer_name}}!"
        ),
    },

    "ready_for_pickup": {
        "sms": (
            "Great news, {{customer_name}}! Your {{vehicle}} is ready at {shop_name}. "
            "Total: ${{total}}. Pick up by {{close_time}}. Call {phone}."
        ),
        "email": (
            "Subject: Your {{vehicle}} is Ready for Pickup! — {shop_name}\n\n"
            "Hi {{customer_name}},\n\n"
            "Your {{vehicle}} is done and waiting for you!\n\n"
            "SERVICE SUMMARY:\n"
            "{{work_summary}}\n\n"
            "TOTAL DUE: ${{total}}\n\n"
            "PICKUP DETAILS:\n"
            "  Location:  {address}\n"
            "  Hours:     {hours}\n"
            "  Phone:     {phone}\n\n"
            "PAYMENT:\n"
            "  We accept cash, personal check, and all major credit cards.\n"
            "  Payment is due at pickup.\n\n"
            "Before you go, we recommend reviewing the service summary with "
            "our front desk. We'll walk you through what was done, point out "
            "anything to watch for, and confirm your next recommended service.\n\n"
            "If you have any questions about the work performed, call us at "
            "{phone} — we're happy to go over everything.\n\n"
            "Thank you for choosing {shop_name}!\n\n"
            "{shop_name}\n"
            "{phone} | {address} | {website}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, great news — this is {{tech_name}} from "
            "{shop_name}.\n\n"
            "[PURPOSE] Your {{vehicle}} is all done and ready for pickup!\n\n"
            "[SUMMARY] Here's a quick rundown of what we completed: "
            "{{work_summary}}. Total comes to ${{total}}.\n\n"
            "[INFO] We're open until {{close_time}} today. Payment is due at pickup — "
            "we accept cash, check, and all major cards.\n\n"
            "[PAUSE] Any questions about the work we did?\n\n"
            "[CLOSE] Perfect — we'll see you when you come in. "
            "If anything comes up between now and then, call us at {phone}. "
            "Thanks, {{customer_name}}!"
        ),
    },

    "delayed_notification": {
        "sms": (
            "Hi {{customer_name}}, we need a bit more time on your {{vehicle}} "
            "— {{delay_reason}}. New ETA: {{new_est_time}}. Call {phone}."
        ),
        "email": (
            "Subject: Updated ETA for Your {{vehicle}} — {shop_name}\n\n"
            "Hi {{customer_name}},\n\n"
            "We want to keep you in the loop — we need a little more time to "
            "complete your {{service_type}} on your {{vehicle}}.\n\n"
            "WHAT'S HAPPENING:\n"
            "  {{delay_reason}}\n\n"
            "UPDATED ESTIMATE:\n"
            "  New completion time: {{new_est_time}}\n\n"
            "We know your time is valuable and we apologize for the delay. "
            "Here are your options:\n\n"
            "  Option 1: Leave the vehicle with us and we'll complete the work "
            "by {{new_est_time}}. We'll call you the moment it's ready.\n\n"
            "  Option 2: Pick up the vehicle now (if the delay means completing "
            "it today isn't practical for you) and reschedule when you're ready. "
            "We'll hold your spot in the queue.\n\n"
            "Call {phone} and let us know how you'd like to handle it — we'll "
            "make it as easy as possible.\n\n"
            "Thank you for your patience.\n\n"
            "{shop_name}\n"
            "{phone} | {address}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{tech_name}} at {shop_name}. "
            "I appreciate you taking my call.\n\n"
            "[PURPOSE] I'm calling because we need a bit more time on your "
            "{{vehicle}}. I want to explain what's going on.\n\n"
            "[REASON] {{delay_reason}}. We're doing this right rather than rushing "
            "it — but I know that affects your timeline, and I wanted to give you "
            "a heads-up right away.\n\n"
            "[NEW ETA] Our new estimated completion time is {{new_est_time}}.\n\n"
            "[PAUSE] I want to give you options. You can leave the vehicle and we'll "
            "have it done by {{new_est_time}}, or if that doesn't work for you, "
            "you're welcome to pick it up now and we can reschedule.\n\n"
            "[IF LEAVING IT] Perfect, we'll take great care of it. I'll call you "
            "personally when it's ready.\n\n"
            "[IF PICKING UP] Absolutely understood. Come in anytime — we'll have it "
            "ready for you and we'll reschedule the remaining work at your convenience. "
            "[Document in work order and flag for follow-up call.]\n\n"
            "[CLOSE] Thank you for your understanding, {{customer_name}}. "
            "Call us at {phone} anytime. We appreciate your patience."
        ),
    },
}


# ---------------------------------------------------------------------------
# Core generation
# ---------------------------------------------------------------------------

def apply_profile(content, profile):
    shop_name = pval(profile, 'shop_name',  'Your Auto Shop')
    phone     = pval(profile, 'phone',       '(555) 555-5555')
    address   = pval(profile, 'address') or pval(profile, 'location', '123 Main St')
    hours     = pval(profile, 'hours',       'Call for hours')
    website   = pval(profile, 'website',     'yourshop.com')

    for token, value in {
        '{shop_name}': shop_name,
        '{phone}':     phone,
        '{address}':   address,
        '{hours}':     hours,
        '{website}':   website,
    }.items():
        content = content.replace(token, value)
    return content


def check_sms_length(content, status):
    sample = content
    subs = {
        '{{customer_name}}': 'Christopher',
        '{{vehicle}}':       '2019 Toyota Camry',
        '{{service_type}}':  'Transmission Flush',
        '{{est_time}}':      '3:30 PM',
        '{{new_est_time}}':  '5:00 PM',
        '{{tech_name}}':     'Marcus',
        '{{total}}':         '285.00',
        '{{close_time}}':    '6:00 PM',
        '{{delay_reason}}':  'waiting on a part',
    }
    for ph, val in subs.items():
        sample = sample.replace(ph, val)
    if len(sample) > SMS_LIMIT:
        print(f"  ⚠️  SMS for '{status}' may exceed 160 chars "
              f"(~{len(sample)} chars with sample substitution). "
              f"Review and tighten if needed.", file=sys.stderr)


def generate_status(status, service_type, channels, profile, output_dir):
    templates = TEMPLATES.get(status)
    if not templates:
        print(f"ERROR: Unknown status '{status}'", file=sys.stderr)
        return []

    generated = []
    for channel in channels:
        if channel not in templates:
            print(f"  ⚠️  No '{channel}' template for '{status}'", file=sys.stderr)
            continue

        content = templates[channel]
        content = apply_profile(content, profile)
        content = content.replace('{{service_type}}', service_type)

        if channel == 'sms':
            check_sms_length(content, status)

        filename = f"{status}_{channel}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(content)

        print(f"  ✅ output/wait_time/{filename}")
        generated.append(filename)

    return generated


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate in-service status update templates for every stage of the customer visit."
    )
    parser.add_argument(
        '--status',
        required=True,
        choices=STATUS_ORDER + ['all'],
        help="Which status update to generate, or 'all' for all five stages."
    )
    parser.add_argument(
        '--service_type',
        default='General Service',
        help="The service type being performed (e.g., 'Brake Service', 'Oil Change')."
    )
    parser.add_argument(
        '--channels',
        default='sms,email,phone_script',
        help="Comma-separated channels: sms,email,phone_script (default: all three)."
    )
    args = parser.parse_args()

    profile  = load_profile()
    channels = [c.strip() for c in args.channels.split(',')]

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)
    output_dir = os.path.abspath(OUTPUT_DIR)

    statuses = STATUS_ORDER if args.status == 'all' else [args.status]

    print(f"\n🔧 Generating wait time communication templates")
    print(f"   Service type : {args.service_type}")
    print(f"   Status types : {'all (5)' if args.status == 'all' else args.status}")
    print(f"   Channels     : {', '.join(channels)}")
    print(f"   Shop         : {pval(profile, 'shop_name', '[Not Set]')}")
    print()

    all_generated = []
    for status in statuses:
        print(f"📋 {status}")
        generated = generate_status(status, args.service_type, channels, profile, output_dir)
        all_generated.extend(generated)

    print(f"\n{'─'*50}")
    print(f"✅ Done — {len(all_generated)} file(s) saved to output/wait_time/")
    if args.status == 'all':
        print(f"   {len(statuses)} status types × {len(channels)} channels = "
              f"{len(statuses) * len(channels)} templates")
    print()
    print("Placeholder guide (fill these at send time):")
    print("  {{customer_name}}  {{vehicle}}  {{tech_name}}  {{est_time}}")
    print("  {{work_summary}}   {{total}}    {{close_time}} {{delay_reason}}")
    print("  {{finding}}        {{finding_cost}}  {{new_est_time}}")


if __name__ == '__main__':
    main()
