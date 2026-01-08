"""Command-line interface for Delitzsch Hebrew New Testament extraction."""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from .constants import DEFAULT_OUTPUT_DIR, DEFAULT_REPO_DIR, NEW_TESTAMENT_BOOKS
from .converter import convert_books_to_json, validate_all_converted_books
from .downloader import ensure_repository, locate_delitzsch_files
from .parser import parse_html_files

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    for pkg, name in [('bs4', 'beautifulsoup4'), ('lxml', 'lxml')]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(name)

    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.info(f"Install with: pip install {' '.join(missing)}")
        sys.exit(1)


def check_dependencies_optional():
    """Check if required packages are installed, but don't exit."""
    missing = []
    for pkg, name in [('bs4', 'beautifulsoup4'), ('lxml', 'lxml')]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(name)

    return missing


def list_books():
    """List all available New Testament books."""
    print("Available Delitzsch Hebrew New Testament books:")
    print("=" * 60)
    for i, (book_key, book_name) in enumerate(NEW_TESTAMENT_BOOKS.items(), 1):
        print(f"{i:2d}. {book_key} ({book_name})")
    print("\nUsage:")
    print("  python -m scripts.delitzsch --list                    # List books")
    print("  python -m scripts.delitzsch --book matthew           # Process one book")
    print("  python -m scripts.delitzsch matthew mark luke        # Multiple books")
    print("  python -m scripts.delitzsch --all                    # All books")
    print("  python -m scripts.delitzsch --all --dry-run          # Test run")


