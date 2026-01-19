#!/usr/bin/env python3
"""
Convert EVE SDE JSON data to a simple vertical list

Takes a JSON file (like subsystem_components.json) and outputs a simple
vertical list of item names that can be easily copied and pasted into
Google Sheets or other applications.
"""

import json
import sys
from pathlib import Path


def main(input_path: str = "data/subsystem_components.json"):
    """
    Convert JSON data to a simple vertical list.

    Args:
        input_path: Path to input JSON file
    """
    in_path = Path(input_path)

    if not in_path.exists():
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Load JSON data
    with open(in_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get the components/items array
    items = None
    if 'components' in data:
        items = data['components']
    elif 'items' in data:
        items = data['items']
    elif 'ores' in data:
        items = data['ores']
    elif 'minerals' in data:
        items = data['minerals']
    else:
        print(f"ERROR: Could not find items array in JSON file", file=sys.stderr)
        sys.exit(1)

    if not items:
        print(f"ERROR: No items found in JSON file", file=sys.stderr)
        sys.exit(1)

    # Print each item name on a new line
    for item in items:
        print(item['name'])

    # Print summary to stderr so it doesn't interfere with output
    print(f"\n✓ Converted {len(items)} items to vertical list", file=sys.stderr)
    print(f"✓ Copy the output above and paste into Google Sheets", file=sys.stderr)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Convert EVE SDE JSON data to a simple vertical list'
    )
    parser.add_argument(
        'input',
        nargs='?',
        default='data/subsystem_components.json',
        help='Input JSON file (default: data/subsystem_components.json)'
    )
    args = parser.parse_args()

    main(args.input)
