"""CLI entrypoint — argument parsing, dispatch, and JSON envelope output.

The `binary` CLI is the sole automation surface for the binary analysis skill.
Every command supports --json for machine-readable output with a standard
envelope: schema_version, command, generated_at, duration_ms, success,
partial, warnings, diagnostics, provenance, data.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from typing import Any

from binary_analysis.cli import (
    binary_ops,
    bootstrap,
    doctor,
    functions,
    project,
    references,
    search,
    security,
    structural,
    version,
)
from binary_analysis.cli.helpers import (
    SCHEMA_VERSION,
    enrich_provenance,
)
from binary_analysis.cli.helpers import (
    default_provenance as _default_provenance,
)
from binary_analysis.domain.enums import ExitCode
from binary_analysis.domain.errors import (
    BinaryAnalysisError,
    DependencyMissingError,
    InvalidArgsError,
)

# ---------------------------------------------------------------------------
# Argument type validators
# ---------------------------------------------------------------------------


def _positive_int(value: str) -> int:  # pragma: no cover
    """Validate a positive integer argument (for --limit)."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("limit must be a positive integer") from None
    if number <= 0:
        raise argparse.ArgumentTypeError("limit must be a positive integer")
    return number


def _positive_duration(value: str) -> int:  # pragma: no cover
    """Validate a positive duration argument in seconds (for --timeout)."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("timeout must be a positive duration") from None
    if number <= 0:
        raise argparse.ArgumentTypeError("timeout must be a positive duration")
    return number


# ---------------------------------------------------------------------------
# JSON envelope builder
# ---------------------------------------------------------------------------


def build_envelope(
    command: str,
    success: bool,
    partial: bool,
    warnings: list[dict[str, Any]],
    diagnostics: list[dict[str, Any]],
    data: Any,
    duration_ms: int,
    provenance: dict[str, Any] | None = None,
    *,
    project_id: str | None = None,
    binary_id: str | None = None,
    binary_sha256: str | None = None,
    architecture: str | None = None,
    analysis_profile: str | None = None,
    project_state: str | None = None,
) -> dict[str, Any]:
    """Build the standard JSON envelope for every command response.

    Args:
        command: The invoked command name (e.g., "doctor", "version").
        success: Whether the command succeeded.
        partial: Whether the result is partial (some work may be incomplete).
        warnings: List of warning entries.
        diagnostics: List of diagnostic entries.
        data: The command-specific data payload.
        duration_ms: Wall-clock duration in milliseconds.
        provenance: Optional provenance metadata (base fields).
        project_id: Optional project UUID for project-context commands.
        binary_id: Optional binary UUID for binary-context commands.
        binary_sha256: Optional binary SHA-256 for binary-context commands.
        architecture: Optional architecture spec for binary commands.
        analysis_profile: Optional profile name for post-analysis commands.

    Returns:
        A dict suitable for JSON serialization.
    """
    if provenance is None:  # pragma: no cover
        provenance = _default_provenance()

    provenance = enrich_provenance(
        provenance,
        project_id=project_id,
        binary_id=binary_id,
        binary_sha256=binary_sha256,
        architecture=architecture,
        analysis_profile=analysis_profile,
    )

    if project_state is not None:
        provenance["project_state"] = project_state

    return {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "duration_ms": duration_ms,
        "success": success,
        "partial": partial,
        "warnings": warnings,
        "diagnostics": diagnostics,
        "provenance": provenance,
        "data": data,
    }


# ---------------------------------------------------------------------------
# Global argument extraction
# ---------------------------------------------------------------------------

_GLOBAL_FLAGS: dict[str, int] = {
    "--json": 0,
    "--quiet": 0,
    "--limit": 1,
    "--timeout": 1,
}


def _extract_globals(argv: list[str]) -> list[str]:
    """Move global flags before the subcommand for argparse.

    Boolean flags consume no value; valued flags consume exactly one.
    """
    head: list[str] = []
    tail: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        param = arg.split("=", 1)[0] if "=" in arg else arg
        if param in _GLOBAL_FLAGS:
            head.append(arg)
            count = _GLOBAL_FLAGS[param]
            for _ in range(count):
                i += 1
                if i < len(argv):
                    head.append(argv[i])
            i += 1
        else:
            tail.append(arg)
            i += 1
    return head + tail


# ---------------------------------------------------------------------------
# Parser construction
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the full argparse hierarchy with subcommands."""
    parser = argparse.ArgumentParser(
        prog="binary",
        description=(
            "Binary analysis CLI — backend-neutral static analysis harness. "
            "Supports project management, binary import, structural queries, "
            "focused analysis, security triage, and reporting."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global flags
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Emit machine-readable JSON output (standard envelope).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress progress messages and non-error diagnostics on stderr.",
    )

    # Shared options added as global flags for validation
    parser.add_argument(
        "--limit",
        type=_positive_int,
        default=None,
        help="Maximum number of results (positive integer).",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_duration,
        default=300,
        help="Operation timeout in seconds (positive integer, default: 300).",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # Register subcommands
    doctor.add_subparser(sub)
    bootstrap.add_subparser(sub)
    version.add_subparser(sub)
    project.add_subparser(sub)
    binary_ops.add_subparser(sub)
    structural.add_subparser(sub)
    functions.add_subparser(sub)
    references.add_subparser(sub)
    search.add_subparser(sub)
    security.add_subparser(sub)

    return parser


# ---------------------------------------------------------------------------
# Command dispatch
# ---------------------------------------------------------------------------


def _resolve_command_name(args: argparse.Namespace) -> str:
    """Resolve the canonical command name from parsed args."""
    command = args.command
    if command == "project":
        subcmd = getattr(args, "project_command", None)
        if subcmd:
            return f"project {subcmd}"
    return command or ""


def _dispatch(args: argparse.Namespace) -> dict[str, Any]:
    """Dispatch to the appropriate command handler and return a result dict."""
    command = args.command

    if not command:
        raise InvalidArgsError("No command specified. Run 'binary --help' for usage.")

    if command == "doctor":
        return doctor.execute(args)
    elif command == "bootstrap":
        return bootstrap.execute(args)
    elif command == "version":
        return version.execute(args)
    elif command == "project":
        project_cmd = getattr(args, "project_command", None)
        if project_cmd:
            return project.execute(args)
        else:
            raise InvalidArgsError(
                "No project subcommand specified. "
                "Available: create, list, status, clean, remove, migrate."
            )
    elif command == "import":
        return binary_ops.execute_import(args)
    elif command == "analyze":
        return binary_ops.execute_analyze(args)
    elif command == "metadata":
        return binary_ops.execute_metadata(args)
    elif command == "sections":
        return structural.execute_sections(args)
    elif command == "entrypoints":
        return structural.execute_entrypoints(args)
    elif command == "imports":
        return structural.execute_imports(args)
    elif command == "exports":
        return structural.execute_exports(args)
    elif command == "symbols":
        return structural.execute_symbols(args)
    elif command == "strings":
        return structural.execute_strings(args)
    elif command == "functions":
        return functions.execute_functions(args)
    elif command == "decompile":
        return functions.execute_decompile(args)
    elif command == "disassemble":
        return functions.execute_disassemble(args)
    elif command == "bytes":
        return functions.execute_bytes(args)
    elif command == "xrefs":
        return references.execute_xrefs(args)
    elif command == "callers":
        return references.execute_callers(args)
    elif command == "callees":
        return references.execute_callees(args)
    elif command == "callgraph":
        return references.execute_callgraph(args)
    elif command == "search":
        return search.execute_search(args)
    elif command == "trace":
        return search.execute_trace(args)
    elif command == "triage":
        return security.execute_triage(args)
    elif command == "diagnostics":
        return security.execute_diagnostics(args)
    else:
        raise InvalidArgsError(f"Unknown command: {command}")  # pragma: no cover


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def _output_json(envelope: dict[str, Any]) -> None:
    """Write the JSON envelope to stdout with no extraneous text."""
    json.dump(envelope, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.stdout.flush()


def _output_text(envelope: dict[str, Any], args: argparse.Namespace) -> None:  # pragma: no cover
    """Write human-readable output for the command result.

    Plain-text output is consistent with --json mode: same entity counts,
    addresses, and key values are displayed. The output format adapts to the
    data shape returned by each command.
    """
    data = envelope.get("data", {})

    if isinstance(data, dict) and data.get("status") == "not_implemented":
        print(data.get("message", "Command not yet implemented."))
        return

    if isinstance(data, dict) and "cli_version" in data:
        _output_version_text(data)
    elif isinstance(data, list):
        _output_list(data)
    elif isinstance(data, dict) and "items" in data:
        _output_paginated(data)
    elif isinstance(data, dict):
        _output_dict(data)
    else:
        print(data)

    # Show diagnostics and warnings
    warnings = envelope.get("warnings", [])
    diagnostics = envelope.get("diagnostics", [])
    _output_warnings(warnings, diagnostics)

    # Footer with metadata
    success = envelope.get("success", False)
    partial = envelope.get("partial", False)
    duration = envelope.get("duration_ms", 0)
    if args.json:
        pass  # Footer only for plain-text
    else:
        status = "SUCCESS" if success else "FAILED"
        if partial:
            status += " (partial)"
        print(f"\n[{status} in {duration}ms]")


def _output_version_text(data: dict[str, Any]) -> None:  # pragma: no cover
    """Human-readable version output."""
    print(f"binary CLI version: {data.get('cli_version', 'unknown')}")
    print(f"Schema version:     {data.get('schema_version', 'unknown')}")
    print(f"Workspace version:  {data.get('workspace_version', 'unknown')}")

    adapter = data.get("adapter", {})
    backend = data.get("backend", {})
    platform_info = data.get("platform", {})

    if isinstance(adapter, dict):
        print(f"Adapter:            {adapter.get('name', 'unknown')} {adapter.get('version', '')}")
    if isinstance(backend, dict):
        print(f"Backend:            {backend.get('name', 'unknown')} {backend.get('version', '')}")
    if isinstance(platform_info, dict):
        print(
            f"Platform:           {platform_info.get('system', '?')} "
            f"{platform_info.get('machine', '?')} "
            f"(Python {platform_info.get('python_version', '?')})"
        )


def _output_list(items: list[Any]) -> None:  # pragma: no cover
    """Output a simple list of items."""
    if not items:
        print("(empty)")
        return
    for item in items:
        if isinstance(item, dict):
            _print_entity(item)
        else:
            print(str(item))


def _output_paginated(data: dict[str, Any]) -> None:  # pragma: no cover
    """Output paginated results with count and cursor info."""
    items = data.get("items", [])
    total = data.get("total", len(items))
    has_more = data.get("has_more", False)
    next_page_token = data.get("next_page_token")

    print(f"Total: {total}")

    if not items:
        print("(no results)")
        return

    for item in items:
        if isinstance(item, dict):
            _print_entity(item)
        else:
            print(str(item))

    if has_more and next_page_token:
        print(f"\n--- more results available (next_page_token: {next_page_token}) ---")


def _output_dict(data: dict[str, Any]) -> None:  # pragma: no cover
    """Output a flat dict as key: value pairs, handling nested entities."""
    for key, value in data.items():
        if key == "status":
            continue
        if isinstance(value, dict):
            if "space" in value and "offset" in value and "display" in value:
                # Address object
                print(
                    f"{key}: {value.get('display', value['offset'])}"
                    f"{' (file_offset=' + str(value['file_offset']) + ')' if value.get('file_offset') is not None else ''}"
                )
            else:
                print(f"{key}:")
                for sub_k, sub_v in value.items():
                    print(f"  {sub_k}: {sub_v}")
        elif isinstance(value, list):
            if not value:
                print(f"{key}: []")
            else:
                print(f"{key}:")
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        _print_entity(item, indent="  ")
                    else:
                        print(f"  [{idx}] {item}")
        elif value is None:
            print(f"{key}: (null)")
        else:
            print(f"{key}: {value}")


def _print_entity(entity: dict[str, Any], indent: str = "") -> None:  # pragma: no cover
    """Print a single entity in a compact human-readable format."""
    name = entity.get("name", entity.get("text", entity.get("symbol", "")))
    address = entity.get("address", {})
    addr_display: str = ""
    if isinstance(address, dict):
        addr_display = str(address.get("display", address.get("offset", "")))
    elif address is not None:
        addr_display = str(address)

    # Build a one-line summary
    parts = []
    if name:
        parts.append(str(name))
    if addr_display:
        parts.append(f"@ {addr_display}")

    # Common extra fields
    if "size_bytes" in entity:
        parts.append(f"{entity['size_bytes']}B")
    if "length" in entity and entity.get("length"):
        parts.append(f"len={entity['length']}")
    if "kind" in entity:
        parts.append(str(entity["kind"]))
    if "state" in entity:
        parts.append(str(entity["state"]))
    if "encoding" in entity:
        parts.append(str(entity["encoding"]))
    if "confidence" in entity:
        parts.append(str(entity["confidence"]))
    if entity.get("module"):
        parts.append(f"({entity['module']})")

    line = f"{indent}{' | '.join(parts)}" if parts else f"{indent}(unnamed)"
    print(line)


def _output_warnings(  # pragma: no cover
    warnings: list[dict[str, Any]],
    diagnostics: list[dict[str, Any]],
) -> None:
    """Output warnings and diagnostics to stderr."""
    for w in warnings:
        msg = w.get("message", str(w))
        print(f"Warning: {msg}", file=sys.stderr)
    for d in diagnostics:
        severity = d.get("severity", "INFO")
        msg = d.get("message", str(d))
        print(f"[{severity}] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, dispatch, and output results.

    Returns an exit code (0-13).
    """
    parser = build_parser()

    if argv is None:  # pragma: no cover
        argv = sys.argv[1:]

    # Reorder to handle global flags before subcommand
    argv = _extract_globals(argv)

    t_start = time.perf_counter()

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        # argparse calls sys.exit(2) on invalid args; map to exit code 2
        if e.code == 0:  # pragma: no cover
            return ExitCode.SUCCESS
        return ExitCode.INVALID_ARGS  # pragma: no cover

    command_name = _resolve_command_name(args)
    quiet = getattr(args, "quiet", False)

    try:
        result = _dispatch(args)
    except InvalidArgsError as e:
        t_elapsed = int((time.perf_counter() - t_start) * 1000)
        envelope = build_envelope(
            command=command_name or "unknown",
            success=False,
            partial=False,
            warnings=[],
            diagnostics=[e.to_diagnostic()],
            data=None,
            duration_ms=t_elapsed,
        )
        if args.json:
            _output_json(envelope)
        else:  # pragma: no cover
            print(f"Error: {e.message}", file=sys.stderr)  # pragma: no cover
        return e.exit_code
    except DependencyMissingError as e:  # pragma: no cover
        t_elapsed = int((time.perf_counter() - t_start) * 1000)
        envelope = build_envelope(
            command=command_name or "unknown",
            success=False,
            partial=False,
            warnings=[],
            diagnostics=[e.to_diagnostic()],
            data=None,
            duration_ms=t_elapsed,
        )
        if args.json:
            _output_json(envelope)
        else:  # pragma: no cover
            print(f"Error: {e.message}", file=sys.stderr)  # pragma: no cover
        return e.exit_code
    except BinaryAnalysisError as e:
        t_elapsed = int((time.perf_counter() - t_start) * 1000)
        envelope = build_envelope(
            command=command_name or "unknown",
            success=False,
            partial=False,
            warnings=[],
            diagnostics=[e.to_diagnostic()],
            data=None,
            duration_ms=t_elapsed,
        )
        if args.json:
            _output_json(envelope)
        else:  # pragma: no cover
            print(f"Error: {e.message}", file=sys.stderr)  # pragma: no cover
        return e.exit_code

    t_elapsed = int((time.perf_counter() - t_start) * 1000)

    # Build the standard envelope
    success = result.get("success", True)
    partial = result.get("partial", False)
    warnings_list = result.get("warnings", [])
    diagnostics = result.get("diagnostics", [])
    data = result.get("data", {})

    # Extract provenance overrides from result
    provenance_project_state: str | None = result.get("_provenance_project_state")
    provenance_analysis_profile: str | None = result.get("_provenance_analysis_profile")
    provenance_project_id: str | None = result.get("_provenance_project_id")
    provenance_binary_id: str | None = result.get("_provenance_binary_id")
    provenance_binary_sha256: str | None = result.get("_provenance_binary_sha256")

    envelope = build_envelope(
        command=command_name,
        success=success,
        partial=partial,
        warnings=warnings_list,
        diagnostics=diagnostics,
        data=data,
        duration_ms=t_elapsed,
        project_id=provenance_project_id,
        binary_id=provenance_binary_id,
        binary_sha256=provenance_binary_sha256,
        project_state=provenance_project_state,
        analysis_profile=provenance_analysis_profile,
    )

    if args.json:
        _output_json(envelope)
    else:  # pragma: no cover
        if not quiet:
            _output_text(envelope, args)

    # Respect explicit exit_code from command result, otherwise derive from success
    explicit_code = result.get("_exit_code")
    if isinstance(explicit_code, int):
        return explicit_code
    return ExitCode.SUCCESS if success else ExitCode.GENERIC_ERROR


if __name__ == "__main__":
    sys.exit(main())
