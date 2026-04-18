#!/usr/bin/env python3
"""
Categorize and log shop expenses.

Usage:
    python tools/expenses/categorize_expenses.py --action add \
        --date "2025-04-02" --amount 847.50 \
        --vendor "AutoZone Commercial" \
        --description "Brake pads and rotors bulk order" \
        --category parts \
        --payment_method "Business Visa" \
        --receipt_ref "AZ-INV-88234"

    python tools/expenses/categorize_expenses.py --action list
    python tools/expenses/categorize_expenses.py --action list --month "2025-04"
    python tools/expenses/categorize_expenses.py --action summary --month "2025-04"
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

CATEGORIES = [
    'parts', 'labor', 'rent', 'utilities', 'insurance', 'marketing',
    'tools_equipment', 'training', 'waste_disposal', 'office_supplies',
    'vehicle_fleet', 'licenses_permits', 'professional_services', 'miscellaneous'
]

CATEGORY_DESCRIPTIONS = {
    'parts': 'Bulk part orders, individual parts for jobs',
    'labor': 'Payroll, subcontracted labor',
    'rent': 'Shop rent/lease payments',
    'utilities': 'Electric, gas, water, internet, phone',
    'insurance': 'Liability, property, workers comp',
    'marketing': 'Advertising, website, social ads, postage',
    'tools_equipment': 'Tools, equipment purchases or leases',
    'training': 'Certifications, courses, trade shows',
    'waste_disposal': 'Oil recycling, hazmat disposal',
    'office_supplies': 'Paper, ink, forms, software subscriptions',
    'vehicle_fleet': 'Shop vehicles, registration, fuel',
    'licenses_permits': 'Business license, EPA permits',
    'professional_services': 'Accountant, attorney, consultant',
    'miscellaneous': 'Other expenses'
}


def load_expenses():
    p = os.path.abspath(DATA_FILE)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_expenses(data):
    p = os.path.abspath(DATA_FILE)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def parse_month_filter(month_str):
    """Accept YYYY-MM or MM/YYYY or just YYYY-MM."""
    if not month_str:
        return None
    month_str = month_str.strip()
    # Already YYYY-MM
    if len(month_str) == 7 and '-' in month_str:
        return month_str
    # Try other formats
    for fmt in ('%Y-%m', '%m/%Y', '%B %Y', '%b %Y'):
        try:
            d = datetime.strptime(month_str, fmt)
            return d.strftime('%Y-%m')
        except ValueError:
            continue
    return month_str  # return as-is and let filtering handle it


def main():
    parser = argparse.ArgumentParser(description="Categorize and log shop expenses")
    parser.add_argument('--action', default='add',
                        choices=['add', 'list', 'summary'],
                        help="Action: add, list, or summary")
    parser.add_argument('--date', default='',
                        help="Expense date YYYY-MM-DD (default: today)")
    parser.add_argument('--amount', type=float, default=0.0,
                        help="Expense amount in dollars")
    parser.add_argument('--vendor', default='',
                        help="Vendor or payee name")
    parser.add_argument('--description', default='',
                        help="What was purchased or paid for")
    parser.add_argument('--category', default='',
                        choices=CATEGORIES + [''],
                        help="Expense category")
    parser.add_argument('--payment_method', default='',
                        help="e.g., Business Visa, Check, ACH")
    parser.add_argument('--receipt_ref', default='',
                        help="Invoice or receipt reference number")
    parser.add_argument('--month', default='',
                        help="Month filter for list/summary: YYYY-MM")
    args = parser.parse_args()

    expenses = load_expenses()
    today = datetime.now().strftime('%Y-%m-%d')

    # ── ADD EXPENSE ───────────────────────────────────────────────────────────
    if args.action == 'add':
        missing = []
        if not args.amount:
            missing.append('--amount')
        if not args.description:
            missing.append('--description')
        if not args.category:
            missing.append('--category')
        if missing:
            print(f"ERROR: Missing required fields: {', '.join(missing)}", file=sys.stderr)
            print(f"\nAvailable categories:", file=sys.stderr)
            for cat in CATEGORIES:
                print(f"  {cat:<22}  {CATEGORY_DESCRIPTIONS[cat]}", file=sys.stderr)
            sys.exit(1)

        entry_date = args.date or today
        # Validate date format
        try:
            datetime.strptime(entry_date, '%Y-%m-%d')
        except ValueError:
            print(f"ERROR: Date must be YYYY-MM-DD, got: '{entry_date}'", file=sys.stderr)
            sys.exit(1)

        entry = {
            "date": entry_date,
            "amount": round(args.amount, 2),
            "vendor": args.vendor,
            "description": args.description,
            "category": args.category,
            "payment_method": args.payment_method,
            "receipt_ref": args.receipt_ref,
            "logged_at": datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        expenses.append(entry)
        save_expenses(expenses)

        # Calculate running month total
        month_prefix = entry_date[:7]
        month_total = sum(e['amount'] for e in expenses if e['date'].startswith(month_prefix))

        print(f"\n  Expense Logged")
        print(f"  {'─' * 40}")
        print(f"  Date       : {entry_date}")
        print(f"  Amount     : ${args.amount:,.2f}")
        print(f"  Category   : {args.category}")
        print(f"  Vendor     : {args.vendor or '(not specified)'}")
        print(f"  Description: {args.description}")
        if args.payment_method:
            print(f"  Payment    : {args.payment_method}")
        if args.receipt_ref:
            print(f"  Receipt    : {args.receipt_ref}")
        print(f"\n  Month-to-date ({month_prefix}): ${month_total:,.2f}  "
              f"({len([e for e in expenses if e['date'].startswith(month_prefix)])} entries)\n")

    # ── LIST EXPENSES ─────────────────────────────────────────────────────────
    elif args.action == 'list':
        if not expenses:
            print("No expenses logged.")
            print("Add expenses with: --action add")
            return

        month_filter = parse_month_filter(args.month)
        if month_filter:
            display = [e for e in expenses if e['date'].startswith(month_filter)]
            period_label = month_filter
        else:
            display = expenses
            period_label = 'All'

        display = sorted(display, key=lambda x: x['date'], reverse=True)

        if not display:
            print(f"No expenses found for {period_label}.")
            return

        total = sum(e['amount'] for e in display)
        print(f"\n{'=' * 75}")
        print(f"  EXPENSE LOG — {period_label.upper()}  ({len(display)} entries)")
        print(f"{'=' * 75}")
        print(f"  {'Date':<12} {'Amount':>10}  {'Category':<22}  {'Vendor':<22}  Description")
        print(f"  {'─' * 12} {'─' * 10}  {'─' * 22}  {'─' * 22}  {'─' * 15}")

        for e in display:
            vendor = (e.get('vendor') or '')[:21]
            desc = (e.get('description') or '')[:35]
            cat = e['category'][:21]
            print(f"  {e['date']:<12} ${e['amount']:>9,.2f}  {cat:<22}  {vendor:<22}  {desc}")

        print(f"  {'─' * 72}")
        print(f"  {'TOTAL':<12} ${total:>9,.2f}")
        print(f"{'=' * 75}\n")

    # ── SUMMARY BY CATEGORY ───────────────────────────────────────────────────
    elif args.action == 'summary':
        if not expenses:
            print("No expenses logged.")
            return

        month_filter = parse_month_filter(args.month) or datetime.now().strftime('%Y-%m')
        filtered = [e for e in expenses if e['date'].startswith(month_filter)]

        if not filtered:
            print(f"No expenses for {month_filter}.")
            return

        cats = defaultdict(float)
        for e in filtered:
            cats[e['category']] += e['amount']
        total = sum(cats.values())

        print(f"\n{'=' * 55}")
        print(f"  EXPENSE SUMMARY: {month_filter}")
        print(f"{'=' * 55}")
        print(f"  {'Category':<25}  {'Amount':>10}  {'%':>5}")
        print(f"  {'─' * 25}  {'─' * 10}  {'─' * 5}")
        for cat in sorted(cats, key=cats.get, reverse=True):
            pct = cats[cat] / total * 100
            bar = '|' * int(pct / 5)
            print(f"  {cat:<25}  ${cats[cat]:>9,.2f}  {pct:>4.1f}%  {bar}")
        print(f"  {'─' * 25}  {'─' * 10}")
        print(f"  {'TOTAL':<25}  ${total:>9,.2f}")
        print(f"{'=' * 55}\n")


if __name__ == '__main__':
    main()
