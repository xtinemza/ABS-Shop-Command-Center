#!/usr/bin/env python3
"""
Track customer referrals and generate referral program reports.

Usage:
    python tools/referrals/track_referrals.py --action add \
        --referrer_name "John Smith" --referrer_phone "(303) 555-4412" \
        --referred_name "Jane Doe" --referred_phone "(303) 555-7821" \
        --service_date "2025-04-10" --service "Brake Repair" \
        --notes "Jane mentioned John sent her"

    python tools/referrals/track_referrals.py --action list
    python tools/referrals/track_referrals.py --action list --filter pending_rewards
    python tools/referrals/track_referrals.py --action update --referral_id R-001 \
        --reward_issued yes --notes "Gave credit on 4/15 visit"
    python tools/referrals/track_referrals.py --action report

    # Legacy compatibility
    python tools/referrals/track_referrals.py --action log \
        --referrer "John Smith" --referee "Jane Doe" \
        --service "Brakes" --date "2025-04-10"
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
from collections import Counter, defaultdict
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'referrals.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'referrals')
PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_referrals():
    p = os.path.abspath(DATA_FILE)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_referrals(data):
    p = os.path.abspath(DATA_FILE)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Track customer referrals")
    parser.add_argument('--action', required=True,
                        choices=['add', 'log', 'update', 'list', 'report', 'check_rewards'],
                        help="Action to perform")
    # New field names
    parser.add_argument('--referrer_name', default='', help="Referrer's name")
    parser.add_argument('--referrer_phone', default='', help="Referrer's phone number")
    parser.add_argument('--referred_name', default='', help="Referred customer's name")
    parser.add_argument('--referred_phone', default='', help="Referred customer's phone")
    parser.add_argument('--service_date', default='', help="Date of service YYYY-MM-DD")
    parser.add_argument('--service', default='', help="Service performed")
    parser.add_argument('--reward_issued', default='',
                        help="Reward issued? yes/no")
    parser.add_argument('--notes', default='', help="Additional notes")
    parser.add_argument('--referral_id', default='', help="Referral ID for updates")
    parser.add_argument('--filter', default='', dest='filter_by',
                        help="Filter for list: pending_rewards")
    # Legacy field names
    parser.add_argument('--referrer', default='', help="[Legacy] Referrer name")
    parser.add_argument('--referee', default='', help="[Legacy] Referee name")
    parser.add_argument('--date', default='', help="[Legacy] Service date")
    parser.add_argument('--rewarded', action='store_true', help="[Legacy] Reward issued flag")
    args = parser.parse_args()

    # Normalize legacy field names
    if args.referrer and not args.referrer_name:
        args.referrer_name = args.referrer
    if args.referee and not args.referred_name:
        args.referred_name = args.referee
    if args.date and not args.service_date:
        args.service_date = args.date
    # Normalize action alias
    if args.action == 'log':
        args.action = 'add'
    if args.action == 'check_rewards':
        args.action = 'list'
        args.filter_by = 'pending_rewards'

    referrals = load_referrals()
    today = datetime.now().strftime('%Y-%m-%d')
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')

    # ── ADD REFERRAL ──────────────────────────────────────────────────────────
    if args.action == 'add':
        if not args.referrer_name:
            print("ERROR: --referrer_name is required", file=sys.stderr)
            sys.exit(1)
        if not args.referred_name:
            print("ERROR: --referred_name is required", file=sys.stderr)
            sys.exit(1)

        # Duplicate check
        for r in referrals:
            if (r.get('referrer_name', '').lower() == args.referrer_name.lower() and
                    r.get('referred_name', '').lower() == args.referred_name.lower()):
                print(f"\n  WARNING: A referral from {args.referrer_name} to "
                      f"{args.referred_name} already exists (ID: {r['id']}).")
                print(f"  If this is a different visit, add --notes to distinguish it.")
                print(f"  Proceeding with new entry...\n")
                break

        referral_id = f"R-{len(referrals) + 1:03d}"
        reward_issued = args.rewarded or (args.reward_issued.lower() in ('yes', 'true', '1'))

        entry = {
            "id": referral_id,
            "referrer_name": args.referrer_name,
            "referrer_phone": args.referrer_phone,
            "referred_name": args.referred_name,
            "referred_phone": args.referred_phone,
            "service_date": args.service_date or today,
            "service": args.service,
            "reward_issued": reward_issued,
            "notes": args.notes,
            "logged_at": now_str
        }

        referrals.append(entry)
        save_referrals(referrals)

        missing_contact = []
        if not args.referrer_phone:
            missing_contact.append(f"{args.referrer_name}'s phone")
        if not args.referred_phone:
            missing_contact.append(f"{args.referred_name}'s phone")

        print(f"\n{'=' * 58}")
        print(f"  REFERRAL LOGGED — {referral_id}")
        print(f"{'=' * 58}")
        print(f"  Referrer : {args.referrer_name}", end='')
        if args.referrer_phone:
            print(f"  |  {args.referrer_phone}", end='')
        print()
        print(f"  Referred : {args.referred_name}", end='')
        if args.referred_phone:
            print(f"  |  {args.referred_phone}", end='')
        print()
        print(f"  Service  : {args.service or '(not specified)'}")
        print(f"  Date     : {entry['service_date']}")
        print(f"  Reward   : {'Issued' if reward_issued else 'Pending'}")
        if args.notes:
            print(f"  Notes    : {args.notes}")

        if missing_contact:
            print(f"\n  NOTE: Missing contact info for: {', '.join(missing_contact)}")
            print(f"  Reward messages cannot be sent without phone numbers.")

        print(f"\n  Next: Generate reward messages with:")
        print(f"  python tools/referrals/generate_rewards.py "
              f"--referrer_name \"{args.referrer_name}\" ...")
        print(f"{'=' * 58}\n")

    # ── UPDATE REFERRAL ───────────────────────────────────────────────────────
    elif args.action == 'update':
        if not args.referral_id:
            print("ERROR: --referral_id required for update", file=sys.stderr)
            sys.exit(1)

        found = False
        for r in referrals:
            if r['id'].upper() == args.referral_id.upper():
                found = True
                if args.reward_issued:
                    r['reward_issued'] = args.reward_issued.lower() in ('yes', 'true', '1')
                if args.notes:
                    existing = r.get('notes', '')
                    r['notes'] = (existing + ' | ' + args.notes).strip(' |')
                r['updated_at'] = now_str
                save_referrals(referrals)

                print(f"\n  Referral {r['id']} updated.")
                print(f"  {r['referrer_name']} → {r['referred_name']}")
                print(f"  Reward Issued: {'Yes' if r['reward_issued'] else 'No'}")
                if r['notes']:
                    print(f"  Notes: {r['notes']}")
                break

        if not found:
            print(f"ERROR: Referral ID '{args.referral_id}' not found.", file=sys.stderr)
            sys.exit(1)

    # ── LIST REFERRALS ────────────────────────────────────────────────────────
    elif args.action == 'list':
        if not referrals:
            print("No referrals logged.")
            print("Log a referral with: --action add")
            return

        filter_by = args.filter_by.lower()
        if filter_by == 'pending_rewards':
            display = [r for r in referrals if not r.get('reward_issued')]
            label = "PENDING REWARDS"
        else:
            display = referrals
            label = f"ALL REFERRALS ({len(referrals)})"

        pending_count = sum(1 for r in referrals if not r.get('reward_issued'))
        issued_count = sum(1 for r in referrals if r.get('reward_issued'))

        print(f"\n{'=' * 65}")
        print(f"  REFERRAL LOG — {label}")
        print(f"{'=' * 65}")
        print(f"  Total: {len(referrals)}  |  "
              f"Rewards Issued: {issued_count}  |  Pending: {pending_count}")
        print(f"{'─' * 65}")

        if not display:
            if filter_by == 'pending_rewards':
                print("  All referrers have received their rewards!")
            else:
                print("  No referrals to display.")
        else:
            for r in sorted(display, key=lambda x: x.get('service_date', ''), reverse=True):
                reward_status = "Reward Issued" if r.get('reward_issued') else "REWARD PENDING"
                print(f"\n  {r['id']}  |  {r.get('service_date', 'N/A')}  |  [{reward_status}]")
                print(f"  Referrer : {r['referrer_name']}", end='')
                if r.get('referrer_phone'):
                    print(f"  |  {r['referrer_phone']}", end='')
                print()
                print(f"  Referred : {r['referred_name']}", end='')
                if r.get('referred_phone'):
                    print(f"  |  {r['referred_phone']}", end='')
                print()
                if r.get('service'):
                    print(f"  Service  : {r['service']}")
                if r.get('notes'):
                    print(f"  Notes    : {r['notes']}")

        if pending_count > 0 and filter_by != 'pending_rewards':
            print(f"\n  {pending_count} referral(s) have rewards not yet issued.")
            print(f"  Run --action list --filter pending_rewards to see them.")

        print(f"\n{'=' * 65}\n")

    # ── REPORT ─────────────────────────────────────────────────────────────────
    elif args.action == 'report':
        profile = load_profile()
        shop_name = profile.get('shop_name') or 'Your Shop'
        os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

        if not referrals:
            print("No referral data. Log referrals first.")
            return

        total = len(referrals)
        issued = sum(1 for r in referrals if r.get('reward_issued'))
        pending = total - issued

        # Count by referrer
        referrer_counts = Counter(r['referrer_name'] for r in referrals)
        referrer_rewards = defaultdict(lambda: {'total': 0, 'rewarded': 0})
        for r in referrals:
            n = r['referrer_name']
            referrer_rewards[n]['total'] += 1
            if r.get('reward_issued'):
                referrer_rewards[n]['rewarded'] += 1

        # Services referred to
        service_counts = Counter(r.get('service', 'Unknown') for r in referrals if r.get('service'))

        report_date = datetime.now().strftime('%B %d, %Y')
        W = 60

        lines = []
        lines.append('=' * W)
        lines.append('  REFERRAL PROGRAM REPORT')
        lines.append(f"  {shop_name}")
        lines.append(f"  Generated: {report_date}")
        lines.append('=' * W)
        lines.append('')
        lines.append('  SUMMARY')
        lines.append('  ' + '─' * (W - 2))
        lines.append(f"  Total Referrals Logged  : {total}")
        lines.append(f"  Rewards Issued          : {issued}")
        lines.append(f"  Rewards Pending         : {pending}")
        if total > 0:
            lines.append(f"  Reward Fulfillment Rate : {issued / total * 100:.0f}%")

        lines.append('')
        lines.append('  TOP REFERRERS')
        lines.append('  ' + '─' * (W - 2))
        lines.append(f"  {'Name':<30}  {'Referrals':>9}  {'Rewarded':>8}  {'Pending':>7}")
        lines.append('  ' + '─' * (W - 2))

        for name, count in referrer_counts.most_common(20):
            rw = referrer_rewards[name]
            pend = rw['total'] - rw['rewarded']
            marker = '  [PENDING REWARD]' if pend > 0 else ''
            lines.append(f"  {name:<30}  {count:>9}  {rw['rewarded']:>8}  {pend:>7}{marker}")

        if service_counts:
            lines.append('')
            lines.append('  SERVICES THAT DROVE REFERRALS')
            lines.append('  ' + '─' * (W - 2))
            for service, cnt in service_counts.most_common(10):
                lines.append(f"  {service:<40}  {cnt:>5}")

        if pending > 0:
            lines.append('')
            lines.append('  REWARDS NOT YET ISSUED')
            lines.append('  ' + '─' * (W - 2))
            for r in [r for r in referrals if not r.get('reward_issued')]:
                lines.append(f"  {r['id']}  {r['referrer_name']}", )
                if r.get('referrer_phone'):
                    lines.append(f"       Phone: {r['referrer_phone']}")
                lines.append(f"       Referred: {r['referred_name']}  |  "
                             f"Date: {r.get('service_date', 'N/A')}")

        lines.append('')
        lines.append('=' * W)

        content = '\n'.join(lines)
        print(content)

        fp = os.path.join(os.path.abspath(OUTPUT_DIR), 'referral_report.txt')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nSaved: output/referrals/referral_report.txt")


if __name__ == '__main__':
    main()
