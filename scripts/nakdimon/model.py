#!/usr/bin/env python3
"""
PyTorch BiLSTM model for Hebrew diacritization.

Character-level sequence-to-sequence model with 3 output heads:
- Vowels (12 classes)
- Dagesh (2 classes: none/dagesh)
- Shin dots (3 classes: none/shin/sin)
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
# Import our modules
import hebrew

class HebrewDiacritizer(nn.Module):
    """
    BiLSTM model for Hebrew diacritization.

    Takes Hebrew text without nikud and predicts nikud marks for each character.
    """

    def __init__(self, embedding_dim=256, hidden_dim=512, num_layers=3, dropout=0.2):
        super().__init__()

        # Get vocabulary sizes
        vocab_sizes = hebrew.get_vocab_sizes()
        self.input_vocab_size = vocab_sizes['input_vocab_size']
        self.vowel_vocab_size = vocab_sizes['vowel_vocab_size']
        self.dagesh_vocab_size = vocab_sizes['dagesh_vocab_size']
        self.shin_vocab_size = vocab_sizes['shin_vocab_size']

        # Character embedding layer (increased capacity)
        self.embedding = nn.Embedding(
            self.input_vocab_size,
            embedding_dim,
            padding_idx=self.input_vocab_size - 2  # <pad> token
        )

        # BiLSTM layers (increased capacity)
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )

        # Output heads for different nikud types
        lstm_output_dim = hidden_dim * 2  # bidirectional

        # Add intermediate layers for better capacity
        self.vowel_hidden = nn.Linear(lstm_output_dim, hidden_dim // 2)
        self.dagesh_hidden = nn.Linear(lstm_output_dim, hidden_dim // 4)
        self.shin_hidden = nn.Linear(lstm_output_dim, hidden_dim // 4)

        self.vowel_head = nn.Linear(hidden_dim // 2, self.vowel_vocab_size)
        self.dagesh_head = nn.Linear(hidden_dim // 4, self.dagesh_vocab_size)
        self.shin_head = nn.Linear(hidden_dim // 4, self.shin_vocab_size)

        # Dropout (increased)
        self.dropout = nn.Dropout(dropout)

        # Activation functions
        self.relu = nn.ReLU()

    def forward(self, x, lengths=None):
        """
        Forward pass.

        Args:
            x: Input tensor of shape (batch_size, seq_len)
            lengths: Original lengths for packed sequences (optional)

        Returns:
            tuple: (vowel_logits, dagesh_logits, shin_logits)
                   Each of shape (batch_size, seq_len, vocab_size)
        """
        # Embed characters
        embedded = self.embedding(x)  # (batch_size, seq_len, embedding_dim)
        embedded = self.dropout(embedded)

        # Pack sequences if lengths provided (for variable-length inputs)
        if lengths is not None:
            packed_embedded = pack_padded_sequence(
                embedded, lengths, batch_first=True, enforce_sorted=False
            )
            packed_output, _ = self.lstm(packed_embedded)
            lstm_output, _ = pad_packed_sequence(packed_output, batch_first=True)
        else:
            lstm_output, _ = self.lstm(embedded)

        # Apply dropout to LSTM output
        lstm_output = self.dropout(lstm_output)

        # Generate predictions for each output head with intermediate layers
        vowel_hidden = self.relu(self.vowel_hidden(lstm_output))
        dagesh_hidden = self.relu(self.dagesh_hidden(lstm_output))
        shin_hidden = self.relu(self.shin_hidden(lstm_output))

        vowel_hidden = self.dropout(vowel_hidden)
        dagesh_hidden = self.dropout(dagesh_hidden)
        shin_hidden = self.dropout(shin_hidden)

        vowel_logits = self.vowel_head(vowel_hidden)
        dagesh_logits = self.dagesh_head(dagesh_hidden)
        shin_logits = self.shin_head(shin_hidden)

        return vowel_logits, dagesh_logits, shin_logits

    def predict(self, x, lengths=None):
        """
        Make predictions (argmax for each output).

        Args:
            x: Input tensor of shape (batch_size, seq_len)
            lengths: Original lengths (optional)

        Returns:
            tuple: (vowel_preds, dagesh_preds, shin_preds)
                   Each of shape (batch_size, seq_len)
        """
        self.eval()
        with torch.no_grad():
            vowel_logits, dagesh_logits, shin_logits = self.forward(x, lengths)

            vowel_preds = torch.argmax(vowel_logits, dim=-1)
            dagesh_preds = torch.argmax(dagesh_logits, dim=-1)
            shin_preds = torch.argmax(shin_logits, dim=-1)

        return vowel_preds, dagesh_preds, shin_preds

def create_model(embedding_dim=256, hidden_dim=512, num_layers=3, dropout=0.2):
    """
    Factory function to create the model with increased capacity.

    Args:
        embedding_dim: Character embedding dimension
        hidden_dim: LSTM hidden dimension
        num_layers: Number of LSTM layers
        dropout: Dropout probability

    Returns:
        HebrewDiacritizer: Configured model
    """
    return HebrewDiacritizer(embedding_dim, hidden_dim, num_layers, dropout)

def compute_class_weights(train_loader, device='cpu'):
    """
    Compute class weights for imbalanced classes in the training data.

    Args:
        train_loader: Training DataLoader
        device: Device to run on

    Returns:
        tuple: (vowel_weights, dagesh_weights, shin_weights) as tensors
    """
    import torch

    # Count occurrences of each class
    vowel_counts = torch.zeros(12)  # 12 vowel classes including <none>
    dagesh_counts = torch.zeros(2)  # 2 dagesh classes
    shin_counts = torch.zeros(3)    # 3 shin classes

    total_samples = 0

    for batch in train_loader:
        vowel_targets, dagesh_targets, shin_targets = batch['targets']

        # Count valid (non-padding) targets
        valid_mask = (vowel_targets != -100)
        vowel_counts += torch.bincount(vowel_targets[valid_mask].flatten(), minlength=12)
        dagesh_counts += torch.bincount(dagesh_targets[valid_mask].flatten(), minlength=2)
        shin_counts += torch.bincount(shin_targets[valid_mask].flatten(), minlength=3)

        total_samples += valid_mask.sum().item()

    # Compute weights as inverse frequency
    vowel_weights = total_samples / (vowel_counts + 1e-6)  # Add small epsilon to avoid division by zero
    dagesh_weights = total_samples / (dagesh_counts + 1e-6)
    shin_weights = total_samples / (shin_counts + 1e-6)

    # Normalize weights
    vowel_weights = vowel_weights / vowel_weights.sum() * len(vowel_weights)
    dagesh_weights = dagesh_weights / dagesh_weights.sum() * len(dagesh_weights)
    shin_weights = shin_weights / shin_weights.sum() * len(shin_weights)

    return vowel_weights.to(device), dagesh_weights.to(device), shin_weights.to(device)

def load_model(path, device='cpu'):
    """
    Load trained model from file.

    Args:
        path: Path to saved model
        device: Device to load model on

    Returns:
        HebrewDiacritizer: Loaded model
    """
    # Get vocab sizes to create model with correct dimensions
    vocab_sizes = hebrew.get_vocab_sizes()

    # Create model with same architecture as saved
    model = HebrewDiacritizer()
    model.load_state_dict(torch.load(path, map_location=device))
    model.to(device)
    model.eval()

    return model

def save_model(model, path):
    """
    Save trained model to file.

    Args:
        model: Trained HebrewDiacritizer model
        path: Path to save model
    """
    torch.save(model.state_dict(), path)