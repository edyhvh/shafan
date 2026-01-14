#!/usr/bin/env python3
"""
Compare original and Moriah-vocalized text for Lena's data.

Generates side-by-side comparison and statistics.
"""

import csv
import sys
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def count_nikud_chars(text: str) -> int:
    """Count nikud characters in text."""
    import re
    nikud_pattern = re.compile(r'[\u0591-\u05C7]')
    return len(nikud_pattern.findall(text))


def compare_texts(original: str, vocalized: str) -> dict:
    """
    Compare two Hebrew texts and return statistics.

    Returns:
        dict with comparison metrics
    """
    original_nikud_count = count_nikud_chars(original)
    vocalized_nikud_count = count_nikud_chars(vocalized)

    # Character-level differences
    original_chars = set(original)
    vocalized_chars = set(vocalized)

    added_chars = vocalized_chars - original_chars
    removed_chars = original_chars - vocalized_chars

    return {
        'original_nikud': original_nikud_count,
        'vocalized_nikud': vocalized_nikud_count,
        'nikud_diff': vocalized_nikud_count - original_nikud_count,
        'added_chars': len(added_chars),
        'removed_chars': len(removed_chars),
        'identical': original == vocalized
    }


def compare_vocalizations():
    """Compare original and vocalized Lena data."""

    print("=" * 60)
    print("Comparing Vocalizations")
    print("=" * 60)
    print()

    # File paths
    original_csv = project_root / 'data' / 'review' / 'hutter_lena.csv'
    vocalized_csv = project_root / 'data' / 'nakdimon' / 'hutter_lena_vocalized.csv'
    comparison_output = project_root / 'data' / 'nakdimon' / 'vocalization_comparison.txt'

    # Read CSVs
    print(f"Reading {original_csv}...")
    with open(original_csv, 'r', encoding='utf-8') as f:
        original_reader = csv.DictReader(f)
        original_rows = {f"{r['book']}:{r['chapter']}:{r['verse']}": r for r in original_reader}

    print(f"Reading {vocalized_csv}...")
    with open(vocalized_csv, 'r', encoding='utf-8') as f:
        vocalized_reader = csv.DictReader(f)
        vocalized_rows = {f"{r['book']}:{r['chapter']}:{r['verse']}": r for r in vocalized_reader}

    print()

    # Compare
    comparisons = []
    stats = defaultdict(int)

    for key in original_rows:
        if key not in vocalized_rows:
            print(f"Warning: Verse {key} not found in vocalized data")
            continue

        orig_row = original_rows[key]
        voc_row = vocalized_rows[key]

        original_text = orig_row.get('corrected_text', '')
        vocalized_text = voc_row.get('corrected_text', '')

        comparison = compare_texts(original_text, vocalized_text)
        comparison['key'] = key
        comparison['original'] = original_text
        comparison['vocalized'] = vocalized_text
        comparisons.append(comparison)

        # Update statistics
        stats['total'] += 1
        if comparison['identical']:
            stats['identical'] += 1
        if comparison['nikud_diff'] > 0:
            stats['nikud_added'] += 1
        elif comparison['nikud_diff'] < 0:
            stats['nikud_removed'] += 1
        stats['total_nikud_added'] += comparison['nikud_diff']

    # Generate report
    print("Statistics:")
    print(f"  Total verses: {stats['total']}")
    print(f"  Identical: {stats['identical']} ({stats['identical']/stats['total']*100:.1f}%)")
    print(f"  With nikud added: {stats['nikud_added']}")
    print(f"  With nikud removed: {stats['nikud_removed']}")
    print(f"  Total nikud characters added: {stats['total_nikud_added']}")
    print()

    # Write detailed comparison
    print(f"Writing detailed comparison to {comparison_output}...")
    with open(comparison_output, 'w', encoding='utf-8') as f:
        f.write("Vocalization Comparison Report\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Total verses: {stats['total']}\n")
        f.write(f"Identical: {stats['identical']} ({stats['identical']/stats['total']*100:.1f}%)\n")
        f.write(f"With nikud added: {stats['nikud_added']}\n")
        f.write(f"With nikud removed: {stats['nikud_removed']}\n")
        f.write(f"Total nikud characters added: {stats['total_nikud_added']}\n\n")

        f.write("=" * 60 + "\n")
        f.write("Detailed Comparison\n")
        f.write("=" * 60 + "\n\n")

        for comp in comparisons:
            if comp['identical']:
                continue  # Skip identical verses

            f.write(f"\nVerse: {comp['key']}\n")
            f.write(f"Nikud diff: {comp['nikud_diff']:+d}\n")
            f.write(f"Original ({comp['original_nikud']} nikud):\n")
            f.write(f"  {comp['original']}\n")
            f.write(f"Vocalized ({comp['vocalized_nikud']} nikud):\n")
            f.write(f"  {comp['vocalized']}\n")
            f.write("-" * 60 + "\n")

    print(f"✓ Comparison report saved to: {comparison_output}")

    # Show sample differences
    print("\nSample differences (first 5 non-identical verses):")
    print("-" * 60)
    shown = 0
    for comp in comparisons:
        if not comp['identical'] and shown < 5:
            print(f"\n{comp['key']}:")
            print(f"  Original:  {comp['original'][:80]}...")
            print(f"  Vocalized: {comp['vocalized'][:80]}...")
            print(f"  Nikud diff: {comp['nikud_diff']:+d}")
            shown += 1


if __name__ == '__main__':
    compare_vocalizations()
