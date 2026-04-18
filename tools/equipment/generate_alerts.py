#!/usr/bin/env python3
"""
Generate equipment maintenance alerts and compliance reports.

Usage:
    python tools/equipment/generate_alerts.py
    python tools/equipment/generate_alerts.py --horizon 90
"""
import argparse, json, os, sys
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'equipment_inventory.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'equipment')
PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')

def main():
    parser = argparse.ArgumentParser(description="Generate equipment alerts")
    parser.add_argument('--horizon', type=int, default=90, help="Days ahead to check")
    args = parser.parse_args()

    data_path = os.path.abspath(DATA_FILE)
    if not os.path.exists(data_path):
        print("No equipment inventory found. Run log_equipment.py --action add first.")
        sys.exit(1)

    with open(data_path, 'r') as f: inventory = json.load(f)
    with open(os.path.abspath(PROFILE_PATH), 'r') as f: profile = json.load(f)

    now = datetime.now()
    overdue = []
    upcoming = []
    calibration_due = []

    for item in inventory:
        # Maintenance check
        if item.get('maintenance_interval_days') and item.get('last_service'):
            try:
                last = datetime.strptime(item['last_service'], '%Y-%m-%d')
                next_due = last + timedelta(days=item['maintenance_interval_days'])
                days_until = (next_due - now).days
                entry = {'name': item['name'], 'serial': item.get('serial',''), 'due': next_due.strftime('%Y-%m-%d'), 'days': days_until}
                if days_until < 0:
                    overdue.append(entry)
                elif days_until <= args.horizon:
                    upcoming.append(entry)
            except ValueError:
                pass

        # Calibration check
        if item.get('calibration_interval_days') and item.get('last_calibration'):
            try:
                last_cal = datetime.strptime(item['last_calibration'], '%Y-%m-%d')
                next_cal = last_cal + timedelta(days=item['calibration_interval_days'])
                days_cal = (next_cal - now).days
                if days_cal <= args.horizon:
                    calibration_due.append({'name': item['name'], 'due': next_cal.strftime('%Y-%m-%d'), 'days': days_cal})
            except ValueError:
                pass

    report = []
    report.append("=" * 50)
    report.append(f"EQUIPMENT MAINTENANCE ALERT REPORT")
    report.append(f"{profile.get('shop_name', '[Shop]')} — {now.strftime('%B %d, %Y')}")
    report.append("=" * 50)

    if overdue:
        report.append(f"\n🔴 OVERDUE MAINTENANCE ({len(overdue)} items)")
        report.append("-" * 40)
        for o in overdue:
            report.append(f"  {o['name']} (Serial: {o['serial']})")
            report.append(f"  Was due: {o['due']} — {abs(o['days'])} days overdue")
    else:
        report.append(f"\n✅ No overdue maintenance items")

    if upcoming:
        report.append(f"\n🟡 UPCOMING MAINTENANCE ({len(upcoming)} items)")
        report.append("-" * 40)
        for u in upcoming:
            report.append(f"  {u['name']} — Due: {u['due']} ({u['days']} days)")
    else:
        report.append(f"\n✅ No maintenance due in next {args.horizon} days")

    if calibration_due:
        report.append(f"\n🔧 CALIBRATION DUE ({len(calibration_due)} items)")
        report.append("-" * 40)
        for c in calibration_due:
            status = "OVERDUE" if c['days'] < 0 else f"{c['days']} days"
            report.append(f"  {c['name']} — Due: {c['due']} ({status})")

    report.append(f"\n{'=' * 50}")
    content = '\n'.join(report)

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)
    filepath = os.path.join(os.path.abspath(OUTPUT_DIR), 'maintenance_alerts.txt')
    with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
    print(content)
    print(f"\n✅ Saved: output/equipment/maintenance_alerts.txt")

if __name__ == '__main__':
    main()
