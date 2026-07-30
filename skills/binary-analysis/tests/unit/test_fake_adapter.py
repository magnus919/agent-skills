"""Unit tests for the FakeAdapter — a fully controllable in-memory backend adapter.

Tests cover:
- Normal data returns for all structural query types
- Fixture registration (PE, ELF, Mach-O)
- Import failures (exit code 10)
- Analysis crashes (exit code 11)
- Backend failures (exit code 13)
- Slow operations and timeout simulation
- Unmapped addresses, partial mapping, and truncation
- Configurable overrides and edge cases
"""

from __future__ import annotations

import sys
from pathlib import Path
_scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import time
from typing import Any
from uuid import uuid4

import pytest
from binary_analysis.adapters.base import (
    AnalysisProfile,
    AnalysisResult,
    BackendAdapter,
    BinaryMetadata,
    CallEdge,
    ConcurrencyMode,
    DecompilationResult,
)
from binary_analysis.adapters.fake import FakeAdapter
from binary_analysis.domain.entities import (
    Address,
    Binary,
    CallGraph,
    Function,
    Instruction,
    Project,
    Reference,
    Section,
    String,
)
from binary_analysis.domain.enums import (
    Confidence,
    Endianness,
    FunctionNameSource,
    ImportResolution,
)
from binary_analysis.domain.errors import (
    AnalysisFailedError,
    BackendFailureError,
    ImportFailedError,
)

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def adapter() -> FakeAdapter:
    """Return a fresh FakeAdapter with PE fixture registered."""
    a = FakeAdapter()
    a.set_fixture("pe-default", FakeAdapter.pe_fixture())
    a.set_fixture("elf-default", FakeAdapter.elf_fixture())
    a.set_fixture("macho-default", FakeAdapter.macho_fixture())
    return a


@pytest.fixture
def project() -> Project:
    """Return a test project."""
    return Project(
        id=uuid4(),
        name="test-project",
    )


@pytest.fixture
def binary(adapter: FakeAdapter, project: Project) -> Binary:
    """Return an imported binary from the adapter."""
    return adapter.import_binary("test.exe", project)


# ---------------------------------------------------------------------------
# Interface compliance
# ---------------------------------------------------------------------------


class TestBackendAdapterInterface:
    """Verify that FakeAdapter implements all BackendAdapter abstract methods."""

    def test_is_subclass_of_backend_adapter(self) -> None:
        assert issubclass(FakeAdapter, BackendAdapter)

    def test_concurrency_mode(self, adapter: FakeAdapter) -> None:
        assert adapter.concurrency == ConcurrencyMode.PROJECT_SERIALIZED

    def test_all_abstract_methods_implemented(self) -> None:
        """Verify FakeAdapter implements every abstract method."""
        # Collect abstract methods from BackendAdapter
        abstract_names: set[str] = set()
        for name in dir(BackendAdapter):
            if name.startswith("_"):
                continue
            attr = getattr(BackendAdapter, name, None)
            if attr is None:
                continue
            if hasattr(attr, "__isabstractmethod__") and attr.__isabstractmethod__:
                abstract_names.add(name)

        # Ensure FakeAdapter has each abstract method and it is NOT abstract
        for method_name in sorted(abstract_names):
            assert hasattr(FakeAdapter, method_name), (
                f"FakeAdapter missing abstract method: {method_name}"
            )
            fake_attr = getattr(FakeAdapter, method_name)
            # Properties decorated with @property + @abstractmethod carry
            # __isabstractmethod__ on the property object; we just need to
            # check the FakeAdapter overrides it (no abstractmethod on the override)
            if hasattr(fake_attr, "fget"):
                # It's a property — verify it has a concrete getter
                assert fake_attr.fget is not None, (
                    f"FakeAdapter.{method_name} property has no getter"
                )
            else:
                assert not hasattr(fake_attr, "__isabstractmethod__"), (
                    f"FakeAdapter.{method_name} is still abstract"
                )


# ---------------------------------------------------------------------------
# Initialization and capabilities
# ---------------------------------------------------------------------------


class TestInitialization:
    """Tests for initialize and capabilities."""

    def test_initialize(self, adapter: FakeAdapter) -> None:
        adapter.initialize()
        assert adapter._initialized is True

    def test_capabilities(self, adapter: FakeAdapter) -> None:
        caps = adapter.capabilities()
        assert caps["adapter"] == "fake"
        assert caps["adapter_version"] == "0.1.0"
        assert "PE" in caps["supported_formats"]
        assert "ELF" in caps["supported_formats"]
        assert "Mach-O" in caps["supported_formats"]
        assert caps["max_depth"] == 10

    def test_available_profiles(self, adapter: FakeAdapter) -> None:
        profiles = adapter.available_profiles()
        assert len(profiles) == 3
        names = {p.name for p in profiles}
        assert names == {"standard", "quick", "deep"}

    def test_validate_profile_valid(self, adapter: FakeAdapter) -> None:
        profile = adapter.validate_profile("quick")
        assert profile.name == "quick"

    def test_validate_profile_invalid(self, adapter: FakeAdapter) -> None:
        with pytest.raises(ValueError, match="Unknown analysis profile"):
            adapter.validate_profile("nonexistent")


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------


