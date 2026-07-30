"""PyGhidra bridge layer — JVM startup and Ghidra API translation.

Provides safe, idempotent initialization of the Ghidra headless environment
and utilities for translating Ghidra exceptions to canonical error types.

This module is the only place in the codebase that imports PyGhidra.
All other modules interact with Ghidra through the adapter boundary.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from binary_analysis.domain.enums import ExitCode
from binary_analysis.domain.errors import (
    AnalysisFailedError,
    BackendFailureError,
    ImportFailedError,
    OperationTimeoutError,
    UnsupportedFormatError,
)

logger = logging.getLogger("binary_analysis.adapters.ghidra.bridge")

# ---------------------------------------------------------------------------
# State tracking
# ---------------------------------------------------------------------------

_initialized: bool = False
_pyghidra_available: bool | None = None
_ghidra_version: str | None = None


def is_pyghidra_available() -> bool:
    """Check whether PyGhidra can be imported.

    Returns:
        True if PyGhidra is importable and JAVA_HOME/GHIDRA_INSTALL_DIR
        are configured.
    """
    global _pyghidra_available

    if _pyghidra_available is not None:
        return _pyghidra_available

    # Check environment variables
    java_home = os.environ.get("JAVA_HOME")
    ghidra_install = os.environ.get("GHIDRA_INSTALL_DIR")

    if not java_home or not ghidra_install:
        logger.debug("PyGhidra not available: JAVA_HOME and/or GHIDRA_INSTALL_DIR not set")
        _pyghidra_available = False
        return False

    try:
        import pyghidra  # noqa: F401

        _pyghidra_available = True
        return True
    except ImportError:
        logger.debug("PyGhidra not available: import failed")
        _pyghidra_available = False
        return False


def get_ghidra_version() -> str | None:
    """Return the Ghidra version string if available.

    The version is read from the Ghidra application.properties file
    or set during initialization.
    """
    global _ghidra_version

    if _ghidra_version is not None:
        return _ghidra_version

    ghidra_install = os.environ.get("GHIDRA_INSTALL_DIR", "")
    props_path = os.path.join(ghidra_install, "Ghidra", "application.properties")
    if os.path.isfile(props_path):
        try:
            with open(props_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("application.version="):
                        _ghidra_version = line.split("=", 1)[1].strip()
                        return _ghidra_version
        except OSError:
            logger.debug("Could not read Ghidra application.properties")
    return None


def start_jvm(headless: bool = True) -> None:
    """Start the JVM and initialize Ghidra in headless mode.

    This is the safe entry point for PyGhidra initialization. It handles:
    - Verifying JAVA_HOME and GHIDRA_INSTALL_DIR
    - Starting the JVM with appropriate memory settings
    - Initializing Ghidra in headless mode

    Args:
        headless: If True, initialize Ghidra in headless mode (no GUI).

    Raises:
        RuntimeError: If PyGhidra is not available or JVM startup fails.
    """
    global _initialized

    if _initialized:
        return

    if not is_pyghidra_available():
        raise RuntimeError(
            "PyGhidra is not available. Ensure JAVA_HOME and GHIDRA_INSTALL_DIR "
            "are set, and PyGhidra is installed."
        )

    try:
        import pyghidra

        pyghidra.start()
        _initialized = True
        _ghidra_version = get_ghidra_version()
        logger.info("Ghidra JVM started successfully (version: %s)", _ghidra_version)
    except Exception as e:
        logger.error("Failed to start Ghidra JVM: %s", e)
        raise RuntimeError(f"Failed to start Ghidra JVM: {e}") from e


def ensure_initialized() -> bool:
    """Ensure PyGhidra is initialized, starting the JVM if necessary.

    Returns:
        True if initialization succeeded or was already done,
        False if PyGhidra is not available.
    """
    global _initialized

    if _initialized:
        return True

    try:
        start_jvm(headless=True)
        return True
    except RuntimeError:
        return False


def is_initialized() -> bool:
    """Return whether the Ghidra JVM has been started."""
    return _initialized


# ---------------------------------------------------------------------------
# Ghidra error normalization
# ---------------------------------------------------------------------------

# Mapping of Ghidra exception class names to canonical error factories.
# Each entry is (exception_class_name_prefix, error_factory).
_GHIDRA_ERROR_MAP: list[tuple[str, Any]] = []


def _build_error_map() -> list[tuple[str, Any]]:
    """Build the Ghidra error-to-canonical mapping lazily."""
    if _GHIDRA_ERROR_MAP:
        return _GHIDRA_ERROR_MAP

    _GHIDRA_ERROR_MAP.extend(
        [
            (
                "CancelledException",
                lambda msg, orig: OperationTimeoutError(f"Operation cancelled: {msg}"),
            ),
            (
                "TimeoutException",
                lambda msg, orig: OperationTimeoutError(f"Operation timed out: {msg}"),
            ),
            (
                "UnsupportedLanguageException",
                lambda msg, orig: UnsupportedFormatError(f"Unsupported language or format: {msg}"),
            ),
            (
                "DomainFileException",
                lambda msg, orig: ImportFailedError(f"Domain file error: {msg}"),
            ),
            (
                "PortableExecutableException",
                lambda msg, orig: ImportFailedError(f"PE import error: {msg}"),
            ),
            (
                "ELFException",
                lambda msg, orig: ImportFailedError(f"ELF import error: {msg}"),
            ),
            (
                "MachException",
                lambda msg, orig: ImportFailedError(f"Mach-O import error: {msg}"),
            ),
            (
                "AssertException",
                lambda msg, orig: AnalysisFailedError(f"Ghidra assertion failed: {msg}"),
            ),
            (
                "IOException",
                lambda msg, orig: BackendFailureError(
                    f"Ghidra I/O error: {msg}", original_error=str(orig)
                ),
            ),
            (
                "RuntimeException",
                lambda msg, orig: BackendFailureError(
                    f"Ghidra runtime error: {msg}", original_error=str(orig)
                ),
            ),
        ]
    )
    return _GHIDRA_ERROR_MAP


def normalize_error(error: Exception) -> Any:
    """Map a Ghidra or Java exception to a canonical error type.

    Uses class name matching against known Ghidra error types. Falls back
    to BackendFailureError for unrecognized exceptions.

    Args:
        error: The exception raised by Ghidra/PyGhidra/JVM.

    Returns:
        A BinaryAnalysisError subclass instance with the appropriate
        exit code and message.
    """
    error_map = _build_error_map()
    error_name = type(error).__name__
    error_msg = str(error)

    for prefix, factory in error_map:
        if prefix in error_name:
            return factory(error_msg, error)

    # Fallback: generic backend failure
    return BackendFailureError(
        f"Unexpected Ghidra error ({error_name}): {error_msg}",
        original_error=error_msg,
    )


def map_exit_code_to_error(ghidra_exception: Exception) -> ExitCode:
    """Map a Ghidra exception to the appropriate canonical exit code.

    Args:
        ghidra_exception: The Ghidra/Java exception.

    Returns:
        The canonical ExitCode for this error class.
    """
    error = normalize_error(ghidra_exception)
    return ExitCode(error.exit_code)


# ---------------------------------------------------------------------------
# Ghidra API translation utilities (skeleton)
# ---------------------------------------------------------------------------


def translate_program_to_binary(program: Any) -> dict[str, Any]:
    """Translate a Ghidra Program object to a canonical binary dict.

    Skeleton only — returns minimal metadata. Full translation deferred
    to subsequent features.

    Args:
        program: A Ghidra Program object.

    Returns:
        A dict with basic binary identity fields.
    """
    raise NotImplementedError("Full Ghidra API translation is deferred to subsequent features")


def translate_function_manager(program: Any) -> list[dict[str, Any]]:
    """Translate Ghidra's FunctionManager data to canonical function dicts.

    Skeleton only — deferred to subsequent features.
    """
    raise NotImplementedError("Full Ghidra API translation is deferred to subsequent features")
