"""Central defaults for the tool.

These are defaults only: each can be overridden per run by its flag, and the flag
always wins. Validation rules never live here; those belong in the JSON schema.
This file is for the small set of mechanics the tool needs.
"""
from __future__ import annotations

# Minimum supported Python. The CLI refuses to start below this.
MIN_PYTHON: tuple[int, int] = (3, 10)

# Default reader: "csv" (standard library) or "pandas".
DEFAULT_ENGINE: str = "csv"
