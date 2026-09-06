"""Exceptions for schema problems, kept separate from data-validation results.

A broken schema means the tool cannot run and is raised. A CSV that simply breaks
the rules is a normal result and comes back as a list of error messages, never as
an exception.
"""
from __future__ import annotations


class SchemaError(Exception):
    """The schema file is missing, is not valid JSON, or is malformed."""
