# shafan - Digital Edition of Elias Hutter's Hebrew Besorah

**shafan** is the first public, free, and completely open digital edition of the Hebrew translation of Besorah (New Testament) made by Elias Hutter in Nuremberg between 1599 and 1602—a historical text that for 426 years only existed in physical libraries or illegible scanned PDFs.

## 🚀 Quick Start

### Clone the Repository

```bash
git clone https://github.com/edyhvh/shafan.git
cd shafan
```

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12** (managed via mise)
- **Node.js 20** (managed via mise)
- **aria2** (for downloading PDFs): `brew install aria2`
- **poppler** (converting PDFs pages to images): `brew install poppler`

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
# Go to shafan dir first
cd path/to/shafan

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

### Convert PDFs to Images

Once you have the PDF source files, you need to convert them to images for OCR processing. This script converts PDF pages to high-quality PNG images optimized for OCR:

```bash
# Go to shafan dir first
cd path/to/shafan

# List all available books
python scripts/get_images_from_pdfs.py --list

# Convert specific books (example)
python scripts/get_images_from_pdfs.py matthew mark luke

# Convert all books (this will take several hours)
python scripts/get_images_from_pdfs.py all

# Test conversion with first 2 pages only (recommended before full conversion)
python scripts/get_images_from_pdfs.py --test matthew

# Convert specific page ranges
python scripts/get_images_from_pdfs.py --pages 1-5 matthew

# Optimized settings for speed (recommended for most books)
python scripts/get_images_from_pdfs.py --dpi 150 --batch-size 25 matthew

# Force re-conversion if needed
python scripts/get_images_from_pdfs.py --force matthew

# Check PDF integrity before conversion
python scripts/get_images_from_pdfs.py --check-integrity
```

**Important Notes**:
- **DPI Settings**: Use 150-200 DPI for OCR (300 DPI produces very large files but similar OCR quality)
- **Batch Size**: Higher values (20-30) are faster but use more memory
- **Resume Capability**: The script automatically detects already converted pages and skips them
- **Estimated Times**: Matthew (~25-35min), Acts (~45-60min), Revelation (~20-30min) at 150 DPI with batch-size 25
- **Requirements**: `pdf2image` (uses poppler), `tqdm` for progress bars

### Extract Hebrew Text Columns

After converting PDFs to images, extract the Hebrew text columns from the manuscript pages:

```bash
# List all available books
python scripts/hebrew_images/main.py --list

# Process specific books (example)
python scripts/hebrew_images/main.py matthew mark luke

# Process all books
python scripts/hebrew_images/main.py all
```

**Special Case**: When processing `colossians`, pages 000026.png, 000028.png, and 000030.png are automatically saved to the `laodikim` directory, as these pages contain Paul's letter to Laodicea.

### Transcribe Hebrew Text with AI

After extracting the Hebrew column images, use the Gemini Vision API to transcribe the Hebrew text into structured JSON:

```bash
# Set your Gemini API key (get one at https://aistudio.google.com/app/apikey)
export GEMINI_API_KEY="your-api-key-here"

# List all available books
python scripts/hebrew_text/main.py --list

# Process specific books
python scripts/hebrew_text/main.py --book jude
python scripts/hebrew_text/main.py --book philemon

# Process multiple books
python scripts/hebrew_text/main.py matthew mark luke

# Process all books
python scripts/hebrew_text/main.py --all

# Test with 5 images only (dry-run)
python scripts/hebrew_text/main.py --book jude --dry-run

# Resume interrupted processing
python scripts/hebrew_text/main.py --book matthew --resume

# Reprocess failed images
python scripts/hebrew_text/main.py --book matthew --reprocess-failed
```

**Output**: JSON files are saved to `output/` with the structure: book → chapters → verses with nikud (vowel points).

**Checkpoints**: Progress is saved automatically to `output/.checkpoints/`, allowing you to resume interrupted processing.

### Training Dataset

The extracted Hebrew text images used for model training are hosted on Hugging Face at [https://huggingface.co/datasets/edyhvh/hutter](https://huggingface.co/datasets/edyhvh/hutter) instead of GitHub to avoid repository bloat. If you want to improve the OCR model, you can download the training images from there.







