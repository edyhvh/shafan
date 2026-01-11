#!/usr/bin/env python3
"""
Versification Mapping Script for Shafan

Downloads and processes versification mapping data from Copenhagen Alliance
to create simplified mappings for Tanakh books with verse/chapter shifts.

This script focuses only on Hebrew Bible (Tanakh) books that have differences
between Masoretic (Hebrew) and KJV-style (English) versification.

Output: A minimal JSON file with mappings for frontend use.
"""

import json
import os
import pathlib
import requests
import sys


# Configuration
VERSIFICATION_URL = "https://raw.githubusercontent.com/Copenhagen-Alliance/copenhagen-alliance.github.io/master/specifications/versification/versification-mappings/standard-mappings/eng.json"
OUTPUT_PATH = pathlib.Path.home() / "shafan" / "frontend" / "public" / "data" / "versification" / "versification.json"

# Tanakh books with versification differences between Hebrew (Masoretic) and English (KJV) traditions
# The Copenhagen Alliance data shows equivalences, not errors - these are legitimate differences
TANAKH_BOOKS_WITH_DIFFERENCES = {
    "GEN": "genesis",     # Genesis - various verse renumberings
    "EXO": "exodus",      # Exodus - chapter/verse shifts
    "LEV": "leviticus",   # Leviticus - verse renumberings
    "NUM": "numbers",     # Numbers - verse renumberings
    "DEU": "deuteronomy", # Deuteronomy - verse renumberings
    "JOS": "joshua",      # Joshua - verse differences
    "JDG": "judges",      # Judges - verse differences
    "RUT": "ruth",        # Ruth - verse differences
    "1SA": "isamuel",     # 1 Samuel - verse renumberings
    "2SA": "iisamuel",    # 2 Samuel - verse renumberings
    "1KI": "ikings",      # 1 Kings - verse renumberings
    "2KI": "iikings",     # 2 Kings - verse renumberings
    "1CH": "ichronicles", # 1 Chronicles - verse renumberings
    "2CH": "iichronicles", # 2 Chronicles - verse renumberings
    "EZR": "ezra",        # Ezra - verse differences
    "NEH": "nehemiah",    # Nehemiah - verse renumberings
    "EST": "esther",      # Esther - verse differences
    "JOB": "job",         # Job - verse renumberings
    "PSA": "psalms",      # Psalms - superscription shifts
    "PRO": "proverbs",    # Proverbs - verse differences
    "ECC": "ecclesiastes", # Ecclesiastes - verse renumberings
    "SNG": "songofsolomon", # Song of Solomon - verse differences
    "ISA": "isaiah",      # Isaiah - verse differences
    "JER": "jeremiah",    # Jeremiah - verse renumberings
    "LAM": "lamentations", # Lamentations - verse differences
    "EZK": "ezekiel",     # Ezekiel - verse renumberings
    "DAN": "daniel",      # Daniel - verse renumberings
    "HOS": "hosea",       # Hosea - verse renumberings
    "AMO": "amos",        # Amos - verse differences
    "OBA": "obadiah",     # Obadiah - verse differences
    "JON": "jonah",       # Jonah - verse renumberings
    "MIC": "micah",       # Micah - verse differences
    "NAM": "nahum",       # Nahum - verse differences
    "HAB": "habakkuk",    # Habakkuk - verse differences
    "ZEP": "zephaniah",   # Zephaniah - verse differences
    "HAG": "haggai",      # Haggai - verse differences
    "ZEC": "zechariah",   # Zechariah - verse renumberings
    "MAL": "malachi",     # Malachi - chapter shifts
    # Note: Joel excluded due to incompatible chapter structure (Hebrew has 4 chapters, mapping assumes different divisions)
}


