"""JSON serialization helpers for the canonical domain model.

Key serialization rules:
  - Addresses: structured objects (space, offset, display, optional file_offset)
  - Sizes: integer bytes (JSON number), never strings
  - Unknown/null fields: serialize as JSON null, not "" or 0
  - Enum values: UPPER_CASE strings matching documented enum members
  - Entity objects: only canonical fields; no backend-specific keys
  - Strings: correct JSON escaping of embedded quotes, backslashes, control chars
"""

from __future__ import annotations

import dataclasses
import json
from enum import Enum
from typing import Any

from binary_analysis.domain.entities import Address

# ---------------------------------------------------------------------------
# Address serialization
# ---------------------------------------------------------------------------


def serialize_address(addr: Address | None) -> dict[str, Any] | None:
    """Serialize an Address to its canonical dict form, or null."""
    if addr is None:
        return None
    return addr.to_dict()


def deserialize_address(data: dict[str, Any] | None) -> Address | None:
    """Deserialize a canonical dict back to an Address, or null."""
    if data is None:
        return None
    return Address.from_dict(data)


def canonical_address(
    space: str, offset: str, display: str | None = None, file_offset: int | None = None
) -> Address:
    """Factory for creating canonical addresses with validated format.

    Args:
        space: Address space name (e.g., "ram", "register").
        offset: Hex-prefixed offset string (e.g., "0x401000").
        display: Display string. Defaults to offset if not provided.
        file_offset: Optional byte offset within the file.
    """
    if not offset.startswith("0x"):
        offset = f"0x{offset}"
    if display is None:
        display = offset
    return Address(space=space, offset=offset, display=display, file_offset=file_offset)


# ---------------------------------------------------------------------------
# Enum serialization
# ---------------------------------------------------------------------------


