"""Canonical domain entities as dataclasses.

All entities use typed fields with proper defaults. Every entity can be
serialized to a JSON-compatible dict via asdict() or the schema helpers.
Address objects use the canonical structured format with space, offset,
display, and optional file_offset.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from binary_analysis.domain.enums import (
    AuditResult,
    Confidence,
    DiagnosticSeverity,
    Endianness,
    FunctionNameSource,
    ImportResolution,
    ProjectState,
    ReferenceKind,
    ReportType,
)

# ---------------------------------------------------------------------------
# Canonical Address
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Address:
    """Canonical structured address.

    Attributes:
        space: Address space name (e.g., "ram", "register", "const").
        offset: Hex-prefixed offset string (e.g., "0x4018d0").
        display: Human-readable display form (e.g., "0x4018d0").
        file_offset: Optional byte offset within the file on disk.
    """

    space: str
    offset: str
    display: str
    file_offset: int | None = None

    def __post_init__(self) -> None:
        """Validate offset format."""
        if not self.offset.startswith("0x"):
            raise ValueError(f"Address offset must start with '0x', got: {self.offset!r}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a canonical dict for JSON output."""
        result: dict[str, Any] = {
            "space": self.space,
            "offset": self.offset,
            "display": self.display,
        }
        if self.file_offset is not None:
            result["file_offset"] = self.file_offset
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Address:
        """Deserialize from a canonical dict."""
        return cls(
            space=data["space"],
            offset=data["offset"],
            display=data["display"],
            file_offset=data.get("file_offset"),
        )


# ---------------------------------------------------------------------------
# Domain Entities
# ---------------------------------------------------------------------------


