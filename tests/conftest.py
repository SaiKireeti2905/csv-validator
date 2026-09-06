"""Shared pytest fixtures for the test suite."""
from pathlib import Path

import pytest


@pytest.fixture
def data_dir() -> Path:
    """Directory holding the four sample CSVs and my_schema.json."""
    return Path(__file__).parent / "data"
