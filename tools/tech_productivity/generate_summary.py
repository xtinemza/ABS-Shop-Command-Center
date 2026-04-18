#!/usr/bin/env python3
"""
Generate technician productivity and labor efficiency reports.

Supports two modes:
  1. JSON batch mode (all techs at once via --technicians)
  2. Individual entry mode (one tech at a time, then --compile)

Usage (batch mode — preferred):
    python tools/tech_productivity/generate_summary.py \
        --period week --date "2025-04-14" \
        --technicians '[
            {"name": "Mike R.", "hours_clocked": 40, "hours_billed": 44.5,
             "jobs_completed": 22, "revenue_generated": 9200, "comebacks": 1},
            {"name": "Sara T.", "hours_clocked": 38, "hours_billed": 35.0,
             "jobs_completed": 18, "revenue_generated": 7400, "comebacks": 0}
        ]'

Usage (individual + compile mode):
    python tools/tech_productivity/generate_summary.py \
        --period week --date "2025-04-14" \
        --tech "Mike R." --hours_clocked 40 --hours_billed 44.5 \
        --jobs_completed 22 --revenue_generated 9200 --comebacks 1

    python tools/tech_productivity/generate_summary.py \
        --period week --date "2025-04-14" --compile
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
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'tech_productivity')
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'tech_data.json')


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_tech_data():
    p = os.path.abspath(DATA_FILE)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_tech_data(data):
    p = os.path.abspath(DATA_FILE)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def efficiency_pct(hours_billed, hours_clocked):
    if hours_clocked and hours_clocked > 0:
        return (hours_billed / hours_clocked) * 100
    return None


def comeback_rate(comebacks, jobs):
    if jobs and jobs > 0:
        return (comebacks / jobs) * 100
    return 0.0


def eff_flag(eff):
    if eff is None:
        return '[NO DATA]'
    if eff >= 100:
        return '[EXCELLENT]'
    if eff >= 90:
        return '[GOOD]'
    if eff >= 80:
        return '[OK]'
    return '[!! BELOW TARGET]'


def cb_flag(rate):
    if rate >= 5:
        return '[!! HIGH COMEBACK RATE]'
    if rate >= 3:
        return '[WATCH]'
    return ''


def revenue_per_hour(revenue, hours_billed):
    if hours_billed and hours_billed > 0:
        return revenue / hours_billed
    return None


def jobs_per_day(jobs, hours_clocked, shift_hours=8):
    if hours_clocked and hours_clocked > 0:
        days = hours_clocked / shift_hours
        return jobs / days if days > 0 else None
    return None


def build_report(techs, period, date_str, shop_name, period_label_str):
    W = 72
    lines = []
    report_date = datetime.now().strftime('%B %d, %Y')

    lines.append('=' * W)
    lines.append('  TECHNICIAN PRODUCTIVITY REPORT')
    lines.append(f"  {shop_name}")
    lines.append(f"  Period: {period_label_str}  |  Generated: {report_date}")
    lines.append('=' * W)

    # ── Per-Tech Section ──────────────────────────────────────────────────────
    valid_techs = [t for t in techs if t.get('hours_clocked', 0) > 0]
    flagged = []
    top_tech = None
    top_eff = -1

    for t in valid_techs:
        name = t['name']
        clocked = t.get('hours_clocked', 0)
        billed = t.get('hours_billed', 0)
        jobs = t.get('jobs_completed', 0)
        revenue = t.get('revenue_generated', 0)
        comebacks = t.get('comebacks', 0)

        eff = efficiency_pct(billed, clocked)
        cb = comeback_rate(comebacks, jobs)
        rev_hr = revenue_per_hour(revenue, billed)
        jpd = jobs_per_day(jobs, clocked)

        if eff is not None and eff > top_eff:
            top_eff = eff
            top_tech = name

        lines.append('')
        lines.append('  ' + '─' * (W - 2))
        lines.append(f"  TECHNICIAN: {name}")
        lines.append('  ' + '─' * (W - 2))

        lines.append(f"  Hours Clocked          : {clocked:.1f} hrs")
        lines.append(f"  Hours Billed           : {billed:.1f} hrs")

        if eff is not None:
            flag = eff_flag(eff)
            lines.append(f"  Efficiency             : {eff:.0f}%  {flag}")
            if eff < 80:
                flagged.append((name, f"Efficiency at {eff:.0f}% — below 80% target"))
        else:
            lines.append(f"  Efficiency             : N/A (no hours clocked)")

        lines.append(f"  Jobs Completed         : {jobs}")
        lines.append(f"  Revenue Generated      : ${revenue:,.2f}")

        if rev_hr is not None:
            lines.append(f"  Revenue per Billed Hr  : ${rev_hr:,.2f}/hr")

        if jpd is not None:
            lines.append(f"  Jobs per Day (8-hr)    : {jpd:.1f}")

        lines.append(f"  Comebacks              : {comebacks}  ({cb:.1f}%)",)
        if comebacks > 0:
            cb_note = cb_flag(cb)
            if cb_note:
                lines.append(f"                           {cb_note}")
                flagged.append((name, f"Comeback rate {cb:.1f}% — review recent work orders"))

        # Extra notes from input
        if t.get('over_estimate_jobs'):
            lines.append(f"  Over-Estimate Jobs     : {t['over_estimate_jobs']}")
        if t.get('notes'):
            lines.append(f"  Notes                  : {t['notes']}")

    # ── Shop Totals ───────────────────────────────────────────────────────────
    if valid_techs:
        total_clocked = sum(t.get('hours_clocked', 0) for t in valid_techs)
        total_billed = sum(t.get('hours_billed', 0) for t in valid_techs)
        total_jobs = sum(t.get('jobs_completed', 0) for t in valid_techs)
        total_revenue = sum(t.get('revenue_generated', 0) for t in valid_techs)
        total_comebacks = sum(t.get('comebacks', 0) for t in valid_techs)

        shop_eff = efficiency_pct(total_billed, total_clocked)
        shop_cb = comeback_rate(total_comebacks, total_jobs)
        shop_rev_hr = revenue_per_hour(total_revenue, total_billed)

        avg_eff = (
            sum(
                efficiency_pct(t.get('hours_billed', 0), t.get('hours_clocked', 0))
                for t in valid_techs
                if t.get('hours_clocked', 0) > 0
            ) / len(valid_techs)
            if valid_techs else 0
        )

        lines.append('')
        lines.append('  ' + '=' * (W - 2))
        lines.append('  SHOP TOTALS & AVERAGES')
        lines.append('  ' + '─' * (W - 2))
        lines.append(f"  Technicians Reported   : {len(valid_techs)}")
        lines.append(f"  Total Hours Clocked    : {total_clocked:.1f} hrs")
        lines.append(f"  Total Hours Billed     : {total_billed:.1f} hrs")
        if shop_eff is not None:
            lines.append(f"  Shop Efficiency        : {shop_eff:.0f}%  (avg per tech: {avg_eff:.0f}%)")
        lines.append(f"  Total Jobs Completed   : {total_jobs}")
        lines.append(f"  Total Revenue          : ${total_revenue:,.2f}")
        if shop_rev_hr is not None:
            lines.append(f"  Revenue per Billed Hr  : ${shop_rev_hr:,.2f}/hr")
        lines.append(f"  Total Comebacks        : {total_comebacks}  ({shop_cb:.1f}%)")

    # ── Top Performer ─────────────────────────────────────────────────────────
    if top_tech:
        lines.append('')
        lines.append('  ' + '─' * (W - 2))
        lines.append(f"  TOP PERFORMER THIS PERIOD: {top_tech}  ({top_eff:.0f}% efficiency)")

    # ── Flagged Items ─────────────────────────────────────────────────────────
    if flagged:
        lines.append('')
        lines.append('  ' + '─' * (W - 2))
        lines.append('  ITEMS FLAGGED FOR REVIEW')
        lines.append('  ' + '─' * (W - 2))
        for name, issue in flagged:
            lines.append(f"  [{name}]  {issue}")
        lines.append('')
        lines.append('  Note: Flagged items are informational, not disciplinary.')
        lines.append('  Review work orders and talk with techs before drawing conclusions.')

    # ── Incomplete Data ───────────────────────────────────────────────────────
    incomplete = [t for t in techs if t.get('hours_clocked', 0) == 0]
    if incomplete:
        lines.append('')
        lines.append('  ' + '─' * (W - 2))
        lines.append('  INCOMPLETE DATA (excluded from calculations)')
        for t in incomplete:
            lines.append(f"  {t['name']} — hours_clocked is 0 or missing")

    lines.append('')
    lines.append('=' * W)

    return '\n'.join(lines)


def period_label(period, date_str):
    if not date_str:
        return period.capitalize()
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d')
        if period == 'week':
            return f"Week of {d.strftime('%B %d, %Y')}"
        elif period == 'month':
            return d.strftime('%B %Y')
        else:
            return d.strftime('%A, %B %d, %Y')
    except ValueError:
        return f"{period.capitalize()} — {date_str}"


def period_slug(period, date_str):
    if date_str:
        return f"{period}_{date_str}"
    return period


def main():
    parser = argparse.ArgumentParser(description="Generate technician productivity report")
    parser.add_argument('--period', default='week',
                        choices=['day', 'week', 'month'],
                        help="Report period: day, week, or month")
    parser.add_argument('--date', default='',
                        help="Date or week start date YYYY-MM-DD")
    parser.add_argument('--week', default='',
                        help="[Legacy] Week identifier, e.g. 2025-W15")
    # Batch JSON mode
    parser.add_argument('--technicians', default='',
                        help="JSON array of technician data objects")
    # Individual mode
    parser.add_argument('--tech', default='', help="Technician name (individual mode)")
    parser.add_argument('--hours_clocked', type=float, default=0.0)
    parser.add_argument('--hours_billed', type=float, default=0.0)
    parser.add_argument('--jobs_completed', type=int, default=0)
    parser.add_argument('--revenue_generated', '--revenue', type=float, default=0.0,
                        dest='revenue_generated')
    parser.add_argument('--comebacks', type=int, default=0)
    parser.add_argument('--over_estimate_jobs', default='',
                        help="Description of over-estimate jobs")
    parser.add_argument('--notes', default='')
    # Compile mode
    parser.add_argument('--compile', action='store_true',
                        help="Compile saved tech entries into final report")
    args = parser.parse_args()

    # Legacy --week flag support
    date_str = args.date or args.week or datetime.now().strftime('%Y-%m-%d')

    profile = load_profile()
    shop_name = profile.get('shop_name') or 'Your Shop'
    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

    plabel = period_label(args.period, date_str)
    pslug = period_slug(args.period, date_str)

    # ── BATCH JSON MODE ────────────────────────────────────────────────────────
    if args.technicians:
        try:
            techs = json.loads(args.technicians)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in --technicians: {e}", file=sys.stderr)
            print("Make sure the JSON is properly quoted and formatted.", file=sys.stderr)
            sys.exit(1)

        if not isinstance(techs, list):
            print("ERROR: --technicians must be a JSON array [...]", file=sys.stderr)
            sys.exit(1)

        # Validate each tech entry
        for t in techs:
            if 'name' not in t:
                print("ERROR: Each technician entry must have a 'name' field.", file=sys.stderr)
                sys.exit(1)

        report = build_report(techs, args.period, date_str, shop_name, plabel)
        print(report)

        fp = os.path.join(os.path.abspath(OUTPUT_DIR), f'productivity_report_{pslug}.txt')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nSaved: output/tech_productivity/productivity_report_{pslug}.txt")
        return

    # ── COMPILE MODE ───────────────────────────────────────────────────────────
    if args.compile:
        all_data = load_tech_data()
        # Filter to current period
        techs = [t for t in all_data
                 if t.get('period') == args.period and t.get('date') == date_str]
        if not techs:
            # Fall back to all saved data if no period match
            techs = all_data
            if not techs:
                print("No tech data saved. Add techs first with --tech [name] or use "
                      "--technicians JSON.", file=sys.stderr)
                sys.exit(1)
            print(f"Note: No data found for {args.period}/{date_str}, "
                  f"showing all saved data.\n")

        report = build_report(techs, args.period, date_str, shop_name, plabel)
        print(report)

        fp = os.path.join(os.path.abspath(OUTPUT_DIR), f'productivity_report_{pslug}.txt')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nSaved: output/tech_productivity/productivity_report_{pslug}.txt")
        return

    # ── INDIVIDUAL ENTRY MODE ─────────────────────────────────────────────────
    if not args.tech:
        print("ERROR: Provide --tech [name], --technicians [JSON], or --compile",
              file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    all_data = load_tech_data()

    entry = {
        'name': args.tech,
        'hours_clocked': args.hours_clocked,
        'hours_billed': args.hours_billed,
        'jobs_completed': args.jobs_completed,
        'revenue_generated': args.revenue_generated,
        'comebacks': args.comebacks,
        'over_estimate_jobs': args.over_estimate_jobs,
        'notes': args.notes,
        'period': args.period,
        'date': date_str
    }

    # Update if this tech already exists for this period/date
    updated = False
    for i, t in enumerate(all_data):
        if t.get('name') == args.tech and t.get('period') == args.period and \
                t.get('date') == date_str:
            all_data[i] = entry
            updated = True
            break
    if not updated:
        all_data.append(entry)

    save_tech_data(all_data)

    eff = efficiency_pct(args.hours_billed, args.hours_clocked)
    cb = comeback_rate(args.comebacks, args.jobs_completed)
    rev_hr = revenue_per_hour(args.revenue_generated, args.hours_billed)

    print(f"\n  Tech Data Saved: {args.tech}")
    print(f"  {'─' * 40}")
    print(f"  Hours Clocked : {args.hours_clocked:.1f}")
    print(f"  Hours Billed  : {args.hours_billed:.1f}")
    if eff is not None:
        print(f"  Efficiency    : {eff:.0f}%  {eff_flag(eff)}")
    print(f"  Jobs          : {args.jobs_completed}")
    print(f"  Revenue       : ${args.revenue_generated:,.2f}")
    if rev_hr is not None:
        print(f"  Rev/Billed Hr : ${rev_hr:,.2f}")
    print(f"  Comebacks     : {args.comebacks}  ({cb:.1f}%)")
    print(f"\n  Add more techs or run --compile to generate the report.\n")


if __name__ == '__main__':
    main()
