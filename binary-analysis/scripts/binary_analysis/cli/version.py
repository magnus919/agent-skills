"""Version command — report component versions."""

from __future__ import annotations

import argparse
import platform
from typing import Any

from binary_analysis import __version__


def add_subparser(subparsers: Any) -> argparse.ArgumentParser:
    """Register the version subcommand."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "version",
        help="Report CLI, schema, adapter, backend, and platform versions.",
    )
    return parser


def execute(args: argparse.Namespace) -> dict[str, Any]:
    """Run the version command.

    Returns a result dict suitable for JSON envelope output.
    """
    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": {
            "cli_version": __version__,
            "schema_version": "1.0.0",
            "workspace_version": "1",
            "adapter": {
                "name": "none",
                "version": "0.1.0",
            },
            "backend": {
                "name": "none",
                "version": "0.1.0",
            },
            "platform": {
                "system": platform.system(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
            },
        },
    }
