#!/usr/bin/env python3
"""
Training script for PyTorch Hebrew diacritizer.

Trains the model on Moriah's 40 vocalized samples to learn her nikud style.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from pathlib import Path
import argparse
import logging
from tqdm import tqdm

# Import our modules
import model
import dataset

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_model(model, train_loader, num_epochs=100, learning_rate=1e-3, device='cpu',
                val_loader=None, early_stopping_patience=10, class_weights=None):
    """
    Train the Hebrew diacritizer model with optional validation and early stopping.

    Args:
        model: HebrewDiacritizer model
        train_loader: DataLoader with training data
        num_epochs: Number of training epochs
        learning_rate: Learning rate for optimizer
        device: Device to train on
        val_loader: Optional validation DataLoader
        early_stopping_patience: Patience for early stopping (0 to disable)
        class_weights: Optional tuple of (vowel_weights, dagesh_weights, shin_weights)

    Returns:
        dict: Training history
    """
    model.to(device)
    model.train()

    # Loss functions for each output head (ignore padding tokens)
    if class_weights is not None:
        vowel_weights, dagesh_weights, shin_weights = class_weights
        vowel_criterion = nn.CrossEntropyLoss(weight=vowel_weights, ignore_index=-100)
        dagesh_criterion = nn.CrossEntropyLoss(weight=dagesh_weights, ignore_index=-100)
        shin_criterion = nn.CrossEntropyLoss(weight=shin_weights, ignore_index=-100)
    else:
        vowel_criterion = nn.CrossEntropyLoss(ignore_index=-100)
        dagesh_criterion = nn.CrossEntropyLoss(ignore_index=-100)
        shin_criterion = nn.CrossEntropyLoss(ignore_index=-100)

    # Optimizer
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=10
    )

    history = {'loss': [], 'vowel_loss': [], 'dagesh_loss': [], 'shin_loss': []}
    if val_loader is not None:
        history['val_loss'] = []

    best_val_loss = float('inf')
    best_model_state = None
    patience_counter = 0

    logger.info(f"Starting training for {num_epochs} epochs on {len(train_loader.dataset)} samples")
    if val_loader:
        logger.info(f"Validation set: {len(val_loader.dataset)} samples")

    for epoch in range(num_epochs):
        epoch_loss = 0.0
        epoch_vowel_loss = 0.0
        epoch_dagesh_loss = 0.0
        epoch_shin_loss = 0.0

        # Training loop
        with tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}') as pbar:
            for batch in pbar:
                input_seq = batch['input'].to(device)
                vowel_targets, dagesh_targets, shin_targets = batch['targets']
                vowel_targets = vowel_targets.to(device)
                dagesh_targets = dagesh_targets.to(device)
                shin_targets = shin_targets.to(device)
                lengths = batch['lengths']

                # Zero gradients
                optimizer.zero_grad()

                # Forward pass
                vowel_logits, dagesh_logits, shin_logits = model(input_seq, lengths)

                # Compute losses
                vowel_loss = vowel_criterion(
                    vowel_logits.view(-1, vowel_logits.size(-1)),
                    vowel_targets.view(-1)
                )
                dagesh_loss = dagesh_criterion(
                    dagesh_logits.view(-1, dagesh_logits.size(-1)),
                    dagesh_targets.view(-1)
                )
                shin_loss = shin_criterion(
                    shin_logits.view(-1, shin_logits.size(-1)),
                    shin_targets.view(-1)
                )

                # Total loss (weighted equally for now)
                total_loss = vowel_loss + dagesh_loss + shin_loss

                # Backward pass
                total_loss.backward()

                # Clip gradients to prevent exploding gradients
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

                # Update parameters
                optimizer.step()

                # Accumulate losses
                epoch_loss += total_loss.item()
                epoch_vowel_loss += vowel_loss.item()
                epoch_dagesh_loss += dagesh_loss.item()
                epoch_shin_loss += shin_loss.item()

                # Update progress bar
                pbar.set_postfix({
                    'loss': f'{total_loss.item():.4f}',
                    'vowel': f'{vowel_loss.item():.4f}',
                    'dagesh': f'{dagesh_loss.item():.4f}',
                    'shin': f'{shin_loss.item():.4f}'
                })

        # Average losses for the epoch
        num_batches = len(train_loader)
        avg_loss = epoch_loss / num_batches
        avg_vowel_loss = epoch_vowel_loss / num_batches
        avg_dagesh_loss = epoch_dagesh_loss / num_batches
        avg_shin_loss = epoch_shin_loss / num_batches

        # Store in history
        history['loss'].append(avg_loss)
        history['vowel_loss'].append(avg_vowel_loss)
        history['dagesh_loss'].append(avg_dagesh_loss)
        history['shin_loss'].append(avg_shin_loss)

        # Validation
        if val_loader is not None:
            val_metrics = validate_model(model, val_loader, device)
            val_loss = val_metrics['loss']
            history['val_loss'].append(val_loss)

            logger.info('.4f')
            logger.info('.4f')

            # Update learning rate scheduler
            scheduler.step(val_loss)

            # Early stopping check
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_model_state = model.state_dict().copy()
                patience_counter = 0
            else:
                patience_counter += 1

            if early_stopping_patience > 0 and patience_counter >= early_stopping_patience:
                logger.info(f"Early stopping triggered after {epoch+1} epochs")
                break
        else:
            scheduler.step(avg_loss)
            logger.info('.4f')
            logger.info('.4f')

    # Restore best model if using validation
    if val_loader is not None and best_model_state is not None:
        model.load_state_dict(best_model_state)
        logger.info("Restored best model from validation")

    return history

def validate_model(model, val_loader, device='cpu'):
    """
    Validate the model on validation data.

    Args:
        model: HebrewDiacritizer model
        val_loader: Validation DataLoader
        device: Device to run validation on

    Returns:
        dict: Validation metrics
    """
    model.to(device)
    model.eval()

    # Loss functions for each output head
    vowel_criterion = nn.CrossEntropyLoss(ignore_index=-100)
    dagesh_criterion = nn.CrossEntropyLoss(ignore_index=-100)
    shin_criterion = nn.CrossEntropyLoss(ignore_index=-100)

    total_loss = 0.0
    total_vowel_loss = 0.0
    total_dagesh_loss = 0.0
    total_shin_loss = 0.0
    num_batches = 0

    with torch.no_grad():
        for batch in val_loader:
            input_seq = batch['input'].to(device)
            vowel_targets, dagesh_targets, shin_targets = batch['targets']
            vowel_targets = vowel_targets.to(device)
            dagesh_targets = dagesh_targets.to(device)
            shin_targets = shin_targets.to(device)
            lengths = batch['lengths']

            # Forward pass
            vowel_logits, dagesh_logits, shin_logits = model(input_seq, lengths)

            # Compute losses
            vowel_loss = vowel_criterion(
                vowel_logits.view(-1, vowel_logits.size(-1)),
                vowel_targets.view(-1)
            )
            dagesh_loss = dagesh_criterion(
                dagesh_logits.view(-1, dagesh_logits.size(-1)),
                dagesh_targets.view(-1)
            )
            shin_loss = shin_criterion(
                shin_logits.view(-1, shin_logits.size(-1)),
                shin_targets.view(-1)
            )

            total_loss += (vowel_loss + dagesh_loss + shin_loss).item()
            total_vowel_loss += vowel_loss.item()
            total_dagesh_loss += dagesh_loss.item()
            total_shin_loss += shin_loss.item()
            num_batches += 1

    avg_loss = total_loss / num_batches
    avg_vowel_loss = total_vowel_loss / num_batches
    avg_dagesh_loss = total_dagesh_loss / num_batches
    avg_shin_loss = total_shin_loss / num_batches

    return {
        'loss': avg_loss,
        'vowel_loss': avg_vowel_loss,
        'dagesh_loss': avg_dagesh_loss,
        'shin_loss': avg_shin_loss
    }

def train_two_stage(model, delitzsch_loader, moriah_loader, device='cpu'):
    """
    Train model in two stages: pretraining on Delitzsch, fine-tuning on Moriah.

    Args:
        model: HebrewDiacritizer model
        delitzsch_loader: tuple of (train_loader, val_loader) for Delitzsch data
        moriah_loader: tuple of (train_loader, val_loader) for Moriah data
        device: Device to train on

    Returns:
        dict: Training history
    """
    delitzsch_train, delitzsch_val = delitzsch_loader
    moriah_train, moriah_val = moriah_loader

    history = {
        'stage1': {'loss': [], 'vowel_loss': [], 'dagesh_loss': [], 'shin_loss': [], 'val_loss': []},
        'stage2': {'loss': [], 'vowel_loss': [], 'dagesh_loss': [], 'shin_loss': [], 'val_loss': []}
    }

    # Stage 1: Pretraining on Delitzsch corpus
    logger.info("=== STAGE 1: Pretraining on Delitzsch Corpus ===")
    stage1_history = train_model(
        model=model,
        train_loader=delitzsch_train,
        num_epochs=100,
        learning_rate=1e-3,
        device=device,
        val_loader=delitzsch_val
    )
    history['stage1'] = stage1_history

    # Stage 2: Fine-tuning on Moriah corrections
    logger.info("=== STAGE 2: Fine-tuning on Moriah Corrections ===")

    # Optionally freeze embeddings for fine-tuning
    # model.embedding.requires_grad_(False)

    stage2_history = train_model(
        model=model,
        train_loader=moriah_train,
        num_epochs=50,
        learning_rate=1e-4,
        device=device,
        val_loader=moriah_val
    )
    history['stage2'] = stage2_history

    return history

def main():
    parser = argparse.ArgumentParser(description='Train Hebrew Diacritizer on Moriah data')
    parser.add_argument('--epochs', type=int, default=100, help='Number of training epochs')
    parser.add_argument('--lr', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--embedding-dim', type=int, default=64, help='Character embedding dimension')
    parser.add_argument('--hidden-dim', type=int, default=128, help='LSTM hidden dimension')
    parser.add_argument('--num-layers', type=int, default=1, help='Number of LSTM layers')
    parser.add_argument('--dropout', type=float, default=0.1, help='Dropout probability')
    parser.add_argument('--max-length', type=int, default=256, help='Maximum sequence length')
    parser.add_argument('--output-dir', type=str, default='data/nakdimon/models', help='Output directory')
    parser.add_argument('--model-name', type=str, default='moriah_pytorch.pt', help='Model filename')
    parser.add_argument('--device', type=str, default='auto', help='Device (cpu/cuda/auto)')

    args = parser.parse_args()

    # Determine device
    if args.device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        device = args.device

    logger.info(f"Using device: {device}")

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / args.model_name

    # Load training data (limit Delitzsch data for faster training)
    logger.info("Loading Delitzsch training data...")
    delitzsch_loaders = dataset.load_delitzsch_data(
        validation_split=0.1,
        augment_data=False,  # Skip augmentation for speed
        max_samples=2000     # Limit to 2000 samples
    )

    logger.info("Loading Moriah training data...")
    moriah_loaders = dataset.load_moriah_data(validation_split=0.1, batch_size=args.batch_size)

    # Create model
    logger.info("Creating model...")
    the_model = model.create_model(
        embedding_dim=args.embedding_dim,
        hidden_dim=args.hidden_dim,
        num_layers=args.num_layers,
        dropout=args.dropout
    )

    # Train model in two stages
    logger.info("=== STAGE 1: Pretraining on Delitzsch Corpus ===")
    delitzsch_train, delitzsch_val = delitzsch_loaders

    # Compute class weights from Delitzsch training data
    logger.info("Computing class weights from Delitzsch training data...")
    class_weights = model.compute_class_weights(delitzsch_train, device)

    stage1_history = train_model(
        the_model,
        delitzsch_train,
        num_epochs=5,        # Reduced from 100 for speed
        learning_rate=1e-3,
        device=device,
        val_loader=delitzsch_val,
        early_stopping_patience=3,  # Reduced patience
        class_weights=class_weights
    )

    logger.info("=== STAGE 2: Fine-tuning on Moriah Corrections ===")
    moriah_train, moriah_val = moriah_loaders
    stage2_history = train_model(
        the_model,
        moriah_train,
        num_epochs=3,        # Reduced from 50 for speed
        learning_rate=1e-4,
        device=device,
        val_loader=moriah_val,
        early_stopping_patience=3,  # Reduced patience
        class_weights=None  # Use uniform weights for fine-tuning
    )

    history = {
        'stage1': stage1_history,
        'stage2': stage2_history
    }

    # Save model
    logger.info(f"Saving model to {model_path}")
    model.save_model(the_model, model_path)

    logger.info("Training completed successfully!")
    logger.info(f"Model saved to: {model_path}")
    logger.info(f"Stage 1 final loss: {history['stage1']['loss'][-1]:.4f}")
    logger.info(f"Stage 2 final loss: {history['stage2']['loss'][-1]:.4f}")

if __name__ == '__main__':
    main()