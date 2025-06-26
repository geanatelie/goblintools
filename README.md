
# GoblinTools

**GoblinTools** is a Python library designed for text extraction, archive handling, OCR integration, and text cleaning. It supports a wide range of file formats and offers both local and cloud-based OCR options.

---

## Installation

```bash
pip install goblintools
```

Note:
- GoblinTools requires Python 3.7 or newer.
- For OCR support, you must install Tesseract OCR separately [https://github.com/tesseract-ocr/tesseract].
- For AWS Textract support, valid AWS credentials are required.

---

### System Requirements

Some archive formats such as `.rar`, `.7z`, `.tar`, and others depend on external system tools to be extracted properly. These tools are not Python packages and must be installed manually. `patoolib` (used by GoblinTools) relies on them.

#### Debian/Ubuntu

```bash
sudo apt install unrar p7zip-full p7zip-rar
```

#### Arch Linux

```bash
sudo pacman -S unrar p7zip
```

#### macOS (Homebrew)

```bash
brew install unrar p7zip
```

---

## Key Features

- Broad File Support: Extract text from over 20 document, spreadsheet, and presentation formats.
- Comprehensive Archive Handling: Supports `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, and many more.
- Flexible OCR Integration: Use Tesseract locally or integrate with AWS Textract.
- Advanced Text Cleaning: Accent removal, lowercasing, and intelligent stopword filtering (Portuguese support).
- Efficient Batch Processing: Handle multiple archives in parallel.
- Robust File Management: Move, delete, and organize files/directories with ease.

---

## Usage

### Text Extraction

```python
from goblintools import TextExtractor
import os

extractor = TextExtractor()
file_path = "example.pdf"

if os.path.exists(file_path):
    text = extractor.extract_from_file(file_path)
    if text:
        print("Successfully extracted text:")
        print(text[:200] + "...")
    else:
        print(f"Could not extract text from {file_path}.")
else:
    print(f"Error: File not found at {file_path}")
```

#### With OCR Enabled

```python
extractor_with_ocr = TextExtractor(ocr_handler=True)
scanned_pdf_path = "scanned_document.pdf"

if os.path.exists(scanned_pdf_path):
    scanned_text = extractor_with_ocr.extract_from_file(scanned_pdf_path)
    if scanned_text:
        print("\nSuccessfully extracted text from scanned document (with OCR):")
        print(scanned_text[:200] + "...")
    else:
        print(f"Could not extract text from {scanned_pdf_path} (OCR might be needed).")
else:
    print(f"\nSkipping scanned document example: File not found at {scanned_pdf_path}")
```

#### Extracting All Text from a Folder

```python
folder_path = "/path/to/your/folder"
text_from_folder = extractor.extract_from_folder(folder_path)
print(f"\nExtracted text from folder: {text_from_folder[:500]}...")
```

---

### File Management & Archive Extraction

```python
from goblintools import FileManager
import os

output_folder = "extracted_content"
os.makedirs(output_folder, exist_ok=True)

# Recursive extraction
FileManager.extract_files_recursive("archive.zip", output_folder)

# Batch extraction
FileManager.batch_extract(["a.zip", "b.rar"], output_folder)
```

---

### Text Cleaning

```python
from goblintools import TextCleaner

cleaner = TextCleaner()
raw_text = "Isso é um Teste com Acentos. E algumas palavras, como 'e', 'a', 'o', são stopwords."

print(f"Original text: {raw_text}")

clean_text_basic = cleaner.clean_text(raw_text)
print(f"Basic cleaning: {clean_text_basic}")

clean_text_full = cleaner.clean_text(raw_text, lowercase=True, remove_stopwords=True)
print(f"Full cleaning: {clean_text_full}")
```

---

### OCR with AWS Textract

```python
from goblintools import TextExtractor

extractor = TextExtractor(
    ocr_handler=True,
    use_aws=True,
    aws_access_key="your-aws-access-key-here",
    aws_secret_key="your-aws-secret-key-here",
    aws_region="us-east-1"
)

# Example:
text = extractor.extract_from_file("aws_scanned_document.pdf")
```

---

## Supported Formats

### Documents
`.pdf`, `.doc`, `.docx`, `.odt`, `.rtf`, `.txt`, `.csv`, `.xml`, `.html`

### Spreadsheets  
`.xlsx`, `.xls`, `.ods`, `.dbf`

### Presentations  
`.pptx`

### Archives  
`.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`, `.iso`, `.deb`, `.rpm`, `.jar`, `.war`, `.ear`, `.cbz`, `.cbr`, `.cb7`, `.tgz`, `.txz`, `.cbt`, `.udf`, `.ace`, `.cba`, `.arj`, `.cab`, `.chm`, `.cpio`, `.dms`, `.lha`, `.lzh`, `.lzma`, `.lzo`, `.xz`, `.zst`, `.zoo`, `.adf`, `.alz`, `.arc`, `.shn`, `.rz`, `.lrz`, `.a`, `.Z`

---

## File Management Utilities

### Move a File

```python
from goblintools import FileManager

source = "path/to/source.txt"
destination = "path/to/destination.txt"

FileManager.move_file(source, destination)
```

### Delete a Folder and Its Contents

```python
FileManager.delete_folder("temp_folder")
```

### Delete a File if It's Empty

```python
FileManager.delete_if_empty("empty_file.txt")
```

### Normalize and Move All Files in a Directory

Moves all files to the root of the folder, renames to avoid conflicts, and removes empty subfolders.

```python
FileManager.move_files("path/to/root_folder")
```


## Text Extraction Utilities

### Verify  if a PDF file needs OCR treatment

```python
if extractor.pdf_needs_ocr("scanned_document.pdf")
    print("Needs OCR!")
```
---

## License

MIT License
