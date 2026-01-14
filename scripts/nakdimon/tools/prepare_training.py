#!/usr/bin/env python3
"""
Prepare Nakdimon training data from Moriah's corrected text.

Reads hutter_moriah.csv, extracts corrected_text with nikud,
strips nikud to create input/output pairs for training.
"""

import csv
import re
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def normalize_nikud(text: str) -> str:
    """
    Normalize Hebrew nikud for Nakdimon compatibility.

    Nakdimon expects marks in this order after each letter:
    1. Dagesh (U+05BC)
    2. Sin/Shin dot (U+05C1/U+05C2)
    3. Vowel (U+05B0-U+05BB, U+05B9)

    Also removes duplicate marks.

    Args:
        text: Hebrew text with potentially malformed nikud

    Returns:
        Text with normalized nikud order
    """
    HEBREW_LETTERS = set('אבגדהוזחטיכלמנסעפצקרשתךםןףץ')
    DAGESH = '\u05BC'  # ּ
    SIN_DOTS = {'\u05C1', '\u05C2'}  # שין/שׂין dots
    VOWELS = set('\u05B0\u05B1\u05B2\u05B3\u05B4\u05B5\u05B6\u05B7\u05B8\u05B9\u05BA\u05BB')

    result = []
    i = 0
    while i < len(text):
        char = text[i]

        # If it's a Hebrew letter, collect and reorder following marks
        if char in HEBREW_LETTERS:
            result.append(char)
            i += 1

            # Collect all marks following this letter
            dagesh = None
            sin_dot = None
            vowel = None

            while i < len(text):
                mark = text[i]
                if mark == DAGESH:
                    if dagesh is None:  # Only keep first dagesh
                        dagesh = mark
                    i += 1
                elif mark in SIN_DOTS:
                    if sin_dot is None:  # Only keep first sin dot
                        sin_dot = mark
                    i += 1
                elif mark in VOWELS:
                    if vowel is None:  # Only keep first vowel
                        vowel = mark
                    i += 1
                else:
                    break  # Not a mark, stop collecting

            # Append in correct order: dagesh, sin_dot, vowel
            if dagesh:
                result.append(dagesh)
            if sin_dot:
                result.append(sin_dot)
            if vowel:
                result.append(vowel)
        else:
            # Not a Hebrew letter, just append
            result.append(char)
            i += 1

    return ''.join(result)


def strip_nikud(text: str) -> str:
    """
    Remove Hebrew nikud (diacritics) from text.

    Removes Unicode combining marks in ranges:
    - U+0591 to U+05C7 (Hebrew diacritics, cantillation, dagesh, etc.)

    Args:
        text: Hebrew text with nikud

    Returns:
        Text without nikud marks
    """
    # Remove Hebrew diacritics (U+0591 to U+05C7)
    # This includes: nikud, cantillation marks, dagesh, shin/sin dots
    nikud_pattern = re.compile(r'[\u0591-\u05C7]')
    return nikud_pattern.sub('', text)


def prepare_training_data():
    """Extract training data from Moriah CSV and prepare Nakdimon format."""

    # Paths
    moriah_csv = project_root / 'data' / 'review' / 'hutter_moriah.csv'
    output_dir = project_root / 'data' / 'nakdimon' / 'training'
    output_dir.mkdir(parents=True, exist_ok=True)

    input_file = output_dir / 'moriah_input.txt'
    expected_file = output_dir / 'moriah_expected.txt'

    # Read Moriah CSV
    print(f"Reading {moriah_csv}...")
    with open(moriah_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Found {len(rows)} verses in Moriah data")

    # Extract corrected_text and create training pairs
    input_lines = []
    expected_lines = []

    for row in rows:
        corrected_text = row.get('corrected_text', '').strip()
        if not corrected_text:
            continue

        # Normalize nikud (remove duplicates like double dagesh)
        normalized_text = normalize_nikud(corrected_text)

        # Strip nikud for input
        text_without_nikud = strip_nikud(normalized_text)

        # Store training pairs
        input_lines.append(text_without_nikud)
        expected_lines.append(normalized_text)

    # Write training files
    print(f"Writing training data to {output_dir}...")

    with open(input_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(input_lines))

    with open(expected_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(expected_lines))

    print(f"✓ Created {input_file} ({len(input_lines)} lines)")
    print(f"✓ Created {expected_file} ({len(expected_lines)} lines)")
    print(f"\nTraining data ready: {len(input_lines)} verse pairs")


if __name__ == '__main__':
    prepare_training_data()
