"""Read a CSV and run every check from a schema against it.

A reader is any function that takes a path and a delimiter and returns
(columns, rows). There are two, one using the standard library and one using
pandas, picked from the READERS registry. Everything else depends only on that
(columns, rows) shape, never on how the file was read, which is the Dependency
Inversion part: swapping the engine touches no check.
"""
from __future__ import annotations

import csv
from collections.abc import Callable
from pathlib import Path
from typing import cast

from csv_validator import config
from csv_validator.errors import CsvReadError
from csv_validator.report import Failure
from csv_validator.schema import load_schema


def read_csv(
    path: str | Path, delimiter: str = config.DEFAULT_DELIMITER
) -> tuple[list[str], list[dict[str, str]]]:
    """Read with the standard library `csv` module."""
    file = Path(path)
    if not file.is_file():
        raise CsvReadError(f"CSV file not found: {file}")
    try:
        # utf-8-sig drops a byte-order mark if Excel added one.
        with file.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            columns = list(reader.fieldnames or [])
            rows = [dict(row) for row in reader]
    except (OSError, csv.Error, UnicodeDecodeError) as exc:
        raise CsvReadError(f"Could not read {file}: {exc}") from exc
    # DictReader yields str values for a well-formed CSV.
    return columns, cast("list[dict[str, str]]", rows)


def read_pandas(
    path: str | Path, delimiter: str = config.DEFAULT_DELIMITER
) -> tuple[list[str], list[dict[str, str]]]:
    """Read with pandas (optional). Returns the same (columns, rows) shape as read_csv."""
    file = Path(path)
    if not file.is_file():
        raise CsvReadError(f"CSV file not found: {file}")
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("the pandas engine needs pandas installed: pip install pandas") from exc
    try:
        # dtype=str and keep_default_na=False keep every cell as raw text, so pandas
        # does not guess types or turn blanks into NaN and hide the problems we look for.
        frame = pd.read_csv(file, sep=delimiter, dtype=str, keep_default_na=False)
    except Exception as exc:  # pandas raises a wide range of error types
        raise CsvReadError(f"Could not read {file}: {exc}") from exc
    columns = list(frame.columns)
    rows: list[dict[str, str]] = frame.to_dict(orient="records")
    return columns, rows


# Registry of readers, same idea as the CHECKS registry: add an engine by adding
# a function and one line here.
READERS: dict[str, Callable[[str | Path, str], tuple[list[str], list[dict[str, str]]]]] = {
    "csv": read_csv,
    "pandas": read_pandas,
}


def validate(
    csv_path: str | Path,
    schema_path: str | Path,
    *,
    engine: str = config.DEFAULT_ENGINE,
    delimiter: str = config.DEFAULT_DELIMITER,
) -> list[Failure]:
    """Validate the CSV against the schema and return every failure found.

    An empty list means it passed. Raises SchemaError, CsvReadError, or ImportError
    (pandas engine unavailable) if the tool cannot run at all.
    """
    checks = load_schema(schema_path)
    columns, rows = READERS[engine](csv_path, delimiter)
    failures: list[Failure] = []
    for check in checks:
        failures.extend(check.run(columns, rows))
    return failures
