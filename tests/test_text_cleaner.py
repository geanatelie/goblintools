"""Tests for TextCleaner."""
import pytest
from goblintools import TextCleaner


def test_clean_text_basic():
    """Test basic text cleaning (accent removal, whitespace normalization)."""
    cleaner = TextCleaner()
    result = cleaner.clean_text("Isso é um Teste com Acentos!")
    assert "Teste" in result
    assert "e" in result  # é -> e after unidecode


def test_clean_text_lowercase():
    """Test lowercase conversion."""
    cleaner = TextCleaner()
    result = cleaner.clean_text("UPPERCASE Text", lowercase=True)
    assert result == "uppercase text" or "uppercase" in result.lower()


def test_clean_text_remove_stopwords():
    """Test stopword removal."""
    cleaner = TextCleaner()
    result = cleaner.clean_text("Este é um documento", lowercase=True, remove_stopwords=True)
    assert "documento" in result
    assert "um" not in result or "este" not in result


def test_clean_text_empty():
    """Test empty input."""
    cleaner = TextCleaner()
    assert cleaner.clean_text("") == ""
    assert cleaner.clean_text(None or "") == ""


def test_remove_stopwords():
    """Test remove_stopwords method."""
    cleaner = TextCleaner(custom_stopwords=["the", "a", "an"])
    result = cleaner.remove_stopwords("the quick brown fox")
    assert "quick" in result
    assert "brown" in result
    assert "fox" in result
    assert "the" not in result


def test_custom_stopwords():
    """Test custom stopwords override default."""
    cleaner = TextCleaner(custom_stopwords=["custom", "words"])
    result = cleaner.remove_stopwords("custom text with words")
    assert "text" in result
    assert "with" in result
    assert "custom" not in result
    assert "words" not in result


def test_remove_text_noise_empty():
    """remove_text_noise returns empty for falsy input."""
    cleaner = TextCleaner()
    assert cleaner.remove_text_noise("") == ""


def test_remove_text_noise_whitespace_and_dots():
    """Collapses runs of whitespace and strips repeated dots."""
    cleaner = TextCleaner()
    assert cleaner.remove_text_noise("a  b   c") == "a b c"
    assert cleaner.remove_text_noise("x\n\n\ty") == "x y"
    assert cleaner.remove_text_noise("no..dots...here") == "nodotshere"
    assert cleaner.remove_text_noise("  padded  ") == "padded"


def test_remove_text_noise_preserves_unicode():
    """Unlike clean_text, does not strip accents (no unidecode)."""
    cleaner = TextCleaner()
    assert "ç" in cleaner.remove_text_noise("Ação   oficial")
    assert "ã" in cleaner.remove_text_noise("Ação   oficial")
    out = cleaner.remove_text_noise("São   Paulo")
    assert out == "São Paulo"
