"""Tests for warning suppression via configure() and constructor kwargs."""
import logging

import pytest

from goblintools import FileManager, TextExtractor, configure
from goblintools.log_policy import _set_suppress_warnings, _warnings_suppressed, log_warning


@pytest.fixture(autouse=True)
def reset_suppress_warnings():
    configure(suppress_warnings=False)
    yield
    configure(suppress_warnings=False)


def test_configure_suppress_warnings():
    configure(suppress_warnings=True)
    assert _warnings_suppressed() is True
    configure(suppress_warnings=False)
    assert _warnings_suppressed() is False


def test_log_warning_respects_flag(caplog):
    logger = logging.getLogger("test_log_policy")
    configure(suppress_warnings=True)
    with caplog.at_level(logging.WARNING):
        log_warning(logger, "hidden")
    assert "hidden" not in caplog.text

    configure(suppress_warnings=False)
    with caplog.at_level(logging.WARNING):
        log_warning(logger, "shown")
    assert "shown" in caplog.text


def test_text_extractor_suppress_warnings_kwarg():
    TextExtractor(suppress_warnings=True)
    assert _warnings_suppressed() is True


def test_text_extractor_default_does_not_change_flag():
    _set_suppress_warnings(True)
    TextExtractor()
    assert _warnings_suppressed() is True


def test_file_manager_suppress_warnings():
    FileManager(suppress_warnings=True)
    assert _warnings_suppressed() is True
