"""
Constants and book mappings for the Delitzsch Hebrew New Testament extractor.
"""

import os
from pathlib import Path

# Repository information
REPOSITORY_URL = "https://github.com/hebrew-bible/hebrew-bible.github.io.git"
REPOSITORY_NAME = "hebrew-bible.github.io"

# Default paths
DEFAULT_CACHE_DIR = Path("/tmp/shafan_cache")
DEFAULT_REPO_DIR = DEFAULT_CACHE_DIR / REPOSITORY_NAME
DEFAULT_OUTPUT_DIR = "data/delitzsch"

# New Testament books available in Delitzsch translation
# Based on the Hutter Polyglot Bible book list
NEW_TESTAMENT_BOOKS = {
    "matthew": "Matthew",
    "mark": "Mark",
    "luke": "Luke",
    "john": "John",
    "acts": "Acts",
    "romans": "Romans",
    "corinthians1": "1 Corinthians",
    "corinthians2": "2 Corinthians",
    "galatians": "Galatians",
    "ephesians": "Ephesians",
    "philippians": "Philippians",
    "colossians": "Colossians",
    "thessalonians1": "1 Thessalonians",
    "thessalonians2": "2 Thessalonians",
    "timothy1": "1 Timothy",
    "timothy2": "2 Timothy",
    "titus": "Titus",
    "philemon": "Philemon",
    "hebrews": "Hebrews",
    "james": "James",
    "peter1": "1 Peter",
    "peter2": "2 Peter",
    "john1": "1 John",
    "john2": "2 John",
    "john3": "3 John",
    "jude": "Jude",
    "revelation": "Revelation",
}

# Mapping from internal book names to HTML filenames in the repository
HTML_FILENAME_MAPPING = {
    "matthew": "matthew",
    "mark": "mark",
    "luke": "luke",
    "john": "john",
    "acts": "acts",
    "romans": "romans",
    "corinthians1": "1corinthians",
    "corinthians2": "2corinthians",
    "galatians": "galatians",
    "ephesians": "ephesians",
    "philippians": "philippians",
    "colossians": "colossians",
    "thessalonians1": "1thessalonians",
    "thessalonians2": "2thessalonians",
    "timothy1": "1timothy",
    "timothy2": "2timothy",
    "titus": "titus",
    "philemon": "philemon",
    "hebrews": "hebrews",
    "james": "jacob",  # Note: HTML file is jacob.html but represents James
    "peter1": "1peter",
    "peter2": "2peter",
    "john1": "1john",
    "john2": "2john",
    "john3": "3john",
    "jude": "jude",
    "revelation": "revelation",
}

# HTML directory structure patterns
# The repository likely has HTML files in html/ subdirectory
HTML_DIR = "html"

# Common HTML file patterns for Delitzsch translation
# These may need adjustment after exploring the repository structure
HTML_PATTERNS = [
    "*.html",
    "**/*.html"
]

# Author and publication information
AUTHOR_NAME = "Franz Delitzsch"
PUBLICATION_YEAR = "1877"

# HTML parsing constants
# These may need adjustment based on actual HTML structure
DEFAULT_ENCODING = "utf-8"

# Timeout for repository operations (in seconds)
REPO_TIMEOUT = 300  # 5 minutes