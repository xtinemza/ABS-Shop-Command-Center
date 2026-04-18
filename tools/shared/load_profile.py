#!/usr/bin/env python3
"""
Load and display the shop profile from data/shop_profile.json.

Usage:
    python tools/shared/load_profile.py
    python tools/shared/load_profile.py --field shop_name
    python tools/shared/load_profile.py --check
"""

import json
import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import argparse

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')

def load_profile():
    """Load and return the shop profile dict."""
    path = os.path.abspath(PROFILE_PATH)
    if not os.path.exists(path):
        print("ERROR: shop_profile.json not found at", path, file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in shop_profile.json: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Load shop profile")
    parser.add_argument('--field', help="Return a specific field value")
    parser.add_argument('--check', action='store_true', help="Check if profile is set up")
    args = parser.parse_args()

    profile = load_profile()

    if args.check:
        if profile.get('setup_complete') and profile.get('shop_name'):
            print("READY")
            print(f"Shop: {profile['shop_name']}")
        else:
            print("NOT_SETUP")
        return

    if args.field:
        value = profile.get(args.field, "")
        if isinstance(value, (dict, list)):
            print(json.dumps(value, indent=2))
        else:
            print(value)
        return

    # Print full profile
    print("=" * 50)
    print("SHOP PROFILE")
    print("=" * 50)
    for key, value in profile.items():
        if isinstance(value, dict):
            print(f"\n{key.upper().replace('_', ' ')}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        elif isinstance(value, list):
            print(f"\n{key.upper().replace('_', ' ')}:")
            for item in value:
                print(f"  - {item}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
    print("=" * 50)

if __name__ == '__main__':
    main()
