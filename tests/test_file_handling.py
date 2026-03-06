"""Tests for FileValidator, ArchiveHandler, FileManager."""
import os
import tempfile
import zipfile
from pathlib import Path

import pytest
from goblintools import FileValidator, ArchiveHandler, FileManager


def test_file_validator_is_empty():
    """Test is_empty for empty and non-empty files."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        empty_path = f.name
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"content")
        non_empty_path = f.name

    try:
        assert FileValidator.is_empty(empty_path) is True
        assert FileValidator.is_empty(non_empty_path) is False
    finally:
        os.unlink(empty_path)
        os.unlink(non_empty_path)


def test_file_validator_is_archive():
    """Test is_archive for zip files."""
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
        zip_path = f.name
    try:
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("test.txt", "content")
        assert FileValidator.is_archive(zip_path) is True
    finally:
        os.unlink(zip_path)


def test_file_validator_is_archive_false():
    """Test is_archive returns False for non-archives."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b"not an archive")
        path = f.name
    try:
        assert FileValidator.is_archive(path) is False
    finally:
        os.unlink(path)


def test_archive_handler_extract_zip(temp_dir):
    """Test ArchiveHandler.extract for zip file (default: remove source)."""
    zip_path = os.path.join(temp_dir, "test.zip")
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("inner.txt", "hello")

    dest = os.path.join(temp_dir, "extracted")
    os.makedirs(dest, exist_ok=True)

    result = ArchiveHandler.extract(zip_path, dest)
    assert result is True
    assert not os.path.exists(zip_path)  # Source removed by default
    extracted_file = os.path.join(dest, "inner.txt")
    assert os.path.exists(extracted_file)
    with open(extracted_file) as f:
        assert f.read() == "hello"


def test_archive_handler_extract_keep_source(temp_dir):
    """Test ArchiveHandler.extract with remove_source=False keeps archive."""
    zip_path = os.path.join(temp_dir, "keep.zip")
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("data.txt", "content")

    dest = os.path.join(temp_dir, "out")
    os.makedirs(dest, exist_ok=True)

    result = ArchiveHandler.extract(zip_path, dest, remove_source=False)
    assert result is True
    assert os.path.exists(zip_path)  # Source kept
    assert os.path.exists(os.path.join(dest, "data.txt"))


def test_file_manager_delete_if_empty():
    """Test delete_if_empty."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = f.name
    try:
        assert FileManager.delete_if_empty(path) is True
        assert not os.path.exists(path)
    except Exception:
        if os.path.exists(path):
            os.unlink(path)
        raise
