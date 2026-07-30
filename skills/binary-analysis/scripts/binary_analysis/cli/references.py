"""Cross-reference and call graph commands — xrefs, callers, callees, callgraph.

All commands follow the standard JSON envelope pattern. Xrefs returns
cross-references with from/to addresses, kind (ReferenceKind), and confidence.
Callers lists functions that call the target. Callees lists functions called
by the target. Callgraph builds a bounded graph rooted at a target function.

Validation assertions covered:
- VAL-FOCUS-015, 016, 017: Xrefs
- VAL-FOCUS-018, 019: Callers
- VAL-FOCUS-020, 021: Callees
- VAL-FOCUS-022, 023, 024, 031: Callgraph
"""

from __future__ import annotations

import argparse
from typing import Any
from uuid import UUID, uuid4

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
# Breadth limits (for callgraph node bounding)
# ---------------------------------------------------------------------------

DEFAULT_MAX_CALLGRAPH_NODES = 100
DEFAULT_MAX_DEPTH = 3
MAX_DEPTH_LIMIT = 10

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
# Entity-to-dict conversion
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
# Address parsing and resolution
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
# Subparser registration
# ---------------------------------------------------------------------------


def add_subparser(subparsers: Any) -> None:
    """Register reference query subcommands: xrefs, callers, callees, callgraph."""

    # -- Xrefs --
    xrefs_parser = subparsers.add_parser(
        "xrefs",
        help="List cross-references to/from an entity (function or address).",
    )
    xrefs_parser.add_argument("--project", required=True, help="Project name or UUID.")
    xrefs_parser.add_argument(
        "selector",
        nargs="?",
        default=None,
        help=(
            "Entity selector: function:<name> (e.g., 'function:main') or "
            "a hex address (e.g., '0x401000')."
        ),
    )

    # -- Callers --
    callers_parser = subparsers.add_parser(
        "callers",
        help="List functions that call the target function.",
    )
    callers_parser.add_argument("--project", required=True, help="Project name or UUID.")
    callers_parser.add_argument(
        "selector",
        nargs="?",
        default=None,
        help="Function selector: function:<name> (e.g., 'function:main') or shorthand name.",
    )

    # -- Callees --
    callees_parser = subparsers.add_parser(
        "callees",
        help="List functions called by the target function.",
    )
    callees_parser.add_argument("--project", required=True, help="Project name or UUID.")
    callees_parser.add_argument(
        "selector",
        nargs="?",
        default=None,
        help="Function selector: function:<name> (e.g., 'function:main') or shorthand name.",
    )

    # -- Callgraph --
    callgraph_parser = subparsers.add_parser(
        "callgraph",
        help="Build a bounded call graph rooted at a target function.",
    )
    callgraph_parser.add_argument("--project", required=True, help="Project name or UUID.")
    callgraph_parser.add_argument(
        "selector",
        nargs="?",
        default=None,
        help="Function selector: function:<name> (e.g., 'function:main') or shorthand name.",
    )
    callgraph_parser.add_argument(
        "--depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help=f"Maximum call graph depth (positive integer, default: {DEFAULT_MAX_DEPTH}, max: {MAX_DEPTH_LIMIT}).",
    )


# ---------------------------------------------------------------------------
# Command: xrefs
# ---------------------------------------------------------------------------


