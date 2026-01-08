#!/usr/bin/env python3
"""
Merge Delitzsch Hebrew text into existing Hutter Polyglot Bible JSON files.

This script adds a 'text_nikud_delitzsch' field to the output/ JSON files,
containing the Hebrew text from Franz Delitzsch's translation.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load JSON file safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return None


def save_json_file(file_path: Path, data: Dict[str, Any]) -> bool:
    """Save JSON file safely."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving {file_path}: {e}")
        return False


def create_delitzsch_lookup(delitzsch_data: Dict[str, Any]) -> Dict[tuple, str]:
    """
    Create a lookup dictionary for Delitzsch verses.

    Returns:
        Dictionary with (chapter_num, verse_num) -> delitzsch_text mapping
    """
    lookup = {}

    for chapter in delitzsch_data.get('chapters', []):
        chapter_num = chapter.get('number')
        for verse in chapter.get('verses', []):
            verse_num = verse.get('number')
            text = verse.get('text_nikud', '')
            lookup[(chapter_num, verse_num)] = text

    return lookup


def merge_delitzsch_into_hutter(hutter_file: Path, delitzsch_file: Path) -> bool:
    """
    Merge Delitzsch text into Hutter JSON file.

    Args:
        hutter_file: Path to Hutter JSON file (output/)
        delitzsch_file: Path to Delitzsch JSON file (data/delitzsch/)

    Returns:
        True if merge successful, False otherwise
    """
    # Load both files
    hutter_data = load_json_file(hutter_file)
    delitzsch_data = load_json_file(delitzsch_file)

    if not hutter_data or not delitzsch_data:
        return False

    # Create Delitzsch lookup
    delitzsch_lookup = create_delitzsch_lookup(delitzsch_data)

    # Merge Delitzsch text into Hutter data
    merged_count = 0
    total_count = 0

    for chapter in hutter_data.get('chapters', []):
        chapter_num = chapter.get('number')
        for verse in chapter.get('verses', []):
            total_count += 1
            verse_num = verse.get('number')

            # Look up Delitzsch text
            delitzsch_text = delitzsch_lookup.get((chapter_num, verse_num))
            if delitzsch_text:
                verse['text_nikud_delitzsch'] = delitzsch_text
                merged_count += 1
            else:
                logger.warning(f"No Delitzsch text found for {hutter_file.name} chapter {chapter_num} verse {verse_num}")
                verse['text_nikud_delitzsch'] = ""  # Empty string for missing verses

    # Save merged data
    success = save_json_file(hutter_file, hutter_data)

    if success:
        book_name = hutter_data.get('book_name', 'unknown')
        logger.info(f"✅ Merged {merged_count}/{total_count} verses for {book_name}")

    return success


def merge_all_books(output_dir: Path = Path("output"), delitzsch_dir: Path = Path("data/delitzsch")) -> None:
    """
    Merge Delitzsch text into all available Hutter books.

    Args:
        output_dir: Directory containing Hutter JSON files
        delitzsch_dir: Directory containing Delitzsch JSON files
    """
    if not output_dir.exists():
        logger.error(f"Output directory not found: {output_dir}")
        return

    if not delitzsch_dir.exists():
        logger.error(f"Delitzsch directory not found: {delitzsch_dir}")
        return

    # Find all JSON files in both directories
    output_files = list(output_dir.glob("*.json"))
    delitzsch_files = list(delitzsch_dir.glob("*.json"))

    if not output_files:
        logger.error(f"No JSON files found in {output_dir}")
        return

    if not delitzsch_files:
        logger.error(f"No JSON files found in {delitzsch_dir}")
        return

    # Create lookup for Delitzsch files by book name
    delitzsch_by_name = {f.stem: f for f in delitzsch_files}

    logger.info(f"Found {len(output_files)} output files and {len(delitzsch_files)} Delitzsch files")

    # Process each output file
    successful = 0
    total = 0

    for output_file in output_files:
        book_name = output_file.stem
        total += 1

        # Find corresponding Delitzsch file
        delitzsch_file = delitzsch_by_name.get(book_name)
        if not delitzsch_file:
            logger.warning(f"No Delitzsch file found for book: {book_name}")
            continue

        # Merge the files
        if merge_delitzsch_into_hutter(output_file, delitzsch_file):
            successful += 1

    logger.info(f"🎉 Merge complete: {successful}/{total} books successfully merged")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Merge Delitzsch Hebrew text into Hutter Polyglot Bible JSON files"
    )

    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=Path("output"),
        help="Directory containing Hutter JSON files (default: output)"
    )

    parser.add_argument(
        '--delitzsch-dir', '-d',
        type=Path,
        default=Path("data/delitzsch"),
        help="Directory containing Delitzsch JSON files (default: data/delitzsch)"
    )

    parser.add_argument(
        '--book', '-b',
        help="Process only specific book (by filename without .json)"
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be merged without making changes"
    )

    args = parser.parse_args()

    if args.book:
        # Process single book
        output_file = args.output_dir / f"{args.book}.json"
        delitzsch_file = args.delitzsch_dir / f"{args.book}.json"

        if not output_file.exists():
            logger.error(f"Output file not found: {output_file}")
            return

        if not delitzsch_file.exists():
            logger.error(f"Delitzsch file not found: {delitzsch_file}")
            return

        if args.dry_run:
            logger.info(f"DRY RUN: Would merge {delitzsch_file} into {output_file}")
        else:
            success = merge_delitzsch_into_hutter(output_file, delitzsch_file)
            if success:
                logger.info("✅ Single book merge completed successfully")
            else:
                logger.error("❌ Single book merge failed")
    else:
        # Process all books
        if args.dry_run:
            logger.info("DRY RUN: Would merge all available books")
            merge_all_books(args.output_dir, args.delitzsch_dir)
        else:
            merge_all_books(args.output_dir, args.delitzsch_dir)


if __name__ == "__main__":
    main()