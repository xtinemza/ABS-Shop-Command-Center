#!/usr/bin/env python3
"""
Save output content to a file in the output/ directory.

Usage:
    python tools/shared/save_output.py <module_folder> <filename> "content"
    echo "content" | python tools/shared/save_output.py <module_folder> <filename>

Examples:
    python tools/shared/save_output.py appointments day_before_reminder_sms.txt "Hi {name}, reminder..."
    echo "template content" | python tools/shared/save_output.py welcome_kit welcome_letter.txt
"""

import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'output')

def main():
    if len(sys.argv) < 3:
        print("Usage: save_output.py <module_folder> <filename> [content]", file=sys.stderr)
        print("  Content can also be piped via stdin.", file=sys.stderr)
        sys.exit(1)

    module_folder = sys.argv[1]
    filename = sys.argv[2]

    # Get content from argument or stdin
    if len(sys.argv) >= 4:
        content = sys.argv[3]
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        print("ERROR: No content provided. Pass as argument or pipe via stdin.", file=sys.stderr)
        sys.exit(1)

    # Build output path
    output_path = os.path.abspath(os.path.join(OUTPUT_DIR, module_folder, filename))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Saved: output/{module_folder}/{filename}")
        print(f"   Path: {output_path}")
        print(f"   Size: {len(content)} characters")
    except IOError as e:
        print(f"ERROR: Could not save file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
