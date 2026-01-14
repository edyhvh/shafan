#!/usr/bin/env python3
"""
Rule-Based OCR Correction System for Soferim.

Implements two correction paths:
- Path B: Known errors from manual reviews (Lena/Moriah)
- Path A: Nonsense words + Delitzsch confirmation
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import json
import re
import difflib

# Add parent directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import our modules
from hebrew_lexicon import HebrewLexicon
from error_dictionary import ErrorDictionary

# Import hebrew utilities from nakdimon
sys.path.insert(0, str(current_dir.parent / 'nakdimon'))
import hebrew

class RuleBasedCorrector:
    """
    Main correction engine implementing both correction paths.
    """

    # Hebrew word separators
    WORD_SEPARATORS = r'[\s־׃׀.,;:?!"\'()\[\]]+'

    def __init__(self, lexicon: HebrewLexicon, error_dict: ErrorDictionary):
        """
        Initialize the corrector.

        Args:
            lexicon: HebrewLexicon instance for nonsense detection
            error_dict: ErrorDictionary instance for known corrections
        """
        self.lexicon = lexicon
        self.error_dict = error_dict

        # Weighted edit distance for common OCR confusions
        self.ocr_confusions = {
            ('ד', 'ר'): 0.5,  # Very common confusion
            ('ר', 'ד'): 0.5,
            ('ה', 'ח'): 0.7,  # Common confusions
            ('ח', 'ה'): 0.7,
            ('ת', 'ח'): 0.7,
            ('ח', 'ת'): 0.7,
            ('ב', 'כ'): 0.7,
            ('כ', 'ב'): 0.7,
        }

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

    def calculate_weighted_distance(self, word1: str, word2: str) -> float:
        """
        Calculate weighted edit distance accounting for OCR confusions.

        Args:
            word1: First word
            word2: Second word

        Returns:
            Weighted distance (lower = more similar)
        """
        # Normalize nikud for comparison
        w1 = hebrew.normalize_nikud(word1)
        w2 = hebrew.normalize_nikud(word2)

        # Use sequence matcher for basic similarity
        matcher = difflib.SequenceMatcher(None, w1, w2)
        base_distance = 1.0 - matcher.ratio()

        # Apply OCR confusion weights
        weighted_distance = base_distance

        # Check for common OCR confusions and reduce distance
        if len(w1) == len(w2):
            for i, (c1, c2) in enumerate(zip(w1, w2)):
                if c1 != c2:
                    confusion_key = (c1, c2)
                    if confusion_key in self.ocr_confusions:
                        weight = self.ocr_confusions[confusion_key]
                        weighted_distance *= weight  # Reduce distance for common errors

        return weighted_distance

    def find_delitzsch_matches(self, target_word: str, delitzsch_text: str,
                             max_distance: float = 0.3) -> List[Tuple[str, float]]:
        """
        Find similar words in Delitzsch text.

        Args:
            target_word: Word to find matches for
            delitzsch_text: Delitzsch verse text
            max_distance: Maximum weighted distance for matches

        Returns:
            List of (matched_word, distance) tuples, sorted by distance
        """
        delitzsch_words = self.tokenize_text(delitzsch_text)
        matches = []

        for delitzsch_word in delitzsch_words:
            distance = self.calculate_weighted_distance(target_word, delitzsch_word)
            if distance <= max_distance:
                matches.append((delitzsch_word, distance))

        # Sort by distance (best matches first)
        matches.sort(key=lambda x: x[1])

        return matches

    def get_correction_confidence(self, correction_type: str, distance: float = 0.0) -> str:
        """
        Determine confidence level for a correction.

        Args:
            correction_type: Type of correction applied
            distance: Weighted distance (for fuzzy matches)

        Returns:
            Confidence level string
        """
        if correction_type == 'known_error':
            return 'high'
        elif correction_type == 'delitzsch_match':
            if distance <= 0.1:
                return 'medium'
            elif distance <= 0.2:
                return 'low'
            else:
                return 'very_low'
        else:
            return 'unknown'

    def correct_verse(self, hutter_text: str, delitzsch_text: str) -> Dict:
        """
        Correct a single verse using both correction paths.

        Args:
            hutter_text: Original Hutter text
            delitzsch_text: Delitzsch reference text

        Returns:
            Correction results dictionary
        """
        hutter_words = self.tokenize_text(hutter_text)
        corrections = []
        corrected_words = []

        for i, word in enumerate(hutter_words):
            original_word = word
            corrected_word = word  # Default: keep original
            correction_type = 'none'
            confidence = 'none'
            metadata = {}

            # PATH B: Check known errors first (highest priority)
            known_correction = self.error_dict.get_correction(word)
            if known_correction:
                # Validate that the correction makes sense in this context
                # Check if Delitzsch has a similar word to the proposed correction
                delitzsch_matches = self.find_delitzsch_matches(known_correction, delitzsch_text, max_distance=0.2)
                if delitzsch_matches:
                    corrected_word = known_correction
                    correction_type = 'known_error'
                    confidence = self.get_correction_confidence('known_error')
                    metadata = self.error_dict.get_metadata(word)
                    metadata['delitzsch_validation'] = delitzsch_matches[0]  # Best match
                # If no Delitzsch validation, don't apply the correction
            else:
                # PATH A: Check if word is nonsense
                if not self.lexicon.is_valid_word(word):
                    # Find matches in Delitzsch
                    matches = self.find_delitzsch_matches(word, delitzsch_text)

                    if matches:
                        # Use best match
                        best_match, distance = matches[0]
                        corrected_word = best_match
                        correction_type = 'delitzsch_match'
                        confidence = self.get_correction_confidence('delitzsch_match', distance)
                        metadata = {
                            'distance': distance,
                            'all_matches': matches
                        }

            # Add to results
            corrected_words.append(corrected_word)

            if correction_type != 'none':
                corrections.append({
                    'word_index': i,
                    'original_word': original_word,
                    'corrected_word': corrected_word,
                    'correction_type': correction_type,
                    'confidence': confidence,
                    'metadata': metadata
                })

        # Reconstruct corrected text
        corrected_text = ' '.join(corrected_words)

        # Handle maqaf and punctuation (simplified)
        # In a full implementation, we'd preserve original punctuation
        corrected_text = re.sub(r'\s+', ' ', corrected_text).strip()

        return {
            'original_text': hutter_text,
            'corrected_text': corrected_text,
            'delitzsch_reference': delitzsch_text,
            'corrections': corrections,
            'total_corrections': len(corrections),
            'correction_types': {
                'known_error': sum(1 for c in corrections if c['correction_type'] == 'known_error'),
                'delitzsch_match': sum(1 for c in corrections if c['correction_type'] == 'delitzsch_match')
            }
        }

    def correct_book(self, book_json_path: str, output_json_path: str) -> Dict:
        """
        Correct all verses in a book.

        Args:
            book_json_path: Path to book JSON file
            output_json_path: Path to output corrections JSON

        Returns:
            Summary statistics
        """
        print(f"Correcting book: {book_json_path}")

        # Load book data
        with open(book_json_path, 'r', encoding='utf-8') as f:
            book_data = json.load(f)

        book_name = book_data['book_name']
        results = []
        total_corrections = 0

        # Process each chapter
        for chapter in book_data.get('chapters', []):
            chapter_num = chapter['number']
            print(f"  Processing chapter {chapter_num}...")

            for verse in chapter.get('verses', []):
                verse_num = verse['number']
                hutter_text = verse.get('text_nikud', '').strip()
                delitzsch_text = verse.get('text_nikud_delitzsch', '').strip()

                if not hutter_text:
                    continue

                # Correct the verse
                correction_result = self.correct_verse(hutter_text, delitzsch_text)

                # Add metadata
                verse_result = {
                    'book': book_name,
                    'chapter': chapter_num,
                    'verse': verse_num,
                    **correction_result
                }

                results.append(verse_result)
                total_corrections += correction_result['total_corrections']

        # Save results
        output_data = {
            'book': book_name,
            'total_verses': len(results),
            'total_corrections': total_corrections,
            'correction_types': {
                'known_error': sum(r['correction_types']['known_error'] for r in results),
                'delitzsch_match': sum(r['correction_types']['delitzsch_match'] for r in results)
            },
            'corrections': results
        }

        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"  Saved {total_corrections} corrections to {output_json_path}")

        return {
            'book': book_name,
            'verses_processed': len(results),
            'total_corrections': total_corrections,
            'known_errors': output_data['correction_types']['known_error'],
            'delitzsch_matches': output_data['correction_types']['delitzsch_match']
        }

def load_corrector(lexicon_path: str = None, error_dict_path: str = None) -> RuleBasedCorrector:
    """
    Load a RuleBasedCorrector with pre-built lexicon and error dictionary.

    Args:
        lexicon_path: Path to saved Hebrew lexicon
        error_dict_path: Path to saved error dictionary

    Returns:
        Initialized RuleBasedCorrector
    """
    # Auto-detect paths
    if lexicon_path is None or error_dict_path is None:
        current_file = Path(__file__)
        soferim_dir = current_file.parent

        lexicon_path = soferim_dir / 'hebrew_lexicon.json'
        error_dict_path = soferim_dir / 'error_dictionary.json'

    # Load lexicon
    lexicon = HebrewLexicon()
    if lexicon_path.exists():
        lexicon.load_lexicon(str(lexicon_path))
    else:
        print(f"Warning: Lexicon not found at {lexicon_path}")
        lexicon.build_lexicon()

    # Load error dictionary
    error_dict = ErrorDictionary()
    if error_dict_path.exists():
        error_dict.load_dictionary(str(error_dict_path))
    else:
        print(f"Warning: Error dictionary not found at {error_dict_path}")
        error_dict.build_dictionary()

    return RuleBasedCorrector(lexicon, error_dict)

def main():
    """
    Command-line interface for the rule-based corrector.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Rule-based OCR correction for Hebrew text')
    parser.add_argument('--book-json', type=str, help='Path to input book JSON file')
    parser.add_argument('--output-json', type=str, help='Path to output corrections JSON')
    parser.add_argument('--lexicon', type=str, help='Path to Hebrew lexicon JSON')
    parser.add_argument('--error-dict', type=str, help='Path to error dictionary JSON')
    parser.add_argument('--text', type=str, help='Single text to correct')
    parser.add_argument('--delitzsch-text', type=str, help='Delitzsch reference text (for single text)')

    args = parser.parse_args()

    # Load corrector
    corrector = load_corrector(args.lexicon, args.error_dict)

    if args.book_json and args.output_json:
        # Correct entire book
        stats = corrector.correct_book(args.book_json, args.output_json)
        print("\nCorrection completed!")
        print(f"Book: {stats['book']}")
        print(f"Verses processed: {stats['verses_processed']}")
        print(f"Total corrections: {stats['total_corrections']}")
        print(f"Known errors applied: {stats['known_errors']}")
        print(f"Delitzsch matches: {stats['delitzsch_matches']}")

    elif args.text and args.delitzsch_text:
        # Correct single text
        result = corrector.correct_verse(args.text, args.delitzsch_text)

        print("Original text:", args.text)
        print("Corrected text:", result['corrected_text'])
        print("Delitzsch reference:", args.delitzsch_text)
        print("Corrections found:", result['total_corrections'])

        for correction in result['corrections']:
            print(f"  Word {correction['word_index']}: '{correction['original_word']}' → '{correction['corrected_word']}' ({correction['confidence']})")

    else:
        parser.error("Must provide either --book-json with --output-json, or --text with --delitzsch-text")

if __name__ == '__main__':
    main()