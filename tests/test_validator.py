"""validate(): orchestrating schema + engine + checks."""
import pytest

from csv_validator.report import Failure
from csv_validator.validator import validate


def test_validate_returns_failures(data_dir):
    """A failing file comes back as a list of Failure objects."""
    failures = validate(data_dir / "bad_types.csv", data_dir / "my_schema.json")
    assert failures and all(isinstance(f, Failure) for f in failures)


def test_pandas_engine_agrees_with_csv(data_dir):
    """The pandas engine produces the same failures as the csv engine (skipped if pandas absent)."""
    pytest.importorskip("pandas")
    schema = data_dir / "my_schema.json"
    csv_failures = validate(data_dir / "bad_types.csv", schema, engine="csv")
    pandas_failures = validate(data_dir / "bad_types.csv", schema, engine="pandas")
    assert csv_failures == pandas_failures
    assert csv_failures  # the file does fail, so this is a real comparison
