#!/usr/bin/env python3
"""
PDF to Images Converter using pdf2image

Convert PDF pages to images for OCR processing.
Supports converting individual books, multiple books, or all books.

Usage:
    python scripts/get_images_from_pdfs.py all                    # Convert all books
    python scripts/get_images_from_pdfs.py matthew               # Convert Matthew only
    python scripts/get_images_from_pdfs.py matthew mark luke     # Convert multiple books
    python scripts/get_images_from_pdfs.py --list                # List available books
    python scripts/get_images_from_pdfs.py --test matthew        # Convert to data/temp for testing (first 2 pages)
    python scripts/get_images_from_pdfs.py --pages 1-5 matthew    # Convert specific page range
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

from pdf2image import convert_from_path
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Performance tracking
PERF_STATS_FILE = 'data/.conversion_stats.json'

def load_performance_stats():
    """Load performance statistics from file"""
    if os.path.exists(PERF_STATS_FILE):
        try:
            with open(PERF_STATS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_performance_stats(stats):
    """Save performance statistics to file"""
    os.makedirs(os.path.dirname(PERF_STATS_FILE), exist_ok=True)
    try:
        with open(PERF_STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not save performance stats: {e}")

def estimate_conversion_time(book_name, total_pages, dpi=300, batch_size=10):
    """Estimate conversion time based on previous runs"""
    stats = load_performance_stats()

    key = f"{book_name}_{dpi}_{batch_size}"
    if key in stats:
        pages_per_sec = stats[key].get('pages_per_sec', 1.0)
        estimated_seconds = total_pages / pages_per_sec
        return estimated_seconds, pages_per_sec

    # Fallback estimates based on DPI
    if dpi >= 300:
        pages_per_sec = 0.8  # Conservative estimate for high DPI
    elif dpi >= 200:
        pages_per_sec = 1.5
    else:
        pages_per_sec = 2.5  # Faster for lower DPI

    estimated_seconds = total_pages / pages_per_sec
    return estimated_seconds, pages_per_sec

def update_performance_stats(book_name, total_pages, dpi, batch_size, actual_time):
    """Update performance statistics after conversion"""
    stats = load_performance_stats()
    key = f"{book_name}_{dpi}_{batch_size}"

    pages_per_sec = total_pages / actual_time if actual_time > 0 else 1.0

    stats[key] = {
        'pages_per_sec': pages_per_sec,
        'total_pages': total_pages,
        'dpi': dpi,
        'batch_size': batch_size,
        'last_updated': time.time()
    }

    save_performance_stats(stats)

def get_converted_pages(book_dir, expected_pages):
    """Check which pages are already converted and return missing pages"""
    converted_pages = set()

    if not os.path.exists(book_dir):
        return converted_pages

    for filename in os.listdir(book_dir):
        if filename.endswith('.png') and filename.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
            try:
                page_num = int(filename.split('.')[0])
                converted_pages.add(page_num)
            except ValueError:
                continue

    return converted_pages

def get_missing_page_ranges(expected_pages, converted_pages):
    """Get ranges of missing pages for efficient batch processing"""
    if not expected_pages:
        return []

    missing_pages = sorted(set(expected_pages) - converted_pages)
    if not missing_pages:
        return []

    # Convert to ranges
    ranges = []
    start = missing_pages[0]
    prev = missing_pages[0]

    for page in missing_pages[1:]:
        if page != prev + 1:
            ranges.append((start, prev))
            start = page
        prev = page

    ranges.append((start, prev))
    return ranges

# Available books (same as in get_hutter_pdfs.py)
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
    print("  python scripts/get_images_from_pdfs.py matthew")
    print("  python scripts/get_images_from_pdfs.py matthew mark luke")
    print("  python scripts/get_images_from_pdfs.py all")
    print("  python scripts/get_images_from_pdfs.py --test matthew")


def check_all_pdfs_integrity():
    """Check integrity of all PDF files and report results"""
    print("PDF Integrity Check")
    print("=" * 60)
    print("<15")
    print("-" * 60)

    corrupted = []
    valid = []

    for book_name in AVAILABLE_BOOKS:
        pdf_path = os.path.join('data/source', f"{book_name}.pdf")

        if not os.path.exists(pdf_path):
            print("<15")
            continue

        if check_pdf_integrity(pdf_path):
            print("<15")
            valid.append(book_name)
        else:
            print("<15")
            corrupted.append(book_name)

    print("-" * 60)
    print(f"Valid PDFs: {len(valid)}")
    print(f"Corrupted PDFs: {len(corrupted)}")

    if corrupted:
        print("\nCorrupted PDFs (need re-download):")
        for book in corrupted:
            print(f"  - {book}")
        print("\nTo re-download corrupted PDFs, run:")
        print(f"  python scripts/get_hutter_pdfs.py {' '.join(corrupted)}")
    else:
        print("\nAll PDFs are valid! ✅")


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


def parse_page_range(page_range_str):
    """Parse page range string like '1-5' or '3'"""
    if not page_range_str:
        return None

    if '-' in page_range_str:
        start, end = page_range_str.split('-')
        return int(start), int(end)
    else:
        page = int(page_range_str)
        return page, page


def check_pdf_integrity(pdf_path):
    """
    Check if a PDF file is complete and valid

    Args:
        pdf_path: Path to the PDF file

    Returns:
        bool: True if PDF appears to be complete, False otherwise
    """
    try:
        with open(pdf_path, 'rb') as f:
            # Check header
            f.seek(0)
            header = f.read(20)
            if not header.startswith(b'%PDF-'):
                return False

            # Check EOF marker at the end
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 100))
            end_content = f.read(100)
            if b'%%EOF' not in end_content:
                return False

            return True
    except Exception:
        return False


def convert_pdf_to_images(pdf_path, output_dir, book_name, page_range=None,
                         image_format='PNG', dpi=300, test_mode=False, batch_size=10, force=False):
    """
    Convert PDF pages to images with batch processing for better performance

    Args:
        pdf_path: Path to the PDF file
        output_dir: Output directory for images
        book_name: Name of the book (for directory naming)
        page_range: Tuple of (start_page, end_page) or None for all pages
        image_format: Image format ('PNG', 'JPEG', etc.)
        dpi: DPI for image conversion
        test_mode: If True, only convert first 2 pages
        batch_size: Number of pages to process at once
    """

    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return False

    # Check PDF integrity before attempting conversion
    if not check_pdf_integrity(pdf_path):
        logger.error(f"PDF file appears to be corrupted or incomplete: {pdf_path}")
        logger.error("This PDF is missing the EOF marker or has an invalid header.")
        logger.error("The file may have been downloaded incompletely.")
        return False

    # Create output directory
    book_dir = os.path.join(output_dir, book_name)
    Path(book_dir).mkdir(parents=True, exist_ok=True)

    try:
        # Determine total pages to process
        if page_range:
            start_page, end_page = page_range
            expected_pages = set(range(start_page, end_page + 1))
        else:
            # Get total pages from PDF (this is fast)
            from pdf2image import pdfinfo_from_path
            info = pdfinfo_from_path(pdf_path)
            total_pages = info["Pages"]
            expected_pages = set(range(1, total_pages + 1))

        if test_mode:
            expected_pages = set(range(1, min(3, max(expected_pages) + 1)))  # pages 1-2
            total_pages = len(expected_pages)
            logger.info("Test mode: converting only first 2 pages")

        # Check which pages are already converted
        converted_pages = get_converted_pages(book_dir, expected_pages) if not force else set()
        missing_pages = expected_pages - converted_pages

        if not missing_pages and not force:
            logger.info(f"All {len(expected_pages)} pages for {book_name} are already converted!")
            return True

        total_pages_to_convert = len(missing_pages)
        logger.info(f"Converting {pdf_path} to images ({total_pages_to_convert}/{len(expected_pages)} pages missing at {dpi} DPI)...")

        # Estimate time before starting
        estimated_time, est_pages_per_sec = estimate_conversion_time(book_name, total_pages_to_convert, dpi, batch_size)
        time_str = f"{estimated_time/60:.1f}min" if estimated_time > 60 else f"{estimated_time:.1f}s"
        logger.info(f"Estimated time: {time_str} ({est_pages_per_sec:.2f} pages/sec)")

        start_time = time.time()

        # Get ranges of missing pages for efficient processing
        missing_ranges = get_missing_page_ranges(expected_pages, converted_pages)

        # Process missing page ranges
        pages_processed = 0

        with tqdm(total=total_pages_to_convert, desc=f"Converting {book_name}", unit="pages") as pbar:
            for range_start, range_end in missing_ranges:
                range_pages = list(range(range_start, range_end + 1))

                # Process this range in batches
                for i in range(0, len(range_pages), batch_size):
                    batch_start_time = time.time()
                    batch_pages = range_pages[i:i + batch_size]

                    # Convert batch
                    pages = convert_from_path(
                        pdf_path,
                        dpi=dpi,
                        first_page=min(batch_pages),
                        last_page=max(batch_pages),
                        fmt=image_format.lower()
                    )

                    # Save batch pages
                    for j, page in enumerate(pages):
                        page_num = batch_pages[j]
                        filename = f"{page_num:06d}.png"
                        filepath = os.path.join(book_dir, filename)
                        page.save(filepath, image_format)
                        logger.debug(f"Saved page {page_num}: {filename}")

                    batch_count = len(pages)
                    pages_processed += batch_count
                    pbar.update(batch_count)

                    # Estimate remaining time
                    elapsed = time.time() - start_time
                    batch_time = time.time() - batch_start_time
                    if pages_processed > 0:
                        current_pages_per_sec = batch_count / batch_time if batch_time > 0 else 0
                        avg_pages_per_sec = pages_processed / elapsed

                        remaining_pages = total_pages_to_convert - pages_processed
                        eta_seconds = remaining_pages / avg_pages_per_sec if avg_pages_per_sec > 0 else 0
                        eta_str = f"{eta_seconds/60:.1f}min" if eta_seconds > 60 else f"{eta_seconds:.1f}s"
                        pbar.set_postfix({
                            "ETA": eta_str,
                            "avg pages/sec": f"{avg_pages_per_sec:.2f}",
                            "current": f"{current_pages_per_sec:.2f}"
                        })

        total_time = time.time() - start_time
        actual_pages_per_sec = pages_processed / total_time if total_time > 0 else 0

        logger.info(f"Successfully converted {pages_processed} pages for {book_name} in {total_time:.1f}s ({actual_pages_per_sec:.2f} pages/sec)")
        logger.info(f"Total converted: {len(expected_pages)} pages ({len(converted_pages)} already existed)")

        # Update performance statistics
        update_performance_stats(book_name, pages_processed, dpi, batch_size, total_time)

        return True

    except Exception as e:
        logger.error(f"Error converting {pdf_path}: {str(e)}")
        return False


def process_books(book_names, output_dir, page_range=None, image_format='PNG',
                 dpi=300, test_mode=False, batch_size=10, force=False):
    """
    Process multiple books for image conversion

    Args:
        book_names: List of book names to process
        output_dir: Base output directory
        page_range: Page range to convert (None for all pages)
        image_format: Image format
        dpi: DPI for conversion
        test_mode: Test mode (first 2 pages only)
    """

    success_count = 0
    corrupted_count = 0
    total_books = len(book_names)

    logger.info(f"Processing {total_books} books...")

    for book_name in book_names:
        pdf_path = os.path.join('data/source', f"{book_name}.pdf")

        logger.info(f"Processing {book_name}...")

        if convert_pdf_to_images(pdf_path, output_dir, book_name, page_range,
                               image_format, dpi, test_mode, batch_size, force):
            success_count += 1
        else:
            # Check if it was due to corruption
            if not check_pdf_integrity(pdf_path):
                corrupted_count += 1
                logger.error(f"PDF is corrupted: {book_name}")
            else:
                logger.error(f"Conversion failed for unknown reason: {book_name}")

    logger.info(f"Completed: {success_count}/{total_books} books processed successfully")
    if corrupted_count > 0:
        logger.warning(f"{corrupted_count} PDFs were corrupted and need re-download")
        logger.info("Run: python scripts/get_hutter_pdfs.py <book_names> to re-download")

    return success_count == total_books


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF pages to images using pdf2image",
        epilog="""
