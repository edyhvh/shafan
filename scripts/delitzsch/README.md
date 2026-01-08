# Delitzsch Hebrew New Testament Translator

This directory contains scripts to extract and process Franz Delitzsch's Hebrew New Testament translation from the [hebrew-bible.github.io](https://github.com/hebrew-bible/hebrew-bible.github.io) repository.

## What We Did

### Background
- **Franz Delitzsch** (1813-1890) created a Hebrew translation of the New Testament
- The translation is available in HTML format on GitHub
- We needed to extract this Hebrew text and convert it to JSON format

### Steps Completed

1. **Repository Access** - Cloned the hebrew-bible.github.io repository
2. **HTML Parsing** - Extracted Hebrew text from complex HTML table structures
3. **Text Cleaning** - Removed formatting issues and normalized Hebrew text
4. **JSON Conversion** - Converted to structured JSON format matching our project
5. **Book Filtering** - Focused only on New Testament books (excluded Old Testament/Tanaj)
6. **Merge Script** - Created tool to add Delitzsch text to existing Hutter translations

## File Structure

```
scripts/delitzsch/
├── __init__.py              # Package initialization
├── __main__.py              # Module entry point
├── cli.py                   # Command-line interface
├── constants.py             # Book mappings and configuration
├── downloader.py            # Repository cloning and file location
├── parser.py                # HTML parsing and text extraction
├── converter.py             # JSON conversion and output formatting
└── README.md               # This file
```

## Key Scripts

### Main CLI (`cli.py`)
```bash
# List all available books
python -m scripts.delitzsch --list

# Process all New Testament books
python -m scripts.delitzsch --all

# Process specific book
python -m scripts.delitzsch --book matthew

# Use existing repository files (faster)
python -m scripts.delitzsch --all --use-existing
```

### Merge Script (`scripts/merge_delitzsch.py`)
```bash
# Add Delitzsch text to existing Hutter files
python scripts/merge_delitzsch.py

# Test what would be merged
python scripts/merge_delitzsch.py --dry-run
```

## Data Output

### Individual Book Files
- Location: `data/delitzsch/`
- Format: `{book_name}.json`
- Example: `data/delitzsch/matthew.json`

### Merged Files
- Location: `output/` (existing Hutter files)
- Added field: `text_nikud_delitzsch`
- Preserves all original Hutter data

## JSON Structure

### Delitzsch Format
```json
{
  "book_name": "matthew",
  "author": "Franz Delitzsch",
  "publication_year": "1877",
  "chapters": [
    {
      "hebrew_letter": "א",
      "number": 1,
      "verses": [
        {
          "number": 1,
          "text_nikud": "בְּרֵאשִׁית הָיָה הַדָּבָר..."
        }
      ]
    }
  ]
}
```

### Merged Format (Hutter + Delitzsch)
```json
{
  "number": 1,
  "text_nikud": "פַּאוְלוֹס שְׁלִיחַ...",           // Hutter text
  "source_files": ["000002.png"],                     // Hutter metadata
  "visual_uncertainty": [],                           // Hutter metadata
  "text_nikud_delitzsch": "פּוֹלוֹס שְׁלִיחַ..."     // Delitzsch text
}
```

## Challenges & Solutions

### 1. HTML Structure Issues
**Problem**: `john.html` had 4 columns instead of 3
**Solution**: Made parser flexible to handle different table structures

### 2. Chapter Detection
**Problem**: All content parsed as single chapter starting at #2
**Solution**: Parse `<h2>` elements with chapter anchors

### 3. Text Formatting
**Problem**: Hebrew text had newlines, extra spaces, and markers
**Solution**: Created `_clean_hebrew_text()` function for normalization

### 4. Repository Access
**Problem**: Git cloning failed due to sandbox restrictions
**Solution**: Added `--use-existing` option for local file processing

### 5. Book Name Mapping
**Problem**: HTML filenames used different naming (e.g., `1corinthians.html`)
**Solution**: Created `HTML_FILENAME_MAPPING` dictionary

## New Testament Books Available

| Book | Chapters | Status |
|------|----------|--------|
| Matthew | 28 | ✅ |
| Mark | 16 | ✅ |
| Luke | 24 | ✅ |
| John | 21 | ✅ |
| Acts | 28 | ✅ |
| Romans | 16 | ✅ |
| 1 Corinthians | 16 | ✅ |
| 2 Corinthians | 13 | ✅ |
| Galatians | 6 | ✅ |
| Ephesians | 6 | ✅ |
| Philippians | 4 | ✅ |
| Colossians | 4 | ✅ |
| 1 Thessalonians | 5 | ✅ |
| 2 Thessalonians | 3 | ✅ |
| 1 Timothy | 6 | ✅ |
| 2 Timothy | 4 | ✅ |
| Titus | 3 | ✅ |
| Philemon | 1 | ✅ |
| Hebrews | 13 | ✅ |
| James | 5 | ✅ |
| 1 Peter | 5 | ✅ |
| 2 Peter | 3 | ✅ |
| 1 John | 5 | ✅ |
| 2 John | 1 | ✅ |
| 3 John | 1 | ✅ |
| Jude | 1 | ✅ |
| Revelation | 22 | ✅ |

## Usage Workflow

### First Time Setup
```bash
# Clone repository (may require permissions)
python -m scripts.delitzsch --all

# Or use existing files if already downloaded
python -m scripts.delitzsch --all --use-existing
```

### Adding to Hutter Files
```bash
# Merge Delitzsch text into existing output files
python scripts/merge_delitzsch.py

# Verify merge worked
head -30 output/matthew.json | grep text_nikud
```

### Verification
```bash
# Check Delitzsch files were created
ls -la data/delitzsch/

# Check merge added new field
grep -c "text_nikud_delitzsch" output/*.json
```

## Notes

- Only New Testament books are processed (27 total)
- Old Testament books from the repository are ignored
- Some verses may have empty `text_nikud_delitzsch` if missing in Delitzsch
- Hebrew text includes proper vowel points (nikud)
- All original Hutter data is preserved during merge

## Dependencies

- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML parser
- `requests` - HTTP downloads (optional)

Install with:
```bash
pip install beautifulsoup4 lxml requests
```

## Success Metrics

- ✅ 27/27 New Testament books extracted
- ✅ All chapters start from 1 (not 2)
- ✅ Clean Hebrew text formatting
- ✅ Proper verse numbering
- ✅ Successful merge with Hutter translations
- ✅ No data loss or corruption