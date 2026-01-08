"""
Repository downloading and HTML file location for Delitzsch Hebrew New Testament extractor.
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    requests = None
    HAS_REQUESTS = False

from .constants import (
    REPOSITORY_URL,
    DEFAULT_REPO_DIR,
    HTML_DIR,
    HTML_PATTERNS,
    REPO_TIMEOUT,
    NEW_TESTAMENT_BOOKS,
    HTML_FILENAME_MAPPING,
)

logger = logging.getLogger(__name__)


def is_git_available() -> bool:
    """Check if git is installed and available."""
    return shutil.which("git") is not None


def get_git_install_instructions() -> str:
    """Return installation instructions for git."""
    return """
Error: git is not installed!

Install git:
  macOS:         xcode-select --install  # or brew install git
  Ubuntu/Debian: sudo apt install git
  Windows:       Download from https://git-scm.com/
"""


def is_repository_valid(repo_path: Path) -> bool:
    """
    Check if a repository path contains a valid git repository.

    Args:
        repo_path: Path to check

    Returns:
        True if repository is valid, False otherwise
    """
    if not repo_path.exists():
        return False

    git_dir = repo_path / ".git"
    if not git_dir.exists() or not git_dir.is_dir():
        return False

    # Check if it's actually a git repository by running git status
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False


def clone_repository(repo_url: str, repo_path: Path, timeout: int = REPO_TIMEOUT) -> bool:
    """
    Clone a git repository to the specified path.

    Args:
        repo_url: URL of the repository to clone
        repo_path: Local path where to clone the repository
        timeout: Timeout in seconds for the clone operation

    Returns:
        True if clone successful, False otherwise
    """
    try:
        # Create parent directories if they don't exist
        repo_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Cloning repository from {repo_url} to {repo_path}")

        # Clone the repository
        result = subprocess.run(
            ["git", "clone", repo_url, str(repo_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            logger.info("Repository cloned successfully")
            return True
        else:
            logger.error(f"Failed to clone repository: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"Repository clone timed out after {timeout} seconds")
        return False
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        return False


def update_repository(repo_path: Path, timeout: int = 30) -> bool:
    """
    Update an existing repository by pulling latest changes.

    Args:
        repo_path: Path to the repository
        timeout: Timeout in seconds for the pull operation

    Returns:
        True if update successful, False otherwise
    """
    try:
        logger.info(f"Updating repository at {repo_path}")

        # Pull latest changes
        result = subprocess.run(
            ["git", "pull"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            logger.info("Repository updated successfully")
            return True
        else:
            logger.warning(f"Failed to update repository: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"Repository update timed out after {timeout} seconds")
        return False
    except Exception as e:
        logger.error(f"Error updating repository: {e}")
        return False


def ensure_repository(
    repo_url: str = REPOSITORY_URL,
    repo_path: Optional[Path] = None,
    force_clone: bool = False,
    update_existing: bool = True
) -> Optional[Path]:
    """
    Ensure the repository is available locally.

    Args:
        repo_url: URL of the repository to clone
        repo_path: Local path for the repository (default: DEFAULT_REPO_DIR)
        force_clone: Force re-clone even if repository exists
        update_existing: Update existing repository with latest changes

    Returns:
        Path to the repository if successful, None otherwise
    """
    if not is_git_available():
        print(get_git_install_instructions())
        return None

    if repo_path is None:
        repo_path = DEFAULT_REPO_DIR

    repo_path = Path(repo_path)

    # Check if repository already exists and is valid
    if repo_path.exists() and not force_clone:
        if is_repository_valid(repo_path):
            logger.info(f"Repository already exists at {repo_path}")
            if update_existing:
                update_repository(repo_path)
            return repo_path
        else:
            logger.warning(f"Repository at {repo_path} is invalid, will re-clone")
            # Remove invalid repository before cloning
            logger.info(f"Removing invalid repository: {repo_path}")
            try:
                shutil.rmtree(repo_path)
            except Exception as e:
                logger.error(f"Failed to remove invalid repository: {e}")
                return None

    # Remove existing directory if force cloning
    if force_clone and repo_path.exists():
        logger.info(f"Removing existing repository for force clone: {repo_path}")
        try:
            shutil.rmtree(repo_path)
        except Exception as e:
            logger.error(f"Failed to remove existing repository: {e}")
            return None

    # Clone the repository
    if clone_repository(repo_url, repo_path):
        return repo_path
    else:
        return None


def find_html_files(repo_path: Path) -> List[Path]:
    """
    Find all HTML files in the repository.

    Args:
        repo_path: Path to the repository

    Returns:
        List of HTML file paths
    """
    html_files = []

    # Check if html directory exists
    html_dir = repo_path / HTML_DIR
    if html_dir.exists() and html_dir.is_dir():
        # Find HTML files in the html directory
        for pattern in HTML_PATTERNS:
            html_files.extend(html_dir.glob(pattern))

    # Also check root directory for HTML files
    for pattern in HTML_PATTERNS:
        html_files.extend(repo_path.glob(pattern))

    # Remove duplicates and sort
    html_files = list(set(html_files))
    html_files.sort()

    logger.info(f"Found {len(html_files)} HTML files in repository")
    return html_files


def download_html_files_directly(output_dir: Path, books: Optional[List[str]] = None) -> List[Path]:
    """
    Download HTML files directly from GitHub raw content instead of cloning repository.

    Args:
        output_dir: Directory to save HTML files
        books: List of book names to download (None for all New Testament books)

    Returns:
        List of downloaded HTML file paths
    """
    if not HAS_REQUESTS:
        logger.error("requests library required for direct download mode")
        logger.info("To install: pip install requests")
        return []

    if books is None:
        books = list(NEW_TESTAMENT_BOOKS.keys())

    downloaded_files = []
    base_url = "https://raw.githubusercontent.com/hebrew-bible/hebrew-bible.github.io/master/html"

    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Attempting to download {len(books)} HTML files...")

    for book in books:
        # Use the HTML filename mapping to get the correct filename
        html_name = HTML_FILENAME_MAPPING.get(book, book)
        html_filename = f"{html_name}.html"
        url = f"{base_url}/{html_filename}"
        output_file = output_dir / html_filename

        try:
            logger.info(f"Downloading {html_filename} for book '{book}'...")
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                downloaded_files.append(output_file)
                logger.debug(f"Downloaded {html_filename}")
            else:
                logger.warning(f"Failed to download {html_filename}: HTTP {response.status_code}")

        except Exception as e:
            logger.error(f"Error downloading {html_filename}: {e}")
            logger.info(f"You can manually download from: {url}")
            logger.info(f"And save to: {output_file}")

    logger.info(f"Downloaded {len(downloaded_files)} HTML files")
    return downloaded_files


def locate_delitzsch_files(repo_path: Path, book_filter: Optional[List[str]] = None) -> List[Path]:
    """
    Locate HTML files that contain Delitzsch translation.

    Args:
        repo_path: Path to the repository
        book_filter: Optional list of book names to filter by (defaults to New Testament books)

    Returns:
        List of HTML files containing Delitzsch translation
    """
    html_files = find_html_files(repo_path)

    # Filter to only New Testament books by default
    if book_filter is None:
        book_filter = list(NEW_TESTAMENT_BOOKS.keys())

    # Create reverse mapping from HTML filename to book name
    html_to_book = {filename: book for book, filename in HTML_FILENAME_MAPPING.items()}

    filtered_files = []
    for html_file in html_files:
        html_name = html_file.stem.lower()  # filename without .html extension
        if html_name in html_to_book:
            book_name = html_to_book[html_name]
            if book_name in book_filter:
                filtered_files.append(html_file)

    logger.info(f"Located {len(filtered_files)} New Testament HTML files out of {len(html_files)} total files")

    # Log the found files
    for i, html_file in enumerate(filtered_files):
        html_name = html_file.stem.lower()
        book_name = html_to_book.get(html_name, "unknown")
        logger.debug(f"New Testament file {i+1}: {html_file.relative_to(repo_path)} (book: {book_name})")

    return filtered_files