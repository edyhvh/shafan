#!/usr/bin/env python3
"""
Fix chapter context issues by reprocessing images with correct chapter information.

The problem: Gemini doesn't know which chapter it's processing because the chapter
marker may be on a previous page. This script:
1. Analyzes the checkpoint to find images with duplicate verse keys
2. Allows reprocessing those specific images with chapter context provided

Usage:
    # Analyze and show what needs fixing
    python tools/fix_chapter_context.py output/.checkpoints/acts_state.json --analyze

    # Generate a mapping file of image -> expected chapter
    python tools/fix_chapter_context.py output/.checkpoints/acts_state.json --generate-mapping

    # Reprocess specific images with correct chapter context
    python tools/fix_chapter_context.py output/.checkpoints/acts_state.json --fix --images 000048.png 000068.png
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
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


def save_checkpoint(checkpoint: Dict[str, Any], checkpoint_path: Path):
    """Save checkpoint file."""
    with open(checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2, ensure_ascii=False)


def find_problematic_images(checkpoint: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Find images that have verse keys that appear in other images.

    Returns:
        Dictionary mapping image name to list of duplicate verse keys
    """
    # First, collect all verse keys and their source images
    verse_to_images: Dict[str, List[str]] = defaultdict(list)

    images = checkpoint.get('images', {})
    for image_name, image_data in images.items():
        if image_data.get('status') != 'completed':
            continue

        verses = image_data.get('verses', {})
        for verse_key in verses.keys():
            verse_to_images[verse_key].append(image_name)

    # Find which verse keys are duplicates
    duplicate_keys = {
        key: imgs for key, imgs in verse_to_images.items()
        if len(imgs) > 1
    }

    # Map each image to its duplicate verse keys
    problematic_images: Dict[str, List[str]] = defaultdict(list)
    for verse_key, images_list in duplicate_keys.items():
        for img in images_list:
            problematic_images[img].append(verse_key)

    return dict(problematic_images)


def find_low_verse_images(checkpoint: Dict[str, Any], threshold: int = 4) -> Dict[str, int]:
    """
    Find images with verse count at or below threshold.

    Returns:
        Dictionary mapping image name to verse count
    """
    low_verse_images = {}

    images = checkpoint.get('images', {})
    for image_name, image_data in images.items():
        if image_data.get('status') != 'completed':
            continue

        verses = image_data.get('verses', {})
        count = len(verses)

        if count <= threshold:
            low_verse_images[image_name] = count

    return low_verse_images


def estimate_chapter_for_image(
    image_name: str,
    checkpoint: Dict[str, Any],
    total_chapters: int = 28  # Acts has 28 chapters
) -> int:
    """
    Estimate which chapter an image belongs to based on its position.

    This is a rough estimate based on assuming chapters are evenly distributed.
    """
    images = checkpoint.get('images', {})
    sorted_images = sorted(images.keys())

    if image_name not in sorted_images:
        return 1

    idx = sorted_images.index(image_name)
    total_images = len(sorted_images)

    # Estimate chapter based on position
    estimated_chapter = max(1, int((idx / total_images) * total_chapters) + 1)
    return min(estimated_chapter, total_chapters)


def generate_image_chapter_mapping(
    checkpoint: Dict[str, Any],
    problematic_images: Dict[str, List[str]]
) -> Dict[str, Dict[str, Any]]:
    """
    Generate a mapping file showing each problematic image and its estimated chapter.

    Returns a dictionary that can be manually edited to correct chapter assignments.
    """
    mapping = {}

    for image_name in sorted(problematic_images.keys()):
        estimated_chapter = estimate_chapter_for_image(image_name, checkpoint)
        duplicate_keys = problematic_images[image_name]

        # Get the verses from this image
        image_data = checkpoint.get('images', {}).get(image_name, {})
        verses = image_data.get('verses', {})

        verse_previews = []
        for key, verse in list(verses.items())[:3]:  # First 3 verses
            text = verse.get('text_nikud', '')[:50]
            verse_previews.append(f"{key}: {text}...")

        mapping[image_name] = {
            'estimated_chapter': estimated_chapter,
            'duplicate_verse_keys': duplicate_keys,
            'verse_count': len(verses),
            'verse_previews': verse_previews,
            'needs_review': True,
            'confirmed_chapter': None  # User fills this in
        }

    return mapping


def remove_image_from_checkpoint(
    checkpoint: Dict[str, Any],
    image_name: str
) -> bool:
    """
    Remove an image from the checkpoint so it can be reprocessed.

    Returns True if successful.
    """
    if 'images' not in checkpoint:
        return False

    if image_name not in checkpoint['images']:
        logger.warning(f"Image {image_name} not found in checkpoint")
        return False

    del checkpoint['images'][image_name]

    # Update counts
    if 'processed_images' in checkpoint:
        checkpoint['processed_images'] = max(0, checkpoint['processed_images'] - 1)

    return True


