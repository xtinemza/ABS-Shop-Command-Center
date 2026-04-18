#!/usr/bin/env python3
"""
Generate a formatted warranty recovery report.

Usage:
    python tools/warranty/generate_warranty_report.py --period month
    python tools/warranty/generate_warranty_report.py --period quarter
    python tools/warranty/generate_warranty_report.py --period year
    python tools/warranty/generate_warranty_report.py --period all
    python tools/warranty/generate_warranty_report.py --period all --status open
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
from collections import defaultdict
from datetime import datetime, date

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'warranty_claims.json')
PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'warranty')

OPEN_STATUSES = {'New', 'Submitted', 'Pending Vendor', 'Parts Requested', 'Escalated'}


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


def days_old(date_str):
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d').date()
        return (date.today() - d).days
    except (ValueError, TypeError):
        return 0


def in_period(claim_date_str, period, now):
    """Return True if the claim_date falls within the requested period."""
    try:
        d = datetime.strptime(claim_date_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        return False

    if period == 'month':
        return d.year == now.year and d.month == now.month
    elif period == 'quarter':
        q = (now.month - 1) // 3
        claim_q = (d.month - 1) // 3
        return d.year == now.year and claim_q == q
    elif period == 'year':
        return d.year == now.year
    else:  # all
        return True


def period_label(period, now):
    if period == 'month':
        return now.strftime('%B %Y')
    elif period == 'quarter':
        q = (now.month - 1) // 3 + 1
        return f"Q{q} {now.year}"
    elif period == 'year':
        return str(now.year)
    return 'All Time'


def main():
    parser = argparse.ArgumentParser(description="Generate warranty recovery report")
    parser.add_argument('--period', default='all',
                        choices=['month', 'quarter', 'year', 'all', 'monthly'],
                        help="Report period")
    parser.add_argument('--status', default='',
                        help="Filter: 'open' for open claims only, 'closed' for resolved/denied")
    args = parser.parse_args()

    # Normalize legacy 'monthly' → 'month'
    if args.period == 'monthly':
        args.period = 'month'

    profile = load_profile()
    shop_name = profile.get('shop_name') or 'Your Shop'
    all_claims = load_claims()
    now = datetime.now()

    # Period filter
    claims = [c for c in all_claims if in_period(c.get('created_date', ''), args.period, now)]

    # Status filter
    status_filter = args.status.lower()
    if status_filter in ('open', 'active'):
        claims = [c for c in claims if c['status'] in OPEN_STATUSES]
    elif status_filter in ('closed', 'resolved', 'denied'):
        claims = [c for c in claims if c['status'] not in OPEN_STATUSES]

    plabel = period_label(args.period, now)
    report_date = now.strftime('%B %d, %Y')

    lines = []
    W = 65

    lines.append('=' * W)
    lines.append(f"  WARRANTY RECOVERY REPORT — {plabel.upper()}")
    lines.append(f"  {shop_name}")
    lines.append(f"  Generated: {report_date}")
    lines.append('=' * W)

    if not claims:
        lines.append(f"\n  No warranty claims found for {plabel}.")
        if not all_claims:
            lines.append("  Log claims with: python tools/warranty/track_claims.py --action add")
        lines.append('')
        content = '\n'.join(lines)
        print(content)
        os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)
        period_slug = args.period.replace(' ', '_')
        fp = os.path.join(os.path.abspath(OUTPUT_DIR), f'warranty_report_{period_slug}.txt')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nSaved: output/warranty/warranty_report_{period_slug}.txt")
        return

    # ── Summary Metrics ───────────────────────────────────────────────────────
    total_claims = len(claims)
    open_claims = [c for c in claims if c['status'] in OPEN_STATUSES]
    resolved_claims = [c for c in claims if c['status'] == 'Resolved']
    denied_claims = [c for c in claims if c['status'] == 'Denied']

    total_claimed = sum(c['cost'] for c in claims)
    total_recovered = sum(c.get('reimbursement', 0.0) for c in claims)
    recovery_rate = (total_recovered / total_claimed * 100) if total_claimed else 0

    lines.append('')
    lines.append('  SUMMARY')
    lines.append('  ' + '─' * (W - 2))
    lines.append(f"  Total Claims Filed  : {total_claims}")
    lines.append(f"  Open / Pending      : {len(open_claims)}")
    lines.append(f"  Resolved            : {len(resolved_claims)}")
    lines.append(f"  Denied              : {len(denied_claims)}")
    lines.append(f"  Total Value Claimed : ${total_claimed:,.2f}")
    lines.append(f"  Total Recovered     : ${total_recovered:,.2f}")
    lines.append(f"  Recovery Rate       : {recovery_rate:.0f}%")

    if open_claims:
        open_value = sum(c['cost'] for c in open_claims)
        lines.append(f"  Open Claims Value   : ${open_value:,.2f}  (potential recovery)")

    # ── Vendor Breakdown ──────────────────────────────────────────────────────
    vendor_stats = defaultdict(lambda: {'count': 0, 'claimed': 0.0, 'recovered': 0.0,
                                        'resolved': 0, 'denied': 0})
    for c in claims:
        v = c.get('vendor', 'Unknown')
        vendor_stats[v]['count'] += 1
        vendor_stats[v]['claimed'] += c['cost']
        vendor_stats[v]['recovered'] += c.get('reimbursement', 0.0)
        if c['status'] == 'Resolved':
            vendor_stats[v]['resolved'] += 1
        elif c['status'] == 'Denied':
            vendor_stats[v]['denied'] += 1

    lines.append('')
    lines.append('  VENDOR BREAKDOWN')
    lines.append('  ' + '─' * (W - 2))
    lines.append(f"  {'Vendor':<28} {'Claims':>6}  {'Claimed':>10}  {'Recovered':>10}  {'Rate':>6}")
    lines.append('  ' + '─' * (W - 2))
    for vendor in sorted(vendor_stats, key=lambda v: vendor_stats[v]['claimed'], reverse=True):
        vs = vendor_stats[vendor]
        rate = (vs['recovered'] / vs['claimed'] * 100) if vs['claimed'] else 0
        vname = vendor[:27]
        lines.append(f"  {vname:<28} {vs['count']:>6}  ${vs['claimed']:>9,.2f}  "
                     f"${vs['recovered']:>9,.2f}  {rate:>5.0f}%")

    # ── Open Claims Requiring Follow-Up ───────────────────────────────────────
    if open_claims:
        aged_90 = [c for c in open_claims if days_old(c['created_date']) >= 90]
        aged_60 = [c for c in open_claims if 60 <= days_old(c['created_date']) < 90]
        aged_30 = [c for c in open_claims if 30 <= days_old(c['created_date']) < 60]
        fresh = [c for c in open_claims if days_old(c['created_date']) < 30]

        lines.append('')
        lines.append('  OPEN CLAIMS — FOLLOW-UP REQUIRED')
        lines.append('  ' + '─' * (W - 2))

        sections = [
            ('!!! 90+ DAYS — REVIEW FOR WRITE-OFF', aged_90),
            ('!! 60–89 DAYS — ESCALATE', aged_60),
            ('! 30–59 DAYS — FOLLOW UP', aged_30),
            ('< 30 DAYS — ACTIVE', fresh),
        ]

        for label, group in sections:
            if not group:
                continue
            lines.append(f"\n  [{label}]")
            for c in sorted(group, key=lambda x: days_old(x['created_date']), reverse=True):
                age = days_old(c['created_date'])
                lines.append(f"  {c['id']}  {c['part']}")
                lines.append(f"         Vendor: {c['vendor']}  |  "
                             f"Cost: ${c['cost']:,.2f}  |  Age: {age} days")
                lines.append(f"         Vehicle: {c['vehicle']}", )
                if c.get('customer'):
                    lines.append(f"         Customer: {c['customer']}")
                lines.append(f"         Status: {c['status']}")
                # Show last history note
                if c.get('history'):
                    last = c['history'][-1]
                    lines.append(f"         Last Update: {last['date']} — {last['note']}")

    # ── All Claims Detail ─────────────────────────────────────────────────────
    lines.append('')
    lines.append('  ALL CLAIMS DETAIL')
    lines.append('  ' + '─' * (W - 2))
    lines.append(f"  {'ID':<8}  {'Part':<25}  {'Vendor':<22}  "
                 f"{'Cost':>8}  {'Recov':>8}  {'Status'}")
    lines.append('  ' + '─' * (W - 2))
    for c in sorted(claims, key=lambda x: x['created_date'], reverse=True):
        pname = c['part'][:24]
        vname = c.get('vendor', '')[:21]
        rec = c.get('reimbursement', 0.0)
        lines.append(f"  {c['id']:<8}  {pname:<25}  {vname:<22}  "
                     f"${c['cost']:>7,.2f}  ${rec:>7,.2f}  {c['status']}")

    lines.append('')
    lines.append('=' * W)

    # ── Save and Print ────────────────────────────────────────────────────────
    content = '\n'.join(lines)
    print(content)

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)
    period_slug = args.period
    fp = os.path.join(os.path.abspath(OUTPUT_DIR), f'warranty_report_{period_slug}.txt')
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\nSaved: output/warranty/warranty_report_{period_slug}.txt")


if __name__ == '__main__':
    main()
