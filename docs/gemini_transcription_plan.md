# Gemini 1.5 Pro Transcription Implementation Plan

Implementation guide for transcribing Hutter's Bible images using Google Gemini 1.5 Pro Vision API.

## Quick Start

### 1. Set API Key

```bash
# Option 1: Environment variable
export GEMINI_API_KEY="your-api-key-here"

# Option 2: Create .env file (recommended)
echo "GEMINI_API_KEY=your-api-key-here" >> .env
```

**To get API key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and set it as shown above

### 2. Test Run

```bash
# Process 5 images from one book (dry-run)
python scripts/hebrew_text/main.py --book matthew --dry-run

# Process one book
python scripts/hebrew_text/main.py --book matthew

# Process all books
python scripts/hebrew_text/main.py --all
```

## Implementation Requirements

### Script Structure

All scripts should be created in `scripts/hebrew_text/` following the pattern of `scripts/hebrew_images/main.py`. Use concise, standard names:

#### 1. `checkpoint.py`
**Purpose**: Manage JSON checkpoint files for transcription state

**Class**: `CheckpointManager`
- `load()` - Load checkpoint state from JSON file
- `save()` - Save checkpoint state atomically
- `update_image_status()` - Update status for specific image
- `is_image_processed()` - Check if image already processed
- `get_processed_verses()` - Get all completed verses
- `set_yaml_info()` - Store YAML version and hash
- `calculate_yaml_hash()` - Calculate SHA256 hash of YAML content

**Checkpoint Structure**: See "Checkpoint Structure" section below

#### 2. `prompt.py`
**Purpose**: Build prompts from `docs/hebrew_vision_context.yaml`

**Functions**:
- `load_yaml(path)` - Load YAML file using PyYAML, return dict
- `build_prompt(yaml_data)` - Construct full prompt from YAML rules
- `get_yaml_version(yaml_data)` - Extract version from YAML metadata
- `calculate_yaml_hash(yaml_content)` - Generate SHA256 hash for versioning

**Prompt Components**:
- Base: `vision_prompt_template.task` from YAML
- Add: All rules from `paleographic_priority`, `advanced_vocalization`, `ornamented_initials`, `auxiliary_hebrew_text_to_ignore`, `normalization_rules`
- Include: Special instruction about first verse of first chapter (ornamented letter)
- Output: Request strict JSON matching `output_specification` schema

#### 3. `client.py`
**Purpose**: Gemini API client with retry logic and error handling

**Class**: `GeminiClient`
- `__init__(api_key)` - Initialize with API key validation
- `transcribe_image(image_path, prompt)` - Send image to Gemini API, return response
- `_retry_with_backoff(func, max_retries)` - Exponential backoff retry logic
- `_handle_error(error)` - Handle different error types (429, 500, etc.)
- `estimate_cost()` - Calculate cost per image (~$0.00125)

**Error Handling**:
- 429 (Rate Limit): Wait for `Retry-After` header or exponential backoff
- 500/502/503: Exponential backoff (1s, 2s, 4s, 8s, 16s, max 60s)
- 400: Log error, don't retry, continue
- 401: Stop execution (API key error)
- Max 5 retries per image

#### 4. `validator.py`
**Purpose**: Validate schema and content

**Functions**:
- `validate_schema(data, schema)` - Validate JSON against YAML schema using `jsonschema`
- `validate_hebrew_text(text)` - Verify Hebrew characters (Unicode U+0590-U+05FF)
- `validate_verse_sequence(verses)` - Check verse numbers are sequential
- `validate_chapter_sequence(chapters)` - Check chapter numbers are sequential
- `detect_gaps(verses)` - Find missing verses in sequence

**Validation Rules**:
- Required fields: `text_nikud`, `source_files`, `number`
- Correct types: string, int, array
- `text_nikud` not empty and valid Hebrew
- `source_files` non-empty array

#### 5. `consolidator.py`
**Purpose**: Consolidate verses into final JSON per book

**Functions**:
- `load_verses_from_checkpoint(checkpoint)` - Load all processed verses
- `group_by_chapter(verses)` - Group verses by chapter number
- `build_book_json(book_name, chapters)` - Build final JSON following YAML schema
- `validate_complete_sequence(chapters)` - Verify no gaps before finalizing
- `save_book_json(book_json, output_path)` - Save final JSON to `output/<book_name>.json`

**Output Format**: Follows `output_specification` from YAML:
```json
{
  "book_name": "matthew",
  "author": "Elias Hutter",
  "publication_year": "1599–1602",
  "chapters": [
    {
      "hebrew_letter": "א",
      "number": 1,
      "verses": [...]
    }
  ]
}
```

#### 6. `main.py`
**Purpose**: Main CLI script (entry point)

**Functions**:
- `main()` - CLI argument parsing and orchestration
- `process_book(book_name, checkpoint, client, prompt_template, dry_run)` - Process single book
- `process_books(book_names, ...)` - Process multiple books
- `list_books()` - List available books
- `validate_books(book_names)` - Validate book names

**CLI Arguments**:
- `books` - Book names or "all"
- `--list` - List available books
- `--dry-run` - Process only 5 images per book
- `--resume` - Resume from checkpoint
- `--reprocess-failed` - Reprocess failed images
- `--verbose` - Enable debug logging