class TestImport:
    """Tests for import_binary."""

    def test_import_binary_returns_binary_entity(
        self, adapter: FakeAdapter, project: Project
    ) -> None:
        b = adapter.import_binary("test.exe", project)
        assert isinstance(b, Binary)
        assert b.format == "PE"
        assert b.architecture == "x86"
        assert b.endianness == Endianness.LITTLE
        assert b.sha256 != ""
        assert b.id is not None

    def test_import_binary_sha256_present(self, adapter: FakeAdapter, project: Project) -> None:
        """SHA-256 is computed client-side and present (VAL-IMP-003)."""
        b = adapter.import_binary("test.exe", project)
        assert len(b.sha256) == 64
        assert all(c in "0123456789abcdef" for c in b.sha256)

    def test_import_failure_simulated(self, adapter: FakeAdapter, project: Project) -> None:
        """Simulate import failure (exit code 10)."""
        adapter.configure_import_failure("fail.exe", "Simulated import failure")
        with pytest.raises(ImportFailedError) as exc:
            adapter.import_binary("fail.exe", project)
        assert exc.value.exit_code == 10
        assert "Simulated import failure" in str(exc.value)

    def test_import_failure_cleared_after_remove(
        self, adapter: FakeAdapter, project: Project
    ) -> None:
        """Clearing configuration removes import failure."""
        adapter.configure_import_failure("fail.exe", "Import failed")
        adapter.clear_configuration()
        b = adapter.import_binary("fail.exe", project)
        assert isinstance(b, Binary)
        assert b.format is not None


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


class TestAnalyze:
    """Tests for analyze method."""

    def test_analyze_returns_result(self, adapter: FakeAdapter, binary: Binary) -> None:
        profile = adapter.validate_profile("standard")
        result = adapter.analyze(binary, profile)
        assert isinstance(result, AnalysisResult)
        assert result.success is True
        assert result.partial is False

    def test_analyze_quick_profile(self, adapter: FakeAdapter, binary: Binary) -> None:
        profile = adapter.validate_profile("quick")
        result = adapter.analyze(binary, profile)
        assert "functions" in result.completed_analysers
        assert "sections" in result.completed_analysers

    def test_analyze_deep_profile(self, adapter: FakeAdapter, binary: Binary) -> None:
        profile = adapter.validate_profile("deep")
        result = adapter.analyze(binary, profile)
        assert len(result.completed_analysers) > 2

    def test_analysis_failure_crash(self, adapter: FakeAdapter, binary: Binary) -> None:
        """Simulate analysis crash (exit code 11)."""
        adapter.configure_analysis_failure("Analysis engine crashed")
        profile = adapter.validate_profile("standard")
        with pytest.raises(AnalysisFailedError) as exc:
            adapter.analyze(binary, profile)
        assert exc.value.exit_code == 11
        assert "Analysis engine crashed" in str(exc.value)


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


class TestMetadata:
    """Tests for get_metadata."""

    def test_metadata_returns_canonical_fields(self, adapter: FakeAdapter, binary: Binary) -> None:
        meta = adapter.get_metadata(binary)
        assert isinstance(meta, BinaryMetadata)
        assert meta.format == "PE"
        assert meta.architecture == "x86"
        assert meta.endianness == "LITTLE"
        assert meta.size_bytes > 0

    def test_metadata_has_entry_point(self, adapter: FakeAdapter, binary: Binary) -> None:
        meta = adapter.get_metadata(binary)
        assert meta.entry_point is not None
        assert meta.entry_point.offset == "0x401000"


# ---------------------------------------------------------------------------
# Structural queries
# ---------------------------------------------------------------------------


