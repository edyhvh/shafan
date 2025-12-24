#!/usr/bin/env python3
"""
Analyze verses in output JSON files to find problematic entries.

This script helps identify verses that have issues such as:
- Too many source_files (indicating incorrect merging)
- Extremely long text (indicating concatenation of multiple pages)
- Suspicious patterns in text content

Usage:
    python tools/analyze_verses.py output/acts.json
    python tools/analyze_verses.py output/acts.json --max-sources 3
    python tools/analyze_verses.py output/acts.json --max-length 500
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class Issue:
    """Represents an issue found in a verse."""
    TOO_MANY_SOURCES = "too_many_sources"
    TEXT_TOO_LONG = "text_too_long"
    POSSIBLE_WRONG_MERGE = "possible_wrong_merge"
    EMPTY_TEXT = "empty_text"


def analyze_verse(
    chapter_num: int,
    verse: Dict[str, Any],
    max_sources: int = 3,
    max_length: int = 500
) -> List[Dict[str, Any]]:
    """
    Analyze a single verse for issues.

    Args:
        chapter_num: Chapter number
        verse: Verse dictionary
        max_sources: Maximum acceptable number of source files
        max_length: Maximum acceptable text length

    Returns:
        List of issues found
    """
    issues = []
    verse_num = verse.get('number')
    text = verse.get('text_nikud', '')
    source_files = verse.get('source_files', [])

    # Check for too many source files
    if len(source_files) > max_sources:
        issues.append({
            'type': Issue.TOO_MANY_SOURCES,
            'chapter': chapter_num,
            'verse': verse_num,
            'source_count': len(source_files),
            'source_files': source_files,
            'text_length': len(text),
            'text_preview': text[:100] + '...' if len(text) > 100 else text
        })

    # Check for excessively long text
    if len(text) > max_length:
        issues.append({
            'type': Issue.TEXT_TOO_LONG,
            'chapter': chapter_num,
            'verse': verse_num,
            'text_length': len(text),
            'source_count': len(source_files),
            'expected_max': max_length,
            'text_preview': text[:100] + '...' if len(text) > 100 else text
        })

    # Check for empty text
    if not text or text.strip() == '':
        issues.append({
            'type': Issue.EMPTY_TEXT,
            'chapter': chapter_num,
            'verse': verse_num,
            'source_files': source_files
        })

    return issues


def analyze_book(
    book_data: Dict[str, Any],
    max_sources: int = 3,
    max_length: int = 500
) -> Dict[str, Any]:
    """
    Analyze all verses in a book for issues.

    Args:
        book_data: Book JSON data
        max_sources: Maximum acceptable number of source files
        max_length: Maximum acceptable text length

    Returns:
        Analysis report dictionary
    """
    all_issues = []
    stats = {
        'total_chapters': 0,
        'total_verses': 0,
        'problematic_verses': 0,
        'issues_by_type': {}
    }

    chapters = book_data.get('chapters', [])
    stats['total_chapters'] = len(chapters)

    for chapter in chapters:
        chapter_num = chapter.get('number')
        verses = chapter.get('verses', [])

        for verse in verses:
            stats['total_verses'] += 1
            issues = analyze_verse(chapter_num, verse, max_sources, max_length)

            if issues:
                stats['problematic_verses'] += 1
                all_issues.extend(issues)

                for issue in issues:
                    issue_type = issue['type']
                    stats['issues_by_type'][issue_type] = stats['issues_by_type'].get(issue_type, 0) + 1

    return {
        'book_name': book_data.get('book_name'),
        'stats': stats,
        'issues': all_issues
    }


def print_report(report: Dict[str, Any], verbose: bool = False):
    """
    Print analysis report to console.

    Args:
        report: Analysis report dictionary
        verbose: If True, print detailed issue information
    """
    print(f"\n{'='*60}")
    print(f"ANALYSIS REPORT: {report['book_name']}")
    print(f"{'='*60}")

    stats = report['stats']
    print(f"\nStatistics:")
    print(f"  Total chapters: {stats['total_chapters']}")
    print(f"  Total verses: {stats['total_verses']}")
    print(f"  Problematic verses: {stats['problematic_verses']}")

    if stats['issues_by_type']:
        print(f"\nIssues by type:")
        for issue_type, count in sorted(stats['issues_by_type'].items()):
            print(f"  {issue_type}: {count}")

    if report['issues']:
        print(f"\n{'='*60}")
        print("DETAILED ISSUES:")
        print(f"{'='*60}")

        # Group issues by type
        issues_by_type = {}
        for issue in report['issues']:
            issue_type = issue['type']
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)

        for issue_type, issues in issues_by_type.items():
            print(f"\n## {issue_type.upper()} ({len(issues)} occurrences)")
            print("-" * 40)

            # Sort by chapter and verse
            issues.sort(key=lambda x: (x.get('chapter', 0), x.get('verse', 0)))

            for issue in issues[:10]:  # Show first 10
                chapter = issue.get('chapter')
                verse = issue.get('verse')
                print(f"\n  Chapter {chapter}, Verse {verse}:")

                if issue_type == Issue.TOO_MANY_SOURCES:
                    print(f"    Source files: {issue['source_count']} (expected ≤3)")
                    print(f"    Files: {issue['source_files']}")
                    print(f"    Text length: {issue['text_length']} chars")

                elif issue_type == Issue.TEXT_TOO_LONG:
                    print(f"    Text length: {issue['text_length']} chars (max: {issue['expected_max']})")
                    print(f"    Source count: {issue['source_count']}")

                elif issue_type == Issue.EMPTY_TEXT:
                    print(f"    Source files: {issue['source_files']}")

                if verbose and 'text_preview' in issue:
                    print(f"    Preview: {issue['text_preview']}")

            if len(issues) > 10:
                print(f"\n  ... and {len(issues) - 10} more")

    print(f"\n{'='*60}")


def get_verses_to_fix(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract list of verses that need to be fixed.

    Args:
        report: Analysis report dictionary

    Returns:
        List of verse references that need fixing
    """
    verses_to_fix = []
    seen = set()

    for issue in report['issues']:
        key = (issue.get('chapter'), issue.get('verse'))
        if key not in seen:
            seen.add(key)
            verses_to_fix.append({
                'chapter': issue.get('chapter'),
                'verse': issue.get('verse'),
                'issues': [issue['type']],
                'source_files': issue.get('source_files', [])
            })
        else:
            # Add issue type to existing entry
            for v in verses_to_fix:
                if v['chapter'] == key[0] and v['verse'] == key[1]:
                    if issue['type'] not in v['issues']:
                        v['issues'].append(issue['type'])
                    break

    return verses_to_fix


