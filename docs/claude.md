# Claude Vision Transcription

Transcribe Hutter's Hebrew Bible images using Anthropic Claude Vision API.

## Quick Start

### 1. Set API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Get your API key from [Anthropic Console](https://console.anthropic.com/settings/keys).

### 2. Usage

```bash
# List available books
python -m scripts.text --list

# Process 5 images (dry-run)
python -m scripts.text --book matthew --dry-run

# Process one book
python -m scripts.text --book matthew

# Process multiple books
python -m scripts.text matthew mark luke

# Process all books
python -m scripts.text --all

# Resume from checkpoint
python -m scripts.text --book matthew --resume

# Reprocess failed images
python -m scripts.text --book acts --reprocess-failed

# Reprocess specific images
python -m scripts.text --book acts --reprocess-images 000086.png,000088.png

# Use a different model
python -m scripts.text --book acts --model opus-4.5
```

## Package Structure

```
scripts/text/
├── __init__.py      # Package exports
├── __main__.py      # Entry point (python -m scripts.text)
├── cli.py           # CLI argument parsing
├── api.py           # Claude API client
├── processor.py     # Core processing logic
├── books.py         # Book structure data
├── checkpoint.py    # Checkpoint management
├── consolidate.py   # Verse consolidation
├── prompt.py        # Prompt building from YAML
├── validate.py      # Validation functions
└── config.py        # Constants and configuration
```

## Modules

### `api.py` - Claude API Client

**Class**: `ClaudeClient`
- `transcribe_image(image_path, prompt)` - Send image to Claude, get transcription
- Automatic image compression for files > 5MB
- Exponential backoff retry (up to 5 retries)

**Available Models**:
| Alias | Model | Description |
|-------|-------|-------------|
| `sonnet-4.5`, `sonnet` | claude-sonnet-4-5 | Default, best speed/quality |
| `opus-4.5`, `opus` | claude-opus-4-5 | Most capable |
| `opus-4` | claude-opus-4 | Very capable |
| `sonnet-4` | claude-sonnet-4 | Fallback |

### `books.py` - Book Structure

**Data**: `BOOK_STRUCTURE` - Chapter/verse counts for each book

**Functions**:
- `get_book_info(book_name)` - Get total chapters, verses
- `get_chapter_context(book_name)` - Generate prompt context
- `validate_chapter_number(book_name, chapter_num)` - Validate chapter
- `fix_chapter_assignment(book_name, chapters_data)` - Fix assignments
- `infer_chapter_from_sequence(...)` - Sequential chapter inference
- `diagnose_checkpoint(book_name, checkpoint_data)` - Detect errors

### `processor.py` - Core Processing

**Functions**:
- `process_image(...)` - Process single image
- `process_book(...)` - Process single book
- `process_books(...)` - Process multiple books
- `get_image_list(book_name, images_dir)` - Get images with special filtering

### `cli.py` - Command Line Interface

**Arguments**:
| Argument | Description |
|----------|-------------|
| `books` | Book names to process |
| `--book`, `-b` | Single book name |
| `--all` | Process all books |
| `--list` | List available books |
| `--dry-run` | Process only 5 images |
| `--resume` | Resume from checkpoint |
| `--reprocess-failed` | Reprocess failed images |
| `--reprocess-images` | Specific images to reprocess |
| `--parallel` | Parallel requests (default: 1) |
| `--model`, `-m` | Claude model |
| `--verbose`, `-v` | Debug logging |
| `--images-dir` | Images directory |
| `--output-dir` | Output directory |
| `--yaml-path` | YAML config path |
| `--checkpoint-dir` | Checkpoint directory |

## Key Features

### Sequential Chapter Inference

Tracks verse progression across images to detect and correct chapter misassignments:

```python
context = {'last_chapter': 5, 'last_verse': 23}
# If next image reports chapter 22 but we expect 5-6,
# the system applies corrections based on verse numbers
```

### Book Structure Validation

Single-chapter books (jude, philemon, john2, john3) automatically merge all verses to chapter 1.

### Checkpoint Diagnostics

After processing, detects:
- Duplicate verse entries
- Invalid chapter numbers
- Unexpected chapter jumps

## Processing Flow

1. Load YAML configuration
2. Validate API key
3. For each book:
   - Initialize checkpoint
   - Get image list (with special filtering)
   - For each image:
     - Add sequential context to prompt
     - Call Claude API
     - Validate and correct response
     - Update checkpoint
   - Consolidate verses to JSON
   - Run diagnostics

## Checkpoint Structure

```json
{
  "book_name": "matthew",
  "yaml_version": "2025-12-22-Shafan-v9",
  "yaml_hash": "sha256...",
  "last_updated": "2025-01-15T10:30:00Z",
  "total_images": 151,
  "processed_images": 45,
  "total_cost_usd": 0.45,
  "images": {
    "000002.png": {
      "status": "completed",
      "cost_usd": 0.01,
      "verses": {
        "1_1": {
          "status": "completed",
          "chapter": 1,
          "verse": 1,
          "text_nikud": "בְּרֵאשִׁית..."
        }
      }
    }
  }
}
```

## Output Structure

```
output/
├── <book_name>.json              # Final JSON per book
└── .checkpoints/
    └── <book_name>_state.json    # Processing state
```

## Cost Estimation

Claude Sonnet 4.5 pricing:
- Input: $3.00 / 1M tokens
- Output: $15.00 / 1M tokens
- Average per image: ~$0.01

## Special Cases

- **colossians**: Excludes pages 000026, 000028, 000030 (belong to laodikim)
- **john1**: Custom filtering logic for page selection
- **Other books**: Process only even-numbered images

## Dependencies

Required:
- `anthropic>=0.25.0`
- `jsonschema>=4.0.0`
- `Pillow>=9.0.0`
- `PyYAML`
- `python-dotenv`
- `tqdm`
