"""Entity selectors for resolving function, address, and entity references.

Selectors are human-readable strings that resolve to specific entities.
Supported selector formats:
  - function:<name>  — Resolve a function by name (exact or fuzzy match)
  - function:<address>  — Resolve a function by address
  - address:<addr-range>  — Resolve an address range (e.g., 0x1000..0x2000)
  - name:<entity-name>  — Generic entity lookup by name
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from binary_analysis.domain.entities import Function
from binary_analysis.domain.errors import AmbiguousSelectorError, EntityNotFoundError

# ---------------------------------------------------------------------------
# Selector types
# ---------------------------------------------------------------------------


class SelectorKind:
    """Selector kind constants."""

    FUNCTION = "function"
    ADDRESS = "address"
    NAME = "name"


# ---------------------------------------------------------------------------
# Parsed selector
# ---------------------------------------------------------------------------


@dataclass
class ParsedSelector:
    """Result of parsing an entity selector string.

    Attributes:
        kind: The selector kind (function, address, name).
        value: The parsed selector value.
        raw: The original selector string.
        is_address: Whether the value represents an address.
        address_value: Parsed address offset (hex string without 0x prefix) if applicable.
        is_range: Whether the selector specifies a range.
        range_start: Start of range if is_range is True.
        range_end: End of range if is_range is True.
    """

    kind: str = ""
    value: str = ""
    raw: str = ""
    is_address: bool = False
    address_value: str | None = None
    is_range: bool = False
    range_start: str | None = None
    range_end: str | None = None

    def __str__(self) -> str:
        return self.raw


# ---------------------------------------------------------------------------
# Selector parser
# ---------------------------------------------------------------------------

_ADDRESS_PATTERN = re.compile(r"^(0x)?[0-9a-fA-F]+$")
_RANGE_PATTERN = re.compile(r"^(0x)?[0-9a-fA-F]+\.\.(0x)?[0-9a-fA-F]+$")
_SELECTOR_PATTERN = re.compile(r"^(function|address|name):(.+)$", re.IGNORECASE)


def parse_selector(raw: str) -> ParsedSelector:
    """Parse a selector string into its components.

    Supported formats:
      "function:main"         → function selector by name
      "function:0x401000"     → function selector by address
      "address:0x1000..0x2000" → address range selector
      "name:entrypoint"       → generic name selector
      "main"                  → implicit function selector (shorthand)
      "0x401000"              → implicit address selector (shorthand)

    Args:
        raw: The raw selector string.

    Returns:
        A ParsedSelector with kind, value, and parsed components.
    """
    result = ParsedSelector(raw=raw, kind=SelectorKind.NAME, value=raw)

    # Try explicit selector format: kind:value
    match = _SELECTOR_PATTERN.match(raw)
    if match:
        kind = match.group(1).lower()
        value = match.group(2)

        if kind == SelectorKind.FUNCTION:
            result.kind = SelectorKind.FUNCTION
            result.value = value
        elif kind == SelectorKind.ADDRESS:
            result.kind = SelectorKind.ADDRESS
            result.value = value
        else:
            result.kind = SelectorKind.NAME
            result.value = value
    else:
        # Implicit: check if it looks like an address
        if _ADDRESS_PATTERN.match(raw):
            result.kind = SelectorKind.ADDRESS
            result.value = raw
        else:
            result.kind = SelectorKind.FUNCTION
            result.value = raw

    # Check if it's an address value
    if _ADDRESS_PATTERN.match(result.value):
        result.is_address = True
        addr = result.value
        if addr.startswith("0x") or addr.startswith("0X"):
            result.address_value = addr[2:].lower()
        else:
            result.address_value = addr.lower()

    # Check if it's a range
    if _RANGE_PATTERN.match(result.value):
        result.is_range = True
        parts = result.value.split("..")
        result.range_start = parts[0]
        result.range_end = parts[1]

    return result


# ---------------------------------------------------------------------------
# Entity resolver
# ---------------------------------------------------------------------------


@dataclass
class ResolvedEntity:
    """Result of resolving a selector to one or more entities.

    Attributes:
        selector: The parsed selector that was resolved.
        entity_type: The type of entity resolved (e.g., "Function", "Address").
        exact_match: The single entity if resolution was unambiguous.
        candidates: List of candidates if multiple matches were found.
        is_ambiguous: Whether resolution produced multiple candidates.
    """

    selector: ParsedSelector
    entity_type: str = ""
    exact_match: Any | None = None
    candidates: list[Any] = field(default_factory=list)
    is_ambiguous: bool = False


def resolve_function(
    parsed: ParsedSelector,
    functions: list[Function],
    require_unique: bool = True,
) -> Function:
    """Resolve a function selector to a single Function entity.

    Args:
        parsed: The parsed function selector.
        functions: List of functions to search.
        require_unique: If True, raise AmbiguousSelectorError when multiple
            functions match.

    Returns:
        The matching Function entity.

    Raises:
        EntityNotFoundError: If no function matches the selector.
        AmbiguousSelectorError: If multiple functions match and require_unique is True.
    """
    if parsed.is_address:
        # Lookup by address
        addr_val = parsed.address_value or ""
        matches = [
            f
            for f in functions
            if f.address is not None and f.address.offset.lower() == f"0x{addr_val}"
        ]
        if not matches:
            matches = [
                f
                for f in functions
                if f.address is not None and addr_val in f.address.offset.lower()
            ]
    else:
        # Lookup by name
        search_name = parsed.value.lower()
        exact_matches = [f for f in functions if f.name.lower() == search_name]
        matches = exact_matches or [f for f in functions if search_name in f.name.lower()]

    if not matches:
        raise EntityNotFoundError("Function", parsed.raw)

    if len(matches) > 1 and require_unique:
        candidates_info = [
            {
                "name": f.name,
                "address": f.address.to_dict() if f.address else None,
                "size_bytes": f.size_bytes,
            }
            for f in matches
        ]
        raise AmbiguousSelectorError(
            f"Function selector '{parsed.raw}' matches {len(matches)} functions",
            candidates=candidates_info,
        )

    return matches[0]


def resolve_functions(
    parsed: ParsedSelector,
    functions: list[Function],
) -> list[Function]:
    """Resolve a function selector to all matching Function entities.

    Args:
        parsed: The parsed function selector.
        functions: List of functions to search.

    Returns:
        List of matching Function entities (may be empty).
    """
    if parsed.is_address:
        addr_val = parsed.address_value or ""
        matches = [
            f for f in functions if f.address is not None and addr_val in f.address.offset.lower()
        ]
    else:
        search_name = parsed.value.lower()
        matches = [f for f in functions if search_name in f.name.lower()]

    return matches


def format_candidates(candidates: list[dict[str, Any]]) -> str:
    """Format candidate entities for display in ambiguity errors.

    Args:
        candidates: List of candidate dicts with name, address, and optional info.

    Returns:
        A human-readable string listing candidates.
    """
    lines = ["Ambiguous selector matches multiple entities:"]
    for i, candidate in enumerate(candidates, start=1):
        name = candidate.get("name", "unknown")
        addr = candidate.get("address", {})
        if isinstance(addr, dict):
            display = addr.get("display", addr.get("offset", "?"))
        else:
            display = str(addr)
        lines.append(f"  {i}. {name} @ {display}")
    return "\n".join(lines)
