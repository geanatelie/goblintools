"""Tests for TextExtractor."""
import logging
import os
import tempfile

import pytest
from pypdf import PdfWriter

from goblintools import TextExtractor
from goblintools.file_handling import FileValidator


def test_extract_from_file_txt(sample_txt_file):
    """Test extraction from TXT file."""
    extractor = TextExtractor()
    result = extractor.extract_from_file(sample_txt_file)
    assert "file_path_pwd:" in result
    assert "Hello world" in result or "test file" in result


def test_extract_from_file_csv(sample_csv_file):
    """Test extraction from CSV file."""
    extractor = TextExtractor()
    result = extractor.extract_from_file(sample_csv_file)
    assert "file_path_pwd:" in result
    assert "col1" in result or "val1" in result


def test_extract_from_file_not_found():
    """Test extraction from non-existent file."""
    extractor = TextExtractor()
    result = extractor.extract_from_file("/nonexistent/file.txt")
    assert result == ""


def test_extract_from_file_unsupported_format():
    """Test extraction from unsupported format returns empty."""
    with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
        path = f.name
    try:
        extractor = TextExtractor()
        result = extractor.extract_from_file(path)
        assert result == ""
    finally:
        os.unlink(path)


def test_add_parser():
    """Test custom parser registration."""
    extractor = TextExtractor()

    def custom_parser(path):
        return "custom content"

    extractor.add_parser('.custom', custom_parser)

    with tempfile.NamedTemporaryFile(suffix='.custom', delete=False) as f:
        path = f.name
    try:
        result = extractor.extract_from_file(path)
        assert "custom content" in result
        assert "file_path_pwd:" in result
    finally:
        os.unlink(path)


def test_extract_from_file_no_file_path_when_whitespace_only():
    """Corrupt/blank docs may yield only whitespace; do not emit file_path_pwd without real text."""
    extractor = TextExtractor()

    def whitespace_parser(path):
        return "   \n\t  "

    extractor.add_parser('.ws', whitespace_parser)
    with tempfile.NamedTemporaryFile(suffix='.ws', delete=False) as f:
        path = f.name
    try:
        assert extractor.extract_from_file(path) == ""
    finally:
        os.unlink(path)


def test_extract_from_file_extensionless_pdf(caplog):
    """PDF without extension: magic bytes route to PDF parser (not 'no parser' warning)."""
    fd, path = tempfile.mkstemp(suffix="")
    os.close(fd)
    try:
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with open(path, "wb") as f:
            writer.write(f)
        assert FileValidator.detect_extension_from_magic(path) == ".pdf"
        extractor = TextExtractor()
        with caplog.at_level(logging.WARNING):
            result = extractor.extract_from_file(path)
        assert "No parser available" not in caplog.text
        # Blank page yields no extractable text — no file_path_pwd without content
        assert result == ""
    finally:
        os.unlink(path)


def test_extract_from_folder_uses_relative_path():
    """Test that file_path_pwd uses path relative to folder (as inside zip)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        edital_dir = os.path.join(tmpdir, "edital")
        os.makedirs(edital_dir)
        arquivo_path = os.path.join(edital_dir, "arquivo.txt")
        with open(arquivo_path, "w") as f:
            f.write("content from edital/arquivo")
        extractor = TextExtractor()
        result = extractor.extract_from_folder(tmpdir)
        assert 'file_path_pwd:"edital/arquivo.txt"' in result
        assert "content from edital/arquivo" in result


def test_validate_installation():
    """Test validate_installation returns dict with tesseract key."""
    extractor = TextExtractor()
    result = extractor.validate_installation()
    assert isinstance(result, dict)
    assert 'tesseract' in result
    assert result['tesseract'] in (True, False)
