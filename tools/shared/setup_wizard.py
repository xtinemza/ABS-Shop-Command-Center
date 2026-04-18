#!/usr/bin/env python3
"""
First-time shop setup wizard.
Collects all required profile fields and saves them in one pass.

Usage:
    python tools/shared/setup_wizard.py \
        --name "Mike's Auto Repair" \
        --owner "Mike Johnson" \
        --phone "(303) 555-1234" \
        --address "1234 Main St, Denver, CO 80202" \
        --location "Denver, CO" \
        --hours "Mon-Fri 7:30am-5:30pm, Sat 8am-1pm" \
        --services "Oil changes, brakes, tires, diagnostics, AC" \
        --type "Independent auto repair" \
        --website "https://mikesautorepair.com" \
        --tagline "Honest repairs, fair prices." \
        --google-review "https://g.page/r/..." \
        --tone "Professional and friendly"
"""

import json
import sys
import os
import argparse
import re

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')


def extract_city_state(address: str) -> str:
    """
    Attempt to extract 'City, ST' from a full address string.
    Falls back to the full address if pattern not found.
    """
    # Match patterns like "Denver, CO" or "Denver, CO 80202"
    match = re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})(?:\s+\d{5})?', address)
    if match:
        return f"{match.group(1).strip()}, {match.group(2)}"
    return address


def load_existing() -> dict:
    path = os.path.abspath(PROFILE_PATH)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_profile(profile: dict) -> None:
    path = os.path.abspath(PROFILE_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="First-time shop setup wizard")

    # Required fields
    parser.add_argument('--name',     required=True, help="Shop name")
    parser.add_argument('--owner',    required=True, help="Owner or manager name")
    parser.add_argument('--phone',    required=True, help="Main phone number")
    parser.add_argument('--address',  required=True, help="Full street address")

    # Auto-derived or provided
    parser.add_argument('--location', help="City, State (auto-extracted from address if omitted)")

    # Optional but recommended
    parser.add_argument('--hours',    default="", help="Business hours")
    parser.add_argument('--services', default="", help="Comma-separated list of services")
    parser.add_argument('--type',     default="Auto repair shop", help="Business type")
    parser.add_argument('--website',  default="", help="Website URL")
    parser.add_argument('--tagline',  default="", help="Shop tagline or slogan")
    parser.add_argument('--tone',     default="Professional and friendly", help="Communication tone")

    # Online presence
    parser.add_argument('--google-review', default="", help="Google review link")
    parser.add_argument('--yelp-review',   default="", help="Yelp review link")
    parser.add_argument('--facebook',      default="", help="Facebook page URL")
    parser.add_argument('--instagram',     default="", help="Instagram handle or URL")

    args = parser.parse_args()

    # Start from existing profile so we never wipe unrelated fields
    profile = load_existing()

    # Core fields
    profile['shop_name']     = args.name.strip()
    profile['owner_name']    = args.owner.strip()
    profile['phone']         = args.phone.strip()
    profile['address']       = args.address.strip()
    profile['location']      = (args.location or extract_city_state(args.address)).strip()
    profile['business_type'] = args.type.strip()
    profile['tone']          = args.tone.strip()

    # Optional fields — only overwrite if a non-empty value was provided
    if args.hours.strip():
        profile['hours'] = args.hours.strip()

    if args.services.strip():
        profile['services'] = [s.strip() for s in args.services.split(',') if s.strip()]

    if args.website.strip() and args.website.strip().lower() not in ('none', 'no', 'skip', 'n/a'):
        profile['website'] = args.website.strip()

    if args.tagline.strip() and args.tagline.strip().lower() not in ('none', 'no', 'skip', 'n/a'):
        profile['tagline'] = args.tagline.strip()

    # Review links
    review_links = profile.get('review_links', {})
    if args.google_review.strip() and args.google_review.strip().lower() not in ('none', 'no', 'skip'):
        review_links['google'] = args.google_review.strip()
    if args.yelp_review.strip() and args.yelp_review.strip().lower() not in ('none', 'no', 'skip'):
        review_links['yelp'] = args.yelp_review.strip()
    profile['review_links'] = review_links

    # Social media
    social = profile.get('social_media', {})
    if args.facebook.strip() and args.facebook.strip().lower() not in ('none', 'no', 'skip'):
        social['facebook'] = args.facebook.strip()
    if args.instagram.strip() and args.instagram.strip().lower() not in ('none', 'no', 'skip'):
        social['instagram'] = args.instagram.strip()
    profile['social_media'] = social

    # Ensure brand_colors key exists
    profile.setdefault('brand_colors', {'primary': '', 'secondary': ''})

    # Mark setup complete
    profile['setup_complete'] = True

    # Save
    try:
        save_profile(profile)
    except IOError as e:
        print(f"ERROR: Could not save profile — {e}", file=sys.stderr)
        sys.exit(1)

    # Confirmation output
    print("=" * 50)
    print("✅ SHOP PROFILE SAVED")
    print("=" * 50)
    print(f"  Shop:     {profile['shop_name']}")
    print(f"  Owner:    {profile['owner_name']}")
    print(f"  Location: {profile['location']}")
    print(f"  Phone:    {profile['phone']}")
    print(f"  Hours:    {profile.get('hours', 'Not set')}")
    print(f"  Services: {', '.join(profile.get('services', [])) or 'Not set'}")
    print(f"  Website:  {profile.get('website', 'Not set')}")
    print(f"  Tone:     {profile['tone']}")
    print(f"  Setup:    Complete ✓")
    print("=" * 50)


if __name__ == '__main__':
    main()
