"""Schema loading: the happy path and strict error handling."""
import pytest

from csv_validator.checks.columns import ColumnsCheck
from csv_validator.checks.non_empty import NonEmptyCheck
from csv_validator.checks.types import TypesCheck
from csv_validator.errors import SchemaError
from csv_validator.schema import load_schema


def test_loads_the_three_checks(data_dir):
    """The sample schema parses into one of each check type."""
    checks = load_schema(data_dir / "my_schema.json")
    assert {type(c) for c in checks} == {ColumnsCheck, NonEmptyCheck, TypesCheck}


def test_missing_file_raises(tmp_path):
    """A schema path that does not exist raises SchemaError."""
    with pytest.raises(SchemaError):
        load_schema(tmp_path / "nope.json")


def test_invalid_json_raises(tmp_path):
    """A file that is not valid JSON raises SchemaError."""
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json", encoding="utf-8")
    with pytest.raises(SchemaError):
        load_schema(bad)


def test_unknown_check_raises(tmp_path):
    """A check name with no registered class raises SchemaError."""
    schema = tmp_path / "s.json"
    schema.write_text('{"validations": [{"range_check": {"params": {}}}]}', encoding="utf-8")
    with pytest.raises(SchemaError):
        load_schema(schema)


def test_missing_validations_key_raises(tmp_path):
    """A schema without a 'validations' key raises SchemaError."""
    schema = tmp_path / "s.json"
    schema.write_text('{"checks": []}', encoding="utf-8")
    with pytest.raises(SchemaError):
        load_schema(schema)
