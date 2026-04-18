#!/usr/bin/env python3
"""
Generate formatted expense reports with category breakdowns, vendor summaries,
trend comparisons, and optional expense-to-revenue ratios.

Usage:
    python tools/expenses/generate_expense_report.py --period month --month 4 --year 2025
    python tools/expenses/generate_expense_report.py --period month --month 4 --year 2025 --revenue 52000
    python tools/expenses/generate_expense_report.py --period year --year 2025
    python tools/expenses/generate_expense_report.py --period month --month 4 --year 2025 --format detailed
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
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'expenses.json')
PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'expenses')

MONTH_NAMES = [
    '', 'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

HEALTHY_RANGES = {
    'parts': (25, 45),
    'labor': (20, 35),
    'rent': (5, 15),
    'utilities': (2, 8),
    'insurance': (3, 8),
    'marketing': (2, 8),
    'tools_equipment': (1, 10),
    'training': (0, 5),
    'waste_disposal': (0, 3),
    'office_supplies': (0, 3),
    'vehicle_fleet': (0, 5),
    'licenses_permits': (0, 2),
    'professional_services': (0, 5),
    'miscellaneous': (0, 5),
}


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_expenses():
    p = os.path.abspath(DATA_FILE)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def get_period_prefix(period, month, year):
    """Return the string prefix(es) to filter by."""
    if period == 'month':
        return [f"{year}-{month:02d}"]
    elif period == 'quarter':
        # determine quarter from month
        q = (month - 1) // 3
        months_in_q = [q * 3 + 1, q * 3 + 2, q * 3 + 3]
        return [f"{year}-{m:02d}" for m in months_in_q]
    else:  # year
        return [f"{year}"]


def filter_expenses(expenses, prefixes):
    return [e for e in expenses if any(e['date'].startswith(p) for p in prefixes)]


def period_label(period, month, year):
    if period == 'month':
        return f"{MONTH_NAMES[month]} {year}"
    elif period == 'quarter':
        q = (month - 1) // 3 + 1
        return f"Q{q} {year}"
    else:
        return str(year)


def prev_month(month, year):
    if month == 1:
        return 12, year - 1
    return month - 1, year


def bar_chart(value, total, width=20):
    if total == 0:
        return ''
    filled = int(value / total * width)
    return '█' * filled + '░' * (width - filled)


def flag_category(cat, pct):
    lo, hi = HEALTHY_RANGES.get(cat, (0, 100))
    if pct > hi + 10:
        return f"  [HIGH — typical range {lo}–{hi}%]"
    return ''


def main():
    parser = argparse.ArgumentParser(description="Generate expense report")
    parser.add_argument('--period', default='month',
                        choices=['month', 'quarter', 'year', 'monthly', 'annual'],
                        help="Report period")
    parser.add_argument('--month', type=int, default=0,
                        help="Month number 1-12 (default: current month)")
    parser.add_argument('--year', type=int, default=0,
                        help="4-digit year (default: current year)")
    parser.add_argument('--revenue', type=float, default=0.0,
                        help="Total revenue for the period (optional)")
    parser.add_argument('--format', default='detailed',
                        choices=['summary', 'detailed'],
                        help="Report format: summary or detailed",
                        dest='report_format')
    args = parser.parse_args()

    # Normalize period aliases
    if args.period == 'monthly':
        args.period = 'month'
    elif args.period == 'annual':
        args.period = 'year'

    now = datetime.now()
    month = args.month or now.month
    year = args.year or now.year

    if not 1 <= month <= 12:
        print(f"ERROR: Month must be 1–12, got {month}", file=sys.stderr)
        sys.exit(1)

    profile = load_profile()
    shop_name = profile.get('shop_name') or 'Your Shop'
    all_expenses = load_expenses()

    if not all_expenses:
        print("No expense data found.")
        print("Add expenses first: python tools/expenses/categorize_expenses.py --action add")
        sys.exit(1)

    prefixes = get_period_prefix(args.period, month, year)
    expenses = filter_expenses(all_expenses, prefixes)
    plabel = period_label(args.period, month, year)

    # Previous period for trend comparison
    prev_m, prev_y = prev_month(month, year)
    prev_prefixes = get_period_prefix(args.period, prev_m, prev_y)
    prev_expenses = filter_expenses(all_expenses, prev_prefixes)
    has_trend = len(prev_expenses) > 0

    W = 68
    lines = []
    report_date = now.strftime('%B %d, %Y')

    lines.append('=' * W)
    lines.append(f"  EXPENSE REPORT — {plabel.upper()}")
    lines.append(f"  {shop_name}")
    lines.append(f"  Generated: {report_date}")
    lines.append('=' * W)

    if not expenses:
        lines.append(f"\n  No expenses recorded for {plabel}.")
        lines.append('  Add expenses with: python tools/expenses/categorize_expenses.py --action add')
        lines.append('')
        content = '\n'.join(lines)
        print(content)
        return

    # ── Category totals ───────────────────────────────────────────────────────
    cats = defaultdict(float)
    vendors = defaultdict(float)
    all_entries = []

    for e in expenses:
        cats[e['category']] += e['amount']
        if e.get('vendor'):
            vendors[e['vendor']] += e['amount']
        all_entries.append(e)

    total = sum(cats.values())

    # ── Previous period totals ─────────────────────────────────────────────────
    prev_cats = defaultdict(float)
    prev_total = 0.0
    if has_trend:
        for e in prev_expenses:
            prev_cats[e['category']] += e['amount']
        prev_total = sum(prev_cats.values())

    prev_plabel = period_label(args.period, prev_m, prev_y) if has_trend else ''

    # ── SUMMARY SECTION ───────────────────────────────────────────────────────
    lines.append('')
    lines.append('  SUMMARY')
    lines.append('  ' + '─' * (W - 2))
    lines.append(f"  Total Expenses     : ${total:,.2f}")
    lines.append(f"  Number of Entries  : {len(all_entries)}")

    if args.revenue:
        net = args.revenue - total
        ratio = (total / args.revenue * 100)
        lines.append(f"  Period Revenue     : ${args.revenue:,.2f}")
        lines.append(f"  Net (Rev - Exp)    : ${net:,.2f}")
        lines.append(f"  Expense/Revenue %  : {ratio:.1f}%")
        if ratio > 80:
            lines.append(f"  [!] Expense ratio above 80% — review largest categories")

    if has_trend and prev_total:
        change = total - prev_total
        change_pct = (change / prev_total * 100)
        direction = 'up' if change >= 0 else 'down'
        lines.append(f"  vs. {prev_plabel:<16} : ${prev_total:,.2f}  "
                     f"({direction} ${abs(change):,.2f} / {abs(change_pct):.1f}%)")

    # ── BREAKDOWN BY CATEGORY ─────────────────────────────────────────────────
    lines.append('')
    lines.append('  BREAKDOWN BY CATEGORY')
    lines.append('  ' + '─' * (W - 2))

    if has_trend:
        lines.append(f"  {'Category':<22}  {'Amount':>10}  {'%':>5}  "
                     f"{'vs ' + prev_plabel:>14}  Chart")
        lines.append('  ' + '─' * (W - 2))
    else:
        lines.append(f"  {'Category':<22}  {'Amount':>10}  {'%':>5}  Chart")
        lines.append('  ' + '─' * (W - 2))

    for cat in sorted(cats, key=cats.get, reverse=True):
        amount = cats[cat]
        pct = amount / total * 100 if total else 0
        chart = bar_chart(amount, total, 16)
        flag = flag_category(cat, pct)

        if has_trend and prev_total:
            prev_amount = prev_cats.get(cat, 0.0)
            change = amount - prev_amount
            change_str = f"+${change:,.0f}" if change >= 0 else f"-${abs(change):,.0f}"
            lines.append(f"  {cat:<22}  ${amount:>9,.2f}  {pct:>4.1f}%  "
                         f"{change_str:>14}  {chart}{flag}")
        else:
            lines.append(f"  {cat:<22}  ${amount:>9,.2f}  {pct:>4.1f}%  {chart}{flag}")

    lines.append('  ' + '─' * (W - 2))
    lines.append(f"  {'TOTAL':<22}  ${total:>9,.2f}  100.0%")

    # ── TOP VENDORS ───────────────────────────────────────────────────────────
    if vendors:
        lines.append('')
        lines.append('  TOP VENDORS')
        lines.append('  ' + '─' * (W - 2))
        top_vendors = sorted(vendors.items(), key=lambda x: x[1], reverse=True)[:10]
        for vendor, amount in top_vendors:
            pct = amount / total * 100
            lines.append(f"  {vendor:<35}  ${amount:>9,.2f}  ({pct:.1f}%)")

    # ── LARGEST INDIVIDUAL EXPENSES ───────────────────────────────────────────
    if args.report_format == 'detailed':
        sorted_entries = sorted(all_entries, key=lambda x: x['amount'], reverse=True)
        top_entries = sorted_entries[:10]

        lines.append('')
        lines.append('  LARGEST EXPENSES (TOP 10)')
        lines.append('  ' + '─' * (W - 2))
        lines.append(f"  {'Date':<12}  {'Amount':>10}  {'Category':<20}  Description")
        lines.append('  ' + '─' * (W - 2))
        for e in top_entries:
            desc = (e.get('description') or '')[:30]
            cat = e['category'][:19]
            vendor = e.get('vendor', '')
            desc_full = f"{vendor}: {desc}" if vendor else desc
            desc_full = desc_full[:45]
            lines.append(f"  {e['date']:<12}  ${e['amount']:>9,.2f}  {cat:<20}  {desc_full}")

    # ── FULL EXPENSE LEDGER ────────────────────────────────────────────────────
    if args.report_format == 'detailed':
        lines.append('')
        lines.append('  FULL EXPENSE LEDGER')
        lines.append('  ' + '─' * (W - 2))
        lines.append(f"  {'Date':<12}  {'Amount':>10}  {'Category':<20}  "
                     f"{'Vendor':<20}  Description")
        lines.append('  ' + '─' * (W - 2))
        for e in sorted(all_entries, key=lambda x: x['date']):
            desc = (e.get('description') or '')[:30]
            vendor = (e.get('vendor') or '')[:19]
            cat = e['category'][:19]
            ref = f"  [{e['receipt_ref']}]" if e.get('receipt_ref') else ''
            lines.append(f"  {e['date']:<12}  ${e['amount']:>9,.2f}  "
                         f"{cat:<20}  {vendor:<20}  {desc}{ref}")
        lines.append('  ' + '─' * (W - 2))
        lines.append(f"  {'TOTAL':<12}  ${total:>9,.2f}")

    lines.append('')
    lines.append('=' * W)

    # ── BOOKKEEPER NOTES ──────────────────────────────────────────────────────
    lines.append('')
    lines.append('  NOTES FOR BOOKKEEPER')
    lines.append('  ' + '─' * (W - 2))
    if args.revenue:
        lines.append(f"  Revenue provided by shop owner: ${args.revenue:,.2f}")
    else:
        lines.append('  Revenue not provided — expense-to-revenue ratio not calculated.')
    lines.append(f"  All amounts in USD. Report covers: {plabel}.")
    lines.append(f"  Entries with receipt references should have supporting documents on file.")
    lines.append('')

    content = '\n'.join(lines)
    print(content)

    # ── Save to file ──────────────────────────────────────────────────────────
    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)
    period_str = plabel.replace(' ', '_').lower()
    fp = os.path.join(os.path.abspath(OUTPUT_DIR), f'expense_report_{period_str}.txt')
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Saved: output/expenses/expense_report_{period_str}.txt")


if __name__ == '__main__':
    main()
