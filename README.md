
# GoblinTools

**GoblinTools** is a Python library designed for text extraction, archive handling, OCR integration, and text cleaning. It supports a wide range of file formats and offers both local and cloud-based OCR options.

---

## Overview

GoblinTools provides a unified toolkit for extracting text from documents (PDF, DOCX, XLSX, etc.), handling archives (ZIP, RAR, 7z, 30+ formats), and cleaning text with Brazilian Portuguese support. OCR can use local Tesseract or AWS Textract. When AWS credentials are missing, the library falls back to local Tesseract with a warning.

### Architecture

```
goblintools/
├── parser.py        # TextExtractor - main extraction, format parsers
├── file_handling.py # FileManager, ArchiveHandler, FileValidator
├── text_cleaner.py  # TextCleaner - accent removal, stopwords
├── config.py        # GoblinConfig, OCRConfig
├── ocr_parser.py    # OCRProcessor - Tesseract / AWS Textract
└── retry.py         # retry_with_backoff utility
```

### Processing Flow

1. **Text extraction**: File → parser by extension → extracted text (with `file_path_pwd` tag)
2. **PDF with images**: PyPDF first → OCR fallback if no text
3. **Archive extraction**: Format handler → extract to temp → move with collision avoidance → optionally remove source

---

## Installation

```bash
pip install goblintools
```

## Requirements

