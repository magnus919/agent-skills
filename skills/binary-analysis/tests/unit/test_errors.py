"""Unit tests for domain errors and exit codes."""

from __future__ import annotations

from binary_analysis.domain.enums import ExitCode
from binary_analysis.domain.errors import (
    BinaryAnalysisError,
    DependencyMissingError,
    InvalidArgsError,
)


class TestExitCodes:
    """Tests for exit code enumeration."""

    def test_success_is_0(self) -> None:
        assert ExitCode.SUCCESS == 0

    def test_invalid_args_is_2(self) -> None:
        assert ExitCode.INVALID_ARGS == 2

    def test_dependency_missing_is_3(self) -> None:
        assert ExitCode.DEPENDENCY_MISSING == 3

    def test_all_codes_are_unique(self) -> None:
        values = [e.value for e in ExitCode]
        assert len(values) == len(set(values))

    def test_all_14_exit_codes_defined(self) -> None:
        assert len(ExitCode) == 14


class TestBinaryAnalysisError:
    """Tests for BinaryAnalysisError base class."""

    def test_default_exit_code(self) -> None:
        error = BinaryAnalysisError("test error")
        assert error.exit_code == ExitCode.GENERIC_ERROR
        assert error.message == "test error"

    def test_custom_exit_code(self) -> None:
        error = BinaryAnalysisError("test error", ExitCode.BACKEND_FAILURE)
        assert error.exit_code == ExitCode.BACKEND_FAILURE

    def test_to_diagnostic(self) -> None:
        error = BinaryAnalysisError("something went wrong")
        diag = error.to_diagnostic()
        assert diag["severity"] == "ERROR"
        assert diag["message"] == "something went wrong"

    def test_is_exception(self) -> None:
        error = BinaryAnalysisError("test")
        assert isinstance(error, Exception)


class TestInvalidArgsError:
    """Tests for InvalidArgsError."""

    def test_exit_code_is_2(self) -> None:
        error = InvalidArgsError("bad args")
        assert error.exit_code == ExitCode.INVALID_ARGS

    def test_message_preserved(self) -> None:
        error = InvalidArgsError("limit must be a positive integer")
        assert "limit must be a positive integer" in error.message


class TestDependencyMissingError:
    """Tests for DependencyMissingError."""

    def test_exit_code_is_3(self) -> None:
        error = DependencyMissingError("Ghidra not found")
        assert error.exit_code == ExitCode.DEPENDENCY_MISSING

    def test_message_preserved(self) -> None:
        error = DependencyMissingError("Java not installed")
        assert "Java not installed" in error.message