Examples:
  python scripts/get_images_from_pdfs.py --list                    # List all books
  python scripts/get_images_from_pdfs.py matthew                  # Convert Matthew
  python scripts/get_images_from_pdfs.py matthew mark luke        # Convert multiple books
  python scripts/get_images_from_pdfs.py all                      # Convert all books
  python scripts/get_images_from_pdfs.py --test matthew           # Test mode (first 2 pages to data/temp)
  python scripts/get_images_from_pdfs.py --pages 1-5 matthew      # Convert pages 1-5
  python scripts/get_images_from_pdfs.py --dpi 150 matthew        # Custom DPI (150-200 recommended for OCR)
  python scripts/get_images_from_pdfs.py --format JPEG matthew    # JPEG format
  python scripts/get_images_from_pdfs.py --batch-size 20 matthew  # Process 20 pages at once (faster)
  python scripts/get_images_from_pdfs.py --dpi 150 --batch-size 25 matthew  # Optimized for speed (Matthew: ~25-35min)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'books',
        nargs='*',
        help='Book names to convert (or "all" for all books)'
    )

    parser.add_argument(
        '--output', '-o',
        default='data/images/raw_images',
        help='Output directory (default: data/images/raw_images)'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: convert first 2 pages to data/temp'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available books'
    )

    parser.add_argument(
        '--check-integrity',
        action='store_true',
        help='Check PDF integrity for all books and report corrupted files'
    )

    parser.add_argument(
        '--pages',
        type=str,
        help='Page range to convert (e.g., "1-5" or "3")'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['PNG', 'JPEG', 'TIFF', 'BMP'],
        default='PNG',
        help='Image format (default: PNG)'
    )

    parser.add_argument(
        '--dpi',
        type=int,
        default=300,
        help='DPI for image conversion (default: 300, recommended: 150-200 for OCR)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of pages to process at once (default: 10, higher = faster but more memory)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-conversion of all pages (ignore existing images)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--pdf-path',
        type=str,
        help='Path to a specific PDF file to convert (for testing)'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle list command
    if args.list:
        list_books()
        return

    # Handle integrity check command
    if args.check_integrity:
        check_all_pdfs_integrity()
        return

    # Determine output directory
    output_dir = args.output
    if args.test:
        output_dir = 'data/temp'
        logger.info("Test mode: converting to data/temp")

    # Parse page range
    page_range = None
    if args.pages:
        try:
            page_range = parse_page_range(args.pages)
            logger.info(f"Converting page range: {args.pages}")
        except ValueError:
            logger.error(f"Invalid page range format: {args.pages}")
            logger.error("Use format like '1-5' or '3'")
            sys.exit(1)

    # Handle custom PDF path
    if args.pdf_path:
        if not os.path.exists(args.pdf_path):
            logger.error(f"PDF file not found: {args.pdf_path}")
            sys.exit(1)

        book_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
        logger.info(f"Processing custom PDF: {args.pdf_path}")

        success = convert_pdf_to_images(
            pdf_path=args.pdf_path,
            output_dir=output_dir,
            book_name=book_name,
            page_range=page_range,
            image_format=args.format,
            dpi=args.dpi,
            test_mode=args.test,
            batch_size=args.batch_size,
            force=args.force
        )

        if not success:
            sys.exit(1)
        return

    # Validate and get books to process
    if not args.books:
        print("Error: No books specified. Use --list to see available books.")
        print("Example: python scripts/get_images_from_pdfs.py matthew")
        sys.exit(1)

    book_names = validate_books(args.books)

    # Process books
    success = process_books(
        book_names=book_names,
        output_dir=output_dir,
        page_range=page_range,
        image_format=args.format,
        dpi=args.dpi,
        test_mode=args.test,
        batch_size=args.batch_size,
        force=args.force
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()









