"""The Failure model and how failures are rendered."""
import json

from csv_validator.report import Failure, render


def test_render_text_pass():
    """No failures renders as PASS."""
    assert "PASS" in render([], "text")


def test_render_text_includes_check_message_and_location():
    """A text failure shows its check, message, column, and line."""
    out = render([Failure("types_check", "'x' is not a valid integer", column="age", line=2)], "text")
    assert "types_check" in out and "age" in out and "line 2" in out


def test_render_json_shape():
    """JSON output carries ok, truncated, a count, and the failures."""
    failure = Failure("types_check", "bad", column="age", line=2)
    payload = json.loads(render([failure], "json", truncated=True))
    assert payload["ok"] is False
    assert payload["truncated"] is True
    assert payload["failure_count"] == 1
    assert payload["failures"][0]["column"] == "age"


def test_render_json_omits_absent_location():
    """A failure with no line leaves the line key out of the JSON."""
    payload = json.loads(render([Failure("columns_check", "missing", column="a")], "json"))
    assert "line" not in payload["failures"][0]