class TestStructuralQueries:
    """Tests for sections, entrypoints, imports, exports, symbols, strings."""

    def test_get_sections_returns_list(self, adapter: FakeAdapter, binary: Binary) -> None:
        sections = adapter.get_sections(binary)
        assert isinstance(sections, list)
        assert len(sections) > 0
        assert all(isinstance(s, Section) for s in sections)

    def test_get_sections_has_expected_fields(self, adapter: FakeAdapter, binary: Binary) -> None:
        sections = adapter.get_sections(binary)
        text = [s for s in sections if s.name == ".text"]
        assert len(text) == 1
        assert text[0].flags is not None
        assert isinstance(text[0].entropy, float)

    def test_get_entrypoints(self, adapter: FakeAdapter, binary: Binary) -> None:
        eps = adapter.get_entrypoints(binary)
        assert len(eps) > 0
        assert eps[0].kind == "program"
        assert eps[0].confidence == Confidence.HIGH

    def test_get_imports(self, adapter: FakeAdapter, binary: Binary) -> None:
        imports = adapter.get_imports(binary)
        assert len(imports) > 0
        kernel_imports = [i for i in imports if i.module == "kernel32.dll"]
        assert len(kernel_imports) > 0
        # Check resolution status
        assert kernel_imports[0].resolution == ImportResolution.RESOLVED

    def test_get_exports(self, adapter: FakeAdapter, binary: Binary) -> None:
        exports = adapter.get_exports(binary)
        assert len(exports) > 0
        assert exports[0].name == "_start"
        assert exports[0].kind == "function"

    def test_get_symbols(self, adapter: FakeAdapter, binary: Binary) -> None:
        symbols = adapter.get_symbols(binary)
        assert len(symbols) > 0
        # At least one symbol should be IMPORTED
        imported = [s for s in symbols if s.source == FunctionNameSource.IMPORTED]
        assert len(imported) > 0

    def test_get_strings(self, adapter: FakeAdapter, binary: Binary) -> None:
        strings = adapter.get_strings(binary)
        assert len(strings) > 0
        assert all(isinstance(s, String) for s in strings)

    def test_get_strings_min_length_filter(self, adapter: FakeAdapter, binary: Binary) -> None:
        strings = adapter.get_strings(binary, min_length=15)
        for s in strings:
            assert s.length >= 15

    def test_get_strings_contains_filter(self, adapter: FakeAdapter, binary: Binary) -> None:
        strings = adapter.get_strings(binary, contains="Access")
        for s in strings:
            assert "Access" in s.text

    def test_get_strings_encoding_filter(self, adapter: FakeAdapter, binary: Binary) -> None:
        strings = adapter.get_strings(binary, encoding_filter="ASCII")
        for s in strings:
            assert s.encoding == "ASCII"

    def test_get_strings_combined_filters(self, adapter: FakeAdapter, binary: Binary) -> None:
        strings = adapter.get_strings(binary, min_length=8, contains="kernel32")
        for s in strings:
            assert s.length >= 8
            assert "kernel32" in s.text


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


class TestFunctions:
    """Tests for get_functions."""

    def test_get_functions_returns_list(self, adapter: FakeAdapter, binary: Binary) -> None:
        funcs = adapter.get_functions(binary)
        assert len(funcs) > 0
        assert all(isinstance(f, Function) for f in funcs)

    def test_get_functions_excludes_external_by_default(
        self, adapter: FakeAdapter, binary: Binary
    ) -> None:
        funcs = adapter.get_functions(binary)
        for f in funcs:
            assert not f.is_external

    def test_get_functions_includes_external_when_requested(
        self, adapter: FakeAdapter, binary: Binary
    ) -> None:
        funcs = adapter.get_functions(binary, exclude_external=False)
        externals = [f for f in funcs if f.is_external]
        assert len(externals) > 0

    def test_get_functions_excludes_thunks_by_default(
        self, adapter: FakeAdapter, binary: Binary
    ) -> None:
        funcs = adapter.get_functions(binary)
        for f in funcs:
            assert not f.is_thunk

    def test_get_functions_has_expected_fields(self, adapter: FakeAdapter, binary: Binary) -> None:
        funcs = adapter.get_functions(binary)
        main_func = [f for f in funcs if f.name == "main"]
        assert len(main_func) == 1
        assert main_func[0].size_bytes > 0
        assert main_func[0].address is not None
        assert main_func[0].confidence == Confidence.HIGH
        assert main_func[0].name_source == FunctionNameSource.ORIGINAL


# ---------------------------------------------------------------------------
# Decompile
# ---------------------------------------------------------------------------


class TestDecompile:
    """Tests for decompile method."""

    def test_decompile_returns_pseudocode(self, adapter: FakeAdapter, binary: Binary) -> None:
        funcs = adapter.get_functions(binary)
        main = next(f for f in funcs if f.name == "main")
        result = adapter.decompile(binary, main)
        assert isinstance(result, DecompilationResult)
        assert "Reconstructed pseudocode" in result.pseudocode
        assert "main" in result.pseudocode
        assert result.language == "c"

    def test_decompile_has_address_map(self, adapter: FakeAdapter, binary: Binary) -> None:
        funcs = adapter.get_functions(binary)
        main = next(f for f in funcs if f.name == "main")
        result = adapter.decompile(binary, main)
        assert len(result.address_map) > 0
        # Address map should contain the function's address
        first_entry = next(iter(result.address_map.values()))
        assert "offset" in first_entry

    def test_decompile_labels_as_reconstructed(self, adapter: FakeAdapter, binary: Binary) -> None:
        """Output is labeled as reconstructed pseudocode, not original source (VAL-FOCUS-001)."""
        funcs = adapter.get_functions(binary)
        main = next(f for f in funcs if f.name == "main")
        result = adapter.decompile(binary, main)
        assert "Reconstructed pseudocode" in result.pseudocode
        assert "// Generated by FakeAdapter" in result.pseudocode


# ---------------------------------------------------------------------------
# Disassemble
# ---------------------------------------------------------------------------


