#!/usr/bin/env python3
"""
Track warranty claims from initiation through vendor reimbursement.

Usage:
    python tools/warranty/track_claims.py --action add \
        --part "Alternator - Reman" --part_number "ALT-8912" \
        --vendor "O'Reilly Auto Parts" --install_date "2025-01-15" \
        --failure_date "2025-06-20" --warranty_period_days 365 \
        --cost 189.99 --vehicle "2018 Honda Accord" \
        --customer "Maria Gonzalez" \
        --description "Premature failure, not charging"

    python tools/warranty/track_claims.py --action update \
        --claim_id WC-001 --status "Submitted" \
        --notes "RMA #44821 issued" --reimbursement 189.99

    python tools/warranty/track_claims.py --action list
    python tools/warranty/track_claims.py --action list --status open
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
from datetime import datetime, date

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'warranty_claims.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'warranty')
PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')

OPEN_STATUSES = {'New', 'Submitted', 'Pending Vendor', 'Parts Requested', 'Escalated'}
CLOSED_STATUSES = {'Resolved', 'Denied'}
ALL_STATUSES = OPEN_STATUSES | CLOSED_STATUSES


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_claims():
    p = os.path.abspath(DATA_FILE)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_claims(data):
    p = os.path.abspath(DATA_FILE)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def days_old(date_str):
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d').date()
        return (date.today() - d).days
    except (ValueError, TypeError):
        return 0


def age_flag(days):
    if days >= 90:
        return " [!!! 90+ DAYS — REVIEW WRITE-OFF]"
    elif days >= 60:
        return " [!! 60+ DAYS — ESCALATE]"
    elif days >= 30:
        return " [! 30+ DAYS — FOLLOW UP]"
    return ""


def validate_dates(install_date, failure_date):
    try:
        i = datetime.strptime(install_date, '%Y-%m-%d')
        f = datetime.strptime(failure_date, '%Y-%m-%d')
        if f < i:
            return False, "Failure date is before install date — please verify."
        return True, None
    except ValueError as e:
        return False, f"Invalid date format: {e}"


def main():
    parser = argparse.ArgumentParser(description="Track warranty claims")
    parser.add_argument('--action', required=True,
                        choices=['add', 'new', 'update', 'list', 'report'],
                        help="Action to perform")
    parser.add_argument('--claim_id', default='', help="Claim ID for updates")
    parser.add_argument('--part', default='', help="Part name")
    parser.add_argument('--part_number', default='', help="Part number from invoice")
    parser.add_argument('--vendor', default='', help="Parts vendor/supplier")
    parser.add_argument('--install_date', default='', help="Installation date YYYY-MM-DD")
    parser.add_argument('--failure_date', default='', help="Failure date YYYY-MM-DD")
    parser.add_argument('--warranty_period_days', type=int, default=365,
                        help="Warranty period in days (default: 365)")
    parser.add_argument('--cost', type=float, default=0.0, help="Part cost in dollars")
    parser.add_argument('--vehicle', default='', help="Year Make Model")
    parser.add_argument('--customer', default='', help="Customer name")
    parser.add_argument('--description', default='', help="Failure description")
    parser.add_argument('--status', default='', help="Claim status")
    parser.add_argument('--notes', default='', help="Notes for status update")
    parser.add_argument('--reimbursement', type=float, default=0.0,
                        help="Amount reimbursed by vendor")
    args = parser.parse_args()

    # Normalize 'new' -> 'add' for backward compat
    if args.action == 'new':
        args.action = 'add'

    claims = load_claims()
    today = datetime.now().strftime('%Y-%m-%d')
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')

    # ── ADD NEW CLAIM ─────────────────────────────────────────────────────────
    if args.action == 'add':
        missing = []
        if not args.part:
            missing.append('--part')
        if not args.vendor:
            missing.append('--vendor')
        if not args.install_date:
            missing.append('--install_date')
        if not args.failure_date:
            missing.append('--failure_date')
        if not args.cost:
            missing.append('--cost')
        if not args.vehicle:
            missing.append('--vehicle')
        if not args.description:
            missing.append('--description')

        if missing:
            print(f"ERROR: Missing required fields: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)

        # Date validation
        if args.install_date and args.failure_date:
            valid, err = validate_dates(args.install_date, args.failure_date)
            if not valid:
                print(f"ERROR: {err}", file=sys.stderr)
                sys.exit(1)

        # Check if still within warranty period
        warranty_note = ""
        if args.install_date and args.failure_date:
            try:
                install_d = datetime.strptime(args.install_date, '%Y-%m-%d')
                failure_d = datetime.strptime(args.failure_date, '%Y-%m-%d')
                days_in_service = (failure_d - install_d).days
                if days_in_service <= args.warranty_period_days:
                    warranty_note = f"Within warranty period ({days_in_service} of {args.warranty_period_days} days)"
                else:
                    warranty_note = f"OUTSIDE warranty period ({days_in_service} days in service; warranty: {args.warranty_period_days} days)"
            except ValueError:
                warranty_note = ""

        claim_id = f"WC-{len(claims) + 1:03d}"

        claim = {
            "id": claim_id,
            "part": args.part,
            "part_number": args.part_number,
            "vendor": args.vendor,
            "install_date": args.install_date,
            "failure_date": args.failure_date,
            "warranty_period_days": args.warranty_period_days,
            "warranty_note": warranty_note,
            "cost": args.cost,
            "vehicle": args.vehicle,
            "customer": args.customer,
            "description": args.description,
            "status": "New",
            "reimbursement": 0.0,
            "created_date": today,
            "history": [
                {
                    "date": now_str,
                    "status": "New",
                    "note": "Claim created"
                }
            ]
        }

        claims.append(claim)
        save_claims(claims)

        print(f"\n{'=' * 58}")
        print(f"  WARRANTY CLAIM CREATED")
        print(f"{'=' * 58}")
        print(f"  Claim ID  : {claim_id}")
        print(f"  Part      : {args.part}")
        if args.part_number:
            print(f"  Part No.  : {args.part_number}")
        print(f"  Vendor    : {args.vendor}")
        print(f"  Vehicle   : {args.vehicle}")
        if args.customer:
            print(f"  Customer  : {args.customer}")
        print(f"  Installed : {args.install_date}")
        print(f"  Failed    : {args.failure_date}")
        print(f"  Cost      : ${args.cost:,.2f}")
        print(f"  Status    : New")
        if warranty_note:
            print(f"  Warranty  : {warranty_note}")
        print(f"\n  Description: {args.description}")
        print(f"\n  Next Steps:")
        print(f"  1. Contact {args.vendor} to initiate the warranty claim")
        print(f"  2. Have original invoice and install record ready")
        print(f"  3. Update status with: --action update --claim_id {claim_id}")
        print(f"{'=' * 58}\n")

    # ── UPDATE CLAIM ──────────────────────────────────────────────────────────
    elif args.action == 'update':
        if not args.claim_id:
            print("ERROR: --claim_id required for update", file=sys.stderr)
            sys.exit(1)

        found = False
        for claim in claims:
            if claim['id'].upper() == args.claim_id.upper():
                found = True
                old_status = claim['status']

                if args.status:
                    claim['status'] = args.status
                if args.reimbursement:
                    claim['reimbursement'] = args.reimbursement
                    if not args.status:
                        claim['status'] = 'Resolved'

                note_text = args.notes or f"Status changed from '{old_status}' to '{claim['status']}'"
                if args.reimbursement:
                    note_text += f" | Reimbursement: ${args.reimbursement:,.2f}"

                claim['history'].append({
                    "date": now_str,
                    "status": claim['status'],
                    "note": note_text
                })

                save_claims(claims)

                print(f"\n{'=' * 58}")
                print(f"  CLAIM {claim['id']} UPDATED")
                print(f"{'=' * 58}")
                print(f"  Part    : {claim['part']} | {claim['vendor']}")
                print(f"  Vehicle : {claim['vehicle']}")
                print(f"  Status  : {old_status} → {claim['status']}")
                if args.reimbursement:
                    print(f"  Recovered: ${args.reimbursement:,.2f} of ${claim['cost']:,.2f} claimed")
                if args.notes:
                    print(f"  Notes   : {args.notes}")
                print(f"\n  History ({len(claim['history'])} entries):")
                for h in claim['history'][-3:]:
                    print(f"    {h['date']}  [{h['status']}]  {h['note']}")
                if len(claim['history']) > 3:
                    print(f"    ... and {len(claim['history']) - 3} earlier entries")
                print(f"{'=' * 58}\n")
                break

        if not found:
            print(f"ERROR: Claim '{args.claim_id}' not found.", file=sys.stderr)
            print("Run --action list to see all claim IDs.", file=sys.stderr)
            sys.exit(1)

    # ── LIST CLAIMS ───────────────────────────────────────────────────────────
    elif args.action == 'list':
        if not claims:
            print("No warranty claims on file.")
            print("Log a claim with: --action add")
            return

        # Optional status filter
        status_filter = args.status.lower() if args.status else ''
        if status_filter in ('open', 'active'):
            display = [c for c in claims if c['status'] in OPEN_STATUSES]
            label = "OPEN CLAIMS"
        elif status_filter in ('closed', 'resolved'):
            display = [c for c in claims if c['status'] in CLOSED_STATUSES]
            label = "CLOSED CLAIMS"
        else:
            display = claims
            label = f"ALL CLAIMS ({len(claims)})"

        open_count = sum(1 for c in claims if c['status'] in OPEN_STATUSES)
        closed_count = sum(1 for c in claims if c['status'] in CLOSED_STATUSES)
        total_claimed = sum(c['cost'] for c in claims)
        total_recovered = sum(c.get('reimbursement', 0) for c in claims)

        print(f"\n{'=' * 65}")
        print(f"  WARRANTY CLAIMS — {label}")
        print(f"{'=' * 65}")
        print(f"  Open: {open_count}  |  Closed: {closed_count}  |  "
              f"Claimed: ${total_claimed:,.2f}  |  Recovered: ${total_recovered:,.2f}")
        print(f"{'─' * 65}")

        if not display:
            print(f"  No claims match filter '{status_filter}'.")
        else:
            for c in sorted(display, key=lambda x: x['created_date'], reverse=True):
                age = days_old(c['created_date'])
                flag = age_flag(age)
                print(f"\n  {c['id']}  |  {c['status']}{flag}")
                print(f"  Part    : {c['part']}", end='')
                if c.get('part_number'):
                    print(f" ({c['part_number']})", end='')
                print()
                print(f"  Vendor  : {c['vendor']}")
                print(f"  Vehicle : {c['vehicle']}", end='')
                if c.get('customer'):
                    print(f"  |  Customer: {c['customer']}", end='')
                print()
                print(f"  Cost    : ${c['cost']:,.2f}", end='')
                if c.get('reimbursement'):
                    print(f"  |  Recovered: ${c['reimbursement']:,.2f}", end='')
                print()
                print(f"  Opened  : {c['created_date']}  ({age} days ago)")
                if c.get('warranty_note'):
                    print(f"  [{c['warranty_note']}]")

        print(f"\n{'=' * 65}\n")

    # ── QUICK REPORT (legacy compat) ──────────────────────────────────────────
    elif args.action == 'report':
        # Delegate to generate_warranty_report.py
        import subprocess
        script = os.path.join(os.path.dirname(__file__), 'generate_warranty_report.py')
        subprocess.run([sys.executable, script, '--period', 'all'])


if __name__ == '__main__':
    main()
