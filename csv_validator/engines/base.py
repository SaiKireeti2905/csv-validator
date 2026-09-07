"""The engine base and the registry engines add themselves to.

An engine is a function that takes a Path and a delimiter and returns
(columns, rows). Each engine lives in its own module and decorates its function
with @register("<engine name>"). The package __init__ imports every engine
module, so registration is automatic: a new engine is a new file in this folder,
and nothing else in the codebase changes. That is the open/closed principle,
applied to engines exactly as it is to checks.
"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

# An engine turns a file into a header plus rows keyed by column name.
Engine = Callable[[Path, str], "tuple[list[str], list[dict[str, str]]]"]

_REGISTRY: dict[str, Engine] = {}


def register(name: str) -> Callable[[Engine], Engine]:
    """Decorator that registers an engine function under its name."""

    def decorate(engine: Engine) -> Engine:
        _REGISTRY[name] = engine
        return engine

    return decorate


def get_engine(name: str) -> Engine | None:
    """Return the engine registered under `name`, or None if there is none."""
    return _REGISTRY.get(name)


def known_engines() -> list[str]:
    """All registered engine names, sorted."""
    return sorted(_REGISTRY)
