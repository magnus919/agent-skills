"""Unit tests for domain errors and exit codes.

Covers all 13 error types with their exit code mappings.
"""

from __future__ import annotations

from binary_analysis.domain.enums import ExitCode
from binary_analysis.domain.errors import (
    AmbiguousSelectorError,
    AnalysisFailedError,
    BackendFailureError,
    BinaryAnalysisError,
    BinaryNotFoundError,
    DependencyMissingError,
    EntityNotFoundError,
    ImportFailedError,
    InvalidArgsError,
    InvalidConfigError,
    OperationTimeoutError,
    ProjectNotFoundError,
    UnsupportedFormatError,
    error_type_for,
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


class TestInvalidConfigError:
    """Tests for InvalidConfigError."""

    def test_exit_code_is_4(self) -> None:
        error = InvalidConfigError("corrupt project.json")
        assert error.exit_code == ExitCode.INVALID_CONFIG

    def test_to_diagnostic(self) -> None:
        error = InvalidConfigError("corrupt project.json")
        diag = error.to_diagnostic()
        assert diag["severity"] == "ERROR"
        assert diag["category"] == "config"


class TestUnsupportedFormatError:
    """Tests for UnsupportedFormatError."""

    def test_exit_code_is_5(self) -> None:
        error = UnsupportedFormatError("unknown format")
        assert error.exit_code == ExitCode.UNSUPPORTED_FORMAT


class TestProjectNotFoundError:
    """Tests for ProjectNotFoundError."""

    def test_exit_code_is_6(self) -> None:
        error = ProjectNotFoundError("my-project")
        assert error.exit_code == ExitCode.PROJECT_NOT_FOUND
        assert "my-project" in error.message


class TestBinaryNotFoundError:
    """Tests for BinaryNotFoundError."""

    def test_exit_code_is_7(self) -> None:
        error = BinaryNotFoundError()
        assert error.exit_code == ExitCode.BINARY_NOT_FOUND
        assert "binary" in error.message.lower()


class TestAmbiguousSelectorError:
    """Tests for AmbiguousSelectorError."""

    def test_exit_code_is_8(self) -> None:
        error = AmbiguousSelectorError("ambiguous", [])
        assert error.exit_code == ExitCode.AMBIGUOUS_SELECTOR

    def test_to_diagnostic_with_candidates(self) -> None:
        candidates = [{"name": "func1"}, {"name": "func2"}]
        error = AmbiguousSelectorError("ambiguous selector", candidates)
        diag = error.to_diagnostic()
        assert "candidates" in diag
        assert len(diag["candidates"]) == 2


class TestEntityNotFoundError:
    """Tests for EntityNotFoundError."""

    def test_exit_code_is_9(self) -> None:
        error = EntityNotFoundError("Function", "my_func")
        assert error.exit_code == ExitCode.ENTITY_NOT_FOUND
        assert error.entity_type == "Function"
        assert error.selector == "my_func"

    def test_message_contains_type_and_selector(self) -> None:
        error = EntityNotFoundError("Function", "nonexistent")
        assert "Function" in error.message
        assert "nonexistent" in error.message


class TestImportFailedError:
    """Tests for ImportFailedError."""

    def test_exit_code_is_10(self) -> None:
        error = ImportFailedError("disk full")
        assert error.exit_code == ExitCode.IMPORT_FAILED

    def test_binary_path_preserved(self) -> None:
        error = ImportFailedError("failed", binary_path="/tmp/test.bin")
        assert error.binary_path == "/tmp/test.bin"


class TestAnalysisFailedError:
    """Tests for AnalysisFailedError."""

    def test_exit_code_is_11(self) -> None:
        error = AnalysisFailedError("analysis crashed")
        assert error.exit_code == ExitCode.ANALYSIS_FAILED

    def test_project_preserved(self) -> None:
        error = AnalysisFailedError("analysis crashed", project="my-proj")
        assert error.project == "my-proj"


class TestOperationTimeoutError:
    """Tests for OperationTimeoutError."""

    def test_exit_code_is_12(self) -> None:
        error = OperationTimeoutError()
        assert error.exit_code == ExitCode.OPERATION_TIMEOUT

    def test_to_diagnostic(self) -> None:
        error = OperationTimeoutError("timed out after 5s")
        diag = error.to_diagnostic()
        assert diag["severity"] == "ERROR"
        assert diag["category"] == "timeout"
        assert diag["recoverable"] is True


class TestBackendFailureError:
    """Tests for BackendFailureError."""

    def test_exit_code_is_13(self) -> None:
        error = BackendFailureError("backend internal error")
        assert error.exit_code == ExitCode.BACKEND_FAILURE

    def test_to_diagnostic_with_original_error(self) -> None:
        error = BackendFailureError("backend failed", original_error="NullPointerException")
        diag = error.to_diagnostic()
        assert diag["backend_error"] == "NullPointerException"


class TestErrorTypeFor:
    """Tests for exit code to error type mapping."""

    def test_all_codes_mapped(self) -> None:
        for code in ExitCode:
            error_cls = error_type_for(code)
            assert issubclass(error_cls, BinaryAnalysisError)

    def test_specific_mappings(self) -> None:
        assert error_type_for(ExitCode.INVALID_ARGS) is InvalidArgsError
        assert error_type_for(ExitCode.INVALID_CONFIG) is InvalidConfigError
        assert error_type_for(ExitCode.UNSUPPORTED_FORMAT) is UnsupportedFormatError
        assert error_type_for(ExitCode.PROJECT_NOT_FOUND) is ProjectNotFoundError
        assert error_type_for(ExitCode.BINARY_NOT_FOUND) is BinaryNotFoundError
        assert error_type_for(ExitCode.AMBIGUOUS_SELECTOR) is AmbiguousSelectorError
        assert error_type_for(ExitCode.ENTITY_NOT_FOUND) is EntityNotFoundError
        assert error_type_for(ExitCode.IMPORT_FAILED) is ImportFailedError
        assert error_type_for(ExitCode.ANALYSIS_FAILED) is AnalysisFailedError
        assert error_type_for(ExitCode.OPERATION_TIMEOUT) is OperationTimeoutError
        assert error_type_for(ExitCode.BACKEND_FAILURE) is BackendFailureError
