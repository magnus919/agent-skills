"""Unit tests for JSON serialization schemas and helpers.

Validates contract assertions:
  - VAL-JSON-003: Addresses use canonical structured format
  - VAL-JSON-004: All size fields are integer bytes
  - VAL-JSON-006: Unknown/null fields serialize as JSON null
  - VAL-JSON-013: Enum values serialize as UPPER_CASE strings
  - VAL-JSON-018: Entity objects contain only canonical fields
  - VAL-STRUCT-017: Strings with embedded quotes and backslashes escaped
"""

from __future__ import annotations

import sys
from pathlib import Path
_scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import json

from binary_analysis.domain.entities import (
    Address,
    Function,
    Section,
)
from binary_analysis.domain.enums import (
    Confidence,
    DiagnosticSeverity,
    FunctionNameSource,
    ProjectState,
    ReferenceKind,
)
from binary_analysis.domain.schemas import (
    FUNCTION_CANONICAL_FIELDS,
    canonical_address,
    deserialize_address,
    entity_to_dict,
    safe_json_dumps,
    serialize_address,
    serialize_enum,
)


class TestAddressSerialization:
    """Tests for address serialization (VAL-JSON-003)."""

    def test_serialize_address_dict(self) -> None:
        """serialize_address returns a structured dict."""
        addr = Address(space="ram", offset="0x4018d0", display="0x4018d0", file_offset=6352)
        result = serialize_address(addr)
        assert result is not None
        assert result["space"] == "ram"
        assert result["offset"] == "0x4018d0"
        assert result["display"] == "0x4018d0"
        assert result["file_offset"] == 6352

    def test_serialize_address_null(self) -> None:
        """serialize_address returns None for null input (VAL-JSON-006)."""
        result = serialize_address(None)
        assert result is None

    def test_serialize_address_no_file_offset(self) -> None:
        """Optional file_offset is omitted when absent."""
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        result = serialize_address(addr)
        assert result is not None
        assert "file_offset" not in result

    def test_deserialize_address(self) -> None:
        data = {"space": "ram", "offset": "0x401000", "display": "0x401000"}
        addr = deserialize_address(data)
        assert addr is not None
        assert addr.space == "ram"
        assert addr.offset == "0x401000"

    def test_deserialize_address_null(self) -> None:
        """deserialize_address returns None for null input."""
        result = deserialize_address(None)
        assert result is None

    def test_canonical_address_factory(self) -> None:
        """canonical_address factory creates valid addresses."""
        addr = canonical_address("ram", "0x401000")
        assert addr.space == "ram"
        assert addr.offset == "0x401000"
        assert addr.display == "0x401000"

    def test_canonical_address_adds_0x_prefix(self) -> None:
        """canonical_address adds 0x prefix if missing."""
        addr = canonical_address("ram", "401000")
        assert addr.offset == "0x401000"

    def test_address_in_json(self) -> None:
        """Address must serialize as a structured object in JSON,
        never a bare string or integer (VAL-JSON-003)."""
        addr = Address(space="ram", offset="0x4018d0", display="0x4018d0")
        d = addr.to_dict()
        raw = json.dumps(d)
        # Must be an object, not a bare string
        assert raw.startswith("{")
        assert '"space"' in raw
        assert '"offset"' in raw
        assert '"display"' in raw


class TestEnumSerialization:
    """Tests for enum serialization (VAL-JSON-013)."""

    def test_serialize_enum_to_string(self) -> None:
        """Enums serialize as UPPER_CASE strings."""
        assert serialize_enum(ProjectState.CREATED) == "CREATED"
        assert serialize_enum(Confidence.HIGH) == "HIGH"
        assert serialize_enum(DiagnosticSeverity.WARNING) == "WARNING"
        assert serialize_enum(ReferenceKind.CALL) == "CALL"
        assert serialize_enum(FunctionNameSource.ORIGINAL) == "ORIGINAL"

    def test_serialize_enum_null(self) -> None:
        """Null enum serializes as None (JSON null)."""
        assert serialize_enum(None) is None

    def test_serialize_enum_string_passthrough(self) -> None:
        """String input is uppercased."""
        assert serialize_enum("high") == "HIGH"

    def test_enum_json_output(self) -> None:
        """Verify enum values in JSON are quoted UPPER_CASE strings."""
        data = {"state": ProjectState.CREATED.value, "confidence": Confidence.HIGH.value}
        raw = json.dumps(data)
        assert '"CREATED"' in raw
        assert '"HIGH"' in raw
        # Must NOT be integer ordinals
        assert "0" not in raw.split('"CREATED"')[0]