- **Python**: 3.7 or newer
- **Tesseract OCR**: Required for local OCR support ([Installation Guide](https://github.com/tesseract-ocr/tesseract))
  - **Portuguese Language Pack**: Install `tesseract-ocr-por` for Portuguese text recognition
- **AWS Credentials**: Required for AWS Textract cloud OCR

---

## System Dependencies

### Archive Support
For complete archive format support, install these system tools (required by `patoolib`):

| OS | Command |
|----|---------|
| **Debian/Ubuntu** | `sudo apt install unrar p7zip-full p7zip-rar` |
| **Arch Linux** | `sudo pacman -S unrar p7zip` |
| **macOS** | `brew install unrar p7zip` |

### Tesseract OCR with Portuguese Support

| OS | Command |
|----|---------|
| **Debian/Ubuntu** | `sudo apt install tesseract-ocr tesseract-ocr-por` |
| **Arch Linux** | `sudo pacman -S tesseract tesseract-data-por` |
| **macOS** | `brew install tesseract tesseract-lang` |
| **Windows** | Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and select Portuguese during installation |

---

## Key Features

- **Broad File Support**: Extract text from 20+ document, spreadsheet, and presentation formats
- **Archive Handling**: Supports `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, and 30+ more formats
- **OCR Integration**: Local Tesseract or cloud AWS Textract support
- **Text Cleaning**: Accent removal, case normalization, stopword filtering (Brazilian Portuguese support)
- **Portuguese OCR**: Optimized for Brazilian Portuguese documents with Tesseract
- **Batch Processing**: Parallel archive extraction
- **File Management**: Comprehensive file/directory operations
- **File Path Tagging**: Automatically includes file path metadata in extracted text

---

## Quick Start

### Basic Text Extraction

```python
from goblintools import TextExtractor

extractor = TextExtractor()
text = extractor.extract_from_file("document.pdf")
print(text[:200] + "..." if text else "No text extracted")

# Output includes file path tag:
# file_path_pwd:"document.pdf"
# [extracted text content...]
```

### OCR-Enabled Extraction

```python
# Local OCR with Tesseract
extractor = TextExtractor(ocr_handler=True)
text = extractor.extract_from_file("scanned_document.pdf")
# Output: file_path_pwd:"scanned_document.pdf" [OCR extracted text]

# AWS Textract OCR
extractor = TextExtractor(
    ocr_handler=True,
    use_aws=True,
    aws_access_key="your-key",
    aws_secret_key="your-secret",
    aws_region="us-east-1"
)
text = extractor.extract_from_file("document.pdf")
# Output: file_path_pwd:"document.pdf" [AWS Textract extracted text]
```

### Configuration Management

```python
from goblintools import GoblinConfig, OCRConfig, TextExtractor

# Create config programmatically
config = GoblinConfig(
    max_file_size=50 * 1024 * 1024,  # 50MB limit
    ocr=OCRConfig(
        use_aws=True,
        aws_access_key="your-key",
        aws_secret_key="your-secret",
        aws_region="us-west-2",
        tesseract_lang="por"  # Portuguese OCR (default)
    )
)

# Use config with extractor
extractor = TextExtractor(ocr_handler=True, config=config)

# Save config to file
config.to_file("goblin_config.json")

# Load config from file
config = GoblinConfig.from_file("goblin_config.json")
extractor = TextExtractor(ocr_handler=True, config=config)
```

**Example config file (`goblin_config.json`):**
```json
{
  "max_file_size": 52428800,
  "ocr": {
    "use_aws": false,
    "aws_access_key": null,
    "aws_secret_key": null,
    "aws_region": "us-east-1",
    "tesseract_lang": "por"
  }
}
```

**Supported Tesseract Languages:**
- `"por"` - Portuguese (default)
- `"eng"` - English
- `"spa"` - Spanish
- `"por+eng"` - Portuguese + English (multi-language)
- See [Tesseract documentation](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html) for more languages

### Advanced Features

```python
# Extract from entire folder (respects max_file_size limit)
# Each file's text is prefixed with file_path_pwd tag
text = extractor.extract_from_folder("/path/to/documents")
# Output: file_path_pwd:"/path/to/documents/file1.pdf" [text] file_path_pwd:"/path/to/documents/file2.docx" [text] ...

# Check if PDF needs OCR
if extractor.pdf_needs_ocr("document.pdf"):
    print("This PDF requires OCR processing")

# Validate installation
status = extractor.validate_installation()
print(f"Tesseract available: {status['tesseract']}")
if 'aws_textract' in status:
    print(f"AWS Textract available: {status['aws_textract']}")

# Add custom file parser
def custom_parser(file_path):
    # Your custom extraction logic
    return "extracted text"

extractor.add_parser('.custom', custom_parser)
text = extractor.extract_from_file("file.custom")
# Output: file_path_pwd:"file.custom" extracted text

# Direct OCR processing with config
from goblintools import OCRProcessor, OCRConfig

ocr_config = OCRConfig(use_aws=True, aws_access_key="key", aws_secret_key="secret")
ocr = OCRProcessor(ocr_config)
text = ocr.extract_text_from_pdf("scanned.pdf")
```

---

### File Path Tagging

All extracted text automatically includes the file path as metadata using the `file_path_pwd` tag:

```python
# Single file extraction
text = extractor.extract_from_file("document.pdf")
# Output format:
# file_path_pwd:"document.pdf"
# [extracted text content]

# Folder extraction
text = extractor.extract_from_folder("/path/to/documents")
# Output format:
# file_path_pwd:"/path/to/documents/file1.pdf" [text] file_path_pwd:"/path/to/documents/file2.docx" [text] ...

# Example output:
# file_path_pwd:"/docs/report.pdf" This is the content of the PDF file. file_path_pwd:"/docs/data.xlsx" Spreadsheet data here.
```

**File Path Tagging Features:**
- **Automatic tagging**: Every extracted text includes the source file path
- **Consistent format**: `file_path_pwd:"path/to/file"` prefix for easy parsing
- **String output**: Simple string format, easy to process and search
- **Source tracking**: Always know which file the text came from

---

### Archive Extraction

```python
from goblintools import FileManager, FileValidator, ArchiveHandler

# Single archive extraction (handles nested archives)
FileManager.extract_files_recursive("archive.zip", "output_folder")

# Parallel batch extraction
results = FileManager.batch_extract(["file1.zip", "file2.rar"], "output_folder")
print(f"Extraction results: {results}")  # [True, False, ...]

# Batch extraction with progress tracking
def progress_callback(current, total):
    print(f"Progress: {current}/{total} ({current/total*100:.1f}%)")

results = FileManager.batch_extract(
    ["file1.zip", "file2.rar", "file3.7z"],
    "output_folder",
    progress_callback=progress_callback
)

# File validation
if FileValidator.is_archive("file.zip"):
    print("File is a supported archive")

if FileValidator.is_empty("file.txt"):
    print("File is empty")

# Direct archive handling (remove_source=True deletes archive after extraction)
ArchiveHandler.extract("archive.7z", "output")
ArchiveHandler.extract("archive.7z", "output", remove_source=False)  # Keep source

# Add custom archive format
ArchiveHandler.add_format('.custom', lambda f, d: custom_extract(f, d))

# File operations with conflict resolution
FileManager.move_file("source.txt", "destination.txt")  # Auto-renames if exists
FileManager.delete_folder("temp_folder")
FileManager.move_files("folder_path")  # Flatten + normalize names
```

---

### Text Cleaning

```python
from goblintools import TextCleaner

# Default Portuguese stopwords
cleaner = TextCleaner()
raw_text = "Isso é um Teste com Acentos!"

# Basic cleaning (remove accents)
clean = cleaner.clean_text(raw_text)
# Output: "Isso e um Teste com Acentos!"

# Full cleaning (lowercase + remove stopwords)
clean = cleaner.clean_text(raw_text, lowercase=True, remove_stopwords=True)
# Output: "teste acentos"

# Custom stopwords
custom_cleaner = TextCleaner(custom_stopwords=['custom', 'words'])
clean = custom_cleaner.remove_stopwords("custom text with words")
# Output: "text with"

# Portuguese text processing example
portuguese_text = "Este é um documento em português com acentuação!"
clean_pt = cleaner.clean_text(portuguese_text, lowercase=True, remove_stopwords=True)
# Output: "documento portugues acentuacao"
```

---

## Brazilian Portuguese Support

GoblinTools is optimized for Brazilian Portuguese users:

```python
from goblintools import TextExtractor, TextCleaner, OCRConfig

# Portuguese OCR configuration
config = OCRConfig(
    tesseract_lang="por",  # Portuguese language
    use_aws=False  # Use local Tesseract
)

# Extract Portuguese documents
extractor = TextExtractor(ocr_handler=True, config=config)
text = extractor.extract_from_file("documento_brasileiro.pdf")

# Clean Portuguese text (removes Portuguese stopwords)
cleaner = TextCleaner()  # Uses Portuguese stopwords by default
clean_text = cleaner.clean_text(
    "Este é um texto em português com acentos!",
    lowercase=True,
    remove_stopwords=True
)
print(clean_text)  # Output: "texto portugues acentos"

# Multi-language OCR (Portuguese + English)
multi_config = OCRConfig(tesseract_lang="por+eng")
extractor_multi = TextExtractor(ocr_handler=True, config=multi_config)
```

**Portuguese Features:**
- Default Portuguese stopwords (400+ words)
- Portuguese Tesseract OCR support
- Accent removal with `unidecode`
- Brazilian document format support

---

## Supported Formats

### Documents
`.pdf`, `.docx`, `.odt`, `.rtf`, `.txt`, `.csv`, `.xml`, `.html`

### Spreadsheets
`.xlsx`, `.xls`, `.ods`, `.dbf`

### Presentations
`.pptx`

### Archives
`.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`, `.iso`, `.deb`, `.rpm`, `.jar`, `.war`, `.ear`, `.cbz`, `.cbr`, `.cb7`, `.tgz`, `.txz`, `.cbt`, `.udf`, `.ace`, `.cba`, `.arj`, `.cab`, `.chm`, `.cpio`, `.dms`, `.lha`, `.lzh`, `.lzma`, `.lzo`, `.xz`, `.zst`, `.zoo`, `.adf`, `.alz`, `.arc`, `.shn`, `.rz`, `.lrz`, `.a`, `.Z`

---

## API Reference

### TextExtractor
- `__init__(ocr_handler=False, use_aws=False, aws_access_key=None, aws_secret_key=None, aws_region='us-east-1', config=None)` - Initialize extractor with OCR options or config
- `extract_from_file(file_path)` - Extract text from single file. Returns `str` with `file_path_pwd:"path"` tag prefix
- `extract_from_folder(folder_path)` - Extract text from all files in folder (recursively). Returns `str` with `file_path_pwd` tags for each file
- `pdf_needs_ocr(pdf_path)` - Check if PDF requires OCR processing
- `add_parser(extension, parser_func)` - Add custom parser for file extension
- `validate_installation()` - Check if dependencies are properly installed

**Output Format:**
- Always returns `str` (string) with extracted text
- Each file's text is prefixed with `file_path_pwd:"file/path"` tag
- Multiple files are concatenated with spaces between them

### FileManager
- `extract_files_recursive(archive_path, output_path)` - Extract archive recursively
- `batch_extract(archive_list, output_path, progress_callback=None)` - Extract multiple archives with optional progress tracking
- `move_file(source, destination)` - Move/rename file with conflict resolution and type safety
- `delete_folder(folder_path)` - Delete folder and contents
- `delete_if_empty(file_path)` - Delete file if empty
- `move_files(folder_path)` - Flatten directory structure and normalize filenames

### FileValidator
- `is_empty(file_path)` - Check if file is empty
- `is_archive(file_path)` - Check if file is a supported archive format

### ArchiveHandler
- `extract(file_path, destination, remove_source=True)` - Extract archive with collision avoidance. When `remove_source=True` (default), deletes the archive after extraction; set to `False` to keep it.
- `add_format(extension, handler)` - Add support for new archive formats

### TextCleaner
- `__init__(custom_stopwords=None)` - Initialize with custom stopwords (defaults to Portuguese)
- `clean_text(text, lowercase=False, remove_stopwords=False)` - Clean and normalize text
- `remove_stopwords(text)` - Remove stopwords from text

### OCRProcessor
- `__init__(config)` - Initialize OCR processor with OCRConfig
- `extract_text_from_pdf(pdf_path)` - Extract text from PDF using OCR

### GoblinConfig
- `__init__(max_file_size=104857600, ocr=None)` - Initialize configuration
- `from_file(config_path)` - Load configuration from JSON file
- `to_file(config_path)` - Save configuration to JSON file
- `default()` - Create default configuration

### OCRConfig
- `__init__(use_aws=False, aws_access_key=None, aws_secret_key=None, aws_region='us-east-1', tesseract_lang='por')` - Initialize OCR configuration
  - `tesseract_lang`: Language for Tesseract OCR (`'por'` for Portuguese, `'eng'` for English, `'por+eng'` for both)
---

## Scripts de Teste

Run tests locally with pytest:

```bash
# Activate venv first
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows

# Run all tests
pytest tests/ -v

# Or
python -m pytest tests/ -v
```

---

## Estrutura do Projeto

```
goblintools/
├── goblintools/           # Package
│   ├── __init__.py
│   ├── parser.py          # TextExtractor
│   ├── file_handling.py   # FileManager, ArchiveHandler, FileValidator
│   ├── text_cleaner.py    # TextCleaner
│   ├── config.py          # GoblinConfig, OCRConfig
│   ├── ocr_parser.py      # OCRProcessor
│   └── retry.py           # retry_with_backoff
├── tests/                 # Pytest tests
│   ├── conftest.py
│   └── test_*.py
├── pytest.ini
├── pyproject.toml
└── requirements.txt
```

---

## Troubleshooting

### "Tesseract is not installed or it's not in your PATH"

Install Tesseract and the Portuguese language pack. See [System Dependencies](#system-dependencies) for OS-specific commands.

### "AWS credentials not found; falling back to local Tesseract OCR"

You set `use_aws=True` but did not provide `aws_access_key` and `aws_secret_key` in `OCRConfig`. The library falls back to local Tesseract. To use AWS Textract, pass credentials explicitly in config.

### "No parser available for file extension"

The file format is not supported. Use `extractor.add_parser('.ext', your_parser_func)` to add a custom parser.

### Archive extraction fails for RAR/7z

Install system tools: `unrar` and `p7zip`. See [Archive Support](#archive-support).

---

## Escopo e Limites

- **In scope**: Text extraction from documents, spreadsheets, presentations; archive handling; OCR (Tesseract, AWS Textract); text cleaning (Portuguese-focused); file operations.
- **Out of scope**: Real-time streaming, document conversion to other formats, indexing/search, web scraping. OCR requires Tesseract (local) or AWS credentials (cloud).

---

## License

MIT License
