#!/usr/bin/env python3
"""
Apply manual corrections from CSV review files to output JSON books.

This script processes corrections from two sources:
1. hutter_moriah.csv - Moriah's corrections to Hutter's text
2. lena_vocalized.csv - Lena's vocalized text corrections

When both sources have corrections for the same verse, Moriah's takes priority.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from collections import defaultdict

# Constants
MORAH_CSV_PATH = Path("data/review/hutter_moriah.csv")
LENA_CSV_PATH = Path("data/nakdimon/output/lena_vocalized.csv")
OUTPUT_DIR = Path("output")
LOG_FILE = Path("data/review/manual_corrections_log.json")

def load_moriah_corrections() -> Dict[Tuple[str, int, int], Dict]:
    """Load corrections from Moriah's CSV file."""
    corrections = {}
    if not MORAH_CSV_PATH.exists():
        print(f"Warning: {MORAH_CSV_PATH} not found")
        return corrections

    with open(MORAH_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                book = row['book']
                chapter = int(row['chapter'])
                verse = int(row['verse'])
                key = (book, chapter, verse)

                corrections[key] = {
                    'corrected_text': row['corrected_text'],
                    'source': 'moriah',
                    'comments': row.get('comments', ''),
                    'uncertainty': row.get('uncertainty', ''),
                    'current_text': row.get('current_text', '')
                }
            except (ValueError, KeyError) as e:
                print(f"Error parsing row in {MORAH_CSV_PATH}: {row}")
                continue

    return corrections

def load_lena_corrections() -> Dict[Tuple[str, int, int], Dict]:
    """Load corrections from Lena's CSV file."""
    corrections = {}
    if not LENA_CSV_PATH.exists():
        print(f"Warning: {LENA_CSV_PATH} not found")
        return corrections

    with open(LENA_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                book = row['book']
                chapter = int(row['chapter'])
                verse = int(row['verse'])
                key = (book, chapter, verse)

                corrections[key] = {
                    'corrected_text': row['vocalized_text'],
                    'source': 'lena',
                    'comments': '',
                    'uncertainty': '',
                    'current_text': ''
                }
            except (ValueError, KeyError) as e:
                print(f"Error parsing row in {LENA_CSV_PATH}: {row}")
                continue

    return corrections

def merge_corrections(moriah_corrections: Dict, lena_corrections: Dict) -> Dict[Tuple[str, int, int], Dict]:
    """
    Merge corrections from both sources, with Moriah taking priority on conflicts.
    """
    merged = {}

    # Add all Moriah corrections first
    for key, correction in moriah_corrections.items():
        merged[key] = correction

    # Add Lena corrections only if no Moriah correction exists
    conflicts = 0
    for key, correction in lena_corrections.items():
        if key in merged:
            conflicts += 1
            # Moriah takes priority, but mark that there was a conflict
            merged[key]['conflict_with_lena'] = True
            merged[key]['lena_text'] = correction['corrected_text']
        else:
            merged[key] = correction

    print(f"Total corrections: {len(merged)}")
    print(f"Conflicts resolved (Moriah priority): {conflicts}")
    print(f"Moriah corrections: {len(moriah_corrections)}")
    print(f"Lena corrections: {len(lena_corrections)}")

    return merged

def apply_corrections(corrections: Dict[Tuple[str, int, int], Dict]) -> Dict[str, List[Dict]]:
    """
    Apply corrections to the JSON files and return summary.
    """
    timestamp = datetime.now().isoformat()
    applied_corrections = defaultdict(list)
    books_processed = set()

    # Group corrections by book
    corrections_by_book = defaultdict(list)
    for key, correction in corrections.items():
        book, chapter, verse = key
        corrections_by_book[book].append((chapter, verse, correction))

    for book, book_corrections in corrections_by_book.items():
        json_path = OUTPUT_DIR / f"{book}.json"
        if not json_path.exists():
            print(f"Warning: {json_path} not found, skipping corrections for {book}")
            continue

        print(f"Processing {book}...")

        # Load the JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        corrections_applied = 0

        # Apply corrections to each chapter
        for chapter_data in data['chapters']:
            chapter_num = chapter_data['number']

            # Find corrections for this chapter
            chapter_corrections = [
                (verse, correction) for ch, verse, correction in book_corrections
                if ch == chapter_num
            ]

            if not chapter_corrections:
                continue

            # Apply corrections to verses
            for verse_data in chapter_data['verses']:
                verse_num = verse_data['number']

                # Find correction for this verse
                correction = None
                for v, corr in chapter_corrections:
                    if v == verse_num:
                        correction = corr
                        break

                if correction:
                    # Rebuild the verse object with correction metadata after source_files
                    new_verse_data = {
                        'number': verse_data['number'],
                        'text_nikud': correction['corrected_text'],
                        'source_files': verse_data['source_files'],
                        'manually_corrected': True,
                        'correction_timestamp': timestamp,
                        'correction_source': correction['source']
                    }

                    # Add optional correction fields
                    if correction['comments']:
                        new_verse_data['correction_comments'] = correction['comments']

                    if correction.get('uncertainty'):
                        new_verse_data['correction_uncertainty'] = correction['uncertainty']

                    if correction.get('conflict_with_lena'):
                        new_verse_data['correction_conflict_with_lena'] = True
                        new_verse_data['lena_correction_text'] = correction['lena_text']

                    # Add remaining fields in original order
                    if 'visual_uncertainty' in verse_data:
                        new_verse_data['visual_uncertainty'] = verse_data['visual_uncertainty']
                    if 'text_nikud_delitzsch' in verse_data:
                        new_verse_data['text_nikud_delitzsch'] = verse_data['text_nikud_delitzsch']

                    # Replace the verse data
                    chapter_data['verses'][chapter_data['verses'].index(verse_data)] = new_verse_data

                    corrections_applied += 1

                    # Track for logging
                    applied_corrections[book].append({
                        'chapter': chapter_num,
                        'verse': verse_num,
                        'source': correction['source'],
                        'timestamp': timestamp,
                        'has_conflict': correction.get('conflict_with_lena', False)
                    })

        # Save the updated JSON file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        books_processed.add(book)
        print(f"Applied {corrections_applied} corrections to {book}")

    return dict(applied_corrections)

def generate_log(applied_corrections: Dict[str, List[Dict]], total_stats: Dict):
    """Generate a summary log file."""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_books_processed': len(applied_corrections),
            'total_corrections_applied': sum(len(corrections) for corrections in applied_corrections.values()),
            'books': list(applied_corrections.keys()),
            **total_stats
        },
        'corrections_by_book': applied_corrections
    }

    # Ensure log directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    print(f"Log written to {LOG_FILE}")

def main():
    print("Loading corrections from CSV files...")

    moriah_corrections = load_moriah_corrections()
    lena_corrections = load_lena_corrections()

    print(f"Loaded {len(moriah_corrections)} corrections from Moriah")
    print(f"Loaded {len(lena_corrections)} corrections from Lena")

    merged_corrections = merge_corrections(moriah_corrections, lena_corrections)

    total_stats = {
        'moriah_corrections': len(moriah_corrections),
        'lena_corrections': len(lena_corrections),
        'conflicts_resolved': len([c for c in merged_corrections.values() if c.get('conflict_with_lena')])
    }

    print("\nApplying corrections to JSON files...")
    applied_corrections = apply_corrections(merged_corrections)

    print("\nGenerating summary log...")
    generate_log(applied_corrections, total_stats)

    print("\nDone!")
    print(f"Total corrections applied: {total_stats['moriah_corrections'] + total_stats['lena_corrections'] - total_stats['conflicts_resolved']}")

if __name__ == "__main__":
    main()