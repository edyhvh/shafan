"""
Core conversion logic for Tanaj text extraction.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .hebrew_utils import number_to_hebrew_numeral

logger = logging.getLogger(__name__)


def validate_source_dir(source_dir: str) -> str:
    """
    Validate and sanitize source directory path.

    Args:
        source_dir: The source directory path to validate

    Returns:
        The validated source directory path

    Raises:
        ValueError: If the path is invalid or potentially dangerous
    """
    import re

    # Check for dangerous path patterns
    dangerous_patterns = [
        r'\.\.',  # Parent directory traversal
        r'^/',    # Absolute paths starting with /
        r'^\\',   # Windows absolute paths
        r'^[a-zA-Z]:',  # Windows drive letters
        r'[<>|]',  # Shell redirection characters
        r'[;&]',   # Command separators
        r'[$`]',   # Shell variable expansion
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, source_dir):
            raise ValueError(f"Invalid source directory path: contains dangerous characters")

    # Check path length
    if len(source_dir) > 260:  # Reasonable path length limit
        raise ValueError(f"Source directory path too long: {len(source_dir)} characters")

    return source_dir


def get_available_books(source_dir: str = "~/tanaj_source") -> List[str]:
    """Get list of available books from source directory."""
    # Validate source directory path
    try:
        validated_source_dir = validate_source_dir(source_dir)
    except ValueError as e:
        logger.error(f"Invalid source directory: {e}")
        return []

    source_path = Path(validated_source_dir).expanduser()
    if not source_path.exists():
        logger.error(f"Source directory not found: {source_dir}")
        return []

    books = []
    for item in source_path.iterdir():
        if item.is_dir() and item.name != 'raw':  # Exclude raw directory
            books.append(item.name)
    return sorted(books)


def load_chapter_data(book_path: Path, chapter_num: int) -> Optional[List[Dict[str, Any]]]:
    """Load chapter data from JSON file."""
    chapter_file = book_path / f"{chapter_num}.json"
    if not chapter_file.exists():
        logger.warning(f"Chapter file not found: {chapter_file}")
        return None

    try:
        with open(chapter_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading chapter {chapter_num} from {chapter_file}: {e}")
        return None


def convert_book(book_name: str, source_dir: str = "~/tanaj_source", output_dir: str = "output", dry_run: bool = False) -> bool:
    """
    Convert a Tanaj book from source format to Shafan JSON format.

    Args:
        book_name: Name of the book to convert
        source_dir: Source directory containing book data
        output_dir: Output directory for JSON files
        dry_run: If True, only process first 5 chapters

    Returns:
        True if conversion successful, False otherwise
    """
    # Validate source directory path
    try:
        validated_source_dir = validate_source_dir(source_dir)
    except ValueError as e:
        logger.error(f"Invalid source directory: {e}")
        return False

    source_path = Path(validated_source_dir).expanduser()
    book_path = source_path / book_name

    if not book_path.exists():
        logger.error(f"Book directory not found: {book_name} in {source_dir}")
        return False

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    output_file = output_path / f"{book_name}.json"

    logger.info(f"Converting book: {book_name}")

    # Find all chapter files
    chapter_files = []
    for i in range(1, 200):  # Reasonable upper limit
        chapter_file = book_path / f"{i}.json"
        if chapter_file.exists():
            chapter_files.append(i)
        else:
            break

    if not chapter_files:
        logger.error(f"No chapter files found for book: {book_name}")
        return False

    if dry_run:
        chapter_files = chapter_files[:5]
        logger.info(f"Dry run: processing first {len(chapter_files)} chapters")

    # Group verses by chapter
    chapter_verses = {}

    for chapter_num in chapter_files:
        logger.info(f"Processing chapter {chapter_num}")

        chapter_data = load_chapter_data(book_path, chapter_num)
        if not chapter_data:
            continue

        verses = []
        for verse_data in chapter_data:
            verse_num = verse_data.get('verse', 0)
            hebrew_text = verse_data.get('hebrew', '')

            if verse_num > 0 and hebrew_text:
                verses.append({
                    "number": verse_num,
                    "text_nikud": hebrew_text  # Keep / separators in stored data
                })

        if verses:
            chapter_verses[chapter_num] = verses

    # Convert to output format
    chapters = []
    for chapter_num in sorted(chapter_verses.keys()):
        verses = chapter_verses[chapter_num]
        # Convert chapter number to Hebrew numeral
        hebrew_letter = number_to_hebrew_numeral(chapter_num)

        chapters.append({
            "hebrew_letter": hebrew_letter,
            "number": chapter_num,
            "verses": verses
        })

    if not chapters:
        logger.error(f"No chapters processed for book: {book_name}")
        return False

    # Create output JSON
    output_data = {
        "book_name": book_name,
        "author": "",
        "publication_year": "",
        "chapters": chapters
    }

    # Debug: check chapters structure
    logger.debug(f"Chapters structure: {type(chapters)}, length: {len(chapters)}")
    if chapters:
        logger.debug(f"First chapter: {chapters[0]}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        total_verses = sum(len(ch.get('verses', [])) for ch in chapters)
        logger.info(f"Successfully converted {book_name} ({len(chapters)} chapters, {total_verses} verses)")
        return True
    except Exception as e:
        logger.error(f"Error writing output file {output_file}: {e}")
        logger.error(f"Chapters data: {chapters}")
        return False