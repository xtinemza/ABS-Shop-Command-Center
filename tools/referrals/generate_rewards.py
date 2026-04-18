#!/usr/bin/env python3
"""
Generate referral thank-you and reward messages for referrers and new customers.

Produces SMS, email, and an internal note for each referral reward.

Usage:
    python tools/referrals/generate_rewards.py \
        --referrer_name "John Smith" \
        --referrer_phone "(303) 555-4412" \
        --referred_name "Jane Doe" \
        --reward_type discount \
        --reward_value "$25 off your next service" \
        --referee_reward "$20 off your first visit"

    python tools/referrals/generate_rewards.py \
        --referrer_name "Maria Lopez" \
        --referred_name "Carlos Reyes" \
        --reward_type free_service \
        --reward_value "Free oil change" \
        --referee_reward "Free tire pressure check"
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
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'referrals')

SMS_LIMIT = 160


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if not os.path.exists(path):
        print("ERROR: shop_profile.json not found.", file=sys.stderr)
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def safe_filename(name):
    """Create a safe filename component from a name."""
    return name.replace(' ', '_').replace("'", '').replace('"', '').lower()


def trim_sms(text, limit=SMS_LIMIT):
    if len(text) <= limit:
        return text
    return text[:limit - 3].rsplit(' ', 1)[0] + '...'


def main():
    parser = argparse.ArgumentParser(description="Generate referral reward messages")
    parser.add_argument('--referrer_name', required=True,
                        help="Name of the person who made the referral")
    parser.add_argument('--referrer_phone', default='',
                        help="Referrer's phone number")
    parser.add_argument('--referred_name', required=True,
                        help="Name of the referred (new) customer")
    parser.add_argument('--referred_phone', default='',
                        help="Referred customer's phone number")
    parser.add_argument('--reward_type',
                        choices=['discount', 'free_service', 'gift_card', 'credit'],
                        default='discount',
                        help="Type of reward for the referrer")
    parser.add_argument('--reward_value', required=True,
                        help="Reward description, e.g. '$25 off your next service'")
    parser.add_argument('--referee_reward', default='',
                        help="Reward for the new customer (optional)")
    # Legacy compat
    parser.add_argument('--referrer', default='', help="[Legacy] Referrer name")
    parser.add_argument('--referee', default='', help="[Legacy] Referee name")
    parser.add_argument('--reward', default='', help="[Legacy] Reward value")
    parser.add_argument('--referred_by', default='', help="[Legacy] Referred by name")
    args = parser.parse_args()

    # Legacy field resolution
    if args.referrer and not args.referrer_name:
        args.referrer_name = args.referrer
    if args.referee and not args.referred_name:
        args.referred_name = args.referee
    if args.reward and not args.reward_value:
        args.reward_value = args.reward

    profile = load_profile()
    shop = profile.get('shop_name') or '[Shop Name]'
    phone = profile.get('phone') or '[Phone]'
    website = profile.get('website') or '[Website]'
    owner = profile.get('owner_name') or f"The Team at {shop}"
    review_link = (profile.get('review_links') or {}).get('google', '')

    today_str = datetime.now().strftime('%B %d, %Y')
    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

    referrer = args.referrer_name
    referred = args.referred_name
    reward = args.reward_value
    referee_reward = args.referee_reward

    referrer_slug = safe_filename(referrer)
    referred_slug = safe_filename(referred)

    generated = []

    # ── REFERRER THANK-YOU SMS ─────────────────────────────────────────────────
    referrer_sms_raw = (
        f"Hi {referrer}, thank you for sending {referred} our way! "
        f"You've earned: {reward}. "
        f"Mention this when you book — no expiration. "
        f"We appreciate you! {shop} {phone}"
    )
    referrer_sms = trim_sms(referrer_sms_raw)
    sms_len = len(referrer_sms)

    referrer_sms_file = os.path.join(
        os.path.abspath(OUTPUT_DIR), f"reward_referrer_{referrer_slug}_sms.txt"
    )
    with open(referrer_sms_file, 'w', encoding='utf-8') as f:
        f.write(f"SMS — REFERRER THANK-YOU: {referrer.upper()}\n")
        f.write("=" * 55 + "\n")
        f.write(f"TO: {referrer}")
        if args.referrer_phone:
            f.write(f"  |  {args.referrer_phone}")
        f.write("\n" + "─" * 55 + "\n\n")
        f.write(referrer_sms + "\n\n")
        f.write(f"({sms_len}/160 chars)\n")
    generated.append(('Referrer SMS', os.path.basename(referrer_sms_file)))

    # ── REFERRER THANK-YOU EMAIL ───────────────────────────────────────────────
    referrer_email_subject = f"You Earned a Reward! — {shop}"
    referrer_email_body = (
        f"Hi {referrer},\n\n"
        f"We wanted to say a genuine thank you — {referred} came in and "
        f"mentioned that you sent them our way. That means a lot to us.\n\n"
        f"Referrals are the best compliment a small business like ours can receive. "
        f"You trusted us enough to recommend us to someone you know, and we don't take "
        f"that lightly.\n\n"
        f"As a thank-you, you've earned:\n\n"
        f"    {reward}\n\n"
        f"Just mention this when you call to book your next appointment — it doesn't expire, "
        f"and no coupon is needed. We have it on file.\n\n"
    )

    if review_link:
        referrer_email_body += (
            f"If you ever have a moment, we'd appreciate a quick Google review. "
            f"It helps other drivers find a shop they can trust:\n"
            f"    {review_link}\n\n"
        )

    referrer_email_body += (
        f"Thank you again, {referrer.split()[0]}. We look forward to seeing you soon.\n\n"
        f"With appreciation,\n"
        f"{owner}\n"
        f"{shop}\n"
        f"{phone}"
    )

    referrer_email_file = os.path.join(
        os.path.abspath(OUTPUT_DIR), f"reward_referrer_{referrer_slug}_email.txt"
    )
    with open(referrer_email_file, 'w', encoding='utf-8') as f:
        f.write(f"EMAIL — REFERRER THANK-YOU: {referrer.upper()}\n")
        f.write("=" * 55 + "\n")
        f.write(f"TO: {referrer}")
        if args.referrer_phone:
            f.write(f"  |  {args.referrer_phone}")
        f.write("\n")
        f.write(f"SUBJECT: {referrer_email_subject}\n")
        f.write("─" * 55 + "\n\n")
        f.write(referrer_email_body + "\n")
    generated.append(('Referrer Email', os.path.basename(referrer_email_file)))

    # ── REFEREE WELCOME SMS ────────────────────────────────────────────────────
    if referee_reward:
        referee_sms_raw = (
            f"Welcome to {shop}, {referred}! "
            f"{referrer} sent you our way — and we're glad they did. "
            f"As a welcome gift: {referee_reward}. "
            f"Mention this when you book. {phone}"
        )
    else:
        referee_sms_raw = (
            f"Welcome to {shop}, {referred}! "
            f"{referrer} recommended us — we hope to earn your trust too. "
            f"Call {phone} to book your first appointment."
        )

    referee_sms = trim_sms(referee_sms_raw)
    referee_sms_len = len(referee_sms)

    referee_sms_file = os.path.join(
        os.path.abspath(OUTPUT_DIR), f"reward_referee_{referred_slug}_sms.txt"
    )
    with open(referee_sms_file, 'w', encoding='utf-8') as f:
        f.write(f"SMS — NEW CUSTOMER WELCOME: {referred.upper()}\n")
        f.write("=" * 55 + "\n")
        f.write(f"TO: {referred}")
        if args.referred_phone:
            f.write(f"  |  {args.referred_phone}")
        f.write("\n" + "─" * 55 + "\n\n")
        f.write(referee_sms + "\n\n")
        f.write(f"({referee_sms_len}/160 chars)\n")
    generated.append(('Referee SMS', os.path.basename(referee_sms_file)))

    # ── REFEREE WELCOME EMAIL ──────────────────────────────────────────────────
    referee_email_subject = f"Welcome to {shop} — A Note from {referrer}"
    referee_email_body = (
        f"Hi {referred},\n\n"
        f"{referrer} recommended {shop} to you, and we're glad they did.\n\n"
        f"We're an independent auto repair shop, and our reputation is built entirely "
        f"on customers like {referrer} who trust us enough to send people they care about "
        f"our way. We don't take that lightly.\n\n"
    )

    if referee_reward:
        referee_email_body += (
            f"As a welcome gift from us:\n\n"
            f"    {referee_reward}\n\n"
            f"Just mention {referrer}'s name or this email when you call to book. "
            f"No expiration.\n\n"
        )

    referee_email_body += (
        f"We look forward to meeting you and earning your trust.\n\n"
        f"{owner}\n"
        f"{shop}\n"
        f"{phone}"
    )

    if website:
        referee_email_body += f"\n{website}"

    referee_email_file = os.path.join(
        os.path.abspath(OUTPUT_DIR), f"reward_referee_{referred_slug}_email.txt"
    )
    with open(referee_email_file, 'w', encoding='utf-8') as f:
        f.write(f"EMAIL — NEW CUSTOMER WELCOME: {referred.upper()}\n")
        f.write("=" * 55 + "\n")
        f.write(f"TO: {referred}")
        if args.referred_phone:
            f.write(f"  |  {args.referred_phone}")
        f.write("\n")
        f.write(f"SUBJECT: {referee_email_subject}\n")
        f.write("─" * 55 + "\n\n")
        f.write(referee_email_body + "\n")
    generated.append(('Referee Email', os.path.basename(referee_email_file)))

    # ── INTERNAL NOTE ─────────────────────────────────────────────────────────
    internal_note = (
        f"INTERNAL REFERRAL NOTE\n"
        f"{'=' * 55}\n"
        f"Date Generated: {today_str}\n"
        f"{'─' * 55}\n\n"
        f"REFERRER: {referrer}\n"
    )
    if args.referrer_phone:
        internal_note += f"  Phone: {args.referrer_phone}\n"
    internal_note += (
        f"  Reward Earned: {reward}\n"
        f"  Reward Type: {args.reward_type}\n"
        f"  Status: PENDING — mark as issued when applied\n\n"
        f"REFERRED CUSTOMER: {referred}\n"
    )
    if args.referred_phone:
        internal_note += f"  Phone: {args.referred_phone}\n"
    if referee_reward:
        internal_note += f"  Welcome Reward: {referee_reward}\n"

    internal_note += (
        f"\nACTION NEEDED:\n"
        f"  1. Apply {referrer}'s reward ({reward}) at next visit\n"
        f"  2. Note it in the work order or customer file\n"
        f"  3. Mark reward as issued in referral tracker:\n"
        f"     python tools/referrals/track_referrals.py \\\n"
        f"         --action update --referral_id [R-XXX] \\\n"
        f"         --reward_issued yes \\\n"
        f"         --notes \"Applied {reward} on [date]\"\n"
    )

    internal_file = os.path.join(
        os.path.abspath(OUTPUT_DIR),
        f"internal_note_{referrer_slug}_referred_{referred_slug}.txt"
    )
    with open(internal_file, 'w', encoding='utf-8') as f:
        f.write(internal_note)
    generated.append(('Internal Note', os.path.basename(internal_file)))

    # ── Summary Output ─────────────────────────────────────────────────────────
    print(f"\n{'=' * 62}")
    print(f"  REFERRAL REWARD MESSAGES GENERATED")
    print(f"{'=' * 62}")
    print(f"  Referrer : {referrer}", end='')
    if args.referrer_phone:
        print(f"  |  {args.referrer_phone}", end='')
    print()
    print(f"  Referred : {referred}", end='')
    if args.referred_phone:
        print(f"  |  {args.referred_phone}", end='')
    print()
    print(f"  Reward   : {reward}")
    if referee_reward:
        print(f"  New Cust : {referee_reward}")
    print(f"{'─' * 62}")
    for label, fname in generated:
        print(f"  {label:<20}  output/referrals/{fname}")
    print(f"{'─' * 62}")
    print(f"\n  SMS PREVIEW (referrer)  ({sms_len}/160 chars)")
    print(f"  {'─' * 56}")
    print(f"  {referrer_sms}")
    print(f"\n{'=' * 62}\n")


if __name__ == '__main__':
    main()
