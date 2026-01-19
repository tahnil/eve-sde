#!/usr/bin/env python3
"""
EVE Online SDE Group Items Extractor

Extracts items from a specific group in the EVE Online SDE.
Can be used to extract any group of items by specifying the group ID or name.

SDE Structure (JSONL - one JSON object per line):
- categories.jsonl: {_key: categoryID, name: {en: str}, ...}
- groups.jsonl: {_key: groupID, categoryID: int, name: {en: str}, ...}
- types.jsonl: {_key: typeID, groupID: int, name: {en: str}, volume: float, published: bool, ...}

Example usage:
  python3 extract_group_items.py --group-id 964 --output data/subsystem_components.json
  python3 extract_group_items.py --group-name "Hybrid Tech Components" --output data/components.json
"""

import json
import sys
from pathlib import Path


def load_jsonl(filepath: Path) -> list[dict]:
    """Load JSONL file."""
    items = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def get_name(item: dict) -> str:
    """Extract English name."""
    name = item.get('name', {})
    return name.get('en', f"Unknown_{item.get('_key', '?')}") if isinstance(name, dict) else str(name)


def main(sde_path: str = ".", output_path: str = None, group_id: int = None, group_name: str = None):
    sde = Path(sde_path)

    # Validate input
    if group_id is None and group_name is None:
        print("ERROR: Either --group-id or --group-name must be specified!", file=sys.stderr)
        sys.exit(1)

    # Load groups
    print("Loading groups...")
    groups = load_jsonl(sde / "groups.jsonl")

    # Find the target group
    group_info = None
    if group_id is not None:
        # Search by ID
        for g in groups:
            if g['_key'] == group_id:
                group_info = g
                break
    else:
        # Search by name (case-insensitive)
        search_name = group_name.lower()
        for g in groups:
            if get_name(g).lower() == search_name:
                group_info = g
                break

    if not group_info:
        if group_id:
            print(f"ERROR: Group ID {group_id} not found!", file=sys.stderr)
        else:
            print(f"ERROR: Group '{group_name}' not found!", file=sys.stderr)
        sys.exit(1)

    target_group_id = group_info['_key']
    target_group_name = get_name(group_info)

    print(f"  Found group: {target_group_name} (ID: {target_group_id})")

    # Auto-generate output path if not specified
    if output_path is None:
        safe_name = target_group_name.lower().replace(' ', '_').replace('-', '_')
        output_path = f"data/{safe_name}.json"

    # Load types
    print("\nLoading types...")
    types = load_jsonl(sde / "types.jsonl")
    print(f"  Loaded {len(types)} types")

    # Extract items from target group
    items = []

    for t in types:
        type_id = t['_key']
        item_group_id = t.get('groupID')
        name = get_name(t)
        volume = t.get('volume', 0)
        published = t.get('published', False)

        # Only published items in the target group
        if not published or item_group_id != target_group_id:
            continue

        items.append({
            'typeID': type_id,
            'name': name,
            'volume': volume,
            'groupID': item_group_id,
            'groupName': target_group_name
        })

    print(f"\nExtracted {len(items)} items from group '{target_group_name}'")

    # Sort by name
    items.sort(key=lambda x: x['name'])

    # Output
    output = {
        'metadata': {
            'source': 'EVE Online SDE',
            'groupID': target_group_id,
            'groupName': target_group_name,
            'itemCount': len(items)
        },
        'items': items
    }

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Written to {output_path}")

    # Sample
    print(f"\n=== {target_group_name} ===")
    for item in items[:20]:  # Show first 20 items
        print(f"  {item['name']} (ID: {item['typeID']}, Volume: {item['volume']} m³)")

    if len(items) > 20:
        print(f"  ... and {len(items) - 20} more items")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Extract items from a specific EVE Online SDE group'
    )
    parser.add_argument(
        '--sde-path',
        default='.',
        help='Path to SDE directory (default: current directory)'
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: auto-generated from group name)'
    )
    parser.add_argument(
        '--group-id',
        type=int,
        help='Group ID to extract (e.g., 964 for Hybrid Tech Components)'
    )
    parser.add_argument(
        '--group-name',
        help='Group name to extract (e.g., "Hybrid Tech Components")'
    )
    args = parser.parse_args()
    main(args.sde_path, args.output, args.group_id, args.group_name)
