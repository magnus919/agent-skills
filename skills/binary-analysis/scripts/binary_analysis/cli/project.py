"""Project command — manage analysis workspaces.

Subcommands: create, list, status, clean, remove, migrate.

Implements the full project lifecycle with state machine enforcement,
atomic manifest writes, file-based locking, and confirmation gates for
destructive operations.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

from binary_analysis.cli.helpers import (
    build_paginated_response,
    clamp_page_size,
)
from binary_analysis.domain.enums import AuditResult, ProjectState
from binary_analysis.domain.errors import (
    InvalidArgsError,
    ProjectNotFoundError,
)
from binary_analysis.projects.cache import cache_clear
from binary_analysis.projects.lock import (
    get_lock_holder,
    is_locked,
)
from binary_analysis.projects.manifest import (
    create_manifest,
    load_manifest,
    save_manifest,
    update_manifest_field,
)
from binary_analysis.projects.state_machine import (
    can_clean,
    should_reject_migrate,
)
from binary_analysis.projects.workspace import (
    create_workspace,
    get_project_path,
    get_workspace_subdirs,
    list_workspaces,
    remove_workspace,
    validate_project_name,
    workspace_exists,
)
from binary_analysis.reporting.audit import write_audit_event

# Current workspace version for migration
_WORKSPACE_VERSION = "1"


# ---------------------------------------------------------------------------
# Subparser registration
# ---------------------------------------------------------------------------


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
    # --limit is read from the root parser (consumed before the subparser by
    # _extract_globals). The list subparser does not register its own --limit
    # to avoid overwriting the root parser's value.
    list_parser.add_argument(
        "--page-token",
        default=None,
        help="Opaque pagination cursor from previous response (next_page_token).",
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


# ---------------------------------------------------------------------------
# Command execution dispatch
# ---------------------------------------------------------------------------


def execute(args: argparse.Namespace) -> dict[str, Any]:
    """Run a project subcommand.

    Dispatches to the appropriate handler based on project_command.
    Returns a result dict compatible with the JSON envelope builder.
    """
    subcommand = getattr(args, "project_command", None)
    if subcommand is None:
        raise InvalidArgsError(
            "No project subcommand specified. "
            "Available: create, list, status, clean, remove, migrate."
        )

    handlers: dict[str, Any] = {
        "create": _execute_create,
        "list": _execute_list,
        "status": _execute_status,
        "clean": _execute_clean,
        "remove": _execute_remove,
        "migrate": _execute_migrate,
    }

    handler = handlers.get(subcommand)
    if handler is None:
        raise InvalidArgsError(f"Unknown project subcommand: {subcommand}")

    result: dict[str, Any] = handler(args)
    return result


# ---------------------------------------------------------------------------
# Project path resolution
# ---------------------------------------------------------------------------


def _resolve_project_path(project_name: str) -> str:
    """Resolve a project name to its workspace path.

    Also tries to resolve by UUID by scanning workspace directories.

    Args:
        project_name: Project name or UUID string.

    Returns:
        Absolute path to the project workspace directory.

    Raises:
        ProjectNotFoundError: If the project doesn't exist.
    """
    # First, try by name
    if workspace_exists(project_name):
        return str(get_project_path(project_name))

    # Try by UUID — scan all workspaces
    for ws_name in list_workspaces():
        ws_path = str(get_project_path(ws_name))
        try:
            manifest = load_manifest(ws_path)
            if manifest.get("id") == project_name:
                return ws_path
        except Exception:
            continue  # Skip corrupted manifests

    raise ProjectNotFoundError(project_name)


def _resolve_project_name(project_name_or_id: str) -> str:
    """Resolve a project name or UUID to the project's directory name.

    Returns the directory name used in the workspace root.
    """
    if workspace_exists(project_name_or_id):
        return project_name_or_id

    # Try UUID lookup
    for ws_name in list_workspaces():
        try:
            ws_path = str(get_project_path(ws_name))
            manifest = load_manifest(ws_path)
            if manifest.get("id") == project_name_or_id:
                return ws_name
        except Exception:
            continue

    raise ProjectNotFoundError(project_name_or_id)


# ---------------------------------------------------------------------------
# Project create
# ---------------------------------------------------------------------------


def _execute_create(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'project create' subcommand."""
    t_start = time.perf_counter()
    project_name = args.name
    dry_run = getattr(args, "dry_run", False)

    # Validate project name
    try:
        validate_project_name(project_name)
    except ValueError as e:
        raise InvalidArgsError(str(e)) from e

    # Check for duplicates
    if workspace_exists(project_name):
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "ERROR",
                    "message": f"Project '{project_name}' already exists.",
                    "category": "project",
                }
            ],
            "data": None,
        }

    # Dry-run: report plan without mutating
    if dry_run:
        project_dir_path = get_project_path(project_name)
        return {
            "success": True,
            "partial": False,
            "warnings": [],
            "diagnostics": [],
            "data": {
                "dry_run": True,
                "name": project_name,
                "directory": str(project_dir_path),
                "state": ProjectState.CREATED.value,
            },
        }

    # Create workspace + manifest
    project_dir_str = str(create_workspace(project_name))
    manifest = create_manifest(project_name)
    save_manifest(project_dir_str, manifest)

    # Record audit event
    duration_ms = int((time.perf_counter() - t_start) * 1000)
    write_audit_event(
        project_dir_str,
        command="project create",
        result=AuditResult.SUCCESS,
        duration_ms=duration_ms,
        args={"name": project_name},
        project_id=manifest["id"],
    )

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": {
            "id": manifest["id"],
            "name": project_name,
            "state": manifest["state"],
            "created_at": manifest["created_at"],
        },
    }


