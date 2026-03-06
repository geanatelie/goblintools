"""Pytest configuration and shared fixtures."""
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_txt_file():
    """Create a temporary TXT file with sample content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Hello world. This is a test file.\nSecond line.")
        path = f.name
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file with sample content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write("col1,col2,col3\nval1,val2,val3\na,b,c")
        path = f.name
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
