#!/usr/bin/env python3
"""
Hebrew Lexicon Builder for Soferim Text Correction.

Builds a set of valid Hebrew words from Delitzsch reference texts and
processed output files for nonsense word detection.
"""

import sys
from pathlib import Path
from typing import Set
import json
import re

# Add parent directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import hebrew utilities from nakdimon
sys.path.insert(0, str(current_dir.parent / 'nakdimon'))
import hebrew

class HebrewLexicon:
    """
    Builds and manages a set of valid Hebrew words for nonsense detection.
    """

    # Hebrew word separators (including maqaf and common punctuation)
    WORD_SEPARATORS = r'[\s־׃׀.,;:?!"\'()\[\]]+'

    def __init__(self, min_word_length: int = 2):
        """
        Initialize the lexicon.

        Args:
            min_word_length: Minimum length for words to include
        """
        self.min_word_length = min_word_length
        self.valid_words: Set[str] = set()

    def normalize_hebrew_word(self, word: str) -> str:
        """
        Normalize a Hebrew word by removing nikud and standardizing forms.

        Args:
            word: Hebrew word with or without nikud

        Returns:
            Normalized word (lowercase, no nikud)
        """
        if not word or len(word.strip()) < self.min_word_length:
            return ""

        # Remove nikud and standardize
        normalized = hebrew.normalize_nikud(word.strip())

        # Remove any remaining non-Hebrew characters except basic punctuation
        # Keep Hebrew letters, maqaf, and basic punctuation
        normalized = re.sub(r'[^\u0590-\u05FF\u200f\u200e\-]', '', normalized)

        return normalized.lower() if len(normalized) >= self.min_word_length else ""

    def tokenize_text(self, text: str) -> Set[str]:
        """
        Tokenize Hebrew text into words and normalize them.

        Args:
            text: Hebrew text to tokenize

        Returns:
            Set of normalized words
        """
        if not text:
            return set()

        # Split on word boundaries
        words = re.split(self.WORD_SEPARATORS, text)

        # Normalize each word and filter
        normalized_words = set()
        for word in words:
            normalized = self.normalize_hebrew_word(word)
            if normalized:
                normalized_words.add(normalized)

        return normalized_words

    def load_delitzsch_books(self, delitzsch_dir: Path) -> None:
        """
        Load all Delitzsch reference books and extract words.

        Args:
            delitzsch_dir: Directory containing Delitzsch JSON files
        """
        print(f"Loading Delitzsch books from {delitzsch_dir}...")

        if not delitzsch_dir.exists():
            raise FileNotFoundError(f"Delitzsch directory not found: {delitzsch_dir}")

        json_files = list(delitzsch_dir.glob("*.json"))
        print(f"Found {len(json_files)} Delitzsch books")

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    book_data = json.load(f)

                book_name = book_data.get('book_name', json_file.stem)
                print(f"  Processing {book_name}...")

                # Process each chapter
                for chapter in book_data.get('chapters', []):
                    for verse in chapter.get('verses', []):
                        verse_text = verse.get('text_nikud', '')
                        words = self.tokenize_text(verse_text)
                        self.valid_words.update(words)

            except Exception as e:
                print(f"    Error processing {json_file}: {e}")
                continue

        print(f"  Added {len(self.valid_words)} words from Delitzsch")

    def load_output_books(self, output_dir: Path) -> None:
        """
        Load processed output books and extract words.

        Args:
            output_dir: Directory containing output JSON files
        """
        print(f"Loading output books from {output_dir}...")

        if not output_dir.exists():
            raise FileNotFoundError(f"Output directory not found: {output_dir}")

        json_files = list(output_dir.glob("*.json"))
        # Filter out temp directory files
        json_files = [f for f in json_files if 'temp' not in str(f)]

        print(f"Found {len(json_files)} output books")

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    book_data = json.load(f)

                book_name = book_data.get('book_name', json_file.stem)
                print(f"  Processing {book_name}...")

                # Process each chapter
                for chapter in book_data.get('chapters', []):
                    for verse in chapter.get('verses', []):
                        verse_text = verse.get('text_nikud', '')
                        words = self.tokenize_text(verse_text)
                        self.valid_words.update(words)

            except Exception as e:
                print(f"    Error processing {json_file}: {e}")
                continue

        print(f"  Added {len(self.valid_words)} total words")

    def build_lexicon(self, delitzsch_dir: Path = None, output_dir: Path = None) -> None:
        """
        Build the complete lexicon from Delitzsch and output files.

        Args:
            delitzsch_dir: Directory with Delitzsch files (auto-detected if None)
            output_dir: Directory with output files (auto-detected if None)
        """
        # Auto-detect directories if not provided
        if delitzsch_dir is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            delitzsch_dir = project_root / 'data' / 'delitzsch'

        if output_dir is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            output_dir = project_root / 'output'

        print("Building Hebrew lexicon...")

        # Load Delitzsch reference texts
        self.load_delitzsch_books(delitzsch_dir)

        # Load processed output texts
        self.load_output_books(output_dir)

        # Add some common Hebrew words that might be missing
        common_words = {
            'אלהים', 'יהוה', 'ישראל', 'תורה', 'משה', 'דוד',
            'אברהם', 'יצחק', 'יעקב', 'יוסף', 'יהודה'
        }
        self.valid_words.update(common_words)

        print(f"Lexicon built with {len(self.valid_words)} unique Hebrew words")

    def is_valid_word(self, word: str) -> bool:
        """
        Check if a word is in the valid Hebrew lexicon.

        Args:
            word: Word to check (will be normalized)

        Returns:
            True if word is valid, False otherwise
        """
        normalized = self.normalize_hebrew_word(word)
        return normalized in self.valid_words if normalized else False

    def save_lexicon(self, filepath: str) -> None:
        """
        Save the lexicon to a JSON file.

        Args:
            filepath: Path to save the lexicon
        """
        data = {
            'lexicon_size': len(self.valid_words),
            'min_word_length': self.min_word_length,
            'valid_words': sorted(list(self.valid_words))
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Lexicon saved to {filepath}")

    def load_lexicon(self, filepath: str) -> None:
        """
        Load a previously saved lexicon.

        Args:
            filepath: Path to the saved lexicon
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.valid_words = set(data['valid_words'])
        self.min_word_length = data.get('min_word_length', 2)

        print(f"Lexicon loaded with {len(self.valid_words)} words")

def main():
    """
    Build and save the Hebrew lexicon.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Build Hebrew word lexicon')
    parser.add_argument('--output', '-o', type=str, default='hebrew_lexicon.json',
                       help='Output file for lexicon')
    parser.add_argument('--delitzsch-dir', type=str,
                       help='Directory with Delitzsch JSON files')
    parser.add_argument('--output-dir', type=str,
                       help='Directory with processed output JSON files')

    args = parser.parse_args()

    # Build lexicon
    lexicon = HebrewLexicon()
    lexicon.build_lexicon(delitzsch_dir=args.delitzsch_dir, output_dir=args.output_dir)

    # Save lexicon
    output_path = Path(args.output)
    lexicon.save_lexicon(str(output_path))

    print(f"\nLexicon saved to {output_path}")
    print(f"Total words: {len(lexicon.valid_words)}")

if __name__ == '__main__':
    main()