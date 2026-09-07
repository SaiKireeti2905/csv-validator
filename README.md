# csv-validator

A small command-line tool that validates a CSV file against a JSON schema. It
runs three kinds of checks and reports every problem it finds.

## Requirements

Python 3.10 or newer. No third-party packages are needed to run it; `pandas` is an
optional engine, and `pytest`, `ruff`, and `mypy` are for development.

## Usage

```bash
python validate.py --file_path="tests/data/valid.csv" --schema_path="tests/data/my_schema.json"
```

Options:

| Flag | Default | Meaning |
|------|---------|---------|
| `--file_path` / `--file-path`     | required | CSV file to validate |
| `--schema_path` / `--schema-path` | required | JSON schema to validate against |
| `--engine`        | `csv`  | Reader: `csv` (standard library) or `pandas` |
| `--format`        | `text` | Output format: `text` or `json` |
| `--delimiter`     | `,`    | Field delimiter (a single character) |
| `--max-failures`  | `100`  | Stop reporting after N problems; `0` means unlimited |
| `--version`       |        | Print the version and exit |

Exit codes:

| Code | Meaning |
|------|---------|
| 0 | Passed |
| 1 | Failed: the data has problems |
| 2 | Tool error: bad arguments, missing/unreadable file, or a broken schema |

Example output:

```text
FAIL - 2 problem(s) found:
  - types_check: 'Fifty' is not a valid integer [column 'age', line 2]
  - types_check: 'Forty four' is not a valid integer [column 'age', line 3]
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

## How it works

```
cli  ->  validator  ->  schema (JSON -> list of Check objects)
                    ->  a reader (csv or pandas) -> (columns, rows)
         each check returns Failure objects; the report renders them
         cli prints text or JSON and returns an exit code
```

- `checks/` is a package with one module per check. Each check subclasses `Check`
  and registers itself with `@register("...")`; the package auto-imports its
  modules on load, so **adding a check is just a new file in `checks/`** and
  nothing else in the codebase changes.
- Checks return `Failure` objects and never format text. All formatting lives in
  `report.render`, so text and JSON stay in sync.
- `validator.py` reads the file (via a `csv` or `pandas` reader picked from a
  `READERS` registry) and runs the checks. It depends only on the `(columns, rows)`
  shape, not on how the file was read.

## Project layout

```
csv-validator/
  validate.py            entry point matching the brief's example
  pyproject.toml
  README.md
  csv_validator/
    config.py            defaults: min Python, engine, format, delimiter, max-failures
    errors.py            SchemaError, CsvReadError
    report.py            Failure + render (text and JSON)
    value_types.py       type predicates used by the types check
    schema.py            JSON schema -> list of Check objects
    validator.py         the csv and pandas readers + run the checks
    cli.py               arguments, version guard, exit codes
    checks/              one module per check, auto-registered
      base.py            Check base class + the @register registry
      columns.py         columns_check
      non_empty.py       non_empty_check
      types.py           types_check
  tests/
    data/                the 4 sample CSVs + my_schema.json
    test_checks.py  test_report.py  test_schema.py  test_validator.py  test_cli.py
```

## Testing

```bash
pip install .[dev]
pytest
ruff check .
mypy
```

The suite covers the four sample files, the type helpers, each check on its own,
schema and read errors, the report rendering, and the CLI options and exit codes.
