"""Abstract BackendAdapter interface.

Defines the typed behavioral contract that every backend must implement.
Public commands never branch on backend names; they interact exclusively
through this interface.

The interface is backend-neutral: all inputs and outputs use canonical
domain entities. Backend-native objects never cross this boundary.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from binary_analysis.domain.entities import (
    Address,
    Binary,
    CallGraph,
    EntryPoint,
    Export,
    Function,
    Import,
    Instruction,
    Project,
    Reference,
    Section,
    String,
    Symbol,
)


class ConcurrencyMode(str, Enum):
    """Declares how a backend handles concurrent access."""

    PROJECT_SERIALIZED = "PROJECT_SERIALIZED"
    """Only one operation per project at a time."""


@dataclass
class AnalysisProfile:
    """An analysis profile specification.

    Attributes:
        name: Profile identifier (e.g., "standard", "quick", "deep").
        description: Human-readable description.
        analysers: List of analyser names included in this profile.
    """

    name: str
    description: str = ""
    analysers: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Result of an analysis operation.

    Attributes:
        success: Whether the analysis completed without critical errors.
        partial: Whether some analysers failed while others succeeded.
        completed_analysers: List of analyser names that completed.
        failed_analysers: List of analyser names that failed.
        diagnostics: List of diagnostic entries describing failures.
    """

    success: bool = True
    partial: bool = False
    completed_analysers: list[str] = field(default_factory=list)
    failed_analysers: list[str] = field(default_factory=list)
    diagnostics: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DecompilationResult:
    """Result of decompiling a function.

    Attributes:
        pseudocode: The reconstructed pseudocode (never original source).
        address_map: Maps source line numbers (1-indexed) to canonical address objects.
        diagnostics: List of diagnostic entries.
        language: The source language of the decompilation output (e.g., "c").
    """

    pseudocode: str = ""
    address_map: dict[int, dict[str, Any]] = field(default_factory=dict)
    diagnostics: list[dict[str, Any]] = field(default_factory=list)
    language: str = "c"


@dataclass
class CallEdge:
    """A directed call edge between two functions.

    Attributes:
        from_address: The caller function's entry address.
        to_address: The callee function's entry address.
        from_name: The caller function's name.
        to_name: The callee function's name.
        kind: The kind of call (direct, indirect, etc.).
    """

    from_address: Address | None = None
    to_address: Address | None = None
    from_name: str = ""
    to_name: str = ""
    kind: str = "direct"


@dataclass
class BinaryMetadata:
    """Canonical metadata about a binary, backend-neutral.

    This is a lightweight subset of the Binary entity focused on
    metadata that does not require full analysis.
    """

    format: str = ""
    architecture: str | None = None
    endianness: str | None = None
    size_bytes: int = 0
    entry_point: Address | None = None
    compiler: str | None = None
    source_language: str | None = None


