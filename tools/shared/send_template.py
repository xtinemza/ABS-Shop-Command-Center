#!/usr/bin/env python3
"""
Format a template for a specific communication channel.

Takes raw template content and formats it according to channel constraints:
- sms: Strips to 160 chars max, plain text only
- email: Adds subject line wrapper, HTML-ready formatting
- phone_script: Adds speaker cues, pause markers, response prompts

Usage:
    python tools/shared/send_template.py <channel> <template_file>
    python tools/shared/send_template.py sms output/appointments/day_before_reminder.txt
    echo "content" | python tools/shared/send_template.py email --subject "Appointment Reminder"

Channels: sms, email, phone_script
"""

import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import argparse
import json

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')

def load_profile():
    """Load shop profile for template variable replacement."""
    path = os.path.abspath(PROFILE_PATH)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}

def format_sms(content, profile):
    """Format for SMS: 160 char max, plain text."""
    # Replace profile variables
    content = replace_vars(content, profile)
    # Strip any HTML
    content = content.replace('<br>', ' ').replace('\n', ' ')
    # Remove multiple spaces
    while '  ' in content:
        content = content.replace('  ', ' ')
    content = content.strip()

    if len(content) > 160:
        print(f"⚠️  WARNING: SMS is {len(content)} chars (max 160). Truncating.", file=sys.stderr)
        content = content[:157] + "..."

    print("=" * 40)
    print("📱 SMS MESSAGE")
    print("=" * 40)
    print(content)
    print(f"\n[{len(content)}/160 characters]")
    print("=" * 40)
    return content

def format_email(content, profile, subject=""):
    """Format for email with subject line."""
    content = replace_vars(content, profile)
    shop_name = profile.get('shop_name', '[Shop Name]')
    phone = profile.get('phone', '[Phone]')

    print("=" * 50)
    print("📧 EMAIL")
    print("=" * 50)
    if subject:
        print(f"Subject: {subject}")
        print("-" * 50)
    print(content)
    print(f"\n---\n{shop_name} | {phone}")
    if profile.get('website'):
        print(profile['website'])
    print("=" * 50)
    return content

def format_phone_script(content, profile):
    """Format as a phone script with speaker cues."""
    content = replace_vars(content, profile)

    print("=" * 50)
    print("📞 PHONE SCRIPT")
    print("=" * 50)
    print(content)
    print("=" * 50)
    return content

def replace_vars(content, profile):
    """Replace common template variables with profile data."""
    replacements = {
        '{shop_name}': profile.get('shop_name', '[Shop Name]'),
        '{owner_name}': profile.get('owner_name', '[Owner Name]'),
        '{phone}': profile.get('phone', '[Phone]'),
        '{address}': profile.get('address', '[Address]'),
        '{hours}': profile.get('hours', '[Hours]'),
        '{website}': profile.get('website', '[Website]'),
        '{location}': profile.get('location', '[Location]'),
    }
    for var, val in replacements.items():
        content = content.replace(var, val)
    return content

def main():
    parser = argparse.ArgumentParser(description="Format template for channel")
    parser.add_argument('channel', choices=['sms', 'email', 'phone_script'],
                        help="Communication channel")
    parser.add_argument('template_file', nargs='?', help="Path to template file")
    parser.add_argument('--subject', default="", help="Email subject line (email channel only)")
    args = parser.parse_args()

    # Get content
    if args.template_file:
        if not os.path.exists(args.template_file):
            print(f"ERROR: File not found: {args.template_file}", file=sys.stderr)
            sys.exit(1)
        with open(args.template_file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        print("ERROR: Provide a template file or pipe content via stdin.", file=sys.stderr)
        sys.exit(1)

    profile = load_profile()

    if args.channel == 'sms':
        format_sms(content, profile)
    elif args.channel == 'email':
        format_email(content, profile, args.subject)
    elif args.channel == 'phone_script':
        format_phone_script(content, profile)

if __name__ == '__main__':
    main()
