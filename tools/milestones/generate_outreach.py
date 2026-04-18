#!/usr/bin/env python3
"""
Generate personalized customer milestone outreach messages.

Produces SMS, email, and (for major milestones) a phone script.
All messages use the shop's real name, phone, and owner details.

Usage:
    python tools/milestones/generate_outreach.py \
        --milestone_type anniversary \
        --customer_name "Maria Gonzalez" \
        --customer_phone "(303) 555-7821" \
        --milestone_value "1 year" \
        --vehicle "2019 Toyota Camry" \
        --last_service "2025-03-15" \
        --offer "10% off your next service"

    python tools/milestones/generate_outreach.py \
        --milestone_type visit_count \
        --customer_name "Tom Bradley" \
        --milestone_value "10th visit" \
        --vehicle "2017 Ford F-150"

    python tools/milestones/generate_outreach.py \
        --milestone_type mileage \
        --customer_name "Kevin Park" \
        --milestone_value "100,000 miles" \
        --vehicle "2015 Subaru Outback" \
        --offer "Free full inspection with next oil change"
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
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'milestones')

SMS_LIMIT = 160

# Milestones that always get a phone script (major relationship moments)
MAJOR_MILESTONES = {
    ('anniversary', '1 year'),
    ('anniversary', '5 years'),
    ('visit_count', '10th visit'),
    ('visit_count', '25th visit'),
    ('mileage', '100,000 miles'),
    ('mileage', '200,000 miles'),
}

# Anniversary-specific recommended services by milestone year
ANNIVERSARY_SERVICES = {
    '1 year': 'full multi-point inspection',
    '2 years': 'fluid check and tire rotation',
    '5 years': 'comprehensive vehicle health check',
}

# Mileage service recommendations
MILEAGE_SERVICES = {
    '50,000': 'transmission service and spark plugs if not done recently',
    '50000': 'transmission service and spark plugs if not done recently',
    '100,000': 'timing belt/chain check, coolant flush, and comprehensive inspection',
    '100000': 'timing belt/chain check, coolant flush, and comprehensive inspection',
    '150,000': 'thorough inspection of all major systems — this is a well-traveled vehicle',
    '150000': 'thorough inspection of all major systems — this is a well-traveled vehicle',
    '200,000': 'full systems review — vehicles at this mileage deserve extra care',
    '200000': 'full systems review — vehicles at this mileage deserve extra care',
}


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if not os.path.exists(path):
        print("ERROR: shop_profile.json not found.", file=sys.stderr)
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def safe_filename(name):
    return name.replace(' ', '_').replace("'", '').replace('"', '').replace(',', '').lower()


def first_name(full_name):
    return full_name.split()[0] if full_name else 'there'


def trim_sms(text, limit=SMS_LIMIT):
    if len(text) <= limit:
        return text, True
    trimmed = text[:limit - 3].rsplit(' ', 1)[0] + '...'
    return trimmed, False


def format_last_service(last_service_str):
    if not last_service_str:
        return None
    try:
        d = datetime.strptime(last_service_str, '%Y-%m-%d')
        return d.strftime('%B %d, %Y')
    except ValueError:
        return last_service_str


def offer_section_text(offer):
    if not offer:
        return ''
    return f"\nAs a thank-you, here's something for you:\n\n    {offer}\n\nJust mention this when you book — no expiration.\n"


def offer_sms_fragment(offer):
    if not offer:
        return ''
    return f" As a thank-you: {offer}."


def mileage_key(milestone_value):
    """Extract numeric mileage key for service lookups."""
    cleaned = milestone_value.replace(',', '').replace(' miles', '').strip()
    return cleaned


def is_major(milestone_type, milestone_value):
    mv_lower = milestone_value.lower().strip()
    return (milestone_type, mv_lower) in MAJOR_MILESTONES


def generate_anniversary(profile, customer_name, customer_phone, milestone_value,
                          vehicle, last_service_fmt, offer, shop, phone, website, owner, review_link):
    fname = first_name(customer_name)
    mv = milestone_value.strip()

    # Tone varies by length of relationship
    if '5' in mv:
        warmth = "Five years. That's not just a customer — that's family."
        descriptor = "VIP"
    elif '2' in mv:
        warmth = "Two years since your first visit — and we're grateful for every one of them."
        descriptor = "loyal"
    else:
        warmth = "It's been a year since your first visit to us — and we wanted to take a moment to say thank you."
        descriptor = "valued"

    service_rec = ANNIVERSARY_SERVICES.get(mv.lower(), 'a quick vehicle checkup')
    vehicle_mention = f"your {vehicle}" if vehicle else "your vehicle"

    # SMS
    sms_raw = (
        f"Hi {fname}! It's been {mv} since your first visit to {shop}. "
        f"Thank you for trusting us with {vehicle_mention}."
        f"{offer_sms_fragment(offer)} Call {phone} to book!"
    )
    sms_text, sms_fits = trim_sms(sms_raw)

    # Email
    email_subject = f"Happy {mv.title()} Anniversary, {fname}! — {shop}"
    email_body = (
        f"Hi {fname},\n\n"
        f"{warmth}\n\n"
        f"You're a {descriptor} part of the {shop} family, and we genuinely appreciate "
        f"the trust you've placed in us with {vehicle_mention}. You could have gone "
        f"anywhere — and you chose to come back to us. That means everything to a "
        f"small business like ours.\n"
        f"{offer_section_text(offer)}"
    )
    if last_service_fmt:
        email_body += f"\nYour last visit was {last_service_fmt}. "
        email_body += f"Coming up, we'd recommend scheduling {service_rec}.\n"

    if review_link:
        email_body += (
            f"\nIf you ever have a moment, a Google review would mean the world to us:\n"
            f"    {review_link}\n"
        )

    email_body += (
        f"\nHere's to many more miles together.\n\n"
        f"With appreciation,\n"
        f"{owner}\n"
        f"{shop}\n"
        f"{phone}"
    )
    if website:
        email_body += f"\n{website}"

    # Phone script (for major milestones)
    phone_script = None
    if is_major('anniversary', mv):
        phone_script = (
            f"PHONE SCRIPT — {mv.upper()} ANNIVERSARY CALL: {customer_name.upper()}\n"
            f"{'=' * 58}\n"
            f"INTERNAL USE — Not for the customer to read\n"
            f"{'─' * 58}\n\n"
            f"OPENING:\n"
            f"  \"Hi, is this {fname}? Great — this is {owner} calling from {shop}. "
            f"I hope I'm catching you at a good time?\"\n"
            f"  [Pause for response]\n\n"
            f"  \"I'm actually calling because I noticed it's been {mv} since your first "
            f"visit with us, and I just wanted to personally say thank you. We really "
            f"appreciate your loyalty.\"\n\n"
        )
        if offer:
            phone_script += (
                f"OFFER:\n"
                f"  \"As a thank-you, I'd like to offer you {offer} on your next visit. "
                f"No strings, no coupon needed — I'll have it noted in your file.\"\n\n"
            )
        if last_service_fmt:
            phone_script += (
                f"SERVICE NOTE (optional to mention):\n"
                f"  \"Your last visit was {last_service_fmt}. "
                f"Coming up, it might be worth scheduling {service_rec} — "
                f"I can help you book that today if you'd like.\"\n\n"
            )
        phone_script += (
            f"CLOSE:\n"
            f"  \"Thank you again, {fname}. We look forward to seeing you soon. "
            f"Is there anything we can help you with?\"\n"
            f"  [Handle any questions, then wrap up warmly]\n\n"
            f"{'─' * 58}\n"
            f"Shop: {shop}  |  Phone: {phone}\n"
        )

    return sms_text, sms_fits, email_subject, email_body, phone_script


def generate_visit_count(profile, customer_name, customer_phone, milestone_value,
                          vehicle, last_service_fmt, offer, shop, phone, website, owner, review_link):
    fname = first_name(customer_name)
    mv = milestone_value.strip()

    vehicle_mention = f"your {vehicle}" if vehicle else "your vehicle"

    if '25' in mv:
        tone_open = f"Twenty-five visits. {fname}, that is seriously impressive loyalty."
        descriptor = "legend"
        relationship = "you're practically part of the team at this point"
    elif '10' in mv:
        tone_open = f"Ten visits. That's a real relationship, and we don't take it for granted."
        descriptor = "valued regular"
        relationship = "you've trusted us again and again, and that means everything"
    else:
        tone_open = f"Your 5th visit — that makes you a regular in our book."
        descriptor = "regular"
        relationship = "we really appreciate you coming back"

    # SMS
    sms_raw = (
        f"Hi {fname}! This is your {mv} at {shop}. "
        f"Thank you — {relationship}."
        f"{offer_sms_fragment(offer)} Call {phone}!"
    )
    sms_text, sms_fits = trim_sms(sms_raw)

    # Email
    email_subject = f"Your {mv.title()} at {shop} — Thank You!"
    email_body = (
        f"Hi {fname},\n\n"
        f"{tone_open}\n\n"
        f"You chose us for {vehicle_mention}, and you keep coming back. "
        f"As a {descriptor}, you've earned more than our thanks — you've helped us "
        f"build the kind of shop we set out to be.\n"
        f"{offer_section_text(offer)}"
    )

    if last_service_fmt:
        email_body += f"\nYour last visit was {last_service_fmt}. We look forward to the next one.\n"

    if review_link:
        email_body += (
            f"\nIf you'd like to help other drivers find a shop they can trust, "
            f"a quick Google review goes a long way:\n"
            f"    {review_link}\n"
        )

    email_body += (
        f"\nThank you for being part of our story.\n\n"
        f"{owner}\n"
        f"{shop}\n"
        f"{phone}"
    )
    if website:
        email_body += f"\n{website}"

    # Phone script
    phone_script = None
    if is_major('visit_count', mv):
        phone_script = (
            f"PHONE SCRIPT — {mv.upper()} MILESTONE CALL: {customer_name.upper()}\n"
            f"{'=' * 58}\n"
            f"INTERNAL USE — Not for the customer to read\n"
            f"{'─' * 58}\n\n"
            f"OPENING:\n"
            f"  \"Hi {fname}, this is {owner} from {shop}. Hope you're doing well! "
            f"I have a quick reason for calling — do you have a moment?\"\n"
            f"  [Pause]\n\n"
            f"  \"I noticed this was your {mv} with us, and I just wanted to personally "
            f"say thank you. {tone_open.split('.')[0]}.\"\n\n"
        )
        if offer:
            phone_script += (
                f"OFFER:\n"
                f"  \"We'd like to show our appreciation — {offer}. "
                f"It's already noted in your file for your next visit.\"\n\n"
            )
        phone_script += (
            f"CLOSE:\n"
            f"  \"We're really glad you chose to stick with us, {fname}. "
            f"Is there anything coming up we can help you with?\"\n\n"
            f"{'─' * 58}\n"
            f"Shop: {shop}  |  Phone: {phone}\n"
        )

    return sms_text, sms_fits, email_subject, email_body, phone_script


def generate_mileage(profile, customer_name, customer_phone, milestone_value,
                      vehicle, last_service_fmt, offer, shop, phone, website, owner, review_link):
    fname = first_name(customer_name)
    mv = milestone_value.strip()
    mk = mileage_key(mv)

    vehicle_mention = vehicle if vehicle else "your vehicle"
    service_rec = MILEAGE_SERVICES.get(mk, 'a comprehensive inspection')

    if '200' in mk:
        tone_intro = f"200,000 miles on {vehicle_mention} — that is a remarkable achievement."
        tone_close = "A vehicle that reaches this milestone deserves expert care."
    elif '100' in mk:
        tone_intro = f"100,000 miles is a major milestone, and {vehicle_mention} has earned every one of them."
        tone_close = "At this mileage, the right maintenance keeps you on the road for years to come."
    else:
        tone_intro = f"50,000 miles on {vehicle_mention} — right on schedule for some important maintenance."
        tone_close = "The 50,000-mile mark is a key maintenance checkpoint."

    # SMS
    sms_raw = (
        f"Hi {fname}! Congrats on {mv} with {vehicle_mention}. "
        f"{shop} can help with the {mk.replace('000', 'k')}-mile service checkpoints."
        f"{offer_sms_fragment(offer)} Call {phone}."
    )
    sms_text, sms_fits = trim_sms(sms_raw)

    # Email
    email_subject = f"{mv} on {vehicle_mention} — Congrats, and Here's What's Next"
    email_body = (
        f"Hi {fname},\n\n"
        f"{tone_intro}\n\n"
        f"{tone_close} Here's what we recommend at this milestone:\n\n"
        f"    {service_rec.capitalize()}\n\n"
        f"We've been taking care of {vehicle_mention}, and we want to keep it that way. "
        f"A quick appointment lets us do a thorough check and flag anything that needs "
        f"attention before it becomes a bigger issue.\n"
        f"{offer_section_text(offer)}"
    )

    if last_service_fmt:
        email_body += f"\nYour last visit was {last_service_fmt}. Ready to schedule the next one?\n"

    email_body += (
        f"\nCall us at {phone} or visit {website} to book.\n\n"
        f"Keep those miles coming,\n"
        f"{owner}\n"
        f"{shop}\n"
        f"{phone}"
    )

    # Phone script for major mileage milestones
    phone_script = None
    if is_major('mileage', mv):
        phone_script = (
            f"PHONE SCRIPT — {mv.upper()} MILESTONE CALL: {customer_name.upper()}\n"
            f"{'=' * 58}\n"
            f"INTERNAL USE — Not for the customer to read\n"
            f"{'─' * 58}\n\n"
            f"OPENING:\n"
            f"  \"Hi {fname}, this is {owner} at {shop}. I'm calling because I saw "
            f"that {vehicle_mention} just hit {mv} — that's a big deal, and "
            f"I wanted to personally reach out.\"\n\n"
            f"SERVICE NOTE:\n"
            f"  \"At this mileage, we typically recommend {service_rec}. "
            f"I'd love to get you in and do a thorough check so we know exactly "
            f"where everything stands.\"\n\n"
        )
        if offer:
            phone_script += (
                f"OFFER:\n"
                f"  \"As a thank-you for your continued trust, I'd like to offer you "
                f"{offer} on that service.\"\n\n"
            )
        phone_script += (
            f"CLOSE:\n"
            f"  \"Can we get you scheduled? Even a quick look would give us both "
            f"peace of mind.\"\n\n"
            f"{'─' * 58}\n"
            f"Shop: {shop}  |  Phone: {phone}\n"
        )

    return sms_text, sms_fits, email_subject, email_body, phone_script


def main():
    parser = argparse.ArgumentParser(description="Generate customer milestone outreach")
    parser.add_argument('--milestone_type', required=True,
                        choices=['anniversary', 'visit_count', 'mileage',
                                 '1_year_anniversary', '2_year_anniversary', '5_year_anniversary',
                                 '5th_visit', '10th_visit', 'birthday'],
                        help="Type of milestone")
    parser.add_argument('--customer_name', required=True, help="Customer's full name")
    parser.add_argument('--customer_phone', default='', help="Customer's phone number")
    parser.add_argument('--milestone_value', default='',
                        help="Milestone description, e.g. '1 year', '10th visit', '100,000 miles'")
    parser.add_argument('--vehicle', default='', help="Year Make Model")
    parser.add_argument('--last_service', default='', help="Last service date YYYY-MM-DD")
    parser.add_argument('--offer', default='', help="Offer or reward to include (optional)")
    # Legacy milestone args
    parser.add_argument('--milestone', default='', help="[Legacy] milestone type string")
    parser.add_argument('--channels', default='sms,email', help="[Legacy] channels")
    args = parser.parse_args()

    # Normalize legacy milestone types to new format
    legacy_map = {
        '1_year_anniversary': ('anniversary', '1 year'),
        '2_year_anniversary': ('anniversary', '2 years'),
        '5_year_anniversary': ('anniversary', '5 years'),
        '5th_visit': ('visit_count', '5th visit'),
        '10th_visit': ('visit_count', '10th visit'),
        'birthday': ('anniversary', 'birthday'),
    }
    if args.milestone_type in legacy_map:
        args.milestone_type, mv_default = legacy_map[args.milestone_type]
        if not args.milestone_value:
            args.milestone_value = mv_default
    elif args.milestone and not args.milestone_value:
        args.milestone_value = args.milestone.replace('_', ' ')

    if not args.milestone_value:
        print("ERROR: --milestone_value is required (e.g. '1 year', '10th visit', '100,000 miles')",
              file=sys.stderr)
        sys.exit(1)

    profile = load_profile()
    shop = profile.get('shop_name') or '[Shop Name]'
    phone = profile.get('phone') or '[Phone]'
    website = profile.get('website') or ''
    owner = profile.get('owner_name') or f"The Team at {shop}"
    review_link = (profile.get('review_links') or {}).get('google', '')

    last_service_fmt = format_last_service(args.last_service)
    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

    customer_slug = safe_filename(args.customer_name)
    type_slug = args.milestone_type
    mv_slug = safe_filename(args.milestone_value)

    # ── Generate content based on milestone type ──────────────────────────────
    if args.milestone_type == 'anniversary':
        sms_text, sms_fits, email_subject, email_body, phone_script = generate_anniversary(
            profile, args.customer_name, args.customer_phone, args.milestone_value,
            args.vehicle, last_service_fmt, args.offer,
            shop, phone, website, owner, review_link
        )
    elif args.milestone_type == 'visit_count':
        sms_text, sms_fits, email_subject, email_body, phone_script = generate_visit_count(
            profile, args.customer_name, args.customer_phone, args.milestone_value,
            args.vehicle, last_service_fmt, args.offer,
            shop, phone, website, owner, review_link
        )
    elif args.milestone_type == 'mileage':
        sms_text, sms_fits, email_subject, email_body, phone_script = generate_mileage(
            profile, args.customer_name, args.customer_phone, args.milestone_value,
            args.vehicle, last_service_fmt, args.offer,
            shop, phone, website, owner, review_link
        )
    else:
        print(f"ERROR: Unknown milestone_type '{args.milestone_type}'", file=sys.stderr)
        sys.exit(1)

    generated = []
    sms_len = len(sms_text)

    # ── Write SMS ──────────────────────────────────────────────────────────────
    sms_file = os.path.join(
        os.path.abspath(OUTPUT_DIR),
        f"{type_slug}_{mv_slug}_{customer_slug}_sms.txt"
    )
    with open(sms_file, 'w', encoding='utf-8') as f:
        f.write(f"SMS — {args.milestone_value.upper()} MILESTONE: {args.customer_name.upper()}\n")
        f.write("=" * 58 + "\n")
        f.write(f"TO: {args.customer_name}")
        if args.customer_phone:
            f.write(f"  |  {args.customer_phone}")
        f.write("\n" + "─" * 58 + "\n\n")
        f.write(sms_text + "\n\n")
        f.write(f"({sms_len}/160 chars)")
        if not sms_fits:
            f.write(" [trimmed to fit]")
        f.write("\n")
    generated.append(('SMS', os.path.basename(sms_file)))

    # ── Write Email ────────────────────────────────────────────────────────────
    email_file = os.path.join(
        os.path.abspath(OUTPUT_DIR),
        f"{type_slug}_{mv_slug}_{customer_slug}_email.txt"
    )
    with open(email_file, 'w', encoding='utf-8') as f:
        f.write(f"EMAIL — {args.milestone_value.upper()} MILESTONE: {args.customer_name.upper()}\n")
        f.write("=" * 58 + "\n")
        f.write(f"TO: {args.customer_name}")
        if args.customer_phone:
            f.write(f"  |  {args.customer_phone}")
        f.write("\n")
        f.write(f"SUBJECT: {email_subject}\n")
        f.write("─" * 58 + "\n\n")
        f.write(email_body + "\n")
    generated.append(('Email', os.path.basename(email_file)))

    # ── Write Phone Script (if generated) ─────────────────────────────────────
    if phone_script:
        ps_file = os.path.join(
            os.path.abspath(OUTPUT_DIR),
            f"{type_slug}_{mv_slug}_{customer_slug}_phone_script.txt"
        )
        with open(ps_file, 'w', encoding='utf-8') as f:
            f.write(phone_script)
        generated.append(('Phone Script', os.path.basename(ps_file)))

    # ── Summary Output ─────────────────────────────────────────────────────────
    print(f"\n{'=' * 62}")
    print(f"  MILESTONE OUTREACH GENERATED")
    print(f"{'=' * 62}")
    print(f"  Customer  : {args.customer_name}", end='')
    if args.customer_phone:
        print(f"  |  {args.customer_phone}", end='')
    print()
    print(f"  Milestone : {args.milestone_value.title()} ({args.milestone_type})")
    if args.vehicle:
        print(f"  Vehicle   : {args.vehicle}")
    if args.offer:
        print(f"  Offer     : {args.offer}")
    print(f"{'─' * 62}")
    for label, fname in generated:
        print(f"  {label:<20}  output/milestones/{fname}")
    print(f"{'─' * 62}")
    print(f"\n  SMS PREVIEW  ({sms_len}/160 chars)")
    print(f"  {'─' * 56}")
    print(f"  {sms_text}")
    print(f"\n{'=' * 62}\n")


if __name__ == '__main__':
    main()
