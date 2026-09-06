"""The reader and the engine registry."""
import pytest

from csv_validator.validator import READERS, read_csv, validate


def test_read_csv_returns_header_and_rows(data_dir):
    """read_csv returns the header names and the rows keyed by column."""
    columns, rows = read_csv(data_dir / "valid.csv")
    assert columns == ["name", "position", "age", "salary", "active"]
    assert len(rows) == 2
    assert rows[0]["name"] == "Joe"


def test_both_engines_are_registered():
    """The registry exposes both the csv and pandas engines."""
    assert set(READERS) == {"csv", "pandas"}


def test_pandas_engine_agrees_with_csv(data_dir):
    """The pandas engine produces the same errors as the csv engine (skipped if pandas absent)."""
    pytest.importorskip("pandas")
    schema = data_dir / "my_schema.json"
    csv_errors = validate(data_dir / "bad_types.csv", schema, engine="csv")
    pandas_errors = validate(data_dir / "bad_types.csv", schema, engine="pandas")
    assert csv_errors == pandas_errors
    assert csv_errors  # the file does fail, so this is a real comparison