**Flow**:
1. Load YAML and calculate hash
2. Validate API key
3. For each book:
   - Load checkpoint
   - Get image list
   - For each image (skip if completed):
     - Load image
     - Build prompt
     - Call API with retry
     - Validate response
     - Update checkpoint
   - Consolidate verses
   - Validate sequence
   - Save final JSON

### Key Points

- **Input**: Images from `data/images/hebrew_images/<book_name>/`
- **Rules**: Load and use `docs/hebrew_vision_context.yaml`
- **Output**: JSON files in `output/<book_name>.json` following YAML schema
- **Checkpoints**: JSON files in `output/.checkpoints/<book_name>_state.json`
- **Verses**: Marked with Arabic numerals (1, 2, 3...) in right margin (RTL)
- **Chapters**: Marked with large centered Hebrew letters
- **Special**: First verse of first chapter uses ornamented letter (no number)

### Checkpoint Structure

```json
{
  "book_name": "matthew",
  "yaml_version": "2025-12-22-Shafan-v8-Platinum",
  "yaml_hash": "sha256_hash",
  "last_updated": "2025-01-15T10:30:00Z",
  "total_images": 151,
  "processed_images": 45,
  "total_cost_usd": 0.056,
  "images": {
    "000002.png": {
      "status": "completed",
      "processed_at": "2025-01-15T10:30:00Z",
      "cost_usd": 0.00125,
      "verses": {
        "1_1": {
          "status": "completed",
          "chapter": 1,
          "verse": 1,
          "text_nikud": "בְּרֵאשִׁית...",
          "source_files": ["000002.png"],
          "visual_uncertainty": []
        }
      }
    }
  }
}
```

### Prompt Construction (in `prompt_builder.py`)

Build prompt from `docs/hebrew_vision_context.yaml`:

1. **Load YAML**: Use `PyYAML` to load `docs/hebrew_vision_context.yaml`
2. **Base Template**: Start with `vision_prompt_template.task` from YAML
3. **Add Rules**: Append all rules from YAML sections:
   - `paleographic_priority.rule` and `paleographic_priority.description`
   - `advanced_vocalization.hataf_vowels.rule`
   - `advanced_vocalization.vav_distinction.rule`
   - `advanced_vocalization.dagesh_verification.rule` and `.warning`
   - `advanced_vocalization.composite_marks.rule`
   - `ornamented_initials.rule`
   - `auxiliary_hebrew_text_to_ignore.root_markers.rule`
   - `normalization_rules.makaf.rule`
   - `normalization_rules.sof_pasuq.rule`
   - `normalization_rules.parentheses.rule`
4. **Special Instructions**:
   - First verse of first chapter uses ornamented letter (no number marker)
   - Verses marked with Arabic numerals in right margin (RTL)
   - Chapters marked with large centered Hebrew letters
5. **Output Format**: Request strict JSON matching `output_specification` schema
6. **Role**: Use `vision_prompt_template.role` from YAML

### API Client Requirements

- Use `google-generativeai` library
- Model: `gemini-1.5-pro`
- Retry logic: Exponential backoff for 429, 500, 502, 503 (max 5 retries)
- Error handling: Log errors, save to checkpoint, continue processing
- Cost tracking: ~$0.00125 per image

### Validation

- Validate JSON structure against YAML schema using `jsonschema`
- Verify Hebrew characters (Unicode U+0590-U+05FF)
- Check verse sequence continuity
- Export 5% random sample for human review

### Output Structure

```
output/
├── <book_name>.json              # Final JSON per book
├── .checkpoints/
│   └── <book_name>_state.json    # Processing state
├── validation_samples/
│   └── <book_name>_sample.json   # 5% sample for review
├── errors/
│   └── <book_name>_errors.json   # Error log
└── logs/
    └── <book_name>.log           # Processing log
```

### Dependencies

Add to `requirements.txt`:
- `google-generativeai>=0.3.0`
- `jsonschema>=4.0.0`

Already included: `PyYAML`, `python-dotenv`, `tqdm`, `json`, `hashlib`

## CLI Interface

Follow pattern from `scripts/hebrew_images/main.py`:

```bash
# List books
python scripts/hebrew_text/main.py --list

# Dry-run (5 images)
python scripts/hebrew_text/main.py --book matthew --dry-run

# Process one book
python scripts/hebrew_text/main.py --book matthew

# Process multiple books
python scripts/hebrew_text/main.py matthew mark luke

# Process all
python scripts/hebrew_text/main.py --all

# Resume from checkpoint
python scripts/hebrew_text/main.py --book matthew --resume

# Reprocess failed
python scripts/hebrew_text/main.py --book matthew --reprocess-failed
```

## Special Cases

- `colossians`: Exclude pages 000026, 000028, 000030 (go to `laodikim`)
- `john1`: Apply special filtering logic from `scripts/hebrew_images/extractor.py`

## Notes

- Save checkpoint after each image (atomicity)
- Process images in numerical order
- Consolidate verses by chapter before finalizing book JSON
- Validate complete sequence before marking book as completed