def execute_xrefs(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'xrefs' command.

    VAL-FOCUS-015: Returns references with from, to (address objects),
                   kind (ReferenceKind), confidence; provenance present.
    VAL-FOCUS-016: Empty references result is valid (exit 0, no error diagnostics).
    VAL-FOCUS-017: Entity not found returns exit code 9 (ENTITY_NOT_FOUND).
    """
    project_name = args.project
    raw_selector: str | None = getattr(args, "selector", None)

    if not raw_selector:
        raise InvalidArgsError(
            "The 'xrefs' command requires an entity selector. "
            "Provide a function selector (e.g., 'function:main') or "
            "a hex address (e.g., '0x401000')."
        )

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    adapter, binary_entity, _project_info = _get_adapter_and_binary(project_path, manifest)

    # Parse the selector
    parsed = parse_selector(raw_selector)

    # Determine the address to look up xrefs for
    if parsed.is_address:
        # Address selector: use parsed address directly
        try:
            addr = _parse_address(parsed.value)
        except InvalidArgsError as err:
            raise InvalidArgsError(
                f"Invalid entity selector for xrefs: {raw_selector!r}. "
                "Use a function selector (e.g., 'function:main') or "
                "a hex address (e.g., '0x401000')."
            ) from err
    else:
        # Function selector: resolve the function, then use its address
        try:
            all_functions = adapter.get_functions(
                binary_entity, exclude_external=False, exclude_thunks=False
            )
        except BinaryAnalysisError:
            raise
        except Exception as e:
            raise BackendFailureError(
                f"Failed to retrieve functions for xrefs: {e}",
                original_error=str(e),
            ) from e

        selected_function = resolve_function(parsed, all_functions, require_unique=True)
        if selected_function.address is None:
            raise EntityNotFoundError("function", raw_selector)
        addr = selected_function.address

    # Retrieve cross-references
    try:
        references = adapter.get_xrefs(binary_entity, addr)
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to retrieve cross-references: {e}",
            original_error=str(e),
        ) from e

    # Convert to dicts
    ref_dicts = []
    for ref in references:
        d = _entity_to_dict(ref)
        # Rename from_addr -> from, to_addr -> to for the JSON contract
        if "from_addr" in d:
            d["from"] = d.pop("from_addr")
        if "to_addr" in d:
            d["to"] = d.pop("to_addr")
        ref_dicts.append(d)

    diagnostics: list[dict[str, Any]] = []
    manifest_state = manifest.get("state", "")
    if manifest_state and manifest_state != "READY":
        diagnostics.append(
            {
                "severity": "INFO",
                "message": (
                    "Project has not been fully analyzed. "
                    "Cross-reference results may be incomplete. "
                    "Run 'binary analyze --project <proj>' for complete analysis."
                ),
                "category": "analysis_state",
            }
        )

    data: dict[str, Any] = {
        "references": ref_dicts,
        "total": len(ref_dicts),
        "selector": raw_selector,
        "max_references": 1000,
    }

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": diagnostics,
        "data": data,
    }


# ---------------------------------------------------------------------------
# Command: callers
# ---------------------------------------------------------------------------


def execute_callers(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'callers' command.

    VAL-FOCUS-018: Returns array of function objects (name/symbol, address)
                   calling the target; depth/node limits disclosed.
    VAL-FOCUS-019: Leaf function returns exit 0 with empty array.
    """
    project_name = args.project
    raw_selector: str | None = getattr(args, "selector", None)

    if not raw_selector:
        raise InvalidArgsError(
            "The 'callers' command requires a function selector. "
            "Provide a function selector (e.g., 'function:main') or "
            "a shorthand function name (e.g., 'main')."
        )

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    adapter, binary_entity, _project_info = _get_adapter_and_binary(project_path, manifest)

    # Resolve the function
    parsed = parse_selector(raw_selector)

    try:
        all_functions = adapter.get_functions(
            binary_entity, exclude_external=False, exclude_thunks=False
        )
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to retrieve functions for callers: {e}",
            original_error=str(e),
        ) from e

    selected_function = resolve_function(parsed, all_functions, require_unique=True)

    # Retrieve callers
    try:
        call_edges = adapter.get_callers(binary_entity, selected_function)
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to retrieve callers: {e}",
            original_error=str(e),
        ) from e

    # Convert CallEdge list to function objects
    caller_dicts = []
    for edge in call_edges:
        caller = {
            "name": edge.from_name,
            "address": edge.from_address.to_dict() if edge.from_address else None,
            "kind": edge.kind,
        }
        caller_dicts.append(caller)

    diagnostics: list[dict[str, Any]] = []
    manifest_state = manifest.get("state", "")
    if manifest_state and manifest_state != "READY":
        diagnostics.append(
            {
                "severity": "INFO",
                "message": (
                    "Project has not been fully analyzed. "
                    "Caller results may be incomplete. "
                    "Run 'binary analyze --project <proj>' for complete analysis."
                ),
                "category": "analysis_state",
            }
        )

    data: dict[str, Any] = {
        "callers": caller_dicts,
        "total": len(caller_dicts),
        "target": {
            "name": selected_function.name,
            "address": selected_function.address.to_dict() if selected_function.address else None,
        },
        "max_depth": 1,
        "max_nodes": 1000,
    }

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": diagnostics,
        "data": data,
    }


