#!/usr/bin/env python3
"""
Hebrew word-level tokenization and processing for Soferim text correction.

Tokenizes Hebrew text into words, handles nikud normalization, and creates
vocabulary for word-level processing (unlike character-level in Nakdimon).
"""

import sys
from pathlib import Path
from collections import Counter
import re

# Add parent directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import hebrew utilities from nakdimon
sys.path.insert(0, str(current_dir.parent / 'nakdimon'))
import hebrew

class HebrewWordTokenizer:
    """
    Tokenizes Hebrew text into words, handling nikud and punctuation.
    """

    # Hebrew word separators (including maqaf)
    WORD_SEPARATORS = r'[\s־]+'

    def __init__(self):
        self.word_pattern = re.compile(r'[^\s־]+')

    def tokenize(self, text):
        """
        Tokenize Hebrew text into words.

        Args:
            text: Hebrew text with or without nikud

        Returns:
            list: List of word tokens
        """
        # Normalize nikud first
        normalized_text = hebrew.normalize_nikud(text)

        # Split on word boundaries
        words = self.word_pattern.findall(normalized_text)

        # Filter out empty strings
        return [word for word in words if word.strip()]

    def tokenize_preserve_positions(self, text):
        """
        Tokenize while preserving position information.

        Args:
            text: Hebrew text

        Returns:
            list: List of (word, start_pos, end_pos) tuples
        """
        tokens = []
        normalized_text = hebrew.normalize_nikud(text)

        for match in self.word_pattern.finditer(normalized_text):
            word = match.group()
            if word.strip():
                tokens.append((word, match.start(), match.end()))

        return tokens

class HebrewWordVocabulary:
    """
    Manages Hebrew word vocabulary with frequency-based filtering.
    """

    def __init__(self, min_freq=2, max_vocab_size=50000):
        self.min_freq = min_freq
        self.max_vocab_size = max_vocab_size
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.word_freq = Counter()

        # Special tokens
        self.special_tokens = ['<pad>', '<unk>', '<sos>', '<eos>']
        self._init_special_tokens()

    def _init_special_tokens(self):
        """Initialize special tokens."""
        for i, token in enumerate(self.special_tokens):
            self.word_to_idx[token] = i
            self.idx_to_word[i] = token

    def build_vocab(self, texts):
        """
        Build vocabulary from list of texts.

        Args:
            texts: List of Hebrew text strings
        """
        tokenizer = HebrewWordTokenizer()

        # Count word frequencies
        for text in texts:
            tokens = tokenizer.tokenize(text)
            self.word_freq.update(tokens)

        # Filter by minimum frequency and size
        filtered_words = [
            word for word, freq in self.word_freq.items()
            if freq >= self.min_freq
        ]

        # Sort by frequency (most common first)
        filtered_words.sort(key=lambda x: self.word_freq[x], reverse=True)

        # Limit vocabulary size
        if len(filtered_words) > self.max_vocab_size:
            filtered_words = filtered_words[:self.max_vocab_size]

        # Add to vocabulary
        for word in filtered_words:
            idx = len(self.word_to_idx)
            self.word_to_idx[word] = idx
            self.idx_to_word[idx] = word

    def __len__(self):
        return len(self.word_to_idx)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.word_to_idx.get(key, self.word_to_idx['<unk>'])
        elif isinstance(key, int):
            return self.idx_to_word.get(key, '<unk>')
        else:
            raise TypeError("Key must be string or int")

class HebrewCorrectionDataset:
    """
    Dataset for training Hebrew text correction model.

    Each sample contains original (potentially erroneous) text and corrected text.
    """

    def __init__(self, training_pairs, vocab=None, max_length=128):
        """
        Initialize dataset.

        Args:
            training_pairs: List of {'original': str, 'corrected': str} dicts
            vocab: HebrewWordVocabulary instance (optional)
            max_length: Maximum sequence length
        """
        self.training_pairs = training_pairs
        self.max_length = max_length
        self.tokenizer = HebrewWordTokenizer()

        # Build or use provided vocabulary
        if vocab is None:
            all_texts = [pair['original'] for pair in training_pairs] + \
                       [pair['corrected'] for pair in training_pairs]
            self.vocab = HebrewWordVocabulary()
            self.vocab.build_vocab(all_texts)
        else:
            self.vocab = vocab

    def __len__(self):
        return len(self.training_pairs)

    def __getitem__(self, idx):
        """Get training sample by index."""
        original_text = self.training_pairs[idx]['original']
        corrected_text = self.training_pairs[idx]['corrected']

        # Tokenize both texts
        orig_tokens = self.tokenizer.tokenize(original_text)
        corr_tokens = self.tokenizer.tokenize(corrected_text)

        # For training, we use the original (potentially erroneous) text as input
        # and the corrected text as the target for what the model should predict
        tokens = orig_tokens  # Use original text as input
        token_indices = [self.vocab[token] for token in tokens]

        # Convert corrected tokens to indices for training targets
        corr_token_indices = [self.vocab[token] for token in corr_tokens]
        if len(corr_token_indices) > self.max_length:
            corr_token_indices = corr_token_indices[:self.max_length]
        corrected_tokens = corr_token_indices + [self.vocab['<pad>']] * (self.max_length - len(corr_token_indices))

        # Create error indicators - mark positions where original differs from corrected
        error_mask = []
        for i in range(min(len(tokens), self.max_length)):
            if i < len(corr_tokens) and tokens[i] != corr_tokens[i]:
                error_mask.append(1)  # Error at this position
            else:
                error_mask.append(0)  # No error at this position
        error_mask += [0] * (self.max_length - len(error_mask))  # Pad with zeros

        # Pad sequences
        if len(token_indices) > self.max_length:
            token_indices = token_indices[:self.max_length]
            error_mask = error_mask[:self.max_length]

        padded_tokens = token_indices + [self.vocab['<pad>']] * (self.max_length - len(token_indices))
        padded_mask = error_mask + [0] * (self.max_length - len(error_mask))

        return {
            'input_tokens': padded_tokens,
            'error_mask': padded_mask,
            'corrected_tokens': corrected_tokens,
            'original_text': original_text,
            'corrected_text': corrected_text,
            'length': min(len(tokens), self.max_length)
        }

    def get_vocab_size(self):
        """Get vocabulary size."""
        return len(self.vocab)

def load_training_pairs_from_csv(csv_path):
    """
    Load training pairs from CSV file.

    Args:
        csv_path: Path to CSV with 'current_text' and 'corrected_text' columns

    Returns:
        list: List of training pair dictionaries
    """
    import csv

    training_pairs = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            original = row.get('current_text', '').strip()
            corrected = row.get('corrected_text', '').strip()

            if original and corrected:
                training_pairs.append({
                    'original': original,
                    'corrected': corrected
                })

    return training_pairs

def create_error_patterns_from_json(pattern_file):
    """
    Extract error patterns from pattern_analysis.json for training.

    Args:
        pattern_file: Path to pattern analysis JSON

    Returns:
        dict: Error pattern statistics
    """
    import json

    with open(pattern_file, 'r', encoding='utf-8') as f:
        patterns = json.load(f)

    return patterns.get('character_substitutions', {})