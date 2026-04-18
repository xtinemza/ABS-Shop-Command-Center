#!/usr/bin/env python3
"""
Vehicle Recall Lookup Guide — Module 8: Recall Notifications
Shop Command Center

This tool does NOT make live API calls. It generates the exact NHTSA lookup
URLs for the vehicle and, once the user has pasted in recall data, formats
it into a clean, standardized recall record.

Usage:
  # Step 1 — Generate lookup guide (open URLs in browser):
  python tools/recall/check_recalls.py --year 2019 --make Toyota --model Camry --customer "Sarah Mitchell"
  python tools/recall/check_recalls.py --vin "1HGBH41JXMN109186" --customer "Sarah Mitchell"

  # Step 2 — Format recall data once you have it from NHTSA:
  python tools/recall/check_recalls.py \\
      --year 2019 --make Toyota --model Camry --customer "Sarah Mitchell" \\
      --recall_campaign "19V123000" \\
      --component "FUEL SYSTEM, GASOLINE:FUEL PUMP" \\
      --description "The fuel pump impeller may crack and cause the engine to stall or fail to start." \\
      --consequence "Engine stall while driving increases the risk of a crash." \\
      --remedy "Toyota will replace the fuel pump free of charge."

  # If no recalls found:
  python tools/recall/check_recalls.py --year 2019 --make Toyota --model Camry --no_recalls
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
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'recall')


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_nhtsa_urls(year, make, model, vin):
    """Return the NHTSA consumer page URL and the API URL for this vehicle."""
    if vin:
        api_url = f"https://api.nhtsa.gov/recalls/recallsByVehicle?vin={vin.strip().upper()}"
        consumer_url = f"https://www.nhtsa.gov/vehicle/{vin.strip().upper()}/recalls"
    elif year and make and model:
        make_enc  = make.strip().upper().replace(' ', '%20')
        model_enc = model.strip().upper().replace(' ', '%20')
        api_url = (
            f"https://api.nhtsa.gov/recalls/recallsByVehicle"
            f"?make={make_enc}&model={model_enc}&modelYear={year}"
        )
        consumer_url = "https://www.nhtsa.gov/vehicle/recalls"
    else:
        return None, None
    return consumer_url, api_url


def generate_lookup_guide(args, profile):
    """Phase 1: Print step-by-step instructions for looking up recalls."""
    shop  = profile.get('shop_name', 'Your Shop')
    phone = profile.get('phone', '')
    today = datetime.now().strftime('%B %d, %Y')

    vin   = args.vin or ''
    year  = args.year or ''
    make  = args.make or ''
    model = args.model or ''
    customer = args.customer or 'Customer'

    if vin:
        vehicle_desc = f"VIN: {vin.upper()}"
    elif year and make and model:
        vehicle_desc = f"{year} {make} {model}"
    else:
        print("ERROR: Provide --vin OR --year/--make/--model", file=sys.stderr)
        sys.exit(1)

    consumer_url, api_url = build_nhtsa_urls(year, make, model, vin)

    lines = []
    lines.append("=" * 65)
    lines.append("  NHTSA RECALL LOOKUP GUIDE")
    lines.append(f"  {shop}")
    lines.append("=" * 65)
    lines.append(f"\n  Customer   : {customer}")
    lines.append(f"  Vehicle    : {vehicle_desc}")
    lines.append(f"  Looked Up  : {today}")

    lines.append("\n" + "─" * 65)
    lines.append("  STEP 1 — Open one of these URLs in your browser:")
    lines.append("─" * 65)
    lines.append(f"\n  Consumer Recall Page (best for browsing):")
    lines.append(f"  {consumer_url}")
    lines.append(f"\n  NHTSA API (paste into browser for raw JSON data):")
    lines.append(f"  {api_url}")

    lines.append("\n" + "─" * 65)
    lines.append("  STEP 2 — Copy the following fields for each recall found:")
    lines.append("─" * 65)
    lines.append("""
  For each recall listed, note:
    • Campaign Number   (e.g., 23V456000)
    • Component         (e.g., FUEL SYSTEM, GASOLINE:FUEL PUMP)
    • Summary/Defect    (what is wrong)
    • Consequence       (what could happen if not fixed)
    • Remedy            (what the manufacturer will do)
