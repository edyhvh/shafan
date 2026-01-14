#!/usr/bin/env python3
"""
Prediction script for Soferim Hebrew text correction model.

Generates correction suggestions with confidence scores for Hebrew text.
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json

# Add parent directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import torch
import torch.nn as nn

# Import our modules
import model
import hebrew_tokens

class SoferimPredictor:
    """
    Predictor class for Soferim text correction model.
    """

    def __init__(self, model_path: str, vocab: hebrew_tokens.HebrewWordVocabulary, device: str = 'cpu'):
        """
        Initialize predictor.

        Args:
            model_path: Path to trained model
            vocab: Word vocabulary
            device: Device to run predictions on
        """
        self.device = device
        self.vocab = vocab
        self.tokenizer = hebrew_tokens.HebrewWordTokenizer()

        # Load model
        self.model = model.load_model(model_path, device)
        self.model.eval()

    def predict_verse(self, verse_text: str, confidence_threshold: float = 0.4,
                     top_k: int = 3) -> Dict:
        """
        Predict corrections for a single verse.

        Args:
            verse_text: Hebrew text to correct
            confidence_threshold: Minimum confidence for suggestions
            top_k: Maximum suggestions per error

        Returns:
            dict: Correction results
        """
        # Tokenize the text
        tokens = self.tokenizer.tokenize(verse_text)
        token_indices = [self.vocab[token] for token in tokens]

        # Pad to model's expected length (must match training)
        max_len = 32  # Matches training max_length
        if len(token_indices) > max_len:
            token_indices = token_indices[:max_len]
            tokens = tokens[:max_len]

        padded_tokens = token_indices + [self.vocab['<pad>']] * (max_len - len(token_indices))

        # Convert to tensor
        input_tensor = torch.tensor([padded_tokens], dtype=torch.long).to(self.device)

        # Get model predictions
        with torch.no_grad():
            outputs = self.model(input_tensor)
            error_probs = outputs['error_probs'][0]  # Remove batch dimension
            correction_logits = outputs['correction_logits'][0]  # (seq_len, vocab_size)

        # Process predictions
        corrections = []
        for i, (token, error_prob) in enumerate(zip(tokens, error_probs)):
            error_confidence = error_prob.item()

            # Skip if below threshold
            if error_confidence < confidence_threshold:
                continue

            # Get correction candidates
            pos_logits = correction_logits[i]  # (vocab_size,)
            probs = torch.softmax(pos_logits, dim=-1)

            # Get top-k candidates (excluding the original word)
            top_probs, top_indices = torch.topk(probs, k=top_k + 1)

            candidates = []
            for prob, idx in zip(top_probs, top_indices):
                suggested_word = self.vocab[idx.item()]
                confidence = prob.item()

                # Skip padding, unknown, and the original word
                if (suggested_word not in ['<pad>', '<unk>'] and
                    suggested_word != token and
                    confidence > 0.1):  # Additional confidence filter

                    candidates.append({
                        'word': suggested_word,
                        'confidence': confidence
                    })

                    if len(candidates) >= top_k:
                        break

            if candidates:
                corrections.append({
                    'word_index': i,
                    'original_word': token,
                    'error_confidence': error_confidence,
                    'suggestions': candidates
                })

        return {
            'original_text': verse_text,
            'corrections': corrections,
            'total_corrections': len(corrections)
        }

    def predict_batch(self, verses: List[str], confidence_threshold: float = 0.5,
                     top_k: int = 3) -> List[Dict]:
        """
        Predict corrections for multiple verses.

        Args:
            verses: List of Hebrew text strings
            confidence_threshold: Minimum confidence for suggestions
            top_k: Maximum suggestions per error

        Returns:
            list: List of correction results
        """
        results = []
        for verse_text in verses:
            result = self.predict_verse(verse_text, confidence_threshold, top_k)
            results.append(result)

        return results

def load_predictor(model_path: str, vocab_path: Optional[str] = None, device: str = 'cpu') -> SoferimPredictor:
    """
    Load a trained Soferim predictor.

    Args:
        model_path: Path to trained model
        vocab_path: Path to vocabulary (if separate from model)
        device: Device for predictions

    Returns:
        SoferimPredictor: Loaded predictor
    """
    # For now, we'll recreate the vocabulary from training data
    # In practice, you'd want to save/load the exact vocabulary used during training

    # Load a small amount of training data to build vocabulary
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent

    try:
        # Try to load from existing training data
        from pathlib import Path
        moriah_csv = project_root / 'data' / 'review' / 'hutter_moriah.csv'

        if moriah_csv.exists():
            training_pairs = hebrew_tokens.load_training_pairs_from_csv(str(moriah_csv))
            vocab = hebrew_tokens.HebrewWordVocabulary()
            all_texts = [pair['original'] for pair in training_pairs] + \
                       [pair['corrected'] for pair in training_pairs]
            vocab.build_vocab(all_texts)
        else:
            # Fallback: create basic vocabulary
            vocab = hebrew_tokens.HebrewWordVocabulary()
            basic_texts = ["שָׁלוֹם עוֹלָם"]  # Basic Hebrew text
            vocab.build_vocab(basic_texts)

    except Exception as e:
        print(f"Warning: Could not load vocabulary: {e}")
        vocab = hebrew_tokens.HebrewWordVocabulary()

    return SoferimPredictor(model_path, vocab, device)

def predict_from_json(json_path: str, model_path: str, output_path: str,
                     confidence_threshold: float = 0.4, top_k: int = 3):
    """
    Predict corrections for all verses in a JSON book file.

    Args:
        json_path: Path to book JSON file (e.g., jude.json)
        model_path: Path to trained model
        output_path: Path to output JSON file
        confidence_threshold: Minimum confidence for suggestions
        top_k: Maximum suggestions per error
    """
    # Load book data
    with open(json_path, 'r', encoding='utf-8') as f:
        book_data = json.load(f)

    book_name = book_data['book_name']

    # Load predictor
    predictor = load_predictor(model_path)

    # Process all verses
    results = []
    total_verses = 0
    verses_with_corrections = 0

    for chapter in book_data['chapters']:
        chapter_num = chapter['number']

        for verse in chapter['verses']:
            verse_num = verse['number']
            verse_text = verse['text_nikud'].strip()

            if not verse_text:
                continue

            total_verses += 1

            # Get predictions
            prediction = predictor.predict_verse(
                verse_text,
                confidence_threshold=confidence_threshold,
                top_k=top_k
            )

            # Add metadata
            verse_result = {
                'book': book_name,
                'chapter': chapter_num,
                'verse': verse_num,
                'original_text': verse_text,
                'delitzsch_reference': verse.get('text_nikud_delitzsch', ''),
                'corrections': prediction['corrections'],
                'requires_manual_review': len(prediction['corrections']) > 0
            }

            results.append(verse_result)

            if len(prediction['corrections']) > 0:
                verses_with_corrections += 1

    # Create output
    output_data = {
        'book': book_name,
        'total_verses': total_verses,
        'verses_with_corrections': verses_with_corrections,
        'confidence_threshold': confidence_threshold,
        'top_k': top_k,
        'corrections': results
    }

    # Save results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Processed {total_verses} verses from {book_name}")
    print(f"Found corrections in {verses_with_corrections} verses")
    print(f"Results saved to {output_path}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Predict Hebrew text corrections with Soferim model')
    parser.add_argument('--model-path', type=str, required=True, help='Path to trained model')
    parser.add_argument('--input-json', type=str, help='Path to input book JSON file')
    parser.add_argument('--output-json', type=str, help='Path to output corrections JSON file')
    parser.add_argument('--text', type=str, help='Single text to correct')
    parser.add_argument('--confidence-threshold', type=float, default=0.4, help='Minimum confidence for suggestions')
    parser.add_argument('--top-k', type=int, default=3, help='Maximum suggestions per error')
    parser.add_argument('--device', type=str, default='cpu', help='Device for predictions')

    args = parser.parse_args()

    # Load predictor
    predictor = load_predictor(args.model_path, device=args.device)

    if args.input_json and args.output_json:
        # Process entire book
        predict_from_json(
            args.input_json,
            args.model_path,
            args.output_json,
            args.confidence_threshold,
            args.top_k
        )

    elif args.text:
        # Process single text
        result = predictor.predict_verse(
            args.text,
            confidence_threshold=args.confidence_threshold,
            top_k=args.top_k
        )

        print("Original text:", args.text)
        print("Corrections found:", len(result['corrections']))

        for correction in result['corrections']:
            print(f"  Word {correction['word_index']}: '{correction['original_word']}' -> ", end="")
            for i, suggestion in enumerate(correction['suggestions']):
                print(f"'{suggestion['word']}' ({suggestion['confidence']:.2f})", end="")
                if i < len(correction['suggestions']) - 1:
                    print(", ", end="")
            print()

    else:
        parser.error("Must provide either --input-json with --output-json, or --text")

if __name__ == '__main__':
    main()