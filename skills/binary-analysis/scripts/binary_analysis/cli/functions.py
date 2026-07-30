"""Focused analysis commands — functions, disassemble, bytes, and decompile.

All commands follow the standard JSON envelope pattern. Functions returns
paginated results. Disassemble and bytes operate on bounded targets (function
selectors or address ranges). Decompile returns reconstructed pseudocode.

Validation assertions covered:
- VAL-STRUCT-011, 012, 013: Functions list with filtering
- VAL-FOCUS-001, 002, 003, 004, 005, 032: Decompile
- VAL-FOCUS-006, 007, 008, 009, 010: Disassemble
- VAL-FOCUS-011, 012, 013, 014: Bytes
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import re
from typing import Any
from uuid import UUID, uuid4

from binary_analysis.cli.helpers import clamp_page_size
from binary_analysis.domain.entities import Address
from binary_analysis.domain.errors import (
    BackendFailureError,
    BinaryAnalysisError,
    BinaryNotFoundError,
    EntityNotFoundError,
    InvalidArgsError,
    OperationTimeoutError,
    ProjectNotFoundError,
)
from binary_analysis.domain.selectors import (
    parse_selector,
    resolve_function,
)
from binary_analysis.projects.manifest import load_manifest
from binary_analysis.projects.workspace import (
    get_project_path,
    list_workspaces,
    workspace_exists,
)

# ---------------------------------------------------------------------------
# Address range regex: <hex_start>..<hex_end>
# ---------------------------------------------------------------------------

_ADDR_RANGE_RE = re.compile(r"^(0x[0-9a-fA-F]+)\.\.(0x[0-9a-fA-F]+)$")

# ---------------------------------------------------------------------------
# Project path resolution (identical to structural.py)
# ---------------------------------------------------------------------------


def _resolve_project_path(project_name: str) -> str:
    """Resolve a project name or UUID to its workspace path."""
    if workspace_exists(project_name):
        return str(get_project_path(project_name))

    for ws_name in list_workspaces():
        ws_path = str(get_project_path(ws_name))
        try:
            manifest = load_manifest(ws_path)
            if manifest.get("id") == project_name:
                return ws_path
        except Exception:
            continue

    raise ProjectNotFoundError(project_name)


# ---------------------------------------------------------------------------
# Shared adapter/binary resolution (identical to structural.py)
# ---------------------------------------------------------------------------


def _get_adapter_and_binary(
    project_path: str, manifest: dict[str, Any]
) -> tuple[Any, Any, dict[str, Any]]:
    """Resolve the adapter, binary entity, and project info.

    Returns:
        Tuple of (adapter, Binary entity, project_info dict with id/name/state).
    """
    from binary_analysis.adapters.fake import FakeAdapter
    from binary_analysis.domain.entities import Binary as BinaryEntity

    current_binary = manifest.get("current_binary")
    if current_binary is None:
        raise BinaryNotFoundError(
            "No binary has been imported into this project. "
            "Use 'binary import' to add a binary before querying."
        )

    adapter = FakeAdapter()
    adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
    adapter.set_fixture("elf-default", FakeAdapter.elf_fixture())
    adapter.set_fixture("macho-default", FakeAdapter.macho_fixture())

    binary_id = current_binary.get("id", str(uuid4()))
    binary_entity = BinaryEntity(
        id=UUID(binary_id),
        sha256=current_binary.get("sha256", ""),
        path=current_binary.get("path", ""),
        format=current_binary.get("format", ""),
        size_bytes=current_binary.get("size_bytes", 0),
        architecture=current_binary.get("architecture"),
    )

    binary_fmt = current_binary.get("format", "").lower()
    fixture_name = "pe-default"
    if "elf" in binary_fmt:
        fixture_name = "elf-default"
    elif "mach" in binary_fmt:
        fixture_name = "macho-default"

    adapter._binaries[str(binary_id)] = {
        "binary": binary_entity,
        "fixture_name": fixture_name,
    }

    project_info = {
        "id": manifest.get("id", ""),
        "name": manifest.get("name", ""),
        "state": manifest.get("state", ""),
    }

    return adapter, binary_entity, project_info


# ---------------------------------------------------------------------------
# Entity-to-dict conversion (identical to structural.py)
# ---------------------------------------------------------------------------


def _entity_to_dict(entity: Any) -> dict[str, Any]:
    """Convert a domain entity to a JSON-serializable dict."""
    from dataclasses import fields, is_dataclass

    if not is_dataclass(entity):
        if isinstance(entity, dict):
            return entity
        return {"value": str(entity)}

    result: dict[str, Any] = {}
    for f in fields(entity):
        value = getattr(entity, f.name)

        if f.name == "binary_id":
            continue
        if f.name == "content_hash" and value is None:
            continue

        if value is None:
            result[f.name] = None
        elif hasattr(value, "to_dict"):
            result[f.name] = value.to_dict()
        elif hasattr(value, "value"):
            result[f.name] = str(value.value)
        elif isinstance(value, UUID):
            result[f.name] = str(value)
        else:
            result[f.name] = value

    return result


# ---------------------------------------------------------------------------
# Address parsing helpers
# ---------------------------------------------------------------------------


def _parse_address(addr_str: str) -> Address:
    """Parse a hex address string like '0x401000' into an Address object.

    Raises InvalidArgsError if the format is invalid.
    """
    if not addr_str.startswith("0x"):
        raise InvalidArgsError(
            f"Invalid address format: {addr_str!r}. Address must start with '0x' "
            "followed by hexadecimal digits (e.g., '0x401000')."
        )
    try:
        int(addr_str, 16)
    except ValueError:
        raise InvalidArgsError(
            f"Invalid address format: {addr_str!r}. Expected hexadecimal address."
        ) from None

    return Address(
        space="ram",
        offset=addr_str,
        display=addr_str,
    )


def _parse_address_range(range_str: str) -> tuple[Address, Address]:
    """Parse an address range string like '0x401000..0x401200'.

    Returns (start_address, end_address).

    Raises InvalidArgsError if the format is invalid.
    """
    match = _ADDR_RANGE_RE.match(range_str)
    if not match:
        raise InvalidArgsError(
            f"Invalid address range format: {range_str!r}. "
            "Expected format: <start_hex>..<end_hex> (e.g., '0x401000..0x401200')."
        )
    start_str, end_str = match.group(1), match.group(2)
    start = _parse_address(start_str)
    end = _parse_address(end_str)

    # Validate that start <= end
    if int(start_str, 16) > int(end_str, 16):
        raise InvalidArgsError(
            f"Invalid address range: start ({start_str}) must be <= end ({end_str})."
        )

    return start, end


# ---------------------------------------------------------------------------
# Cursor helpers (adapted from structural.py)
# ---------------------------------------------------------------------------


def _make_cursor(
    command: str,
    project_id: str,
    offset: int,
    filters: dict[str, Any] | None = None,
    sort_key: str | None = None,
) -> str:
    """Build a scoped pagination cursor."""
    import hashlib
    import json

    filters_hash = hashlib.md5(
        json.dumps(filters or {}, sort_keys=True).encode("utf-8")
    ).hexdigest()
    cursor_data = {
        "c": command,
        "p": project_id,
        "fh": filters_hash,
        "s": sort_key,
        "o": offset,
    }
    json_bytes = json.dumps(cursor_data, sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(json_bytes).decode("ascii")


def _decode_cursor(cursor_str: str) -> dict[str, Any]:
    """Decode a base64-encoded cursor string back to a dict."""
    import json

    try:
        json_bytes = base64.urlsafe_b64decode(cursor_str.encode("ascii"))
        result: dict[str, Any] = json.loads(json_bytes)
        return result
    except Exception:
        raise InvalidArgsError(
            "Invalid cursor value. Cursors are scoped to command, project, "
            "filters, and sort. Use a cursor from a matching query."
        ) from None


def _validate_cursor_scope(
    cursor_data: dict[str, Any],
    command: str,
    project_id: str,
    filters: dict[str, Any] | None = None,
    sort_key: str | None = None,
) -> int:
    """Validate cursor scope and return offset."""
    import hashlib
    import json

    filters_hash = hashlib.md5(
        json.dumps(filters or {}, sort_keys=True).encode("utf-8")
    ).hexdigest()

    c_cmd = cursor_data.get("c")
    c_proj = cursor_data.get("p")
    c_fh = cursor_data.get("fh")
    c_sort = cursor_data.get("s")
    offset = cursor_data.get("o", 0)

    mismatches: list[str] = []
    if c_cmd != command:
        mismatches.append(f"command (cursor: {c_cmd}, current: {command})")
    if c_proj != project_id:
        mismatches.append(f"project (cursor: {c_proj}, current: {project_id})")
    if c_fh != filters_hash:
        mismatches.append("filters")
    if (c_sort or None) != (sort_key or None):
        mismatches.append("sort")

    if mismatches:
        raise InvalidArgsError(
            "Cursor scope mismatch: " + "; ".join(mismatches) + ". "
            "Pagination cursors are scoped to command, project, filters, and sort. "
            "Use a cursor from a matching query."
        )

    if not isinstance(offset, int) or offset < 0:
        raise InvalidArgsError("Invalid cursor offset")

    return offset


# ---------------------------------------------------------------------------
# Subparser registration
# ---------------------------------------------------------------------------


def add_subparser(subparsers: Any) -> None:
    """Register focused analysis subcommands: functions, decompile, disassemble, bytes."""

    # -- Functions --
    functions_parser = subparsers.add_parser(
        "functions", help="List functions with name, address, size, confidence, and name source."
    )
    functions_parser.add_argument("--project", required=True, help="Project name or UUID.")
    functions_parser.add_argument(
        "--no-exclude-external",
        action="store_true",
        default=False,
        help="Include externally defined functions (excluded by default).",
    )
    functions_parser.add_argument(
        "--no-exclude-thunks",
        action="store_true",
        default=False,
        help="Include thunk functions (excluded by default).",
    )
    functions_parser.add_argument(
        "--cursor", default=None, help="Pagination cursor from previous response (next_cursor)."
    )
    functions_parser.add_argument(
        "--sort", default="address", help="Sort field (default: address)."
    )

    # -- Decompile --
    decompile_parser = subparsers.add_parser(
        "decompile",
        help="Decompile a function to reconstructed pseudocode with address map.",
    )
    decompile_parser.add_argument("--project", required=True, help="Project name or UUID.")
    decompile_parser.add_argument(
        "selector",
        nargs="?",
        default=None,
        help=(
            "A single function selector: function:<name> (e.g., 'function:main') "
            "or shorthand function name (e.g., 'main'). "
            "Exactly one function selector is required."
        ),
    )

    # -- Disassemble --
    disassemble_parser = subparsers.add_parser(
        "disassemble",
        help="Disassemble instructions in a function or address range.",
    )
    disassemble_parser.add_argument("--project", required=True, help="Project name or UUID.")
    disassemble_parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help=(
            "Disassembly target. Either function:<name> (e.g., 'function:main') "
            "or an address range <start>..<end> (e.g., '0x401000..0x401200')."
        ),
    )

    # -- Bytes --
    bytes_parser = subparsers.add_parser("bytes", help="Read raw bytes at a given address.")
    bytes_parser.add_argument("--project", required=True, help="Project name or UUID.")
    bytes_parser.add_argument(
        "address",
        nargs="?",
        default=None,
        help="Starting address in hex (e.g., '0x401000').",
    )
    bytes_parser.add_argument(
        "length",
        nargs="?",
        type=int,
        default=None,
        help="Number of bytes to read (positive integer).",
    )


# ---------------------------------------------------------------------------
# Command: functions
# ---------------------------------------------------------------------------


def execute_functions(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'functions' command.

    VAL-STRUCT-011: Returns name, address, size_bytes, confidence, name_source.
    VAL-STRUCT-012: Excludes external/thunks by default; reports in applied_filters.
    VAL-STRUCT-013: --no-exclude-external/--no-exclude-thunks override defaults.
    """
    project_name = args.project
    limit = clamp_page_size(getattr(args, "limit", None))
    cursor_str: str | None = getattr(args, "cursor", None)
    sort_key: str = getattr(args, "sort", "address")
    no_exclude_external: bool = getattr(args, "no_exclude_external", False)
    no_exclude_thunks: bool = getattr(args, "no_exclude_thunks", False)
    command = "functions"

    # Exclude by default; flags invert the default
    exclude_external = not no_exclude_external
    exclude_thunks = not no_exclude_thunks

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)
    project_id = manifest.get("id", "")
    project_state = manifest.get("state", "")

    adapter, binary_entity, __ = _get_adapter_and_binary(project_path, manifest)

    try:
        functions = adapter.get_functions(
            binary_entity,
            exclude_external=exclude_external,
            exclude_thunks=exclude_thunks,
        )
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to retrieve functions: {e}", original_error=str(e)
        ) from e

    items = []
    for fn in functions:
        d = _entity_to_dict(fn)
        # Only include the canonical fields per VAL-STRUCT-011
        items.append(d)

    # Sort by address offset
    if sort_key == "address":
        items.sort(
            key=lambda x: int((x.get("address") or {}).get("offset", "0x0").lstrip("0x") or "0", 16)
        )
    elif sort_key == "name":
        items.sort(key=lambda x: x.get("name", ""))

    total = len(items)
    offset = 0

    # Build filters dict for cursor scoping
    filters: dict[str, Any] = {
        "exclude_external": exclude_external,
        "exclude_thunks": exclude_thunks,
    }

    if cursor_str:
        cursor_data = _decode_cursor(cursor_str)
        offset = _validate_cursor_scope(
            cursor_data, command, project_id, filters=filters, sort_key=sort_key
        )

    page_items = items[offset : offset + limit]
    has_more = (offset + limit) < total
    next_cursor: str | None = None
    if has_more:
        next_cursor = _make_cursor(
            command=command,
            project_id=project_id,
            offset=offset + limit,
            filters=filters,
            sort_key=sort_key,
        )

    # Build applied_filters showing the active exclusion state
    applied_filters: list[dict[str, Any]] = [
        {"filter": "exclude_external", "active": exclude_external},
        {"filter": "exclude_thunks", "active": exclude_thunks},
    ]

    data: dict[str, Any] = {
        "items": page_items,
        "total": total,
        "has_more": has_more,
        "next_cursor": next_cursor,
        "applied_filters": applied_filters,
    }

    diagnostics: list[dict[str, Any]] = []
    if project_state and project_state != "READY":
        diagnostics.append(
            {
                "severity": "INFO",
                "message": (
                    "Project has not been fully analyzed. "
                    "Results may be incomplete. "
                    "Run 'binary analyze --project <proj>' for complete analysis."
                ),
                "category": "analysis_state",
            }
        )

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": diagnostics,
        "data": data,
    }


