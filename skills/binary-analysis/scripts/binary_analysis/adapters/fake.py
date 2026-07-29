"""FakeAdapter — a fully controllable in-memory backend adapter for testing.

Implements the BackendAdapter interface with configurable responses:
- Normal data returns for all structural query types
- Import failures (exit code 10), analysis crashes (exit code 11),
  and backend failures (exit code 13)
- Slow operations and timeout simulation
- Unmapped addresses, partial mapping, and truncation
- Custom binary fixtures with deterministic address layouts
"""

from __future__ import annotations

import time
from typing import Any, ClassVar
from uuid import uuid4

from binary_analysis.adapters.base import (
    AnalysisProfile,
    AnalysisResult,
    BackendAdapter,
    BinaryMetadata,
    CallEdge,
    ConcurrencyMode,
    DecompilationResult,
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
from binary_analysis.domain.enums import (
    Confidence,
    Endianness,
    FunctionNameSource,
    ImportResolution,
    ReferenceKind,
)


class FakeAdapter(BackendAdapter):
    """In-memory backend adapter with fully controllable behaviour.

    Usage::

        adapter = FakeAdapter()
        adapter.set_fixture("test-bin", FakeAdapter.pe_fixture())
        adapter.configure_import_failure("test-bin", "Simulated import failure")
        adapter.configure_slow_operation("analyze", 5.0)  # 5-second delay
        adapter.configure_unmapped_range(0x5000, 0x6000)
    """

    # ------------------------------------------------------------------
    # Configuration constants and helpers
    # ------------------------------------------------------------------

    DEFAULT_PROFILES: ClassVar[list[AnalysisProfile]] = [
        AnalysisProfile(
            name="standard",
            description="Standard analysis: functions, sections, strings, symbols, imports/exports",
            analysers=[
                "functions",
                "sections",
                "strings",
                "symbols",
                "imports",
                "exports",
                "entrypoints",
            ],
        ),
        AnalysisProfile(
            name="quick",
            description="Quick analysis: functions and sections only",
            analysers=["functions", "sections"],
        ),
        AnalysisProfile(
            name="deep",
            description="Deep analysis: full decompilation and callgraph",
            analysers=[
                "functions",
                "sections",
                "strings",
                "symbols",
                "imports",
                "exports",
                "entrypoints",
                "decompiler",
                "callgraph",
                "xrefs",
            ],
        ),
    ]

    @property
    def concurrency(self) -> ConcurrencyMode:
        return ConcurrencyMode.PROJECT_SERIALIZED

    # ------------------------------------------------------------------
    # Fixture helpers — pre-built deterministic data sets
    # ------------------------------------------------------------------

    @staticmethod
    def pe_fixture() -> dict[str, Any]:
        """Return a PE fixture with known section/function/import/export layouts.

        Represents a minimal x86 PE executable with:
        - .text, .rdata, .data sections
        - Three functions: main (0x401000), check_password (0x401200), print_message (0x401400)
        - Imports from kernel32.dll and msvcrt.dll
        - Exports: start entrypoint
        """
        return FakeAdapter._build_fixture(
            fmt="PE",
            arch="x86",
            endianness=Endianness.LITTLE,
            sections=[
                {
                    "name": ".text",
                    "address": Address(
                        space="ram", offset="0x401000", display="0x401000", file_offset=1024
                    ),
                    "virtual_size": 8192,
                    "raw_size": 7168,
                    "flags": ["r", "x"],
                    "entropy": 5.92,
                },
                {
                    "name": ".rdata",
                    "address": Address(
                        space="ram", offset="0x403000", display="0x403000", file_offset=8192
                    ),
                    "virtual_size": 4096,
                    "raw_size": 2048,
                    "flags": ["r"],
                    "entropy": 3.14,
                },
                {
                    "name": ".data",
                    "address": Address(
                        space="ram", offset="0x404000", display="0x404000", file_offset=12288
                    ),
                    "virtual_size": 8192,
                    "raw_size": 512,
                    "flags": ["r", "w"],
                    "entropy": 1.87,
                },
            ],
            entrypoints=[
                {
                    "address": Address(
                        space="ram", offset="0x401000", display="0x401000", file_offset=1024
                    ),
                    "kind": "program",
                    "confidence": Confidence.HIGH,
                    "name": "_start",
                },
            ],
            imports=[
                {
                    "module": "kernel32.dll",
                    "symbol": "GetProcAddress",
                    "address": Address(space="ram", offset="0x403100", display="0x403100"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
                {
                    "module": "kernel32.dll",
                    "symbol": "LoadLibraryA",
                    "address": Address(space="ram", offset="0x403108", display="0x403108"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
                {
                    "module": "kernel32.dll",
                    "symbol": "VirtualAlloc",
                    "address": Address(space="ram", offset="0x403110", display="0x403110"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
                {
                    "module": "msvcrt.dll",
                    "symbol": "printf",
                    "address": Address(space="ram", offset="0x403118", display="0x403118"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
                {
                    "module": "msvcrt.dll",
                    "symbol": "scanf",
                    "address": Address(space="ram", offset="0x403120", display="0x403120"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
            ],
            exports=[
                {
                    "name": "_start",
                    "address": Address(space="ram", offset="0x401000", display="0x401000"),
                    "ordinal": 1,
                    "forwarder": None,
                    "kind": "function",
                },
            ],
            symbols=[
                {
                    "name": "main",
                    "address": Address(space="ram", offset="0x401000", display="0x401000"),
                    "source": FunctionNameSource.ORIGINAL,
                    "scope": "global",
                },
                {
                    "name": "check_password",
                    "address": Address(space="ram", offset="0x401200", display="0x401200"),
                    "source": FunctionNameSource.ORIGINAL,
                    "scope": "global",
                },
                {
                    "name": "print_message",
                    "address": Address(space="ram", offset="0x401400", display="0x401400"),
                    "source": FunctionNameSource.ORIGINAL,
                    "scope": "global",
                },
                {
                    "name": "printf",
                    "address": Address(space="ram", offset="0x403118", display="0x403118"),
                    "source": FunctionNameSource.IMPORTED,
                    "scope": "global",
                },
            ],
            strings=[
                {
                    "text": "Enter password: ",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x403200", display="0x403200"),
                    "length": 17,
                },
                {
                    "text": "Access granted!",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x403220", display="0x403220"),
                    "length": 15,
                },
                {
                    "text": "Access denied!",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x403240", display="0x403240"),
                    "length": 14,
                },
                {
                    "text": "kernel32.dll",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x403260", display="0x403260"),
                    "length": 13,
                },
                {
                    "text": "msvcrt.dll",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x403270", display="0x403270"),
                    "length": 10,
                },
            ],
            functions=[
                {
                    "name": "main",
                    "address": Address(space="ram", offset="0x401000", display="0x401000"),
                    "size_bytes": 512,
                    "confidence": Confidence.HIGH,
                    "name_source": FunctionNameSource.ORIGINAL,
                    "is_external": False,
                    "is_thunk": False,
                    "signature": "int main(int argc, char **argv)",
                    "basic_block_count": 12,
                    "instruction_count": 87,
                    "cyclomatic_complexity": 5,
                },
                {
                    "name": "check_password",
                    "address": Address(space="ram", offset="0x401200", display="0x401200"),
                    "size_bytes": 256,
                    "confidence": Confidence.HIGH,
                    "name_source": FunctionNameSource.ORIGINAL,
                    "is_external": False,
                    "is_thunk": False,
                    "signature": "int check_password(const char *input)",
                    "basic_block_count": 5,
                    "instruction_count": 34,
                    "cyclomatic_complexity": 3,
                },
                {
                    "name": "print_message",
                    "address": Address(space="ram", offset="0x401400", display="0x401400"),
                    "size_bytes": 128,
                    "confidence": Confidence.HIGH,
                    "name_source": FunctionNameSource.ORIGINAL,
                    "is_external": False,
                    "is_thunk": False,
                    "signature": "void print_message(const char *msg)",
                    "basic_block_count": 3,
                    "instruction_count": 18,
                    "cyclomatic_complexity": 2,
                },
                {
                    "name": "printf",
                    "address": Address(space="ram", offset="0x403118", display="0x403118"),
                    "size_bytes": 8,
                    "confidence": Confidence.HIGH,
                    "name_source": FunctionNameSource.IMPORTED,
                    "is_external": True,
                    "is_thunk": False,
                    "signature": None,
                },
            ],
        )

    @staticmethod
    def elf_fixture() -> dict[str, Any]:
        """Return an ELF fixture with known section/function/import/export layouts.

        Represents a minimal x86-64 ELF executable with:
        - .text, .rodata, .data, .bss sections
        - Four functions: _start (0x401000), main (0x401100),
          compute_hash (0x401300), parse_input (0x401500)
        - Imports from libc.so.6
        - Exports: main, compute_hash
        """
        return FakeAdapter._build_fixture(
            fmt="ELF",
            arch="x86-64",
            endianness=Endianness.LITTLE,
            sections=[
                {
                    "name": ".text",
                    "address": Address(
                        space="ram", offset="0x401000", display="0x401000", file_offset=4096
                    ),
                    "virtual_size": 16384,
                    "raw_size": 12288,
                    "flags": ["r", "x"],
                    "entropy": 6.12,
                },
                {
                    "name": ".rodata",
                    "address": Address(
                        space="ram", offset="0x405000", display="0x405000", file_offset=16384
                    ),
                    "virtual_size": 4096,
                    "raw_size": 1024,
                    "flags": ["r"],
                    "entropy": 2.87,
                },
                {
                    "name": ".data",
                    "address": Address(
                        space="ram", offset="0x406000", display="0x406000", file_offset=20480
                    ),
                    "virtual_size": 4096,
                    "raw_size": 256,
                    "flags": ["r", "w"],
                    "entropy": 1.45,
                },
                {
                    "name": ".bss",
                    "address": Address(space="ram", offset="0x407000", display="0x407000"),
                    "virtual_size": 8192,
                    "raw_size": 0,
                    "flags": ["r", "w"],
                    "entropy": 0.0,
                },
            ],
            entrypoints=[
                {
                    "address": Address(
                        space="ram", offset="0x401000", display="0x401000", file_offset=4096
                    ),
                    "kind": "program",
                    "confidence": Confidence.HIGH,
                    "name": "_start",
                },
            ],
            imports=[
                {
                    "module": "libc.so.6",
                    "symbol": "printf",
                    "address": Address(space="ram", offset="0x405100", display="0x405100"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
                {
                    "module": "libc.so.6",
                    "symbol": "fgets",
                    "address": Address(space="ram", offset="0x405108", display="0x405108"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
                {
                    "module": "libc.so.6",
                    "symbol": "malloc",
                    "address": Address(space="ram", offset="0x405110", display="0x405110"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
                {
                    "module": "libc.so.6",
                    "symbol": "free",
                    "address": Address(space="ram", offset="0x405118", display="0x405118"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
                {
                    "module": "libc.so.6",
                    "symbol": "strcmp",
                    "address": Address(space="ram", offset="0x405120", display="0x405120"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
            ],
            exports=[
                {
                    "name": "main",
                    "address": Address(space="ram", offset="0x401100", display="0x401100"),
                    "ordinal": None,
                    "forwarder": None,
                    "kind": "function",
                },
                {
                    "name": "compute_hash",
                    "address": Address(space="ram", offset="0x401300", display="0x401300"),
                    "ordinal": None,
                    "forwarder": None,
                    "kind": "function",
                },
            ],
            symbols=[
                {
                    "name": "_start",
                    "address": Address(space="ram", offset="0x401000", display="0x401000"),
                    "source": FunctionNameSource.ORIGINAL,
                    "scope": "global",
                },
                {
                    "name": "main",
                    "address": Address(space="ram", offset="0x401100", display="0x401100"),
                    "source": FunctionNameSource.ORIGINAL,
                    "scope": "global",
                },
                {
                    "name": "compute_hash",
                    "address": Address(space="ram", offset="0x401300", display="0x401300"),
                    "source": FunctionNameSource.ORIGINAL,
                    "scope": "global",
                },
                {
                    "name": "parse_input",
                    "address": Address(space="ram", offset="0x401500", display="0x401500"),
                    "source": FunctionNameSource.ORIGINAL,
                    "scope": "local",
                },
            ],
            strings=[
                {
                    "text": "Enter input: ",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x405200", display="0x405200"),
                    "length": 14,
                },
                {
                    "text": "Hash: 0x",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x405210", display="0x405210"),
                    "length": 8,
                },
                {
                    "text": "Invalid input",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x405220", display="0x405220"),
                    "length": 13,
                },
                {
                    "text": "libc.so.6",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x405230", display="0x405230"),
                    "length": 9,
                },
            ],
            functions=[
                {
                    "name": "_start",
                    "address": Address(space="ram", offset="0x401000", display="0x401000"),
                    "size_bytes": 64,
                    "confidence": Confidence.HIGH,
                    "name_source": FunctionNameSource.BACKEND_GENERATED,
                    "is_external": False,
                    "is_thunk": False,
                    "signature": "void _start()",
                    "basic_block_count": 2,
                    "instruction_count": 6,
                    "cyclomatic_complexity": 1,
                },
                {
                    "name": "main",
                    "address": Address(space="ram", offset="0x401100", display="0x401100"),
                    "size_bytes": 384,
                    "confidence": Confidence.HIGH,
                    "name_source": FunctionNameSource.ORIGINAL,
                    "is_external": False,
                    "is_thunk": False,
                    "signature": "int main(int argc, char **argv)",
                    "basic_block_count": 10,
                    "instruction_count": 72,
                    "cyclomatic_complexity": 4,
                },
                {
                    "name": "compute_hash",
                    "address": Address(space="ram", offset="0x401300", display="0x401300"),
                    "size_bytes": 256,
                    "confidence": Confidence.HIGH,
                    "name_source": FunctionNameSource.ORIGINAL,
                    "is_external": False,
                    "is_thunk": False,
                    "signature": "uint32_t compute_hash(const char *data)",
                    "basic_block_count": 6,
                    "instruction_count": 41,
                    "cyclomatic_complexity": 3,
                },
                {
                    "name": "parse_input",
                    "address": Address(space="ram", offset="0x401500", display="0x401500"),
                    "size_bytes": 192,
                    "confidence": Confidence.HIGH,
                    "name_source": FunctionNameSource.ORIGINAL,
                    "is_external": False,
                    "is_thunk": False,
                    "signature": "int parse_input(const char *buf, size_t len)",
                    "basic_block_count": 4,
                    "instruction_count": 28,
                    "cyclomatic_complexity": 2,
                },
            ],
        )

    @staticmethod
    def macho_fixture() -> dict[str, Any]:
        """Return a Mach-O fixture with known section/function/import/export layouts.

        Represents a minimal arm64 macOS binary with:
        - __TEXT (__text, __cstring, __const), __DATA (__data, __bss),
          __LINKEDIT sections
        - Three functions: _main (0x100003f80), _validate_input (0x100003fc0),
          _do_work (0x100004000)
        - Imports from libSystem.B.dylib
        - Exports: _main
        """
        return FakeAdapter._build_fixture(
            fmt="Mach-O",
            arch="arm64",
            endianness=Endianness.LITTLE,
            sections=[
                {
                    "name": "__text",
                    "address": Address(
                        space="ram", offset="0x100003f80", display="0x100003f80", file_offset=0
                    ),
                    "virtual_size": 4096,
                    "raw_size": 2048,
                    "flags": ["r", "x"],
                    "entropy": 5.71,
                },
                {
                    "name": "__cstring",
                    "address": Address(
                        space="ram", offset="0x100004f80", display="0x100004f80", file_offset=4096
                    ),
                    "virtual_size": 1024,
                    "raw_size": 512,
                    "flags": ["r"],
                    "entropy": 3.02,
                },
                {
                    "name": "__const",
                    "address": Address(
                        space="ram", offset="0x100005380", display="0x100005380", file_offset=5120
                    ),
                    "virtual_size": 1024,
                    "raw_size": 256,
                    "flags": ["r"],
                    "entropy": 1.92,
                },
                {
                    "name": "__data",
                    "address": Address(
                        space="ram", offset="0x100005780", display="0x100005780", file_offset=6144
                    ),
                    "virtual_size": 1024,
                    "raw_size": 128,
                    "flags": ["r", "w"],
                    "entropy": 1.12,
                },
                {
                    "name": "__bss",
                    "address": Address(space="ram", offset="0x100005b80", display="0x100005b80"),
                    "virtual_size": 4096,
                    "raw_size": 0,
                    "flags": ["r", "w"],
                    "entropy": 0.0,
                },
                {
                    "name": "__linkedit",
                    "address": Address(
                        space="ram", offset="0x100006b80", display="0x100006b80", file_offset=7168
                    ),
                    "virtual_size": 2048,
                    "raw_size": 1024,
                    "flags": ["r"],
                    "entropy": 4.33,
                },
            ],
            entrypoints=[
                {
                    "address": Address(
                        space="ram", offset="0x100003f80", display="0x100003f80", file_offset=0
                    ),
                    "kind": "program",
                    "confidence": Confidence.HIGH,
                    "name": "_main",
                },
            ],
            imports=[
                {
                    "module": "libSystem.B.dylib",
                    "symbol": "_printf",
                    "address": Address(space="ram", offset="0x100005400", display="0x100005400"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
                {
                    "module": "libSystem.B.dylib",
                    "symbol": "_malloc",
                    "address": Address(space="ram", offset="0x100005408", display="0x100005408"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
                {
                    "module": "libSystem.B.dylib",
                    "symbol": "_free",
                    "address": Address(space="ram", offset="0x100005410", display="0x100005410"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
                {
                    "module": "libSystem.B.dylib",
                    "symbol": "_dispatch_async",
                    "address": Address(space="ram", offset="0x100005418", display="0x100005418"),
                    "resolution": ImportResolution.RESOLVED,
                    "ordinal": None,
                },
            ],
            exports=[
                {
                    "name": "_main",
                    "address": Address(space="ram", offset="0x100003f80", display="0x100003f80"),
                    "ordinal": None,
                    "forwarder": None,
                    "kind": "function",
                },
                {
                    "name": "_validate_input",
                    "address": Address(space="ram", offset="0x100003fc0", display="0x100003fc0"),
                    "ordinal": None,
                    "forwarder": None,
                    "kind": "function",
                },
            ],
            symbols=[
                {
                    "name": "_main",
                    "address": Address(space="ram", offset="0x100003f80", display="0x100003f80"),
                    "source": FunctionNameSource.ORIGINAL,
                    "scope": "global",
                },
                {
                    "name": "_validate_input",
                    "address": Address(space="ram", offset="0x100003fc0", display="0x100003fc0"),
                    "source": FunctionNameSource.ORIGINAL,
                    "scope": "global",
                },
                {
                    "name": "_do_work",
                    "address": Address(space="ram", offset="0x100004000", display="0x100004000"),
                    "source": FunctionNameSource.ORIGINAL,
                    "scope": "local",
                },
            ],
            strings=[
                {
                    "text": "Hello, World!",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x100004f80", display="0x100004f80"),
                    "length": 13,
                },
                {
                    "text": "Processing...",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x100004f90", display="0x100004f90"),
                    "length": 14,
                },
                {
                    "text": "Done.",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x100004fa0", display="0x100004fa0"),
                    "length": 5,
                },
                {
                    "text": "libSystem.B.dylib",
                    "encoding": "ASCII",
                    "address": Address(space="ram", offset="0x100004fb0", display="0x100004fb0"),
                    "length": 18,
                },
            ],
            functions=[
                {
                    "name": "_main",
                    "address": Address(space="ram", offset="0x100003f80", display="0x100003f80"),
                    "size_bytes": 64,
                    "confidence": Confidence.HIGH,
                    "name_source": FunctionNameSource.ORIGINAL,
                    "is_external": False,
                    "is_thunk": False,
                    "signature": "int main(int argc, char **argv)",
                    "basic_block_count": 3,
                    "instruction_count": 12,
                    "cyclomatic_complexity": 2,
                },
                {
                    "name": "_validate_input",
                    "address": Address(space="ram", offset="0x100003fc0", display="0x100003fc0"),
                    "size_bytes": 64,
                    "confidence": Confidence.HIGH,
                    "name_source": FunctionNameSource.ORIGINAL,
                    "is_external": False,
                    "is_thunk": False,
                    "signature": "bool validate_input(const char *data)",
                    "basic_block_count": 2,
                    "instruction_count": 8,
                    "cyclomatic_complexity": 2,
                },
                {
                    "name": "_do_work",
                    "address": Address(space="ram", offset="0x100004000", display="0x100004000"),
                    "size_bytes": 128,
                    "confidence": Confidence.HIGH,
                    "name_source": FunctionNameSource.ORIGINAL,
                    "is_external": False,
                    "is_thunk": False,
                    "signature": "void do_work(size_t count)",
                    "basic_block_count": 4,
                    "instruction_count": 21,
                    "cyclomatic_complexity": 2,
                },
            ],
        )

    @staticmethod
    def _build_fixture(
        fmt: str,
        arch: str,
        endianness: Endianness,
        sections: list[dict[str, Any]],
        entrypoints: list[dict[str, Any]],
        imports: list[dict[str, Any]],
        exports: list[dict[str, Any]],
        symbols: list[dict[str, Any]],
        strings: list[dict[str, Any]],
        functions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build a fixture data dict from structured inputs.

        Returns a dict with keys matching the FakeAdapter's internal fixture storage.
        """
        # Build Section entities
        section_entities = []
        for s in sections:
            section_entities.append(
                Section(
                    name=s["name"],
                    address=s.get("address"),
                    virtual_size=s.get("virtual_size", 0),
                    raw_size=s.get("raw_size", 0),
                    flags=s.get("flags", []),
                    entropy=s.get("entropy"),
                )
            )

        # Build EntryPoint entities
        entrypoint_entities = []
        for ep in entrypoints:
            entrypoint_entities.append(
                EntryPoint(
                    address=ep.get("address"),
                    kind=ep.get("kind", "unknown"),
                    confidence=ep.get("confidence", Confidence.UNKNOWN),
                    name=ep.get("name"),
                )
            )

        # Build Import entities
        import_entities = []
        for imp in imports:
            import_entities.append(
                Import(
                    module=imp.get("module", ""),
                    symbol=imp.get("symbol", ""),
                    address=imp.get("address"),
                    resolution=imp.get("resolution", ImportResolution.UNRESOLVED),
                    ordinal=imp.get("ordinal"),
                )
            )

        # Build Export entities
        export_entities = []
        for exp in exports:
            export_entities.append(
                Export(
                    name=exp.get("name", ""),
                    address=exp.get("address"),
                    ordinal=exp.get("ordinal"),
                    forwarder=exp.get("forwarder"),
                    kind=exp.get("kind", "function"),
                )
            )

        # Build Symbol entities
        symbol_entities = []
        for sym in symbols:
            symbol_entities.append(
                Symbol(
                    name=sym.get("name", ""),
                    address=sym.get("address"),
                    source=sym.get("source", FunctionNameSource.UNKNOWN),
                    scope=sym.get("scope", "unknown"),
                )
            )

        # Build String entities
        string_entities = []
        for st in strings:
            string_entities.append(
                String(
                    text=st.get("text", ""),
                    encoding=st.get("encoding", "ASCII"),
                    address=st.get("address"),
                    length=st.get("length", len(st.get("text", ""))),
                )
            )

        # Build Function entities
        function_entities = []
        for fn in functions:
            function_entities.append(
                Function(
                    name=fn.get("name", ""),
                    address=fn.get("address"),
                    size_bytes=fn.get("size_bytes", 0),
                    confidence=fn.get("confidence", Confidence.UNKNOWN),
                    name_source=fn.get("name_source", FunctionNameSource.UNKNOWN),
                    is_external=fn.get("is_external", False),
                    is_thunk=fn.get("is_thunk", False),
                    signature=fn.get("signature"),
                    basic_block_count=fn.get("basic_block_count"),
                    instruction_count=fn.get("instruction_count"),
                    cyclomatic_complexity=fn.get("cyclomatic_complexity"),
                )
            )

        return {
            "format": fmt,
            "architecture": arch,
            "endianness": endianness,
            "sections": section_entities,
            "entrypoints": entrypoint_entities,
            "imports": import_entities,
            "exports": export_entities,
            "symbols": symbol_entities,
            "strings": string_entities,
            "functions": function_entities,
        }

    # ------------------------------------------------------------------
    # FakeAdapter implementation
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        self._initialized: bool = False
        self._fixtures: dict[str, dict[str, Any]] = {}
        self._binaries: dict[str, dict[str, Any]] = {}

        # Failure configuration
        self._import_failures: dict[str, str] = {}
        self._analysis_failure: str | None = None
        self._backend_failures: dict[str, str] = {}

        # Slow operation configuration
        self._slow_operations: dict[str, float] = {}

        # Address mapping configuration
        self._unmapped_ranges: list[tuple[int, int]] = []
        self._partially_mapped_ranges: list[tuple[int, int, int]] = []
        self._truncation_points: dict[int, int] = {}  # start_addr -> max_bytes

        # Override data
        self._override_sections: dict[str, list[Section]] = {}
        self._override_functions: dict[str, list[Function]] = {}
        self._override_strings: dict[str, list[String]] = {}

    # ------------------------------------------------------------------
    # Configuration API
    # ------------------------------------------------------------------

    def set_fixture(self, name: str, fixture: dict[str, Any]) -> None:
        """Register a named fixture in the adapter."""
        self._fixtures[name] = fixture

    def configure_import_failure(self, binary_name: str, message: str) -> None:
        """Configure an import failure for a specific binary."""
        self._import_failures[binary_name] = message

    def configure_analysis_failure(self, message: str) -> None:
        """Configure the next analysis to fail completely."""
        self._analysis_failure = message

    def configure_backend_failure(self, method_name: str, message: str) -> None:
        """Configure a backend failure for a specific method (e.g., 'get_functions')."""
        self._backend_failures[method_name] = message

    def configure_slow_operation(self, operation: str, delay_seconds: float) -> None:
        """Make a specific operation slow (simulate delay)."""
        self._slow_operations[operation] = delay_seconds

    def configure_unmapped_range(self, start: int, end: int) -> None:
        """Mark an address range as unmapped.

        Args:
            start: Start offset (integer).
            end: End offset (integer, exclusive).
        """
        self._unmapped_ranges.append((start, end))

    def configure_partial_mapping(self, start: int, end: int, mapped_end: int) -> None:
        """Mark a range as partially mapped — from start to mapped_end only.

        Args:
            start: Start offset.
            end: Intended end offset.
            mapped_end: Actual end of mapped data (must be < end).
        """
        self._partially_mapped_ranges.append((start, end, mapped_end))

    def configure_truncation(self, start_addr: int, max_bytes: int) -> None:
        """Configure truncation at a given address.

        Args:
            start_addr: Starting address offset.
            max_bytes: Maximum bytes that can be read from this address.
        """
        self._truncation_points[start_addr] = max_bytes

    def clear_configuration(self) -> None:
        """Reset all failure, slow, and mapping configuration."""
        self._import_failures.clear()
        self._analysis_failure = None
        self._backend_failures.clear()
        self._slow_operations.clear()
        self._unmapped_ranges.clear()
        self._partially_mapped_ranges.clear()
        self._truncation_points.clear()

    # ------------------------------------------------------------------
    # BackendAdapter implementation
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        self._initialized = True

    def capabilities(self) -> dict[str, Any]:
        return {
            "adapter": "fake",
            "adapter_version": "0.1.0",
            "backend": "FakeAdapter",
            "backend_version": "0.1.0",
            "supported_formats": ["PE", "ELF", "Mach-O"],
            "supported_architectures": ["x86", "x86-64", "arm64"],
            "concurrency": "PROJECT_SERIALIZED",
            "max_depth": 10,
        }

    def available_profiles(self) -> list[AnalysisProfile]:
        return list(self.DEFAULT_PROFILES)

    def import_binary(self, path: str, project: Project) -> Binary:
        self._check_slow("import")

        # Check for import failure
        # Determine the fixture name from path or project
        for name, msg in self._import_failures.items():
            if name in path or name == project.name:
                from binary_analysis.domain.errors import ImportFailedError

                raise ImportFailedError(msg, binary_path=path)

        # Determine format from fixture data
        fixture = self._resolve_fixture(path, project)

        binary = Binary(
            id=uuid4(),
            sha256="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
            path=path,
            format=fixture.get("format", "unknown"),
            import_mode="copy",
            size_bytes=16384,
            architecture=fixture.get("architecture"),
            endianness=fixture.get("endianness"),
        )

        # Store the binary
        self._binaries[str(binary.id)] = {
            "binary": binary,
            "fixture_name": self._resolve_fixture_name(path, project),
        }

        return binary

    def analyze(self, binary: Binary, profile: AnalysisProfile) -> AnalysisResult:
        self._check_slow("analyze")

        if self._analysis_failure is not None:
            from binary_analysis.domain.errors import AnalysisFailedError

            msg = self._analysis_failure
            self._analysis_failure = None
            raise AnalysisFailedError(msg)

        # Build result based on profile
        fixture = self._get_binary_fixture(binary)
        available = set(fixture.keys())
        requested = set(profile.analysers)

        completed = []
        failed = []
        diagnostics = []

        for analyser in requested:
            if analyser in available and fixture.get(analyser):
                completed.append(analyser)
            else:
                failed.append(analyser)
                diagnostics.append(
                    {
                        "severity": "WARNING",
                        "category": analyser,
                        "message": f"Analyser '{analyser}' not available in fixture",
                        "recoverable": True,
                    }
                )

        return AnalysisResult(
            success=len(failed) == 0 or len(completed) > 0,
            partial=len(failed) > 0 and len(completed) > 0,
            completed_analysers=completed,
            failed_analysers=failed,
            diagnostics=diagnostics,
        )

    def get_metadata(self, binary: Binary) -> BinaryMetadata:
        self._check_slow("get_metadata")
        self._check_backend_failure("get_metadata")

        fixture = self._get_binary_fixture(binary)
        endian_val = fixture.get("endianness")
        return BinaryMetadata(
            format=fixture.get("format", "unknown"),
            architecture=fixture.get("architecture"),
            endianness=endian_val.value if endian_val is not None else None,
            size_bytes=16384,
            entry_point=self._first_entrypoint(fixture),
        )

    def get_sections(self, binary: Binary) -> list[Section]:
        self._check_slow("get_sections")
        self._check_backend_failure("get_sections")

        if str(binary.id) in self._override_sections:
            return list(self._override_sections[str(binary.id)])

        fixture = self._get_binary_fixture(binary)
        return list(fixture.get("sections", []))

    def get_entrypoints(self, binary: Binary) -> list[EntryPoint]:
        self._check_backend_failure("get_entrypoints")
        fixture = self._get_binary_fixture(binary)
        return list(fixture.get("entrypoints", []))

    def get_imports(self, binary: Binary) -> list[Import]:
        self._check_backend_failure("get_imports")
        fixture = self._get_binary_fixture(binary)
        return list(fixture.get("imports", []))

    def get_exports(self, binary: Binary) -> list[Export]:
        self._check_backend_failure("get_exports")
        fixture = self._get_binary_fixture(binary)
        return list(fixture.get("exports", []))

    def get_symbols(self, binary: Binary) -> list[Symbol]:
        self._check_backend_failure("get_symbols")
        fixture = self._get_binary_fixture(binary)
        return list(fixture.get("symbols", []))

    def get_strings(
        self,
        binary: Binary,
        min_length: int = 4,
        contains: str | None = None,
        encoding_filter: str | None = None,
    ) -> list[String]:
        self._check_slow("get_strings")
        self._check_backend_failure("get_strings")

        fixture = self._get_binary_fixture(binary)
        strings = fixture.get("strings", [])

        result = []
        for s in strings:
            if s.length < min_length:
                continue
            if contains is not None and contains not in s.text:
                continue
            if encoding_filter is not None and s.encoding != encoding_filter:
                continue
            result.append(s)

        return result

    def get_functions(
        self,
        binary: Binary,
        exclude_external: bool = True,
        exclude_thunks: bool = True,
    ) -> list[Function]:
        self._check_backend_failure("get_functions")

        if str(binary.id) in self._override_functions:
            functions = list(self._override_functions[str(binary.id)])
        else:
            fixture = self._get_binary_fixture(binary)
            functions = list(fixture.get("functions", []))

        result = []
        for fn in functions:
            if exclude_external and fn.is_external:
                continue
            if exclude_thunks and fn.is_thunk:
                continue
            result.append(fn)

        return result

    def decompile(self, binary: Binary, function: Function) -> DecompilationResult:
        self._check_slow("decompile")
        self._check_backend_failure("decompile")

        func_name = function.name
        fn_address = function.address.offset if function.address else "0x0"

        pseudocode = (
            f"// Reconstructed pseudocode for {func_name} @ {fn_address}\n"
            f"// Generated by FakeAdapter\n"
            f"\n"
            f"{'int' if function.signature and 'int' in function.signature else 'void'} "
            f"{func_name}(void) {{\n"
            f"    // Function body ({function.size_bytes} bytes)\n"
            f"    // ... (simulated decompilation)\n"
            f"    return;\n"
            f"}}\n"
        )

        address_map: dict[int, dict[str, Any]] = {}
        if function.address:
            for i in range(1, pseudocode.count("\n") + 1):
                address_map[i] = function.address.to_dict()

        return DecompilationResult(
            pseudocode=pseudocode,
            address_map=address_map,
            diagnostics=[],
            language="c",
        )

    def disassemble(
        self, binary: Binary, start_address: Address, end_address: Address
    ) -> list[Instruction]:
        self._check_backend_failure("disassemble")

        # Check if the range is unmapped
        if self._is_unmapped(start_address) and self._is_unmapped(end_address):
            raise ValueError(
                f"Address range {start_address.offset}..{end_address.offset} is unmapped"
            )

        fixture = self._get_binary_fixture(binary)
        # Generate synthetic instructions for the range
        instructions = self._generate_instructions(start_address, end_address, fixture)

        return instructions

    def read_bytes(self, binary: Binary, address: Address, length: int) -> tuple[bytes, int]:
        self._check_backend_failure("read_bytes")

        if length <= 0:
            raise ValueError("Length must be positive")

        start_int = self._addr_to_int(address)

        # Check if unmapped
        if self._is_unmapped(address):
            raise ValueError(f"Address {address.offset} is unmapped")

        # Apply truncation
        actual_length = length
        if start_int in self._truncation_points:
            max_bytes = self._truncation_points[start_int]
            actual_length = min(length, max_bytes)

        # Generate deterministic bytes based on address
        data = bytes((start_int + i) % 256 for i in range(actual_length))
        return (data, actual_length)

    def get_xrefs(self, binary: Binary, address: Address) -> list[Reference]:
        self._check_backend_failure("get_xrefs")

        fixture = self._get_binary_fixture(binary)
        functions = fixture.get("functions", [])

        refs = []
        for fn in functions:
            if fn.address is None:
                continue
            if fn.address.offset == address.offset:
                # References FROM this function to others
                for target in functions:
                    if target.address is None or target is fn:
                        continue
                    refs.append(
                        Reference(
                            from_addr=fn.address,
                            to_addr=target.address,
                            kind=ReferenceKind.CALL,
                            confidence=Confidence.HIGH,
                        )
                    )
            elif fn.address.offset != address.offset:
                # If another function's address matches, add a reference TO it
                pass

        return refs

    def get_callers(self, binary: Binary, function: Function) -> list[CallEdge]:
        self._check_backend_failure("get_callers")

        fixture = self._get_binary_fixture(binary)
        functions = fixture.get("functions", [])

        # Find functions that "call" this one — in the fake, each function
        # calls the next one in the list (for deterministic graph)
        callers = []
        for i, fn in enumerate(functions):
            if fn.address is None or function.address is None:
                continue
            # In our fake model, each function calls the next one
            if i + 1 < len(functions) and functions[i + 1].address == function.address:
                callers.append(
                    CallEdge(
                        from_address=fn.address,
                        to_address=function.address,
                        from_name=fn.name,
                        to_name=function.name,
                        kind="direct",
                    )
                )

        return callers

    def get_callees(self, binary: Binary, function: Function) -> list[CallEdge]:
        self._check_backend_failure("get_callees")

        fixture = self._get_binary_fixture(binary)
        functions = fixture.get("functions", [])

        callees = []
        for i, fn in enumerate(functions):
            if fn.address is None or function.address is None:
                continue
            if fn.address == function.address and i + 1 < len(functions):
                callee = functions[i + 1]
                callees.append(
                    CallEdge(
                        from_address=function.address,
                        to_address=callee.address,
                        from_name=function.name,
                        to_name=callee.name,
                        kind="direct",
                    )
                )

        return callees

    def get_callgraph(self, binary: Binary, function: Function, max_depth: int = 3) -> CallGraph:
        self._check_backend_failure("get_callgraph")
        self._check_slow("get_callgraph")

        fixture = self._get_binary_fixture(binary)
        functions = fixture.get("functions", [])

        # Build a linear chain: each function calls the next
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []

        # Find the root index
        root_idx = None
        for i, fn in enumerate(functions):
            if fn.address and function.address and fn.address == function.address:
                root_idx = i
                break

        if root_idx is None:
            if function.address:
                nodes.append(
                    {
                        "name": function.name,
                        "address": function.address.to_dict(),
                        "depth": 0,
                    }
                )
            return CallGraph(
                root_address=function.address,
                nodes=nodes,
                edges=edges,
                max_depth=max_depth,
                total_nodes=len(nodes),
                total_edges=len(edges),
                truncated=False,
            )

        visited: set[int] = set()
        truncated = False

        for depth in range(min(max_depth + 1, len(functions))):
            idx = root_idx + depth
            if idx >= len(functions):
                break

            fn = functions[idx]
            if fn.address is None:
                continue

            visited.add(idx)
            nodes.append(
                {
                    "name": fn.name,
                    "address": fn.address.to_dict(),
                    "depth": depth,
                }
            )

            if idx + 1 < len(functions) and depth < max_depth:
                next_fn = functions[idx + 1]
                if next_fn.address:
                    edges.append(
                        {
                            "from": fn.address.to_dict(),
                            "to": next_fn.address.to_dict(),
                            "kind": "CALL",
                        }
                    )

        return CallGraph(
            root_address=function.address,
            nodes=nodes,
            edges=edges,
            max_depth=max_depth,
            total_nodes=len(nodes),
            total_edges=len(edges),
            truncated=truncated,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_slow(self, operation: str) -> None:
        """Simulate a slow operation if configured."""
        if operation in self._slow_operations:
            delay = self._slow_operations[operation]
            if delay > 0:
                time.sleep(delay)

    def _check_backend_failure(self, method_name: str) -> None:
        """Check if a backend failure is configured for this method."""
        if method_name in self._backend_failures:
            from binary_analysis.domain.errors import BackendFailureError

            msg = self._backend_failures[method_name]
            raise BackendFailureError(msg, original_error="Simulated backend failure")

    def _resolve_fixture_name(self, path: str, project: Project) -> str:
        """Determine which fixture to use based on the binary path."""
        for name in self._fixtures:
            if name in path or name == project.name:
                return name
        # Default: return the first fixture
        if self._fixtures:
            return next(iter(self._fixtures))
        return "pe-default"

    def _resolve_fixture(self, path: str, project: Project) -> dict[str, Any]:
        """Resolve the fixture data for a given binary path."""
        name = self._resolve_fixture_name(path, project)
        if name in self._fixtures:
            return self._fixtures[name]
        # Return a minimal default fixture
        return {
            "format": "PE",
            "architecture": "x86",
            "endianness": Endianness.LITTLE,
            "sections": [],
            "entrypoints": [],
            "imports": [],
            "exports": [],
            "symbols": [],
            "strings": [],
            "functions": [],
        }

    def _get_binary_fixture(self, binary: Binary) -> dict[str, Any]:
        """Get the fixture data associated with a binary."""
        key = str(binary.id)
        if key in self._binaries:
            fixture_name = self._binaries[key].get("fixture_name", "")
            if fixture_name in self._fixtures:
                return self._fixtures[fixture_name]
        return {
            "format": binary.format or "PE",
            "architecture": binary.architecture or "x86",
            "endianness": binary.endianness or Endianness.LITTLE,
            "sections": [],
            "entrypoints": [],
            "imports": [],
            "exports": [],
            "symbols": [],
            "strings": [],
            "functions": [],
        }

    def _first_entrypoint(self, fixture: dict[str, Any]) -> Address | None:
        """Return the first entrypoint's address, or None."""
        entrypoints: list[EntryPoint] = fixture.get("entrypoints", [])
        if entrypoints:
            return entrypoints[0].address
        return None

    @staticmethod
    def _addr_to_int(addr: Address) -> int:
        """Convert an Address offset string to an integer."""
        if addr.offset.startswith("0x"):
            return int(addr.offset, 16)
        return int(addr.offset, 16)

    def _is_unmapped(self, addr: Address) -> bool:
        """Check if an address falls within any unmapped range."""
        addr_int = self._addr_to_int(addr)
        return any(start <= addr_int < end for start, end in self._unmapped_ranges)

    def _generate_instructions(
        self,
        start_address: Address,
        end_address: Address,
        fixture: dict[str, Any],
    ) -> list[Instruction]:
        """Generate synthetic instructions for an address range."""
        start_int = self._addr_to_int(start_address)
        end_int = self._addr_to_int(end_address)

        instructions: list[Instruction] = []
        offset = start_int
        idx = 0

        # Simple x86-like instruction templates
        templates = [
            ("push", "rbp"),
            ("mov", "rbp, rsp"),
            ("sub", "rsp, 0x20"),
            ("mov", "eax, 0x0"),
            ("call", "0x401100"),
            ("test", "eax, eax"),
            ("je", "0x401050"),
            ("lea", "rdi, [rip+0x1f4]"),
            ("call", "0x401200"),
            ("add", "rsp, 0x20"),
            ("pop", "rbp"),
            ("ret", ""),
        ]

        while offset <= end_int and len(instructions) < 1000:
            template = templates[idx % len(templates)]
            inst_size = 1 + len(template[0]) % 5  # 1-5 bytes

            instr = Instruction(
                mnemonic=template[0],
                operands=template[1],
                bytes_hex=format(offset % 256, "02x"),
                address=Address(
                    space="ram",
                    offset=f"0x{offset:x}",
                    display=f"0x{offset:x}",
                ),
                size_bytes=inst_size,
            )
            instructions.append(instr)
            offset += inst_size
            idx += 1

        return instructions
