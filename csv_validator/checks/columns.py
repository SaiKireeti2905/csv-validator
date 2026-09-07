"""columns_check: the file must have exactly the expected columns."""
from __future__ import annotations

from csv_validator.checks.base import Check, register
from csv_validator.errors import SchemaError
from csv_validator.report import Failure


@register("columns_check")
class ColumnsCheck(Check):
    """No missing columns, no extra ones, and no duplicate headers."""

    def __init__(self, params: object) -> None:
        """Validate the params (a list of column names) and store them as expected."""
        if not isinstance(params, list) or not all(isinstance(p, str) for p in params):
            raise SchemaError("columns_check params must be a list of column names")
        self.expected = params

    def run(self, columns: list[str], rows: list[dict[str, str]]) -> list[Failure]:
        """Report missing, unexpected, and duplicate columns in the header."""
        failures: list[Failure] = []
        seen: set[str] = set()
        reported: set[str] = set()
        for name in columns:
            if name in seen and name not in reported:  # report each duplicate once
                failures.append(Failure("columns_check", "duplicate column in file", column=name))
                reported.add(name)
            seen.add(name)
        for missing in sorted(set(self.expected) - set(columns)):
            failures.append(Failure("columns_check", "missing expected column", column=missing))
        for extra in sorted(set(columns) - set(self.expected)):
            failures.append(Failure("columns_check", "unexpected column not in schema", column=extra))
        return failures
