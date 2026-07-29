"""Canonical error types and exit codes for the binary CLI."""

from __future__ import annotations

import sys
from typing import Any

from binary_analysis.domain.enums import ExitCode


class BinaryAnalysisError(Exception):
    """Base exception for all binary analysis errors.

    Every BinaryAnalysisError carries an exit code and can produce
    a JSON-serializable representation for the envelope's diagnostics.
    """

    def __init__(self, message: str, exit_code: ExitCode = ExitCode.GENERIC_ERROR) -> None:
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code

    def to_diagnostic(self) -> dict[str, Any]:
        """Return a diagnostic entry suitable for the envelope."""
        return {
            "severity": "ERROR",
            "message": self.message,
        }


class InvalidArgsError(BinaryAnalysisError):
    """Raised when CLI arguments are invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, ExitCode.INVALID_ARGS)


class DependencyMissingError(BinaryAnalysisError):
    """Raised when a required external dependency is missing."""

    def __init__(self, message: str) -> None:
        super().__init__(message, ExitCode.DEPENDENCY_MISSING)


def fail(error: BinaryAnalysisError) -> None:
    """Print the error to stderr and exit with the appropriate code."""
    print(f"Error: {error.message}", file=sys.stderr)
    sys.exit(error.exit_code)
