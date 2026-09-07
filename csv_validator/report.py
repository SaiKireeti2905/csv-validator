"""A validation failure and how to render a collection of them.

Checks produce `Failure` objects; they never build display strings themselves.
All formatting lives in `render`, so the output format is defined in one place
and the text and JSON views cannot drift apart.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Failure:
    """One problem found in the data: which check, a short message, and where."""

    check: str
    message: str
    column: str | None = None
    line: int | None = None


def render(failures: list[Failure], output_format: str = "text", truncated: bool = False) -> str:
    """Format failures as human-readable text or machine-readable JSON."""
    if output_format == "json":
        return json.dumps(
            {
                "ok": not failures,
                "truncated": truncated,
                "failure_count": len(failures),
                "failures": [
                    {key: value for key, value in asdict(f).items() if value is not None}
                    for f in failures
                ],
            },
            indent=2,
        )

    if not failures:
        return "PASS - all validations succeeded."

    lines = [f"FAIL - {len(failures)} problem(s) found:"]
    for f in failures:
        where = ""
        if f.column is not None and f.line is not None:
            where = f" [column '{f.column}', line {f.line}]"
        elif f.column is not None:
            where = f" [column '{f.column}']"
        elif f.line is not None:
            where = f" [line {f.line}]"
        lines.append(f"  - {f.check}: {f.message}{where}")
    if truncated:
        lines.append("... stopped at the --max-failures limit; more problems may exist")
    return "\n".join(lines)
