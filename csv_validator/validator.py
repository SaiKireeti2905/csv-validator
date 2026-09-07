"""Orchestrate a validation: load the schema, read the file with the chosen
engine, run every check, and collect the failures.

This layer depends only on the `(columns, rows)` shape a reader returns and on
the `Check` interface, never on a specific engine or check. Swapping the engine
or adding a check does not touch this file.
"""
from __future__ import annotations

from pathlib import Path

from csv_validator import config
from csv_validator.engines import get_engine
from csv_validator.errors import CsvReadError
from csv_validator.report import Failure
from csv_validator.schema import load_schema


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
    read = get_engine(engine)
    if read is None:
        raise CsvReadError(f"Unknown engine '{engine}'")
    columns, rows = read(Path(csv_path), delimiter)
    failures: list[Failure] = []
    for check in checks:
        failures.extend(check.run(columns, rows))
    return failures
