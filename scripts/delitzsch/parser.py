"""
HTML parsing and extraction logic for Delitzsch Hebrew New Testament.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

try:
    from bs4 import BeautifulSoup
    HAS_BEAUTIFULSOUP = True
except ImportError:
    BeautifulSoup = None
    HAS_BEAUTIFULSOUP = False

from .constants import DEFAULT_ENCODING, NEW_TESTAMENT_BOOKS, HTML_FILENAME_MAPPING

logger = logging.getLogger(__name__)


class DelitzschParser:
    """Parser for Delitzsch Hebrew New Testament HTML files."""

    def __init__(self):
        """Initialize the parser."""
        self.has_bs4 = HAS_BEAUTIFULSOUP
        if not HAS_BEAUTIFULSOUP:
            logger.warning("BeautifulSoup4 not available - limited functionality")

        # Common Hebrew text patterns
        self.hebrew_text_pattern = re.compile(r'[\u0590-\u05FF\u2000-\u206F]+')

        # Verse number patterns (may need adjustment based on actual HTML)
        self.verse_number_pattern = re.compile(r'^(\d+)\.?\s*')

        # Chapter header patterns (may need adjustment)
        self.chapter_header_pattern = re.compile(r'(?:chapter|פרק)\s*(\d+)', re.IGNORECASE)

    def parse_html_file(self, html_file: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a single HTML file and extract book data.

        Args:
            html_file: Path to the HTML file

        Returns:
            Dictionary containing parsed book data, or None if parsing failed
        """
        if not self.has_bs4:
            logger.error("BeautifulSoup4 required for HTML parsing")
            return None

        try:
            logger.debug(f"Parsing HTML file: {html_file}")

            # Read HTML content
            with open(html_file, 'r', encoding=DEFAULT_ENCODING) as f:
                html_content = f.read()

            # Parse HTML
            soup = BeautifulSoup(html_content, 'lxml')

            # Extract book information
            book_data = self._extract_book_data(soup, html_file)

            if book_data:
                logger.info(f"Successfully parsed {html_file.name}: {len(book_data.get('chapters', []))} chapters")
                return book_data
            else:
                logger.warning(f"No book data found in {html_file.name}")
                return None

        except Exception as e:
            logger.error(f"Error parsing HTML file {html_file}: {e}")
            return None

    def _extract_book_data(self, soup: BeautifulSoup, html_file: Path) -> Optional[Dict[str, Any]]:
        """
        Extract book data from parsed HTML.

        Args:
            soup: BeautifulSoup object
            html_file: Path to the HTML file

        Returns:
            Dictionary with book data or None
        """
        # Try to determine book name from filename or content
        book_name = self._determine_book_name(html_file, soup)
        if not book_name:
            logger.warning(f"Could not determine book name for {html_file.name}")
            return None

        # Extract chapters
        chapters = self._extract_chapters(soup)

        if not chapters:
            logger.warning(f"No chapters found in {html_file.name}")
            return None

        return {
            'book_name': book_name,
            'chapters': chapters,
            'source_file': str(html_file)
        }

    def _determine_book_name(self, html_file: Path, soup: BeautifulSoup) -> Optional[str]:
        """
        Determine the book name from filename or HTML content.

        Args:
            html_file: Path to the HTML file
            soup: BeautifulSoup object

        Returns:
            Book name in lowercase format, or None
        """
        filename = html_file.stem.lower()

        # Create reverse mapping from HTML filename to book name
        html_to_book = {html_name: book for book, html_name in HTML_FILENAME_MAPPING.items()}

        # Try direct filename mapping first
        if filename in html_to_book:
            return html_to_book[filename]

        # Fallback: Try to match filename against known book names
        for book_key in NEW_TESTAMENT_BOOKS.keys():
            if book_key in filename:
                return book_key

        # Try to extract from title or headings
        title = soup.find('title')
        if title and title.text:
            title_text = title.text.lower()
            for book_key, book_name in NEW_TESTAMENT_BOOKS.items():
                if book_key in title_text or book_name.lower() in title_text:
                    return book_key

        # Try to find book name in headings
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            heading_text = heading.get_text().lower().strip()
            for book_key, book_name in NEW_TESTAMENT_BOOKS.items():
                if book_key in heading_text or book_name.lower() in heading_text:
                    return book_key

        logger.debug(f"Could not determine book name from {filename}")
        return None

    def _extract_chapters(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract chapters from the HTML content.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of chapter dictionaries
        """
        chapters = []

        # Get chapter elements with their actual numbers
        chapter_elements = self._find_chapter_elements(soup)

        for chapter_num, chapter_element in chapter_elements:
            verses = self._extract_verses_from_chapter(chapter_element)

            if verses:
                # Convert chapter number to Hebrew numeral
                hebrew_letter = self._number_to_hebrew_numeral(chapter_num)

                chapters.append({
                    'hebrew_letter': hebrew_letter,
                    'number': chapter_num,
                    'verses': verses
                })

        return chapters

    def _find_chapter_elements(self, soup: BeautifulSoup) -> List[Tuple[int, Any]]:
        """
        Find HTML elements that contain chapter content.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of tuples (chapter_number, element) containing chapter content
        """
        chapters = []

        # Look for h2 elements containing "Chapter"
        for h2 in soup.find_all('h2'):
            text = h2.get_text().strip()
            if 'Chapter' in text or 'פרק' in text:
                # Extract chapter number from <a name="X"> tag
                anchor = h2.find('a', attrs={'name': True})
                if anchor and anchor.get('name'):
                    try:
                        chapter_num = int(anchor.get('name'))
                        # Find the table that follows this h2
                        table = h2.find_next('table')
                        if table:
                            chapters.append((chapter_num, table))
                    except ValueError:
                        continue

        # Sort by chapter number
        chapters.sort(key=lambda x: x[0])

        return chapters

    def _extract_verses_from_chapter(self, chapter_element) -> List[Dict[str, Any]]:
        """
        Extract verses from a chapter element (table).

        Args:
            chapter_element: BeautifulSoup table element containing chapter verses

        Returns:
            List of verse dictionaries
        """
        verses = []

        # Find all table rows with class="break"
        rows = chapter_element.find_all('tr', class_='break')

        for row in rows:
            # Get all table cells
            cells = row.find_all('td')
            if len(cells) >= 3:
                # First cell: Hebrew text
                hebrew_cell = cells[0]
                hebrew_text_elem = hebrew_cell.find('p', class_='heb')
                if hebrew_text_elem:
                    hebrew_text = self._clean_hebrew_text(hebrew_text_elem.get_text())
                else:
                    continue

                # Find verse number - it could be in column 2 (3-column table) or column 3 (4-column table)
                verse_num = None
                for cell in cells[1:]:  # Check cells after the Hebrew text cell
                    verse_num_elem = cell.find('p', class_='versenum')
                    if verse_num_elem:
                        verse_num_text = verse_num_elem.get_text().strip()
                        try:
                            verse_num = int(verse_num_text)
                            break  # Found it, stop looking
                        except ValueError:
                            continue

                if verse_num is None:
                    continue

                # Add verse if we have both text and number
                if hebrew_text and verse_num:
                    verses.append({
                        'number': verse_num,
                        'text_nikud': hebrew_text
                    })

        return verses

    def _clean_hebrew_text(self, text: str) -> str:
        """
        Clean and normalize Hebrew text.

        Args:
            text: Raw Hebrew text from HTML

        Returns:
            Cleaned Hebrew text
        """
        if not text:
            return ""

        # Remove newlines and extra whitespace
        text = text.replace('\n', ' ')

        # Replace multiple spaces with single space
        import re
        text = re.sub(r'\s+', ' ', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def _number_to_hebrew_numeral(self, number: int) -> str:
        """
        Convert a number to Hebrew numeral.

        Args:
            number: Number to convert

        Returns:
            Hebrew numeral string
        """
        # Hebrew numerals mapping (extended for all reasonable chapter numbers)
        hebrew_numerals = {
            1: 'א', 2: 'ב', 3: 'ג', 4: 'ד', 5: 'ה', 6: 'ו', 7: 'ז', 8: 'ח', 9: 'ט', 10: 'י',
            11: 'יא', 12: 'יב', 13: 'יג', 14: 'יד', 15: 'טו', 16: 'טז', 17: 'יז', 18: 'יח', 19: 'יט', 20: 'כ',
            21: 'כא', 22: 'כב', 23: 'כג', 24: 'כד', 25: 'כה', 26: 'כו', 27: 'כז', 28: 'כח', 29: 'כט', 30: 'ל',
            31: 'לא', 32: 'לב', 33: 'לג', 34: 'לד', 35: 'לה', 36: 'לו', 37: 'לז', 38: 'לח', 39: 'לט', 40: 'מ',
            41: 'מא', 42: 'מב', 43: 'מג', 44: 'מד', 45: 'מה', 46: 'מו', 47: 'מז', 48: 'מח', 49: 'מט', 50: 'נ',
            51: 'נא', 52: 'נב', 53: 'נג', 54: 'נד', 55: 'נה', 56: 'נו', 57: 'נז', 58: 'נח', 59: 'נט', 60: 'ס',
            61: 'סא', 62: 'סב', 63: 'סג', 64: 'סד', 65: 'סה', 66: 'סו', 67: 'סז', 68: 'סח', 69: 'סט', 70: 'ע',
            71: 'עא', 72: 'עב', 73: 'עג', 74: 'עד', 75: 'עה', 76: 'עו', 77: 'עז', 78: 'עח', 79: 'עט', 80: 'פ',
            81: 'פא', 82: 'פב', 83: 'פג', 84: 'פד', 85: 'פה', 86: 'פו', 87: 'פז', 88: 'פח', 89: 'פט', 90: 'צ',
            91: 'צא', 92: 'צב', 93: 'צג', 94: 'צד', 95: 'צה', 96: 'צו', 97: 'צז', 98: 'צח', 99: 'צט', 100: 'ק'
        }

        return hebrew_numerals.get(number, str(number))

    def explore_html_structure(self, html_file: Path) -> Dict[str, Any]:
        """
        Explore and analyze the HTML structure for debugging.

        Args:
            html_file: Path to the HTML file

        Returns:
            Dictionary with structural analysis
        """
        if not self.has_bs4:
            return {'error': 'BeautifulSoup4 required for HTML exploration'}

        try:
            with open(html_file, 'r', encoding=DEFAULT_ENCODING) as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'lxml')

            analysis = {
                'file': str(html_file),
                'title': soup.find('title').get_text() if soup.find('title') else None,
                'headings': [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])],
                'div_count': len(soup.find_all('div')),
                'p_count': len(soup.find_all('p')),
                'span_count': len(soup.find_all('span')),
                'text_length': len(html_content),
                'sample_text': html_content[:500] + '...' if len(html_content) > 500 else html_content
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing HTML structure: {e}")
            return {'error': str(e)}


def parse_html_files(html_files: List[Path], explore_only: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    Parse multiple HTML files.

    Args:
        html_files: List of HTML file paths
        explore_only: If True, only explore structure without full parsing

    Returns:
        Dictionary mapping book names to parsed data
    """
    parser = DelitzschParser()
    results = {}

    for html_file in html_files:
        if explore_only:
            analysis = parser.explore_html_structure(html_file)
            book_name = html_file.stem  # Use filename as key for exploration
            results[book_name] = {'analysis': analysis}
        else:
            book_data = parser.parse_html_file(html_file)
            if book_data:
                results[book_data['book_name']] = book_data

    return results