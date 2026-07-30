"""Structural query commands — sections, entrypoints, imports, exports,
symbols, and strings.

All commands follow the standard JSON envelope pattern and return paginated
results with cursor-based pagination. Cursors are scoped to command + project
+ filters + sort.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from typing import Any
from uuid import UUID, uuid4

from binary_analysis.cli.helpers import (
    clamp_page_size,
    make_warning,
)
from binary_analysis.domain.errors import (
    BackendFailureError,
    BinaryAnalysisError,
    BinaryNotFoundError,
    InvalidArgsError,
    ProjectNotFoundError,
)
from binary_analysis.projects.manifest import load_manifest
from binary_analysis.projects.workspace import (
    get_project_path,
    list_workspaces,
    workspace_exists,
)

# ---------------------------------------------------------------------------
# Project path resolution (shared with binary_ops)
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
# Cursor helper — scoped to command + project + filters + sort
# ---------------------------------------------------------------------------


def _encode_cursor(data: dict[str, Any]) -> str:
    """Encode a cursor dict as a base64-encoded JSON string."""
    json_bytes = json.dumps(data, sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(json_bytes).decode("ascii")


def _decode_cursor(cursor_str: str) -> dict[str, Any]:
    """Decode a base64-encoded cursor string back to a dict.

    Raises InvalidArgsError if the cursor is malformed.
    """
    try:
        json_bytes = base64.urlsafe_b64decode(cursor_str.encode("ascii"))
        result: dict[str, Any] = json.loads(json_bytes)
        return result
    except Exception:
        raise InvalidArgsError(
            "Invalid cursor value. Cursors are scoped to command, project, "
            "filters, and sort. Use a cursor from a matching query."
        ) from None


def _make_cursor(
    command: str,
    project_id: str,
    offset: int,
    filters: dict[str, Any] | None = None,
    sort_key: str | None = None,
) -> str:
    """Build a scoped pagination cursor.

    The cursor encodes the command, project, filters hash, sort key, and
    offset so that cursors from different queries are rejected.
    """
    filters_hash = hashlib.md5(
        json.dumps(filters or {}, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return _encode_cursor(
        {
            "c": command,
            "p": project_id,
            "fh": filters_hash,
            "s": sort_key,
            "o": offset,
        }
    )


def _validate_cursor_scope(
    cursor_data: dict[str, Any],
    command: str,
    project_id: str,
    filters: dict[str, Any] | None = None,
    sort_key: str | None = None,
) -> int:
    """Validate a cursor matches the current query scope and return offset.

    Raises InvalidArgsError if the cursor is for a different command,
    project, filter set, or sort.
    """
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
    """Register structural query subcommands."""
    # -- Sections --
    sections_parser = subparsers.add_parser(
        "sections", help="List canonical sections in the binary."
    )
    sections_parser.add_argument("--project", required=True, help="Project name or UUID.")
    sections_parser.add_argument(
        "--cursor", default=None, help="Pagination cursor from previous response (next_cursor)."
    )
    sections_parser.add_argument("--sort", default="address", help="Sort field (default: address).")

    # -- Entrypoints --
    entrypoints_parser = subparsers.add_parser(
        "entrypoints", help="List entry points with confidence scoring."
    )
    entrypoints_parser.add_argument("--project", required=True, help="Project name or UUID.")
    entrypoints_parser.add_argument(
        "--cursor", default=None, help="Pagination cursor from previous response (next_cursor)."
    )

    # -- Imports --
    imports_parser = subparsers.add_parser(
        "imports", help="List imported symbols with resolution status."
    )
    imports_parser.add_argument("--project", required=True, help="Project name or UUID.")
    imports_parser.add_argument(
        "--cursor", default=None, help="Pagination cursor from previous response (next_cursor)."
    )

    # -- Exports --
    exports_parser = subparsers.add_parser("exports", help="List exported symbols.")
    exports_parser.add_argument("--project", required=True, help="Project name or UUID.")
    exports_parser.add_argument(
        "--cursor", default=None, help="Pagination cursor from previous response (next_cursor)."
    )

    # -- Symbols --
    symbols_parser = subparsers.add_parser("symbols", help="List symbols with source and scope.")
    symbols_parser.add_argument("--project", required=True, help="Project name or UUID.")
    symbols_parser.add_argument(
        "--cursor", default=None, help="Pagination cursor from previous response (next_cursor)."
    )

    # -- Strings --
    strings_parser = subparsers.add_parser(
        "strings", help="List decoded strings with encoding, address, and length."
    )
    strings_parser.add_argument("--project", required=True, help="Project name or UUID.")
    strings_parser.add_argument(
        "--min-length",
        type=int,
        default=4,
        help="Minimum string length to return (default: 4).",
    )
    strings_parser.add_argument(
        "--contains",
        default=None,
        help="Case-sensitive substring filter.",
    )
    strings_parser.add_argument(
        "--encoding",
        default=None,
        choices=["ASCII", "UTF-8", "UTF-16"],
        help="Filter by string encoding.",
    )
    strings_parser.add_argument(
        "--cursor", default=None, help="Pagination cursor from previous response (next_cursor)."
    )


# ---------------------------------------------------------------------------
# Shared helpers for structural commands
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

    # Map the binary to the appropriate fixture based on its format.
    # This is needed so the adapter knows which fixture to use for this binary.
    binary_fmt = current_binary.get("format", "").lower()
    fixture_name = "pe-default"
    if "elf" in binary_fmt:
        fixture_name = "elf-default"
    elif "mach" in binary_fmt:
        fixture_name = "macho-default"

    adapter.register_binary(binary_entity, fixture_name)

    project_info = {
        "id": manifest.get("id", ""),
        "name": manifest.get("name", ""),
        "state": manifest.get("state", ""),
    }

    return adapter, binary_entity, project_info


def _entity_to_dict(entity: Any) -> dict[str, Any]:
    """Convert a domain entity to a JSON-serializable dict.

    Handles addresses (Address -> dict), UUIDs (UUID -> str),
    enums (Enum -> str), and None values.
    """
    from dataclasses import fields, is_dataclass

    if not is_dataclass(entity):
        if isinstance(entity, dict):
            return entity
        return {"value": str(entity)}

    result: dict[str, Any] = {}
    for f in fields(entity):
        value = getattr(entity, f.name)

        # Skip binary_id — internal linking field, not part of canonical output
        if f.name == "binary_id":
            continue
        # Skip content_hash for sections unless present
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


def _build_structural_result(
    items: list[dict[str, Any]],
    total: int,
    offset: int,
    limit: int,
    command: str,
    project_id: str,
    filters: dict[str, Any] | None = None,
    sort_key: str | None = None,
    applied_filters: list[dict[str, Any]] | None = None,
    diagnostics_extra: list[dict[str, Any]] | None = None,
    warnings_extra: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a paginated structural query result.

    The response uses next_cursor (not next_page_token) as per the
    validation contract naming convention.
    """
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

    data: dict[str, Any] = {
        "items": items,
        "total": total,
        "has_more": has_more,
        "next_cursor": next_cursor,
    }

    if applied_filters:
        data["applied_filters"] = applied_filters

    result: dict[str, Any] = {
        "success": True,
        "partial": False,
        "warnings": list(warnings_extra or []),
        "diagnostics": list(diagnostics_extra or []),
        "data": data,
    }

    return result


