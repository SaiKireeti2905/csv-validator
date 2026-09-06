"""Read a CSV and run every check from a schema against it.

A reader is any function that takes a path and returns (columns, rows). There are
two, one using the standard library and one using pandas, and they are picked from
the READERS registry. The rest of the tool depends only on that (columns, rows)
shape, never on how the file was read, which is the Dependency Inversion part:
swapping the engine touches no check.
"""
from __future__ import annotations

import csv
from collections.abc import Callable
from pathlib import Path

from csv_validator import config
from csv_validator.schema import load_schema

# A reader turns a file path into a header plus rows keyed by column name.
Reader = Callable[["str | Path"], "tuple[list[str], list[dict[str, str]]]"]


def read_csv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read with the standard library `csv` module."""
    file = Path(path)
    if not file.is_file():
        raise FileNotFoundError(f"CSV file not found: {file}")
    # utf-8-sig drops a byte-order mark if Excel added one.
    with file.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    return columns, rows


def read_pandas(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read with pandas (optional). Returns the same (columns, rows) shape as read_csv."""
    file = Path(path)
    if not file.is_file():
        raise FileNotFoundError(f"CSV file not found: {file}")
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("the pandas engine needs pandas installed: pip install pandas") from exc
    # dtype=str and keep_default_na=False keep every cell as raw text, so pandas
    # does not guess types or turn blanks into NaN and hide the problems we look for.
    frame = pd.read_csv(file, dtype=str, keep_default_na=False)
    columns = list(frame.columns)
    rows: list[dict[str, str]] = frame.to_dict(orient="records")
    return columns, rows


# Registry of readers, same idea as the CHECKS registry: add an engine by adding
# a function and one line here.
READERS: dict[str, Reader] = {
    "csv": read_csv,
    "pandas": read_pandas,
}


def validate(
    csv_path: str | Path, schema_path: str | Path, engine: str = config.DEFAULT_ENGINE
) -> list[str]:
    """Validate the CSV against the schema and return every error message found.

    An empty list means the file passed. Raises SchemaError, FileNotFoundError, or
    ImportError (pandas engine unavailable) if the tool cannot run at all.
    """
    checks = load_schema(schema_path)
    columns, rows = READERS[engine](csv_path)
    errors: list[str] = []
    for check in checks:
        errors.extend(check.run(columns, rows))
    return errors