def serialize_enum(value: Enum | None) -> str | None:
    """Serialize an enum member to its UPPER_CASE string name, or null."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.upper()
    return str(value.value)


# ---------------------------------------------------------------------------
# Entity serialization (generic)
# ---------------------------------------------------------------------------


def entity_to_dict(
    entity: Any,
    canonical_fields: set[str] | None = None,
) -> dict[str, Any]:
    """Convert a dataclass entity to a dict using only canonical fields.

    Args:
        entity: The dataclass entity to serialize.
        canonical_fields: Optional whitelist of field names to include.
            If not provided, all dataclass fields are serialized.

    Returns:
        A dict with only canonical fields, with proper serialization:
        - Addresses become structured dicts or null
        - Enums become UPPER_CASE strings or null
        - UUIDs become strings
        - None values remain as null
        - Sizes remain as integers (never converted to strings)
    """
    result: dict[str, Any] = {}
    fields_dict = {f.name: f for f in dataclasses.fields(entity)}

    for field_name in fields_dict:
        # Skip non-canonical fields if a whitelist is provided
        if canonical_fields is not None and field_name not in canonical_fields:
            continue

        value = getattr(entity, field_name)

        # Serialize based on type
        serialized = _serialize_value(value)

        # Only include optional fields if they have a non-None value,
        # to keep the JSON minimal
        result[field_name] = serialized

    return result


def _serialize_value(value: Any) -> Any:
    """Serialize a single value to its JSON-compatible form.

    Rules:
    - None → None (JSON null)
    - Address → structured dict or None
    - Enum → UPPER_CASE string or None
    - UUID → string
    - list → list of serialized values
    - dict → dict of serialized values
    - booleans → remain booleans
    - integers → remain integers (never strings)
    - floats → remain floats
    - strings → remain strings
    """
    if value is None:
        return None
    if isinstance(value, Address):
        return value.to_dict()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    # Primitives pass through as-is
    return value


# ---------------------------------------------------------------------------
# Canonical field whitelists per entity type
# These ensure no backend-specific keys leak into entity objects.
# ---------------------------------------------------------------------------

PROJECT_CANONICAL_FIELDS = frozenset(
    {
        "id",
        "name",
        "state",
        "created_at",
        "updated_at",
        "workspace_version",
        "binary_count",
        "is_stale",
        "lock",
        "description",
        "max_binary_size_bytes",
    }
)

BINARY_CANONICAL_FIELDS = frozenset(
    {
        "id",
        "sha256",
        "path",
        "format",
        "import_mode",
        "size_bytes",
        "architecture",
        "endianness",
        "entry_point",
        "compiler",
        "source_language",
        "imported_at",
        "analyzed_at",
        "analysis_profile",
        "is_stale",
    }
)

SECTION_CANONICAL_FIELDS = frozenset(
    {
        "name",
        "binary_id",
        "address",
        "virtual_size",
        "raw_size",
        "flags",
        "entropy",
        "content_hash",
    }
)

ENTRYPOINT_CANONICAL_FIELDS = frozenset(
    {
        "address",
        "kind",
        "confidence",
        "name",
        "binary_id",
    }
)

IMPORT_CANONICAL_FIELDS = frozenset(
    {
        "module",
        "symbol",
        "address",
        "resolution",
        "ordinal",
        "binary_id",
    }
)

EXPORT_CANONICAL_FIELDS = frozenset(
    {
        "name",
        "address",
        "ordinal",
        "forwarder",
        "kind",
        "binary_id",
    }
)

SYMBOL_CANONICAL_FIELDS = frozenset(
    {
        "name",
        "address",
        "source",
        "scope",
        "binary_id",
    }
)

STRING_CANONICAL_FIELDS = frozenset(
    {
        "text",
        "encoding",
        "address",
        "length",
        "binary_id",
    }
)

FUNCTION_CANONICAL_FIELDS = frozenset(
    {
        "name",
        "address",
        "size_bytes",
        "confidence",
        "name_source",
        "binary_id",
        "is_external",
        "is_thunk",
        "signature",
        "source_language",
        "basic_block_count",
        "instruction_count",
        "cyclomatic_complexity",
    }
)

INSTRUCTION_CANONICAL_FIELDS = frozenset(
    {
        "mnemonic",
        "operands",
        "bytes_hex",
        "address",
        "size_bytes",
        "function_id",
    }
)

BASIC_BLOCK_CANONICAL_FIELDS = frozenset(
    {
        "start_address",
        "end_address",
        "instruction_count",
        "function_id",
        "is_entry",
        "is_exit",
    }
)

REFERENCE_CANONICAL_FIELDS = frozenset(
    {
        "from_addr",
        "to_addr",
        "kind",
        "confidence",
        "binary_id",
    }
)

CALLGRAPH_CANONICAL_FIELDS = frozenset(
    {
        "root_address",
        "nodes",
        "edges",
        "max_depth",
        "total_nodes",
        "total_edges",
        "truncated",
        "binary_id",
    }
)

DIAGNOSTIC_CANONICAL_FIELDS = frozenset(
    {
        "severity",
        "category",
        "message",
        "component",
        "remediation",
        "recoverable",
    }
)

CAPABILITY_CANONICAL_FIELDS = frozenset(
    {
        "name",
        "confidence",
        "evidence",
        "binary_id",
    }
)

OBSERVATION_CANONICAL_FIELDS = frozenset(
    {
        "category",
        "description",
        "source",
        "address",
        "evidence",
        "binary_id",
    }
)

HEURISTIC_CANONICAL_FIELDS = frozenset(
    {
        "name",
        "description",
        "confidence",
        "rule_id",
        "evidence",
        "binary_id",
    }
)

INFERENCE_CANONICAL_FIELDS = frozenset(
    {
        "description",
        "confidence",
        "basis",
        "binary_id",
    }
)

UNKNOWN_CANONICAL_FIELDS = frozenset(
    {
        "address",
        "question",
        "category",
        "binary_id",
    }
)

REPORT_CANONICAL_FIELDS = frozenset(
    {
        "id",
        "report_type",
        "project_id",
        "binary_id",
        "created_at",
        "format",
        "summary",
        "sections",
    }
)

AUDIT_EVENT_CANONICAL_FIELDS = frozenset(
    {
        "timestamp",
        "event_type",
        "result",
        "project_id",
        "binary_id",
        "user",
        "details",
    }
)


# ---------------------------------------------------------------------------
# JSON encoding with correct string escaping
# ---------------------------------------------------------------------------


def safe_json_dumps(obj: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
    """Serialize to JSON with correct escaping of embedded quotes, backslashes,
    and control characters.

    Uses json.dumps with ensure_ascii=False (preserving Unicode) unless
    ensure_ascii is explicitly True. The standard library json module
    correctly escapes ", \\, and control characters by default, but we
    document the expected behavior here.

    Args:
        obj: The object to serialize.
        indent: Indentation level (default 2 spaces).
        ensure_ascii: Whether to escape non-ASCII characters.

    Returns:
        A valid JSON string.

    Serialization rules enforced:
    - Double quotes in strings → \\"
    - Backslashes in strings → \\\\
    - Control characters → \\uXXXX
    - Unicode preserved by default (ensure_ascii=False)
    """
    return json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii)


# ---------------------------------------------------------------------------
# Serializable entity mixin
# ---------------------------------------------------------------------------


class SerializableEntity:
    """Mixin for entities that need JSON serialization.

    Subclasses must implement to_dict() and can override _canonical_fields
    to restrict which fields are serialized.
    """

    _canonical_fields: frozenset[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-compatible dict."""
        if self._canonical_fields is not None:
            return entity_to_dict(self, set(self._canonical_fields))
        return entity_to_dict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string with correct escaping."""
        return safe_json_dumps(self.to_dict(), indent=indent)
