"""Doctor command — check dependency health.

Detects missing dependencies (Java, Ghidra, PyGhidra) and reports
diagnostic entries with severity, component, message, and remediation hints.
When all dependencies are healthy, returns success=true with zero ERROR entries.

Supports --require-ready flag for programmatic readiness checks (used by
bootstrap-to-doctor roundtrip validation).
"""

from __future__ import annotations

import argparse
from typing import Any

from binary_analysis.bootstrap.deps import discover_dependencies
from binary_analysis.domain.enums import ExitCode


def add_subparser(subparsers: Any) -> argparse.ArgumentParser:
    """Register the doctor subcommand."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "doctor",
        help="Check dependency health and report diagnostics.",
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Fail (exit code 3) unless all dependencies are present and verified.",
    )
    return parser


def execute(args: argparse.Namespace) -> dict[str, Any]:
    """Run the doctor command.

    Discovers Java, Ghidra, and PyGhidra and reports diagnostic entries
    for each. Missing components get ERROR severity with remediation hints.
    Healthy components get INFO severity.

    With --require-ready, fails unless every component is present.

    Returns:
        A result dict with diagnostics and component status.
    """
    deps = discover_dependencies()
    diagnostics: list[dict[str, Any]] = []
    components: list[dict[str, Any]] = []
    has_error = False
    require_ready: bool = getattr(args, "require_ready", False)

    for dep in deps:
        components.append(dep.to_dict())

        if dep.status == "missing" or dep.status == "error":
            has_error = True
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "component": dep.name,
                    "message": dep.message,
                    "remediation": dep.remediation,
                }
            )
        else:
            diagnostics.append(
                {
                    "severity": "INFO",
                    "component": dep.name,
                    "message": dep.message,
                    "remediation": dep.remediation,
                }
            )

    result: dict[str, Any] = {
        "success": not has_error,
        "partial": False,
        "warnings": [],
        "diagnostics": diagnostics,
        "data": {
            "components": components,
        },
    }

    if has_error:
        result["_exit_code"] = ExitCode.DEPENDENCY_MISSING
    elif require_ready:
        # All dependencies present and --require-ready: report all-green
        result["data"]["ready"] = True

    return result
