# csv-validator

A small command-line tool that validates a CSV file against a JSON schema. It
runs three kinds of checks and reports every problem it finds.

- **Python 3.10+**, standard library only.
- Clean, layered design; adding a new check is one class plus one line.

## Requirements

Python 3.10 or newer. No third-party packages are needed to run it (`pytest` and
`ruff` are only for development).

## Usage

```bash
python validate.py --file_path="tests/data/valid.csv" --schema_path="tests/data/my_schema.json"
```

An optional `--engine` chooses the reader: `csv` (standard library, the default)
or `pandas`. Both produce the same result.

```bash
python validate.py --file_path="tests/data/valid.csv" --schema_path="tests/data/my_schema.json" --engine=pandas
```

Exit codes: `0` passed, `1` the data has problems, `2` a tool error (bad
arguments, missing file, a broken schema, or the pandas engine not installed).

Example output:

```text
FAIL - 2 problem(s) found:
  - types_check: 'Fifty' in 'age' is not a valid integer at line 2
  - types_check: 'Forty four' in 'age' is not a valid integer at line 3
```

Line numbers count from the file, so the header is line 1 and the first data row
is line 2.

## Schema format

```json
{
  "validations": [
    {
      "columns_check":   { "params": ["name", "position", "age", "salary", "active"] },
      "non_empty_check": { "params": ["name", "salary", "active"] },
      "types_check":     { "params": { "age": "integer", "salary": "float", "active": "bool" } }
    }
  ]
}
```

- `columns_check`: the file must have exactly these columns, with no missing, extra, or duplicate names.
- `non_empty_check`: the listed columns must have a value in every row.
- `types_check`: every non-empty value in each column must match its declared type.

Supported types: `string`, `integer`, `float`, `bool`.

## Project layout

```
csv-validator/
  validate.py            entry point matching the brief's example
  pyproject.toml
  README.md
  csv_validator/
    config.py            defaults: minimum Python, default engine
    errors.py            SchemaError
    checks.py            Check base class, the 3 checks, type helpers, the registry
    schema.py            JSON schema -> list of Check objects
    validator.py         the csv and pandas readers + run the checks
    cli.py               arguments, version guard, exit codes
  tests/
    data/                the 4 sample CSVs + my_schema.json
    test_checks.py
    test_schema.py
    test_cli.py
```

## Testing

```bash
pip install .[dev]
pytest
ruff check .
```

The suite covers the four sample files (valid.csv passes; bad_columns,
empty_values, and bad_types each fail one check), the type helpers, each check on
its own, and the CLI's exit codes.
