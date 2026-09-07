"""The standard-library CSV engine (engine name: 'csv')."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import cast

from csv_validator import config
from csv_validator.engines.base import register
from csv_validator.errors import CsvReadError


@register("csv")
def read_csv(
    path: Path, delimiter: str = config.DEFAULT_DELIMITER
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
