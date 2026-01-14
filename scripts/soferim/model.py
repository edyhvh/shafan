#!/usr/bin/env python3
"""
PyTorch BiLSTM model for Hebrew text correction (Soferim).

Character-level sequence-to-sequence model with error detection and correction heads:
- Error Detection Head: Predicts probability of error for each word
- Correction Head: Suggests corrected words with confidence scores
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

class ErrorDetectionHead(nn.Module):
    """
    Head for detecting potential errors in text.

    Outputs probability that each word contains an error.
    """

    def __init__(self, hidden_dim, dropout=0.1):
        super().__init__()
        self.linear = nn.Linear(hidden_dim, 1)  # Single output for binary classification
        self.dropout = nn.Dropout(dropout)
        self.sigmoid = nn.Sigmoid()

    def forward(self, lstm_output):
        """
        Args:
            lstm_output: (batch_size, seq_len, hidden_dim)

        Returns:
            error_probs: (batch_size, seq_len) - probability of error for each position
        """
        x = self.dropout(lstm_output)
        logits = self.linear(x).squeeze(-1)  # (batch_size, seq_len)
        error_probs = self.sigmoid(logits)
        return error_probs

class CorrectionHead(nn.Module):
    """
    Head for suggesting corrections.

    For each position, outputs a distribution over possible corrections.
    Uses a simplified approach: predict corrections from a fixed vocabulary.
    """

    def __init__(self, hidden_dim, vocab_size, dropout=0.1):
        super().__init__()
        self.linear = nn.Linear(hidden_dim, vocab_size)
        self.dropout = nn.Dropout(dropout)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, lstm_output):
        """
        Args:
            lstm_output: (batch_size, seq_len, hidden_dim)

        Returns:
            correction_logits: (batch_size, seq_len, vocab_size)
        """
        x = self.dropout(lstm_output)
        correction_logits = self.linear(x)
        return correction_logits

    def get_correction_probs(self, lstm_output):
        """
        Get correction probabilities.

        Args:
            lstm_output: (batch_size, seq_len, hidden_dim)

        Returns:
            correction_probs: (batch_size, seq_len, vocab_size)
        """
        logits = self.forward(lstm_output)
        return self.softmax(logits)

class SoferimModel(nn.Module):
    """
    Complete Soferim model for Hebrew text correction.

    Combines BiLSTM encoder with error detection and correction heads.
    """

    def __init__(self, vocab_size, embedding_dim=256, hidden_dim=512, num_layers=3, dropout=0.2):
        """
        Initialize Soferim model.

        Args:
            vocab_size: Size of word vocabulary
            embedding_dim: Word embedding dimension
            hidden_dim: LSTM hidden dimension
            num_layers: Number of LSTM layers
            dropout: Dropout probability
        """
        super().__init__()

        self.vocab_size = vocab_size

        # Word embedding layer
        self.embedding = nn.Embedding(
            vocab_size,
            embedding_dim,
            padding_idx=0  # Assume <pad> is at index 0
        )

        # BiLSTM layers
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )

        # Output heads
        lstm_output_dim = hidden_dim * 2  # bidirectional
        self.error_detection_head = ErrorDetectionHead(lstm_output_dim, dropout)
        self.correction_head = CorrectionHead(lstm_output_dim, vocab_size, dropout)

        # Dropout
        self.dropout = nn.Dropout(dropout)

    def forward(self, input_tokens):
        """
        Forward pass through the model.

        Args:
            input_tokens: (batch_size, seq_len) - word indices (padded to same length)

        Returns:
            dict: {
                'error_probs': (batch_size, seq_len),
                'correction_logits': (batch_size, seq_len, vocab_size)
            }
        """
        # Embed words
        embedded = self.embedding(input_tokens)  # (batch_size, seq_len, embedding_dim)
        embedded = self.dropout(embedded)

        # For fixed-length sequences, we don't need packing
        # All sequences are padded to the same length
        lstm_output, _ = self.lstm(embedded)

        # Apply dropout to LSTM output
        lstm_output = self.dropout(lstm_output)

        # Get outputs from both heads
        error_probs = self.error_detection_head(lstm_output)
        correction_logits = self.correction_head(lstm_output)

        return {
            'error_probs': error_probs,
            'correction_logits': correction_logits
        }

    def compute_loss(self, outputs, targets, error_mask, vocab_size, use_focal_loss=True, focal_gamma=2.0, focal_alpha=0.75):
        """
        Compute training loss for Soferim model.

        Args:
            outputs: Model outputs dict
            targets: Dict with target tensors
            error_mask: (batch_size, seq_len) - 1 where errors should be corrected
            vocab_size: Vocabulary size
            use_focal_loss: Whether to use focal loss for error detection
            focal_gamma: Focusing parameter for focal loss (higher = focus more on hard examples)
            focal_alpha: Class weight for positive class (errors)

        Returns:
            dict: Loss components
        """
        error_probs = outputs['error_probs']  # (batch_size, seq_len)
        correction_logits = outputs['correction_logits']  # (batch_size, seq_len, vocab_size)

        # Error detection loss
        error_targets = error_mask.float()

        if use_focal_loss:
            # Focal Loss: FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
            # This down-weights easy examples and focuses on hard ones
            p_t = torch.where(error_targets == 1, error_probs, 1 - error_probs)
            alpha_t = torch.where(error_targets == 1, focal_alpha, 1 - focal_alpha)

            # Clamp to avoid log(0)
            p_t = torch.clamp(p_t, min=1e-8, max=1-1e-8)

            focal_weight = (1 - p_t) ** focal_gamma
            bce = -torch.log(p_t)
            error_detection_loss = (alpha_t * focal_weight * bce).mean()
        else:
            # Standard binary cross-entropy
            error_detection_loss = nn.functional.binary_cross_entropy(
                error_probs, error_targets, reduction='mean'
            )

        # Correction loss (cross-entropy)
        # Only compute loss for positions marked as errors
        correction_targets = targets.get('correction_targets', error_mask)  # Simplified
        correction_loss = nn.functional.cross_entropy(
            correction_logits.view(-1, vocab_size),
            correction_targets.view(-1),
            ignore_index=-100,  # Ignore padding
            reduction='mean'
        )

        # Combined loss with adjusted weights
        alpha = 0.4  # Weight for error detection
        beta = 0.6   # Weight for correction
        total_loss = alpha * error_detection_loss + beta * correction_loss

        return {
            'total_loss': total_loss,
            'error_detection_loss': error_detection_loss,
            'correction_loss': correction_loss
        }

    def save_model(self, path):
        """
        Save trained model to file.

        Args:
            path: Path to save model
        """
        from pathlib import Path

        # Ensure parent directory exists
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        torch.save({
            'model_state_dict': self.state_dict(),
            'vocab_size': self.vocab_size,
            'config': {
                'embedding_dim': self.embedding.embedding_dim,
                'hidden_dim': self.lstm.hidden_size,
                'num_layers': self.lstm.num_layers,
            }
        }, path)

    def predict_corrections(self, input_tokens, confidence_threshold=0.5, top_k=3):
        """
        Predict corrections for input text.

        Args:
            input_tokens: (batch_size, seq_len) - word indices (padded)
            confidence_threshold: Minimum error probability to suggest correction
            top_k: Number of top correction candidates to return

        Returns:
            list: List of correction suggestions per sequence
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(input_tokens)
            error_probs = outputs['error_probs']
            correction_logits = outputs['correction_logits']

            batch_size, seq_len = input_tokens.shape
            corrections = []

            for batch_idx in range(batch_size):
                sequence_corrections = []

                for pos in range(seq_len):
                    error_prob = error_probs[batch_idx, pos].item()
                    current_word_idx = input_tokens[batch_idx, pos].item()

                    # Skip if below confidence threshold or padding
                    if error_prob < confidence_threshold or current_word_idx == 0:  # <pad>
                        continue

                    # Get top-k correction candidates
                    pos_logits = correction_logits[batch_idx, pos]  # (vocab_size,)
                    top_probs, top_indices = torch.topk(
                        torch.softmax(pos_logits, dim=-1),
                        k=min(top_k + 1, self.vocab_size)  # +1 to exclude current word if needed
                    )

                    # Filter out the current word if it's in top predictions
                    candidates = []
                    for prob, idx in zip(top_probs, top_indices):
                        if idx.item() != current_word_idx:  # Don't suggest the same word
                            candidates.append({
                                'word_index': pos,
                                'suggested_word_idx': idx.item(),
                                'confidence': prob.item()
                            })
                            if len(candidates) >= top_k:
                                break

                    if candidates:
                        sequence_corrections.extend(candidates)

                corrections.append(sequence_corrections)

        return corrections