# ---------------------------------------------------------------------------
# Project list
# ---------------------------------------------------------------------------


def _execute_list(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'project list' subcommand with cursor-based pagination."""
    # Read limit from global args (consumed by argparse before subparser).
    limit = clamp_page_size(getattr(args, "limit", None))
    page_token_str: str | None = getattr(args, "page_token", None)

    # Collect all project names
    all_names = list_workspaces()

    # Decode cursor if present (opaque base64-encoded JSON with offset)
    start_index = 0
    if page_token_str:
        try:
            import base64

            cursor_data = json.loads(base64.urlsafe_b64decode(page_token_str.encode("ascii")))
            start_index = cursor_data.get("offset", 0)
        except Exception:
            raise InvalidArgsError("Invalid page_token value") from None

    # Slice for pagination
    total = len(all_names)
    page_names = all_names[start_index : start_index + limit]

    # Load manifests for each project in the page
    items: list[dict[str, Any]] = []
    for name in page_names:
        try:
            ws_path = str(get_project_path(name))
            manifest = load_manifest(ws_path)
            items.append(
                {
                    "id": manifest.get("id"),
                    "name": manifest.get("name", name),
                    "state": manifest.get("state"),
                    "created_at": manifest.get("created_at"),
                    "binary_count": manifest.get("binary_count", 0),
                    "is_stale": manifest.get("is_stale", False),
                }
            )
        except Exception:
            # Skip corrupted/missing projects in listing
            items.append(
                {
                    "name": name,
                    "state": "UNKNOWN",
                }
            )

    paginated = build_paginated_response(
        items=items,
        total=total,
        offset=start_index,
        limit=limit,
    )

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": paginated,
    }


def _encode_cursor(data: dict[str, Any]) -> str:
    """Encode a cursor dict as a base64-encoded JSON string (opaque cursor)."""
    import base64

    json_bytes = json.dumps(data).encode("utf-8")
    return base64.urlsafe_b64encode(json_bytes).decode("ascii")


def _decode_cursor(cursor_str: str) -> dict[str, Any]:
    """Decode a base64-encoded cursor string back to a dict."""
    import base64

    json_bytes = base64.urlsafe_b64decode(cursor_str.encode("ascii"))
    result: dict[str, Any] = json.loads(json_bytes)
    return result


# ---------------------------------------------------------------------------
# Project status
# ---------------------------------------------------------------------------


def _execute_status(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'project status' subcommand."""
    project_name = args.project
    project_path = _resolve_project_path(project_name)
    pw_name = _resolve_project_name(project_name)
    manifest = load_manifest(project_path)

    # Get lock information
    lock_holder = get_lock_holder(project_path)
    lock_info: dict[str, Any] | None = None
    if lock_holder:
        lock_info = {"holder": lock_holder}

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": {
            "id": manifest.get("id"),
            "name": manifest.get("name", pw_name),
            "state": manifest.get("state"),
            "binary_count": manifest.get("binary_count", 0),
            "created_at": manifest.get("created_at"),
            "updated_at": manifest.get("updated_at"),
            "workspace_version": manifest.get("workspace_version"),
            "is_stale": manifest.get("is_stale", False),
            "lock": lock_info,
            "description": manifest.get("description"),
        },
    }


