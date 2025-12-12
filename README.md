# safan - Digital Edition of Elias Hutter's Hebrew Besorah

**SAFAN** is the first public, free, and completely open digital edition of the Hebrew translation of Besorah (New Testament) made by Elias Hutter in Nuremberg between 1599 and 1602—a historical text that for 426 years only existed in physical libraries or illegible scanned PDFs.

## 🚀 Quick Start

### Clone the Repository

```bash
git clone https://github.com/edyhvh/safan.git
cd safan
```

**Note**: Replace `YOUR_USERNAME` with your actual GitHub username when you create the repository.

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12** (managed via mise)
- **Node.js 20** (managed via mise)
- **aria2** (for downloading PDFs): `brew install aria2`

### One-Command Setup

```bash
python setup.py
```

This command will:
- Set up mise and install Python 3.12 + Node.js 20
- Create a virtual environment (`.venv`)
- Install all Python dependencies (OCR libraries, OpenCV, etc.)
- Configure direnv for automatic environment activation
- Create the basic project structure

### Download the Source PDFs

The Hutter Polyglot Bible PDFs are not included in this repository because they are very large (~7.5G total). You can download them using the provided script: 

```bash
# Go to safan dir first
cd path/to/safan

# List all available books
python scripts/get_hutter_pdfs.py --list

# Download specific books (example)
python scripts/get_hutter_pdfs.py matthew mark luke

# Download all books
python scripts/get_hutter_pdfs.py all

# Resume incomplete downloads (useful if download was interrupted)
python scripts/get_hutter_pdfs.py --resume acts matthew

# Force re-download existing files
python scripts/get_hutter_pdfs.py --force matthew
```

**Note**: This requires `aria2` to be installed. The script uses optimized aria2 settings for maximum download speed with resume capability for interrupted downloads.