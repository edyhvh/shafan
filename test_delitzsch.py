#!/usr/bin/env python3
"""
Simple test script for Delitzsch parser functionality.
"""

import sys
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def test_parser():
    """Test the parser with our test HTML file."""
    try:
        from delitzsch.parser import DelitzschParser

        parser = DelitzschParser()
        test_file = Path("data/cache/hebrew-bible.github.io/html/matthew.html")

        if not test_file.exists():
            print("Test HTML file not found")
            return False

        print(f"Testing parser with {test_file}")
        result = parser.parse_html_file(test_file)

        if result:
            print("Parser test successful!")
            print(f"Book: {result['book_name']}")
            print(f"Chapters: {len(result['chapters'])}")
            for chapter in result['chapters']:
                print(f"  Chapter {chapter['number']}: {len(chapter['verses'])} verses")
                for verse in chapter['verses'][:2]:  # Show first 2 verses
                    print(f"    Verse {verse['number']}: {verse['text_nikud'][:50]}...")
            return True
        else:
            print("Parser test failed")
            return False

    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_parser()
    sys.exit(0 if success else 1)