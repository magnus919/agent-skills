"""Unit tests for domain entities and the Address type."""

from __future__ import annotations

import json
from uuid import UUID, uuid4

import pytest
from binary_analysis.domain.entities import (
    Address,
    AuditEvent,
    BasicBlock,
    Binary,
    CallGraph,
    Capability,
    Diagnostic,
    EntryPoint,
    Export,
    Function,
    Heuristic,
    Import,
    Inference,
    Instruction,
    Observation,
    Project,
    Reference,
    Report,
    Section,
    String,
    Symbol,
    Unknown,
)
from binary_analysis.domain.enums import (
    Confidence,
    FunctionNameSource,
    ProjectState,
)


class TestAddress:
    """Tests for the canonical Address type."""

    def test_create_address_minimal(self) -> None:
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        assert addr.space == "ram"
        assert addr.offset == "0x401000"
        assert addr.display == "0x401000"
        assert addr.file_offset is None

    def test_create_address_with_file_offset(self) -> None:
        addr = Address(space="ram", offset="0x401000", display="0x401000", file_offset=6352)
        assert addr.file_offset == 6352

    def test_address_is_frozen(self) -> None:
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        with pytest.raises(AttributeError):
            addr.space = "other"  # type: ignore[misc]

    def test_offset_must_start_with_0x(self) -> None:
        with pytest.raises(ValueError, match="must start with '0x'"):
            Address(space="ram", offset="401000", display="401000")

    def test_to_dict_minimal(self) -> None:
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        d = addr.to_dict()
        assert d["space"] == "ram"
        assert d["offset"] == "0x401000"
        assert d["display"] == "0x401000"
        assert "file_offset" not in d  # omitted when None (VAL-JSON-003)

    def test_to_dict_with_file_offset(self) -> None:
        addr = Address(space="ram", offset="0x401000", display="0x401000", file_offset=6352)
        d = addr.to_dict()
        assert d["file_offset"] == 6352

    def test_to_dict_file_offset_is_integer(self) -> None:
        """file_offset must be an integer, not a string (VAL-JSON-003)."""
        addr = Address(space="ram", offset="0x401000", display="0x401000", file_offset=6352)
        d = addr.to_dict()
        assert isinstance(d["file_offset"], int)

    def test_from_dict(self) -> None:
        data = {"space": "ram", "offset": "0x401000", "display": "0x401000", "file_offset": 100}
        addr = Address.from_dict(data)
        assert addr.space == "ram"
        assert addr.offset == "0x401000"
        assert addr.display == "0x401000"
        assert addr.file_offset == 100

    def test_from_dict_minimal(self) -> None:
        data = {"space": "ram", "offset": "0x401000", "display": "0x401000"}
        addr = Address.from_dict(data)
        assert addr.file_offset is None

    def test_to_dict_serializable_to_json(self) -> None:
        """Address.to_dict() must produce JSON-serializable output."""
        addr = Address(space="ram", offset="0x4018d0", display="0x4018d0", file_offset=6352)
        d = addr.to_dict()
        raw = json.dumps(d)
        parsed = json.loads(raw)
        assert parsed["space"] == "ram"
        assert parsed["offset"] == "0x4018d0"
        assert parsed["file_offset"] == 6352

    def test_address_equality(self) -> None:
        a1 = Address(space="ram", offset="0x401000", display="0x401000")
        a2 = Address(space="ram", offset="0x401000", display="0x401000")
        a3 = Address(space="ram", offset="0x402000", display="0x402000")
        assert a1 == a2
        assert a1 != a3


class TestProjectEntity:
    """Tests for Project entity."""

    def test_default_project(self) -> None:
        p = Project()
        assert isinstance(p.id, UUID)
        assert p.name == ""
        assert p.state == ProjectState.CREATED
        assert p.binary_count == 0
        assert p.is_stale is False
        assert p.lock is None

    def test_custom_project(self) -> None:
        pid = uuid4()
        p = Project(
            id=pid,
            name="my-analysis",
            state=ProjectState.READY,
            binary_count=2,
            is_stale=True,
        )
        assert p.id == pid
        assert p.name == "my-analysis"
        assert p.state == ProjectState.READY
        assert p.binary_count == 2
        assert p.is_stale is True


class TestBinaryEntity:
    """Tests for Binary entity."""

    def test_default_binary(self) -> None:
        b = Binary()
        assert isinstance(b.id, UUID)
        assert b.size_bytes == 0
        assert b.import_mode == "copy"
        assert b.is_stale is False

    def test_size_bytes_is_int(self) -> None:
        """size_bytes must be an int, never a string (VAL-JSON-004)."""
        b = Binary(size_bytes=4096)
        assert isinstance(b.size_bytes, int)
        assert b.size_bytes == 4096

    def test_optional_fields_default_to_none(self) -> None:
        """Optional fields should default to None (VAL-JSON-006)."""
        b = Binary()
        assert b.architecture is None
        assert b.endianness is None
        assert b.entry_point is None
        assert b.compiler is None
        assert b.source_language is None
        assert b.imported_at is None
        assert b.analyzed_at is None


