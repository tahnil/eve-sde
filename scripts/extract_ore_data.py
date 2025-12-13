#!/usr/bin/env python3
"""
EVE Online SDE Ore & Mineral Data Extractor

SDE Structure (JSONL - one JSON object per line):
- categories.jsonl: {_key: categoryID, name: {en: str}, ...}
- groups.jsonl: {_key: groupID, categoryID: int, name: {en: str}, ...}
- types.jsonl: {_key: typeID, groupID: int, name: {en: str}, volume: float, published: bool, ...}
- typeMaterials.jsonl: {_key: typeID, materials: [{materialTypeID: int, quantity: int}, ...]}

Key IDs:
- Category 25 = "Asteroid" (all ore groups)
- Group 18 = "Mineral" (Tritanium, Pyerite, etc.)
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


def main(sde_path: str = ".", output_path: str = "data/ores.json"):
    sde = Path(sde_path)
    
    # Load groups to find ore groups (category 25 = Asteroid)
    print("Loading groups...")
    groups = load_jsonl(sde / "groups.jsonl")
    
    ore_group_ids = set()
    for g in groups:
        if g.get('categoryID') == 25:
            ore_group_ids.add(g['_key'])
            print(f"  Ore group {g['_key']}: {get_name(g)}")
    
    print(f"\nFound {len(ore_group_ids)} ore groups")
    
    # Load types
    print("\nLoading types...")
    types = load_jsonl(sde / "types.jsonl")
    print(f"  Loaded {len(types)} types")
    
    # Extract ores and minerals
    ores = []
    minerals = []
    type_lookup = {}
    
    for t in types:
        type_id = t['_key']
        group_id = t.get('groupID')
        name = get_name(t)
        volume = t.get('volume', 0)
        published = t.get('published', False)
        
        type_lookup[type_id] = {'name': name, 'groupID': group_id}
        
        if not published:
            continue
        
        # Ores: types in ore groups (category 25)
        if group_id in ore_group_ids:
            ores.append({
                'typeID': type_id,
                'name': name,
                'volume': volume,
                'groupID': group_id,
                'compressed': 'compressed' in name.lower()
            })
        
        # Minerals: group 18
        elif group_id == 18:
            minerals.append({
                'typeID': type_id,
                'name': name,
                'volume': volume
            })
    
    print(f"\nExtracted {len(ores)} ores, {len(minerals)} minerals")
    
    # Load reprocessing data
    print("\nLoading reprocessing data...")
    materials = load_jsonl(sde / "typeMaterials.jsonl")
    print(f"  Loaded {len(materials)} entries")
    
    # Build reprocessing map
    ore_ids = {o['typeID'] for o in ores}
    mineral_ids = {m['typeID'] for m in minerals}
    
    reprocessing = {}
    for mat in materials:
        type_id = mat['_key']
        if type_id not in ore_ids:
            continue
        
        yields = [
            {'mineralID': m['materialTypeID'], 'quantity': m['quantity']}
            for m in mat.get('materials', [])
            if m['materialTypeID'] in mineral_ids
        ]
        
        if yields:
            reprocessing[str(type_id)] = yields
    
    print(f"  Found reprocessing for {len(reprocessing)} ores")
    
    # Sort
    ores.sort(key=lambda x: (x['compressed'], x['name']))
    minerals.sort(key=lambda x: x['name'])
    
    # Output
    output = {
        'metadata': {
            'source': 'EVE Online SDE',
            'oreCount': len(ores),
            'mineralCount': len(minerals),
            'reprocessingCount': len(reprocessing)
        },
        'ores': ores,
        'minerals': minerals,
        'reprocessing': reprocessing
    }
    
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Written to {output_path}")
    
    # Sample
    print("\n=== Sample ===")
    print("Minerals:", [m['name'] for m in minerals[:8]])
    print("Sample ores:", [o['name'] for o in ores[:5]])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sde-path', default='.', help='Path to SDE directory')
    parser.add_argument('--output', default='data/ores.json', help='Output file')
    args = parser.parse_args()
    main(args.sde_path, args.output)