@dataclass
class Project:
    """Persistent analysis workspace.

    Identity: UUID.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    state: ProjectState = ProjectState.CREATED
    created_at: str = ""
    updated_at: str = ""
    workspace_version: str = "1"
    binary_count: int = 0
    is_stale: bool = False
    lock: dict[str, Any] | None = None
    description: str | None = None
    max_binary_size_bytes: int | None = None


@dataclass
class Binary:
    """Imported artifact identified by SHA-256.

    Identity: UUID + SHA-256.
    """

    id: UUID = field(default_factory=uuid4)
    sha256: str = ""
    path: str = ""
    format: str = ""
    import_mode: str = "copy"
    size_bytes: int = 0
    architecture: str | None = None
    endianness: Endianness | None = None
    entry_point: Address | None = None
    compiler: str | None = None
    source_language: str | None = None
    imported_at: str | None = None
    analyzed_at: str | None = None
    analysis_profile: str | None = None
    is_stale: bool = False


@dataclass
class Section:
    """Mapped code or data region within a binary.

    Identity: Name + binary ID.
    """

    name: str = ""
    binary_id: UUID | None = None
    address: Address | None = None
    virtual_size: int = 0
    raw_size: int = 0
    flags: list[str] = field(default_factory=list)
    entropy: float | None = None
    content_hash: str | None = None


@dataclass
class EntryPoint:
    """Process, library, boot, or firmware entry point.

    Identity: Address within binary.
    """

    address: Address | None = None
    kind: str = "unknown"
    confidence: Confidence = Confidence.UNKNOWN
    name: str | None = None
    binary_id: UUID | None = None


@dataclass
class Import:
    """External dependency symbol.

    Identity: Address within binary.
    """

    module: str = ""
    symbol: str = ""
    address: Address | None = None
    resolution: ImportResolution = ImportResolution.UNRESOLVED
    ordinal: int | None = None
    binary_id: UUID | None = None


@dataclass
class Export:
    """Public symbol or forwarder.

    Identity: Address or ordinal.
    """

    name: str = ""
    address: Address | None = None
    ordinal: int | None = None
    forwarder: str | None = None
    kind: str = "function"
    binary_id: UUID | None = None


@dataclass
class Symbol:
    """Named entity with source and scope.

    Identity: Address within binary.
    """

    name: str = ""
    address: Address | None = None
    source: FunctionNameSource = FunctionNameSource.UNKNOWN
    scope: str = "unknown"
    binary_id: UUID | None = None


@dataclass
class String:
    """Decoded string at a specific address.

    Identity: Address + encoding + length.
    """

    text: str = ""
    encoding: str = "ASCII"
    address: Address | None = None
    length: int = 0
    binary_id: UUID | None = None


@dataclass
class Function:
    """Callable code region.

    Identity: Binary ID + entry address.
    """

    name: str = ""
    address: Address | None = None
    size_bytes: int = 0
    confidence: Confidence = Confidence.UNKNOWN
    name_source: FunctionNameSource = FunctionNameSource.UNKNOWN
    binary_id: UUID | None = None
    is_external: bool = False
    is_thunk: bool = False
    signature: str | None = None
    source_language: str | None = None
    basic_block_count: int | None = None
    instruction_count: int | None = None
    cyclomatic_complexity: int | None = None


@dataclass
class Instruction:
    """Canonical machine instruction.

    Identity: Address within function.
    """

    mnemonic: str = ""
    operands: str = ""
    bytes_hex: str = ""
    address: Address | None = None
    size_bytes: int = 0
    function_id: str | None = None


@dataclass
class BasicBlock:
    """Control-flow node within a function.

    Identity: Start address within function.
    """

    start_address: Address | None = None
    end_address: Address | None = None
    instruction_count: int = 0
    function_id: str | None = None
    is_entry: bool = False
    is_exit: bool = False


@dataclass
class Reference:
    """Directed call, jump, read, write, or data relation.

    Identity: Address pair + kind.
    """

    from_addr: Address | None = None
    to_addr: Address | None = None
    kind: ReferenceKind = ReferenceKind.UNKNOWN
    confidence: Confidence = Confidence.UNKNOWN
    binary_id: UUID | None = None


@dataclass
class CallGraph:
    """Bounded call graph rooted at a function.

    Identity: Derived from function references.
    """

    root_address: Address | None = None
    nodes: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)
    max_depth: int = 3
    total_nodes: int = 0
    total_edges: int = 0
    truncated: bool = False
    binary_id: UUID | None = None


@dataclass
class Diagnostic:
    """Warning or limitation from an analysis run.

    Identity: Unique within analysis run.
    """

    severity: DiagnosticSeverity = DiagnosticSeverity.INFO
    category: str = ""
    message: str = ""
    component: str | None = None
    remediation: str | None = None
    recoverable: bool = True


@dataclass
class Capability:
    """Rule-derived functional indicator.

    Identity: Name within binary.
    """

    name: str = ""
    confidence: Confidence = Confidence.UNKNOWN
    evidence: list[dict[str, Any]] = field(default_factory=list)
    binary_id: UUID | None = None


@dataclass
class Observation:
    """Direct deterministic fact from analysis.

    Identity: Unique within analysis run.
    """

    category: str = ""
    description: str = ""
    source: str = ""
    address: Address | None = None
    evidence: Any | None = None
    binary_id: UUID | None = None


@dataclass
class Heuristic:
    """Rule-derived interpretation with confidence.

    Identity: Name within analysis run.
    """

    name: str = ""
    description: str = ""
    confidence: Confidence = Confidence.UNKNOWN
    rule_id: str | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    binary_id: UUID | None = None


@dataclass
class Inference:
    """Agent-generated interpretation.

    Identity: Unique within analysis run.
    """

    description: str = ""
    confidence: Confidence = Confidence.UNKNOWN
    basis: list[str] = field(default_factory=list)
    binary_id: UUID | None = None


@dataclass
class Unknown:
    """Explicit unresolved question.

    Identity: Address within binary.
    """

    address: Address | None = None
    question: str = ""
    category: str | None = None
    binary_id: UUID | None = None


@dataclass
class Report:
    """Durable handoff artifact.

    Identity: UUID.
    """

    id: UUID = field(default_factory=uuid4)
    report_type: ReportType = ReportType.TRIAGE
    project_id: UUID | None = None
    binary_id: UUID | None = None
    created_at: str = ""
    format: str = "json"
    summary: str | None = None
    sections: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class AuditEvent:
    """Append-only provenance event.

    Identity: Timestamp sequence.
    """

    timestamp: str = ""
    event_type: str = ""
    result: AuditResult = AuditResult.SUCCESS
    project_id: UUID | None = None
    binary_id: UUID | None = None
    user: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