class TestSectionEntity:
    """Tests for Section entity."""

    def test_default_section(self) -> None:
        s = Section()
        assert s.name == ""
        assert s.virtual_size == 0
        assert s.raw_size == 0
        assert s.flags == []
        assert s.entropy is None

    def test_sizes_are_ints(self) -> None:
        """virtual_size and raw_size must be ints (VAL-JSON-004)."""
        s = Section(name=".text", virtual_size=4096, raw_size=4096)
        assert isinstance(s.virtual_size, int)
        assert isinstance(s.raw_size, int)

    def test_entropy_can_be_float_or_none(self) -> None:
        s = Section(name=".text", entropy=6.5)
        assert isinstance(s.entropy, float)
        s2 = Section(name=".data")
        assert s2.entropy is None


class TestFunctionEntity:
    """Tests for Function entity."""

    def test_default_function(self) -> None:
        f = Function()
        assert f.name == ""
        assert f.address is None
        assert f.size_bytes == 0
        assert f.confidence == Confidence.UNKNOWN
        assert f.name_source == FunctionNameSource.UNKNOWN
        assert f.is_external is False
        assert f.is_thunk is False

    def test_size_bytes_is_int(self) -> None:
        f = Function(name="main", size_bytes=256)
        assert isinstance(f.size_bytes, int)

    def test_optional_fields_null(self) -> None:
        f = Function()
        assert f.signature is None
        assert f.source_language is None
        assert f.basic_block_count is None
        assert f.instruction_count is None
        assert f.cyclomatic_complexity is None

    def test_confidece_is_enum(self) -> None:
        f = Function(name="main", confidence=Confidence.HIGH)
        assert f.confidence == Confidence.HIGH
        assert isinstance(f.confidence, Confidence)


class TestAllEntityDefaults:
    """Verify that all optional fields default to None (VAL-JSON-006)."""

    def test_entrypoint_optional_fields_null(self) -> None:
        e = EntryPoint()
        assert e.address is None
        assert e.name is None
        assert e.binary_id is None

    def test_import_optional_fields_null(self) -> None:
        imp = Import()
        assert imp.address is None
        assert imp.ordinal is None
        assert imp.binary_id is None

    def test_export_optional_fields_null(self) -> None:
        exp = Export()
        assert exp.address is None
        assert exp.ordinal is None
        assert exp.forwarder is None
        assert exp.binary_id is None

    def test_symbol_optional_fields_null(self) -> None:
        s = Symbol()
        assert s.address is None
        assert s.binary_id is None

    def test_string_optional_fields_null(self) -> None:
        s = String()
        assert s.address is None
        assert s.binary_id is None


class TestEntitySizeFields:
    """Verify all size fields are integer bytes (VAL-JSON-004)."""

    def test_all_size_fields_are_int(self) -> None:
        """Every size-like field must be int type."""
        # Create each entity with size fields and verify they are ints
        entities = [
            ("Binary", Binary(size_bytes=100)),
            ("Section", Section(virtual_size=200, raw_size=150)),
            ("Function", Function(size_bytes=300)),
            ("String", String(length=50)),
            ("Instruction", Instruction(size_bytes=4)),
            ("BasicBlock", BasicBlock(instruction_count=10)),
        ]

        for name, entity in entities:
            for field_name in [
                "size_bytes",
                "virtual_size",
                "raw_size",
                "length",
                "instruction_count",
                "binary_count",
            ]:
                value = getattr(entity, field_name, None)
                if value is not None:
                    assert isinstance(value, int), (
                        f"{name}.{field_name} is {type(value).__name__}, expected int"
                    )


class TestEntityOnlyCanonicalFields:
    """Verify entities contain only canonical fields (VAL-JSON-018)."""

    def test_no_internal_fields_on_project(self) -> None:
        """Project entity must not have backend-specific keys."""
        p = Project(name="test")
        d = vars(p)
        # Should not contain any backend-specific keys
        assert "_ghidra_id" not in d
        assert "program_address" not in d
        assert "analyzer_ordinal" not in d

    def test_no_internal_fields_on_function(self) -> None:
        """Function entity must not have backend-specific keys."""
        f = Function(name="main")
        d = vars(f)
        assert "_ghidra_id" not in d
        assert "ghidra_internal_id" not in d
        assert "backend_raw" not in d

    def test_no_internal_fields_on_section(self) -> None:
        """Section entity must not have backend-specific keys."""
        s = Section(name=".text")
        d = vars(s)
        assert "ghidra_section_id" not in d


class TestAllEntitiesInstantiable:
    """Verify all 21 entity types can be instantiated."""

    def test_all_entities_instantiate(self) -> None:
        entities = [
            Project(name="test"),
            Binary(),
            Section(),
            EntryPoint(),
            Import(),
            Export(),
            Symbol(),
            String(),
            Function(),
            Instruction(),
            BasicBlock(),
            Reference(),
            CallGraph(),
            Diagnostic(),
            Capability(),
            Observation(),
            Heuristic(),
            Inference(),
            Unknown(),
            Report(),
            AuditEvent(),
        ]
        assert len(entities) == 21
