"""Central defaults for the tool.

These are defaults only: each can be overridden per run by its flag, and the flag
always wins. Validation rules never live here; those belong in the JSON schema.
"""
from __future__ import annotations

# Minimum supported Python. The CLI refuses to start below this.
MIN_PYTHON: tuple[int, int] = (3, 10)

# Default reader: "csv" (standard library) or "pandas".
DEFAULT_ENGINE: str = "csv"

# Default output format: "text" or "json".
DEFAULT_FORMAT: str = "text"

# Default CSV field delimiter (a single character).
DEFAULT_DELIMITER: str = ","

# Stop reporting after this many problems; 0 means unlimited.
DEFAULT_MAX_FAILURES: int = 0
