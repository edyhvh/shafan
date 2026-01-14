#!/usr/bin/env python3
"""
Training script for PyTorch Hebrew text correction model (Soferim).

Trains the model in two stages:
1. Pretraining on Delitzsch corpus (language modeling)
2. Fine-tuning on Hutter manual corrections
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

def train_epoch(model, train_loader, optimizer, device, vocab_size):
    """
    Train model for one epoch.

    Args:
        model: SoferimModel
        train_loader: Training DataLoader
        optimizer: Optimizer
        device: Device to train on
        vocab_size: Vocabulary size

    Returns:
        dict: Training metrics for the epoch
    """
    model.train()

    total_loss = 0.0
    total_error_detection_loss = 0.0
    total_correction_loss = 0.0
    num_batches = 0

    with tqdm(train_loader, desc='Training') as pbar:
        for batch in pbar:
            input_tokens = batch['input_tokens'].to(device)
            error_mask = batch['error_mask'].to(device)
            lengths = batch['lengths']

            # Zero gradients
            optimizer.zero_grad()

            # Forward pass
            outputs = model(input_tokens)

            # Use corrected tokens as targets for training
            targets = {
                'correction_targets': batch['corrected_tokens']
            }

            # Compute loss
            losses = model.compute_loss(outputs, targets, error_mask, vocab_size)

            # Backward pass
            losses['total_loss'].backward()

            # Clip gradients to prevent exploding gradients
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            # Update parameters
            optimizer.step()

            # Accumulate losses
            total_loss += losses['total_loss'].item()
            total_error_detection_loss += losses['error_detection_loss'].item()
            total_correction_loss += losses['correction_loss'].item()
            num_batches += 1

            # Update progress bar
            pbar.set_postfix({
                'loss': '.4f',
                'err_det': '.4f',
                'corr': '.4f'
            })

    # Average losses
    avg_loss = total_loss / num_batches
    avg_error_detection_loss = total_error_detection_loss / num_batches
    avg_correction_loss = total_correction_loss / num_batches

    return {
        'loss': avg_loss,
        'error_detection_loss': avg_error_detection_loss,
        'correction_loss': avg_correction_loss
    }

def validate_epoch(model, val_loader, device, vocab_size):
    """
    Validate model for one epoch.

    Args:
        model: SoferimModel
        val_loader: Validation DataLoader
        device: Device to validate on
        vocab_size: Vocabulary size

    Returns:
        dict: Validation metrics
    """
    model.eval()

    total_loss = 0.0
    total_error_detection_loss = 0.0
    total_correction_loss = 0.0
    num_batches = 0

    with torch.no_grad():
        for batch in val_loader:
            input_tokens = batch['input_tokens'].to(device)
            error_mask = batch['error_mask'].to(device)
            lengths = batch['lengths']

            # Forward pass
            outputs = model(input_tokens)

            # Create targets
            targets = {'correction_targets': input_tokens}

            # Compute loss
            losses = model.compute_loss(outputs, targets, error_mask, vocab_size)

            # Accumulate losses
            total_loss += losses['total_loss'].item()
            total_error_detection_loss += losses['error_detection_loss'].item()
            total_correction_loss += losses['correction_loss'].item()
            num_batches += 1

    # Average losses
    avg_loss = total_loss / num_batches
    avg_error_detection_loss = total_error_detection_loss / num_batches
    avg_correction_loss = total_correction_loss / num_batches

    return {
        'loss': avg_loss,
        'error_detection_loss': avg_error_detection_loss,
        'correction_loss': avg_correction_loss
    }

def train_model(model, train_loader, val_loader, vocab_size, num_epochs=50,
                learning_rate=1e-3, device='cpu', patience=10, model_save_path=None,
                resume_from=None, checkpoint_freq=5, checkpoint_prefix=''):
    """
    Train the Soferim model with optional validation and early stopping.

    Args:
        model: SoferimModel
        train_loader: Training DataLoader
        val_loader: Validation DataLoader (optional)
        vocab_size: Vocabulary size
        num_epochs: Number of training epochs
        learning_rate: Learning rate
        device: Device to train on
        patience: Early stopping patience
        model_save_path: Path to save best model

    Returns:
        dict: Training history
    """
    model.to(device)

    # Initialize optimizer and scheduler (required before loading state dicts)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5
    )

    # Resume from checkpoint if provided
    start_epoch = 0
    best_val_loss = float('inf')
    best_model_state = None
    patience_counter = 0

    if resume_from and Path(resume_from).exists():
        logger.info(f"Resuming from checkpoint: {resume_from}")
        checkpoint = torch.load(resume_from, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        start_epoch = checkpoint['epoch'] + 1
        best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        patience_counter = checkpoint.get('patience_counter', 0)

        # Load history if available
        if 'history' in checkpoint:
            history = checkpoint['history']
        else:
            history = {
                'train_loss': [], 'train_error_detection_loss': [], 'train_correction_loss': [],
                'val_loss': [], 'val_error_detection_loss': [], 'val_correction_loss': []
            }

        logger.info(f"Resumed from epoch {start_epoch}")
    else:
        # Training history
        history = {
            'train_loss': [], 'train_error_detection_loss': [], 'train_correction_loss': [],
            'val_loss': [], 'val_error_detection_loss': [], 'val_correction_loss': []
        }

    logger.info(f"Starting training for {num_epochs} epochs (starting from epoch {start_epoch})")

    for epoch in range(start_epoch, num_epochs):
        # Train epoch
        train_metrics = train_epoch(model, train_loader, optimizer, device, vocab_size)

        # Store training metrics
        history['train_loss'].append(train_metrics['loss'])
        history['train_error_detection_loss'].append(train_metrics['error_detection_loss'])
        history['train_correction_loss'].append(train_metrics['correction_loss'])

        # Validation
        if val_loader is not None:
            val_metrics = validate_epoch(model, val_loader, device, vocab_size)

            # Store validation metrics
            history['val_loss'].append(val_metrics['loss'])
            history['val_error_detection_loss'].append(val_metrics['error_detection_loss'])
            history['val_correction_loss'].append(val_metrics['correction_loss'])

            # Update learning rate scheduler
            scheduler.step(val_metrics['loss'])

            logger.info(
                f"Epoch {epoch+1}/{num_epochs} - "
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Val Loss: {val_metrics['loss']:.4f}"
            )

            # Early stopping check
            if val_metrics['loss'] < best_val_loss:
                best_val_loss = val_metrics['loss']
                best_model_state = model.state_dict().copy()
                patience_counter = 0

                # Save best model
                if model_save_path:
                    model.save_model(model_save_path)
                    logger.info(f"Saved best model to {model_save_path}")
            else:
                patience_counter += 1

            if patience > 0 and patience_counter >= patience:
                logger.info(f"Early stopping triggered after {epoch+1} epochs")
                break

        # Save checkpoint every checkpoint_freq epochs
        if (epoch + 1) % checkpoint_freq == 0 and model_save_path:
            prefix = f"{checkpoint_prefix}_" if checkpoint_prefix else ""
            checkpoint_path = Path(model_save_path).parent / f"{prefix}checkpoint_epoch_{epoch+1}.pt"
            # Ensure directory exists
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'best_val_loss': best_val_loss,
                'patience_counter': patience_counter,
                'history': history
            }
            torch.save(checkpoint, checkpoint_path)
            logger.info(f"Saved checkpoint to {checkpoint_path}")
        else:
            scheduler.step(train_metrics['loss'])
            logger.info(f"Epoch {epoch+1}/{num_epochs} - Train Loss: {train_metrics['loss']:.4f}")

    # Restore best model if validation was used
    if val_loader is not None and best_model_state is not None:
        model.load_state_dict(best_model_state)
        logger.info("Restored best model from validation")

    return history

def train_two_stage(project_root=None, device='cpu', resume_stage1_from=None, resume_stage2_from=None, checkpoint_freq=5):
    """
    Train model in two stages: pretraining on Delitzsch, fine-tuning on Hutter.

    Args:
        project_root: Path to project root
        device: Device to train on

    Returns:
        SoferimModel: Trained model
    """
    if project_root is None:
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent

    # Stage 1: Pretraining on Delitzsch corpus
    logger.info("=== STAGE 1: Pretraining on Delitzsch Corpus ===")

    delitzsch_train, delitzsch_val, delitzsch_vocab_size = dataset.load_delitzsch_only(
        project_root=project_root,
        validation_split=0.1,
        batch_size=32,
        max_samples=10000  # Increased for richer Hebrew language understanding
    )

    # Create model for pretraining
    soferim_model = model.create_model(
        vocab_size=delitzsch_vocab_size,
        embedding_dim=256,  # Increased for better capacity
        hidden_dim=512,
        num_layers=3,
        dropout=0.1
    )

    # Path for stage 1 model
    stage1_model_path = project_root / 'models' / 'soferim_stage1_pretrained.pt'

    # Check if stage 1 is already completed
    if stage1_model_path.exists() and resume_stage1_from is None:
        logger.info(f"Stage 1 model already exists at {stage1_model_path}. Skipping stage 1.")
        logger.info("To retrain stage 1, delete the model file or use --resume-stage1-from to continue training.")
        # Load the pretrained model
        soferim_model = model.load_model(stage1_model_path, device)
        stage1_history = {'train_loss': [0]}  # Dummy history
    else:
        # Train on Delitzsch
        stage1_history = train_model(
            model=soferim_model,
            train_loader=delitzsch_train,
            val_loader=delitzsch_val,
            vocab_size=delitzsch_vocab_size,
            num_epochs=10,  # Reduced for demo
            learning_rate=1e-3,
            device=device,
            patience=3,
            resume_from=resume_stage1_from,
            checkpoint_freq=checkpoint_freq,
            model_save_path=stage1_model_path,
            checkpoint_prefix='stage1'
        )

        logger.info(f"Stage 1 completed. Final loss: {stage1_history['train_loss'][-1]:.4f}")

        # Save stage 1 model
        soferim_model.save_model(stage1_model_path)
        logger.info(f"Stage 1 model saved to {stage1_model_path}")

    # Stage 2: Fine-tuning on Hutter corrections
    logger.info("=== STAGE 2: Fine-tuning on Hutter Corrections ===")

    hutter_train, hutter_val, hutter_vocab_size = dataset.load_soferim_dataset(
        project_root=project_root,
        validation_split=0.2,
        batch_size=16,  # Smaller batch size for better generalization
        max_length=32,  # Shorter sequences for faster training
        error_weight=15.0  # Increased to oversample error examples more
    )

    # Note: In practice, we'd need to handle vocabulary differences between stages
    # For now, we'll use the Hutter vocabulary
    if hutter_vocab_size != delitzsch_vocab_size:
        logger.warning("Vocabulary size changed between stages. Recreating model for fine-tuning.")

        soferim_model = model.create_model(
            vocab_size=hutter_vocab_size,
            embedding_dim=256,  # Increased for better capacity
            hidden_dim=512,
            num_layers=3,
            dropout=0.3  # Higher dropout to prevent overfitting
        )

    # Fine-tune on Hutter data
    stage2_model_path = project_root / 'models' / 'soferim_stage2_finetuned.pt'

    stage2_history = train_model(
        model=soferim_model,
        train_loader=hutter_train,
        val_loader=hutter_val,
        vocab_size=hutter_vocab_size,
        num_epochs=30,  # More epochs for better convergence
        learning_rate=1e-4,  # Lower learning rate for stable fine-tuning
        device=device,
        patience=5,  # Early stopping with some patience
        model_save_path=stage2_model_path,
        resume_from=resume_stage2_from,
        checkpoint_freq=5,  # Save checkpoints every 5 epochs
        checkpoint_prefix='stage2'
    )

    logger.info(f"Stage 2 completed. Final loss: {stage2_history['train_loss'][-1]:.4f}")

    return soferim_model, {'stage1': stage1_history, 'stage2': stage2_history}

def main():
    parser = argparse.ArgumentParser(description='Train Soferim Hebrew Text Correction Model')
    parser.add_argument('--epochs', type=int, default=50, help='Number of training epochs')
    parser.add_argument('--lr', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--embedding-dim', type=int, default=256, help='Word embedding dimension')
    parser.add_argument('--hidden-dim', type=int, default=512, help='LSTM hidden dimension')
    parser.add_argument('--num-layers', type=int, default=3, help='Number of LSTM layers')
    parser.add_argument('--dropout', type=float, default=0.2, help='Dropout probability')
    parser.add_argument('--max-length', type=int, default=128, help='Maximum sequence length')
    parser.add_argument('--output-dir', type=str, default='models', help='Output directory')
    parser.add_argument('--model-name', type=str, default='soferim.pt', help='Model filename')
    parser.add_argument('--device', type=str, default='auto', help='Device (cpu/cuda/auto)')
    parser.add_argument('--two-stage', action='store_true', help='Use two-stage training')
    parser.add_argument('--resume-from', type=str, help='Resume training from checkpoint path (single-stage training)')
    parser.add_argument('--resume-stage1-from', type=str, help='Resume stage 1 from checkpoint (two-stage training)')
    parser.add_argument('--resume-stage2-from', type=str, help='Resume stage 2 from checkpoint (two-stage training)')
    parser.add_argument('--checkpoint-freq', type=int, default=5, help='Save checkpoint every N epochs')

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

    # Also ensure the models subdirectory exists for two-stage training
    models_dir = Path(args.output_dir) / 'models'
    models_dir.mkdir(parents=True, exist_ok=True)

    if args.two_stage:
        # Two-stage training
        trained_model, history = train_two_stage(
            device=device,
            resume_stage1_from=args.resume_stage1_from,
            resume_stage2_from=args.resume_stage2_from,
            checkpoint_freq=args.checkpoint_freq
        )

        # Save final model
        trained_model.save_model(model_path)
        logger.info(f"Final model saved to {model_path}")

    else:
        # Single-stage training on Hutter data
        logger.info("Loading Hutter training data...")

        train_loader, val_loader, vocab_size = dataset.load_soferim_dataset(
            validation_split=0.1,
            batch_size=args.batch_size
        )

        logger.info("Creating model...")
        soferim_model = model.create_model(
            vocab_size=vocab_size,
            embedding_dim=args.embedding_dim,
            hidden_dim=args.hidden_dim,
            num_layers=args.num_layers,
            dropout=args.dropout
        )

        # Train model
        history = train_model(
            model=soferim_model,
            train_loader=train_loader,
            val_loader=val_loader,
            vocab_size=vocab_size,
            num_epochs=args.epochs,
            learning_rate=args.lr,
            device=device,
            patience=10,
            model_save_path=model_path,
            resume_from=args.resume_from,
            checkpoint_freq=args.checkpoint_freq
        )

    logger.info("Training completed successfully!")
    logger.info(f"Model saved to: {model_path}")

if __name__ == '__main__':
    main()