"""Tests for GoblinConfig and OCRConfig."""
import json
import tempfile
from pathlib import Path

import pytest
from goblintools import GoblinConfig, OCRConfig


def test_ocr_config_defaults():
    """Test OCRConfig default values."""
    config = OCRConfig()
    assert config.use_aws is False
    assert config.aws_access_key is None
    assert config.aws_secret_key is None
    assert config.aws_region == 'us-east-1'
    assert config.tesseract_lang == 'por'


def test_goblin_config_default():
    """Test GoblinConfig.default()."""
    config = GoblinConfig.default()
    assert config.max_file_size == 100 * 1024 * 1024
    assert config.ocr is not None
    assert config.ocr.use_aws is False


def test_config_to_file_and_from_file():
    """Test saving and loading config from JSON file."""
    config = GoblinConfig(max_file_size=50 * 1024 * 1024)
    config.ocr = OCRConfig(use_aws=False, tesseract_lang='eng')

    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        path = f.name

    try:
        config.to_file(path)
        loaded = GoblinConfig.from_file(path)
        assert loaded.max_file_size == config.max_file_size
        assert loaded.ocr.tesseract_lang == 'eng'
    finally:
        Path(path).unlink(missing_ok=True)


def test_config_from_file_not_found():
    """Test from_file raises when file does not exist."""
    with pytest.raises(FileNotFoundError):
        GoblinConfig.from_file("/nonexistent/path/config.json")
