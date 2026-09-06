"""Command-line entry point.

Exit codes:
  0  passed
  1  the data has problems
  2  tool error (bad arguments, missing file, or a broken schema)
"""
from __future__ import annotations

import argparse
import sys

from csv_validator import config
from csv_validator.errors import SchemaError
from csv_validator.validator import READERS, validate

EXIT_OK = 0
EXIT_VALIDATION_FAILED = 1
EXIT_TOOL_ERROR = 2


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the validation, print the result, and return an exit code."""
    if sys.version_info < config.MIN_PYTHON:
        minimum = f"{config.MIN_PYTHON[0]}.{config.MIN_PYTHON[1]}"
        print(f"error: this tool requires Python {minimum} or newer", file=sys.stderr)
        return EXIT_TOOL_ERROR

    parser = argparse.ArgumentParser(
        prog="csv-validate",
        description="Validate a CSV file against a JSON validation schema.",
    )
    parser.add_argument("--file_path", required=True, help="Path to the CSV file to validate.")
    parser.add_argument("--schema_path", required=True, help="Path to the JSON schema.")
    parser.add_argument(
        "--engine",
        choices=sorted(READERS),
        default=config.DEFAULT_ENGINE,
        help="Reader to use: 'csv' (standard library) or 'pandas'.",
    )
    args = parser.parse_args(argv)

    try:
        errors = validate(args.file_path, args.schema_path, engine=args.engine)
    except (FileNotFoundError, SchemaError, ImportError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_TOOL_ERROR

    if errors:
        print(f"FAIL - {len(errors)} problem(s) found:")
        for error in errors:
            print(f"  - {error}")
        return EXIT_VALIDATION_FAILED

    print("PASS - all validations succeeded.")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
