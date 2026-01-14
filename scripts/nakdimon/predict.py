#!/usr/bin/env python3
"""
Prediction/inference script for PyTorch Hebrew diacritizer.

Loads trained model and vocalizes Hebrew text by adding nikud marks.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import torch
import csv
from pathlib import Path
from typing import List, Tuple

# Import our modules
import model
import dataset
import hebrew

class HebrewVocalizer:
    """
    Class for vocalizing Hebrew text using trained PyTorch model.
    """

    def __init__(self, model_path, device='cpu'):
        """
        Initialize vocalizer with trained model.

        Args:
            model_path: Path to trained model
            device: Device to run inference on
        """
        self.device = device
        self.model = model.load_model(model_path, device)

        # Create reverse mappings for predictions
        self.vowel_idx_to_char = {idx: char for char, idx in hebrew.NIKUD_VOCAB['vowels'].items()}
        self.dagesh_idx_to_char = {idx: char for char, idx in hebrew.NIKUD_VOCAB['dagesh'].items()}
        self.shin_idx_to_char = {idx: char for char, idx in hebrew.NIKUD_VOCAB['shin'].items()}

    def vocalize_text(self, text: str) -> str:
        """
        Vocalize a single Hebrew text by adding nikud marks.

        Args:
            text: Hebrew text without nikud

        Returns:
            str: Vocalized Hebrew text
        """
        if not text.strip():
            return text

        # Convert text to indices
        input_indices = [hebrew.char_to_idx(char) for char in text]

        # Convert to tensor
        input_tensor = torch.tensor([input_indices], dtype=torch.long).to(self.device)

        # Get predictions
        vowel_preds, dagesh_preds, shin_preds = self.model.predict(input_tensor)

        # Convert predictions back to text
        vocalized_text = self._predictions_to_text(
            input_indices,
            vowel_preds[0].cpu().numpy(),
            dagesh_preds[0].cpu().numpy(),
            shin_preds[0].cpu().numpy()
        )

        # Apply Hutter-specific post-processing
        vocalized_text = self._post_process_hutter(vocalized_text)

        return vocalized_text

    def _predictions_to_text(self, input_indices, vowel_preds, dagesh_preds, shin_preds):
        """
        Convert model predictions back to vocalized text.

        Args:
            input_indices: Original character indices
            vowel_preds: Vowel predictions (indices)
            dagesh_preds: Dagesh predictions (indices)
            shin_preds: Shin dot predictions (indices)

        Returns:
            str: Vocalized text
        """
        result = []

        for i, char_idx in enumerate(input_indices):
            # Get original character
            char = hebrew.idx_to_char(char_idx)

            # Add character
            result.append(char)

            # Add nikud marks if this is a Hebrew letter
            if hebrew.is_hebrew_letter(char):
                # Add marks in correct order: dagesh, shin_dot, vowel
                if i < len(dagesh_preds) and dagesh_preds[i] > 0:
                    dagesh_char = self.dagesh_idx_to_char.get(dagesh_preds[i], '')
                    if dagesh_char:
                        result.append(dagesh_char)

                if i < len(shin_preds) and shin_preds[i] > 0:
                    shin_char = self.shin_idx_to_char.get(shin_preds[i], '')
                    if shin_char:
                        result.append(shin_char)

                if i < len(vowel_preds) and vowel_preds[i] > 0:
                    vowel_char = self.vowel_idx_to_char.get(vowel_preds[i], '')
                    if vowel_char:
                        result.append(vowel_char)

        return ''.join(result)

    def _post_process_hutter(self, text):
        """
        Apply Hutter-specific post-processing rules to improve vocalization accuracy.

        Args:
            text: Vocalized Hebrew text from model

        Returns:
            str: Post-processed text with Hutter-specific corrections
        """
        result = list(text)

        # Rule 1: Maqaf handling - ensure proper word boundaries around maqaf
        i = 0
        while i < len(result):
            if result[i] == '־':  # Hebrew maqaf
                # Remove any stray marks immediately after maqaf
                j = i + 1
                while j < len(result) and result[j] in hebrew.VOWELS + hebrew.DAGESH + hebrew.SHIN_DOTS:
                    result[j] = ''
                    j += 1
                i = j
            else:
                i += 1

        # Rule 2: YHWH handling - special vocalization for divine name
        # Look for patterns like יהוה with various vocalizations
        text_str = ''.join(result)
        text_str = text_str.replace('יְהֹוָה', 'יְהוָה')  # Common Hutter pattern
        text_str = text_str.replace('יְהוִה', 'יְהוָה')   # Alternative pattern
        result = list(text_str)

        # Rule 3: Greek name handling - remove excessive marks on proper names
        # Common Greek names in NT that often get over-vocalized
        greek_names = ['פַּוְלוֹס', 'יֵשׁוּעַ', 'יֹהָנָן', 'פֶּטְרוֹס', 'יַעֲקֹב', 'אַנְדְּרֵי']
        for name in greek_names:
            # Remove extra dagesh/shin dots that are common model errors
            if name in text_str:
                text_str = text_str.replace(name + '\u05bc', name)  # Remove extra dagesh
                text_str = text_str.replace(name + '\u05c1', name)  # Remove extra shin dot
                text_str = text_str.replace(name + '\u05c2', name)  # Remove extra sin dot

        # Rule 4: Fix common over-marking patterns (remove duplicate marks)
        result = list(text_str)
        i = 0
        while i < len(result) - 1:
            # Remove consecutive duplicate marks
            if result[i] in hebrew.VOWELS + hebrew.DAGESH + hebrew.SHIN_DOTS and result[i] == result[i+1]:
                result[i+1] = ''
                i += 1
            i += 1

        return ''.join(result)

    def vocalize_batch(self, texts: List[str]) -> List[str]:
        """
        Vocalize a batch of texts.

        Args:
            texts: List of Hebrew texts without nikud

        Returns:
            List[str]: List of vocalized texts
        """
        return [self.vocalize_text(text) for text in texts]

def vocalize_lena_data(model_path, output_csv_path=None, device='cpu'):
    """
    Vocalize all of Lena's data and save to CSV.

    Args:
        model_path: Path to trained model
        output_csv_path: Path to save vocalized CSV (optional)
        device: Device for inference

    Returns:
        List[Tuple[str, str, str, str]]: List of (book, chapter, verse, vocalized_text) tuples
    """
    print("Loading Lena data for vocalization...")
    lena_data = dataset.load_lena_data_for_prediction()

    print(f"Creating vocalizer with model: {model_path}")
    vocalizer = HebrewVocalizer(model_path, device)

    print(f"Vocalizing {len(lena_data)} verses...")

    vocalized_results = []
    for consonant_text, book, chapter, verse in lena_data:
        vocalized_text = vocalizer.vocalize_text(consonant_text)
        vocalized_results.append((book, chapter, verse, vocalized_text))

        if len(vocalized_results) % 10 == 0:
            print(f"  Processed {len(vocalized_results)}/{len(lena_data)} verses")

    print(f"Completed vocalization of {len(vocalized_results)} verses")

    # Save to CSV if requested
    if output_csv_path:
        print(f"Saving results to {output_csv_path}")

        # Auto-detect project root
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent

        output_path = project_root / output_csv_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['book', 'chapter', 'verse', 'vocalized_text'])
            for book, chapter, verse, vocalized_text in vocalized_results:
                writer.writerow([book, chapter, verse, vocalized_text])

        print(f"Results saved to {output_path}")

    return vocalized_results

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Vocalize Hebrew text with trained model')
    parser.add_argument('--model', type=str, required=True, help='Path to trained model')
    parser.add_argument('--input-text', type=str, help='Single text to vocalize')
    parser.add_argument('--input-csv', type=str, help='CSV file with texts to vocalize')
    parser.add_argument('--output-csv', type=str, help='Output CSV file for results')
    parser.add_argument('--device', type=str, default='cpu', help='Device for inference')

    args = parser.parse_args()

    # Create vocalizer
    vocalizer = HebrewVocalizer(args.model, args.device)

    if args.input_text:
        # Vocalize single text
        result = vocalizer.vocalize_text(args.input_text)
        print(f"Input:  {args.input_text}")
        print(f"Output: {result}")

    elif args.input_csv:
        # Vocalize CSV data
        vocalize_lena_data(args.model, args.output_csv, args.device)

    else:
        print("Please provide either --input-text or --input-csv")

if __name__ == '__main__':
    main()