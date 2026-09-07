"""The validation checks, the type helpers they use, and the check registry.

Every check extends `Check` and implements `run`, returning `Failure` objects.
Checks find problems; they do not format text (that is `report.render`'s job).
Adding a new check is: write a class, add one line to the CHECKS registry.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Callable

from csv_validator.errors import SchemaError
from csv_validator.report import Failure

# --- value-type helpers --------------------------------------------------
# ASCII-digit patterns, so that things Python's int()/float() quietly accept,
# like "1_000" or non-ASCII digits, are rejected. That kind of silent
# acceptance is how bad numbers slip into financial data.
_INTEGER = re.compile(r"^[+-]?[0-9]+$")
_FLOAT = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")


def is_integer(value: str) -> bool:
    """Return True if the value is a whole number: an optional sign then ASCII digits."""
    return bool(_INTEGER.match(value.strip()))


def is_float(value: str) -> bool:
    """Return True for a real number in plain or scientific notation; NaN and inf are rejected."""
    return bool(_FLOAT.match(value.strip()))


def is_bool(value: str) -> bool:
    """Return True for 'true' or 'false', case-insensitive."""
    return value.strip().lower() in {"true", "false"}


def is_string(value: str) -> bool:
    """Return True for any value, since any cell is a valid string."""
    return True


TYPE_CHECKERS: dict[str, Callable[[str], bool]] = {
    "string": is_string,
    "integer": is_integer,
    "float": is_float,
    "bool": is_bool,
}


# --- the abstraction -----------------------------------------------------
class Check(ABC):
    """A validation rule. Built from its schema params, it inspects the data and
    returns a list of Failure objects (empty means it passed)."""

    @abstractmethod
    def run(self, columns: list[str], rows: list[dict[str, str]]) -> list[Failure]:
        """Inspect the data and return the failures found (empty means it passed)."""
        ...


# --- the three checks ----------------------------------------------------
class ColumnsCheck(Check):
    """The file must have exactly the expected columns: none missing, extra, or duplicated."""

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


# --- the registry: add a check by adding one class above and one line here ---
CHECKS: dict[str, Callable[[object], Check]] = {
    "columns_check": ColumnsCheck,
    "non_empty_check": NonEmptyCheck,
    "types_check": TypesCheck,
}
