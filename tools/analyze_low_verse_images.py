#!/usr/bin/env python3
"""
Analyze images that returned few verses to identify quality issues.

This script identifies:
- Images with abnormally low verse counts (likely transcription issues)
- Blank or very faded pages (should be excluded from processing)

Usage:
    python tools/analyze_low_verse_images.py output/.checkpoints/acts_state.json
    python tools/analyze_low_verse_images.py output/.checkpoints/acts_state.json --threshold 4
    python tools/analyze_low_verse_images.py output/.checkpoints/acts_state.json --check-images
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import Counter

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


def get_verse_counts(checkpoint: Dict[str, Any]) -> List[Tuple[str, int, Dict]]:
    """
    Get verse count for each processed image.

    Returns:
        List of tuples (image_name, verse_count, verse_data)
    """
    results = []

    images = checkpoint.get('images', {})
    for img_name, img_data in sorted(images.items()):
        if img_data.get('status') == 'completed':
            verses = img_data.get('verses', {})
            results.append((img_name, len(verses), verses))

    return results


def analyze_verse_distribution(verse_counts: List[Tuple[str, int, Dict]]) -> Dict[str, Any]:
    """
    Analyze the distribution of verse counts.

    Returns:
        Analysis dictionary
    """
    counts = [c for _, c, _ in verse_counts]

    if not counts:
        return {'error': 'No data'}

    distribution = Counter(counts)
    avg = sum(counts) / len(counts)
    median = sorted(counts)[len(counts) // 2]

    return {
        'total_images': len(counts),
        'average_verses': round(avg, 2),
        'median_verses': median,
        'min_verses': min(counts),
        'max_verses': max(counts),
        'distribution': dict(sorted(distribution.items()))
    }


def find_low_verse_images(
    verse_counts: List[Tuple[str, int, Dict]],
    threshold: int = 4
) -> List[Dict[str, Any]]:
    """
    Find images with verse count at or below threshold.

    Returns:
        List of problematic image info
    """
    low_verse_images = []

    for img_name, count, verses in verse_counts:
        if count <= threshold:
            # Get verse previews
            verse_previews = []
            for key, verse in list(verses.items())[:3]:
                text = verse.get('text_nikud', '')[:60]
                verse_previews.append(f"{key}: {text}...")

            low_verse_images.append({
                'image': img_name,
                'verse_count': count,
                'verse_keys': list(verses.keys()),
                'verse_previews': verse_previews
            })

    return low_verse_images


def check_image_quality(image_path: Path) -> Dict[str, Any]:
    """
    Check image quality metrics.

    Returns:
        Dictionary with quality metrics
    """
    try:
        from PIL import Image
        import statistics

        img = Image.open(image_path)

        # Convert to grayscale for analysis
        gray = img.convert('L')
        pixels = list(gray.getdata())

        avg_brightness = statistics.mean(pixels)
        std_brightness = statistics.stdev(pixels) if len(pixels) > 1 else 0
        min_brightness = min(pixels)
        max_brightness = max(pixels)

        # Estimate if image is blank/faded
        # A normal page has good contrast (high std deviation, typically > 35)
        # A blank/faded page has low contrast (low std deviation, typically < 20)
        is_likely_blank = std_brightness < 20

        return {
            'width': img.width,
            'height': img.height,
            'avg_brightness': round(avg_brightness, 2),
            'std_brightness': round(std_brightness, 2),
            'contrast_range': max_brightness - min_brightness,
            'is_likely_blank': is_likely_blank,
            'quality_issue': 'blank_or_faded' if is_likely_blank else None
        }

    except Exception as e:
        return {'error': str(e)}


def print_analysis(
    stats: Dict[str, Any],
    low_verse_images: List[Dict[str, Any]],
    image_quality: Dict[str, Dict[str, Any]] = None
):
    """Print the analysis report."""
    print(f"\n{'='*70}")
    print("VERSE COUNT ANALYSIS")
    print(f"{'='*70}")

    print(f"\n📊 Distribution Statistics:")
    print(f"  Total images: {stats['total_images']}")
    print(f"  Average verses per image: {stats['average_verses']}")
    print(f"  Median verses per image: {stats['median_verses']}")
    print(f"  Range: {stats['min_verses']} - {stats['max_verses']} verses")

    print(f"\n📈 Verse Count Distribution:")
    for count, num_images in sorted(stats['distribution'].items()):
        bar = '█' * min(num_images, 40)
        print(f"  {count} verses: {bar} ({num_images})")

    if not low_verse_images:
        print(f"\n✅ No images with abnormally low verse counts found!")
        return

    print(f"\n{'='*70}")
    print(f"⚠️ IMAGES WITH LOW VERSE COUNT ({len(low_verse_images)} found)")
    print(f"{'='*70}")

    # Categorize by likely issue
    blank_pages = []
    transcription_issues = []

    for img_info in low_verse_images:
        img_name = img_info['image']
        if image_quality and img_name in image_quality:
            quality = image_quality[img_name]
            if quality.get('is_likely_blank'):
                blank_pages.append((img_info, quality))
            else:
                transcription_issues.append((img_info, quality))
        else:
            transcription_issues.append((img_info, None))

    if blank_pages:
        print(f"\n🔳 BLANK/FADED PAGES (should be excluded):")
        for img_info, quality in blank_pages:
            print(f"  - {img_info['image']}: {img_info['verse_count']} verses")
            if quality:
                print(f"    Brightness: {quality['avg_brightness']}, Contrast: {quality['std_brightness']}")

    if transcription_issues:
        print(f"\n📝 TRANSCRIPTION ISSUES (need reprocessing):")
        for img_info, quality in transcription_issues:
            print(f"\n  {img_info['image']}: {img_info['verse_count']} verses")
            print(f"    Keys: {', '.join(img_info['verse_keys'])}")
            if quality:
                print(f"    Image quality: OK (brightness={quality['avg_brightness']}, contrast={quality['std_brightness']})")

    print(f"\n{'='*70}")
    print("RECOMMENDATIONS")
    print(f"{'='*70}")

    if blank_pages:
        blank_names = [img['image'] for img, _ in blank_pages]
        print(f"\n1. Exclude blank pages from processing:")
        print(f"   Add to exclusion list: {', '.join(blank_names)}")

    if transcription_issues:
        issue_names = [img['image'] for img, _ in transcription_issues]
        print(f"\n2. Reprocess images with transcription issues:")
        print(f"   python tools/fix_chapter_context.py <checkpoint> --reset-images {' '.join(issue_names)}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze images with low verse counts.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'checkpoint_file',
        type=str,
        help='Path to checkpoint file'
    )

    parser.add_argument(
        '--threshold',
        type=int,
        default=4,
        help='Verse count threshold (images at or below this are flagged)'
    )

    parser.add_argument(
        '--check-images',
        action='store_true',
        help='Also check image quality (requires PIL)'
    )

    parser.add_argument(
        '--images-dir',
        type=str,
        default='data/images/hebrew_images',
        help='Base directory containing images'
    )

    parser.add_argument(
        '--output-exclude-list',
        type=str,
        help='Output file for list of images to exclude'
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

    # Get verse counts
    verse_counts = get_verse_counts(checkpoint)

    # Analyze distribution
    stats = analyze_verse_distribution(verse_counts)

    # Find low verse images
    low_verse_images = find_low_verse_images(verse_counts, args.threshold)

    # Check image quality if requested
    image_quality = {}
    if args.check_images and low_verse_images:
        images_dir = Path(args.images_dir) / book_name
        logger.info(f"Checking image quality in: {images_dir}")

        for img_info in low_verse_images:
            img_path = images_dir / img_info['image']
            if img_path.exists():
                image_quality[img_info['image']] = check_image_quality(img_path)
            else:
                logger.warning(f"Image not found: {img_path}")

    # Print analysis
    print_analysis(stats, low_verse_images, image_quality if args.check_images else None)

    # Save exclude list if requested
    if args.output_exclude_list and image_quality:
        blank_images = [
            img_name for img_name, quality in image_quality.items()
            if quality.get('is_likely_blank')
        ]
        if blank_images:
            with open(args.output_exclude_list, 'w') as f:
                json.dump({'exclude_images': blank_images}, f, indent=2)
            logger.info(f"Saved exclude list to: {args.output_exclude_list}")


if __name__ == "__main__":
    main()

