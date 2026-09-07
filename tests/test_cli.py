"""End-to-end tests against the four sample files, plus the CLI options.

  valid.csv         passes every check
  bad_columns.csv   fails the columns check
  empty_values.csv  fails the non-empty check
  bad_types.csv     fails the types check
"""
import json

import pytest

from csv_validator.cli import (
    EXIT_OK,
    EXIT_TOOL_ERROR,
    EXIT_VALIDATION_FAILED,
    main,
)


def run(data_dir, csv_name, *extra):
    """Invoke the CLI on a sample file with the standard schema, returning the exit code."""
    return main(
        [
            f"--file_path={data_dir / csv_name}",
            f"--schema_path={data_dir / 'my_schema.json'}",
            *extra,
        ]
    )


def test_valid_passes(data_dir, capsys):
    """valid.csv passes every check and exits 0 with PASS."""
    assert run(data_dir, "valid.csv") == EXIT_OK
    assert "PASS" in capsys.readouterr().out


def test_bad_columns_fails(data_dir, capsys):
    """bad_columns.csv fails the columns check and exits 1."""
    assert run(data_dir, "bad_columns.csv") == EXIT_VALIDATION_FAILED
    assert "columns_check" in capsys.readouterr().out


def test_empty_values_fails(data_dir, capsys):
    """empty_values.csv fails the non-empty check, flagging the blank at line 3."""
    assert run(data_dir, "empty_values.csv") == EXIT_VALIDATION_FAILED
    out = capsys.readouterr().out
    assert "non_empty_check" in out and "line 3" in out


def test_bad_types_fails(data_dir, capsys):
    """bad_types.csv fails the types check on the non-numeric age values."""
    assert run(data_dir, "bad_types.csv") == EXIT_VALIDATION_FAILED
    out = capsys.readouterr().out
    assert "types_check" in out and "Fifty" in out


def test_json_output(data_dir, capsys):
    """--format=json emits a machine-readable object with ok and failure_count."""
    assert run(data_dir, "bad_types.csv", "--format=json") == EXIT_VALIDATION_FAILED
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["failure_count"] == 2


def test_max_failures_truncates(data_dir, capsys):
    """--max-failures caps the reported failures and marks the result truncated."""
    assert run(data_dir, "bad_types.csv", "--format=json", "--max-failures=1") == EXIT_VALIDATION_FAILED
    payload = json.loads(capsys.readouterr().out)
    assert payload["failure_count"] == 1
    assert payload["truncated"] is True


def test_hyphenated_flags_work(data_dir, capsys):
    """The hyphenated --file-path / --schema-path aliases work too."""
    code = main(
        [
            f"--file-path={data_dir / 'valid.csv'}",
            f"--schema-path={data_dir / 'my_schema.json'}",
        ]
    )
    assert code == EXIT_OK


def test_multichar_delimiter_is_error(data_dir, capsys):
    """A delimiter longer than one character is a tool error."""
    assert run(data_dir, "valid.csv", "--delimiter=;;") == EXIT_TOOL_ERROR
    assert "delimiter" in capsys.readouterr().err


def test_version_flag(capsys):
    """--version prints the version and exits 0."""
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert "csv-validate" in capsys.readouterr().out


def test_missing_file_is_tool_error(data_dir, capsys):
    """A missing CSV is a tool error: exit 2 with a message on stderr."""
    code = main(
        [
            f"--file_path={data_dir / 'nope.csv'}",
            f"--schema_path={data_dir / 'my_schema.json'}",
        ]
    )
    assert code == EXIT_TOOL_ERROR
    assert "error:" in capsys.readouterr().err
