"""Consolidate verses into final JSON per book."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict

from .validator import validate_chapter_sequence, validate_verse_sequence

logger = logging.getLogger(__name__)


def load_verses_from_checkpoint(checkpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Load all processed verses from checkpoint.

    Args:
        checkpoint: Checkpoint state dictionary

    Returns:
        List of verse dictionaries
    """
    verses = []
    if 'images' not in checkpoint:
        return verses

    for image_name, image_data in checkpoint['images'].items():
        if image_data.get('status') == 'completed' and 'verses' in image_data:
            for verse_key, verse_data in image_data['verses'].items():
                if verse_data.get('status') == 'completed':
                    verses.append({
                        'chapter': verse_data.get('chapter'),
                        'verse': verse_data.get('verse'),
                        'text_nikud': verse_data.get('text_nikud'),
                        'source_files': verse_data.get('source_files', [image_name]),
                        'visual_uncertainty': verse_data.get('visual_uncertainty', [])
                    })

    return verses


def merge_duplicate_verses(verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge verses that appear in multiple images (same chapter and verse number).

    When a verse spans multiple images, the text from each image is concatenated
    in the order of the source files (sorted by image number).

    Args:
        verses: List of verse dictionaries (may contain duplicates)

    Returns:
        List of merged verse dictionaries (no duplicates)
    """
    # Dictionary to store merged verses: key = (chapter, verse)
    # Value is a list of verse parts to merge (ordered by source file)
    verse_parts: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}

    for verse in verses:
        chapter = verse.get('chapter')
        verse_num = verse.get('verse')

        if chapter is None or verse_num is None:
            logger.warning(f"Skipping verse with missing chapter or verse number: {verse}")
            continue

        key = (chapter, verse_num)

        if key not in verse_parts:
            verse_parts[key] = []

        verse_parts[key].append(verse)

    # Merge each verse's parts
    merged_verses = []
    for key, parts in verse_parts.items():
        chapter, verse_num = key

        # Sort parts by source file name (to maintain order across images)
        def get_first_source_file(verse_part: Dict[str, Any]) -> str:
            source_files = verse_part.get('source_files', [])
            if source_files:
                return source_files[0]
            return ''

        parts.sort(key=get_first_source_file)

        # Merge text_nikud: concatenate all parts with space
        text_parts = []
        all_source_files = set()
        all_uncertainty = []

        for part in parts:
            text = part.get('text_nikud', '').strip()
            if text:
                text_parts.append(text)

            # Collect source files
            source_files = part.get('source_files', [])
            if isinstance(source_files, list):
                all_source_files.update(source_files)

            # Collect visual uncertainty
            uncertainty = part.get('visual_uncertainty', [])
            if isinstance(uncertainty, list):
                all_uncertainty.extend(uncertainty)

        # Join text parts with space
        merged_text = ' '.join(text_parts).strip()

        # Remove duplicate uncertainty entries
        if all_uncertainty and all(isinstance(x, str) for x in all_uncertainty):
            all_uncertainty = sorted(list(set(all_uncertainty)))

        merged_verses.append({
            'chapter': chapter,
            'verse': verse_num,
            'text_nikud': merged_text,
            'source_files': sorted(list(all_source_files)),
            'visual_uncertainty': all_uncertainty
        })

    # Log if any verses were merged
    if len(merged_verses) < len(verses):
        logger.info(f"Merged {len(verses) - len(merged_verses)} duplicate verse entries")

    return merged_verses


def group_by_chapter(verses: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    """
    Group verses by chapter number.

    Args:
        verses: List of verse dictionaries

    Returns:
        Dictionary mapping chapter number to list of verses
    """
    chapters = defaultdict(list)

    for verse in verses:
        chapter_num = verse.get('chapter')
        if chapter_num is not None:
            chapters[chapter_num].append(verse)

    # Sort verses within each chapter
    for chapter_num in chapters:
        chapters[chapter_num].sort(key=lambda v: v.get('verse', 0))

    return dict(chapters)


def build_book_json(book_name: str, chapters: Dict[int, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Build final JSON following YAML schema.

    Args:
        book_name: Name of the book
        chapters: Dictionary mapping chapter number to list of verses

    Returns:
        Book JSON dictionary
    """
    # Hebrew letters for chapters (א, ב, ג, ד, etc.)
    hebrew_letters = [
        'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י',
        'יא', 'יב', 'יג', 'יד', 'טו', 'טז', 'יז', 'יח', 'יט', 'כ',
        'כא', 'כב', 'כג', 'כד', 'כה', 'כו', 'כז', 'כח', 'כט', 'ל',
        'לא', 'לב', 'לג', 'לד', 'לה', 'לו', 'לז', 'לח', 'לט', 'מ',
        'מא', 'מב', 'מג', 'מד', 'מה', 'מו', 'מז', 'מח', 'מט', 'נ'
    ]

    # Build chapters list
    chapters_list = []
    for chapter_num in sorted(chapters.keys()):
        chapter_verses = chapters[chapter_num]

        # Get Hebrew letter (use modulo to handle books with many chapters)
        hebrew_letter_idx = (chapter_num - 1) % len(hebrew_letters)
        hebrew_letter = hebrew_letters[hebrew_letter_idx]

        # Prepare verses (ensure they have all required fields)
        verses_list = []
        for verse in chapter_verses:
            verse_obj = {
                'number': verse.get('verse'),
                'text_nikud': verse.get('text_nikud', ''),
                'source_files': verse.get('source_files', []),
                'visual_uncertainty': verse.get('visual_uncertainty', [])
            }
            verses_list.append(verse_obj)

        chapter_obj = {
            'hebrew_letter': hebrew_letter,
            'number': chapter_num,
            'verses': verses_list
        }
        chapters_list.append(chapter_obj)

    book_json = {
        'book_name': book_name,
        'author': 'Elias Hutter',
        'publication_year': '1599–1602',
        'chapters': chapters_list
    }

    return book_json


def validate_complete_sequence(chapters: Dict[int, List[Dict[str, Any]]]) -> Tuple[bool, Optional[str]]:
    """
    Verify no gaps before finalizing.

    Args:
        chapters: Dictionary mapping chapter number to list of verses

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not chapters:
        return False, "No chapters found"

    # Validate chapter sequence
    chapter_list = [{'number': num} for num in chapters.keys()]
    is_valid, error, missing = validate_chapter_sequence(chapter_list)
    if not is_valid:
        return False, error

    # Validate verse sequences within each chapter
    # Convert verses to format expected by validator (with 'number' field)
    for chapter_num, verses in chapters.items():
        verses_for_validation = [{'number': v.get('verse')} for v in verses]
        is_valid, error, missing = validate_verse_sequence(verses_for_validation)
        if not is_valid:
            return False, f"Chapter {chapter_num}: {error}"

    return True, None


def save_book_json(book_json: Dict[str, Any], output_path: Path) -> bool:
    """
    Save final JSON to output directory.

    Args:
        book_json: Book JSON dictionary
        output_path: Path to output JSON file

    Returns:
        True if successful, False otherwise
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(book_json, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved book JSON to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save book JSON: {e}")
        return False


def consolidate_book(checkpoint: Dict[str, Any], book_name: str, output_dir: Path) -> bool:
    """
    Consolidate verses from checkpoint into final book JSON.

    Args:
        checkpoint: Checkpoint state dictionary
        book_name: Name of the book
        output_dir: Output directory for JSON file

    Returns:
        True if successful, False otherwise
    """
    # Load verses from checkpoint
    verses = load_verses_from_checkpoint(checkpoint)

    if not verses:
        logger.warning(f"No verses found in checkpoint for {book_name}")
        return False

    logger.info(f"Consolidating {len(verses)} verses for {book_name}")

    # Merge duplicate verses (same chapter/verse from different images)
    verses = merge_duplicate_verses(verses)
    logger.info(f"After merging duplicates: {len(verses)} unique verses")

    # Group by chapter
    chapters = group_by_chapter(verses)
    logger.info(f"Found {len(chapters)} chapters")

    # Validate sequence
    is_valid, error = validate_complete_sequence(chapters)
    if not is_valid:
        logger.warning(f"Sequence validation failed: {error}")
        logger.warning("Proceeding anyway, but review recommended")

    # Build book JSON
    book_json = build_book_json(book_name, chapters)

    # Save to output directory
    output_path = output_dir / f"{book_name}.json"
    success = save_book_json(book_json, output_path)

    return success

