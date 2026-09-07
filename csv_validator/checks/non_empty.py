"""non_empty_check: the listed columns must have a value in every row."""
from __future__ import annotations

from csv_validator.checks.base import Check, register
from csv_validator.errors import SchemaError
from csv_validator.report import Failure


@register("non_empty_check")
class NonEmptyCheck(Check):
    """The listed columns must have a non-empty value in every row."""

    def __init__(self, params: object) -> None:
        """Validate the params (a list of column names) and store them."""
        if not isinstance(params, list) or not all(isinstance(p, str) for p in params):
            raise SchemaError("non_empty_check params must be a list of column names")
        self.columns = params

    def run(self, columns: list[str], rows: list[dict[str, str]]) -> list[Failure]:
        """Report blank values, and any listed column that is missing from the file."""
        failures: list[Failure] = []
        for column in self.columns:
            if column not in columns:
                failures.append(Failure("non_empty_check", "column is not in the file", column=column))
                continue
            for line, row in enumerate(rows, start=2):  # header is line 1
                if row.get(column, "").strip() == "":
                    failures.append(Failure("non_empty_check", "empty value", column=column, line=line))
        return failures
