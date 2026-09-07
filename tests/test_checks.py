"""The type helpers and each check in isolation."""
import pytest

from csv_validator.checks import get_check, known_checks
from csv_validator.checks.columns import ColumnsCheck
from csv_validator.checks.non_empty import NonEmptyCheck
from csv_validator.checks.types import TypesCheck
from csv_validator.errors import SchemaError
from csv_validator.value_types import is_bool, is_float, is_integer


def test_registry_autoloads_all_checks():
    """All three checks register themselves when the package is imported."""
    assert set(known_checks()) == {"columns_check", "non_empty_check", "types_check"}


def test_get_check_resolves_known_and_unknown():
    """get_check returns the class for a known name and None for an unknown one."""
    assert get_check("columns_check") is ColumnsCheck
    assert get_check("nope") is None


# --- type helpers --------------------------------------------------------
@pytest.mark.parametrize("value", ["50", "-7", " 12 "])
def test_is_integer_accepts(value):
    """Whole numbers, with an optional sign and surrounding spaces, are integers."""
    assert is_integer(value)


@pytest.mark.parametrize("value", ["50.0", "Fifty", "1_000", ""])
def test_is_integer_rejects(value):
    """Decimals, words, underscores, and blanks are not integers."""
    assert not is_integer(value)


@pytest.mark.parametrize("value", ["50000.00", "50000", "-3.14", "2e3"])
def test_is_float_accepts(value):
    """Decimals, whole numbers, and scientific notation are floats."""
    assert is_float(value)


@pytest.mark.parametrize("value", ["nan", "inf", "abc", ""])
def test_is_float_rejects(value):
    """NaN, infinity, words, and blanks are not floats."""
    assert not is_float(value)


def test_is_bool():
    """Only 'true'/'false' (any case) are booleans."""
    assert is_bool("True") and is_bool("false")
    assert not is_bool("1") and not is_bool("yes")


# --- columns check -------------------------------------------------------
def test_columns_pass():
    """An exact column match produces no failures."""
    assert ColumnsCheck(["a", "b"]).run(["a", "b"], []) == []


def test_columns_missing_extra_and_duplicate():
    """Missing, unexpected, and duplicate columns are all reported."""
    failures = ColumnsCheck(["a", "b"]).run(["a", "x", "x"], [])
    found = {(f.message, f.column) for f in failures}
    assert ("missing expected column", "b") in found
    assert ("unexpected column not in schema", "x") in found
    assert ("duplicate column in file", "x") in found


def test_columns_duplicate_reported_once():
    """A column appearing three times is reported as a duplicate only once."""
    failures = ColumnsCheck(["a"]).run(["a", "a", "a"], [])
    duplicates = [f for f in failures if f.message == "duplicate column in file"]
    assert len(duplicates) == 1


# --- non-empty check -----------------------------------------------------
def test_non_empty_flags_blank_with_line():
    """A blank or whitespace value is flagged with its file line number."""
    rows = [{"a": "x"}, {"a": ""}, {"a": "  "}]
    failures = NonEmptyCheck(["a"]).run(["a"], rows)
    assert [f.line for f in failures] == [3, 4]
    assert all(f.check == "non_empty_check" for f in failures)


def test_non_empty_missing_column_reported_once():
    """A configured column absent from the file is reported once, not per row."""
    failures = NonEmptyCheck(["ghost"]).run(["a"], [{"a": "x"}])
    assert len(failures) == 1 and failures[0].column == "ghost"


# --- types check ---------------------------------------------------------
def test_types_pass():
    """Values matching their declared types produce no failures."""
    rows = [{"age": "50", "salary": "50000.00"}]
    assert TypesCheck({"age": "integer", "salary": "float"}).run(["age", "salary"], rows) == []


def test_types_flags_bad_value_with_line():
    """A value of the wrong type is flagged with its line number and value."""
    rows = [{"age": "50"}, {"age": "Fifty"}]
    failures = TypesCheck({"age": "integer"}).run(["age"], rows)
    assert len(failures) == 1
    assert failures[0].line == 3 and failures[0].column == "age"
    assert "Fifty" in failures[0].message


def test_types_skips_empty():
    """The types check ignores empty cells; emptiness is the non-empty check's job."""
    assert TypesCheck({"age": "integer"}).run(["age"], [{"age": ""}]) == []


# --- param validation ----------------------------------------------------
def test_bad_params_raise():
    """Malformed params raise SchemaError at construction time."""
    with pytest.raises(SchemaError):
        ColumnsCheck("not a list")
    with pytest.raises(SchemaError):
        TypesCheck({"age": "date"})  # unknown type
