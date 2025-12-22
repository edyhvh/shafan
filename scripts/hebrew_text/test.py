#!/usr/bin/env python3
"""Test script to verify implementation without API calls."""

import sys
from pathlib import Path

# Import modules directly to avoid __init__.py importing client
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Check for yaml before importing anything else
try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install PyYAML")
    sys.exit(1)

from scripts.hebrew_text.checkpoint import CheckpointManager
from scripts.hebrew_text.prompt import load_yaml, build_prompt, get_yaml_version, calculate_yaml_hash
from scripts.hebrew_text.validator import (
    validate_hebrew_text,
    validate_verse_object,
    validate_chapter_object,
    parse_json_response
)
from scripts.hebrew_text.consolidator import (
    group_by_chapter,
    build_book_json
)

def test_checkpoint():
    """Test checkpoint functionality."""
    print("Testing CheckpointManager...")
    checkpoint_path = Path("/tmp/test_checkpoint.json")
    if checkpoint_path.exists():
        checkpoint_path.unlink()

    manager = CheckpointManager(checkpoint_path)
    manager.initialize("test_book", 10, "v1.0", "abc123")
    manager.update_image_status("000002.png", "completed", cost_usd=0.00125, verses={
        "1_1": {
            "status": "completed",
            "chapter": 1,
            "verse": 1,
            "text_nikud": "בְּרֵאשִׁית",
            "source_files": ["000002.png"],
            "visual_uncertainty": []
        }
    })
    assert manager.save(), "Failed to save checkpoint"
    assert manager.is_image_processed("000002.png"), "Image should be processed"
    assert not manager.is_image_processed("000004.png"), "Image should not be processed"

    verses = manager.get_processed_verses()
    assert len(verses) == 1, f"Expected 1 verse, got {len(verses)}"
    assert verses[0]['text_nikud'] == "בְּרֵאשִׁית", "Verse text mismatch"

    checkpoint_path.unlink()
    print("✓ CheckpointManager tests passed")


def test_prompt():
    """Test prompt building."""
    print("Testing prompt building...")
    yaml_path = Path("docs/hebrew_vision_context.yaml")
    assert yaml_path.exists(), f"YAML file not found: {yaml_path}"

    yaml_data = load_yaml(yaml_path)
    assert yaml_data is not None, "Failed to load YAML"

    version = get_yaml_version(yaml_data)
    assert version is not None, "Failed to get version"
    print(f"  YAML version: {version}")

    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_content = f.read()
    yaml_hash = calculate_yaml_hash(yaml_content)
    assert len(yaml_hash) == 64, "Hash should be 64 characters"
    print(f"  YAML hash: {yaml_hash[:16]}...")

    prompt = build_prompt(yaml_data)
    assert len(prompt) > 0, "Prompt should not be empty"
    assert "Paleographic Priority" in prompt, "Prompt should contain paleographic rules"
    assert "Output Format" in prompt, "Prompt should contain output format"
    print(f"  Prompt length: {len(prompt)} characters")
    print("✓ Prompt building tests passed")


def test_validator():
    """Test validation functions."""
    print("Testing validator...")

    # Test Hebrew text validation
    is_valid, error = validate_hebrew_text("בְּרֵאשִׁית")
    assert is_valid, f"Valid Hebrew text rejected: {error}"

    is_valid, error = validate_hebrew_text("hello")
    assert not is_valid, "Non-Hebrew text should be rejected"

    # Test verse object validation
    valid_verse = {
        "number": 1,
        "text_nikud": "בְּרֵאשִׁית",
        "source_files": ["000002.png"],
        "visual_uncertainty": []
    }
    is_valid, error = validate_verse_object(valid_verse)
    assert is_valid, f"Valid verse rejected: {error}"

    invalid_verse = {"number": 1}  # Missing required fields
    is_valid, error = validate_verse_object(invalid_verse)
    assert not is_valid, "Invalid verse should be rejected"

    # Test chapter object validation
    valid_chapter = {
        "hebrew_letter": "א",
        "number": 1,
        "verses": [valid_verse]
    }
    is_valid, error = validate_chapter_object(valid_chapter)
    assert is_valid, f"Valid chapter rejected: {error}"

    # Test JSON parsing
    json_text = '{"chapters": [{"hebrew_letter": "א", "number": 1, "verses": []}]}'
    parsed, error = parse_json_response(json_text)
    assert parsed is not None, f"Failed to parse JSON: {error}"
    assert "chapters" in parsed, "Parsed JSON should contain chapters"

    print("✓ Validator tests passed")


def test_consolidator():
    """Test consolidation functions."""
    print("Testing consolidator...")

    verses = [
        {"chapter": 1, "verse": 1, "text_nikud": "בְּרֵאשִׁית", "source_files": ["000002.png"], "visual_uncertainty": []},
        {"chapter": 1, "verse": 2, "text_nikud": "בָּרָא", "source_files": ["000002.png"], "visual_uncertainty": []},
        {"chapter": 2, "verse": 1, "text_nikud": "וַיְהִי", "source_files": ["000004.png"], "visual_uncertainty": []},
    ]

    chapters = group_by_chapter(verses)
    assert len(chapters) == 2, f"Expected 2 chapters, got {len(chapters)}"
    assert 1 in chapters, "Chapter 1 should exist"
    assert 2 in chapters, "Chapter 2 should exist"
    assert len(chapters[1]) == 2, "Chapter 1 should have 2 verses"
    assert len(chapters[2]) == 1, "Chapter 2 should have 1 verse"

    book_json = build_book_json("test_book", chapters)
    assert book_json["book_name"] == "test_book", "Book name mismatch"
    assert book_json["author"] == "Elias Hutter", "Author mismatch"
    assert len(book_json["chapters"]) == 2, "Should have 2 chapters"
    assert book_json["chapters"][0]["hebrew_letter"] == "א", "First chapter should be א"
    assert book_json["chapters"][1]["hebrew_letter"] == "ב", "Second chapter should be ב"

    print("✓ Consolidator tests passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Gemini Transcription Implementation")
    print("=" * 60)
    print()

    try:
        test_checkpoint()
        print()
        test_prompt()
        print()
        test_validator()
        print()
        test_consolidator()
        print()
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Test failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

