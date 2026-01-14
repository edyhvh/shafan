#!/usr/bin/env python3
"""
Error Dictionary Builder for Soferim Text Correction.

Extracts word-level error→correction pairs from Lena and Moriah's manual reviews.
Creates a lookup dictionary for known OCR errors.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
import csv
import json
import re

# Add parent directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import hebrew utilities from nakdimon
sys.path.insert(0, str(current_dir.parent / 'nakdimon'))
import hebrew

class ErrorDictionary:
    """
    Builds and manages a dictionary of known word-level corrections from manual reviews.
    """

    # Hebrew word separators
    WORD_SEPARATORS = r'[\s־׃׀.,;:?!"\'()\[\]]+'

    def __init__(self):
        """
        Initialize the error dictionary.
        """
        self.error_to_correction: Dict[str, str] = {}  # wrong_word -> correct_word_with_nikud
        self.correction_metadata: Dict[str, Dict] = {}  # wrong_word -> metadata

    def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize Hebrew text into words.

        Args:
            text: Hebrew text to tokenize

        Returns:
            List of words
        """
        if not text:
            return []

        # Split on word boundaries
        words = re.split(self.WORD_SEPARATORS, text.strip())

        # Filter out empty strings
        return [word for word in words if word.strip()]

    def extract_word_corrections(self, wrong_text: str, correct_text: str,
                               book: str, chapter: int, verse: int) -> List[Tuple[str, str]]:
        """
        Extract word-level corrections from a wrong→correct text pair.

        Args:
            wrong_text: Original text with errors
            correct_text: Corrected text
            book: Book name
            chapter: Chapter number
            verse: Verse number

        Returns:
            List of (wrong_word, correct_word) tuples
        """
        wrong_words = self.tokenize_text(wrong_text)
        correct_words = self.tokenize_text(correct_text)

        corrections = []

        # Find word-level differences
        min_len = min(len(wrong_words), len(correct_words))

        for i in range(min_len):
            wrong_word = wrong_words[i]
            correct_word = correct_words[i]

            # Skip identical words
            if wrong_word == correct_word:
                continue

            # Normalize for comparison (remove nikud)
            wrong_normalized = hebrew.normalize_nikud(wrong_word)
            correct_normalized = hebrew.normalize_nikud(correct_word)

            # Only include if they're actually different
            if wrong_normalized != correct_normalized and len(wrong_normalized) > 1:
                corrections.append((wrong_word, correct_word))

        return corrections

    def load_lena_reviews(self, lena_csv: Path, vocalized_csv: Path) -> None:
        """
        Load Lena's reviews and merge with vocalized corrections.

        Args:
            lena_csv: Path to hutter_lena.csv
            vocalized_csv: Path to lena_vocalized.csv
        """
        print(f"Loading Lena's reviews from {lena_csv} and {vocalized_csv}...")

        # Load vocalized corrections (preferred)
        vocalized_data = {}
        with open(vocalized_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['book'], int(row['chapter']), int(row['verse']))
                vocalized_data[key] = row['vocalized_text']

        print(f"Loaded {len(vocalized_data)} vocalized corrections")

        # Load main Lena CSV and merge
        corrections_added = 0

        with open(lena_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                book = row['book']
                chapter = int(row['chapter'])
                verse = int(row['verse'])

                wrong_text = row['current_text']
                key = (book, chapter, verse)

                # Use vocalized correction if available, otherwise corrected_text
                correct_text = vocalized_data.get(key, row['corrected_text'])

                if not correct_text:
                    continue

                # Extract word-level corrections
                word_corrections = self.extract_word_corrections(
                    wrong_text, correct_text, book, chapter, verse
                )

                # Add to dictionary
                for wrong_word, correct_word in word_corrections:
                    self.error_to_correction[wrong_word] = correct_word
                    self.correction_metadata[wrong_word] = {
                        'source': 'lena',
                        'book': book,
                        'chapter': chapter,
                        'verse': verse,
                        'confidence': 'high'  # Manual review
                    }
                    corrections_added += 1

        print(f"Added {corrections_added} corrections from Lena's reviews")

    def load_moriah_reviews(self, moriah_csv: Path) -> None:
        """
        Load Moriah's reviews.

        Args:
            moriah_csv: Path to hutter_moriah.csv
        """
        print(f"Loading Moriah's reviews from {moriah_csv}...")

        corrections_added = 0

        with open(moriah_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                book = row['book']
                chapter = int(row['chapter'])
                verse = int(row['verse'])

                wrong_text = row['current_text']
                correct_text = row['corrected_text']

                if not correct_text:
                    continue

                # Extract word-level corrections
                word_corrections = self.extract_word_corrections(
                    wrong_text, correct_text, book, chapter, verse
                )

                # Add to dictionary
                for wrong_word, correct_word in word_corrections:
                    self.error_to_correction[wrong_word] = correct_word
                    self.correction_metadata[wrong_word] = {
                        'source': 'moriah',
                        'book': book,
                        'chapter': chapter,
                        'verse': verse,
                        'confidence': 'high'  # Manual review
                    }
                    corrections_added += 1

        print(f"Added {corrections_added} corrections from Moriah's reviews")

    def build_dictionary(self, lena_csv: Path = None, vocalized_csv: Path = None,
                        moriah_csv: Path = None) -> None:
        """
        Build the complete error dictionary from manual reviews.

        Args:
            lena_csv: Path to hutter_lena.csv
            vocalized_csv: Path to lena_vocalized.csv
            moriah_csv: Path to hutter_moriah.csv
        """
        # Auto-detect paths if not provided
        if lena_csv is None or vocalized_csv is None or moriah_csv is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            data_dir = project_root / 'data' / 'review'
            nakdimon_dir = project_root / 'data' / 'nakdimon' / 'output'

            lena_csv = data_dir / 'hutter_lena.csv'
            vocalized_csv = nakdimon_dir / 'lena_vocalized.csv'
            moriah_csv = data_dir / 'hutter_moriah.csv'

        print("Building error dictionary from manual reviews...")

        # Load Lena's reviews
        if lena_csv.exists() and vocalized_csv.exists():
            self.load_lena_reviews(lena_csv, vocalized_csv)
        else:
            print("Warning: Lena's review files not found")

        # Load Moriah's reviews
        if moriah_csv.exists():
            self.load_moriah_reviews(moriah_csv)
        else:
            print("Warning: Moriah's review file not found")

        print(f"Error dictionary built with {len(self.error_to_correction)} unique corrections")

    def get_correction(self, wrong_word: str) -> str:
        """
        Get the correction for a word if it exists in the dictionary.

        Args:
            wrong_word: Word that might be wrong

        Returns:
            Corrected word (with nikud) or empty string if not found
        """
        return self.error_to_correction.get(wrong_word, "")

    def get_metadata(self, wrong_word: str) -> Dict:
        """
        Get metadata for a correction.

        Args:
            wrong_word: Word to get metadata for

        Returns:
            Metadata dictionary or empty dict if not found
        """
        return self.correction_metadata.get(wrong_word, {})

    def save_dictionary(self, filepath: str) -> None:
        """
        Save the error dictionary to a JSON file.

        Args:
            filepath: Path to save the dictionary
        """
        data = {
            'dictionary_size': len(self.error_to_correction),
            'error_to_correction': self.error_to_correction,
            'correction_metadata': self.correction_metadata
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Error dictionary saved to {filepath}")

    def load_dictionary(self, filepath: str) -> None:
        """
        Load a previously saved error dictionary.

        Args:
            filepath: Path to the saved dictionary
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.error_to_correction = data['error_to_correction']
        self.correction_metadata = data.get('correction_metadata', {})

        print(f"Error dictionary loaded with {len(self.error_to_correction)} corrections")

    def get_stats(self) -> Dict:
        """
        Get statistics about the error dictionary.

        Returns:
            Statistics dictionary
        """
        sources = {}
        books = set()

        for metadata in self.correction_metadata.values():
            source = metadata.get('source', 'unknown')
            book = metadata.get('book', 'unknown')

            sources[source] = sources.get(source, 0) + 1
            books.add(book)

        return {
            'total_corrections': len(self.error_to_correction),
            'sources': sources,
            'books': sorted(list(books))
        }

def main():
    """
    Build and save the error dictionary.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Build error dictionary from manual reviews')
    parser.add_argument('--output', '-o', type=str, default='error_dictionary.json',
                       help='Output file for error dictionary')
    parser.add_argument('--lena-csv', type=str,
                       help='Path to hutter_lena.csv')
    parser.add_argument('--vocalized-csv', type=str,
                       help='Path to lena_vocalized.csv')
    parser.add_argument('--moriah-csv', type=str,
                       help='Path to hutter_moriah.csv')

    args = parser.parse_args()

    # Build dictionary
    error_dict = ErrorDictionary()
    error_dict.build_dictionary(
        lena_csv=args.lena_csv,
        vocalized_csv=args.vocalized_csv,
        moriah_csv=args.moriah_csv
    )

    # Print stats
    stats = error_dict.get_stats()
    print(f"\nDictionary Statistics:")
    print(f"  Total corrections: {stats['total_corrections']}")
    print(f"  Sources: {stats['sources']}")
    print(f"  Books: {', '.join(stats['books'])}")

    # Save dictionary
    output_path = Path(args.output)
    error_dict.save_dictionary(str(output_path))

    print(f"\nError dictionary saved to {output_path}")

if __name__ == '__main__':
    main()