""")

    lines.append("─" * 65)
    lines.append("  STEP 3 — Run this command with the recall data:")
    lines.append("─" * 65)

    if vin:
        vehicle_args = f'--vin "{vin}"'
    else:
        vehicle_args = f'--year {year} --make "{make}" --model "{model}"'

    lines.append(f"""
  python tools/recall/check_recalls.py \\
      {vehicle_args} \\
      --customer "{customer}" \\
      --recall_campaign "CAMPAIGN_NUMBER" \\
      --component "COMPONENT_NAME" \\
      --description "DEFECT_DESCRIPTION" \\
      --consequence "CONSEQUENCE_DESCRIPTION" \\
      --remedy "REMEDY_DESCRIPTION"

  If NO recalls are found, run:
  python tools/recall/check_recalls.py {vehicle_args} --customer "{customer}" --no_recalls
""")

    lines.append("─" * 65)
    lines.append("  STEP 4 — Then generate customer notifications:")
    lines.append("─" * 65)
    lines.append(f"""
  python tools/recall/generate_notifications.py \\
      --customer "{customer}" \\
      --vehicle "{vehicle_desc.replace('VIN: ', '')}" \\
      --recall_campaign "CAMPAIGN_NUMBER" \\
      --component "COMPONENT_NAME" \\
      --description "DEFECT_DESCRIPTION" \\
      --remedy "REMEDY_DESCRIPTION" \\
      --urgency medium
""")
    lines.append("=" * 65)

    return "\n".join(lines)


def generate_recall_record(args, profile):
    """Phase 2: Format a confirmed recall into a clean record."""
    shop     = profile.get('shop_name', 'Your Shop')
    phone    = profile.get('phone', '')
    today    = datetime.now().strftime('%B %d, %Y')
    customer = args.customer or 'Customer'

    vin   = args.vin or ''
    year  = args.year or ''
    make  = args.make or ''
    model = args.model or ''

    if vin:
        vehicle_desc = f"VIN: {vin.upper()}"
    elif year and make and model:
        vehicle_desc = f"{year} {make} {model}"
    else:
        print("ERROR: Provide --vin OR --year/--make/--model", file=sys.stderr)
        sys.exit(1)

    lines = []
    lines.append("=" * 65)
    lines.append("  NHTSA RECALL RECORD — CONFIRMED")
    lines.append(f"  {shop}")
    lines.append("=" * 65)
    lines.append(f"\n  Customer       : {customer}")
    lines.append(f"  Vehicle        : {vehicle_desc}")
    lines.append(f"  Date Checked   : {today}")
    lines.append(f"  Checked By     : {shop} Service Team")
    lines.append("\n" + "─" * 65)
    lines.append("  RECALL DETAILS")
    lines.append("─" * 65)
    lines.append(f"  Campaign #     : {args.recall_campaign}")
    lines.append(f"  Component      : {args.component}")
    lines.append(f"\n  DEFECT:")
    lines.append(f"  {args.description}")
    lines.append(f"\n  CONSEQUENCE:")
    lines.append(f"  {args.consequence}")
    lines.append(f"\n  REMEDY (at no charge to owner):")
    lines.append(f"  {args.remedy}")
    lines.append("\n" + "─" * 65)
    lines.append("  NEXT STEPS")
    lines.append("─" * 65)
    lines.append(f"""
  1. Generate customer notifications:
     python tools/recall/generate_notifications.py \\
         --customer "{customer}" \\
         --vehicle "{vehicle_desc.replace('VIN: ', '')}" \\
         --recall_campaign "{args.recall_campaign}" \\
         --component "{args.component}" \\
         --description "{args.description}" \\
         --remedy "{args.remedy}" \\
         --urgency medium

  2. Contact customer via SMS, email, or phone (use generated templates).
  3. Schedule appointment to perform recall work.
  4. Add recall record to customer file.
