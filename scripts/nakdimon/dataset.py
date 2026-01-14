#!/usr/bin/env python3
"""
Dataset loading and preprocessing for PyTorch Hebrew diacritizer.

Loads Moriah's vocalized text and creates training pairs for the model.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import csv
import json
import torch
from torch.utils.data import Dataset
from pathlib import Path
# Import our modules
import hebrew

class HebrewDiacritizationDataset(Dataset):
    """
    Dataset for Hebrew diacritization training.

    Each sample is a sequence of Hebrew characters with their corresponding
    nikud marks as targets.
    """

    def __init__(self, csv_path, max_length=512):
        """
        Initialize dataset from CSV file.

        Args:
            csv_path: Path to CSV file with vocalized Hebrew text
            max_length: Maximum sequence length
        """
        self.max_length = max_length
        self.samples = []

        # Load and process data
        self._load_data(csv_path)

    def _load_data(self, csv_path):
        """Load and preprocess data from CSV."""
        print(f"Loading data from {csv_path}...")

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row.get('corrected_text', '').strip()
                if not text:
                    continue

                # Normalize nikud ordering
                normalized_text = hebrew.normalize_nikud(text)

                # Create training sample
                sample = self._process_text(normalized_text)
                if sample:
                    self.samples.append(sample)

        print(f"Loaded {len(self.samples)} training samples")

    def _process_text(self, text):
        """
        Process a single text sample into input and targets.

        Args:
            text: Normalized Hebrew text with nikud

        Returns:
            dict: {'input': input_sequence, 'targets': (vowels, dagesh, shin), 'length': seq_len}
        """
        input_chars = []
        vowel_targets = []
        dagesh_targets = []
        shin_targets = []

        i = 0
        while i < len(text):
            char = text[i]

            if hebrew.is_hebrew_letter(char):
                # Add letter to input
                input_chars.append(hebrew.char_to_idx(char))

                # Initialize targets as "none" (0)
                vowel_target = 0  # <none>
                dagesh_target = 0  # <none>
                shin_target = 0    # <none>

                # Look ahead for nikud marks
                i += 1
                while i < len(text):
                    mark = text[i]

                    if mark in hebrew.VOWELS:
                        vowel_target = hebrew.NIKUD_VOCAB['vowels'].get(mark, 0)
                        i += 1
                    elif mark in hebrew.DAGESH:
                        dagesh_target = hebrew.NIKUD_VOCAB['dagesh'].get(mark, 0)
                        i += 1
                    elif mark in hebrew.SHIN_DOTS:
                        shin_target = hebrew.NIKUD_VOCAB['shin'].get(mark, 0)
                        i += 1
                    else:
                        break  # Not a nikud mark, stop looking ahead

                # Add targets
                vowel_targets.append(vowel_target)
                dagesh_targets.append(dagesh_target)
                shin_targets.append(shin_target)

            elif char in [' ', '־']:  # Space or maqaf
                # Add to input but with no nikud targets (all zeros)
                input_chars.append(hebrew.char_to_idx(char))
                vowel_targets.append(0)
                dagesh_targets.append(0)
                shin_targets.append(0)
                i += 1
            else:
                # Skip unknown characters
                i += 1

        # Skip if too short or too long
        if len(input_chars) < 2 or len(input_chars) > self.max_length:
            return None

        return {
            'input': input_chars,
            'targets': (vowel_targets, dagesh_targets, shin_targets),
            'length': len(input_chars)
        }

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]

    def collate_fn(self, batch):
        """
        Collate function for DataLoader.

        Args:
            batch: List of samples

        Returns:
            dict: Batched tensors
        """
        # Sort by length (descending) for packed sequences
        batch.sort(key=lambda x: x['length'], reverse=True)

        # Get max length in batch
        max_len = max(x['length'] for x in batch)

        # Get padding indices (separate from 0 which is <none>)
        pad_idx = hebrew.CHAR_VOCAB['<pad>']  # Should be different from 0

        # Pad sequences
        input_batch = []
        vowel_batch = []
        dagesh_batch = []
        shin_batch = []
        lengths = []

        for sample in batch:
            input_seq = sample['input']
            vowel_seq, dagesh_seq, shin_seq = sample['targets']
            length = sample['length']

            # Pad input sequence with <pad> token
            padded_input = input_seq + [pad_idx] * (max_len - len(input_seq))
            input_batch.append(padded_input)

            # Pad target sequences with <pad> token (-100 for loss masking)
            padded_vowel = vowel_seq + [-100] * (max_len - len(vowel_seq))
            padded_dagesh = dagesh_seq + [-100] * (max_len - len(dagesh_seq))
            padded_shin = shin_seq + [-100] * (max_len - len(shin_seq))

            vowel_batch.append(padded_vowel)
            dagesh_batch.append(padded_dagesh)
            shin_batch.append(padded_shin)

            lengths.append(length)

        return {
            'input': torch.tensor(input_batch, dtype=torch.long),
            'targets': (
                torch.tensor(vowel_batch, dtype=torch.long),
                torch.tensor(dagesh_batch, dtype=torch.long),
                torch.tensor(shin_batch, dtype=torch.long)
            ),
            'lengths': torch.tensor(lengths, dtype=torch.long)
        }

def create_data_loader(csv_path, batch_size=4, shuffle=True, max_length=512, validation_split=0.1):
    """
    Create DataLoader for Hebrew diacritization training with validation split.

    Args:
        csv_path: Path to CSV file
        batch_size: Batch size
        shuffle: Whether to shuffle data
        max_length: Maximum sequence length
        validation_split: Fraction of data for validation (0.0 to 1.0)

    Returns:
        tuple: (train_loader, val_loader) if validation_split > 0, else (data_loader, None)
    """
    from torch.utils.data import DataLoader, random_split

    dataset = HebrewDiacritizationDataset(csv_path, max_length=max_length)

    if validation_split > 0:
        # Split dataset
        val_size = int(len(dataset) * validation_split)
        train_size = len(dataset) - val_size
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            collate_fn=dataset.collate_fn,
            num_workers=0
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            collate_fn=dataset.collate_fn,
            num_workers=0
        )

        return train_loader, val_loader
    else:
        data_loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            collate_fn=dataset.collate_fn,
            num_workers=0
        )
        return data_loader, None

def load_moriah_data(project_root=None, validation_split=0.0, batch_size=4):
    """
    Load Moriah training data with optional validation split.

    Args:
        project_root: Path to project root (optional, auto-detects)
        validation_split: Fraction of data for validation
        batch_size: Batch size for data loading

    Returns:
        tuple: (train_loader, val_loader) if validation_split > 0, else (data_loader, None)
    """
    if project_root is None:
        # Auto-detect project root
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent

    csv_path = project_root / 'data' / 'review' / 'hutter_moriah.csv'

    if not csv_path.exists():
        raise FileNotFoundError(f"Moriah data not found at {csv_path}")

    return create_data_loader(csv_path, batch_size=batch_size, shuffle=True, validation_split=validation_split)

def load_delitzsch_data(project_root=None, validation_split=0.1, augment_data=False, max_samples=5000):
    """
    Load Delitzsch Hebrew NT corpus for training with data augmentation and validation split.

    Args:
        project_root: Path to project root (optional, auto-detects)
        validation_split: Fraction of data for validation
        augment_data: Whether to augment data by concatenating verses

    Returns:
        tuple: (train_loader, val_loader) if validation_split > 0, else (data_loader, None)
    """
    if project_root is None:
        # Auto-detect project root
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent

    delitzsch_dir = project_root / 'data' / 'delitzsch'
    delitzsch_data = []

    print(f"Loading Delitzsch corpus from {delitzsch_dir}...")

    # Load each JSON file
    json_files = list(delitzsch_dir.glob('*.json'))
    print(f"Found {len(json_files)} JSON files to process")

    for json_file in json_files:
        print(f"  Processing {json_file.name}...")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                book_data = json.load(f)

            # Extract verses from all chapters
            for chapter in book_data['chapters']:
                for verse in chapter['verses']:
                    vocalized_text = verse['text_nikud'].strip()
                    if vocalized_text:
                        delitzsch_data.append(vocalized_text)

        except Exception as e:
            print(f"    Error processing {json_file}: {e}")
            continue

    print(f"Loaded {len(delitzsch_data)} verses from Delitzsch corpus")

    # Limit dataset size for faster training
    if max_samples and len(delitzsch_data) > max_samples:
        delitzsch_data = delitzsch_data[:max_samples]
        print(f"Limited to {max_samples} samples for faster training")

    # Data augmentation: concatenate adjacent verses for longer sequences
    if augment_data and len(delitzsch_data) > 1:
        augmented_data = []
        # Add original verses
        augmented_data.extend(delitzsch_data)

        # Add concatenated pairs (verse n + verse n+1)
        for i in range(len(delitzsch_data) - 1):
            combined = delitzsch_data[i] + ' ' + delitzsch_data[i + 1]
            augmented_data.append(combined)

        # Add concatenated triplets (verse n + n+1 + n+2)
        for i in range(len(delitzsch_data) - 2):
            combined = delitzsch_data[i] + ' ' + delitzsch_data[i + 1] + ' ' + delitzsch_data[i + 2]
            augmented_data.append(combined)

        delitzsch_data = augmented_data
        print(f"After augmentation: {len(delitzsch_data)} training samples")

    # Create a temporary CSV file for the data loader
    temp_csv_path = project_root / 'data' / 'temp' / 'delitzsch.csv'
    temp_csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(temp_csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['corrected_text'])  # Only vocalized text column needed
        for vocalized_text in delitzsch_data:
            writer.writerow([vocalized_text])

    print(f"Created temporary CSV at {temp_csv_path}")

    return create_data_loader(temp_csv_path, batch_size=16, shuffle=True, validation_split=validation_split)

def load_lena_data_for_prediction(project_root=None):
    """
    Load Lena data for prediction (without nikud).

    Args:
        project_root: Path to project root

    Returns:
        list: List of (verse_text, book, chapter, verse) tuples
    """
    if project_root is None:
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent

    csv_path = project_root / 'data' / 'review' / 'hutter_lena.csv'

    verses = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            verse_text = row.get('corrected_text', '').strip()
            book = row.get('book', '').strip()
            chapter = row.get('chapter', '').strip()
            verse = row.get('verse', '').strip()
            if verse_text:
                # Strip nikud for prediction input
                consonant_text = hebrew.strip_nikud(verse_text)
                verses.append((consonant_text, book, chapter, verse))

    return verses