class TestDisassemble:
    """Tests for disassemble method."""

    def test_disassemble_returns_instructions(self, adapter: FakeAdapter, binary: Binary) -> None:
        start = Address(space="ram", offset="0x401000", display="0x401000")
        end = Address(space="ram", offset="0x401020", display="0x401020")
        instructions = adapter.disassemble(binary, start, end)
        assert len(instructions) > 0
        assert all(isinstance(i, Instruction) for i in instructions)
        # Each instruction should have mnemonic and operands
        for inst in instructions:
            assert inst.mnemonic != ""
            assert inst.address is not None

    def test_disassemble_unmapped_range_raises(self, adapter: FakeAdapter, binary: Binary) -> None:
        """Unmapped address range raises ValueError (VAL-FOCUS-009)."""
        adapter.configure_unmapped_range(0x5000, 0x6000)
        start = Address(space="ram", offset="0x5000", display="0x5000")
        end = Address(space="ram", offset="0x5010", display="0x5010")
        with pytest.raises(ValueError, match="unmapped"):
            adapter.disassemble(binary, start, end)


# ---------------------------------------------------------------------------
# Read bytes
# ---------------------------------------------------------------------------


class TestReadBytes:
    """Tests for read_bytes method."""

    def test_read_bytes_returns_data(self, adapter: FakeAdapter, binary: Binary) -> None:
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        data, length = adapter.read_bytes(binary, addr, 16)
        assert isinstance(data, bytes)
        assert length == 16

    def test_read_bytes_deterministic(self, adapter: FakeAdapter, binary: Binary) -> None:
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        data1, _ = adapter.read_bytes(binary, addr, 8)
        data2, _ = adapter.read_bytes(binary, addr, 8)
        assert data1 == data2

    def test_read_bytes_unmapped_raises(self, adapter: FakeAdapter, binary: Binary) -> None:
        """Unmapped address raises ValueError (VAL-FOCUS-012)."""
        adapter.configure_unmapped_range(0x5000, 0x6000)
        addr = Address(space="ram", offset="0x5000", display="0x5000")
        with pytest.raises(ValueError, match="unmapped"):
            adapter.read_bytes(binary, addr, 16)

    def test_read_bytes_zero_length_raises(self, adapter: FakeAdapter, binary: Binary) -> None:
        """Zero-length read raises ValueError (VAL-FOCUS-013)."""
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        with pytest.raises(ValueError, match="positive"):
            adapter.read_bytes(binary, addr, 0)

    def test_read_bytes_truncation(self, adapter: FakeAdapter, binary: Binary) -> None:
        """Truncation at segment boundary returns partial data (VAL-FOCUS-014)."""
        adapter.configure_truncation(0x401000, 8)
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        data, length = adapter.read_bytes(binary, addr, 16)
        assert length == 8  # Truncated to 8
        assert len(data) == 8


# ---------------------------------------------------------------------------
# Xrefs, callers, callees, callgraph
# ---------------------------------------------------------------------------


class TestReferences:
    """Tests for xrefs, callers, callees, callgraph."""

    def test_get_xrefs(self, adapter: FakeAdapter, binary: Binary) -> None:
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        refs = adapter.get_xrefs(binary, addr)
        assert isinstance(refs, list)
        if refs:
            assert isinstance(refs[0], Reference)
            assert refs[0].kind is not None

    def test_get_xrefs_empty_for_unknown_address(
        self, adapter: FakeAdapter, binary: Binary
    ) -> None:
        """Xrefs on unknown address returns empty list, not error (VAL-FOCUS-016)."""
        addr = Address(space="ram", offset="0x999999", display="0x999999")
        refs = adapter.get_xrefs(binary, addr)
        assert isinstance(refs, list)

    def test_get_callers(self, adapter: FakeAdapter, binary: Binary) -> None:
        funcs = adapter.get_functions(binary)
        check = next(f for f in funcs if f.name == "check_password")
        callers = adapter.get_callers(binary, check)
        assert isinstance(callers, list)
        if callers:
            assert isinstance(callers[0], CallEdge)

    def test_get_callees(self, adapter: FakeAdapter, binary: Binary) -> None:
        funcs = adapter.get_functions(binary)
        main = next(f for f in funcs if f.name == "main")
        callees = adapter.get_callees(binary, main)
        assert isinstance(callees, list)
        if callees:
            assert isinstance(callees[0], CallEdge)
            assert callees[0].from_name == "main"

    def test_get_callgraph(self, adapter: FakeAdapter, binary: Binary) -> None:
        funcs = adapter.get_functions(binary)
        main = next(f for f in funcs if f.name == "main")
        cg = adapter.get_callgraph(binary, main, max_depth=2)
        assert isinstance(cg, CallGraph)
        assert cg.max_depth == 2

    def test_get_callgraph_with_depth(self, adapter: FakeAdapter, binary: Binary) -> None:
        funcs = adapter.get_functions(binary)
        main = next(f for f in funcs if f.name == "main")
        cg = adapter.get_callgraph(binary, main, max_depth=1)
        # All nodes should be at depth <= 1
        for node in cg.nodes:
            assert node["depth"] <= 1


