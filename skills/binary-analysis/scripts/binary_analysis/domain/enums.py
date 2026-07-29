"""Canonical enumerations for the binary analysis domain model."""

from __future__ import annotations

from enum import Enum


class ExitCode(int, Enum):
    """Standard exit codes for the binary CLI.

    Every error that terminates the CLI maps to one of these codes.
    """

    SUCCESS = 0
    GENERIC_ERROR = 1
    INVALID_ARGS = 2
    DEPENDENCY_MISSING = 3
    INVALID_CONFIG = 4
    UNSUPPORTED_FORMAT = 5
    PROJECT_NOT_FOUND = 6
    BINARY_NOT_FOUND = 7
    AMBIGUOUS_SELECTOR = 8
    ENTITY_NOT_FOUND = 9
    IMPORT_FAILED = 10
    ANALYSIS_FAILED = 11
    OPERATION_TIMEOUT = 12
    BACKEND_FAILURE = 13