# ---------------------------------------------------------------------------
# Command execution
# ---------------------------------------------------------------------------


def execute_sections(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'sections' command.

    Returns canonical section objects with pagination.
    """
    project_name = args.project
    limit, clamp_warning = clamp_page_size(getattr(args, "limit", None))
    cursor_str: str | None = getattr(args, "cursor", None)
    sort_key: str = getattr(args, "sort", "address")
    command = "sections"

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)
    project_id = manifest.get("id", "")
    project_state = manifest.get("state", "")

    adapter, binary_entity, __ = _get_adapter_and_binary(project_path, manifest)

    # Get all sections
    try:
        sections = adapter.get_sections(binary_entity)
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(f"Failed to retrieve sections: {e}", original_error=str(e)) from e

    # Convert to dicts and sort
    items = [_entity_to_dict(s) for s in sections]

    # Sort by address offset
    if sort_key == "address":
        items.sort(
            key=lambda x: int((x.get("address") or {}).get("offset", "0x0").lstrip("0x") or "0", 16)
        )

    total = len(items)
    offset = 0

    # Decode cursor if present
    if cursor_str:
        cursor_data = _decode_cursor(cursor_str)
        offset = _validate_cursor_scope(
            cursor_data,
            command,
            project_id,
            filters=None,
            sort_key=sort_key,
        )

    # Apply pagination
    page_items = items[offset : offset + limit]

    # Add info diagnostics for unanalyzed projects
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

    return _build_structural_result(
        items=page_items,
        total=total,
        offset=offset,
        limit=limit,
        command=command,
        project_id=project_id,
        sort_key=sort_key,
        diagnostics_extra=diagnostics,
        warnings_extra=(
            [make_warning(clamp_warning, severity="WARNING", category="pagination")]
            if clamp_warning
            else None
        ),
    )


def execute_entrypoints(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'entrypoints' command.

    Returns entry point objects with kind and confidence.
    """
    project_name = args.project
    limit, clamp_warning = clamp_page_size(getattr(args, "limit", None))
    cursor_str: str | None = getattr(args, "cursor", None)
    command = "entrypoints"

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)
    project_id = manifest.get("id", "")
    project_state = manifest.get("state", "")

    adapter, binary_entity, __ = _get_adapter_and_binary(project_path, manifest)

    try:
        entrypoints = adapter.get_entrypoints(binary_entity)
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to retrieve entrypoints: {e}", original_error=str(e)
        ) from e

    items = [_entity_to_dict(ep) for ep in entrypoints]
    items.sort(
        key=lambda x: int((x.get("address") or {}).get("offset", "0x0").lstrip("0x") or "0", 16)
    )

    total = len(items)
    offset = 0

    if cursor_str:
        cursor_data = _decode_cursor(cursor_str)
        offset = _validate_cursor_scope(
            cursor_data,
            command,
            project_id,
            filters=None,
            sort_key=None,
        )

    page_items = items[offset : offset + limit]

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

    return _build_structural_result(
        items=page_items,
        total=total,
        offset=offset,
        limit=limit,
        command=command,
        project_id=project_id,
        diagnostics_extra=diagnostics,
        warnings_extra=(
            [make_warning(clamp_warning, severity="WARNING", category="pagination")]
            if clamp_warning
            else None
        ),
    )


