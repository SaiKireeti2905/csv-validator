"""The Check base class and the registry checks add themselves to.

A check subclasses Check, implements run(), and decorates itself with
@register("<schema name>"). The package __init__ imports every check module, so
registration is automatic: a new check is a new file in this folder, and nothing
else in the codebase changes. That is the open/closed principle, made literal.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeVar

from csv_validator.report import Failure


class Check(ABC):
    """A validation rule. Built from its schema params, it inspects the data and
    returns a list of Failure objects (empty means it passed)."""

    @abstractmethod
    def __init__(self, params: object) -> None:
        """Build the check from its schema params; subclasses validate and store them."""
        ...

    @abstractmethod
    def run(self, columns: list[str], rows: list[dict[str, str]]) -> list[Failure]:
        """Inspect the data and return the failures found (empty means it passed)."""
        ...


_C = TypeVar("_C", bound=Check)
_REGISTRY: dict[str, type[Check]] = {}


def register(name: str) -> Callable[[type[_C]], type[_C]]:
    """Class decorator that registers a check under its schema name."""

    def decorate(cls: type[_C]) -> type[_C]:
        _REGISTRY[name] = cls
        return cls

    return decorate


def get_check(name: str) -> type[Check] | None:
    """Return the check class registered under `name`, or None if there is none."""
    return _REGISTRY.get(name)


def known_checks() -> list[str]:
    """All registered check names, sorted."""
    return sorted(_REGISTRY)
