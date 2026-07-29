"""Project command — manage analysis workspaces.

Subcommands: create, list, status, clean, remove, migrate.
"""

from __future__ import annotations

import argparse
from typing import Any


def _build_project_subparsers(subparsers: Any) -> None:
    """Register project sub-subcommands."""
    create_parser: argparse.ArgumentParser = subparsers.add_parser(
        "create", help="Create a new project workspace."
    )
    create_parser.add_argument("name", help="Project name.")
    create_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview creation without mutating.",
    )

    list_parser = subparsers.add_parser("list", help="List projects with pagination.")
    list_parser.add_argument(
        "--limit",
        type=_positive_int,
        default=100,
        help="Maximum projects per page (positive integer).",
    )
    list_parser.add_argument(
        "--cursor",
        default=None,
        help="Pagination cursor from previous response.",
    )

    status_parser = subparsers.add_parser("status", help="Show project state and metadata.")
    status_parser.add_argument("project", help="Project name or UUID.")

    clean_parser = subparsers.add_parser("clean", help="Reset a FAILED project to CREATED.")
    clean_parser.add_argument("project", help="Project name or UUID.")
    clean_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt.")
    clean_parser.add_argument(
        "--force", action="store_true", help="Force clean without confirmation."
    )

    remove_parser = subparsers.add_parser("remove", help="Delete a project workspace.")
    remove_parser.add_argument("project", help="Project name or UUID.")
    remove_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt.")
    remove_parser.add_argument(
        "--force", action="store_true", help="Force removal without confirmation."
    )
    remove_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deletion paths without mutating.",
    )

    migrate_parser = subparsers.add_parser("migrate", help="Upgrade project workspace format.")
    migrate_parser.add_argument("project", help="Project name or UUID.")
    migrate_parser.add_argument(
        "--plan",
        action="store_true",
        help="Show migration plan without mutating.",
    )
    migrate_parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform the workspace format upgrade.",
    )
    migrate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migration plan without mutating.",
    )


def add_subparser(subparsers: Any) -> argparse.ArgumentParser:
    """Register the project subcommand with sub-subcommands."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "project",
        help="Manage analysis workspaces.",
    )
    project_sub = parser.add_subparsers(dest="project_command", help="Project subcommands")
    _build_project_subparsers(project_sub)
    return parser


def _positive_int(value: str) -> int:
    """Validate a positive integer argument."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("limit must be a positive integer") from None
    if number <= 0:
        raise argparse.ArgumentTypeError("limit must be a positive integer")
    return number


def execute(args: argparse.Namespace) -> dict[str, Any]:
    """Run a project subcommand.

    Currently a stub — real implementation comes in a later feature.
    """
    subcommand = getattr(args, "project_command", None)
    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": {
            "status": "not_implemented",
            "message": f"project {subcommand} not yet implemented.",
            "subcommand": subcommand,
        },
    }
