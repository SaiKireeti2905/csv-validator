"""The optional pandas engine (engine name: 'pandas').

Same (columns, rows) shape as the csv engine, so nothing downstream changes when
you switch engines. pandas is imported lazily, so it stays optional.
"""
from __future__ import annotations

from pathlib import Path

from csv_validator import config
from csv_validator.engines.base import register
from csv_validator.errors import CsvReadError


@register("pandas")
def read_pandas(
    path: Path, delimiter: str = config.DEFAULT_DELIMITER
) -> tuple[list[str], list[dict[str, str]]]:
    """Read with pandas. Returns the same (columns, rows) shape as read_csv."""
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
