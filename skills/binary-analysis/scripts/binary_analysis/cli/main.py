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

from binary_analysis import __version__
from binary_analysis.cli import bootstrap, doctor, project, version
from binary_analysis.domain.enums import ExitCode
from binary_analysis.domain.errors import (
    BinaryAnalysisError,
    DependencyMissingError,
    InvalidArgsError,
)

# ---------------------------------------------------------------------------
# Schema version
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Argument type validators
# ---------------------------------------------------------------------------


def _positive_int(value: str) -> int:
    """Validate a positive integer argument (for --limit)."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("limit must be a positive integer") from None
    if number <= 0:
        raise argparse.ArgumentTypeError("limit must be a positive integer")
    return number


def _positive_duration(value: str) -> int:
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
        provenance: Optional provenance metadata.

    Returns:
        A dict suitable for JSON serialization.
    """
    if provenance is None:
        provenance = _default_provenance()

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


def _default_provenance() -> dict[str, Any]:
    """Return default provenance metadata for stub commands."""
    return {
        "cli_version": __version__,
        "schema_version": SCHEMA_VERSION,
        "adapter": "none",
        "adapter_version": "0.1.0",
        "backend": "none",
        "backend_version": "0.1.0",
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
    else:
        raise InvalidArgsError(f"Unknown command: {command}")


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def _output_json(envelope: dict[str, Any]) -> None:
    """Write the JSON envelope to stdout with no extraneous text."""
    json.dump(envelope, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.stdout.flush()


def _output_text(envelope: dict[str, Any], args: argparse.Namespace) -> None:
    """Write human-readable output for the command result."""
    data = envelope.get("data", {})

    if isinstance(data, dict) and data.get("status") == "not_implemented":
        print(data.get("message", "Command not yet implemented."))
    elif isinstance(data, dict) and "cli_version" in data:
        _output_version_text(data)
    elif isinstance(data, list):
        for item in data:
            print(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            if key == "status":
                continue
            print(f"{key}: {value}")
    else:
        print(data)


def _output_version_text(data: dict[str, Any]) -> None:
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


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, dispatch, and output results.

    Returns an exit code (0-13).
    """
    parser = build_parser()

    if argv is None:
        argv = sys.argv[1:]

    # Reorder to handle global flags before subcommand
    argv = _extract_globals(argv)

    t_start = time.perf_counter()

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        # argparse calls sys.exit(2) on invalid args; map to exit code 2
        if e.code == 0:
            return ExitCode.SUCCESS
        return ExitCode.INVALID_ARGS

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
        else:
            print(f"Error: {e.message}", file=sys.stderr)
        return e.exit_code
    except DependencyMissingError as e:
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
        else:
            print(f"Error: {e.message}", file=sys.stderr)
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
        else:
            print(f"Error: {e.message}", file=sys.stderr)
        return e.exit_code

    t_elapsed = int((time.perf_counter() - t_start) * 1000)

    # Build the standard envelope
    success = result.get("success", True)
    partial = result.get("partial", False)
    warnings_list = result.get("warnings", [])
    diagnostics = result.get("diagnostics", [])
    data = result.get("data", {})

    envelope = build_envelope(
        command=command_name,
        success=success,
        partial=partial,
        warnings=warnings_list,
        diagnostics=diagnostics,
        data=data,
        duration_ms=t_elapsed,
    )

    if args.json:
        _output_json(envelope)
    else:
        if not quiet:
            _output_text(envelope, args)

    return ExitCode.SUCCESS if success else ExitCode.GENERIC_ERROR


if __name__ == "__main__":
    sys.exit(main())
