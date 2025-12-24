# Tools Directory

This directory contains scripts for analyzing and fixing issues in the OCR output files.

## Identified Issues

### Issue #1: Incorrect Chapter Numbers from Gemini (Critical)

**Status**: Identified, needs fix
**Affected Books**: `acts` (possibly others)
**Date Identified**: 2025-12-23

#### Problem Description

Gemini is returning **incorrect chapter numbers** for verses. When processing each page, it appears to be labeling verses based on what's visible on that page rather than maintaining the correct chapter numbering from the book.

**Example**:
- Page `000002.png` correctly has `1_1` (Chapter 1, Verse 1): "ת שֵׁפֶר הַרִאשׁוֹן..."
- Page `000048.png` incorrectly has `1_1` (should be ~Chapter 5): "וְאִישׁ אֶחָד וּשְׁמוֹ חֲנַנְיָהּ..."
- Page `000068.png` incorrectly has `1_1` (should be ~Chapter 7): "וַיֹּאמֶר כֹּהֵן גָּדוֹל..."

This results in:
- **65 verse keys appearing in multiple images** for the book of Acts
- **42 problematic verses** in the final output
- Verses with **15-22 source files** (should be 1-2)
- Text length of **1800-2700+ characters** per verse (should be ~150-300)

#### Root Cause

Gemini is not correctly identifying chapter numbers from the page images. It seems to restart chapter numbering based on what it sees on each page rather than understanding the overall book structure.

#### Impact

The consolidator (`scripts/hebrew_text/consolidator.py`) merges all verses with the same `chapter_verse` key. When multiple pages incorrectly report the same key (e.g., `1_1`), all their text gets concatenated, resulting in:
- Garbled, extremely long verse text
- Many source files listed per verse
- Invalid biblical text

#### Root Cause in Code

The issue was in `scripts/hebrew_text/prompt.py` lines 228-245, which explicitly told Gemini:
```
"- Start verse numbering from 1 for each new image, regardless of previous requests."
"- If this appears to be a continuation page, still number verses starting from 1."
```

This caused Gemini to always report Chapter 1, Verse 1, 2, 3... for every page.

#### Solution Implemented

1. **Prompt Fix** (DONE): Modified `scripts/hebrew_text/prompt.py` to:
   - Remove the "start from 1" instructions
   - Add clear Hebrew chapter marker identification (א=1, ב=2, ג=3...)
   - Instruct Gemini to report ACTUAL verse numbers, not restart from 1
   - Add guidance for pages without visible chapter markers

2. **Fix Tool**: Created `tools/fix_chapter_context.py` to:
   - Analyze checkpoints and identify problematic images
   - Reset specific images for reprocessing
   - Generate mapping files for manual chapter correction

---

### Issue #2: Low Verse Count / Missing Verses

**Status**: Identified, same fix as Issue #1
**Affected Books**: `acts` (possibly others)
**Date Identified**: 2025-12-23

#### Problem Description

Some images returned only 1-4 verses when they should have 5-7. This is caused by:

1. **Same root cause as Issue #1**: The "start from 1" instruction caused Gemini to stop early
2. **Blank/faded pages**: Some pages (like `000338.png`) are blank reversos that shouldn't be processed

#### Detection

Run `analyze_low_verse_images.py` to find these:

```bash
python tools/analyze_low_verse_images.py output/.checkpoints/acts_state.json --check-images
```

This will:
- Show verse count distribution
- Identify images with low contrast (blank pages)
- List images that need reprocessing

#### Solution

Use the same fix as Issue #1, with the `--reset-low-verse` flag:

```bash
python tools/fix_chapter_context.py output/.checkpoints/acts_state.json \
    --reset-all-problematic --reset-low-verse 4
```

---

## Available Scripts

### analyze_verses.py

Analyze output JSON files to find problematic verses.

```bash
# Basic analysis
python tools/analyze_verses.py output/acts.json

# With custom thresholds
python tools/analyze_verses.py output/acts.json --max-sources 3 --max-length 500

# Verbose output with text previews
python tools/analyze_verses.py output/acts.json --verbose

# Save list of verses needing fixes
python tools/analyze_verses.py output/acts.json --output-fix-list output/acts_fix_list.json
```

**Detects**:
- `too_many_sources`: Verses with more than expected source files
- `text_too_long`: Verses with abnormally long text
- `empty_text`: Verses with no text content

### analyze_checkpoint.py

Analyze checkpoint files to find the root cause of issues.