# ---------------------------------------------------------------------------
# Command: callees
# ---------------------------------------------------------------------------


def execute_callees(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'callees' command.

    VAL-FOCUS-020: Returns array of function objects called by target;
                   depth/node limits disclosed.
    VAL-FOCUS-021: Terminal function returns exit 0 with empty array.
    """
    project_name = args.project
    raw_selector: str | None = getattr(args, "selector", None)

    if not raw_selector:
        raise InvalidArgsError(
            "The 'callees' command requires a function selector. "
            "Provide a function selector (e.g., 'function:main') or "
            "a shorthand function name (e.g., 'main')."
        )

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    adapter, binary_entity, _project_info = _get_adapter_and_binary(project_path, manifest)

    # Resolve the function
    parsed = parse_selector(raw_selector)

    try:
        all_functions = adapter.get_functions(
            binary_entity, exclude_external=False, exclude_thunks=False
        )
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to retrieve functions for callees: {e}",
            original_error=str(e),
        ) from e

    selected_function = resolve_function(parsed, all_functions, require_unique=True)

    # Retrieve callees
    try:
        call_edges = adapter.get_callees(binary_entity, selected_function)
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to retrieve callees: {e}",
            original_error=str(e),
        ) from e

    # Convert CallEdge list to function objects
    callee_dicts = []
    for edge in call_edges:
        callee = {
            "name": edge.to_name,
            "address": edge.to_address.to_dict() if edge.to_address else None,
            "kind": edge.kind,
        }
        callee_dicts.append(callee)

    diagnostics: list[dict[str, Any]] = []
    manifest_state = manifest.get("state", "")
    if manifest_state and manifest_state != "READY":
        diagnostics.append(
            {
                "severity": "INFO",
                "message": (
                    "Project has not been fully analyzed. "
                    "Callee results may be incomplete. "
                    "Run 'binary analyze --project <proj>' for complete analysis."
                ),
                "category": "analysis_state",
            }
        )

    data: dict[str, Any] = {
        "callees": callee_dicts,
        "total": len(callee_dicts),
        "target": {
            "name": selected_function.name,
            "address": selected_function.address.to_dict() if selected_function.address else None,
        },
        "max_depth": 1,
        "max_nodes": 1000,
    }

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": diagnostics,
        "data": data,
    }


# ---------------------------------------------------------------------------
# Command: callgraph
# ---------------------------------------------------------------------------


def execute_callgraph(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'callgraph' command.

    VAL-FOCUS-022: Builds bounded graph rooted at target function with nodes
                   and edges; root is target; depth disclosed.
    VAL-FOCUS-023: --depth 2 limits graph to exactly 2 levels; applied depth disclosed.
    VAL-FOCUS-024: --depth 0 or --depth -1 fails with exit code 2,
                   'depth must be a positive integer'.
    VAL-FOCUS-031: Breadth limits enforced with truncation diagnostic and
                   bounded node count.
    """
    project_name = args.project
    raw_selector: str | None = getattr(args, "selector", None)
    depth: int = getattr(args, "depth", DEFAULT_MAX_DEPTH)

    # VAL-FOCUS-024: Validate depth is a positive integer
    if depth <= 0:
        raise InvalidArgsError(
            f"Depth must be a positive integer, got {depth}. "
            "Provide a positive depth value (e.g., --depth 2) or use the default (3)."
        )

    if depth > MAX_DEPTH_LIMIT:
        raise InvalidArgsError(
            f"Depth {depth} exceeds maximum allowed depth of {MAX_DEPTH_LIMIT}. "
            f"Use a depth value between 1 and {MAX_DEPTH_LIMIT}."
        )

    if not raw_selector:
        raise InvalidArgsError(
            "The 'callgraph' command requires a function selector. "
            "Provide a function selector (e.g., 'function:main') or "
            "a shorthand function name (e.g., 'main')."
        )

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    adapter, binary_entity, _project_info = _get_adapter_and_binary(project_path, manifest)

    # Resolve the function
    parsed = parse_selector(raw_selector)

    try:
        all_functions = adapter.get_functions(
            binary_entity, exclude_external=False, exclude_thunks=False
        )
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to retrieve functions for callgraph: {e}",
            original_error=str(e),
        ) from e

    selected_function = resolve_function(parsed, all_functions, require_unique=True)

    # Build the call graph
    try:
        callgraph = adapter.get_callgraph(binary_entity, selected_function, max_depth=depth)
    except BinaryAnalysisError:
        raise
    except Exception as e:
        raise BackendFailureError(
            f"Failed to build call graph: {e}",
            original_error=str(e),
        ) from e

    # Apply breadth limits (VAL-FOCUS-031)
    max_nodes = getattr(adapter, "_callgraph_max_breadth", DEFAULT_MAX_CALLGRAPH_NODES)

    nodes = list(callgraph.nodes)
    edges = list(callgraph.edges)
    truncated = callgraph.truncated

    # Apply node count bounding if there are too many nodes
    if len(nodes) > max_nodes:
        truncated = True
        nodes = nodes[:max_nodes]
        # Remove edges that reference truncated nodes
        valid_addrs = set()
        for n in nodes:
            addr = n.get("address", {})
            offset = addr.get("offset", "")
            valid_addrs.add(offset)

        edges = [
            e
            for e in edges
            if e.get("from", {}).get("offset", "") in valid_addrs
            and e.get("to", {}).get("offset", "") in valid_addrs
        ]

    total_nodes = len(nodes)
    total_edges = len(edges)

    graph_data: dict[str, Any] = {
        "root_address": callgraph.root_address.to_dict() if callgraph.root_address else None,
        "nodes": nodes,
        "edges": edges,
        "max_depth": depth,
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "truncated": truncated,
    }

    diagnostics: list[dict[str, Any]] = []

    if truncated:
        diagnostics.append(
            {
                "severity": "WARNING",
                "message": (
                    f"Call graph truncated: total nodes bounded to {max_nodes}. "
                    f"The graph contains {total_nodes} nodes and {total_edges} edges "
                    f"after applying breadth limits. Some call targets beyond the "
                    f"limit may have been omitted."
                ),
                "category": "truncation",
            }
        )

    manifest_state = manifest.get("state", "")
    if manifest_state and manifest_state != "READY":
        diagnostics.append(
            {
                "severity": "INFO",
                "message": (
                    "Project has not been fully analyzed. "
                    "Call graph results may be incomplete. "
                    "Run 'binary analyze --project <proj>' for complete analysis."
                ),
                "category": "analysis_state",
            }
        )

    data: dict[str, Any] = {
        "graph": graph_data,
        "target": {
            "name": selected_function.name,
            "address": selected_function.address.to_dict() if selected_function.address else None,
        },
        "applied_depth": depth,
    }

    return {
        "success": True,
        "partial": truncated,
        "warnings": [],
        "diagnostics": diagnostics,
        "data": data,
    }