class TestEntitySerialization:
    """Tests for entity-to-dict serialization."""

    def test_entity_to_dict_basic(self) -> None:
        """entity_to_dict converts a dataclass to a plain dict."""
        f = Function(name="main", size_bytes=256, confidence=Confidence.HIGH)
        d = entity_to_dict(f)
        assert d["name"] == "main"
        assert d["size_bytes"] == 256
        assert d["confidence"] == "HIGH"

    def test_address_in_entity_serialized_as_dict(self) -> None:
        """Address fields in entities must be structured dicts."""
        addr = Address(space="ram", offset="0x401000", display="0x401000")
        f = Function(name="main", address=addr, size_bytes=128)
        d = entity_to_dict(f)
        assert isinstance(d["address"], dict)
        assert d["address"]["space"] == "ram"

    def test_null_address_serializes_as_null(self) -> None:
        """Null address field must serialize as JSON null (VAL-JSON-006)."""
        f = Function(name="main")
        d = entity_to_dict(f)
        assert d["address"] is None

    def test_size_fields_are_ints(self) -> None:
        """All size fields must be JSON numbers (integers), never strings (VAL-JSON-004)."""
        f = Function(name="main", size_bytes=4096)
        d = entity_to_dict(f)
        assert isinstance(d["size_bytes"], int)
        assert d["size_bytes"] == 4096

    def test_canonical_fields_restriction(self) -> None:
        """entity_to_dict with canonical_fields restricts output (VAL-JSON-018)."""
        f = Function(
            name="main",
            address=Address(space="ram", offset="0x401000", display="0x401000"),
            size_bytes=256,
            confidence=Confidence.HIGH,
            name_source=FunctionNameSource.ORIGINAL,
            is_external=True,
        )
        d = entity_to_dict(f, canonical_fields={"name", "address", "size_bytes"})
        assert set(d.keys()) == {"name", "address", "size_bytes"}
        assert "confidence" not in d
        assert "name_source" not in d
        assert "is_external" not in d

    def test_function_canonical_fields_match_expected(self) -> None:
        """Verify the function canonical field list covers key fields."""
        assert "name" in FUNCTION_CANONICAL_FIELDS
        assert "address" in FUNCTION_CANONICAL_FIELDS
        assert "size_bytes" in FUNCTION_CANONICAL_FIELDS
        assert "confidence" in FUNCTION_CANONICAL_FIELDS
        assert "name_source" in FUNCTION_CANONICAL_FIELDS
        assert "is_external" in FUNCTION_CANONICAL_FIELDS
        assert "is_thunk" in FUNCTION_CANONICAL_FIELDS


class TestSafeJsonDumps:
    """Tests for JSON escaping (VAL-STRUCT-017)."""

    def test_valid_json_output(self) -> None:
        """safe_json_dumps produces valid parseable JSON."""
        data = {"message": "hello world", "count": 42}
        raw = safe_json_dumps(data)
        parsed = json.loads(raw)
        assert parsed == data

    def test_embedded_quotes_escaped(self) -> None:
        """Strings with embedded double quotes must be escaped (VAL-STRUCT-017)."""
        text = 'He said "hello"'
        data = {"text": text}
        raw = safe_json_dumps(data)
        parsed = json.loads(raw)
        assert parsed["text"] == text

    def test_embedded_backslashes_escaped(self) -> None:
        """Strings with backslashes must be escaped (VAL-STRUCT-017)."""
        text = "C:\\path\\to\\file"
        data = {"path": text}
        raw = safe_json_dumps(data)
        parsed = json.loads(raw)
        assert parsed["path"] == text

    def test_combined_quotes_and_backslashes(self) -> None:
        """Combined quotes and backslashes must be escaped."""
        text = 'file "test" at C:\\dir\\file.txt'
        data = {"text": text}
        raw = safe_json_dumps(data)
        parsed = json.loads(raw)
        assert parsed["text"] == text

    def test_control_characters_escaped(self) -> None:
        """Control characters must be escaped."""
        text = "line1\nline2\tindented"
        data = {"text": text}
        raw = safe_json_dumps(data)
        parsed = json.loads(raw)
        assert parsed["text"] == text
        # Verify the raw JSON contains escape sequences
        assert "\\n" in raw
        assert "\\t" in raw

    def test_unicode_preserved(self) -> None:
        """Unicode characters should be preserved by default (ensure_ascii=False)."""
        text = "こんにちは"
        data = {"text": text}
        raw = safe_json_dumps(data)
        parsed = json.loads(raw)
        assert parsed["text"] == text

    def test_ascii_mode_escapes_unicode(self) -> None:
        """ensure_ascii=True should escape non-ASCII characters."""
        text = "こんにちは"
        data = {"text": text}
        raw = safe_json_dumps(data, ensure_ascii=True)
        parsed = json.loads(raw)
        assert parsed["text"] == text
        # In ASCII mode, non-ASCII chars are \u-escaped
        assert "こ" not in raw


class TestNullSerialization:
    """Tests for null serialization (VAL-JSON-006)."""

    def test_none_serializes_as_null(self) -> None:
        """Python None must serialize as JSON null, never "" or 0."""
        data = {"value": None}
        raw = json.dumps(data)
        assert '"value": null' in raw

    def test_optional_entity_field_null(self) -> None:
        """Optional entity fields with None serialize as null."""
        f = Function(name="main", signature=None)
        d = entity_to_dict(f)
        assert d["signature"] is None

    def test_null_not_empty_string(self) -> None:
        """Null must not serialize as empty string."""
        data = {"compiler": None}
        raw = json.dumps(data)
        assert '""' not in raw

    def test_null_not_zero(self) -> None:
        """Null must not serialize as zero."""
        data = {"entry_point": None}
        raw = json.dumps(data)
        # Entry point should be null, not 0
        parsed = json.loads(raw)
        assert parsed["entry_point"] is None


class TestSizeFieldIntegers:
    """Tests for size field serialization (VAL-JSON-004)."""

    def test_sizes_not_strings(self) -> None:
        """Size fields must NEVER be strings."""
        f = Function(name="main", size_bytes=4096)
        d = entity_to_dict(f)
        assert isinstance(d["size_bytes"], int)

    def test_simple_section_sizes(self) -> None:
        s = Section(name=".text", virtual_size=8192, raw_size=4096)
        d = entity_to_dict(s)
        assert isinstance(d["virtual_size"], int)
        assert isinstance(d["raw_size"], int)
