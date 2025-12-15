#!/usr/bin/env python3
"""
EVE Online SDE Item Volume Data Extractor

Extracts volume data for all published items in EVE Online.
Useful for manufacturing, logistics, and inventory management calculations.

SDE Structure (JSONL - one JSON object per line):
- categories.jsonl: {_key: categoryID, name: {en: str}, ...}
- groups.jsonl: {_key: groupID, categoryID: int, name: {en: str}, ...}
- types.jsonl: {_key: typeID, groupID: int, name: {en: str}, volume: float, published: bool, ...}
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


def main(sde_path: str = ".", output_path: str = "data/items.json"):
    sde = Path(sde_path)

    # Load categories for metadata
    print("Loading categories...")
    categories = load_jsonl(sde / "categories.jsonl")
    category_lookup = {c['_key']: get_name(c) for c in categories}
    print(f"  Loaded {len(categories)} categories")

    # Load groups for metadata
    print("\nLoading groups...")
    groups = load_jsonl(sde / "groups.jsonl")
    group_lookup = {
        g['_key']: {
            'name': get_name(g),
            'categoryID': g.get('categoryID'),
            'categoryName': category_lookup.get(g.get('categoryID'), 'Unknown')
        }
        for g in groups
    }
    print(f"  Loaded {len(groups)} groups")

    # Load types
    print("\nLoading types...")
    types = load_jsonl(sde / "types.jsonl")
    print(f"  Loaded {len(types)} types")

    # Extract all published items with volumes
    items = []

    for t in types:
        type_id = t['_key']
        group_id = t.get('groupID')
        name = get_name(t)
        volume = t.get('volume', 0)
        published = t.get('published', False)

        # Only include published items
        if not published:
            continue

        # Get group and category info
        group_info = group_lookup.get(group_id, {'name': 'Unknown', 'categoryID': None, 'categoryName': 'Unknown'})

        items.append({
            'typeID': type_id,
            'name': name,
            'volume': volume,
            'groupID': group_id,
            'groupName': group_info['name'],
            'categoryID': group_info['categoryID'],
            'categoryName': group_info['categoryName']
        })

    print(f"\nExtracted {len(items)} published items")

    # Sort by name for easier browsing
    items.sort(key=lambda x: x['name'])

    # Gather statistics
    items_by_category = {}
    total_volume = 0
    zero_volume_count = 0

    for item in items:
        cat_name = item['categoryName']
        items_by_category[cat_name] = items_by_category.get(cat_name, 0) + 1
        total_volume += item['volume']
        if item['volume'] == 0:
            zero_volume_count += 1

    # Output
    output = {
        'metadata': {
            'source': 'EVE Online SDE',
            'itemCount': len(items),
            'categoryCount': len(items_by_category),
            'itemsWithZeroVolume': zero_volume_count,
            'categories': items_by_category
        },
        'items': items
    }

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Written to {output_path}")

    # Statistics
    print("\n=== Statistics ===")
    print(f"Total items: {len(items):,}")
    print(f"Items with zero volume: {zero_volume_count:,}")
    print(f"Items with volume: {len(items) - zero_volume_count:,}")
    print(f"\nTop 10 categories by item count:")
    sorted_cats = sorted(items_by_category.items(), key=lambda x: x[1], reverse=True)
    for cat_name, count in sorted_cats[:10]:
        print(f"  {cat_name}: {count:,} items")

    print("\n=== Sample Items ===")
    # Show a few examples from different categories
    sample_categories = ['Ship', 'Module', 'Charge', 'Commodity', 'Blueprint']
    for cat in sample_categories:
        cat_items = [i for i in items if cat in i['categoryName']]
        if cat_items:
            print(f"{cat}: {cat_items[0]['name']} (volume: {cat_items[0]['volume']})")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sde-path', default='.', help='Path to SDE directory')
    parser.add_argument('--output', default='data/items.json', help='Output file')
    args = parser.parse_args()
    main(args.sde_path, args.output)
