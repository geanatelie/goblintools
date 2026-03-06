"""Tests for OCRProcessor (with mocked Tesseract/AWS)."""
import pytest
from unittest.mock import patch, MagicMock

from goblintools import OCRConfig
from goblintools.ocr_parser import OCRProcessor


def test_ocr_processor_fallback_when_aws_creds_missing(caplog):
    """Test that OCRProcessor falls back to local when use_aws=True but credentials missing."""
    config = OCRConfig(use_aws=True, aws_access_key=None, aws_secret_key=None)
    processor = OCRProcessor(config)

    assert processor.use_aws is False
    assert "falling back to local" in caplog.text.lower() or "credentials not found" in caplog.text.lower()


def test_ocr_processor_uses_aws_when_creds_provided():
    """Test that OCRProcessor uses AWS when credentials are provided."""
    config = OCRConfig(
        use_aws=True,
        aws_access_key="test-key",
        aws_secret_key="test-secret"
    )
    processor = OCRProcessor(config)
    assert processor.use_aws is True


def test_ocr_processor_local_by_default():
    """Test that OCRProcessor uses local when use_aws=False."""
    config = OCRConfig(use_aws=False)
    processor = OCRProcessor(config)
    assert processor.use_aws is False
