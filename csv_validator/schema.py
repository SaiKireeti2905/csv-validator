"""Load a JSON schema and turn it into a list of check objects.

Schema shape (from the brief)::

    {
      "validations": [
        {
          "columns_check":   {"params": ["name", "age", ...]},
          "non_empty_check": {"params": ["name", ...]},
          "types_check":     {"params": {"name": "string", "age": "integer", ...}}
        }
      ]
    }

Parsing is strict: an unknown check or a missing 'params' raises SchemaError, so a
typo fails loudly rather than silently dropping a validation.
"""
from __future__ import annotations

import json
from pathlib import Path

from csv_validator.checks import CHECKS, Check
from csv_validator.errors import SchemaError


def load_schema(path: str | Path) -> list[Check]:
    """Read the schema file and build the checks it describes."""
    file = Path(path)
    if not file.is_file():
        raise SchemaError(f"Schema file not found: {file}")
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SchemaError(f"Invalid JSON in schema {file}: {exc}") from exc

    if not isinstance(data, dict) or "validations" not in data:
        raise SchemaError("Schema must be an object with a 'validations' key")

    checks: list[Check] = []
    for group in data["validations"]:
        if not isinstance(group, dict):
            raise SchemaError("Each item in 'validations' must be an object")
        for name, spec in group.items():
            check_class = CHECKS.get(name)
            if check_class is None:
                raise SchemaError(f"Unknown check '{name}'. Known checks: {sorted(CHECKS)}")
            if not isinstance(spec, dict) or "params" not in spec:
                raise SchemaError(f"'{name}' must be an object with a 'params' key")
            checks.append(check_class(spec["params"]))  # each check validates its own params

    if not checks:
        raise SchemaError("Schema defines no checks")
    return checks