def download_versification_data():
    """Download the raw versification JSON from Copenhagen Alliance."""
    print(f"Downloading versification data from: {VERSIFICATION_URL}")

    try:
        response = requests.get(VERSIFICATION_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error downloading versification data: {e}")
        sys.exit(1)


def has_versification_differences(book_data):
    """
    Check if a book has actual versification differences.

    Returns True if the book has merged-verses or mapping data that indicates
    differences between Hebrew and English versification.
    """
    # Check for merged verses (indicates verse merging/splitting)
    if "merged-verses" in book_data and book_data["merged-verses"]:
        return True

    # Check for mapping data (indicates verse renumbering)
    if "mapping" in book_data and book_data["mapping"]:
        return True

    return False


def parse_verse_range(range_str):
    """
    Parse a verse range like "3:1-9" into (chapter, start_verse, end_verse).

    Args:
        range_str: String like "3:1-9" or "3:1"

    Returns:
        tuple: (chapter_num, start_verse, end_verse) or (chapter_num, verse, verse) for single verse
    """
    if ':' not in range_str:
        raise ValueError(f"Invalid range format: {range_str}")

    chapter_part, verse_part = range_str.split(':', 1)

    try:
        chapter = int(chapter_part)

        if '-' in verse_part:
            start_verse, end_verse = verse_part.split('-', 1)
            start_verse = int(start_verse)
            end_verse = int(end_verse)
        else:
            start_verse = end_verse = int(verse_part)

        return chapter, start_verse, end_verse
    except ValueError as e:
        raise ValueError(f"Could not parse verse range '{range_str}': {e}")


def create_psalms_mapping(psa_entries, mapped_verses):
    """
    Create mapping for Psalms with superscription shifts.

    Hebrew Psalms include verse 0 (superscription) as verse 1.
    English starts content verses as verse 1.
    """
    mapping = {}

    for entry in psa_entries:
        source_ref = entry  # e.g., "PSA 3:0-8"
        target_ref = mapped_verses[entry]  # e.g., "PSA 3:1-9"

        try:
            # Parse source (Hebrew) and target (English) ranges
            source_chapter, source_start, source_end = parse_verse_range(source_ref.replace('PSA ', ''))
            target_chapter, target_start, target_end = parse_verse_range(target_ref.replace('PSA ', ''))

            # Validate that chapters match
            if source_chapter != target_chapter:
                print(f"Warning: Chapter mismatch in {entry}: {source_chapter} vs {target_chapter}")
                continue

            # Create verse mapping for this chapter
            chapter_map = {}
            hebrew_verse = source_start
            english_verse = target_start

            while hebrew_verse <= source_end and english_verse <= target_end:
                chapter_map[str(hebrew_verse)] = f"{target_chapter}:{english_verse}"
                hebrew_verse += 1
                english_verse += 1

            if chapter_map:
                mapping[str(source_chapter)] = chapter_map

        except ValueError as e:
            print(f"Warning: Could not parse PSA entry {entry}: {e}")
            continue

    return mapping


def create_joel_mapping(jol_entries, mapped_verses):
    """
    Create mapping for Joel with chapter shifts.

    Hebrew Joel 2:28-32 = English Joel 3:1-5
    Hebrew Joel 3:1-21 = English Joel 4:1-21
    """
    mapping = {}

    for entry in jol_entries:
        source_ref = entry  # e.g., "JOL 2:28-32"
        target_ref = mapped_verses[entry]  # e.g., "JOL 3:1-5"

        try:
            # Parse source (Hebrew) and target (English) ranges
            source_chapter, source_start, source_end = parse_verse_range(source_ref.replace('JOL ', ''))
            target_chapter, target_start, target_end = parse_verse_range(target_ref.replace('JOL ', ''))

            # Create verse mapping for this chapter
            chapter_map = {}
            hebrew_verse = source_start
            english_verse = target_start

            while hebrew_verse <= source_end and english_verse <= target_end:
                # Format English reference as "chapter:verse"
                english_ref = f"{target_chapter}:{english_verse}"
                chapter_map[str(hebrew_verse)] = english_ref
                hebrew_verse += 1
                english_verse += 1

            if chapter_map:
                mapping[str(source_chapter)] = chapter_map

        except ValueError as e:
            print(f"Warning: Could not parse JOL entry {entry}: {e}")
            continue

    return mapping


def create_malachi_mapping(mal_entries, mapped_verses):
    """
    Create mapping for Malachi with chapter shifts.

    English Malachi 4:1-6 = Hebrew Malachi 3:19-24
    """
    mapping = {}

    for entry in mal_entries:
        source_ref = entry  # e.g., "MAL 4:1-6"
        target_ref = mapped_verses[entry]  # e.g., "MAL 3:19-24"

        try:
            # Parse source (English) and target (Hebrew) ranges
            source_chapter, source_start, source_end = parse_verse_range(source_ref.replace('MAL ', ''))
            target_chapter, target_start, target_end = parse_verse_range(target_ref.replace('MAL ', ''))

            # For Malachi, the mapping is reversed - we need Hebrew to English
            # So we create the inverse mapping
            chapter_map = {}
            english_verse = source_start
            hebrew_verse = target_start

            while english_verse <= source_end and hebrew_verse <= target_end:
                # Format English reference as "chapter:verse"
                english_ref = f"{source_chapter}:{english_verse}"
                chapter_map[str(hebrew_verse)] = english_ref
                english_verse += 1
                hebrew_verse += 1

            if chapter_map:
                mapping[str(target_chapter)] = chapter_map

        except ValueError as e:
            print(f"Warning: Could not parse MAL entry {entry}: {e}")
            continue

    return mapping


def process_book(book_osis, book_data, book_type):
    """
    Process a single book and create simplified mapping structure.

    Args:
        book_osis: OSIS code (e.g., "PSA", "JOL")
        book_data: Raw book data from source JSON
        book_type: "superscription_shift" or "chapter_shift"

    Returns:
        Simplified book mapping dict or None if no valid mappings
    """
    if book_type == "superscription_shift":
        mapping = create_superscription_mapping(book_data)
        description = "Hebrew counts psalm titles as verse 1; English starts content as verse 1"
    elif book_type == "chapter_shift":
        mapping = create_chapter_shift_mapping(book_data)
        if book_osis == "JOL":
            description = "Hebrew Joel 2:28-32 = English Joel 3:1-5"
        elif book_osis == "MAL":
            description = "Hebrew Mal 3:19-24 = English Mal 4:1-6"
        else:
            description = f"{book_osis} has chapter shifts between Hebrew and English versification"
    else:
        return None

    # Only return if we have actual mappings
    if not mapping:
        return None

    return {
        "type": book_type,
        "description": description,
        "simple_map": mapping
    }


def create_general_mapping(entries, mapped_verses, osis_code):
    """
    Create a general mapping from versification entries.
    This handles various types of versification differences.

    IMPORTANT: The Copenhagen Alliance data has ENGLISH as source and HEBREW as target.
    We need to INVERT this to store: Hebrew verse → English reference.
    """
    mapping = {}

    for entry in entries:
        english_ref = entry  # e.g., "GEN 31:55" - this is the ENGLISH reference
        hebrew_ref = mapped_verses[entry]  # e.g., "GEN 32:1" - this is the HEBREW reference

        try:
            # Parse English and Hebrew references
            english_parts = english_ref.replace(osis_code + ' ', '').split(':')
            hebrew_parts = hebrew_ref.replace(osis_code + ' ', '').split(':')

            english_chapter = int(english_parts[0])
            hebrew_chapter = int(hebrew_parts[0])

            # Handle verse ranges
            if '-' in english_parts[1]:
                english_start, english_end = map(int, english_parts[1].split('-'))
            else:
                english_start = english_end = int(english_parts[1])

            if '-' in hebrew_parts[1]:
                hebrew_start, hebrew_end = map(int, hebrew_parts[1].split('-'))
            else:
                hebrew_start = hebrew_end = int(hebrew_parts[1])

            # Create INVERTED mapping: Hebrew → English
            # We store by Hebrew chapter, mapping Hebrew verse to English chapter:verse
            if hebrew_chapter not in mapping:
                mapping[hebrew_chapter] = {}

            # For ranges, map each verse individually
            english_verse = english_start
            hebrew_verse = hebrew_start

            while english_verse <= english_end and hebrew_verse <= hebrew_end:
                # Store: Hebrew verse → English chapter:verse
                english_ref_formatted = f"{english_chapter}:{english_verse}"
                mapping[hebrew_chapter][str(hebrew_verse)] = english_ref_formatted
                english_verse += 1
                hebrew_verse += 1

        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse {osis_code} entry {entry}: {e}")
            continue

    return mapping


def create_simplified_versification(raw_data):
    """
    Create simplified versification mapping from raw Copenhagen Alliance data.

    Focuses on Tanakh books with versification differences.
    """
    simplified = {}

    # Get the mappedVerses data
    mapped_verses = raw_data.get('mappedVerses', {})
    if not isinstance(mapped_verses, dict):
        print("Warning: mappedVerses is not a dict")
        return simplified

    # Process all books in our allowed list
    for osis_code, internal_name in TANAKH_BOOKS_WITH_DIFFERENCES.items():
        # Find entries for this book
        book_entries = [k for k in mapped_verses.keys() if k.startswith(osis_code)]

        if not book_entries:
            continue

        print(f"Processing {osis_code} ({internal_name}) - {len(book_entries)} entries")

        # Create mapping based on book type
        if osis_code == "PSA":
            # Psalms have special superscription handling
            mapping = create_psalms_mapping(book_entries, mapped_verses)
            book_type = "superscription_shift"
            description = "Hebrew counts psalm titles as verse 1; English starts content as verse 1"
        elif osis_code == "MAL":
            # Malachi has special chapter shift handling
            mapping = create_malachi_mapping(book_entries, mapped_verses)
            book_type = "chapter_shift"
            description = "Hebrew Malachi 3:19-24 = English Malachi 4:1-6"
        else:
            # General versification differences
            mapping = create_general_mapping(book_entries, mapped_verses, osis_code)
            book_type = "verse_differences"
            description = f"{internal_name.title()} has versification differences between Hebrew and English traditions"

        if mapping:
            simplified[osis_code] = {
                "type": book_type,
                "description": description,
                "simple_map": mapping
            }
            print(f"  Created mapping with {len(mapping)} chapters")

    return simplified


def save_versification_data(data):
    """Save the simplified versification data to JSON file."""
    # Create directory if it doesn't exist
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Save with nice formatting for readability
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved versification data to: {OUTPUT_PATH}")
    print(f"File size: {OUTPUT_PATH.stat().st_size} bytes")


def main():
    """Main execution function."""
    print("Shafan Versification Mapping Script")
    print("=" * 40)

    # Download raw data
    raw_data = download_versification_data()
    print(f"Downloaded data for {len(raw_data)} books")

    # Create simplified version
    simplified_data = create_simplified_versification(raw_data)

    # Save result
    save_versification_data(simplified_data)

    # Summary
    print(f"\nProcessed {len(simplified_data)} Tanakh books with versification differences:")
    for osis_code, book_data in simplified_data.items():
        internal_name = TANAKH_BOOKS_WITH_DIFFERENCES.get(osis_code, "unknown")
        chapters_mapped = len(book_data["simple_map"])
        print(f"  - {osis_code} ({internal_name}): {chapters_mapped} chapters, {book_data['type']}")

    print("\nSuccess! Versification mapping complete.")


if __name__ == "__main__":
    main()