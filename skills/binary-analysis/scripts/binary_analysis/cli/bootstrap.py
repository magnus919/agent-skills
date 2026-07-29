"""Bootstrap command — discover and install dependencies."""

from __future__ import annotations

import argparse
from typing import Any


def add_subparser(subparsers: Any) -> argparse.ArgumentParser:
    """Register the bootstrap subcommand."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "bootstrap",
        help="Discover and install dependencies (Ghidra, Java, PyGhidra).",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Show what would be installed without making changes.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Download and install missing dependencies.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview installation plan without mutation.",
    )
    return parser


def execute(args: argparse.Namespace) -> dict[str, Any]:
    """Run the bootstrap command.

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
            "message": "Bootstrap command not yet implemented.",
            "plan_requested": args.plan if hasattr(args, "plan") else False,
            "apply_requested": args.apply if hasattr(args, "apply") else False,
        },
    }
