"""Validate a CSV file against a JSON schema.

    from csv_validator import validate

    errors = validate("data.csv", "schema.json")
    if errors:
        print("\n".join(errors))
"""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from csv_validator.validator import validate

__all__ = ["validate"]

# Single source of truth is the version in pyproject.toml. We read it from the
# installed package metadata rather than hardcoding a second copy here. The
# fallback covers running straight from the source tree without installing.
try:
    __version__ = version("csv-validator")
except PackageNotFoundError:
    __version__ = "0.0.0+source"