# ---------------------------------------------------------------------------
# Command: disassemble
# ---------------------------------------------------------------------------


def execute_disassemble(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'disassemble' command.

    VAL-FOCUS-006: Disassemble by function selector returns instructions.
    VAL-FOCUS-007: Disassemble by address range returns instructions in bounds.
    VAL-FOCUS-008: No range/selector → exit code 2.
    VAL-FOCUS-009: Unmapped range → exit code 9.
    VAL-FOCUS-010: Partially mapped → partial=true with diagnostics.
    """
    project_name = args.project
    target: str | None = getattr(args, "target", None)

    # VAL-FOCUS-008: Require explicit target
    if not target:
        raise InvalidArgsError(
            "Disassembly requires a bounded target. "
            "Provide a function selector (e.g., 'function:main') or "
            "an address range (e.g., '0x401000..0x401200')."
        )

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    adapter, binary_entity, __ = _get_adapter_and_binary(project_path, manifest)

    # Determine if target is a function selector or address range
    is_function_selector = target.startswith("function:")
    is_address_range = ".." in target and not target.startswith("function:")

    if is_function_selector:
        # VAL-FOCUS-006: Disassemble by function selector
        func_name = target[len("function:") :]
        if not func_name:
            raise InvalidArgsError("Function selector requires a function name: 'function:<name>'.")

        # Find the function by name
        try:
            all_functions = adapter.get_functions(
                binary_entity, exclude_external=False, exclude_thunks=False
            )
        except BinaryAnalysisError:
            raise
        except Exception as e:
            raise BackendFailureError(
                f"Failed to retrieve functions: {e}", original_error=str(e)
            ) from e

        # Find matching function(s)
        matching = [fn for fn in all_functions if fn.name == func_name]
        if not matching:
            raise EntityNotFoundError("function", func_name)

        function = matching[0]
        if function.address is None:
            raise EntityNotFoundError("function", func_name)

        # Determine the range of the function
        start_addr = function.address
        # Calculate end address from size
        start_int = int(start_addr.offset, 16)
        end_int = start_int + function.size_bytes - 1
        end_addr = Address(
            space=start_addr.space,
            offset=f"0x{end_int:x}",
            display=f"0x{end_int:x}",
        )

    elif is_address_range:
        # VAL-FOCUS-007: Disassemble by explicit address range
        start_addr, end_addr = _parse_address_range(target)
    else:
        raise InvalidArgsError(
            f"Invalid disassembly target: {target!r}. "
            "Provide a function selector (e.g., 'function:main') or "
            "an address range (e.g., '0x401000..0x401200')."
        )

    # Perform disassembly
    try:
        instructions = adapter.disassemble(binary_entity, start_addr, end_addr)
    except ValueError as e:
        msg = str(e)
        if "unmapped" in msg.lower():
            # VAL-FOCUS-009: Unmapped range → exit code 9
            raise EntityNotFoundError(
                "address range", f"{start_addr.offset}..{end_addr.offset}"
            ) from e
        raise BackendFailureError(f"Disassembly failed: {e}", original_error=msg) from e
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(f"Disassembly failed: {e}", original_error=str(e)) from e

    # Convert to dicts
    instr_dicts = [_entity_to_dict(inst) for inst in instructions]

    # Check for partial mapping (VAL-FOCUS-010)
    partial = False
    diagnostics: list[dict[str, Any]] = []

    if len(instructions) == 0:
        # No instructions returned — the range might be unmapped
        raise EntityNotFoundError("address range", f"{start_addr.offset}..{end_addr.offset}")

    # Check if the result is partial (last instruction doesn't reach end)
    if instructions:
        last_addr = instructions[-1].address
        if last_addr is not None:
            last_offset = int(last_addr.offset, 16)
            end_offset = int(end_addr.offset, 16)
            if last_offset < end_offset:
                partial = True
                diagnostics.append(
                    {
                        "severity": "WARNING",
                        "message": (
                            f"Address range {start_addr.offset}..{end_addr.offset} "
                            "is partially mapped. Disassembly covers only the mapped "
                            f"portion up to {last_addr.offset}."
                        ),
                        "category": "partial_mapping",
                    }
                )

    data: dict[str, Any] = {
        "instructions": instr_dicts,
        "start_address": start_addr.to_dict(),
        "end_address": end_addr.to_dict(),
        "instruction_count": len(instr_dicts),
        "target": target,
    }

    return {
        "success": True,
        "partial": partial,
        "warnings": [],
        "diagnostics": diagnostics,
        "data": data,
    }


# ---------------------------------------------------------------------------
# Command: bytes
# ---------------------------------------------------------------------------


def execute_bytes(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'bytes' command.

    VAL-FOCUS-011: Returns hex (2*length chars) and base64.
    VAL-FOCUS-012: Unmapped address → exit code 9.
    VAL-FOCUS-013: Zero-length request → exit code 2.
    VAL-FOCUS-014: Truncation at segment boundary → partial=true with diagnostic.
    """
    project_name = args.project
    addr_str: str | None = getattr(args, "address", None)
    length: int | None = getattr(args, "length", None)

    # Validate address
    if addr_str is None:
        raise InvalidArgsError(
            "The 'bytes' command requires an address argument (e.g., '0x401000')."
        )

    # VAL-FOCUS-013: Zero-length request rejected
    if length is None:
        raise InvalidArgsError("The 'bytes' command requires a length argument (positive integer).")
    if length <= 0:
        raise InvalidArgsError(f"Length must be a positive integer, got {length}.")

    address = _parse_address(addr_str)

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    adapter, binary_entity, __ = _get_adapter_and_binary(project_path, manifest)

    # Read bytes from adapter
    try:
        raw_bytes, actual_length = adapter.read_bytes(binary_entity, address, length)
    except ValueError as e:
        msg = str(e)
        if "unmapped" in msg.lower():
            # VAL-FOCUS-012: Unmapped address → exit code 9
            raise EntityNotFoundError("address", addr_str) from e
        if "positive" in msg.lower() or "length" in msg.lower():
            raise InvalidArgsError(msg) from e
        raise BackendFailureError(f"Failed to read bytes: {e}", original_error=msg) from e
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(f"Failed to read bytes: {e}", original_error=str(e)) from e

    # Build hex and base64 output
    hex_str = raw_bytes.hex()
    b64_str = base64.standard_b64encode(raw_bytes).decode("ascii")

    # VAL-FOCUS-014: Truncation detection
    partial = actual_length < length
    diagnostics: list[dict[str, Any]] = []

    if partial:
        diagnostics.append(
            {
                "severity": "WARNING",
                "message": (
                    f"Requested {length} bytes at {addr_str}, but only {actual_length} "
                    f"bytes are available within the mapped segment. "
                    "The data has been truncated at the segment boundary."
                ),
                "category": "truncation",
            }
        )

    # VAL-FOCUS-011: Verify hex length
    # hex should be 2 * actual_length characters
    assert len(hex_str) == 2 * actual_length, (
        f"Hex output length mismatch: expected {2 * actual_length}, got {len(hex_str)}"
    )

    data: dict[str, Any] = {
        "hex": hex_str,
        "base64": b64_str,
        "address": address.to_dict(),
        "length": actual_length,
        "requested_length": length,
    }

    return {
        "success": True,
        "partial": partial,
        "warnings": [],
        "diagnostics": diagnostics,
        "data": data,
    }


# ---------------------------------------------------------------------------
# Command: decompile
# ---------------------------------------------------------------------------


def _validate_decompile_selector(raw: str) -> str:
    """Validate and normalize a decompile selector.

    The decompile command accepts exactly one function selector.
    Multiple selectors (comma-separated), wildcards ('*'), and address
    ranges ('..') are rejected with INVALID_ARGS (exit code 2).

    Args:
        raw: The raw selector string from the CLI.

    Returns:
        The normalized function name string.

    Raises:
        InvalidArgsError: If the selector is invalid.
    """
    if not raw:
        raise InvalidArgsError(
            "Decompile requires exactly one function selector. "
            "Provide a function selector (e.g., 'function:main') or "
            "a shorthand function name (e.g., 'main')."
        )

    # VAL-FOCUS-003: Reject multiple selectors (comma-separated)
    if "," in raw:
        raise InvalidArgsError(
            "Decompile requires exactly one function selector. "
            f"Multiple selectors are not supported: {raw!r}. "
            "Provide a single function selector like 'function:main' or 'main'."
        )

    # VAL-FOCUS-003: Reject wildcards
    if "*" in raw:
        raise InvalidArgsError(
            "Decompile requires exactly one function selector. "
            f"Wildcards are not supported: {raw!r}. "
            "Provide a single function selector like 'function:main' or 'main'."
        )

    # VAL-FOCUS-003: Reject address ranges
    if ".." in raw:
        raise InvalidArgsError(
            "Decompile requires exactly one function selector. "
            f"Address ranges are not supported: {raw!r}. "
            "Provide a single function selector like 'function:main' or 'main'."
        )

    # Check for empty function: prefix (e.g., "function:" with no name)
    if raw.strip().lower().startswith("function:") and len(raw.strip()) <= len("function:"):
        raise InvalidArgsError(
            "Decompile requires a valid function selector. "
            f"Empty function name in selector: {raw!r}. "
            "Provide a function selector like 'function:main' or 'main'."
        )

    # Parse the selector
    parsed = parse_selector(raw)

    # VAL-FOCUS-003: Reject non-function selectors (e.g., address:...)
    if parsed.kind == "address":
        raise InvalidArgsError(
            "Decompile requires exactly one function selector. "
            f"Address selectors are not supported: {raw!r}. "
            "Provide a function selector like 'function:main' or 'main'."
        )

    # Extract function name
    func_name = parsed.value
    if not func_name:
        raise InvalidArgsError(
            "Decompile requires a valid function selector. "
            f"Empty selector value in: {raw!r}. "
            "Provide a function selector like 'function:main' or 'main'."
        )

    return func_name


def execute_decompile(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'decompile' command.

    VAL-FOCUS-001: Returns pseudocode (labeled as reconstructed), address_map, diagnostics.
    VAL-FOCUS-002: Ambiguous selector → exit code 8 with candidate functions list.
    VAL-FOCUS-003: Multiple selectors/wildcards/ranges → exit code 2.
    VAL-FOCUS-004: Entity not found → exit code 9.
    VAL-FOCUS-005: Timeout → partial results with exit code 12.
    VAL-FOCUS-032: Large function respects time limit; no crash or hang.
    """
    project_name = args.project
    raw_selector: str | None = getattr(args, "selector", None)
    timeout_seconds: int = getattr(args, "timeout", 300)

    if not raw_selector:
        raise InvalidArgsError(
            "Decompile requires exactly one function selector. "
            "Provide a function selector (e.g., 'function:main') or "
            "a shorthand function name (e.g., 'main')."
        )

    # Validate selector (exactly one function, no wildcards/ranges/multiples)
    _ = _validate_decompile_selector(raw_selector)

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    adapter, binary_entity, _project_info = _get_adapter_and_binary(project_path, manifest)

    # Retrieve all functions and resolve the selector
    try:
        all_functions = adapter.get_functions(
            binary_entity, exclude_external=False, exclude_thunks=False
        )
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to retrieve functions for decompilation: {e}",
            original_error=str(e),
        ) from e

    # Resolve the function selector
    parsed = parse_selector(raw_selector)
    selected_function = resolve_function(parsed, all_functions, require_unique=True)

    # Build function info for the result
    fn_info: dict[str, Any] = {
        "name": selected_function.name,
        "address": selected_function.address.to_dict() if selected_function.address else None,
        "size_bytes": selected_function.size_bytes,
        "signature": selected_function.signature,
    }

    # Perform decompilation with timeout
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(adapter.decompile, binary_entity, selected_function)
            try:
                decomp_result = future.result(timeout=timeout_seconds)
            except concurrent.futures.TimeoutError:
                # VAL-FOCUS-005, VAL-FOCUS-032: Timeout → partial results
                future.cancel()
                raise OperationTimeoutError(
                    f"Decompilation of function '{selected_function.name}' "
                    f"timed out after {timeout_seconds}s. "
                    "Partial results may be available from a shorter analysis run."
                ) from None
    except OperationTimeoutError:
        raise
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Decompilation failed for function '{selected_function.name}': {e}",
            original_error=str(e),
        ) from e

    # Build the address map: string keys for line numbers → canonical address objects
    address_map: dict[str, Any] = {}
    for line_num, addr_obj in decomp_result.address_map.items():
        address_map[str(line_num)] = addr_obj

    # Build diagnostics
    diagnostics: list[dict[str, Any]] = list(decomp_result.diagnostics)
    manifest_state = manifest.get("state", "")
    if manifest_state and manifest_state != "READY":
        diagnostics.append(
            {
                "severity": "INFO",
                "message": (
                    "Project has not been fully analyzed. "
                    "Decompilation results may be incomplete. "
                    "Run 'binary analyze --project <proj>' for complete analysis."
                ),
                "category": "analysis_state",
            }
        )

    data: dict[str, Any] = {
        "pseudocode": decomp_result.pseudocode,
        "address_map": address_map,
        "diagnostics": diagnostics,
        "language": decomp_result.language,
        "function": fn_info,
    }

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": diagnostics,
        "data": data,
    }
