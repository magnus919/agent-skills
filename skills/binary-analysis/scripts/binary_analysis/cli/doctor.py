"""Doctor command — check dependency health."""

from __future__ import annotations

import argparse
from typing import Any


def add_subparser(subparsers: Any) -> argparse.ArgumentParser:
    """Register the doctor subcommand."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "doctor",
        help="Check dependency health and report diagnostics.",
    )
    return parser


def execute(args: argparse.Namespace) -> dict[str, Any]:
    """Run the doctor command.

    Returns a result dict suitable for JSON envelope output.
    Currently a stub — real implementation comes in a later feature.
    """
    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": {
            "status": "not_implemented",
            "message": "Doctor command not yet implemented.",
            "components": [],
        },
    }
