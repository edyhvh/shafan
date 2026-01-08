"""
Tanaj text extraction from Hebrew source data.

This package provides tools for converting Hebrew Tanaj (Old Testament)
source data to JSON format compatible with Shafan.

Usage:
    python -m scripts.tanaj --list                    # List available books
    python -m scripts.tanaj --book genesis --dry-run  # Process 5 chapters
    python -m scripts.tanaj --book genesis            # Process one book
    python -m scripts.tanaj genesis exodus            # Process multiple books
    python -m scripts.tanaj --all                     # Process all books
"""

from .converter import convert_book, get_available_books

__all__ = [
    'convert_book',
    'get_available_books',
]