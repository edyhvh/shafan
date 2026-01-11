# shafan - Digital Edition of Elias Hutter's Hebrew Besorah

**shafan** is the first public, free, and completely open digital edition of the Hebrew translation of Besorah (New Testament) made by Elias Hutter in Nuremberg between 1599 and 1602—a historical text that for 426 years only existed in physical libraries or illegible scanned PDFs.

## Data Sources

### Tanaj (Hebrew Bible)
The Tanaj data used in this project comes from the Open Scriptures Hebrew Bible project. We use the morphological analysis from [morphhb](https://github.com/openscriptures/morphhb), which provides lemma and morphology information for Hebrew Bible texts.

### Besorah (Delitzsch)
The Besorah data used in this project comes from Franz Delitzsch's Hebrew New Testament. We obtained the data from [hebrew-bible.github.io](https://github.com/hebrew-bible/hebrew-bible.github.io), which provides a complete Hebrew Bible including the New Testament.

### Versification Mapping
Versification mapping data is obtained from the [Copenhagen Alliance](https://github.com/Copenhagen-Alliance/copenhagen-alliance.github.io) project, which provides standardized mappings between Hebrew (Masoretic) and English (KJV-style) versification systems. This data is used to handle differences in verse numbering between Hebrew and English traditions, particularly for Tanakh books where verse numbers differ (e.g., Psalms where Hebrew counts psalm titles as verse 1, while English starts content as verse 1). The mapping data is processed and simplified for use in the frontend to enable accurate cross-referencing between Hebrew and English verse numbers.

## Quick Start

### Prerequisites

- **Python 3.12** (managed via mise)
- **Node.js 20** (managed via mise)
- **aria2** (for downloading PDFs): `brew install aria2`
- **poppler** (for converting PDFs to images): `brew install poppler`

### Setup

```bash
# Clone the repository
git clone https://github.com/edyhvh/shafan.git
cd shafan

# One-command setup (installs dependencies, creates virtual environment)
python setup.py
```

This will set up mise, install Python 3.12 + Node.js 20, create a virtual environment, install all dependencies, and configure direnv for automatic environment activation.

## Workflow Overview

The project follows a pipeline to convert historical PDF manuscripts into a digital edition:

1. **Download PDFs** → Download source PDFs from the Hutter Polyglot Bible archive
2. **Convert to Images** → Convert PDF pages to images optimized for OCR
3. **Extract Hebrew Columns** → Extract the Hebrew text columns from manuscript pages
4. **Transcribe Text** → Use AI to transcribe Hebrew text into structured JSON
5. **Web Interface** → Browse and read the digital edition in the frontend

## Detailed Documentation

For detailed instructions and options for each step, see the README files in each directory:

- **[scripts/pdf/README.md](scripts/pdf/README.md)** - Downloading source PDFs
- **[scripts/images/README.md](scripts/images/README.md)** - Converting PDFs to images
- **[scripts/hebrew_images/README.md](scripts/hebrew_images/README.md)** - Extracting Hebrew text columns
- **[scripts/text/README.md](scripts/text/README.md)** - Transcribing Hebrew text with AI
- **[frontend/README.md](frontend/README.md)** - Running the web application

## Quick Commands

```bash
# Download PDFs
python -m scripts.pdf all

# Convert PDFs to images
python -m scripts.images all

# Extract Hebrew columns
python scripts/hebrew_images/main.py all

# Transcribe text (requires API key)
export ANTHROPIC_API_KEY="your-api-key"
python -m scripts.text --all

# Run frontend
cd frontend && npm run dev
```

## Training Dataset

The extracted Hebrew text images used for model training are hosted on Hugging Face at [https://huggingface.co/datasets/edyhvh/hutter](https://huggingface.co/datasets/edyhvh/hutter) instead of GitHub to avoid repository bloat.







