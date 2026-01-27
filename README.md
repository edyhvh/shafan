# Shafan - שפן

**Shafan** is a comprehensive, free, and open-source platform for studying Hebrew Scriptures, featuring both the **Tanakh** (Hebrew Bible) and the **Besorah** (New Testament) with multiple Hebrew translations.

The project brings together two significant Hebrew Besorah translations: **Elias Hutter's** groundbreaking 1599-1602 edition (digitized for the first time from historical manuscripts) and **Franz Delitzsch's** scholarly 19th-century translation. Combined with morphologically analyzed Tanakh texts, Shafan provides a modern digital interface for deep study of Hebrew Scriptures.

This project combines digital humanities, computer vision, and AI to transform rare manuscript images and historical texts into a searchable, multilingual web application.

## What Makes This Special

- **Comprehensive Hebrew Bible**: Complete Tanakh and Besorah in one unified platform
- **Multiple Besorah Translations**: Features both Hutter (1599-1602) and Delitzsch Hebrew New Testament versions
- **Historic Digitization**: First-ever digital edition of Hutter's 426-year-old manuscript, previously only in physical libraries
- **AI-Powered Transcription**: Uses Claude AI to accurately transcribe complex Hebrew text with nikud from manuscript images
- **Modern Web Interface**: Clean, responsive UI with Hebrew (RTL), Spanish, and English support
- **Fully Open Source**: MIT licensed, complete processing pipeline and data included

## Project Structure

```
shafan/
├── scripts/           # Complete processing pipeline
│   ├── pdf/          # Download historical PDFs
│   ├── images/       # Convert to optimized images
│   ├── hebrew_images/# Extract Hebrew text columns
│   └── text/         # AI transcription to JSON
├── frontend/         # Next.js web application
├── output/           # Final structured JSON (source of truth)
├── data/             # Source materials & references
└── models/           # ML models (if training custom OCR)
```

## Quick Start

### Prerequisites

- **Python 3.12** (managed via mise)
- **Node.js 20** (managed via mise)
- **aria2** (for downloading PDFs): `brew install aria2`
- **poppler** (for PDF conversion): `brew install poppler`

### Installation

```bash
# Clone the repository
git clone https://github.com/edyhvh/shafan.git
cd shafan

# One-command setup (installs dependencies, creates virtual environment)
python setup.py

# Run the web interface
cd frontend
npm install
npm run dev
```

Visit [http://localhost:3001](http://localhost:3001) to browse the Hebrew texts!

## Data Sources

### Tanakh (Hebrew Bible)

- Morphological data from [Open Scriptures morphhb](https://github.com/openscriptures/morphhb)
- Complete Hebrew Bible with lemma and morphology analysis
- Masoretic text with vowel points (nikud) and cantillation marks

### Besorah - Hutter Edition (1599-1602)

- Elias Hutter's Hebrew New Testament from his Polyglot Bible
- Original manuscript PDFs from historical archives
- AI-transcribed using Claude with manual verification
- First digital edition of this historic translation
- Manuscript images hosted on [Hugging Face](https://huggingface.co/datasets/edyhvh/hutter)

### Besorah - Delitzsch Edition (19th century)

- Franz Delitzsch's scholarly Hebrew New Testament translation
- Widely regarded as the standard modern Hebrew New Testament
- Data from [hebrew-bible.github.io](https://github.com/hebrew-bible/hebrew-bible.github.io)

### Versification Mapping

- [Copenhagen Alliance](https://github.com/Copenhagen-Alliance/copenhagen-alliance.github.io) standardized mappings
- Handles Hebrew (Masoretic) ↔ English (KJV) verse number differences
- Critical for books like Psalms where numbering systems diverge

## Processing Pipeline

The project follows a complete pipeline to convert historical PDF manuscripts into a modern digital edition:

1. **Download PDFs** → Fetch source PDFs from Hutter Polyglot Bible archive
2. **Convert to Images** → Transform PDF pages to OCR-optimized images
3. **Extract Hebrew Columns** → Isolate Hebrew text columns from manuscript pages
4. **AI Transcription** → Use Claude AI to transcribe Hebrew with nikud into structured JSON
5. **Web Interface** → Browse and study the texts in a modern, responsive web app

### Pipeline Commands

```bash
# Step 1: Download source PDFs
python -m scripts.pdf all

# Step 2: Convert PDFs to images
python -m scripts.images all

# Step 3: Extract Hebrew text columns
python scripts/hebrew_images/main.py all

# Step 4: AI transcription (requires API key)
export ANTHROPIC_API_KEY="your-api-key"
python -m scripts.text --all

# Step 5: Run frontend
cd frontend
npm run dev
```

## Detailed Documentation

Each component has its own comprehensive README:

- **[scripts/pdf/README.md](scripts/pdf/README.md)** — Downloading historical manuscript PDFs
- **[scripts/images/README.md](scripts/images/README.md)** — Converting PDFs to optimized images
- **[scripts/hebrew_images/README.md](scripts/hebrew_images/README.md)** — Extracting Hebrew text columns with computer vision
- **[scripts/text/README.md](scripts/text/README.md)** — AI transcription with Claude
- **[frontend/README.md](frontend/README.md)** — Web application setup and features

## Contributing

We welcome contributions! Whether you:

- **Found a transcription error?** Report it or fix it
- **Want to improve the code?** Submit a PR
- **Have UI suggestions?** Open an issue
- **Can help with translations?** We'd love your help

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for detailed guidelines on how to help improve the text, verify corrections against original manuscripts, and contribute code.

## Training Dataset

The extracted Hebrew text images used for AI training and verification are hosted on Hugging Face at [edyhvh/hutter](https://huggingface.co/datasets/edyhvh/hutter) to keep the repository lightweight.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- **Elias Hutter** (1553–1605) — Original translator and printer
- **Open Scriptures** — Hebrew Bible morphological data
- **Copenhagen Alliance** — Versification mapping standards
- **Anthropic Claude** — AI transcription technology
- **Moriah Betzalel and Lena Kamilkov** - Helped me catch and find error patterns when the AI transcribed Hutter's text, this text is not fully corrected yet but it's a good starting point.
- All contributors who help verify and improve the texts

---

<div align="center">

**Built for digital humanities and Biblical scholarship**

[Report an Issue](https://github.com/edyhvh/shafan/issues) · [Request Feature](https://github.com/edyhvh/shafan/issues) · [View Demo](https://shafan.xyz)

</div>