class BackendAdapter(ABC):
    """Abstract interface for all backend adapters.

    Every backend implementation must subclass this and implement
    all abstract methods. The adapter translates backend-specific
    data into canonical domain entities.

    Concurrency is declared via the ``concurrency`` property.
    """

    @property
    @abstractmethod
    def concurrency(self) -> ConcurrencyMode:
        """Declare how this backend handles concurrent access."""
        ...

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the backend (start JVM, load libraries, etc.).

        Must be safe to call multiple times (idempotent).
        """
        ...

    @abstractmethod
    def capabilities(self) -> dict[str, Any]:
        """Return the backend's capabilities.

        Returns:
            A dict describing supported formats, architectures, analyzers,
            and limitations.
        """
        ...

    @abstractmethod
    def available_profiles(self) -> list[AnalysisProfile]:
        """Return the list of available analysis profiles."""
        ...

    def validate_profile(self, profile_name: str) -> AnalysisProfile:
        """Validate that a profile name is known.

        Args:
            profile_name: The profile to validate.

        Returns:
            The matching AnalysisProfile.

        Raises:
            ValueError: If the profile is not available.
        """
        profiles = self.available_profiles()
        for profile in profiles:
            if profile.name == profile_name:
                return profile
        available = [p.name for p in profiles]
        raise ValueError(
            f"Unknown analysis profile: {profile_name!r}. Available: {', '.join(available)}"
        )

    @abstractmethod
    def import_binary(self, path: str, project: Project) -> Binary:
        """Import a binary into the backend.

        Args:
            path: Path to the binary file on disk.
            project: The project this binary belongs to.

        Returns:
            A canonical Binary entity with format, architecture, and
            SHA-256 populated.

        Raises:
            Various backend-specific errors that are normalized to
            canonical error types by the caller.
        """
        ...

    @abstractmethod
    def analyze(self, binary: Binary, profile: AnalysisProfile) -> AnalysisResult:
        """Run analysis on an imported binary.

        Args:
            binary: The canonical Binary entity to analyze.
            profile: The analysis profile to apply.

        Returns:
            An AnalysisResult with completed/failed analysers and diagnostics.
        """
        ...

    @abstractmethod
    def get_metadata(self, binary: Binary) -> BinaryMetadata:
        """Return canonical metadata for a binary.

        Does not require full analysis. Should return whatever info is
        available from the import step (format, architecture, etc.).

        Args:
            binary: The binary to query.

        Returns:
            Backend-neutral metadata.
        """
        ...

    @abstractmethod
    def get_sections(self, binary: Binary) -> list[Section]:
        """Return all sections in the binary.

        Args:
            binary: The binary to query.

        Returns:
            List of canonical Section entities.
        """
        ...

    @abstractmethod
    def get_entrypoints(self, binary: Binary) -> list[EntryPoint]:
        """Return all entry points in the binary.

        Args:
            binary: The binary to query.

        Returns:
            List of canonical EntryPoint entities.
        """
        ...

    @abstractmethod
    def get_imports(self, binary: Binary) -> list[Import]:
        """Return all imported symbols in the binary.

        Args:
            binary: The binary to query.

        Returns:
            List of canonical Import entities.
        """
        ...

    @abstractmethod
    def get_exports(self, binary: Binary) -> list[Export]:
        """Return all exported symbols in the binary.

        Args:
            binary: The binary to query.

        Returns:
            List of canonical Export entities.
        """
        ...

    @abstractmethod
    def get_symbols(self, binary: Binary) -> list[Symbol]:
        """Return all symbols in the binary.

        Args:
            binary: The binary to query.

        Returns:
            List of canonical Symbol entities.
        """
        ...

    @abstractmethod
    def get_strings(
        self,
        binary: Binary,
        min_length: int = 4,
        contains: str | None = None,
        encoding_filter: str | None = None,
    ) -> list[String]:
        """Return all decoded strings in the binary.

        Args:
            binary: The binary to query.
            min_length: Minimum string length to return (default 4).
            contains: Optional substring filter (case-sensitive).
            encoding_filter: Optional encoding filter (e.g., "ASCII", "UTF-16").

        Returns:
            List of canonical String entities.
        """
        ...

    @abstractmethod
    def get_functions(
        self,
        binary: Binary,
        exclude_external: bool = True,
        exclude_thunks: bool = True,
    ) -> list[Function]:
        """Return all functions in the binary.

        Args:
            binary: The binary to query.
            exclude_external: If True, exclude externally defined functions.
            exclude_thunks: If True, exclude thunk functions.

        Returns:
            List of canonical Function entities.
        """
        ...

    @abstractmethod
    def decompile(self, binary: Binary, function: Function) -> DecompilationResult:
        """Decompile a function to pseudocode.

        Args:
            binary: The binary containing the function.
            function: The function to decompile.

        Returns:
            Reconstructed pseudocode with address map and diagnostics.
        """
        ...

    @abstractmethod
    def disassemble(
        self, binary: Binary, start_address: Address, end_address: Address
    ) -> list[Instruction]:
        """Disassemble instructions in an address range.

        Args:
            binary: The binary to disassemble from.
            start_address: Start of the address range (inclusive).
            end_address: End of the address range (inclusive).

        Returns:
            List of canonical Instruction entities.

        Raises:
            ValueError: If the address range is entirely unmapped.
        """
        ...

    @abstractmethod
    def read_bytes(self, binary: Binary, address: Address, length: int) -> tuple[bytes, int]:
        """Read raw bytes from a binary at a given address.

        Args:
            binary: The binary to read from.
            address: The starting address.
            length: The number of bytes to read.

        Returns:
            A tuple of (bytes_read, actual_length). actual_length may be
            less than length if the read crosses a segment boundary.

        Raises:
            ValueError: If the address is not mapped.
        """
        ...

    @abstractmethod
    def get_xrefs(self, binary: Binary, address: Address) -> list[Reference]:
        """Return cross-references to/from an address.

        Args:
            binary: The binary to query.
            address: The address to find references for.

        Returns:
            List of canonical Reference entities.
        """
        ...

    @abstractmethod
    def get_callers(self, binary: Binary, function: Function) -> list[CallEdge]:
        """Return functions that call the given function.

        Args:
            binary: The binary to query.
            function: The target function.

        Returns:
            List of CallEdge entities from callers to the target.
        """
        ...

    @abstractmethod
    def get_callees(self, binary: Binary, function: Function) -> list[CallEdge]:
        """Return functions called by the given function.

        Args:
            binary: The binary to query.
            function: The target function.

        Returns:
            List of CallEdge entities from the target to callees.
        """
        ...

    @abstractmethod
    def get_callgraph(self, binary: Binary, function: Function, max_depth: int = 3) -> CallGraph:
        """Build a call graph rooted at a function.

        Args:
            binary: The binary to query.
            function: The root function.
            max_depth: Maximum depth to traverse (default 3, max 10).

        Returns:
            A bounded CallGraph entity.
        """
        ...
