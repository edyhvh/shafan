#!/usr/bin/env python3
"""
Script to extract Hebrew text columns from biblical manuscript images using dynamic OpenCV detection.

This script processes images, detects the central Hebrew text column (including title),
and crops them dynamically. It handles variations in page layout and falls back to
approximate coordinates if detection fails.

Supports processing individual books, multiple books, or all books.

Usage:
    python scripts/hebrew_images/main.py all                    # Process all books
    python scripts/hebrew_images/main.py matthew                # Process Matthew only
    python scripts/hebrew_images/main.py matthew mark luke      # Process multiple books
    python scripts/hebrew_images/main.py --list                # List available books
    python -m scripts.hebrew_images.main all                   # Also works as module
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Handle both module and standalone execution
try:
    from .extractor import HebrewTextExtractor
    from .logger import setup_logging
except ImportError:
    # If running as standalone script, add parent directory to path
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir.parent.parent))
    from scripts.hebrew_images.extractor import HebrewTextExtractor
    from scripts.hebrew_images.logger import setup_logging

# Setup logging
logger = setup_logging(verbose=False)

# Available books (same as in get_images_from_pdfs.py)
AVAILABLE_BOOKS = [
    'matthew', 'mark', 'luke', 'john', 'acts', 'romans',
    'corinthians1', 'corinthians2', 'galatians', 'ephesians',
    'philippians', 'colossians', 'thessalonians1', 'thessalonians2',
    'timothy1', 'timothy2', 'titus', 'philemon', 'hebrews',
    'james', 'peter1', 'peter2', 'john1', 'john2', 'john3',
    'jude', 'revelation'
]


def list_books():
    """List all available books"""
    print("Available books:")
    print("=" * 50)
    for i, book in enumerate(AVAILABLE_BOOKS, 1):
        print(f"{i:2d}. {book}")
    print("\nUsage examples:")
    print("  python scripts/hebrew_images/main.py matthew")
    print("  python scripts/hebrew_images/main.py matthew mark luke")
    print("  python scripts/hebrew_images/main.py all")


def validate_books(book_names):
    """Validate that requested books exist"""
    invalid_books = []
    valid_books = []

    for book in book_names:
        if book.lower() == 'all':
            return AVAILABLE_BOOKS
        elif book.lower() in AVAILABLE_BOOKS:
            valid_books.append(book.lower())
        else:
            invalid_books.append(book)

    if invalid_books:
        print(f"Error: Unknown books: {', '.join(invalid_books)}")
        print("Use --list to see available books")
        sys.exit(1)

    return valid_books


def process_book(book_name, input_base_dir, output_base_dir):
    """
    Process a single book for Hebrew text extraction.

    Args:
        book_name: Name of the book to process
        input_base_dir: Base directory containing raw images (e.g., data/images/raw_images)
        output_base_dir: Base directory for output (e.g., data/images/hebrew_images)

    Returns:
        bool: True if processing was successful, False otherwise
    """
    input_dir = Path(input_base_dir) / book_name
    output_dir = Path(output_base_dir) / book_name

    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        logger.error(f"Make sure you have run: python scripts/get_images_from_pdfs.py {book_name}")
        return False

    if not any(input_dir.iterdir()):
        logger.warning(f"Input directory is empty: {input_dir}")
        return False

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Processing {book_name}...")
    logger.info(f"  Input: {input_dir}")
    logger.info(f"  Output: {output_dir}")

    try:
        extractor = HebrewTextExtractor(input_dir, output_dir)
        extractor.process_all_images()
        logger.info(f"Successfully processed {book_name}")
        return True
    except Exception as e:
        logger.error(f"Error processing {book_name}: {str(e)}")
        return False


def process_books(book_names, input_base_dir, output_base_dir):
    """
    Process multiple books for Hebrew text extraction.

    Args:
        book_names: List of book names to process
        input_base_dir: Base directory containing raw images
        output_base_dir: Base directory for output

    Returns:
        bool: True if all books were processed successfully, False otherwise
    """
    success_count = 0
    total_books = len(book_names)

    logger.info(f"Processing {total_books} books...")

    for book_name in book_names:
        if process_book(book_name, input_base_dir, output_base_dir):
            success_count += 1

    logger.info(f"Completed: {success_count}/{total_books} books processed successfully")

    return success_count == total_books


def main():
    parser = argparse.ArgumentParser(
        description="Extract Hebrew text columns from images.",
        epilog="""
Examples:
  python scripts/hebrew_images/main.py --list                    # List all books
  python scripts/hebrew_images/main.py matthew                  # Process Matthew
  python scripts/hebrew_images/main.py matthew mark luke        # Process multiple books
  python scripts/hebrew_images/main.py all                      # Process all books
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'books',
        nargs='*',
        help='Book names to process (or "all" for all books)'
    )

    parser.add_argument(
        '--input-dir',
        type=str,
        default='data/images/raw_images',
        help='Base directory containing raw images (default: data/images/raw_images)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/images/hebrew_images',
        help='Base directory for output (default: data/images/hebrew_images)'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available books'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle list command
    if args.list:
        list_books()
        return

    # Validate and get books to process
    if not args.books:
        print("Error: No books specified. Use --list to see available books.")
        print("Example: python scripts/hebrew_images/main.py matthew")
        sys.exit(1)

    book_names = validate_books(args.books)

    # Process books
    success = process_books(
        book_names=book_names,
        input_base_dir=args.input_dir,
        output_base_dir=args.output_dir
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
