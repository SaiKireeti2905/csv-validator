"""End-to-end tests against the four sample files.

  valid.csv         passes every check
  bad_columns.csv   fails the columns check
  empty_values.csv  fails the non-empty check
  bad_types.csv     fails the types check
"""
from csv_validator.cli import (
    EXIT_OK,
    EXIT_TOOL_ERROR,
    EXIT_VALIDATION_FAILED,
    main,
)


def run(data_dir, csv_name):
    """Invoke the CLI on a sample file with the standard schema, returning the exit code."""
    return main(
        [
            f"--file_path={data_dir / csv_name}",
            f"--schema_path={data_dir / 'my_schema.json'}",
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
