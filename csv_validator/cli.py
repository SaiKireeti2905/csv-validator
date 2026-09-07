"""Command-line entry point.

Exit codes:
  0  passed
  1  the data has problems
  2  tool error (bad arguments, missing/unreadable file, or a broken schema)
"""
from __future__ import annotations

import argparse
import sys

from csv_validator import __version__, config
from csv_validator.engines import known_engines
from csv_validator.errors import CsvReadError, SchemaError
from csv_validator.report import render
from csv_validator.validator import validate

EXIT_OK = 0
EXIT_VALIDATION_FAILED = 1
EXIT_TOOL_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser: flags, aliases, choices, defaults, and help."""
    parser = argparse.ArgumentParser(
        prog="csv-validate",
        description="Validate a CSV file against a JSON validation schema.",
        epilog="Exit codes: 0 = passed, 1 = data problems found, 2 = tool error.",
    )
    parser.add_argument("--version", action="version", version=f"csv-validate {__version__}")
    parser.add_argument(
        "--file-path", "--file_path", dest="file_path", required=True, metavar="PATH",
        help="Path to the CSV file to validate.",
    )
    parser.add_argument(
        "--schema-path", "--schema_path", dest="schema_path", required=True, metavar="PATH",
        help="Path to the JSON schema.",
    )
    parser.add_argument(
        "--engine", choices=sorted(known_engines()), default=config.DEFAULT_ENGINE, metavar="ENGINE",
        help="Reader to use: 'csv' (standard library) or 'pandas'.",
    )
    parser.add_argument(
        "--format", "--output_format", dest="output_format",
        choices=("text", "json"), default=config.DEFAULT_FORMAT, metavar="FORMAT",
        help="Output format: 'text' or 'json'.",
    )
    parser.add_argument(
        "--delimiter", default=config.DEFAULT_DELIMITER, metavar="CHAR",
        help="CSV field delimiter, a single character (default: ',').",
    )
    parser.add_argument(
        "--max-failures", type=int, default=config.DEFAULT_MAX_FAILURES, metavar="N",
        help="Stop reporting after N problems; 0 means unlimited.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the validation, print the result, and return an exit code."""
    if sys.version_info < config.MIN_PYTHON:
        minimum = f"{config.MIN_PYTHON[0]}.{config.MIN_PYTHON[1]}"
        print(f"error: this tool requires Python {minimum} or newer", file=sys.stderr)
        return EXIT_TOOL_ERROR

    args = build_parser().parse_args(argv)

    if len(args.delimiter) != 1:
        print("error: --delimiter must be a single character", file=sys.stderr)
        return EXIT_TOOL_ERROR
    if args.max_failures < 0:
        print("error: --max-failures must be 0 or greater", file=sys.stderr)
        return EXIT_TOOL_ERROR

    try:
        failures = validate(
            args.file_path, args.schema_path, engine=args.engine, delimiter=args.delimiter
        )
    except (CsvReadError, SchemaError, ImportError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_TOOL_ERROR

    limit = args.max_failures
    truncated = 0 < limit < len(failures)
    shown = failures[:limit] if limit > 0 else failures
    print(render(shown, args.output_format, truncated))
    return EXIT_VALIDATION_FAILED if failures else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
