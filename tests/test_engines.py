"""The engines and the engine registry."""
from csv_validator.engines import get_engine, known_engines
from csv_validator.engines.csv_engine import read_csv


def test_read_csv_returns_header_and_rows(data_dir):
    """read_csv returns the header names and the rows keyed by column."""
    columns, rows = read_csv(data_dir / "valid.csv")
    assert columns == ["name", "position", "age", "salary", "active"]
    assert len(rows) == 2
    assert rows[0]["name"] == "Joe"


def test_engines_are_registered():
    """Both engines register themselves when the package is imported."""
    assert set(known_engines()) == {"csv", "pandas"}


def test_get_engine_resolves_known_and_unknown():
    """get_engine returns the reader for a known name and None for an unknown one."""
    assert get_engine("csv") is read_csv
    assert get_engine("nope") is None