""")
    lines.append(f"  Source: NHTSA — https://www.nhtsa.gov/recalls")
    lines.append("=" * 65)

    return "\n".join(lines)


def generate_no_recall_record(args, profile):
    """Generate a clean 'no recalls found' record for documentation."""
    shop     = profile.get('shop_name', 'Your Shop')
    today    = datetime.now().strftime('%B %d, %Y')
    customer = args.customer or 'Customer'

    vin   = args.vin or ''
    year  = args.year or ''
    make  = args.make or ''
    model = args.model or ''

    if vin:
        vehicle_desc = f"VIN: {vin.upper()}"
    elif year and make and model:
        vehicle_desc = f"{year} {make} {model}"
    else:
        vehicle_desc = "Unknown Vehicle"

    lines = []
    lines.append("=" * 65)
    lines.append("  NHTSA RECALL CHECK — NO OPEN RECALLS")
    lines.append(f"  {shop}")
    lines.append("=" * 65)
    lines.append(f"\n  Customer       : {customer}")
    lines.append(f"  Vehicle        : {vehicle_desc}")
    lines.append(f"  Date Checked   : {today}")
    lines.append(f"  Result         : NO OPEN RECALLS FOUND")
    lines.append(f"\n  This vehicle has no open safety recalls in the NHTSA database")
    lines.append(f"  as of {today}.")
    lines.append(f"\n  Note: Recalls are issued continuously. Check again if the")
    lines.append(f"  customer reports any safety-related symptoms or concerns.")
    lines.append(f"\n  Verified at: https://www.nhtsa.gov/recalls")
    lines.append("=" * 65)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Vehicle recall lookup guide and record formatter — Module 8"
    )
    # Vehicle identification
    parser.add_argument('--vin',   help="Vehicle VIN (17 characters)")
    parser.add_argument('--year',  help="Model year (e.g. 2019)")
    parser.add_argument('--make',  help="Manufacturer (e.g. Toyota)")
    parser.add_argument('--model', help="Model name (e.g. Camry)")

    # Customer
    parser.add_argument('--customer', default='', help="Customer name for the record")

    # Recall data fields (optional — omit to generate lookup guide only)
    parser.add_argument('--recall_campaign', default='', help="NHTSA Campaign Number (e.g. 19V123000)")
    parser.add_argument('--component',       default='', help="Component affected")
    parser.add_argument('--description',     default='', help="Defect description")
    parser.add_argument('--consequence',     default='', help="Consequence of defect")
    parser.add_argument('--remedy',          default='', help="Manufacturer remedy")

    # Result flags
    parser.add_argument('--no_recalls', action='store_true',
                        help="Flag that NHTSA returned no open recalls for this vehicle")

    args = parser.parse_args()

    # Validate we have at least a vehicle identifier
    if not args.vin and not (args.year and args.make and args.model):
        parser.print_help()
        print("\nERROR: Provide --vin OR all three of --year / --make / --model", file=sys.stderr)
        sys.exit(1)

    profile = load_profile()
    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

    # Determine mode
    has_recall_data = bool(args.recall_campaign and args.component and args.description)

    if args.no_recalls:
        content = generate_no_recall_record(args, profile)
        filename = "recall_check_no_recalls.txt"
        print(content)
        print(f"\nResult: No open recalls. Documentation saved.")

    elif has_recall_data:
        content = generate_recall_record(args, profile)
        safe_campaign = args.recall_campaign.replace('/', '-').replace(' ', '_')
        filename = f"recall_record_{safe_campaign}.txt"
        print(content)
        print(f"\nRecall record formatted. Run generate_notifications.py to create customer alerts.")

    else:
        content = generate_lookup_guide(args, profile)
        filename = "recall_lookup_guide.txt"
        print(content)
        print(f"\nLookup guide ready. Open the URLs above, then re-run with --recall_campaign etc.")

    filepath = os.path.join(os.path.abspath(OUTPUT_DIR), filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: output/recall/{filename}")


if __name__ == '__main__':
    main()