def create_model(vocab_size, embedding_dim=256, hidden_dim=512, num_layers=3, dropout=0.2):
    """
    Factory function to create Soferim model.

    Args:
        vocab_size: Size of word vocabulary
        embedding_dim: Word embedding dimension
        hidden_dim: LSTM hidden dimension
        num_layers: Number of LSTM layers
        dropout: Dropout probability

    Returns:
        SoferimModel: Configured model
    """
    return SoferimModel(vocab_size, embedding_dim, hidden_dim, num_layers, dropout)


def save_model(model, path):
    """
    Save trained model to file.

    Args:
        model: Trained SoferimModel
        path: Path to save model
    """
    torch.save({
        'model_state_dict': model.state_dict(),
        'vocab_size': model.vocab_size,
        'config': {
            'embedding_dim': model.embedding.embedding_dim,
            'hidden_dim': model.lstm.hidden_size,
            'num_layers': model.lstm.num_layers,
        }
    }, path)

def load_model(path, device='cpu'):
    """
    Load trained model from file.

    Args:
        path: Path to saved model
        device: Device to load model on

    Returns:
        SoferimModel: Loaded model
    """
    checkpoint = torch.load(path, map_location=device)

    # Recreate model with saved config
    config = checkpoint['config']
    model = SoferimModel(
        vocab_size=checkpoint['vocab_size'],
        embedding_dim=config['embedding_dim'],
        hidden_dim=config['hidden_dim'],
        num_layers=config['num_layers']
    )

    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()

    return model