def execute_imports(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'imports' command.

    Returns imported symbols with module, symbol, address, resolution, ordinal.
    """
    project_name = args.project
    limit, clamp_warning = clamp_page_size(getattr(args, "limit", None))
    cursor_str: str | None = getattr(args, "cursor", None)
    command = "imports"

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)
    project_id = manifest.get("id", "")
    project_state = manifest.get("state", "")

    adapter, binary_entity, __ = _get_adapter_and_binary(project_path, manifest)

    try:
        imports = adapter.get_imports(binary_entity)
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(f"Failed to retrieve imports: {e}", original_error=str(e)) from e

    items = [_entity_to_dict(imp) for imp in imports]
    items.sort(
        key=lambda x: int((x.get("address") or {}).get("offset", "0x0").lstrip("0x") or "0", 16)
    )

    total = len(items)
    offset = 0

    if cursor_str:
        cursor_data = _decode_cursor(cursor_str)
        offset = _validate_cursor_scope(
            cursor_data,
            command,
            project_id,
            filters=None,
            sort_key=None,
        )

    page_items = items[offset : offset + limit]

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

    return _build_structural_result(
        items=page_items,
        total=total,
        offset=offset,
        limit=limit,
        command=command,
        project_id=project_id,
        diagnostics_extra=diagnostics,
        warnings_extra=(
            [make_warning(clamp_warning, severity="WARNING", category="pagination")]
            if clamp_warning
            else None
        ),
    )


def execute_exports(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'exports' command.

    Returns exported symbols with name, address, ordinal, forwarder, kind.
    """
    project_name = args.project
    limit, clamp_warning = clamp_page_size(getattr(args, "limit", None))
    cursor_str: str | None = getattr(args, "cursor", None)
    command = "exports"

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)
    project_id = manifest.get("id", "")
    project_state = manifest.get("state", "")

    adapter, binary_entity, __ = _get_adapter_and_binary(project_path, manifest)

    try:
        exports = adapter.get_exports(binary_entity)
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(f"Failed to retrieve exports: {e}", original_error=str(e)) from e

    items = [_entity_to_dict(exp) for exp in exports]
    items.sort(
        key=lambda x: int((x.get("address") or {}).get("offset", "0x0").lstrip("0x") or "0", 16)
    )

    total = len(items)
    offset = 0

    if cursor_str:
        cursor_data = _decode_cursor(cursor_str)
        offset = _validate_cursor_scope(
            cursor_data,
            command,
            project_id,
            filters=None,
            sort_key=None,
        )

    page_items = items[offset : offset + limit]

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

    return _build_structural_result(
        items=page_items,
        total=total,
        offset=offset,
        limit=limit,
        command=command,
        project_id=project_id,
        diagnostics_extra=diagnostics,
        warnings_extra=(
            [make_warning(clamp_warning, severity="WARNING", category="pagination")]
            if clamp_warning
            else None
        ),
    )


