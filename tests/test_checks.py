"""The type helpers and each check in isolation."""
import pytest

from csv_validator.checks import (
    ColumnsCheck,
    NonEmptyCheck,
    TypesCheck,
    is_bool,
    is_float,
    is_integer,
)
from csv_validator.errors import SchemaError


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
    """An exact column match produces no errors."""
    assert ColumnsCheck(["a", "b"]).run(["a", "b"], []) == []


def test_columns_missing_extra_and_duplicate():
    """Missing, unexpected, and duplicate columns are all reported."""
    errors = ColumnsCheck(["a", "b"]).run(["a", "x", "x"], [])
    joined = " ".join(errors)
    assert "missing column 'b'" in joined
    assert "unexpected column 'x'" in joined
    assert "duplicate column 'x'" in joined


# --- non-empty check -----------------------------------------------------
def test_non_empty_flags_blank_with_line():
    """A blank or whitespace value is flagged with its file line number."""
    rows = [{"a": "x"}, {"a": ""}, {"a": "  "}]
    errors = NonEmptyCheck(["a"]).run(["a"], rows)
    assert len(errors) == 2
    assert "line 3" in errors[0] and "line 4" in errors[1]


def test_non_empty_missing_column_reported_once():
    """A configured column absent from the file is reported once, not per row."""
    errors = NonEmptyCheck(["ghost"]).run(["a"], [{"a": "x"}])
    assert len(errors) == 1 and "not in the file" in errors[0]


# --- types check ---------------------------------------------------------
def test_types_pass():
    """Values matching their declared types produce no errors."""
    rows = [{"age": "50", "salary": "50000.00"}]
    assert TypesCheck({"age": "integer", "salary": "float"}).run(["age", "salary"], rows) == []


def test_types_flags_bad_value_with_line():
    """A value of the wrong type is flagged with its line number."""
    rows = [{"age": "50"}, {"age": "Fifty"}]
    errors = TypesCheck({"age": "integer"}).run(["age"], rows)
    assert len(errors) == 1 and "line 3" in errors[0]


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
