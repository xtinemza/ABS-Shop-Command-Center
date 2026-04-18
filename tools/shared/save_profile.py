#!/usr/bin/env python3
"""
Save or update the shop profile in data/shop_profile.json.

Usage:
    python tools/shared/save_profile.py \
        --name "Mike's Auto Repair" \
        --owner "Mike Johnson" \
        --location "Denver, CO" \
        --address "1234 Main St, Denver, CO 80202" \
        --phone "(303) 555-1234" \
        --hours "Mon-Fri 7:30am-5:30pm, Sat 8am-1pm" \
        --services "General repair, brakes, tires, oil changes, diagnostics, AC" \
        --type "Auto repair" \
        --website "https://mikesautorepair.com"
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

def main():
    parser = argparse.ArgumentParser(description="Save shop profile")
    parser.add_argument('--name', help="Shop name")
    parser.add_argument('--owner', help="Owner/manager name")
    parser.add_argument('--location', help="City, State")
    parser.add_argument('--address', help="Full street address")
    parser.add_argument('--phone', help="Main phone number")
    parser.add_argument('--hours', help="Business hours")
    parser.add_argument('--services', help="Comma-separated list of services")
    parser.add_argument('--type', help="Business type")
    parser.add_argument('--website', help="Website URL")
    parser.add_argument('--tagline', help="Shop tagline")
    parser.add_argument('--tone', help="Communication tone preference")
    parser.add_argument('--google-review', help="Google review link")
    parser.add_argument('--yelp-review', help="Yelp review link")
    parser.add_argument('--facebook', help="Facebook page URL")
    parser.add_argument('--instagram', help="Instagram handle")
    args = parser.parse_args()

    path = os.path.abspath(PROFILE_PATH)

    # Load existing profile
    profile = {}
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
        except (json.JSONDecodeError, IOError):
            profile = {}

    # Update fields (only if provided)
    if args.name:
        profile['shop_name'] = args.name
    if args.owner:
        profile['owner_name'] = args.owner
    if args.location:
        profile['location'] = args.location
    if args.address:
        profile['address'] = args.address
    if args.phone:
        profile['phone'] = args.phone
    if args.hours:
        profile['hours'] = args.hours
    if args.services:
        profile['services'] = [s.strip() for s in args.services.split(',')]
    if args.type:
        profile['business_type'] = args.type
    if args.website:
        profile['website'] = args.website
    if args.tagline:
        profile['tagline'] = args.tagline
    if args.tone:
        profile['tone'] = args.tone
    if args.google_review:
        profile.setdefault('review_links', {})['google'] = args.google_review
    if args.yelp_review:
        profile.setdefault('review_links', {})['yelp'] = args.yelp_review
    if args.facebook:
        profile.setdefault('social_media', {})['facebook'] = args.facebook
    if args.instagram:
        profile.setdefault('social_media', {})['instagram'] = args.instagram

    # Mark as setup complete if minimum fields are present
    required = ['shop_name', 'owner_name', 'location', 'phone']
    if all(profile.get(f) for f in required):
        profile['setup_complete'] = True

    # Save
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        print(f"✅ Shop profile saved: {profile.get('shop_name', 'Unknown')}")
        print(f"   Location: {profile.get('location', 'Not set')}")
        print(f"   Setup complete: {profile.get('setup_complete', False)}")
    except IOError as e:
        print(f"ERROR: Could not save profile: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