```bash
# Find duplicate verse keys across images
python tools/analyze_checkpoint.py output/.checkpoints/acts_state.json --find-duplicates

# Show verse distribution across images
python tools/analyze_checkpoint.py output/.checkpoints/acts_state.json --show-distribution

# Save fix recommendations
python tools/analyze_checkpoint.py output/.checkpoints/acts_state.json --output-recommendations output/acts_recommendations.json
```

**Detects**:
- Verse keys that appear in multiple images (indicates wrong chapter/verse numbers)
- Distribution of verses per image
- Chapter coverage per image

### fix_chapter_context.py

Fix chapter context issues by reprocessing specific images.

```bash
# Analyze problematic images
python tools/fix_chapter_context.py output/.checkpoints/acts_state.json --analyze

# Reset ALL problematic images (duplicate verse keys)
python tools/fix_chapter_context.py output/.checkpoints/acts_state.json --reset-all-problematic

# Reset images with low verse count (≤4 verses)
python tools/fix_chapter_context.py output/.checkpoints/acts_state.json --reset-low-verse 4

# Reset BOTH problematic AND low-verse images
python tools/fix_chapter_context.py output/.checkpoints/acts_state.json --reset-all-problematic --reset-low-verse 4

# Preview what would be reset (dry run)
python tools/fix_chapter_context.py output/.checkpoints/acts_state.json --reset-all-problematic --dry-run

# Reset specific images
python tools/fix_chapter_context.py output/.checkpoints/acts_state.json --reset-images 000048.png 000068.png

# After resetting, rerun the main script to reprocess
python scripts/hebrew_text/main.py --book acts --resume
```

### analyze_low_verse_images.py

Analyze images that returned few verses to identify quality issues.

```bash
# Analyze verse count distribution
python tools/analyze_low_verse_images.py output/.checkpoints/acts_state.json

# Check image quality (brightness, contrast) to detect blank pages
python tools/analyze_low_verse_images.py output/.checkpoints/acts_state.json --check-images

# Custom threshold for "low verse count"
python tools/analyze_low_verse_images.py output/.checkpoints/acts_state.json --threshold 3 --check-images
```

**Detects**:
- Blank/faded pages (low contrast < 20)
- Images with fewer verses than expected (transcription issues)

---

## Analysis Results for Acts

**Date**: 2025-12-23

### Summary

| Metric | Value |
|--------|-------|
| Total chapters in output | 15 (should be 28) |
| Total verses in output | 150 |
| Problematic verses | 42 (28%) |
| Duplicate verse keys | 65 |
| Max source files per verse | 22 |
| Max text length | ~2700 chars |

### Top Duplicate Verse Keys

| Verse Key | Occurrences | Expected |
|-----------|-------------|----------|
| 1_8 | 22 images | 1-2 |
| 1_9 | 22 images | 1-2 |
| 1_7 | 21 images | 1-2 |
| 1_10 | 21 images | 1-2 |
| 1_5 | 20 images | 1-2 |
| 1_6 | 20 images | 1-2 |

This clearly shows that Gemini is labeling verses from different chapters as "Chapter 1" consistently.

---

## Next Steps

1. [x] Review the YAML prompt for chapter identification instructions
2. [x] Add Hebrew chapter marker detection to the prompt
3. [x] Create a reprocessing script for affected images (`fix_chapter_context.py`)
4. [ ] Reprocess the affected images for Acts
5. [ ] Test with other books to determine scope of issue
6. [ ] Consider adding page sequence validation in the pipeline (post-processing)

## How to Fix Acts

```bash
# 1. See what's problematic (dry run)
python tools/fix_chapter_context.py output/.checkpoints/acts_state.json \
    --reset-all-problematic --reset-low-verse 4 --dry-run

# 2. Reset ALL problematic images (removes them from checkpoint)
python tools/fix_chapter_context.py output/.checkpoints/acts_state.json \
    --reset-all-problematic --reset-low-verse 4

# 3. Reprocess with the fixed prompt
python scripts/hebrew_text/main.py --book acts --resume

# 4. Verify the fix
python tools/analyze_verses.py output/acts.json
```

### Current Status for Acts

| Issue | Count | Description |
|-------|-------|-------------|
| Duplicate verse keys | 112 images | Wrong chapter numbers reported |
| Low verse count (≤4) | 18 images | Missing verses (4 are unique, 14 overlap with duplicates) |
| Blank pages | 1 image | 000338.png (contrast=11.56) |
| **Total to reprocess** | **116 images** | After removing overlaps |