def execute_symbols(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'symbols' command.

    Returns symbols with name, address, source, scope.
    IMPORTED symbols are cross-linked to imports table.
    """
    project_name = args.project
    limit, clamp_warning = clamp_page_size(getattr(args, "limit", None))
    cursor_str: str | None = getattr(args, "cursor", None)
    command = "symbols"

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)
    project_id = manifest.get("id", "")
    project_state = manifest.get("state", "")

    adapter, binary_entity, __ = _get_adapter_and_binary(project_path, manifest)

    # Get both symbols and imports for cross-linking
    try:
        symbols = adapter.get_symbols(binary_entity)
        imports = adapter.get_imports(binary_entity)
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(f"Failed to retrieve symbols: {e}", original_error=str(e)) from e

    # Build import lookup by address for cross-linking
    import_by_addr: dict[str, dict[str, Any]] = {}
    for imp in imports:
        if imp.address is not None:
            addr_key = imp.address.offset
            import_by_addr[addr_key] = {
                "module": imp.module,
                "symbol": imp.symbol,
                "resolution": str(imp.resolution.value),
            }

    # Convert symbols to dicts with cross-linking
    items = []
    for sym in symbols:
        sym_dict = _entity_to_dict(sym)
        # Cross-link IMPORTED symbols to imports table
        if str(sym.source.value) == "IMPORTED" and sym.address is not None:
            imp_info = import_by_addr.get(sym.address.offset)
            if imp_info:
                sym_dict["import"] = imp_info
            else:
                # Try matching by name
                for imp in imports:
                    if imp.symbol == sym.name:
                        sym_dict["import"] = {
                            "module": imp.module,
                            "symbol": imp.symbol,
                            "resolution": str(imp.resolution.value),
                        }
                        break
        items.append(sym_dict)

    items.sort(
        key=lambda x: int((x.get("address") or {}).get("offset", "0x0").lstrip("0x") or "0", 16)
    )

    total = len(items)
    offset = 0

    if cursor_str:
        cursor_data = _decode_cursor(cursor_str)
        offset = _validate_cursor_scope(
            cursor_data,
            command,
            project_id,
            filters=None,
            sort_key=None,
        )

    page_items = items[offset : offset + limit]

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

    return _build_structural_result(
        items=page_items,
        total=total,
        offset=offset,
        limit=limit,
        command=command,
        project_id=project_id,
        diagnostics_extra=diagnostics,
        warnings_extra=(
            [make_warning(clamp_warning, severity="WARNING", category="pagination")]
            if clamp_warning
            else None
        ),
    )


def execute_strings(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'strings' command.

    Returns decoded strings with text, encoding, address, length.
    Supports --min-length, --contains, --encoding filters.
    Combined filters work together and are reported in applied_filters.
    """
    project_name = args.project
    limit, clamp_warning = clamp_page_size(getattr(args, "limit", None))
    cursor_str: str | None = getattr(args, "cursor", None)
    min_length: int = getattr(args, "min_length", 4)
    contains: str | None = getattr(args, "contains", None)
    encoding_filter: str | None = getattr(args, "encoding", None)
    command = "strings"

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)
    project_id = manifest.get("id", "")
    project_state = manifest.get("state", "")

    adapter, binary_entity, __ = _get_adapter_and_binary(project_path, manifest)

    # Build filters dict for cursor scoping
    filters: dict[str, Any] = {}
    if min_length != 4:  # Only track non-default
        filters["min_length"] = min_length
    if contains is not None:
        filters["contains"] = contains
    if encoding_filter is not None:
        filters["encoding"] = encoding_filter

    # Build applied_filters for response
    applied_filters: list[dict[str, Any]] = []
    if min_length != 4 or min_length == 4:
        applied_filters.append({"filter": "min_length", "value": min_length})
    if contains is not None:
        applied_filters.append({"filter": "contains", "value": contains})
    if encoding_filter is not None:
        applied_filters.append({"filter": "encoding", "value": encoding_filter})

    try:
        strings = adapter.get_strings(
            binary_entity,
            min_length=min_length,
            contains=contains,
            encoding_filter=encoding_filter,
        )
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(f"Failed to retrieve strings: {e}", original_error=str(e)) from e

    items = [_entity_to_dict(s) for s in strings]
    # Sort by address for deterministic pagination
    items.sort(
        key=lambda x: int((x.get("address") or {}).get("offset", "0x0").lstrip("0x") or "0", 16)
    )

    total = len(items)
    offset = 0

    if cursor_str:
        cursor_data = _decode_cursor(cursor_str)
        offset = _validate_cursor_scope(
            cursor_data,
            command,
            project_id,
            filters=filters,
            sort_key=None,
        )

    page_items = items[offset : offset + limit]

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

    return _build_structural_result(
        items=page_items,
        total=total,
        offset=offset,
        limit=limit,
        command=command,
        project_id=project_id,
        filters=filters if filters else None,
        applied_filters=applied_filters,
        diagnostics_extra=diagnostics,
        warnings_extra=(
            [make_warning(clamp_warning, severity="WARNING", category="pagination")]
            if clamp_warning
            else None
        ),
    )
