#!/usr/bin/env python3
"""
Generate appointment reminder templates for every touchpoint in the customer journey.

Usage:
    python tools/appointments/generate_reminders.py \\
        --touchpoint all \\
        --service_type "Oil Change" \\
        --channels sms,email,phone_script

    python tools/appointments/generate_reminders.py \\
        --touchpoint booking_confirmation \\
        --service_type "Brake Service" \\
        --channels sms,email,phone_script

Touchpoints:
    booking_confirmation   day_before_reminder   day_of_notification
    post_service_thankyou  thirty_day_followup   six_month_maintenance
    all  (generates all 6 touchpoints = 18 files)

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
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'appointments')

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


# ---------------------------------------------------------------------------
# Templates
# Each template uses:
#   {shop_name}  {phone}  {address}  {owner_name}  {website}  {review_link}
#   {{customer_name}}  {{vehicle}}  {{service_type}}  {{date}}  {{time}}
#   {{duration}}  {{next_service}}  {{next_date}}  {{season}}
#   {{seasonal_tip}}  {{recommended_service_1}}  {{recommended_service_2}}
#   {{next_available}}  {{agent_name}}
# ---------------------------------------------------------------------------

TEMPLATES = {
    "booking_confirmation": {
        "sms": (
            "Hi {{customer_name}}, your {{service_type}} at {shop_name} is confirmed for "
            "{{date}} at {{time}}. {address}. Call {phone} with questions. See you then!"
        ),
        "email": (
            "Subject: Your {{service_type}} Appointment is Confirmed — {shop_name}\n\n"
            "Hi {{customer_name}},\n\n"
            "You're all set! Here's a summary of your upcoming appointment:\n\n"
            "  Service:    {{service_type}}\n"
            "  Date:       {{date}}\n"
            "  Time:       {{time}}\n"
            "  Est. Time:  {{duration}}\n"
            "  Location:   {address}\n\n"
            "A few things to know before you arrive:\n"
            "- Please arrive 5 minutes early so we can get the paperwork started.\n"
            "- Bring your keys (and a spare key fob if you have one).\n"
            "- If you've noticed anything else with your vehicle lately, let us know when "
            "you drop off — we're happy to take a look.\n\n"
            "Need to reschedule? No problem at all — just call us at {phone} and we'll "
            "find a time that works better.\n\n"
            "We'll see you on {{date}}!\n\n"
            "{owner_name}\n"
            "{shop_name}\n"
            "{phone} | {website}"
        ),
        "phone_script": (
            "[GREET] Hi, may I speak with {{customer_name}}? ... "
            "Great, this is {{agent_name}} calling from {shop_name}.\n\n"
            "[PURPOSE] I'm calling to confirm your {{service_type}} appointment "
            "that's scheduled for {{date}} at {{time}}.\n\n"
            "[PAUSE] Does that time still work for you?\n\n"
            "[IF YES] Perfect! Just plan to arrive a few minutes early if you can. "
            "We're located at {address}. The service should take about {{duration}}, "
            "and we'll call you if we find anything else that needs attention.\n\n"
            "[IF NO] No problem at all — let me look at what else we have available. "
            "[Check schedule and offer 2–3 alternatives. Confirm new date/time and "
            "update the booking system before ending the call.]\n\n"
            "[CLOSE] Great, we have you down for {{date}} at {{time}}. "
            "If anything comes up before then, don't hesitate to call us at {phone}. "
            "Thanks, {{customer_name}} — we'll see you soon!"
        ),
    },

    "day_before_reminder": {
        "sms": (
            "Reminder: {{service_type}} at {shop_name} is TOMORROW at {{time}}. "
            "Need to reschedule? Call {phone}. See you soon!"
        ),
        "email": (
            "Subject: Reminder — Your {{service_type}} is Tomorrow at {{time}} | {shop_name}\n\n"
            "Hi {{customer_name}},\n\n"
            "Just a friendly heads-up — your appointment is tomorrow and we're looking "
            "forward to seeing you!\n\n"
            "  Service:   {{service_type}}\n"
            "  Date:      {{date}}\n"
            "  Time:      {{time}}\n"
            "  Location:  {address}\n\n"
            "Quick tips for a smooth drop-off:\n"
            "- Arrive a few minutes early to get checked in quickly.\n"
            "- Let us know if you've noticed any new sounds, smells, or warning lights "
            "— we'll add it to the inspection checklist.\n"
            "- We accept cash, check, and all major credit cards.\n\n"
            "Need to reschedule? No hassle — just call {phone} and we'll sort it out.\n\n"
            "See you tomorrow,\n"
            "{shop_name}\n"
            "{phone}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{agent_name}} from {shop_name}.\n\n"
            "[PURPOSE] I'm just calling with a quick reminder — your {{service_type}} "
            "is scheduled for tomorrow at {{time}}.\n\n"
            "[PAUSE] Are we still on for tomorrow?\n\n"
            "[IF YES] Wonderful! Plan to arrive a few minutes early if you can. "
            "We're at {address}. Is there anything else you'd like us to check while "
            "we have the vehicle?\n\n"
            "[IF NO] Not a problem — let me find you a better time. "
            "[Offer alternatives. Update booking system. Confirm new time before hanging up.]\n\n"
            "[CLOSE] Great, we'll see you tomorrow at {{time}}. "
            "Call us at {phone} if anything comes up. Have a great evening!"
        ),
    },

    "day_of_notification": {
        "sms": (
            "Good morning {{customer_name}}! Your {{service_type}} at {shop_name} "
            "is TODAY at {{time}}. Est. time: {{duration}}. See you soon!"
        ),
        "email": (
            "Subject: See You Today, {{customer_name}}! — {shop_name}\n\n"
            "Good morning {{customer_name}},\n\n"
            "Today's the day! We're all set and ready for your {{service_type}}.\n\n"
            "  Time:      {{time}}\n"
            "  Est. Time: {{duration}}\n"
            "  Location:  {address}\n\n"
            "A couple of things that help us serve you faster:\n"
            "- Let the front desk know when you arrive if you have a preference for "
            "waiting in our lobby or getting a ride.\n"
            "- Mention anything you've noticed recently — unusual sounds, smells, or "
            "changes in how the vehicle drives. Our techs will check it out.\n\n"
            "We're here if you have any last-minute questions: {phone}.\n\n"
            "See you shortly,\n"
            "{shop_name}"
        ),
        "phone_script": (
            "[GREET] Good morning {{customer_name}}! This is {{agent_name}} from {shop_name}.\n\n"
            "[PURPOSE] Just a quick call to say we're expecting you today at {{time}} "
            "for your {{service_type}}.\n\n"
            "[INFO] The job should take about {{duration}}. While we have the vehicle, "
            "is there anything else you'd like us to take a look at?\n\n"
            "[PAUSE] ... Great.\n\n"
            "[CLOSE] We'll have everything ready for you. See you at {{time}}, "
            "{{customer_name}}!"
        ),
    },

    "post_service_thankyou": {
        "sms": (
            "Thanks, {{customer_name}}! Your {{service_type}} is done. "
            "We appreciate you choosing {shop_name}. Mind leaving us a quick review? "
            "{review_link}"
        ),
        "email": (
            "Subject: Thank You for Trusting {shop_name}, {{customer_name}}!\n\n"
            "Hi {{customer_name}},\n\n"
            "Thank you for bringing your {{vehicle}} to {shop_name} today for "
            "your {{service_type}}. We really appreciate your business.\n\n"
            "A few things to keep in mind:\n\n"
            "1. If you notice anything unusual in the next few days — any sounds, smells, "
            "or warning lights — don't hesitate to call us at {phone}. We stand behind "
            "our work and we'll make it right.\n\n"
            "2. Based on today's service, your next recommended maintenance is "
            "{{next_service}} around {{next_date}}. We'll send you a reminder when "
            "that's coming up.\n\n"
            "3. If you had a good experience today, a quick Google review would mean "
            "the world to us — it helps other drivers in {location} find a shop they "
            "can trust:\n"
            "   {review_link}\n\n"
            "Thank you again. Drive safe and don't hesitate to reach out whenever "
            "you need us.\n\n"
            "Gratefully,\n"
            "{owner_name}\n"
            "{shop_name}\n"
            "{phone} | {website}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{agent_name}} from {shop_name}.\n\n"
            "[PURPOSE] We just wanted to follow up and make sure everything went well "
            "with your {{service_type}} today.\n\n"
            "[PAUSE] How is the vehicle feeling?\n\n"
            "[IF GOOD] That's great to hear! We really appreciate you trusting us. "
            "If you have a spare moment, a quick Google review helps us a lot — I can "
            "text you the link right now.\n\n"
            "[IF ISSUE] I'm sorry to hear that — I want to make sure we take care of "
            "that for you. Can you describe what you're noticing? "
            "[Listen, log the issue, and schedule a follow-up inspection at no charge "
            "if the issue is related to the service performed.]\n\n"
            "[CLOSE] Thanks again, {{customer_name}}. We appreciate you choosing "
            "{shop_name}. Don't hesitate to call us at {phone} if you need anything!"
        ),
    },

    "thirty_day_followup": {
        "sms": (
            "Hi {{customer_name}}, it's been a month since your {{service_type}} at "
            "{shop_name}. How's the vehicle running? Book your next visit: {phone}"
        ),
        "email": (
            "Subject: Checking In — How's Your {{vehicle}} Running? | {shop_name}\n\n"
            "Hi {{customer_name}},\n\n"
            "It's been about 30 days since your {{service_type}} here at {shop_name}, "
            "and we wanted to check in.\n\n"
            "How's your vehicle running? If you've noticed anything — a new sound, a "
            "dashboard light, or just a feeling that something's off — it's always "
            "better to catch it early. Give us a call at {phone} and we'll tell you "
            "if it's worth bringing in.\n\n"
            "Also, with {{season}} just around the corner, this is a great time to "
            "{{seasonal_tip}}. A quick preventive check now can save you from a "
            "breakdown later.\n\n"
            "Ready to schedule your next visit? Call {phone} or book online at "
            "{website} — we'll get you in quickly.\n\n"
            "Drive safe,\n"
            "{shop_name}\n"
            "{phone}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{agent_name}} calling from {shop_name}.\n\n"
            "[PURPOSE] It's been about a month since your {{service_type}}, and I "
            "just wanted to do a quick check-in.\n\n"
            "[PAUSE] How's the vehicle running? Anything we should know about?\n\n"
            "[IF GOOD] Glad to hear it! Just a heads-up — with {{season}} coming, "
            "it's worth thinking about {{seasonal_tip}}. Want me to get you scheduled "
            "for a quick look?\n\n"
            "[IF ISSUE] Thanks for letting me know. That's worth getting checked. "
            "I can get you in as early as {{next_available}} — does that work? "
            "[Book the appointment and confirm before ending the call.]\n\n"
            "[CLOSE] Thanks, {{customer_name}}. Don't hesitate to call us at {phone} "
            "anytime. Take care!"
        ),
    },

    "six_month_maintenance": {
        "sms": (
            "Hi {{customer_name}}, it's been 6 months since your {{service_type}} at "
            "{shop_name}. Time for a check-up! Call {phone} to book."
        ),
        "email": (
            "Subject: Your 6-Month Maintenance Reminder from {shop_name}\n\n"
            "Hi {{customer_name}},\n\n"
            "It's been about six months since your last visit to {shop_name} for "
            "your {{service_type}}, and based on your vehicle's maintenance schedule, "
            "it's a good time to think about:\n\n"
            "  - {{recommended_service_1}}\n"
            "  - {{recommended_service_2}}\n"
            "  - Multi-point inspection (we include this with every service)\n\n"
            "Staying on top of routine maintenance is the best way to avoid big "
            "repair bills down the road. Most of these services take under an hour "
            "and cost far less than fixing what happens when they're skipped.\n\n"
            "Not sure if your vehicle is due? Just call us at {phone} — give us "
            "your year, make, model, and mileage and we'll tell you exactly what's "
            "coming up at no charge.\n\n"
            "Ready to book? Call {phone} or visit {website}.\n\n"
            "Keeping you on the road,\n"
            "{shop_name}\n"
            "{phone}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{agent_name}} from {shop_name}.\n\n"
            "[PURPOSE] It's been about six months since your {{service_type}}, and "
            "I'm calling because based on your vehicle's schedule, you're likely due "
            "for some routine maintenance.\n\n"
            "[DETAILS] Specifically, we'd recommend {{recommended_service_1}} and "
            "{{recommended_service_2}}. These are the kinds of things that keep small "
            "issues from turning into expensive ones.\n\n"
            "[PAUSE] Would you like to get that scheduled? I've got availability as "
            "early as {{next_available}}.\n\n"
            "[IF YES] Great — let me get that booked for you. "
            "[Confirm date, time, and services. Read back the appointment details.]\n\n"
            "[IF NO] No worries at all. I'll send you a text with the details so you "
            "have it when you're ready. Just call us at {phone} whenever you'd like "
            "to come in.\n\n"
            "[CLOSE] Thanks, {{customer_name}}. Drive safe and we'll talk soon!"
        ),
    },
}

TOUCHPOINT_ORDER = [
    "booking_confirmation",
    "day_before_reminder",
    "day_of_notification",
    "post_service_thankyou",
    "thirty_day_followup",
    "six_month_maintenance",
]

ALL_CHANNELS = ["sms", "email", "phone_script"]


# ---------------------------------------------------------------------------
# Core generation
# ---------------------------------------------------------------------------

def apply_profile(content, profile):
    """Replace {profile_var} tokens with real values from the shop profile."""
    shop_name   = pval(profile, 'shop_name',  'Your Auto Shop')
    phone       = pval(profile, 'phone',       '(555) 555-5555')
    address     = pval(profile, 'address') or pval(profile, 'location', '123 Main St')
    owner_name  = pval(profile, 'owner_name', 'The Owner')
    website     = pval(profile, 'website',    'yourshop.com')
    location    = pval(profile, 'location',   'your area')
    review_link = profile.get('review_links', {}).get('google', '') or \
                  'https://g.page/r/[add-your-google-review-link]'

    replacements = {
        '{shop_name}':   shop_name,
        '{phone}':       phone,
        '{address}':     address,
        '{owner_name}':  owner_name,
        '{website}':     website,
        '{location}':    location,
        '{review_link}': review_link,
    }
    for token, value in replacements.items():
        content = content.replace(token, value)
    return content


def check_sms_length(content, touchpoint, profile):
    """
    Warn if an SMS template might exceed 160 chars after typical placeholder
    substitution.  We substitute a realistic worst-case for each placeholder.
    """
    sample = content
    sample_subs = {
        '{{customer_name}}': 'Christopher',
        '{{service_type}}':  'Transmission Flush',
        '{{date}}':          'Tuesday, Nov 12',
        '{{time}}':          '10:30 AM',
        '{{duration}}':      '90 min',
        '{{vehicle}}':       '2018 Ford F-150',
        '{{next_service}}':  'tire rotation',
        '{{next_date}}':     'March 2025',
        '{{season}}':        'winter',
        '{{seasonal_tip}}':  'check your battery and tire pressure',
        '{{next_available}}': 'Thursday',
    }
    for ph, val in sample_subs.items():
        sample = sample.replace(ph, val)
    if len(sample) > SMS_LIMIT:
        print(f"  ⚠️  SMS for '{touchpoint}' may exceed 160 chars "
              f"(~{len(sample)} chars with sample substitution). "
              f"Review and tighten if needed.", file=sys.stderr)


def generate_touchpoint(touchpoint, service_type, channels, profile, output_dir):
    """Generate all requested channels for one touchpoint."""
    templates = TEMPLATES.get(touchpoint)
    if not templates:
        print(f"ERROR: Unknown touchpoint '{touchpoint}'", file=sys.stderr)
        return []

    generated = []
    for channel in channels:
        if channel not in templates:
            print(f"  ⚠️  No '{channel}' template for '{touchpoint}'", file=sys.stderr)
            continue

        content = templates[channel]
        content = apply_profile(content, profile)
        content = content.replace('{{service_type}}', service_type)

        if channel == 'sms':
            check_sms_length(content, touchpoint, profile)

        filename = f"{touchpoint}_{channel}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(content)

        print(f"  ✅ output/appointments/{filename}")
        generated.append(filename)

    return generated


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate appointment reminder templates for every touchpoint."
    )
    parser.add_argument(
        '--touchpoint',
        required=True,
        choices=TOUCHPOINT_ORDER + ['all'],
        help="Which touchpoint to generate, or 'all' for all 6 touchpoints."
    )
    parser.add_argument(
        '--service_type',
        required=True,
        help="The service being performed (e.g. 'Oil Change', 'Brake Pad Replacement')."
    )
    parser.add_argument(
        '--channels',
        default='sms,email,phone_script',
        help="Comma-separated list of channels: sms,email,phone_script (default: all three)."
    )
    args = parser.parse_args()

    profile  = load_profile()
    channels = [c.strip() for c in args.channels.split(',')]

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)
    output_dir = os.path.abspath(OUTPUT_DIR)

    touchpoints = TOUCHPOINT_ORDER if args.touchpoint == 'all' else [args.touchpoint]

    print(f"\n🔧 Generating appointment reminders")
    print(f"   Service type : {args.service_type}")
    print(f"   Touchpoints  : {'all (6)' if args.touchpoint == 'all' else args.touchpoint}")
    print(f"   Channels     : {', '.join(channels)}")
    print(f"   Shop         : {pval(profile, 'shop_name', '[Not Set]')}")
    print()

    all_generated = []
    for tp in touchpoints:
        print(f"📋 {tp}")
        generated = generate_touchpoint(tp, args.service_type, channels, profile, output_dir)
        all_generated.extend(generated)

    print(f"\n{'─'*50}")
    print(f"✅ Done — {len(all_generated)} file(s) saved to output/appointments/")
    if args.touchpoint == 'all':
        print(f"   {len(touchpoints)} touchpoints × {len(channels)} channels = "
              f"{len(touchpoints) * len(channels)} total templates")


if __name__ == '__main__':
    main()