def validate_books(book_names: List[str]) -> List[str]:
    """Validate book names."""
    invalid = []
    valid = []

    for book in book_names:
        if book.lower() == 'all':
            return list(NEW_TESTAMENT_BOOKS.keys())
        elif book.lower() in NEW_TESTAMENT_BOOKS:
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
        description="Extract Delitzsch Hebrew New Testament from GitHub repository.",
        epilog="""
Examples:
  python -m scripts.delitzsch --list                    # List books
  python -m scripts.delitzsch --book matthew           # Process Matthew
  python -m scripts.delitzsch matthew mark luke        # Multiple books
  python -m scripts.delitzsch --all                    # All books
  python -m scripts.delitzsch --all --dry-run          # Test run
  python -m scripts.delitzsch --explore-only           # Explore HTML structure only
  python -m scripts.delitzsch --force matthew          # Force re-download repo
  python -m scripts.delitzsch --all --download-direct  # Download files directly

Repository: https://github.com/hebrew-bible/hebrew-bible.github.io
Output: data/delitzsch/ (JSON files)

Note: If git cloning fails, try --download-direct for individual file downloads
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('books', nargs='*', help='Book names to process')
    parser.add_argument('--book', '-b', type=str, help='Single book name')
    parser.add_argument('--all', action='store_true', help='Process all books')
    parser.add_argument('--list', action='store_true', help='List available books')
    parser.add_argument('--dry-run', action='store_true', help='Process only first book/chapter for testing')
    parser.add_argument('--explore-only', action='store_true', help='Only explore HTML structure, do not parse')
    parser.add_argument('--repo-path', type=str, default=str(DEFAULT_REPO_DIR), help='Repository path')
    parser.add_argument('--output-dir', type=str, default=DEFAULT_OUTPUT_DIR, help='Output directory')
    parser.add_argument('--force', action='store_true', help='Force re-clone repository')
    parser.add_argument('--validate', action='store_true', help='Validate output JSON files after conversion')
    parser.add_argument('--download-direct', action='store_true', help='Download HTML files directly instead of cloning repository')
    parser.add_argument('--use-existing', action='store_true', help='Use existing HTML files without repository operations')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    return parser


def process_books(
    book_names: List[str],
    repo_path: str = str(DEFAULT_REPO_DIR),
    output_dir: str = DEFAULT_OUTPUT_DIR,
    force_clone: bool = False,
    dry_run: bool = False,
    explore_only: bool = False,
    validate_output: bool = False,
    download_direct: bool = False,
    use_existing: bool = False
) -> bool:
    """
    Main processing function.

    Args:
        book_names: List of book names to process
        repo_path: Path to the repository
        output_dir: Output directory for JSON files
        force_clone: Force re-clone repository
        dry_run: Dry run mode
        explore_only: Only explore HTML structure
        validate_output: Validate output after conversion

    Returns:
        True if processing successful, False otherwise
    """
    try:
        # For dry-run, skip actual repository and parsing operations
        if dry_run:
            logger.info("DRY RUN: Simulating processing without actual operations")
            logger.info(f"Would process books: {', '.join(book_names)}")
            logger.info("Would clone/update repository and parse HTML files")
            logger.info("Would convert to JSON format in data/delitzsch/")
            return True

        if use_existing:
            # Use existing HTML files in repo_path
            logger.info("Using existing HTML files...")
            import os
            if not os.path.exists(repo_path):
                logger.error(f"Repository path does not exist: {repo_path}")
                return False
            html_dir = os.path.join(repo_path, 'html')
            if not os.path.exists(html_dir):
                logger.error(f"HTML directory does not exist: {html_dir}")
                return False

            # Find existing HTML files
            from .downloader import locate_delitzsch_files
            from pathlib import Path
            html_files = locate_delitzsch_files(Path(repo_path), book_filter=book_names)
            if not html_files:
                logger.error("No HTML files found for requested books")
                return False
        elif download_direct:
            # Use direct download mode
            logger.info("Using direct download mode...")
            from .downloader import download_html_files_directly
            html_files = download_html_files_directly(
                output_dir=Path(repo_path),
                books=book_names
            )
            if not html_files:
                logger.error("Failed to download HTML files automatically")
                logger.info("You can manually download the HTML files from:")
                logger.info("https://github.com/hebrew-bible/hebrew-bible.github.io/tree/master/html")
                logger.info(f"And place them in: {repo_path}")
                return False
        else:
            # Use repository cloning mode
            logger.info("Ensuring repository is available...")
            repo_path_obj = ensure_repository(
                repo_path=Path(repo_path) if repo_path != str(DEFAULT_REPO_DIR) else None,
                force_clone=force_clone
            )

            if not repo_path_obj:
                logger.error("Failed to access repository")
                logger.info("Alternative: Try using --download-direct option")
                return False

            # Locate HTML files
            logger.info("Locating HTML files...")
            from .downloader import locate_delitzsch_files
            html_files = locate_delitzsch_files(repo_path_obj, book_filter=book_names)

            if not html_files:
                logger.error("No HTML files found in repository for requested books")
                return False

        # Parse HTML files
        logger.info(f"Parsing {len(html_files)} HTML files...")
        books_data = parse_html_files(html_files, explore_only=explore_only)

        if not books_data:
            logger.error("No book data extracted from HTML files")
            return False

        if explore_only:
            logger.info("Exploration mode - displaying results:")
            for book_name, data in books_data.items():
                if 'analysis' in data:
                    analysis = data['analysis']
                    print(f"\n=== {book_name} ===")
                    print(f"Title: {analysis.get('title', 'N/A')}")
                    print(f"Headings: {len(analysis.get('headings', []))}")
                    print(f"Divs: {analysis.get('div_count', 0)}")
                    print(f"Paragraphs: {analysis.get('p_count', 0)}")
                    print(f"Spans: {analysis.get('span_count', 0)}")
                    print(f"Text length: {analysis.get('text_length', 0)}")
                    print(f"Sample: {analysis.get('sample_text', '')[:200]}...")
            return True

        # Filter books if specific books requested
        if book_names and book_names != list(NEW_TESTAMENT_BOOKS.keys()):
            filtered_books = {}
            for book_name in book_names:
                if book_name in books_data:
                    filtered_books[book_name] = books_data[book_name]
                else:
                    logger.warning(f"Requested book '{book_name}' not found in parsed data")
            books_data = filtered_books

        if not books_data:
            logger.error("No matching books found to process")
            return False

        # Convert to JSON
        logger.info(f"Converting {len(books_data)} books to JSON...")
        conversion_results = convert_books_to_json(
            books_data=books_data,
            output_dir=output_dir,
            dry_run=dry_run
        )

        # Validate output if requested
        if validate_output and not dry_run:
            logger.info("Validating output JSON files...")
            validation_results = validate_all_converted_books(
                list(conversion_results.keys()),
                output_dir=output_dir
            )

            # Check if all validations passed
            if not all(validation_results.values()):
                failed_books = [book for book, success in validation_results.items() if not success]
                logger.error(f"Validation failed for books: {', '.join(failed_books)}")
                return False

        # Check conversion results
        successful_conversions = sum(conversion_results.values())
        total_conversions = len(conversion_results)

        if successful_conversions == total_conversions:
            logger.info("All books processed successfully!")
            return True
        else:
            failed_books = [book for book, success in conversion_results.items() if not success]
            logger.error(f"Failed to process books: {', '.join(failed_books)}")
            return False

    except Exception as e:
        logger.error(f"Error during processing: {e}")
        return False


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    setup_logging(args.verbose)

    if args.list:
        list_books()
        return

    # Check dependencies for processing operations
    if not args.explore_only and not args.dry_run:
        missing_deps = check_dependencies_optional()
        if missing_deps:
            logger.error(f"Missing dependencies required for processing: {', '.join(missing_deps)}")
            logger.info(f"Install with: pip install {' '.join(missing_deps)}")
            sys.exit(1)
    elif args.explore_only:
        # For exploration, check but don't fail
        missing_deps = check_dependencies_optional()
        if missing_deps:
            logger.warning(f"Missing dependencies (exploration may not work): {', '.join(missing_deps)}")
    elif args.dry_run:
        # For dry-run, warn about missing dependencies but continue
        missing_deps = check_dependencies_optional()
        if missing_deps:
            logger.warning(f"Missing dependencies (dry-run will show what would be processed): {', '.join(missing_deps)}")

    # Determine books to process
    if args.all:
        book_names = list(NEW_TESTAMENT_BOOKS.keys())
    elif args.book:
        book_names = validate_books([args.book])
    elif args.books:
        book_names = validate_books(args.books)
    else:
        if not args.explore_only:
            print("Error: No books specified. Use --list to see available books.")
            print("Example: python -m scripts.delitzsch --book matthew --dry-run")
            sys.exit(1)
        book_names = []  # For exploration mode

    # Validate paths
    repo_path = Path(args.repo_path)
    output_dir = Path(args.output_dir)

    # Process books
    success = process_books(
        book_names=book_names,
        repo_path=str(repo_path),
        output_dir=str(output_dir),
        force_clone=args.force,
        dry_run=args.dry_run,
        explore_only=args.explore_only,
        validate_output=args.validate,
        download_direct=args.download_direct,
        use_existing=args.use_existing
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()