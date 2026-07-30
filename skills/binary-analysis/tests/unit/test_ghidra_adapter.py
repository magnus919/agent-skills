"""Unit tests for the GhidraAdapter skeleton.

Tests cover:
- GhidraAdapter is a proper BackendAdapter subclass
- PROJECT_SERIALIZED concurrency declaration
- Capability detection reports available formats and profiles
- available_profiles() returns all three profiles
- validate_profile() accepts valid and rejects unknown profiles
- initialize() raises RuntimeError when PyGhidra not available
- Skeleton methods raise NotImplementedError with appropriate messages
- Error normalization maps Ghidra exceptions to canonical error types
- Bridge: PyGhidra availability detection
- Bridge: Ghidra version detection
- Bridge: JVM initialization guards
"""

from __future__ import annotations

from typing import ClassVar

import pytest
from binary_analysis.adapters.base import (
    AnalysisProfile,
    BackendAdapter,
    ConcurrencyMode,
)
from binary_analysis.adapters.ghidra.adapter import GhidraAdapter
from binary_analysis.adapters.ghidra.bridge import (
    ensure_initialized,
    get_ghidra_version,
    is_initialized,
    is_pyghidra_available,
    normalize_error,
)
from binary_analysis.domain.entities import (
    Address,
    Binary,
    Function,
    Project,
)
from binary_analysis.domain.enums import ExitCode
from binary_analysis.domain.errors import (
    AnalysisFailedError,
    BackendFailureError,
    ImportFailedError,
    OperationTimeoutError,
    UnsupportedFormatError,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def adapter() -> GhidraAdapter:
    """Return a fresh GhidraAdapter instance."""
    return GhidraAdapter()


# ---------------------------------------------------------------------------
# BackendAdapter interface compliance
# ---------------------------------------------------------------------------


class TestInterfaceCompliance:
    """Verify GhidraAdapter properly implements BackendAdapter."""

    def test_subclass_of_backend_adapter(self, adapter: GhidraAdapter) -> None:
        """GhidraAdapter must subclass BackendAdapter."""
        assert isinstance(adapter, BackendAdapter)

    def test_concurrency_is_project_serialized(self, adapter: GhidraAdapter) -> None:
        """GhidraAdapter must declare PROJECT_SERIALIZED concurrency."""
        assert adapter.concurrency == ConcurrencyMode.PROJECT_SERIALIZED

    def test_has_all_required_methods(self, adapter: GhidraAdapter) -> None:
        """GhidraAdapter must have all BackendAdapter abstract methods.

        Checks that all methods from the abstract interface exist and
        are callable (raising NotImplementedError is acceptable for
        skeleton methods).
        """
        required_methods = [
            "initialize",
            "capabilities",
            "available_profiles",
            "validate_profile",
            "import_binary",
            "analyze",
            "get_metadata",
            "get_sections",
            "get_entrypoints",
            "get_imports",
            "get_exports",
            "get_symbols",
            "get_strings",
            "get_functions",
            "decompile",
            "disassemble",
            "read_bytes",
            "get_xrefs",
            "get_callers",
            "get_callees",
            "get_callgraph",
        ]
        for method_name in required_methods:
            method = getattr(adapter, method_name, None)
            assert method is not None, f"Missing method: {method_name}"
            assert callable(method), f"Method not callable: {method_name}"

    def test_concurrency_property_is_enum(self, adapter: GhidraAdapter) -> None:
        """concurrency property must return a ConcurrencyMode enum value."""
        mode = adapter.concurrency
        assert isinstance(mode, ConcurrencyMode)
        assert mode.value == "PROJECT_SERIALIZED"


# ---------------------------------------------------------------------------
# Capability detection
# ---------------------------------------------------------------------------


class TestCapabilities:
    """Verify capability detection reports correct information."""

    def test_capabilities_returns_expected_structure(self, adapter: GhidraAdapter) -> None:
        """capabilities() must have all required top-level keys."""
        caps = adapter.capabilities()
        required_keys = {
            "backend",
            "backend_version",
            "adapter",
            "adapter_version",
            "concurrency",
            "pyghidra_available",
            "jvm_initialized",
            "formats",
            "architectures",
            "profiles",
            "limitations",
        }
        for key in required_keys:
            assert key in caps, f"Missing capability key: {key}"

    def test_capabilities_backend_is_ghidra(self, adapter: GhidraAdapter) -> None:
        """backend field must always be 'Ghidra'."""
        caps = adapter.capabilities()
        assert caps["backend"] == "Ghidra"

    def test_capabilities_adapter_name(self, adapter: GhidraAdapter) -> None:
        """adapter field must be 'GhidraAdapter'."""
        caps = adapter.capabilities()
        assert caps["adapter"] == "GhidraAdapter"

    def test_capabilities_concurrency(self, adapter: GhidraAdapter) -> None:
        """concurrency field must match PROJECT_SERIALIZED."""
        caps = adapter.capabilities()
        assert caps["concurrency"] == "PROJECT_SERIALIZED"

    def test_capabilities_formats_is_list(self, adapter: GhidraAdapter) -> None:
        """formats must be a non-empty list of format strings."""
        caps = adapter.capabilities()
        assert isinstance(caps["formats"], list)
        assert len(caps["formats"]) > 0
        assert all(isinstance(f, str) for f in caps["formats"])

    def test_capabilities_architectures_is_list(self, adapter: GhidraAdapter) -> None:
        """architectures must be a non-empty list of architecture strings."""
        caps = adapter.capabilities()
        assert isinstance(caps["architectures"], list)
        assert len(caps["architectures"]) > 0
        assert all(isinstance(a, str) for a in caps["architectures"])

    def test_capabilities_profiles_is_list(self, adapter: GhidraAdapter) -> None:
        """profiles must be a non-empty list of profile dicts."""
        caps = adapter.capabilities()
        assert isinstance(caps["profiles"], list)
        assert len(caps["profiles"]) > 0
        for profile in caps["profiles"]:
            assert "name" in profile
            assert "description" in profile
            assert "analyser_count" in profile

    def test_capabilities_profiles_include_standard_quick_deep(
        self, adapter: GhidraAdapter
    ) -> None:
        """profiles must include standard, quick, and deep."""
        caps = adapter.capabilities()
        profile_names = {p["name"] for p in caps["profiles"]}
        assert "standard" in profile_names
        assert "quick" in profile_names
        assert "deep" in profile_names

    def test_capabilities_limitations_is_list(self, adapter: GhidraAdapter) -> None:
        """limitations must be a list of strings."""
        caps = adapter.capabilities()
        assert isinstance(caps["limitations"], list)
        assert len(caps["limitations"]) > 0
        assert all(isinstance(item, str) for item in caps["limitations"])

    def test_capabilities_pyghidra_available_is_bool(self, adapter: GhidraAdapter) -> None:
        """pyghidra_available must be a boolean."""
        caps = adapter.capabilities()
        assert isinstance(caps["pyghidra_available"], bool)

    def test_capabilities_jvm_initialized_is_bool(self, adapter: GhidraAdapter) -> None:
        """jvm_initialized must be a boolean."""
        caps = adapter.capabilities()
        assert isinstance(caps["jvm_initialized"], bool)


# ---------------------------------------------------------------------------
# Available profiles
# ---------------------------------------------------------------------------


class TestAvailableProfiles:
    """Verify available_profiles() returns correct profiles."""

    def test_available_profiles_returns_three(self, adapter: GhidraAdapter) -> None:
        """available_profiles() must return exactly 3 profiles."""
        profiles = adapter.available_profiles()
        assert len(profiles) == 3

    def test_available_profiles_are_analysis_profiles(self, adapter: GhidraAdapter) -> None:
        """All returned profiles must be AnalysisProfile instances."""
        profiles = adapter.available_profiles()
        for p in profiles:
            assert isinstance(p, AnalysisProfile)

    def test_available_profiles_names(self, adapter: GhidraAdapter) -> None:
        """Profile names must be standard, quick, and deep."""
        profiles = adapter.available_profiles()
        names = {p.name for p in profiles}
        assert names == {"standard", "quick", "deep"}

    def test_available_profiles_have_analysers(self, adapter: GhidraAdapter) -> None:
        """Each profile must have a non-empty analysers list."""
        profiles = adapter.available_profiles()
        for p in profiles:
            assert len(p.analysers) > 0, f"Profile {p.name} has no analysers"

    def test_available_profiles_have_descriptions(self, adapter: GhidraAdapter) -> None:
        """Each profile must have a non-empty description."""
        profiles = adapter.available_profiles()
        for p in profiles:
            assert p.description, f"Profile {p.name} has no description"

    def test_available_profiles_standard_has_function_analysers(
        self, adapter: GhidraAdapter
    ) -> None:
        """Standard profile must include function_start and function_id."""
        for p in adapter.available_profiles():
            if p.name == "standard":
                assert "function_start" in p.analysers
                assert "function_id" in p.analysers
                break


# ---------------------------------------------------------------------------
# Profile validation
# ---------------------------------------------------------------------------


class TestProfileValidation:
    """Verify validate_profile() (inherited from BackendAdapter)."""

    def test_validate_known_profile_returns_profile(self, adapter: GhidraAdapter) -> None:
        """validate_profile with a known name must return the AnalysisProfile."""
        profile = adapter.validate_profile("standard")
        assert isinstance(profile, AnalysisProfile)
        assert profile.name == "standard"

    def test_validate_unknown_profile_raises_valueerror(self, adapter: GhidraAdapter) -> None:
        """validate_profile with an unknown name must raise ValueError."""
        with pytest.raises(ValueError, match="Unknown analysis profile"):
            adapter.validate_profile("nonexistent")

    def test_validate_profile_error_lists_available(self, adapter: GhidraAdapter) -> None:
        """validate_profile error message must list available profiles."""
        with pytest.raises(ValueError) as excinfo:
            adapter.validate_profile("bogus")
        error_msg = str(excinfo.value)
        assert "standard" in error_msg
        assert "quick" in error_msg
        assert "deep" in error_msg

    def test_validate_all_three_profiles_pass(self, adapter: GhidraAdapter) -> None:
        """validate_profile must accept standard, quick, and deep."""
        for name in ("standard", "quick", "deep"):
            profile = adapter.validate_profile(name)
            assert profile.name == name


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestInitialize:
    """Verify initialize() behavior."""

    def test_initialize_raises_when_pyghidra_unavailable(self, adapter: GhidraAdapter) -> None:
        """initialize() must raise RuntimeError when PyGhidra not installed."""
        # We don't have PyGhidra in the default test environment.
        if not is_pyghidra_available():
            with pytest.raises(RuntimeError, match="PyGhidra is not available"):
                adapter.initialize()


# ---------------------------------------------------------------------------
# Skeleton methods raise NotImplementedError
# ---------------------------------------------------------------------------


class TestSkeletonMethods:
    """Verify skeleton methods raise NotImplementedError."""

    _SKELETON_METHODS: ClassVar = [
        ("import_binary", ("/fake/path", Project(name="test")), {}),
        ("analyze", (Binary(), AnalysisProfile(name="standard")), {}),
        ("get_metadata", (Binary(),), {}),
        ("get_sections", (Binary(),), {}),
        ("get_entrypoints", (Binary(),), {}),
        ("get_imports", (Binary(),), {}),
        ("get_exports", (Binary(),), {}),
        ("get_symbols", (Binary(),), {}),
        ("get_strings", (Binary(),), {}),
        ("get_functions", (Binary(),), {}),
        ("decompile", (Binary(), Function(name="test")), {}),
        (
            "disassemble",
            (
                Binary(),
                Address(space="ram", offset="0x1000", display="0x1000"),
                Address(space="ram", offset="0x2000", display="0x2000"),
            ),
            {},
        ),
        (
            "read_bytes",
            (Binary(), Address(space="ram", offset="0x1000", display="0x1000"), 16),
            {},
        ),
        ("get_xrefs", (Binary(), Address(space="ram", offset="0x1000", display="0x1000")), {}),
        ("get_callers", (Binary(), Function(name="test")), {}),
        ("get_callees", (Binary(), Function(name="test")), {}),
        ("get_callgraph", (Binary(), Function(name="test")), {}),
    ]

    @pytest.mark.parametrize(
        "method_name,args,kwargs",
        _SKELETON_METHODS,
    )
    def test_skeleton_method_raises_not_implemented(
        self,
        adapter: GhidraAdapter,
        method_name: str,
        args: tuple,
        kwargs: dict,
    ) -> None:
        """Skeleton method must raise NotImplementedError."""
        method = getattr(adapter, method_name)
        with pytest.raises(NotImplementedError):
            method(*args, **kwargs)

    def test_import_binary_has_meaningful_message(self, adapter: GhidraAdapter) -> None:
        """NotImplementedError message must reference the deferred method."""
        with pytest.raises(NotImplementedError, match="Ghidra binary import"):
            adapter.import_binary("/test", Project(name="test"))

    def test_decompile_has_meaningful_message(self, adapter: GhidraAdapter) -> None:
        """NotImplementedError message must reference the deferred method."""
        with pytest.raises(NotImplementedError, match="Ghidra decompile"):
            adapter.decompile(Binary(), Function(name="test"))

    def test_disassemble_has_meaningful_message(self, adapter: GhidraAdapter) -> None:
        """NotImplementedError message must reference the deferred method."""
        with pytest.raises(NotImplementedError, match="Ghidra disassembly"):
            adapter.disassemble(
                Binary(),
                Address(space="ram", offset="0x1000", display="0x1000"),
                Address(space="ram", offset="0x2000", display="0x2000"),
            )

    def test_get_callgraph_has_meaningful_message(self, adapter: GhidraAdapter) -> None:
        """NotImplementedError message must reference the deferred method."""
        with pytest.raises(NotImplementedError, match="Ghidra callgraph"):
            adapter.get_callgraph(Binary(), Function(name="test"))


# ---------------------------------------------------------------------------
# Bridge: Error normalization
# ---------------------------------------------------------------------------


class TestErrorNormalization:
    """Verify the bridge's error normalization maps Ghidra exceptions."""

    def test_cancelled_exception_maps_to_timeout(self) -> None:
        """CancelledException must map to OperationTimeoutError."""

        class CancelledException(Exception):
            pass

        err = normalize_error(CancelledException("User cancelled"))
        assert isinstance(err, OperationTimeoutError)
        assert err.exit_code == ExitCode.OPERATION_TIMEOUT

    def test_timeout_exception_maps_to_timeout(self) -> None:
        """TimeoutException must map to OperationTimeoutError."""

        class TimeoutException(Exception):
            pass

        err = normalize_error(TimeoutException("Timed out"))
        assert isinstance(err, OperationTimeoutError)
        assert err.exit_code == ExitCode.OPERATION_TIMEOUT

    def test_unsupported_language_maps_to_unsupported_format(self) -> None:
        """UnsupportedLanguageException must map to UnsupportedFormatError."""

        class UnsupportedLanguageException(Exception):
            pass

        err = normalize_error(UnsupportedLanguageException("Bad arch"))
        assert isinstance(err, UnsupportedFormatError)
        assert err.exit_code == ExitCode.UNSUPPORTED_FORMAT

    def test_domain_file_exception_maps_to_import_failed(self) -> None:
        """DomainFileException must map to ImportFailedError."""

        class DomainFileException(Exception):
            pass

        err = normalize_error(DomainFileException("Corrupt"))
        assert isinstance(err, ImportFailedError)
        assert err.exit_code == ExitCode.IMPORT_FAILED

    def test_pe_exception_maps_to_import_failed(self) -> None:
        """PortableExecutableException must map to ImportFailedError."""

        class PortableExecutableException(Exception):
            pass

        err = normalize_error(PortableExecutableException("Bad PE"))
        assert isinstance(err, ImportFailedError)
        assert err.exit_code == ExitCode.IMPORT_FAILED

    def test_elf_exception_maps_to_import_failed(self) -> None:
        """ELFException must map to ImportFailedError."""

        class ELFException(Exception):
            pass

        err = normalize_error(ELFException("Bad ELF"))
        assert isinstance(err, ImportFailedError)
        assert err.exit_code == ExitCode.IMPORT_FAILED

    def test_mach_exception_maps_to_import_failed(self) -> None:
        """MachException must map to ImportFailedError."""

        class MachException(Exception):
            pass

        err = normalize_error(MachException("Bad Mach-O"))
        assert isinstance(err, ImportFailedError)
        assert err.exit_code == ExitCode.IMPORT_FAILED

    def test_assert_exception_maps_to_analysis_failed(self) -> None:
        """AssertException must map to AnalysisFailedError."""

        class AssertException(Exception):
            pass

        err = normalize_error(AssertException("Assertion failed"))
        assert isinstance(err, AnalysisFailedError)
        assert err.exit_code == ExitCode.ANALYSIS_FAILED

    def test_io_exception_maps_to_backend_failure(self) -> None:
        """IOException must map to BackendFailureError."""

        class IOException(Exception):
            pass

        err = normalize_error(IOException("Disk error"))
        assert isinstance(err, BackendFailureError)
        assert err.exit_code == ExitCode.BACKEND_FAILURE

    def test_runtime_exception_maps_to_backend_failure(self) -> None:
        """RuntimeException must map to BackendFailureError."""

        class RuntimeException(Exception):
            pass

        err = normalize_error(RuntimeException("Unexpected"))
        assert isinstance(err, BackendFailureError)
        assert err.exit_code == ExitCode.BACKEND_FAILURE

    def test_unknown_exception_maps_to_backend_failure(self) -> None:
        """Unrecognized exception must map to BackendFailureError (fallback)."""

        class SomeObscureError(Exception):
            pass

        err = normalize_error(SomeObscureError("Mystery"))
        assert isinstance(err, BackendFailureError)
        assert err.exit_code == ExitCode.BACKEND_FAILURE

    def test_backend_failure_preserves_original_error(self) -> None:
        """BackendFailureError must preserve the original error string."""

        class IOException(Exception):
            pass

        err = normalize_error(IOException("Disk full"))
        assert isinstance(err, BackendFailureError)
        assert err.original_error == "Disk full"

    def test_operation_timeout_message_includes_original(self) -> None:
        """OperationTimeoutError message must reference the original cause."""

        class CancelledException(Exception):
            pass

        err = normalize_error(CancelledException("User hit cancel"))
        assert isinstance(err, OperationTimeoutError)
        assert "User hit cancel" in str(err)


# ---------------------------------------------------------------------------
# Bridge: PyGhidra availability
# ---------------------------------------------------------------------------


class TestPyGhidraAvailability:
    """Verify bridge PyGhidra availability detection."""

    def test_is_pyghidra_available_returns_bool(self) -> None:
        """is_pyghidra_available() must return a boolean."""
        result = is_pyghidra_available()
        assert isinstance(result, bool)

    def test_is_pyghidra_available_is_idempotent(self) -> None:
        """is_pyghidra_available() must return the same result on repeated calls."""
        first = is_pyghidra_available()
        second = is_pyghidra_available()
        assert first == second

    def test_is_initialized_returns_bool(self) -> None:
        """is_initialized() must return a boolean."""
        result = is_initialized()
        assert isinstance(result, bool)

    def test_ensure_initialized_returns_bool(self) -> None:
        """ensure_initialized() must return a boolean (False when PyGhidra unavailable)."""
        result = ensure_initialized()
        assert isinstance(result, bool)

    def test_get_ghidra_version_returns_string_or_none(self) -> None:
        """get_ghidra_version() must return a string or None."""
        version = get_ghidra_version()
        assert version is None or isinstance(version, str)


# ---------------------------------------------------------------------------
# Bridge: error normalization edge cases
# ---------------------------------------------------------------------------


class TestErrorNormalizationEdgeCases:
    """Verify edge cases in error normalization."""

    def test_empty_error_message(self) -> None:
        """Normalizing an exception with no message must still produce an error."""

        class CancelledException(Exception):
            pass

        err = normalize_error(CancelledException())
        assert isinstance(err, OperationTimeoutError)

    def test_nested_class_name_matching(self) -> None:
        """Exception names containing prefix substrings must match correctly."""

        class GhidraCancelledException(Exception):
            pass

        err = normalize_error(GhidraCancelledException("Cancelled"))
        assert isinstance(err, OperationTimeoutError)

    def test_to_diagnostic_on_operation_timeout(self) -> None:
        """OperationTimeoutError.to_diagnostic() must include category and recoverable."""
        err = OperationTimeoutError("Timed out")
        diag = err.to_diagnostic()
        assert diag["severity"] == "ERROR"
        assert diag["category"] == "timeout"
        assert diag["recoverable"] is True

    def test_to_diagnostic_on_backend_failure(self) -> None:
        """BackendFailureError.to_diagnostic() must include backend_error."""
        err = BackendFailureError("JVM crash", original_error="OOM")
        diag = err.to_diagnostic()
        assert diag["severity"] == "ERROR"
        assert diag["backend_error"] == "OOM"
