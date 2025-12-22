"""
Hebrew text processing module for shafan OCR project.

This module provides tools for transcribing Hebrew biblical manuscript images
using Google Gemini 1.5 Pro Vision API, specifically for the Hutter Hebrew New Testament (1599-1602).

Modules:
    - checkpoint: Checkpoint management for transcription state
    - prompt: Prompt building from YAML configuration
    - client: Gemini API client with retry logic
    - validator: Validation functions for schema and content
    - consolidator: Consolidate verses into final JSON per book
    - main: Main CLI script for transcription
"""

from .checkpoint import CheckpointManager
from .prompt import load_yaml, build_prompt, get_yaml_version, calculate_yaml_hash
from .validator import (
    validate_schema,
    validate_hebrew_text,
    validate_verse_sequence,
    validate_chapter_sequence,
    detect_gaps,
    parse_json_response,
    validate_verse_object,
    validate_chapter_object,
)
from .consolidator import (
    load_verses_from_checkpoint,
    group_by_chapter,
    build_book_json,
    validate_complete_sequence,
    save_book_json,
    consolidate_book,
)

# Optional import for GeminiClient (requires google-generativeai)
try:
    from .client import GeminiClient
except ImportError:
    GeminiClient = None  # type: ignore

__all__ = [
    "CheckpointManager",
    "load_yaml",
    "build_prompt",
    "get_yaml_version",
    "calculate_yaml_hash",
    "GeminiClient",
    "validate_schema",
    "validate_hebrew_text",
    "validate_verse_sequence",
    "validate_chapter_sequence",
    "detect_gaps",
    "parse_json_response",
    "validate_verse_object",
    "validate_chapter_object",
    "load_verses_from_checkpoint",
    "group_by_chapter",
    "build_book_json",
    "validate_complete_sequence",
    "save_book_json",
    "consolidate_book",
]


