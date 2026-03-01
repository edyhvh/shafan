#!/usr/bin/env python3
"""
Validate versification mappings used by Shafan.

Checks:
1) frontend/public and data/versification files are identical
2) key boundary mappings exist (especially Isaiah)
3) Joel mapping exists and matches expected chapter shifts
"""

import json
import pathlib
import sys


ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
FRONTEND_PATH = ROOT_DIR / "frontend" / "public" / "data" / "versification" / "versification.json"
DATA_PATH = ROOT_DIR / "data" / "versification" / "versification.json"


REQUIRED_MAPPINGS = {
    "ISA": {
        "8": {"23": "9:1"},
        "9": {"1": "9:2", "20": "9:21"},
        "64": {"1": "64:2", "11": "64:12"},
    },
    "JER": {
        "8": {"23": "9:1"},
    },
    "EZK": {
        "21": {"1": "20:45"},
    },
    "MAL": {
        "3": {"19": "4:1", "24": "4:6"},
    },
    "JOL": {
        "3": {"1": "2:28", "5": "2:32"},
        "4": {"1": "3:1", "21": "3:21"},
    },
    "PSA": {
        "3": {"0": "3:1"},
        "51": {"1": "51:3"},
    },
}


def load_json(path: pathlib.Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_required_mappings(data: dict) -> list[str]:
    errors: list[str] = []

    for book, chapter_map in REQUIRED_MAPPINGS.items():
        if book not in data:
            errors.append(f"Missing book mapping: {book}")
            continue

        simple_map = data[book].get("simple_map", {})
        for chapter, verse_map in chapter_map.items():
            if chapter not in simple_map:
                errors.append(f"Missing chapter mapping: {book} {chapter}")
                continue
            for verse, expected in verse_map.items():
                actual = simple_map[chapter].get(verse)
                if actual != expected:
                    errors.append(
                        f"Wrong mapping for {book} {chapter}:{verse} -> {actual!r}, expected {expected!r}"
                    )

    return errors


def validate_value_format(data: dict) -> list[str]:
    errors: list[str] = []

    for book, book_data in data.items():
        simple_map = book_data.get("simple_map", {})
        for chapter, verses in simple_map.items():
            for verse, mapped in verses.items():
                if ":" not in mapped:
                    errors.append(
                        f"Invalid mapped value format for {book} {chapter}:{verse}: {mapped!r} (expected 'chapter:verse')"
                    )

    return errors


def main() -> int:
    try:
        frontend_data = load_json(FRONTEND_PATH)
        data_copy = load_json(DATA_PATH)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1

    errors: list[str] = []

    if frontend_data != data_copy:
        errors.append(
            f"Files are not synchronized: {FRONTEND_PATH} != {DATA_PATH}"
        )

    errors.extend(validate_required_mappings(frontend_data))
    errors.extend(validate_value_format(frontend_data))

    if errors:
        print("Versification validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Versification validation passed.")
    print(f"- Synchronized files: {FRONTEND_PATH.name} and {DATA_PATH.name}")
    print("- Required boundary mappings verified (ISA/JER/EZK/PSA/JOL/MAL)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
