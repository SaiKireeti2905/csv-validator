#!/usr/bin/env python3
"""Run the validator exactly as in the assessment example:

    python validate.py --file_path="1.csv" --schema_path="my_schema.json"

It just calls the packaged CLI, so there is a single implementation.
"""
from csv_validator.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
