"""Search and trace commands for the binary analysis CLI.

Search returns paginated results with opaque cursor (not incrementing offset).
Trace finds bounded paths between --from and --to entities within disclosed
path count and depth limits.

Validation assertions covered:
- VAL-FOCUS-025, 026, 027: Search
- VAL-FOCUS-028, 029, 030: Trace
"""

from __future__ import annotations

import argparse
import base64
import json
from typing import Any
from uuid import UUID, uuid4

from binary_analysis.cli.helpers import (
    PAGE_SIZE_DEFAULT,
    PAGE_SIZE_MAX,
    build_paginated_response,
    clamp_page_size,
    make_diagnostic,
    make_warning,
)
from binary_analysis.domain.entities import Address
from binary_analysis.domain.errors import (
    BackendFailureError,
    BinaryAnalysisError,
    BinaryNotFoundError,
    EntityNotFoundError,
    InvalidArgsError,
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
# Search limits
# ---------------------------------------------------------------------------

DEFAULT_SEARCH_PAGE_SIZE = PAGE_SIZE_DEFAULT
MAX_SEARCH_PAGE_SIZE = PAGE_SIZE_MAX
MAX_SEARCH_RESULTS = 10000

# ---------------------------------------------------------------------------
# Trace limits
# ---------------------------------------------------------------------------

DEFAULT_MAX_PATHS = 10
DEFAULT_MAX_TRACE_DEPTH = 10
MAX_PATHS_LIMIT = 100
MAX_TRACE_DEPTH_LIMIT = 20

# ---------------------------------------------------------------------------
# Project path resolution
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
# Shared adapter/binary resolution
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

    adapter.register_binary(binary_entity, fixture_name)

    project_info = {
        "id": manifest.get("id", ""),
        "name": manifest.get("name", ""),
        "state": manifest.get("state", ""),
    }

    return adapter, binary_entity, project_info


# ---------------------------------------------------------------------------
# Address parsing
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


# ---------------------------------------------------------------------------
# Cursor encoding
# ---------------------------------------------------------------------------


def _encode_cursor(cursor_data: dict[str, Any]) -> str:
    """Encode pagination cursor data to an opaque string token."""
    payload = json.dumps(cursor_data, sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii")


def _decode_cursor(token: str) -> dict[str, Any]:
    """Decode an opaque cursor token back to cursor data.

    Raises InvalidArgsError if the token is malformed.
    """
    try:
        payload = base64.urlsafe_b64decode(token)
        result: Any = json.loads(payload)
        if not isinstance(result, dict):
            raise InvalidArgsError(
                f"Invalid cursor token: {token!r}. Cursor payload must be a JSON object."
            )
        return result
    except Exception:
        raise InvalidArgsError(
            f"Invalid cursor token: {token!r}. Cursors must be obtained from "
            "a previous search response's next_page_token field."
        ) from None


# ---------------------------------------------------------------------------
# Subparser registration
# ---------------------------------------------------------------------------


def add_subparser(subparsers: Any) -> None:
    """Register search and trace subcommands."""

    # -- Search --
    search_parser = subparsers.add_parser(
        "search",
        help="Search for entities (functions, strings, symbols) by name or pattern.",
    )
    search_parser.add_argument("--project", required=True, help="Project name or UUID.")
    search_parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Search query string (case-insensitive substring match).",
    )
    search_parser.add_argument(
        "--type",
        dest="search_type",
        default="function",
        choices=["function", "string", "symbol", "import", "export", "all"],
        help="Type of entity to search (default: function).",
    )
    search_parser.add_argument(
        "--page-token",
        dest="cursor",
        default=None,
        help="Opaque cursor token for pagination (from next_page_token in prior response).",
    )

    # -- Trace --
    trace_parser = subparsers.add_parser(
        "trace",
        help="Find call paths between two entities.",
    )
    trace_parser.add_argument("--project", required=True, help="Project name or UUID.")
    trace_parser.add_argument(
        "--from",
        dest="from_selector",
        required=True,
        help="Source entity: function:<name>, shorthand name, or hex address.",
    )
    trace_parser.add_argument(
        "--to",
        dest="to_selector",
        required=True,
        help="Target entity: function:<name>, shorthand name, or hex address.",
    )
    trace_parser.add_argument(
        "--max-paths",
        type=int,
        default=DEFAULT_MAX_PATHS,
        help=f"Maximum number of paths to return (default: {DEFAULT_MAX_PATHS}, max: {MAX_PATHS_LIMIT}).",
    )
    trace_parser.add_argument(
        "--max-depth",
        type=int,
        default=DEFAULT_MAX_TRACE_DEPTH,
        help=f"Maximum path depth to explore (default: {DEFAULT_MAX_TRACE_DEPTH}, max: {MAX_TRACE_DEPTH_LIMIT}).",
    )


# ---------------------------------------------------------------------------
# Command: search
# ---------------------------------------------------------------------------


def execute_search(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'search' command.

    VAL-FOCUS-025: Returns paginated results with opaque next_page_token;
                   default page size enforced.
    VAL-FOCUS-026: Search pagination with cursor produces next page
                   without duplicating first page results.
    VAL-FOCUS-027: Search with no matching results returns exit 0,
                   empty results array, null/missing next_page_token.
    """
    project_name = args.project
    query: str | None = args.query
    search_type: str = getattr(args, "search_type", "function")
    cursor_token: str | None = getattr(args, "cursor", None)
    raw_limit: int | None = getattr(args, "limit", None)

    if query is None:
        raise InvalidArgsError(
            "The 'search' command requires a query string. "
            "Provide a search term to match against entities (e.g., 'binary search --project proj \"main\"')."
        )

    page_size, clamp_warning = clamp_page_size(raw_limit)

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    adapter, binary_entity, _project_info = _get_adapter_and_binary(project_path, manifest)

    # Decode cursor if provided
    cursor_offset: int = 0
    cursor_query: str | None = None
    cursor_search_type: str | None = None

    if cursor_token:
        cursor_data = _decode_cursor(cursor_token)
        cursor_offset = cursor_data.get("offset", 0)
        cursor_query = cursor_data.get("query")
        cursor_search_type = cursor_data.get("search_type")

        # Validate cursor scope
        if cursor_query != query or cursor_search_type != search_type:
            raise InvalidArgsError(
                "Cursor token is scoped to a different query or search type. "
                "Obtain a fresh cursor for this query/type combination."
            )

    # Perform search
    try:
        results = adapter.search(binary_entity, query, search_type=search_type)
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to perform search: {e}",
            original_error=str(e),
        ) from e

    # Bound total results
    total = min(len(results), MAX_SEARCH_RESULTS)

    # Apply pagination
    sliced = results[cursor_offset : cursor_offset + page_size]

    # Build paginated response
    # Include query and search_type in the cursor for scope validation
    def _search_cursor_encoder(data: dict[str, Any]) -> str:
        data["query"] = query
        data["search_type"] = search_type
        return _encode_cursor(data)

    paginated = build_paginated_response(
        sliced,
        total,
        cursor_offset,
        page_size,
        cursor_encoder=_search_cursor_encoder,
    )

    # Build warnings/diagnostics
    warnings: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []

    if clamp_warning:
        warnings.append(make_warning(clamp_warning, severity="WARNING", category="pagination"))

    if len(results) > MAX_SEARCH_RESULTS:
        warnings.append(
            make_warning(
                f"Search results truncated: {len(results)} results found, "
                f"limited to {MAX_SEARCH_RESULTS}.",
                category="truncation",
            )
        )

    if not results:
        diagnostics.append(
            make_diagnostic(
                f"No entities matched query '{query}' (type: {search_type}).",
                severity="INFO",
                category="search",
                recoverable=True,
            )
        )

    manifest_state = manifest.get("state", "")
    if manifest_state and manifest_state != "READY":
        diagnostics.append(
            make_diagnostic(
                "Project has not been fully analyzed. Search results may be incomplete. "
                "Run 'binary analyze --project <proj>' for complete analysis.",
                severity="INFO",
                category="analysis_state",
                recoverable=True,
            )
        )

    data: dict[str, Any] = {
        "results": paginated["items"],
        "total": paginated["total"],
        "page_size": paginated["page_size"],
        "has_more": paginated["has_more"],
        "next_page_token": paginated.get("next_page_token"),
        "query": query,
        "search_type": search_type,
        "applied_filters": [
            {"filter": "search_type", "value": search_type},
        ],
    }

    return {
        "success": True,
        "partial": False,
        "warnings": warnings,
        "diagnostics": diagnostics,
        "data": data,
    }


# ---------------------------------------------------------------------------
# Command: trace
# ---------------------------------------------------------------------------


def execute_trace(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'trace' command.

    VAL-FOCUS-028: Finds bounded paths between --from and --to entities;
                   disclosed max path count and depth.
    VAL-FOCUS-029: Truncates paths at disclosed limits with partial=true
                   and diagnostic.
    VAL-FOCUS-030: Trace with no path between entities returns exit 0
                   with empty paths array and informational diagnostic.
    """
    project_name = args.project
    from_selector: str = args.from_selector
    to_selector: str = args.to_selector
    max_paths: int = getattr(args, "max_paths", DEFAULT_MAX_PATHS)
    max_depth: int = getattr(args, "max_depth", DEFAULT_MAX_TRACE_DEPTH)

    # Validate limits
    if max_paths <= 0:
        raise InvalidArgsError(f"--max-paths must be a positive integer, got {max_paths}.")
    if max_paths > MAX_PATHS_LIMIT:
        raise InvalidArgsError(
            f"--max-paths {max_paths} exceeds maximum allowed value of {MAX_PATHS_LIMIT}."
        )

    if max_depth <= 0:
        raise InvalidArgsError(f"--max-depth must be a positive integer, got {max_depth}.")
    if max_depth > MAX_TRACE_DEPTH_LIMIT:
        raise InvalidArgsError(
            f"--max-depth {max_depth} exceeds maximum allowed value of {MAX_TRACE_DEPTH_LIMIT}."
        )

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    adapter, binary_entity, _project_info = _get_adapter_and_binary(project_path, manifest)

    # Resolve --from entity
    from_addr = _resolve_trace_entity(from_selector, "from", adapter, binary_entity)
    # Resolve --to entity
    to_addr = _resolve_trace_entity(to_selector, "to", adapter, binary_entity)

    # Perform trace
    try:
        paths, truncated = adapter.trace(
            binary_entity,
            from_address=from_addr,
            to_address=to_addr,
            max_paths=max_paths,
            max_depth=max_depth,
        )
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to perform trace: {e}",
            original_error=str(e),
        ) from e

    # Build diagnostics
    warnings: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []

    partial = truncated

    if truncated:
        diagnostics.append(
            make_diagnostic(
                f"Trace truncated: paths or depth exceeded disclosed limits "
                f"(max_paths={max_paths}, max_depth={max_depth}). "
                f"Results may be incomplete.",
                severity="WARNING",
                category="truncation",
                recoverable=True,
            )
        )

    if not paths:
        diagnostics.append(
            make_diagnostic(
                f"No path found from '{from_selector}' to '{to_selector}'. "
                f"The entities may not be connected via call paths within "
                f"the disclosed depth limit of {max_depth}.",
                severity="INFO",
                category="trace",
                recoverable=True,
            )
        )

    manifest_state = manifest.get("state", "")
    if manifest_state and manifest_state != "READY":
        diagnostics.append(
            make_diagnostic(
                "Project has not been fully analyzed. Trace results may be incomplete. "
                "Run 'binary analyze --project <proj>' for complete analysis.",
                severity="INFO",
                category="analysis_state",
                recoverable=True,
            )
        )

    data: dict[str, Any] = {
        "paths": paths,
        "total_paths": len(paths),
        "from": {
            "selector": from_selector,
            "address": from_addr.to_dict(),
        },
        "to": {
            "selector": to_selector,
            "address": to_addr.to_dict(),
        },
        "max_paths": max_paths,
        "max_depth": max_depth,
        "truncated": truncated,
    }

    return {
        "success": True,
        "partial": partial,
        "warnings": warnings,
        "diagnostics": diagnostics,
        "data": data,
    }


def _resolve_trace_entity(
    selector: str,
    label: str,
    adapter: Any,
    binary_entity: Any,
) -> Address:
    """Resolve a trace entity selector to an Address.

    Accepts function:<name>, shorthand name, or hex address.
    """
    # Try hex address first
    if selector.startswith("0x"):
        try:
            return _parse_address(selector)
        except InvalidArgsError:
            pass

    # Try function selector
    parsed = parse_selector(selector)

    if parsed.is_address:
        try:
            return _parse_address(parsed.value)
        except InvalidArgsError:
            pass

    # Resolve as function name
    try:
        all_functions = adapter.get_functions(
            binary_entity, exclude_external=False, exclude_thunks=False
        )
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to retrieve functions for trace {label} entity: {e}",
            original_error=str(e),
        ) from e

    selected_function = resolve_function(parsed, all_functions, require_unique=True)

    if selected_function.address is None:
        raise EntityNotFoundError(
            f"Trace {label} entity: function",
            selector,
        )

    return selected_function.address
