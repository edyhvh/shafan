#!/usr/bin/env python3
"""
Analyze checkpoint files to find duplicate verse keys across images.

This helps identify when Gemini is returning incorrect verse numbers,
causing the consolidator to merge unrelated verses.

Usage:
    python tools/analyze_checkpoint.py output/.checkpoints/acts_state.json
    python tools/analyze_checkpoint.py output/.checkpoints/acts_state.json --find-duplicates
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_checkpoint(checkpoint_path: Path) -> Dict[str, Any]:
    """Load checkpoint file."""
    with open(checkpoint_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_duplicate_verses(checkpoint: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Find verses with the same chapter:verse key appearing in multiple images.

    Returns:
        Dictionary mapping verse_key to list of occurrences with image info
    """
    verse_occurrences = defaultdict(list)

    images = checkpoint.get('images', {})
    for image_name, image_data in images.items():
        if image_data.get('status') != 'completed':
            continue

        verses = image_data.get('verses', {})
        for verse_key, verse_data in verses.items():
            chapter = verse_data.get('chapter')
            verse_num = verse_data.get('verse')
            text = verse_data.get('text_nikud', '')

            verse_occurrences[verse_key].append({
                'image': image_name,
                'chapter': chapter,
                'verse': verse_num,
                'text_length': len(text),
                'text_preview': text[:80] + '...' if len(text) > 80 else text
            })

    # Filter to only those with multiple occurrences
    duplicates = {
        key: occurrences
        for key, occurrences in verse_occurrences.items()
        if len(occurrences) > 1
    }

    return duplicates


def analyze_image_verse_distribution(checkpoint: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze how verses are distributed across images.

    Returns:
        Analysis report
    """
    images = checkpoint.get('images', {})
    image_stats = []

    for image_name, image_data in sorted(images.items()):
        if image_data.get('status') != 'completed':
            continue

        verses = image_data.get('verses', {})

        # Extract chapter numbers from this image
        chapters_in_image = set()
        verse_nums = []
        for verse_key, verse_data in verses.items():
            chapter = verse_data.get('chapter')
            verse_num = verse_data.get('verse')
            chapters_in_image.add(chapter)
            verse_nums.append(verse_num)

        image_stats.append({
            'image': image_name,
            'verse_count': len(verses),
            'chapters': sorted(list(chapters_in_image)),
            'verse_range': f"{min(verse_nums)}-{max(verse_nums)}" if verse_nums else "none",
            'verse_keys': sorted(verses.keys())
        })

    return {
        'total_images': len(image_stats),
        'images': image_stats
    }


def print_duplicate_report(duplicates: Dict[str, List[Dict[str, Any]]]):
    """Print report of duplicate verses."""
    if not duplicates:
        print("\nNo duplicate verses found!")
        return

    print(f"\n{'='*70}")
    print(f"DUPLICATE VERSES FOUND: {len(duplicates)} verse keys appear in multiple images")
    print(f"{'='*70}")

    # Sort by number of occurrences (most duplicated first)
    sorted_duplicates = sorted(
        duplicates.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    for verse_key, occurrences in sorted_duplicates[:20]:  # Show top 20
        print(f"\n{verse_key} appears in {len(occurrences)} images:")
        print("-" * 50)

        # Sort occurrences by image name
        for occ in sorted(occurrences, key=lambda x: x['image'])[:10]:
            print(f"  {occ['image']}: [{occ['text_length']} chars] {occ['text_preview']}")

        if len(occurrences) > 10:
            print(f"  ... and {len(occurrences) - 10} more images")

    if len(sorted_duplicates) > 20:
        print(f"\n... and {len(sorted_duplicates) - 20} more duplicate verse keys")


def print_distribution_report(distribution: Dict[str, Any]):
    """Print image verse distribution report."""
    print(f"\n{'='*70}")
    print("IMAGE VERSE DISTRIBUTION")
    print(f"{'='*70}")

    for img in distribution['images'][:30]:  # Show first 30 images
        chapters_str = ','.join(map(str, img['chapters']))
        print(f"\n{img['image']}:")
        print(f"  Chapters: {chapters_str}")
        print(f"  Verses: {img['verse_count']} ({img['verse_range']})")

    if len(distribution['images']) > 30:
        print(f"\n... and {len(distribution['images']) - 30} more images")


def generate_fix_recommendations(duplicates: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Generate recommendations for fixing duplicate verses.

    Strategy: Keep only the first occurrence (by image number) for each verse_key.
    """
    recommendations = []

    for verse_key, occurrences in duplicates.items():
        # Sort by image name (first image should be the correct one)
        sorted_occs = sorted(occurrences, key=lambda x: x['image'])

        # Keep first, remove others
        keep = sorted_occs[0]
        remove = sorted_occs[1:]

        recommendations.append({
            'verse_key': verse_key,
            'keep': {
                'image': keep['image'],
                'text_length': keep['text_length']
            },
            'remove': [
                {'image': r['image'], 'text_length': r['text_length']}
                for r in remove
            ]
        })

    return recommendations


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze checkpoint files for verse duplication issues.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'checkpoint_file',
        type=str,
        help='Path to checkpoint file (e.g., output/.checkpoints/acts_state.json)'
    )

    parser.add_argument(
        '--find-duplicates',
        action='store_true',
        help='Find verses that appear in multiple images'
    )

    parser.add_argument(
        '--show-distribution',
        action='store_true',
        help='Show verse distribution across images'
    )

    parser.add_argument(
        '--output-recommendations',
        type=str,
        help='Path to save fix recommendations (JSON file)'
    )

    args = parser.parse_args()

    # Load checkpoint
    checkpoint_path = Path(args.checkpoint_file)
    if not checkpoint_path.exists():
        logger.error(f"Checkpoint file not found: {checkpoint_path}")
        sys.exit(1)

    logger.info(f"Loading checkpoint: {checkpoint_path}")
    checkpoint = load_checkpoint(checkpoint_path)

    print(f"\nBook: {checkpoint.get('book_name')}")
    print(f"Total images: {checkpoint.get('total_images')}")
    print(f"Processed images: {checkpoint.get('processed_images')}")

    # Default behavior: show both duplicates and distribution
    if not args.find_duplicates and not args.show_distribution:
        args.find_duplicates = True
        args.show_distribution = True

    if args.find_duplicates:
        duplicates = find_duplicate_verses(checkpoint)
        print_duplicate_report(duplicates)

        if args.output_recommendations and duplicates:
            recommendations = generate_fix_recommendations(duplicates)
            with open(args.output_recommendations, 'w', encoding='utf-8') as f:
                json.dump({
                    'book_name': checkpoint.get('book_name'),
                    'total_duplicates': len(duplicates),
                    'recommendations': recommendations
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved recommendations to: {args.output_recommendations}")

    if args.show_distribution:
        distribution = analyze_image_verse_distribution(checkpoint)
        print_distribution_report(distribution)


if __name__ == "__main__":
    main()