# ---------------------------------------------------------------------------
# Project clean
# ---------------------------------------------------------------------------


def _execute_clean(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'project clean' subcommand.

    Resets a FAILED project back to CREATED state, clearing cache and
    diagnostics. Only operates on FAILED projects. Requires user
    confirmation unless --yes or --force is provided.
    """
    project_name = args.project
    yes = getattr(args, "yes", False)
    force = getattr(args, "force", False)
    skip_confirmation = yes or force

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    current_state_str = manifest.get("state", "")
    try:
        current_state = ProjectState(current_state_str)
    except ValueError:
        current_state = ProjectState.CREATED

    # Confirmation check (VAL-PROJ-009: must come before state validation)
    if not skip_confirmation:
        try:
            prompt = (
                f"This will reset project '{project_name}' from FAILED to CREATED, "
                f"clearing all cached data and diagnostics. Continue? [y/N]: "
            )
            print(prompt, file=sys.stderr, end="", flush=True)
            response = sys.stdin.readline().strip().lower()
            if response not in ("y", "yes"):
                return {
                    "success": False,
                    "partial": False,
                    "warnings": [],
                    "diagnostics": [
                        {
                            "severity": "INFO",
                            "message": "Clean operation cancelled by user.",
                            "category": "user",
                        }
                    ],
                    "data": None,
                }
        except (EOFError, KeyboardInterrupt):
            return {
                "success": False,
                "partial": False,
                "warnings": [],
                "diagnostics": [
                    {
                        "severity": "INFO",
                        "message": "Clean operation cancelled.",
                        "category": "user",
                    }
                ],
                "data": None,
            }

    # Only FAILED projects can be cleaned (validated after confirmation)
    if not can_clean(current_state):
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "ERROR",
                    "message": (
                        f"Clean is only allowed on FAILED projects. "
                        f"Current state: {current_state.value}. "
                        f"Use 'project remove' to delete this project."
                    ),
                    "category": "state_machine",
                }
            ],
            "data": None,
        }

    # Clear cache
    cache_clear(project_path)

    # Reset state to CREATED, clear diagnostics
    update_manifest_field(
        project_path,
        {
            "state": ProjectState.CREATED.value,
            "is_stale": False,
            "diagnostics": [],
        },
    )

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": {
            "name": manifest.get("name", project_name),
            "id": manifest.get("id"),
            "state": ProjectState.CREATED.value,
            "previous_state": current_state.value,
        },
    }


# ---------------------------------------------------------------------------
# Project remove
# ---------------------------------------------------------------------------


def _execute_remove(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'project remove' subcommand.

    Deletes the entire project workspace. Requires user confirmation
    unless --yes or --force is provided. Supports --dry-run for preview.
    """
    project_name = args.project
    yes = getattr(args, "yes", False)
    force = getattr(args, "force", False)
    dry_run = getattr(args, "dry_run", False)
    skip_confirmation = yes or force or dry_run

    pw_name = _resolve_project_name(project_name)
    project_path = str(get_project_path(pw_name))

    # Get paths that would be deleted
    paths_to_delete: list[str] = []
    try:
        subdirs = get_workspace_subdirs(pw_name)
        for _name, dir_path in sorted(subdirs.items()):
            paths_to_delete.append(str(dir_path))
    except Exception:
        paths_to_delete.append(project_path)

    # Dry-run: preview without deleting
    if dry_run:
        return {
            "success": True,
            "partial": False,
            "warnings": [],
            "diagnostics": [],
            "data": {
                "dry_run": True,
                "name": pw_name,
                "paths": paths_to_delete,
            },
        }

    # Confirmation check
    if not skip_confirmation:
        try:
            prompt = (
                f"This will permanently delete project '{pw_name}' "
                f"and all its contents ({len(paths_to_delete)} directories). "
                f"Continue? [y/N]: "
            )
            print(prompt, file=sys.stderr, end="", flush=True)
            response = sys.stdin.readline().strip().lower()
            if response not in ("y", "yes"):
                return {
                    "success": False,
                    "partial": False,
                    "warnings": [],
                    "diagnostics": [
                        {
                            "severity": "INFO",
                            "message": "Remove operation cancelled by user.",
                            "category": "user",
                        }
                    ],
                    "data": None,
                }
        except (EOFError, KeyboardInterrupt):
            return {
                "success": False,
                "partial": False,
                "warnings": [],
                "diagnostics": [
                    {
                        "severity": "INFO",
                        "message": "Remove operation cancelled.",
                        "category": "user",
                    }
                ],
                "data": None,
            }

    # Perform deletion
    remove_workspace(pw_name)

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": {
            "name": pw_name,
            "removed": True,
        },
    }