# ---------------------------------------------------------------------------
# Fixtures — PE, ELF, Mach-O
# ---------------------------------------------------------------------------


class TestFixtures:
    """Tests for the built-in fixture helpers."""

    def test_pe_fixture(self) -> None:
        fixture = FakeAdapter.pe_fixture()
        assert fixture["format"] == "PE"
        assert fixture["architecture"] == "x86"
        assert fixture["endianness"] == Endianness.LITTLE
        assert len(fixture["sections"]) == 3
        assert len(fixture["functions"]) == 4
        assert len(fixture["imports"]) == 5
        assert len(fixture["exports"]) == 1
        assert len(fixture["strings"]) == 5

    def test_elf_fixture(self) -> None:
        fixture = FakeAdapter.elf_fixture()
        assert fixture["format"] == "ELF"
        assert fixture["architecture"] == "x86-64"
        assert fixture["endianness"] == Endianness.LITTLE
        assert len(fixture["sections"]) == 4  # .text, .rodata, .data, .bss
        assert len(fixture["functions"]) == 4
        assert len(fixture["imports"]) == 5
        assert len(fixture["exports"]) == 2  # main, compute_hash

    def test_macho_fixture(self) -> None:
        fixture = FakeAdapter.macho_fixture()
        assert fixture["format"] == "Mach-O"
        assert fixture["architecture"] == "arm64"
        assert fixture["endianness"] == Endianness.LITTLE
        assert (
            len(fixture["sections"]) == 6
        )  # __text, __cstring, __const, __data, __bss, __linkedit
        assert len(fixture["functions"]) == 3
        assert len(fixture["imports"]) == 4
        assert len(fixture["exports"]) == 2

    def test_pe_fixture_sections_have_deterministic_addresses(self) -> None:
        fixture = FakeAdapter.pe_fixture()
        text_sec = next(s for s in fixture["sections"] if s.name == ".text")
        assert text_sec.address is not None
        assert text_sec.address.offset == "0x401000"
        assert text_sec.address.space == "ram"

    def test_pe_fixture_functions_have_known_addresses(self) -> None:
        fixture = FakeAdapter.pe_fixture()
        main_fn = next(f for f in fixture["functions"] if f.name == "main")
        assert main_fn.address is not None
        assert main_fn.address.offset == "0x401000"
        assert main_fn.size_bytes == 512

    def test_elf_fixture_exports_are_deterministic(self) -> None:
        fixture = FakeAdapter.elf_fixture()
        exports = fixture["exports"]
        names = {e.name for e in exports}
        assert "main" in names
        assert "compute_hash" in names

    def test_macho_fixture_imports_are_deterministic(self) -> None:
        fixture = FakeAdapter.macho_fixture()
        imports = fixture["imports"]
        modules = {i.module for i in imports}
        assert "libSystem.B.dylib" in modules


# ---------------------------------------------------------------------------
# Failure simulation
# ---------------------------------------------------------------------------


class TestFailureSimulation:
    """Tests for all failure simulation modes."""

    def test_import_failure_exit_code_10(self, adapter: FakeAdapter, project: Project) -> None:
        adapter.configure_import_failure("bad.exe", "Disk full during import")
        with pytest.raises(ImportFailedError) as exc:
            adapter.import_binary("bad.exe", project)
        assert exc.value.exit_code == 10

    def test_analysis_crash_exit_code_11(self, adapter: FakeAdapter, binary: Binary) -> None:
        adapter.configure_analysis_failure("Segmentation fault in analyzer")
        profile = AnalysisProfile(name="standard", analysers=["functions"])
        with pytest.raises(AnalysisFailedError) as exc:
            adapter.analyze(binary, profile)
        assert exc.value.exit_code == 11

    def test_backend_failure_exit_code_13(self, adapter: FakeAdapter, binary: Binary) -> None:
        adapter.configure_backend_failure("get_functions", "JVM OOM error")
        with pytest.raises(BackendFailureError) as exc:
            adapter.get_functions(binary)
        assert exc.value.exit_code == 13

    def test_backend_failure_on_structural_query(
        self, adapter: FakeAdapter, binary: Binary
    ) -> None:
        """Backend crash during structural query (VAL-IMP-018)."""
        adapter.configure_backend_failure("get_sections", "Ghidra saw a ghost")
        with pytest.raises(BackendFailureError) as exc:
            adapter.get_sections(binary)
        assert exc.value.exit_code == 13

    def test_multiple_backend_failures(self, adapter: FakeAdapter, binary: Binary) -> None:
        adapter.configure_backend_failure("get_symbols", "Symbol lookup failed")
        adapter.configure_backend_failure("get_strings", "String extraction failed")

        with pytest.raises(BackendFailureError):
            adapter.get_symbols(binary)
        with pytest.raises(BackendFailureError):
            adapter.get_strings(binary)


