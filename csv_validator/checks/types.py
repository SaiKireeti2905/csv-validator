"""types_check: every non-empty value in a column must match its declared type."""
from __future__ import annotations

from csv_validator.checks.base import Check, register
from csv_validator.errors import SchemaError
from csv_validator.report import Failure
from csv_validator.value_types import TYPE_CHECKERS


@register("types_check")
class TypesCheck(Check):
    """Every non-empty value in a column must match its declared type."""

    def __init__(self, params: object) -> None:
        """Validate the params (a column-to-type map with known types) and store them."""
        if not isinstance(params, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in params.items()
        ):
            raise SchemaError("types_check params must map column names to type names")
        unknown = sorted(t for t in params.values() if t not in TYPE_CHECKERS)
        if unknown:
            raise SchemaError(f"types_check has unknown type(s): {unknown}")
        self.column_types = params

    def run(self, columns: list[str], rows: list[dict[str, str]]) -> list[Failure]:
        """Report values that do not match their column's declared type, skipping empties."""
        failures: list[Failure] = []
        for column, type_name in self.column_types.items():
            if column not in columns:
                failures.append(Failure("types_check", "column is not in the file", column=column))
                continue
            checker = TYPE_CHECKERS[type_name]
            for line, row in enumerate(rows, start=2):
                value = row.get(column, "")
                if value.strip() == "":
                    continue  # emptiness is the non-empty check's job
                if not checker(value):
                    failures.append(
                        Failure(
                            "types_check",
                            f"'{value}' is not a valid {type_name}",
                            column=column,
                            line=line,
                        )
                    )
        return failures
