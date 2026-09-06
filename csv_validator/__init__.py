"""Validate a CSV file against a JSON schema.

    from csv_validator import validate

    errors = validate("data.csv", "schema.json")
    if errors:
        print("\n".join(errors))
"""
from __future__ import annotations

from csv_validator.validator import validate

__all__ = ["validate"]
__version__ = "1.0.0"