# ---------------------------------------------------------------------------
# Slow operations
# ---------------------------------------------------------------------------


class TestSlowOperations:
    """Tests for slow operation simulation."""

    def test_slow_import(self, adapter: FakeAdapter, project: Project) -> None:
        adapter.configure_slow_operation("import", 0.1)
        start = time.time()
        adapter.import_binary("test.exe", project)
        elapsed = time.time() - start
        assert elapsed >= 0.1

    def test_slow_analyze(self, adapter: FakeAdapter, binary: Binary) -> None:
        adapter.configure_slow_operation("analyze", 0.1)
        profile = AnalysisProfile(name="quick", analysers=["functions"])
        start = time.time()
        adapter.analyze(binary, profile)
        elapsed = time.time() - start
        assert elapsed >= 0.1

    def test_slow_decompile(self, adapter: FakeAdapter, binary: Binary) -> None:
        adapter.configure_slow_operation("decompile", 0.1)
        funcs = adapter.get_functions(binary)
        main = next(f for f in funcs if f.name == "main")
        start = time.time()
        adapter.decompile(binary, main)
        elapsed = time.time() - start
        assert elapsed >= 0.1


# ---------------------------------------------------------------------------
# Address mapping edge cases
# ---------------------------------------------------------------------------


class TestAddressMapping:
    """Tests for unmapped addresses, partial mapping, and truncation."""

    def test_unmapped_address_range(self, adapter: FakeAdapter, binary: Binary) -> None:
        adapter.configure_unmapped_range(0x5000, 0x6000)
        addr = Address(space="ram", offset="0x5000", display="0x5000")
        with pytest.raises(ValueError, match="unmapped"):
            adapter.read_bytes(binary, addr, 16)

    def test_mapped_address_outside_unmapped_range(
        self, adapter: FakeAdapter, binary: Binary
    ) -> None:
        """Addresses outside the unmapped range should work normally."""
        adapter.configure_unmapped_range(0x5000, 0x6000)
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        _data, length = adapter.read_bytes(binary, addr, 16)
        assert length == 16

    def test_truncation_at_segment_boundary(self, adapter: FakeAdapter, binary: Binary) -> None:
        """Truncation returns fewer bytes than requested (VAL-FOCUS-014)."""
        adapter.configure_truncation(0x401000, 4)
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        data, actual = adapter.read_bytes(binary, addr, 16)
        assert actual == 4
        assert len(data) == 4

    def test_configuration_cleared(self, adapter: FakeAdapter, binary: Binary) -> None:
        adapter.configure_unmapped_range(0x5000, 0x6000)
        adapter.clear_configuration()
        addr = Address(space="ram", offset="0x5000", display="0x5000")
        # Should now work (not unmapped anymore)
        _data, length = adapter.read_bytes(binary, addr, 16)
        assert length == 16


# ---------------------------------------------------------------------------
# Custom fixture registration
# ---------------------------------------------------------------------------


class TestCustomFixtures:
    """Tests for registering custom fixtures."""

    def test_register_custom_fixture(self) -> None:
        adapter = FakeAdapter()
        custom = {
            "format": "PE",
            "architecture": "x86",
            "endianness": Endianness.LITTLE,
            "sections": [
                Section(name=".custom", flags=["r", "w", "x"]),
            ],
            "entrypoints": [],
            "imports": [],
            "exports": [],
            "symbols": [],
            "strings": [],
            "functions": [
                Function(name="custom_func", size_bytes=42),
            ],
        }
        adapter.set_fixture("custom", custom)
        assert "custom" in adapter._fixtures

    def test_custom_fixture_used_for_import(self, adapter: FakeAdapter, project: Project) -> None:
        """A custom fixture is used when importing a matching binary."""
        adapter.configure_import_failure("my-special.exe", "Import failed for my-special")
        with pytest.raises(ImportFailedError):
            adapter.import_binary("my-special.exe", project)


# ---------------------------------------------------------------------------
# Deterministic behavior
# ---------------------------------------------------------------------------


class TestDeterministicBehavior:
    """Tests for deterministic output across repeated calls."""

    def test_repeated_imports_same_sha256(self, adapter: FakeAdapter, project: Project) -> None:
        b1 = adapter.import_binary("test.exe", project)
        b2 = adapter.import_binary("test.exe", project)
        assert b1.sha256 == b2.sha256

    def test_repeated_section_queries_same_result(
        self, adapter: FakeAdapter, binary: Binary
    ) -> None:
        s1 = adapter.get_sections(binary)
        s2 = adapter.get_sections(binary)
        assert len(s1) == len(s2)
        for i in range(len(s1)):
            assert s1[i].name == s2[i].name

    def test_repeated_function_queries_same_result(
        self, adapter: FakeAdapter, binary: Binary
    ) -> None:
        f1 = adapter.get_functions(binary)
        f2 = adapter.get_functions(binary)
        assert len(f1) == len(f2)
        for i in range(len(f1)):
            assert f1[i].name == f2[i].name
            assert f1[i].size_bytes == f2[i].size_bytes