def save_fix_list(verses_to_fix: List[Dict[str, Any]], output_path: Path):
    """
    Save list of verses to fix to JSON file.

    Args:
        verses_to_fix: List of verse references
        output_path: Path to output file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_verses_to_fix': len(verses_to_fix),
            'verses': verses_to_fix
        }, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved fix list to: {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze verses in output JSON files for issues.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'input_file',
        type=str,
        help='Path to the JSON file to analyze (e.g., output/acts.json)'
    )

    parser.add_argument(
        '--max-sources',
        type=int,
        default=3,
        help='Maximum acceptable number of source files per verse (default: 3)'
    )

    parser.add_argument(
        '--max-length',
        type=int,
        default=500,
        help='Maximum acceptable text length per verse (default: 500)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed issue information including text previews'
    )

    parser.add_argument(
        '--output-fix-list',
        type=str,
        help='Path to save list of verses that need fixing (JSON file)'
    )

    args = parser.parse_args()

    # Load input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    logger.info(f"Loading: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        book_data = json.load(f)

    # Analyze book
    report = analyze_book(
        book_data,
        max_sources=args.max_sources,
        max_length=args.max_length
    )

    # Print report
    print_report(report, verbose=args.verbose)

    # Save fix list if requested
    if args.output_fix_list:
        verses_to_fix = get_verses_to_fix(report)
        save_fix_list(verses_to_fix, Path(args.output_fix_list))


if __name__ == "__main__":
    main()

