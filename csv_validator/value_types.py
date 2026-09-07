"""Value-type predicates used by the types check.

ASCII-digit patterns, so that things Python's int()/float() quietly accept, like
"1_000" or non-ASCII digits, are rejected. That kind of silent acceptance is how
bad numbers slip into financial data.
"""
from __future__ import annotations

import re
from collections.abc import Callable

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
