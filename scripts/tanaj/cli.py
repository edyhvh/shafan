"""Command-line interface for Tanaj text conversion."""

import argparse
import logging
import os
import sys
from pathlib import Path

from .converter import convert_book, get_available_books

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def list_books():
    """List all available books."""
    books = get_available_books()
    if not books:
        print("No books found in source directory.")
        return

    print("Available Tanaj books:")
    print("=" * 50)
    for i, book in enumerate(books, 1):
        print(f"{i:2d}. {book}")
    print("\nUsage:")
    print("  python -m scripts.tanaj --book genesis --dry-run")
    print("  python -m scripts.tanaj genesis exodus")
    print("  python -m scripts.tanaj --all")


def validate_books(book_names: list) -> list:
    """Validate book names."""
    available_books = get_available_books()
    invalid = []
    valid = []

    for book in book_names:
        if book.lower() == 'all':
            return available_books
        elif book.lower() in available_books:
            valid.append(book.lower())
        else:
            invalid.append(book)

    if invalid:
        print(f"Error: Unknown books: {', '.join(invalid)}")
        print("Use --list to see available books")
        sys.exit(1)

    return valid


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert Tanaj Hebrew text data to Shafan JSON format.",
        epilog="""
Examples:
  python -m scripts.tanaj --list                    # List books
  python -m scripts.tanaj --book genesis --dry-run  # Process 5 chapters
  python -m scripts.tanaj --book genesis            # Process one book
  python -m scripts.tanaj genesis exodus            # Multiple books
  python -m scripts.tanaj --all                     # All books

Source: ~/tanaj_source/
Output: output/
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('books', nargs='*', help='Book names to process')
    parser.add_argument('--book', '-b', type=str, help='Single book name')
    parser.add_argument('--all', action='store_true', help='Process all books')
    parser.add_argument('--list', action='store_true', help='List available books')
    parser.add_argument('--dry-run', action='store_true', help='Process only first 5 chapters per book')
    parser.add_argument('--source-dir', type=str, default=os.getenv('TANAJ_SOURCE_DIR', '~/tanaj_source'), help='Source directory (default: ~/tanaj_source)')
    parser.add_argument('--output-dir', type=str, default='output', help='Output directory (default: output)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    setup_logging(args.verbose)

    # Handle list command
    if args.list:
        list_books()
        return

    # Determine which books to process
    books_to_process = []

    if args.all:
        books_to_process = get_available_books(args.source_dir)
    elif args.book:
        books_to_process = validate_books([args.book])
    elif args.books:
        books_to_process = validate_books(args.books)
    else:
        parser.print_help()
        return

    if not books_to_process:
        print("No books to process. Use --list to see available books.")
        return

    logger.info(f"Processing {len(books_to_process)} book(s): {', '.join(books_to_process)}")

    # Process each book
    success_count = 0
    for book_name in books_to_process:
        try:
            success = convert_book(
                book_name=book_name,
                source_dir=args.source_dir,
                output_dir=args.output_dir,
                dry_run=args.dry_run
            )
            if success:
                success_count += 1
        except Exception as e:
            logger.error(f"Failed to process {book_name}: {e}")

    logger.info(f"Completed: {success_count}/{len(books_to_process)} books processed successfully")


if __name__ == '__main__':
    main()