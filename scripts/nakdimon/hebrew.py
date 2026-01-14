#!/usr/bin/env python3
"""
Hebrew character definitions and mappings for PyTorch diacritizer.

Defines the Hebrew alphabet, nikud marks, and character-to-index mappings
for training and inference.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports (only needed if imported by other modules)
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Hebrew letters (22 regular + 5 final forms)
HEBREW_LETTERS = [
    # Regular letters (22)
    'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י',
    'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת',
    # Final forms (5)
    'ך', 'ם', 'ן', 'ף', 'ץ'
]

# Nikud marks (vowel points and diacritics)
NIKUD_MARKS = {
    # Vowels (12)
    'שְׁוָא': '\u05B0',      # Shva
    'חֲטַף-סְגוֹל': '\u05B1', # Hataf segol
    'חֲטַף-פַּתַח': '\u05B2', # Hataf patach
    'חֲטַף-קָמַץ': '\u05B3', # Hataf kamatz
    'חִירִיק': '\u05B4',     # Hirik
    'צֵירֵא': '\u05B5',      # Tsere
    'סֶגוֹל': '\u05B6',      # Segol
    'פַּתַח': '\u05B7',      # Patach
    'קָמַץ': '\u05B8',       # Kamatz
    'חוֹלַם': '\u05B9',      # Holam
    'קֻבּוּץ': '\u05BB',     # Kubutz
    'שׁוּרֻק': '\u05BC',     # Shuruk (same as dagesh)

    # Dagesh and related
    'דָּגֵשׁ': '\u05BC',     # Dagesh

    # Shin/sin dots
    'שִׁין יְמָנִית': '\u05C1', # Shin dot (right)
    'שִׁין שְׂמָאלִית': '\u05C2', # Sin dot (left)
}

# For easier access, create lists of marks by category
VOWELS = [
    '\u05B0', '\u05B1', '\u05B2', '\u05B3', '\u05B4',
    '\u05B5', '\u05B6', '\u05B7', '\u05B8', '\u05B9', '\u05BB'
]  # 11 vowels (shuruk is separate)

DAGESH = ['\u05BC']  # Dagesh (only one)

SHIN_DOTS = ['\u05C1', '\u05C2']  # Shin and sin dots

# Special characters
SPACE = ' '
MAQAF = '־'  # Hebrew hyphen

# All valid input characters (Hebrew letters + space + maqaf)
VALID_INPUT_CHARS = HEBREW_LETTERS + [SPACE, MAQAF]

# Create character-to-index mappings for model input
def create_char_vocab():
    """Create vocabulary for Hebrew characters."""
    vocab = {}
    idx = 0

    # Add Hebrew letters
    for char in HEBREW_LETTERS:
        vocab[char] = idx
        idx += 1

    # Add space and maqaf
    vocab[SPACE] = idx
    idx += 1
    vocab[MAQAF] = idx
    idx += 1

    # Add padding and unknown tokens
    vocab['<pad>'] = idx
    idx += 1
    vocab['<unk>'] = idx
    idx += 1

    return vocab

# Create index-to-character mappings for nikud marks
def create_nikud_vocab():
    """Create vocabulary for nikud marks (3 separate outputs)."""
    # Vowel classes (12: 11 vowels + none)
    vowel_vocab = {'<none>': 0}
    for i, mark in enumerate(VOWELS):
        vowel_vocab[mark] = i + 1

    # Dagesh classes (2: none, dagesh)
    dagesh_vocab = {'<none>': 0, '\u05BC': 1}

    # Shin dot classes (3: none, shin, sin)
    shin_vocab = {'<none>': 0, '\u05C1': 1, '\u05C2': 2}

    return {
        'vowels': vowel_vocab,
        'dagesh': dagesh_vocab,
        'shin': shin_vocab
    }

# Global vocabularies
CHAR_VOCAB = create_char_vocab()
NIKUD_VOCAB = create_nikud_vocab()

def char_to_idx(char):
    """Convert character to index for model input."""
    return CHAR_VOCAB.get(char, CHAR_VOCAB['<unk>'])

def idx_to_char(idx):
    """Convert index back to character."""
    for char, index in CHAR_VOCAB.items():
        if index == idx:
            return char
    return '<unk>'

def get_vocab_sizes():
    """Get vocabulary sizes for model architecture."""
    return {
        'input_vocab_size': len(CHAR_VOCAB),
        'vowel_vocab_size': len(NIKUD_VOCAB['vowels']),
        'dagesh_vocab_size': len(NIKUD_VOCAB['dagesh']),
        'shin_vocab_size': len(NIKUD_VOCAB['shin'])
    }

def is_hebrew_letter(char):
    """Check if character is a Hebrew letter."""
    return char in HEBREW_LETTERS

def strip_nikud(text):
    """Remove all nikud marks from Hebrew text."""
    # Remove all nikud Unicode characters
    nikud_chars = set(VOWELS + DAGESH + SHIN_DOTS)
    return ''.join(char for char in text if char not in nikud_chars)

def normalize_nikud(text):
    """
    Normalize nikud marks for consistent processing.
    Similar to our previous normalization but simpler for PyTorch.
    """
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
            shin_dot = None
            vowel = None

            while i < len(text):
                mark = text[i]
                if mark in DAGESH and dagesh is None:
                    dagesh = mark
                    i += 1
                elif mark in SHIN_DOTS and shin_dot is None:
                    shin_dot = mark
                    i += 1
                elif mark in VOWELS and vowel is None:
                    vowel = mark
                    i += 1
                else:
                    break  # Not a mark, stop collecting

            # Append in correct order: dagesh, shin_dot, vowel
            if dagesh:
                result.append(dagesh)
            if shin_dot:
                result.append(shin_dot)
            if vowel:
                result.append(vowel)
        else:
            # Not a Hebrew letter, just append
            result.append(char)
            i += 1

    return ''.join(result)