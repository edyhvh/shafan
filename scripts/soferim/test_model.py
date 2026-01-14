#!/usr/bin/env python3
"""
Quick test script to debug model predictions.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import predict
import hebrew_tokens

def test_model():
    # Load model
    model_path = Path(__file__).parent.parent.parent / 'models' / 'soferim_stage2_finetuned.pt'
    if not model_path.exists():
        print(f"Model not found at {model_path}")
        return

    print(f"Loading model from {model_path}")

    # Build vocabulary
    vocab = hebrew_tokens.HebrewWordVocabulary()
    project_root = Path(__file__).parent.parent.parent

    # Load training texts to build vocab
    moriah_csv = project_root / 'data' / 'review' / 'hutter_moriah.csv'
    lena_csv = project_root / 'data' / 'review' / 'hutter_lena.csv'

    all_texts = []

    # Load Moriah data
    if moriah_csv.exists():
        import csv
        with open(moriah_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                original = row.get('current_text', '').strip()
                corrected = row.get('corrected_text', '').strip()
                if original and corrected:
                    all_texts.extend([original, corrected])

    # Load Lena data
    if lena_csv.exists():
        import csv
        with open(lena_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                original = row.get('current_text', '').strip()
                corrected = row.get('corrected_text', '').strip()
                if original and corrected:
                    all_texts.extend([original, corrected])

    vocab.build_vocab(all_texts)
    print(f"Vocabulary size: {len(vocab)}")

    # Load predictor
    try:
        predictor = predict.SoferimPredictor(str(model_path), vocab, device='cpu')
        print("Model loaded successfully")
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    # Test with a simple verse
    test_verse = "יְהוּדָה עֶבֶד יֵשׁוּעַ הַמָּשִׁיחַ וְאָחִי יַעֲקֹב לְאֵשֶׁר בֵּאלֹהִים הָאָב נִקְדָּשִׁים רִבְשׁוּעַ הַמָּשִׁיחַ נִקְרָאִים וְנִגְנֹּבִים וְהָמַּח"
    print(f"\nTesting with verse: {test_verse[:50]}...")

    try:
        result = predictor.predict_verse(test_verse, confidence_threshold=0.1, top_k=3)
        print(f"Prediction successful!")
        print(f"Corrections found: {len(result['corrections'])}")

        for i, corr in enumerate(result['corrections'][:5]):  # Show first 5
            print(f"  {i+1}. Word '{corr['original_word']}' (confidence: {corr['error_confidence']:.3f})")
            for j, suggestion in enumerate(corr['suggestions'][:2]):
                print(f"     -> '{suggestion['word']}' (conf: {suggestion['confidence']:.3f})")

    except Exception as e:
        print(f"Prediction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_model()