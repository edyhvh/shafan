"""
Hebrew text transcription using Claude Vision API.

This package provides tools for transcribing Hebrew Bible images
using Anthropic's Claude Vision API.

Usage:
    python -m scripts.text --list                    # List available books
    python -m scripts.text --book matthew --dry-run  # Process 5 images
    python -m scripts.text --book matthew            # Process one book
    python -m scripts.text matthew mark luke         # Process multiple books
    python -m scripts.text --all                     # Process all books
    python -m scripts.text --book matthew --resume   # Resume from checkpoint
"""

from .api import ClaudeClient
from .checkpoint import CheckpointManager
from .prompt import load_yaml, build_prompt, get_yaml_version, calculate_yaml_hash
from .validate import (
    parse_json_response,
    validate_chapter_object,
    validate_verse_object,
    validate_hebrew_text,
    validate_verse_sequence,
    validate_chapter_sequence
)
from .consolidate import consolidate_book
from .books import get_book_info, get_chapter_context, validate_chapter_number
from .config import AVAILABLE_BOOKS

__all__ = [
    # API
    'ClaudeClient',
    # Checkpoint
    'CheckpointManager',
    # Prompt
    'load_yaml',
    'build_prompt',
    'get_yaml_version',
    'calculate_yaml_hash',
    # Validation
    'parse_json_response',
    'validate_chapter_object',
    'validate_verse_object',
    'validate_hebrew_text',
    'validate_verse_sequence',
    'validate_chapter_sequence',
    # Consolidation
    'consolidate_book',
    # Books
    'get_book_info',
    'get_chapter_context',
    'validate_chapter_number',
    'AVAILABLE_BOOKS',
]