def print_analysis(problematic_images: Dict[str, List[str]], checkpoint: Dict[str, Any]):
    """Print analysis of problematic images."""
    print(f"\n{'='*70}")
    print("PROBLEMATIC IMAGES ANALYSIS")
    print(f"{'='*70}")

    print(f"\nTotal problematic images: {len(problematic_images)}")

    # Group by estimated chapter
    by_estimated_chapter: Dict[int, List[str]] = defaultdict(list)
    for img in problematic_images:
        chapter = estimate_chapter_for_image(img, checkpoint)
        by_estimated_chapter[chapter].append(img)

    print(f"\nImages grouped by estimated chapter:")
    for chapter in sorted(by_estimated_chapter.keys()):
        imgs = by_estimated_chapter[chapter]
        print(f"\n  Chapter ~{chapter}: {len(imgs)} images")
        for img in sorted(imgs)[:5]:
            dup_keys = problematic_images[img]
            print(f"    - {img}: {len(dup_keys)} duplicate keys ({', '.join(dup_keys[:3])}...)")
        if len(imgs) > 5:
            print(f"    ... and {len(imgs) - 5} more")

    print(f"\n{'='*70}")
    print("RECOMMENDATION")
    print(f"{'='*70}")
    print("""
The issue is that Gemini is not correctly identifying chapter numbers.
To fix this, you need to:

1. Generate a mapping file:
   python tools/fix_chapter_context.py <checkpoint> --generate-mapping -o mapping.json

2. Manually review and correct the chapter assignments in mapping.json

3. Use the corrected mapping to reprocess the images:
   python tools/fix_chapter_context.py <checkpoint> --fix --mapping mapping.json

OR for a simpler approach:

4. Mark specific images for reprocessing (removes them from checkpoint):
   python tools/fix_chapter_context.py <checkpoint> --reset-images 000048.png 000068.png

5. Then run the main script with --reprocess-failed or --resume
""")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Fix chapter context issues in processed images.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'checkpoint_file',
        type=str,
        help='Path to checkpoint file (e.g., output/.checkpoints/acts_state.json)'
    )

    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze and show problematic images'
    )

    parser.add_argument(
        '--generate-mapping',
        action='store_true',
        help='Generate a mapping file for manual chapter correction'
    )

    parser.add_argument(
        '--reset-images',
        nargs='+',
        help='Reset specific images (remove from checkpoint for reprocessing)'
    )

    parser.add_argument(
        '--reset-all-problematic',
        action='store_true',
        help='Reset ALL problematic images (removes them from checkpoint for reprocessing)'
    )

    parser.add_argument(
        '--reset-low-verse',
        type=int,
        metavar='THRESHOLD',
        help='Also reset images with verse count at or below THRESHOLD (e.g., --reset-low-verse 4)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path for mapping'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be reset without actually modifying the checkpoint'
    )

    args = parser.parse_args()

    # Load checkpoint
    checkpoint_path = Path(args.checkpoint_file)
    if not checkpoint_path.exists():
        logger.error(f"Checkpoint file not found: {checkpoint_path}")
        sys.exit(1)

    logger.info(f"Loading checkpoint: {checkpoint_path}")
    checkpoint = load_checkpoint(checkpoint_path)

    book_name = checkpoint.get('book_name', 'unknown')
    print(f"\nBook: {book_name}")
    print(f"Total images: {checkpoint.get('total_images')}")
    print(f"Processed images: {checkpoint.get('processed_images')}")

    # Find problematic images (duplicate verse keys)
    problematic = find_problematic_images(checkpoint)

    # Find low verse images if threshold specified
    low_verse = {}
    if args.reset_low_verse:
        low_verse = find_low_verse_images(checkpoint, args.reset_low_verse)
        print(f"\n⚠️ Found {len(low_verse)} images with ≤{args.reset_low_verse} verses")

    if not problematic and not low_verse:
        print("\n✅ No problematic images found!")
        return

    if problematic:
        print(f"\n⚠️ Found {len(problematic)} images with duplicate verse keys")

    # Handle different modes
    if args.analyze:
        print_analysis(problematic, checkpoint)

    elif args.generate_mapping:
        mapping = generate_image_chapter_mapping(checkpoint, problematic)
        output_path = Path(args.output) if args.output else Path(f"output/{book_name}_chapter_mapping.json")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved mapping to: {output_path}")
        print(f"\n📄 Mapping file created: {output_path}")
        print("Please review and edit 'confirmed_chapter' for each image, then use --fix")

    elif args.reset_images or args.reset_all_problematic or args.reset_low_verse:
        images_to_reset = set()

        if args.reset_all_problematic and problematic:
            images_to_reset.update(problematic.keys())
            print(f"\n⚠️ Will reset {len(problematic)} images with duplicate verse keys")

        if args.reset_low_verse and low_verse:
            new_low_verse = set(low_verse.keys()) - images_to_reset
            images_to_reset.update(low_verse.keys())
            if new_low_verse:
                print(f"⚠️ Will also reset {len(new_low_verse)} additional images with ≤{args.reset_low_verse} verses")

        if args.reset_images:
            images_to_reset.update(args.reset_images)

        images_to_reset = list(images_to_reset)

        if not images_to_reset:
            print("\n❌ No images to reset")
            return

        print(f"\n📋 Total images to reset: {len(images_to_reset)}")

        if args.dry_run:
            print(f"\n🔍 DRY RUN - Would reset {len(images_to_reset)} images:")
            for img in sorted(images_to_reset)[:20]:
                print(f"  - {img}")
            if len(images_to_reset) > 20:
                print(f"  ... and {len(images_to_reset) - 20} more")
            print("\nRun without --dry-run to actually reset them.")
            return

        reset_count = 0
        for img in images_to_reset:
            if remove_image_from_checkpoint(checkpoint, img):
                logger.info(f"Reset: {img}")
                reset_count += 1
            else:
                logger.warning(f"Could not reset: {img}")

        if reset_count > 0:
            save_checkpoint(checkpoint, checkpoint_path)
            print(f"\n✅ Reset {reset_count} images. They will be reprocessed on next run.")
            print(f"\nNext steps:")
            print(f"  python scripts/hebrew_text/main.py --book {book_name} --resume")
        else:
            print("\n❌ No images were reset")

    else:
        # Default: show summary
        print_analysis(problematic, checkpoint)


if __name__ == "__main__":
    main()