# ---------------------------------------------------------------------------
# Project migrate
# ---------------------------------------------------------------------------


def _execute_migrate(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the 'project migrate' subcommand.

    Supports --plan (show upgrade path), --apply (perform upgrade),
    and --dry-run (preview without mutation). Rejects migrate on locked
    projects.
    """
    project_name = args.project
    plan = getattr(args, "plan", False)
    apply_flag = getattr(args, "apply", False)
    dry_run = getattr(args, "dry_run", False)

    # --dry-run is equivalent to --plan for preview
    is_preview = plan or dry_run
    is_apply = apply_flag

    project_path = _resolve_project_path(project_name)
    manifest = load_manifest(project_path)

    current_version = manifest.get("workspace_version", "1")
    target_version = _WORKSPACE_VERSION

    # Read current state
    current_state_str = manifest.get("state", "")
    try:
        current_state = ProjectState(current_state_str)
    except ValueError:
        current_state = ProjectState.CREATED

    locked = is_locked(project_path)

    # Reject migrate on locked projects
    if is_apply and should_reject_migrate(current_state, locked):
        reason_parts = []
        if locked:
            reason_parts.append("project is currently locked")
        if current_state == ProjectState.ANALYZING:
            reason_parts.append("project is in ANALYZING state")
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "ERROR",
                    "message": (
                        f"Cannot migrate: {'; '.join(reason_parts)}. "
                        f"Wait for the operation to complete or release the lock."
                    ),
                    "category": "state_machine",
                }
            ],
            "data": None,
        }

    # Build migration steps
    if current_version == target_version:
        migration_steps: list[dict[str, str]] = []
        message = "Project is already at the latest workspace version."
    else:
        migration_steps = [
            {
                "from_version": current_version,
                "to_version": target_version,
                "description": f"Upgrade workspace from v{current_version} to v{target_version}",
            }
        ]
        message = f"Upgrade from v{current_version} to v{target_version} available."

    # Preview mode
    if is_preview:
        return {
            "success": True,
            "partial": False,
            "warnings": [],
            "diagnostics": [],
            "data": {
                "current_version": current_version,
                "target_version": target_version,
                "migration_steps": migration_steps,
                "message": message,
                "dry_run": True,
            },
        }

    # Apply migration
    if is_apply:
        if current_version == target_version:
            # Already at target — no-op success
            return {
                "success": True,
                "partial": False,
                "warnings": [],
                "diagnostics": [],
                "data": {
                    "current_version": current_version,
                    "target_version": target_version,
                    "migration_steps": migration_steps,
                    "applied": False,
                    "message": "Already at target version; no migration needed.",
                },
            }

        # Perform the upgrade
        update_manifest_field(project_path, {"workspace_version": target_version})
        return {
            "success": True,
            "partial": False,
            "warnings": [],
            "diagnostics": [],
            "data": {
                "current_version": target_version,
                "target_version": target_version,
                "migration_steps": migration_steps,
                "applied": True,
                "message": f"Migrated from v{current_version} to v{target_version}.",
            },
        }

    # Neither --plan, --dry-run, nor --apply specified — show error
    raise InvalidArgsError(
        "Migrate requires --plan, --apply, or --dry-run. "
        "Use --plan to preview the migration, --apply to perform it."
    )
