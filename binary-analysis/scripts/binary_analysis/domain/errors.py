"""Canonical error types and exit codes for the binary CLI.

Each error type maps to a specific exit code from ExitCode enum (0-13).
The error hierarchy allows callers to catch specific error types while
the base class provides a fallback for GENERIC_ERROR.
"""

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
    """Raised when CLI arguments are invalid. Exit code 2."""

    def __init__(self, message: str) -> None:
        super().__init__(message, ExitCode.INVALID_ARGS)


class DependencyMissingError(BinaryAnalysisError):
    """Raised when a required external dependency is missing. Exit code 3."""

    def __init__(self, message: str) -> None:
        super().__init__(message, ExitCode.DEPENDENCY_MISSING)


class InvalidConfigError(BinaryAnalysisError):
    """Raised when configuration is invalid or corrupted. Exit code 4."""

    def __init__(self, message: str) -> None:
        super().__init__(message, ExitCode.INVALID_CONFIG)

    def to_diagnostic(self) -> dict[str, Any]:
        return {
            "severity": "ERROR",
            "message": self.message,
            "category": "config",
        }


class UnsupportedFormatError(BinaryAnalysisError):
    """Raised when the binary format is not supported. Exit code 5."""

    def __init__(self, message: str) -> None:
        super().__init__(message, ExitCode.UNSUPPORTED_FORMAT)


class ProjectNotFoundError(BinaryAnalysisError):
    """Raised when a project does not exist. Exit code 6."""

    def __init__(self, project: str) -> None:
        super().__init__(f"Project not found: {project}", ExitCode.PROJECT_NOT_FOUND)


class BinaryNotFoundError(BinaryAnalysisError):
    """Raised when a binary is not found in a project. Exit code 7."""

    def __init__(self, message: str = "No binary has been imported into this project") -> None:
        super().__init__(message, ExitCode.BINARY_NOT_FOUND)


class AmbiguousSelectorError(BinaryAnalysisError):
    """Raised when an entity selector matches multiple entities. Exit code 8."""

    def __init__(self, message: str, candidates: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message, ExitCode.AMBIGUOUS_SELECTOR)
        self.candidates = candidates or []

    def to_diagnostic(self) -> dict[str, Any]:
        diag = super().to_diagnostic()
        if self.candidates:
            diag["candidates"] = self.candidates
        return diag


class EntityNotFoundError(BinaryAnalysisError):
    """Raised when a referenced entity does not exist. Exit code 9."""

    def __init__(self, entity_type: str, selector: str) -> None:
        super().__init__(
            f"{entity_type} not found: {selector}",
            ExitCode.ENTITY_NOT_FOUND,
        )
        self.entity_type = entity_type
        self.selector = selector


class ImportFailedError(BinaryAnalysisError):
    """Raised when binary import fails. Exit code 10."""

    def __init__(self, message: str, binary_path: str | None = None) -> None:
        super().__init__(message, ExitCode.IMPORT_FAILED)
        self.binary_path = binary_path


class AnalysisFailedError(BinaryAnalysisError):
    """Raised when analysis fails completely (not partial). Exit code 11."""

    def __init__(self, message: str, project: str | None = None) -> None:
        super().__init__(message, ExitCode.ANALYSIS_FAILED)
        self.project = project


class OperationTimeoutError(BinaryAnalysisError):
    """Raised when an operation exceeds its timeout. Exit code 12."""

    def __init__(self, message: str = "Operation timed out") -> None:
        super().__init__(message, ExitCode.OPERATION_TIMEOUT)

    def to_diagnostic(self) -> dict[str, Any]:
        return {
            "severity": "ERROR",
            "message": self.message,
            "category": "timeout",
            "recoverable": True,
        }


class BackendFailureError(BinaryAnalysisError):
    """Raised when the backend encounters an internal failure. Exit code 13."""

    def __init__(self, message: str, original_error: str | None = None) -> None:
        super().__init__(message, ExitCode.BACKEND_FAILURE)
        self.original_error = original_error

    def to_diagnostic(self) -> dict[str, Any]:
        diag = super().to_diagnostic()
        if self.original_error:
            diag["backend_error"] = self.original_error
        return diag


# ---------------------------------------------------------------------------
# Exit code to error type lookup
# ---------------------------------------------------------------------------

_EXIT_CODE_TO_ERROR: dict[ExitCode, type[BinaryAnalysisError]] = {
    ExitCode.SUCCESS: BinaryAnalysisError,
    ExitCode.GENERIC_ERROR: BinaryAnalysisError,
    ExitCode.INVALID_ARGS: InvalidArgsError,
    ExitCode.DEPENDENCY_MISSING: DependencyMissingError,
    ExitCode.INVALID_CONFIG: InvalidConfigError,
    ExitCode.UNSUPPORTED_FORMAT: UnsupportedFormatError,
    ExitCode.PROJECT_NOT_FOUND: ProjectNotFoundError,
    ExitCode.BINARY_NOT_FOUND: BinaryNotFoundError,
    ExitCode.AMBIGUOUS_SELECTOR: AmbiguousSelectorError,
    ExitCode.ENTITY_NOT_FOUND: EntityNotFoundError,
    ExitCode.IMPORT_FAILED: ImportFailedError,
    ExitCode.ANALYSIS_FAILED: AnalysisFailedError,
    ExitCode.OPERATION_TIMEOUT: OperationTimeoutError,
    ExitCode.BACKEND_FAILURE: BackendFailureError,
}


def error_type_for(code: ExitCode) -> type[BinaryAnalysisError]:
    """Get the error class for a given exit code."""
    return _EXIT_CODE_TO_ERROR.get(code, BinaryAnalysisError)


def fail(error: BinaryAnalysisError) -> None:
    """Print the error to stderr and exit with the appropriate code."""
    print(f"Error: {error.message}", file=sys.stderr)
    sys.exit(error.exit_code)
