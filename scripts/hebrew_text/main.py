#!/usr/bin/env python3
"""
Main CLI script for transcribing Hebrew Bible images using Google Gemini 1.5 Pro Vision API.

This script processes images, sends them to Gemini API for transcription,
validates responses, and consolidates verses into final JSON files.

Usage:
    python scripts/hebrew_text/main.py --list                    # List available books
    python scripts/hebrew_text/main.py --book matthew --dry-run  # Process 5 images (dry-run)
    python scripts/hebrew_text/main.py --book matthew            # Process one book
    python scripts/hebrew_text/main.py matthew mark luke          # Process multiple books
    python scripts/hebrew_text/main.py --all                      # Process all books
    python scripts/hebrew_text/main.py --book matthew --resume    # Resume from checkpoint
    python scripts/hebrew_text/main.py --book matthew --reprocess-failed  # Reprocess failed images
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from tqdm import tqdm
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    try:
        import yaml
    except ImportError:
        missing.append("PyYAML")

    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")

    try:
        import jsonschema
    except ImportError:
        missing.append("jsonschema")

    # Check for Gemini SDK (either new or old)
    gemini_found = False
    try:
        from google import genai
        gemini_found = True
    except ImportError:
        try:
            import google.generativeai
            gemini_found = True
        except ImportError:
            pass

    if not gemini_found:
        missing.append("google-genai (or google-generativeai)")

    if missing:
        logger.error("Missing required dependencies:")
        for lib in missing:
            logger.error(f"  - {lib}")
        logger.info("\nPlease install missing dependencies using:")
        logger.info(f"pip install {' '.join(missing) if 'google-genai (or google-generativeai)' not in missing else ' '.join([m for m in missing if 'google' not in m] + ['google-genai'])}")
        sys.exit(1)

# Run dependency check
check_dependencies()

# Load environment variables from .env file
load_dotenv()

# Handle both module and standalone execution
try:
    from .checkpoint import CheckpointManager
    from .prompt import load_yaml, build_prompt, get_yaml_version, calculate_yaml_hash
    from .client import GeminiClient
    from .validator import parse_json_response, validate_chapter_object, validate_verse_object
    from .consolidator import consolidate_book
except ImportError:
    # If running as standalone script, add project root to path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from scripts.hebrew_text.checkpoint import CheckpointManager
    from scripts.hebrew_text.prompt import load_yaml, build_prompt, get_yaml_version, calculate_yaml_hash
    from scripts.hebrew_text.client import GeminiClient
    from scripts.hebrew_text.validator import parse_json_response, validate_chapter_object, validate_verse_object
    from scripts.hebrew_text.consolidator import consolidate_book

# Available books (same as in hebrew_images/main.py)
AVAILABLE_BOOKS = [
    'matthew', 'mark', 'luke', 'john', 'acts', 'romans',
    'corinthians1', 'corinthians2', 'galatians', 'ephesians',
    'philippians', 'colossians', 'thessalonians1', 'thessalonians2',
    'timothy1', 'timothy2', 'titus', 'philemon', 'hebrews',
    'james', 'peter1', 'peter2', 'john1', 'john2', 'john3',
    'jude', 'revelation'
]


def list_books():
    """List all available books."""
    print("Available books:")
    print("=" * 50)
    for i, book in enumerate(AVAILABLE_BOOKS, 1):
        print(f"{i:2d}. {book}")
    print("\nUsage examples:")
    print("  python scripts/hebrew_text/main.py --book matthew --dry-run")
    print("  python scripts/hebrew_text/main.py --book matthew")
    print("  python scripts/hebrew_text/main.py matthew mark luke")
    print("  python scripts/hebrew_text/main.py --all")


def validate_books(book_names: List[str]) -> List[str]:
    """
    Validate that requested books exist.

    Args:
        book_names: List of book names to validate

    Returns:
        List of valid book names
    """
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


def get_image_list(book_name: str, images_dir: Path) -> List[Path]:
    """
    Get list of images to process for a book.

    Args:
        book_name: Name of the book
        images_dir: Base directory containing images

    Returns:
        List of image paths
    """
    book_dir = images_dir / book_name

    if not book_dir.exists():
        logger.warning(f"Image directory not found: {book_dir}")
        return []

    # Special case: colossians - exclude pages 000026, 000028, 000030
    laodikim_pages = ['000026.png', '000028.png', '000030.png']

    image_files = []
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        image_files.extend(book_dir.glob(ext))

    image_files = sorted(list(set(image_files)))

    if book_name.lower() == 'colossians':
        image_files = [img for img in image_files if img.name not in laodikim_pages]

    # Special case: john1 - apply filtering logic
    if book_name.lower() == 'john1':
        filtered = []
        for img_path in image_files:
            try:
                img_num = int(img_path.stem)
                # Skip 000006.png and 000008.png
                if img_num in [6, 8]:
                    continue
                # From 000009.png onwards, process only odd-numbered images
                if img_num >= 9:
                    if img_num % 2 == 0:
                        continue
                # Before 000009, process only even-numbered
                elif img_num % 2 == 1:
                    continue
                filtered.append(img_path)
            except ValueError:
                continue
        image_files = filtered
    else:
        # Normal behavior: skip odd-numbered images
        filtered = []
        for img_path in image_files:
            try:
                img_num = int(img_path.stem)
                if img_num % 2 == 1:
                    continue
                filtered.append(img_path)
            except ValueError:
                continue
        image_files = filtered

    return image_files


def calculate_cost(usage: dict) -> float:
    """
    Calculate actual cost based on token usage.

    Prices (Gemini 1.5 Pro):
    Input: $1.25 / 1M tokens
    Output: $5.00 / 1M tokens
    """
    if not usage:
        return 0.00125  # Fallback estimate

    input_tokens = usage.get('prompt_tokens', 0)
    output_tokens = usage.get('completion_tokens', 0)

    cost = (input_tokens / 1_000_000 * 1.25) + (output_tokens / 1_000_000 * 5.00)
    return max(cost, 0.00001)


def process_image(
    image_path: Path,
    client: GeminiClient,
    prompt_template: str,
    checkpoint: CheckpointManager,
    dry_run: bool = False
) -> bool:
    """
    Process a single image.

    Args:
        image_path: Path to image file
        client: Gemini client instance
        prompt_template: Prompt template string
        checkpoint: Checkpoint manager instance
        dry_run: If True, skip API call

    Returns:
        True if successful, False otherwise
    """
    image_name = image_path.name

    # Check if already processed
    if checkpoint.is_image_processed(image_name):
        logger.debug(f"Skipping {image_name} (already processed)")
        return True

    if dry_run:
        logger.info(f"[DRY RUN] Would process {image_name}")
        return True

    try:
        # Update status to processing
        checkpoint.update_image_status(image_name, 'processing')

        # Call API
        logger.info(f"Processing {image_name}...")
        response = client.transcribe_image(image_path, prompt_template)

        # Calculate cost
        cost = calculate_cost(response.get('usage', {}))

        # Parse JSON response
        parsed_json, error = parse_json_response(response['text'])
        if error:
            logger.error(f"Failed to parse JSON for {image_name}: {error}")
            checkpoint.update_image_status(
                image_name,
                'failed',
                cost_usd=cost,
                error=f"JSON parse error: {error}"
            )
            checkpoint.save()
            return False

        # Validate response structure
        if 'chapters' not in parsed_json:
            logger.error(f"Invalid response structure for {image_name}: missing 'chapters'")
            checkpoint.update_image_status(
                image_name,
                'failed',
                cost_usd=cost,
                error="Invalid response structure: missing 'chapters'"
            )
            checkpoint.save()
            return False

        # Extract and validate verses
        verses_dict = {}
        for chapter_data in parsed_json['chapters']:
            # Validate chapter
            is_valid, error = validate_chapter_object(chapter_data)
            if not is_valid:
                logger.error(f"Invalid chapter in {image_name}: {error}")
                continue

            chapter_num = chapter_data['number']

            for verse_data in chapter_data['verses']:
                # Validate verse
                is_valid, error = validate_verse_object(verse_data)
                if not is_valid:
                    logger.warning(f"Invalid verse in {image_name}: {error}")
                    continue

                verse_num = verse_data['number']
                verse_key = f"{chapter_num}_{verse_num}"

                # Each verse should only reference its source image
                # Ignore any source_files returned by Gemini as they may contain previous images
                source_files = [image_name]

                verses_dict[verse_key] = {
                    'status': 'completed',
                    'chapter': chapter_num,
                    'verse': verse_num,
                    'text_nikud': verse_data['text_nikud'],
                    'source_files': source_files,
                    'visual_uncertainty': verse_data.get('visual_uncertainty', [])
                }

        if not verses_dict:
            logger.warning(f"No valid verses extracted from {image_name}")
            checkpoint.update_image_status(
                image_name,
                'failed',
                cost_usd=cost,
                error="No valid verses extracted"
            )
            checkpoint.save()
            return False

        # Update checkpoint with completed verses
        checkpoint.update_image_status(
            image_name,
            'completed',
            cost_usd=cost,
            verses=verses_dict
        )
        checkpoint.save()

        logger.info(f"✓ Completed {image_name}: {len(verses_dict)} verses, ${cost:.5f}")
        return True

    except Exception as e:
        logger.error(f"Error processing {image_name}: {e}")
        checkpoint.update_image_status(
            image_name,
            'failed',
            cost_usd=0.0,
            error=str(e)
        )
        checkpoint.save()
        return False


def process_book(
    book_name: str,
    images_dir: Path,
    output_dir: Path,
    yaml_path: Path,
    checkpoint_dir: Path,
    client: GeminiClient,
    prompt_template: str,
    yaml_version: str,
    yaml_hash: str,
    dry_run: bool = False,
    resume: bool = False,
    reprocess_failed: bool = False,
    parallel: int = 1
) -> bool:
    """
    Process a single book.

    Args:
        book_name: Name of the book
        images_dir: Directory containing images
        output_dir: Output directory for JSON files
        yaml_path: Path to YAML configuration file
        checkpoint_dir: Directory for checkpoint files
        client: Gemini client instance
        prompt_template: Prompt template string
        yaml_version: YAML version string
        yaml_hash: YAML hash string
        dry_run: If True, process only 5 images
        resume: If True, resume from checkpoint
        reprocess_failed: If True, reprocess failed images
        parallel: Number of parallel requests

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing book: {book_name}")
    logger.info(f"{'='*60}")

    # Initialize checkpoint
    checkpoint_path = checkpoint_dir / f"{book_name}_state.json"
    checkpoint = CheckpointManager(checkpoint_path)

    if resume or reprocess_failed:
        checkpoint.load()
        # Check if YAML version/hash changed
        if checkpoint.state.get('yaml_hash') != yaml_hash:
            logger.warning(f"YAML configuration has changed since last run for {book_name}")
            logger.warning(f"  Old hash: {checkpoint.state.get('yaml_hash', 'unknown')[:16]}...")
            logger.warning(f"  New hash: {yaml_hash[:16]}...")
            # If resume is not explicitly requested, we might want to warn or reprocess
            # For now, we just update the hash and continue
            checkpoint.state['yaml_hash'] = yaml_hash
            checkpoint.state['yaml_version'] = yaml_version
    else:
        # Initialize new checkpoint
        image_list = get_image_list(book_name, images_dir)
        checkpoint.initialize(book_name, len(image_list), yaml_version, yaml_hash)
        checkpoint.save()

    # Get image list
    image_list = get_image_list(book_name, images_dir)

    if not image_list:
        logger.warning(f"No images found for {book_name}")
        return False

    # Filter images based on flags
    if reprocess_failed:
        failed_images = checkpoint.get_failed_images()
        image_list = [img for img in image_list if img.name in failed_images]
        logger.info(f"Reprocessing {len(image_list)} failed images")
    elif dry_run:
        # For dry run, we only take the first 5 UNPROCESSED images
        unprocessed = [img for img in image_list if not checkpoint.is_image_processed(img.name)]
        image_list = unprocessed[:5]
        logger.info(f"DRY RUN: Processing first {len(image_list)} images")
    else:
        # Filter out already processed images
        image_list = [img for img in image_list if not checkpoint.is_image_processed(img.name)]

    if not image_list:
        logger.info(f"No images to process for {book_name}")
        # Still consolidate if some images were already processed
        if checkpoint.state.get('processed_images', 0) > 0:
            logger.info(f"Consolidating existing results for {book_name}...")
            consolidate_book(checkpoint.state, book_name, output_dir)
        return True

    # Process images
    successful = 0
    failed = 0

    if parallel > 1 and not dry_run:
        logger.info(f"Processing with {parallel} threads...")
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            future_to_img = {
                executor.submit(process_image, img_path, client, prompt_template, checkpoint, False): img_path
                for img_path in image_list
            }

            with tqdm(total=len(image_list), desc=f"Processing {book_name}", ncols=80) as pbar:
                for future in as_completed(future_to_img):
                    try:
                        if future.result():
                            successful += 1
                        else:
                            failed += 1
                    except Exception as e:
                        logger.error(f"Thread failed: {e}")
                        failed += 1
                    pbar.update(1)
                    # Small delay to avoid aggressive rate limiting
                    time.sleep(0.5)
    else:
        with tqdm(total=len(image_list), desc=f"Processing {book_name}", ncols=80) as pbar:
            for image_path in image_list:
                if process_image(image_path, client, prompt_template, checkpoint, dry_run):
                    successful += 1
                else:
                    failed += 1
                pbar.update(1)

    logger.info(f"\nCompleted {book_name}: {successful} successful, {failed} failed")

    # Consolidate verses if not dry run
    if not dry_run and (successful > 0 or checkpoint.state.get('processed_images', 0) > 0):
        checkpoint.load()  # Reload to get latest state
        logger.info(f"Consolidating verses for {book_name}...")
        consolidate_book(checkpoint.state, book_name, output_dir)

    return failed == 0


