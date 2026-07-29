"""Canonical enumerations for the binary analysis domain model.

All enums serialize as UPPER_CASE strings in JSON output. Integer ordinals and
lowercase representations are never used.
"""

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


class ProjectState(str, Enum):
    """Lifecycle states for a binary analysis project."""

    CREATED = "CREATED"
    IMPORTED = "IMPORTED"
    ANALYZING = "ANALYZING"
    READY = "READY"
    STALE = "STALE"
    FAILED = "FAILED"


class Confidence(str, Enum):
    """Confidence levels for observations, heuristics, and inferences."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class DiagnosticSeverity(str, Enum):
    """Severity levels for diagnostic entries."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ReferenceKind(str, Enum):
    """Types of cross-references between entities."""

    CALL = "CALL"
    JUMP = "JUMP"
    READ = "READ"
    WRITE = "WRITE"
    DATA = "DATA"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    INDIRECT = "INDIRECT"
    UNKNOWN = "UNKNOWN"


class Endianness(str, Enum):
    """Byte ordering of the target architecture."""

    LITTLE = "LITTLE"
    BIG = "BIG"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class FunctionNameSource(str, Enum):
    """Provenance of a function name."""

    ORIGINAL = "ORIGINAL"
    IMPORTED = "IMPORTED"
    DEBUG = "DEBUG"
    BACKEND_GENERATED = "BACKEND_GENERATED"
    USER_ANNOTATION = "USER_ANNOTATION"
    AGENT_SUGGESTION = "AGENT_SUGGESTION"
    UNKNOWN = "UNKNOWN"


class ImportResolution(str, Enum):
    """Resolution status of an imported symbol."""

    RESOLVED = "RESOLVED"
    PARTIAL = "PARTIAL"
    UNRESOLVED = "UNRESOLVED"


class ReportType(str, Enum):
    """Types of analysis reports that can be generated."""

    TRIAGE = "TRIAGE"
    FOCUSED = "FOCUSED"
    PROJECT = "PROJECT"


class AuditResult(str, Enum):
    """Outcome of an audited operation."""

    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUSED = "REFUSED"
