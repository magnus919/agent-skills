"""Workspace directory structure management.

Manages the hierarchical directory layout for each project workspace:
  project/
    project.json          # Project manifest
    binaries/<id>.json    # Binary metadata records
    samples/              # Copied binary samples
    audit/events.jsonl    # Append-only audit log
    reports/              # Generated reports
    exports/              # Export artifacts
    cache/                # Cached analysis data
    backend/ghidra/       # Ghidra-specific data

Also provides workspace root discovery via:
  BINARY_WORKSPACE_ROOT env var, or
  default XDG-compatible location (~/.local/share/binary-analysis/workspaces).
"""

from __future__ import annotations

import os
from pathlib import Path

# Workspace root can be configured via this environment variable
_WORKSPACE_ROOT_ENV = "BINARY_WORKSPACE_ROOT"

# Default workspace root (XDG-compatible)
_DEFAULT_WORKSPACE_ROOT = os.path.expanduser("~/.local/share/binary-analysis/workspaces")


def get_workspace_root() -> Path:
    """Return the root directory for all project workspaces.

    Resolution order:
    1. BINARY_WORKSPACE_ROOT environment variable
    2. Default XDG-compatible path (~/.local/share/binary-analysis/workspaces)

    Returns:
        Absolute path to the workspace root directory.
    """
    env_root = os.environ.get(_WORKSPACE_ROOT_ENV)
    if env_root:
        return Path(env_root).resolve()
    return Path(_DEFAULT_WORKSPACE_ROOT).resolve()


def ensure_workspace_root() -> Path:
    """Create and return the workspace root directory.

    Creates the directory if it doesn't exist, along with parent directories.

    Returns:
        Absolute path to the (now existing) workspace root directory.
    """
    root = get_workspace_root()
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_project_path(project_name: str) -> Path:
    """Return the workspace path for a named project.

    Args:
        project_name: The project name. Must be a valid directory name.

    Returns:
        Absolute path to the project's workspace directory.
    """
    root = get_workspace_root()
    return root / project_name


def create_workspace(project_name: str) -> Path:
    """Create a full project workspace directory structure.

    Creates the project root directory and all standard subdirectories.

    Args:
        project_name: The project name. Must be a valid directory name.

    Returns:
        Absolute path to the created project workspace root.

    Raises:
        FileExistsError: If the project workspace already exists.
        OSError: If directory creation fails.
    """
    project_dir = get_project_path(project_name)

    if project_dir.exists():
        raise FileExistsError(f"Project workspace already exists: {project_dir}")

    # Standard subdirectories per architecture
    subdirs = [
        "binaries",
        "samples",
        "audit",
        "reports",
        "exports",
        "cache",
        "backend/ghidra",
    ]

    # Create project root + all subdirectories
    project_dir.mkdir(parents=True, exist_ok=False)
    for subdir in subdirs:
        (project_dir / subdir).mkdir(parents=True, exist_ok=True)

    return project_dir


def remove_workspace(project_name: str) -> None:
    """Remove an entire project workspace directory.

    Deletes the project directory and all contents recursively.

    Args:
        project_name: The project name to remove.

    Raises:
        FileNotFoundError: If the project workspace does not exist.
    """
    import shutil

    project_dir = get_project_path(project_name)
    if not project_dir.exists():
        raise FileNotFoundError(f"Project workspace not found: {project_dir}")
    shutil.rmtree(str(project_dir))


def workspace_exists(project_name: str) -> bool:
    """Check if a project workspace directory exists.

    Args:
        project_name: The project name to check.

    Returns:
        True if the workspace directory exists.
    """
    return get_project_path(project_name).exists()


def list_workspaces() -> list[str]:
    """List all project workspace names in the workspace root.

    Returns:
        Sorted list of project directory names.
    """
    root = get_workspace_root()
    if not root.exists():
        return []
    entries = sorted(e.name for e in root.iterdir() if e.is_dir() and not e.name.startswith("."))
    return entries


def get_workspace_subdirs(project_name: str) -> dict[str, Path]:
    """Return paths to all standard subdirectories within a project workspace.

    Args:
        project_name: The project name.

    Returns:
        Dict mapping subdirectory names to absolute paths.

    Raises:
        FileNotFoundError: If the project workspace does not exist.
    """
    project_dir = get_project_path(project_name)
    if not project_dir.exists():
        raise FileNotFoundError(f"Project workspace not found: {project_dir}")

    return {
        "root": project_dir,
        "binaries": project_dir / "binaries",
        "samples": project_dir / "samples",
        "audit": project_dir / "audit",
        "reports": project_dir / "reports",
        "exports": project_dir / "exports",
        "cache": project_dir / "cache",
        "backend_ghidra": project_dir / "backend" / "ghidra",
    }


def validate_project_name(name: str) -> str:
    """Validate and sanitize a project name.

    Project names must:
    - Not be empty
    - Not contain path separators (/ or \\)
    - Not contain null bytes
    - Not start with a dot
    - Only contain alphanumeric characters, hyphens, and underscores

    Args:
        name: The proposed project name.

    Returns:
        The validated project name (unchanged if valid).

    Raises:
        ValueError: If the project name is invalid.
    """
    if not name or not name.strip():
        raise ValueError("Project name must not be empty")

    name = name.strip()

    if name in (".", ".."):
        raise ValueError(f"Invalid project name: {name}")

    if "\x00" in name:
        raise ValueError("Project name must not contain null bytes")

    if "/" in name or "\\" in name:
        raise ValueError("Project name must not contain path separators")

    if name.startswith("."):
        raise ValueError("Project name must not start with a dot")

    # Only allow alphanumeric, hyphens, and underscores
    invalid_chars = [c for c in name if not (c.isalnum() or c in "-_")]
    if invalid_chars:
        raise ValueError(
            f"Project name contains invalid characters: {''.join(invalid_chars)}. "
            "Only alphanumeric, hyphens, and underscores are allowed."
        )

    return name