def process_books(
    book_names: List[str],
    images_dir: Path,
    output_dir: Path,
    yaml_path: Path,
    checkpoint_dir: Path,
    dry_run: bool = False,
    resume: bool = False,
    reprocess_failed: bool = False,
    parallel: int = 1,
    model_name: Optional[str] = None
) -> bool:
    """
    Process multiple books.

    Args:
        book_names: List of book names to process
        images_dir: Directory containing images
        output_dir: Output directory for JSON files
        yaml_path: Path to YAML configuration file
        checkpoint_dir: Directory for checkpoint files
        dry_run: If True, process only 5 images per book
        resume: If True, resume from checkpoint
        reprocess_failed: If True, reprocess failed images
        parallel: Number of parallel requests
        model_name: Name of the Gemini model to use

    Returns:
        True if all books were processed successfully, False otherwise
    """
    # Load YAML and build prompt
    logger.info("Loading YAML configuration...")
    yaml_data = load_yaml(yaml_path)

    # Read YAML content for hash calculation
    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_content = f.read()

    yaml_version = get_yaml_version(yaml_data)
    yaml_hash = calculate_yaml_hash(yaml_content)

    logger.info(f"YAML version: {yaml_version}")
    logger.info(f"YAML hash: {yaml_hash[:16]}...")

    # Build prompt template
    prompt_template = build_prompt(yaml_data)
    logger.info("Prompt template built")

    # Initialize Gemini client
    try:
        client = GeminiClient(model_name=model_name)
        logger.info(f"Gemini client initialized with model: {client.model_name}")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        return False

    # Process each book
    success_count = 0
    total_books = len(book_names)

    for book_name in book_names:
        if process_book(
            book_name,
            images_dir,
            output_dir,
            yaml_path,
            checkpoint_dir,
            client,
            prompt_template,
            yaml_version,
            yaml_hash,
            dry_run,
            resume,
            reprocess_failed,
            parallel
        ):
            success_count += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"Completed: {success_count}/{total_books} books processed successfully")
    logger.info(f"{'='*60}")

    return success_count == total_books


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Transcribe Hebrew Bible images using Google Gemini 1.5 Pro Vision API.",
        epilog="""
Examples:
  python scripts/hebrew_text/main.py --list                    # List all books
  python scripts/hebrew_text/main.py --book matthew --dry-run  # Process 5 images (dry-run)
  python scripts/hebrew_text/main.py --book matthew            # Process one book
  python scripts/hebrew_text/main.py matthew mark luke        # Process multiple books
  python scripts/hebrew_text/main.py --all                      # Process all books
  python scripts/hebrew_text/main.py --book matthew --resume    # Resume from checkpoint
  python scripts/hebrew_text/main.py --book matthew --reprocess-failed  # Reprocess failed images
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'books',
        nargs='*',
        help='Book names to process (or use --all for all books, or --book for single book)'
    )

    parser.add_argument(
        '--book', '-b',
        type=str,
        help='Single book name to process'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all books'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available books'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Process only 5 images per book (for testing)'
    )

    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from checkpoint'
    )

    parser.add_argument(
        '--reprocess-failed',
        action='store_true',
        help='Reprocess failed images'
    )

    parser.add_argument(
        '--images-dir',
        type=str,
        default='data/images/hebrew_images',
        help='Directory containing images (default: data/images/hebrew_images)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory for JSON files (default: output)'
    )

    parser.add_argument(
        '--yaml-path',
        type=str,
        default='docs/hebrew_vision_context.yaml',
        help='Path to YAML configuration file (default: docs/hebrew_vision_context.yaml)'
    )

    parser.add_argument(
        '--checkpoint-dir',
        type=str,
        default='output/.checkpoints',
        help='Directory for checkpoint files (default: output/.checkpoints)'
    )

    parser.add_argument(
        '--parallel',
        type=int,
        default=1,
        help='Number of parallel requests to Gemini API (default: 1)'
    )

    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Specific Gemini model to use (e.g., gemini-2.0-flash-exp, gemini-1.5-flash)'
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

    # Determine books to process
    if args.all:
        book_names = AVAILABLE_BOOKS
    elif args.book:
        book_names = validate_books([args.book])
    elif args.books:
        book_names = validate_books(args.books)
    else:
        print("Error: No books specified. Use --list to see available books.")
        print("Example: python scripts/hebrew_text/main.py --book matthew --dry-run")
        sys.exit(1)

    # Convert paths
    images_dir = Path(args.images_dir)
    output_dir = Path(args.output_dir)
    yaml_path = Path(args.yaml_path)
    checkpoint_dir = Path(args.checkpoint_dir)

    # Validate paths
    if not images_dir.exists():
        logger.error(f"Images directory not found: {images_dir}")
        sys.exit(1)

    if not yaml_path.exists():
        logger.error(f"YAML file not found: {yaml_path}")
        sys.exit(1)

    # Process books
    success = process_books(
        book_names=book_names,
        images_dir=images_dir,
        output_dir=output_dir,
        yaml_path=yaml_path,
        checkpoint_dir=checkpoint_dir,
        dry_run=args.dry_run,
        resume=args.resume,
        reprocess_failed=args.reprocess_failed,
        parallel=args.parallel,
        model_name=args.model
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
