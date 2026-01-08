"""
Conversion logic for transforming parsed Delitzsch data to Shafan JSON format.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from .constants import AUTHOR_NAME, PUBLICATION_YEAR
from .parser import DelitzschParser

logger = logging.getLogger(__name__)


def convert_book_to_json(book_data: Dict[str, Any], output_dir: Path) -> bool:
    """
    Convert parsed book data to JSON format and save to file.

    Args:
        book_data: Parsed book data from the parser
        output_dir: Directory to save the JSON file

    Returns:
        True if conversion successful, False otherwise
    """
    try:
        book_name = book_data.get('book_name')
        if not book_name:
            logger.error("Book data missing book_name")
            return False

        # Build the output data structure
        output_data = {
            "book_name": book_name,
            "author": AUTHOR_NAME,
            "publication_year": PUBLICATION_YEAR,
            "chapters": []
        }

        chapters = book_data.get('chapters', [])
        if not chapters:
            logger.warning(f"No chapters found for book {book_name}")
            return False

        # Convert chapters
        converted_chapters = []
        for chapter in chapters:
            converted_chapter = {
                "hebrew_letter": chapter.get('hebrew_letter', ''),
                "number": chapter.get('number', 0),
                "verses": []
            }

            verses = chapter.get('verses', [])
            for verse in verses:
                # Adapt verse format to match existing JSON structure
                # Remove source_files and visual_uncertainty since we don't have images
                converted_verse = {
                    "number": verse.get('number', 0),
                    "text_nikud": verse.get('text_nikud', '').strip()
                }
                converted_chapter["verses"].append(converted_verse)

            converted_chapters.append(converted_chapter)

        output_data["chapters"] = converted_chapters

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save to JSON file
        output_file = output_dir / f"{book_name}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        # Log statistics
        total_verses = sum(len(ch.get('verses', [])) for ch in converted_chapters)
        logger.info(f"Converted {book_name}: {len(converted_chapters)} chapters, {total_verses} verses")

        return True

    except Exception as e:
        logger.error(f"Error converting book {book_data.get('book_name', 'unknown')}: {e}")
        return False


def convert_books_to_json(
    books_data: Dict[str, Dict[str, Any]],
    output_dir: str = "data/delitzsch",
    dry_run: bool = False
) -> Dict[str, bool]:
    """
    Convert multiple books to JSON format.

    Args:
        books_data: Dictionary mapping book names to parsed book data
        output_dir: Directory to save JSON files
        dry_run: If True, don't actually write files

    Returns:
        Dictionary mapping book names to conversion success status
    """
    output_path = Path(output_dir)
    results = {}

    if dry_run:
        logger.info("DRY RUN: Would process the following books:")
        for book_name in books_data.keys():
            logger.info(f"  - {book_name}")
        return {book_name: True for book_name in books_data.keys()}

    for book_name, book_data in books_data.items():
        logger.info(f"Converting book: {book_name}")
        success = convert_book_to_json(book_data, output_path)
        results[book_name] = success

        if not success:
            logger.error(f"Failed to convert book: {book_name}")

    # Summary
    successful = sum(results.values())
    total = len(results)
    logger.info(f"Conversion complete: {successful}/{total} books successful")

    return results


def validate_converted_book(book_name: str, output_dir: str = "data/delitzsch") -> bool:
    """
    Validate a converted JSON file.

    Args:
        book_name: Name of the book to validate
        output_dir: Directory containing the JSON files

    Returns:
        True if validation passes, False otherwise
    """
    try:
        json_file = Path(output_dir) / f"{book_name}.json"

        if not json_file.exists():
            logger.error(f"JSON file not found: {json_file}")
            return False

        # Load and validate JSON structure
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check required fields
        required_fields = ['book_name', 'author', 'publication_year', 'chapters']
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field '{field}' in {book_name}.json")
                return False

        # Validate chapters structure
        chapters = data.get('chapters', [])
        if not chapters:
            logger.error(f"No chapters found in {book_name}.json")
            return False

        for i, chapter in enumerate(chapters):
            if 'number' not in chapter or 'verses' not in chapter:
                logger.error(f"Invalid chapter structure at index {i} in {book_name}.json")
                return False

            verses = chapter.get('verses', [])
            for j, verse in enumerate(verses):
                if 'number' not in verse or 'text_nikud' not in verse:
                    logger.error(f"Invalid verse structure at chapter {i+1}, verse {j} in {book_name}.json")
                    return False

        logger.info(f"Validation passed for {book_name}.json")
        return True

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {book_name}.json: {e}")
        return False
    except Exception as e:
        logger.error(f"Error validating {book_name}.json: {e}")
        return False


def validate_all_converted_books(
    book_names: List[str],
    output_dir: str = "data/delitzsch"
) -> Dict[str, bool]:
    """
    Validate multiple converted JSON files.

    Args:
        book_names: List of book names to validate
        output_dir: Directory containing the JSON files

    Returns:
        Dictionary mapping book names to validation results
    """
    results = {}

    for book_name in book_names:
        results[book_name] = validate_converted_book(book_name, output_dir)

    # Summary
    successful = sum(results.values())
    total = len(results)
    logger.info(f"Validation complete: {successful}/{total} books passed validation")

    return results