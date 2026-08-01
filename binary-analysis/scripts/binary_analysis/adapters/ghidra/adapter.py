"""GhidraAdapter — bridges the canonical domain model to PyGhidra/Ghidra.

Implements the BackendAdapter interface using PyGhidra for JVM interaction
and Ghidra API calls. This is a skeleton implementation at this stage;
full analysis methods are deferred to subsequent features.

Key characteristics:
- PROJECT_SERIALIZED concurrency: only one operation per project at a time
- Error normalization: Ghidra/Java exceptions mapped to canonical error types
- Capability detection: reports available formats, analyzers, and limitations
- Idempotent initialization: safe to call initialize() multiple times
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from binary_analysis.adapters.base import (
    AnalysisProfile,
    AnalysisResult,
    BackendAdapter,
    BinaryMetadata,
    CallEdge,
    ConcurrencyMode,
    DecompilationResult,
)
from binary_analysis.adapters.ghidra.bridge import (
    ensure_initialized,
    get_ghidra_version,
    is_pyghidra_available,
)
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

logger = logging.getLogger("binary_analysis.adapters.ghidra.adapter")


class GhidraAdapter(BackendAdapter):
    """Ghidra backend adapter via PyGhidra.

    Concurrency: PROJECT_SERIALIZED.

    Skeleton implementation — structural queries, decompile, disassemble,
    and analysis methods raise NotImplementedError until fully implemented
    in subsequent features. initialize(), capabilities(), and
    available_profiles() are functional with capability detection.
    """

    # ------------------------------------------------------------------
    # Built-in analysis profiles
    # ------------------------------------------------------------------

    DEFAULT_PROFILES: ClassVar[list[AnalysisProfile]] = [
        AnalysisProfile(
            name="standard",
            description=(
                "Standard analysis: auto-analysis with function discovery, "
                "reference analysis, decompiler parameter ID, and data type propagation"
            ),
            analysers=[
                "function_start",
                "function_id",
                "references",
                "data_type_propagation",
                "decompiler_parameter_id",
                "stack_analysis",
            ],
        ),
        AnalysisProfile(
            name="quick",
            description=("Quick analysis: function discovery and basic reference analysis only"),
            analysers=[
                "function_start",
                "function_id",
                "references",
            ],
        ),
        AnalysisProfile(
            name="deep",
            description=(
                "Deep analysis: full auto-analysis plus decompiler, callgraph, "
                "and cross-reference analysis"
            ),
            analysers=[
                "function_start",
                "function_id",
                "references",
                "data_type_propagation",
                "decompiler_parameter_id",
                "stack_analysis",
                "decompiler",
                "callgraph",
                "xrefs",
                "string_analysis",
                "constant_propagation",
            ],
        ),
    ]

    # ------------------------------------------------------------------
    # Supported formats (reported by Ghidra)
    # ------------------------------------------------------------------

    _SUPPORTED_FORMATS: tuple[str, ...] = (
        "PE",
        "ELF",
        "Mach-O",
        "COFF",
        "NES",
        "RAW",
        "MIPS",
        "Intel Hex",
        "Motorola SREC",
        "DOS MZ",
    )

    _SUPPORTED_ARCHITECTURES: tuple[str, ...] = (
        "x86",
        "x86-64",
        "ARM",
        "ARM-64",
        "MIPS",
        "MIPS-64",
        "PowerPC",
        "PowerPC-64",
        "SPARC",
        "6502",
        "Z80",
        "Java Bytecode",
        "Dalvik",
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def concurrency(self) -> ConcurrencyMode:
        """Ghidra requires project-level serialization.

        Only one operation per Ghidra project at a time. This is because
        Ghidra's ProgramDB is not thread-safe and Ghidra projects lock
        at the program level.
        """
        return ConcurrencyMode.PROJECT_SERIALIZED

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Initialize the Ghidra backend.

        Starts the JVM and initializes Ghidra in headless mode.
        Safe to call multiple times (idempotent).

        Raises:
            RuntimeError: If PyGhidra is not available or JVM startup fails.
        """
        if not is_pyghidra_available():
            raise RuntimeError(
                "PyGhidra is not available. Run 'binary doctor' to diagnose "
                "or 'binary bootstrap --apply' to install dependencies."
            )
        ensure_initialized()
        logger.info("GhidraAdapter initialized")

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(self) -> dict[str, Any]:
        """Return the Ghidra backend's capabilities.

        Reports:
        - Supported binary formats
        - Supported architectures
        - Available analyzers (by profile)
        - Backend version
        - Concurrency model
        - PyGhidra status
        - JVM status

        Returns:
            A dict describing capabilities, formats, and limitations.
        """
        version = get_ghidra_version()
        jvm_ready = ensure_initialized()

        return {
            "backend": "Ghidra",
            "backend_version": version or "unknown",
            "adapter": "GhidraAdapter",
            "adapter_version": "0.1.0",
            "concurrency": self.concurrency.value,
            "pyghidra_available": is_pyghidra_available(),
            "jvm_initialized": jvm_ready,
            "formats": list(self._SUPPORTED_FORMATS),
            "architectures": list(self._SUPPORTED_ARCHITECTURES),
            "profiles": [
                {
                    "name": p.name,
                    "description": p.description,
                    "analyser_count": len(p.analysers),
                }
                for p in self.DEFAULT_PROFILES
            ],
            "limitations": [
                "Skeleton implementation — structural queries and analysis "
                "methods deferred to subsequent features",
                "Single-project concurrency (PROJECT_SERIALIZED)",
                "Headless mode only — no GUI interaction",
            ],
        }

    def available_profiles(self) -> list[AnalysisProfile]:
        """Return the list of available analysis profiles.

        Returns:
            List of built-in Ghidra analysis profiles.
        """
        return list(self.DEFAULT_PROFILES)

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def import_binary(self, path: str, project: Project) -> Binary:
        """Import a binary into Ghidra. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra binary import is deferred to subsequent features")

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyze(self, binary: Binary, profile: AnalysisProfile) -> AnalysisResult:
        """Run analysis on an imported binary. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra analysis is deferred to subsequent features")

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_metadata(self, binary: Binary) -> BinaryMetadata:
        """Return canonical metadata. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra metadata query is deferred to subsequent features")

    # ------------------------------------------------------------------
    # Structural queries
    # ------------------------------------------------------------------

    def get_sections(self, binary: Binary) -> list[Section]:
        """Return all sections in the binary. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra section query is deferred to subsequent features")

    def get_entrypoints(self, binary: Binary) -> list[EntryPoint]:
        """Return all entry points. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra entrypoints query is deferred to subsequent features")

    def get_imports(self, binary: Binary) -> list[Import]:
        """Return all imported symbols. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra imports query is deferred to subsequent features")

    def get_exports(self, binary: Binary) -> list[Export]:
        """Return all exported symbols. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra exports query is deferred to subsequent features")

    def get_symbols(self, binary: Binary) -> list[Symbol]:
        """Return all symbols. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra symbols query is deferred to subsequent features")

    def get_strings(
        self,
        binary: Binary,
        min_length: int = 4,
        contains: str | None = None,
        encoding_filter: str | None = None,
    ) -> list[String]:
        """Return decoded strings. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra strings query is deferred to subsequent features")

    def get_functions(
        self,
        binary: Binary,
        exclude_external: bool = True,
        exclude_thunks: bool = True,
    ) -> list[Function]:
        """Return all functions. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra functions query is deferred to subsequent features")

    # ------------------------------------------------------------------
    # Focused analysis
    # ------------------------------------------------------------------

    def decompile(self, binary: Binary, function: Function) -> DecompilationResult:
        """Decompile a function. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra decompile is deferred to subsequent features")

    def disassemble(
        self, binary: Binary, start_address: Address, end_address: Address
    ) -> list[Instruction]:
        """Disassemble instructions in an address range. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra disassembly is deferred to subsequent features")

    def read_bytes(self, binary: Binary, address: Address, length: int) -> tuple[bytes, int]:
        """Read raw bytes. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra byte reading is deferred to subsequent features")

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------

    def get_xrefs(self, binary: Binary, address: Address) -> list[Reference]:
        """Return cross-references. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra xrefs query is deferred to subsequent features")

    def get_callers(self, binary: Binary, function: Function) -> list[CallEdge]:
        """Return functions that call the given function. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra callers query is deferred to subsequent features")

    def get_callees(self, binary: Binary, function: Function) -> list[CallEdge]:
        """Return functions called by the given function. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra callees query is deferred to subsequent features")

    def get_callgraph(self, binary: Binary, function: Function, max_depth: int = 3) -> CallGraph:
        """Build a call graph. SKELETON — deferred.

        Raises:
            NotImplementedError: Full implementation deferred.
        """
        raise NotImplementedError("Ghidra callgraph is deferred to subsequent features")
