"""Tool-level exceptions, kept separate from data-validation results.

A broken schema or an unreadable file means the tool cannot run, and is raised.
A CSV that simply breaks the rules is a normal result and comes back as a list of
Failure objects, never as an exception.
"""
from __future__ import annotations


class CsvValidatorError(Exception):
    """Base class for every tool-level error; the CLI maps these to exit code 2."""


class SchemaError(CsvValidatorError):
    """The schema file is missing, is not valid JSON, or is malformed."""


class CsvReadError(CsvValidatorError):
    """The CSV file is missing or cannot be read or parsed."""
