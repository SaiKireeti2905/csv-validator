"""The engines package, with automatic registration.

Importing this package imports every engine module beside `base`, so each
module's `@register` decorator runs and its engine joins the registry. Adding an
engine is a new file in this folder; nothing else in the codebase changes.
"""
from __future__ import annotations

import importlib
import pkgutil

from csv_validator.engines.base import Engine, get_engine, known_engines, register

# Import each sibling module (except base) so its @register decorator runs.
for _module in pkgutil.iter_modules(__path__):
    if _module.name != "base":
        importlib.import_module(f"{__name__}.{_module.name}")

__all__ = ["Engine", "get_engine", "known_engines", "register"]