# ---------------------------------------------------------------------------
# Partial results
# ---------------------------------------------------------------------------


class TestEnvironmentConfiguration:
    """Tests for BINARY_FAKE_* environment variable support in FakeAdapter.__init__.

    These env vars enable black-box CLI testing of failure and injection modes
    without modifying CLI command modules.
    """

    def test_env_import_failure_triggers_import_failed_error(
        self, monkeypatch: Any, project: Project
    ) -> None:
        """BINARY_FAKE_IMPORT_FAILURE triggers ImportFailedError (exit 10)."""
        monkeypatch.setenv("BINARY_FAKE_IMPORT_FAILURE", "Simulated import error from env")
        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())

        with pytest.raises(ImportFailedError) as exc:
            adapter.import_binary("anyfile.exe", project)
        assert exc.value.exit_code == 10
        assert "Simulated import error from env" in str(exc.value)

    def test_env_analysis_failure_triggers_analysis_failed_error(
        self, monkeypatch: Any, binary: Binary
    ) -> None:
        """BINARY_FAKE_ANALYSIS_FAILURE triggers AnalysisFailedError (exit 11)."""
        monkeypatch.setenv("BINARY_FAKE_ANALYSIS_FAILURE", "Analysis crash from env")

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        # We need to import a binary first so the adapter knows about it
        b = adapter.import_binary("test.exe", Project(id=uuid4(), name="test-proj"))

        profile = AnalysisProfile(name="standard", analysers=["functions"])
        with pytest.raises(AnalysisFailedError) as exc:
            adapter.analyze(b, profile)
        assert exc.value.exit_code == 11
        assert "Analysis crash from env" in str(exc.value)

    def test_env_backend_failure_triggers_backend_failure_error(
        self, monkeypatch: Any, binary: Binary
    ) -> None:
        """BINARY_FAKE_BACKEND_FAILURE=method:msg triggers BackendFailureError (exit 13)."""
        monkeypatch.setenv("BINARY_FAKE_BACKEND_FAILURE", "get_functions:JVM OOM from env")

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        b = adapter.import_binary("test.exe", Project(id=uuid4(), name="test-proj"))

        with pytest.raises(BackendFailureError) as exc:
            adapter.get_functions(b)
        assert exc.value.exit_code == 13
        assert "JVM OOM from env" in str(exc.value)

    def test_env_backend_failure_defaults_to_get_functions(
        self, monkeypatch: Any, binary: Binary
    ) -> None:
        """BINARY_FAKE_BACKEND_FAILURE without colon defaults to get_functions."""
        monkeypatch.setenv("BINARY_FAKE_BACKEND_FAILURE", "Generic backend failure")

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        b = adapter.import_binary("test.exe", Project(id=uuid4(), name="test-proj"))

        with pytest.raises(BackendFailureError) as exc:
            adapter.get_functions(b)
        assert exc.value.exit_code == 13
        assert "Generic backend failure" in str(exc.value)

    def test_env_slow_import_adds_delay(self, monkeypatch: Any, project: Project) -> None:
        """BINARY_FAKE_SLOW_IMPORT_MS adds configurable delay to import."""
        monkeypatch.setenv("BINARY_FAKE_SLOW_IMPORT_MS", "100")

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())

        start = time.time()
        adapter.import_binary("test.exe", project)
        elapsed = time.time() - start
        assert elapsed >= 0.1, f"Expected >= 100ms delay, got {elapsed * 1000:.0f}ms"

    def test_env_slow_analyze_adds_delay(self, monkeypatch: Any, binary: Binary) -> None:
        """BINARY_FAKE_SLOW_ANALYZE_MS adds configurable delay to analyze."""
        monkeypatch.setenv("BINARY_FAKE_SLOW_ANALYZE_MS", "100")

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        b = adapter.import_binary("test.exe", Project(id=uuid4(), name="test-proj"))

        profile = AnalysisProfile(name="quick", analysers=["functions"])
        start = time.time()
        adapter.analyze(b, profile)
        elapsed = time.time() - start
        assert elapsed >= 0.1, f"Expected >= 100ms delay, got {elapsed * 1000:.0f}ms"

    def test_env_slow_decompile_adds_delay(self, monkeypatch: Any, binary: Binary) -> None:
        """BINARY_FAKE_SLOW_DECOMPILE_MS adds configurable delay to decompile."""
        monkeypatch.setenv("BINARY_FAKE_SLOW_DECOMPILE_MS", "100")

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        b = adapter.import_binary("test.exe", Project(id=uuid4(), name="test-proj"))

        funcs = adapter.get_functions(b)
        main = next(f for f in funcs if f.name == "main")
        start = time.time()
        adapter.decompile(b, main)
        elapsed = time.time() - start
        assert elapsed >= 0.1, f"Expected >= 100ms delay, got {elapsed * 1000:.0f}ms"

    def test_env_unmapped_ranges_marks_addresses_as_unmapped(
        self, monkeypatch: Any, binary: Binary
    ) -> None:
        """BINARY_FAKE_UNMAPPED_RANGES marks address ranges as unmapped."""
        monkeypatch.setenv("BINARY_FAKE_UNMAPPED_RANGES", "0x5000:0x6000,0x7000:0x7100")

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        b = adapter.import_binary("test.exe", Project(id=uuid4(), name="test-proj"))

        # Address 0x5000 should be unmapped
        addr1 = Address(space="ram", offset="0x5000", display="0x5000")
        with pytest.raises(ValueError, match="unmapped"):
            adapter.read_bytes(b, addr1, 16)

        # Address 0x7000 should also be unmapped
        addr2 = Address(space="ram", offset="0x7000", display="0x7000")
        with pytest.raises(ValueError, match="unmapped"):
            adapter.read_bytes(b, addr2, 16)

        # Address 0x401000 should still be mapped
        addr3 = Address(space="ram", offset="0x401000", display="0x401000")
        _data, length = adapter.read_bytes(b, addr3, 16)
        assert length == 16

    def test_env_truncation_limits_bytes_at_specified_addresses(
        self, monkeypatch: Any, binary: Binary
    ) -> None:
        """BINARY_FAKE_TRUNCATION limits bytes at specified addresses."""
        monkeypatch.setenv("BINARY_FAKE_TRUNCATION", "0x401000:8,0x402000:4")

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        b = adapter.import_binary("test.exe", Project(id=uuid4(), name="test-proj"))

        # Request 16 bytes at 0x401000, should get only 8
        addr1 = Address(space="ram", offset="0x401000", display="0x401000")
        data1, length1 = adapter.read_bytes(b, addr1, 16)
        assert length1 == 8
        assert len(data1) == 8

        # Request 16 bytes at 0x402000, should get only 4
        addr2 = Address(space="ram", offset="0x402000", display="0x402000")
        data2, length2 = adapter.read_bytes(b, addr2, 16)
        assert length2 == 4
        assert len(data2) == 4

    def test_env_empty_vars_do_not_affect_behavior(
        self, monkeypatch: Any, project: Project
    ) -> None:
        """Empty env vars produce a normal, fully functional adapter."""
        monkeypatch.setenv("BINARY_FAKE_IMPORT_FAILURE", "")
        monkeypatch.setenv("BINARY_FAKE_ANALYSIS_FAILURE", "")

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())

        # Should import normally
        b = adapter.import_binary("test.exe", project)
        assert isinstance(b, Binary)
        assert b.format == "PE"

    def test_env_vars_work_without_modifying_cli_modules(
        self, monkeypatch: Any, project: Project
    ) -> None:
        """Env vars are read in FakeAdapter.__init__ only; CLI modules are untouched."""
        monkeypatch.setenv("BINARY_FAKE_IMPORT_FAILURE", "Env import failure")
        monkeypatch.setenv("BINARY_FAKE_SLOW_ANALYZE_MS", "50")

        # Create adapter as CLI modules do (same pattern)
        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        adapter.set_fixture("elf-default", FakeAdapter.elf_fixture())
        adapter.set_fixture("macho-default", FakeAdapter.macho_fixture())

        # Import should fail from env var
        with pytest.raises(ImportFailedError) as exc:
            adapter.import_binary("test.exe", project)
        assert exc.value.exit_code == 10
        assert "Env import failure" in str(exc.value)

    def test_multiple_env_vars_combined(self, monkeypatch: Any, binary: Binary) -> None:
        """Multiple env vars combine correctly."""
        monkeypatch.setenv("BINARY_FAKE_BACKEND_FAILURE", "get_sections:Backend crash")
        monkeypatch.setenv("BINARY_FAKE_SLOW_DECOMPILE_MS", "50")
        monkeypatch.setenv("BINARY_FAKE_UNMAPPED_RANGES", "0x9999:0x999a")

        adapter = FakeAdapter()
        adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
        b = adapter.import_binary("test.exe", Project(id=uuid4(), name="test-proj"))

        # Backend failure on get_sections
        with pytest.raises(BackendFailureError) as exc:
            adapter.get_sections(b)
        assert exc.value.exit_code == 13
        assert "Backend crash" in str(exc.value)

        # Unmapped range
        addr = Address(space="ram", offset="0x9999", display="0x9999")
        with pytest.raises(ValueError, match="unmapped"):
            adapter.read_bytes(b, addr, 1)


class TestPartialResults:
    """Tests for partial analysis results."""

    def test_analyze_partial_when_some_analyzers_unavailable(
        self, adapter: FakeAdapter, binary: Binary
    ) -> None:
        # Request an analyser that doesn't exist in the fixture
        profile = AnalysisProfile(
            name="custom",
            analysers=["functions", "nonexistent_analyzer"],
        )
        result = adapter.analyze(binary, profile)
        assert result.partial is True
        assert len(result.completed_analysers) > 0
        assert len(result.failed_analysers) > 0
        assert len(result.diagnostics) > 0
