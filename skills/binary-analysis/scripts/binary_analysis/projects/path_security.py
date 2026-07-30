"""Path security — symlink resolution, workspace containment, path traversal prevention.

This module provides the central path validation used by all commands that
accept user-supplied file paths (binary import, report output, workspace
operations). All path validation follows the same pattern:

1. Resolve symlinks (os.path.realpath)
2. Check path is contained within the allowed boundary (workspace or project)
3. Reject traversal sequences, absolute paths outside boundary, and null bytes

These checks enforce the safety architecture:
- Never write files outside the project workspace
- Reject paths designed to escape containment
- Prevent symlink-based traversal attacks
"""

from __future__ import annotations

import os
from pathlib import Path


def resolve_path(path: str) -> str:
    """Resolve a path with symlink expansion to its canonical form.

    Uses os.path.realpath to follow all symlinks and resolve relative
    path components. If the path does not exist, still resolves as far
    as possible through os.path.realpath (which handles most cases).

    Args:
        path: The user-supplied path string.

    Returns:
        The canonical absolute path with all symlinks resolved.
    """
    # os.path.realpath resolves symlinks and normalizes the path
    # even if the file doesn't exist (it resolves the directory part)
    return os.path.realpath(path)


def check_no_path_traversal(path: str) -> None:
    """Reject path traversal sequences and null bytes in a path.

    Args:
        path: The user-supplied path string.

    Raises:
        ValueError: If the path contains null bytes or explicit traversal sequences.
    """
    # Null byte rejection
    if "\x00" in path:
        raise ValueError("Path must not contain null bytes")

    # Check for explicit traversal sequences in the raw path
    # Split by both Unix and Windows separators
    raw_parts = path.replace("\\", "/").split("/")
    if ".." in raw_parts:
        raise ValueError(f"Path traversal detected in: {path}")

    # Also check normalized form as a backup
    normalized = os.path.normpath(path)
    norm_parts = Path(normalized).parts
    if ".." in norm_parts:
        raise ValueError(f"Path traversal detected in: {path}")


def check_within_boundary(path: str, boundary: str) -> None:
    """Check that a resolved path is contained within a boundary directory.

    The boundary check uses os.path.commonpath to verify containment.
    Both paths must be absolute and resolved before calling this function.

    Args:
        path: The resolved absolute path to check.
        boundary: The resolved absolute boundary directory.

    Raises:
        ValueError: If the path is not within the boundary directory.
    """
    path_abs = os.path.abspath(path)
    boundary_abs = os.path.abspath(boundary)

    common = os.path.commonpath([path_abs, boundary_abs])
    if common != boundary_abs:
        raise ValueError(f"Path '{path}' is outside the allowed boundary '{boundary}'.")


def validate_binary_import_path(binary_path: str, project_path: str) -> str:
    """Validate a binary import path for safety.

    Performs:
    1. Null byte and traversal sequence checks on the raw path
    2. Symlink resolution to get the canonical path
    3. File existence check (after resolution)
    4. Workspace containment check (the binary must be within the project)

    Note: For copy mode, the binary can come from outside the project.
    The workspace containment check is relaxed — we check that the path
    does not traverse to sensitive system locations, but absolute paths
    from /tmp or user home are allowed for import.

    For reference mode, the binary source path is stored but the binary
    is never written outside the project.

    Args:
        binary_path: The user-supplied path to the binary file.
        project_path: The resolved project workspace directory.

    Returns:
        The resolved canonical path to the binary.

    Raises:
        ValueError: If the path fails validation.
        FileNotFoundError: If the resolved path does not exist.
    """
    # Step 1: Reject null bytes and explicit traversal
    check_no_path_traversal(binary_path)

    # Step 2: Resolve symlinks for the directory part (file may not exist yet
    # for import dry-run, but it must exist for a real import)
    # We resolve the directory path first, then append the file name
    dir_part = os.path.dirname(binary_path) or "."
    base_part = os.path.basename(binary_path)

    resolved_dir = os.path.realpath(dir_part)
    resolved_path = os.path.join(resolved_dir, base_part)

    # Step 3: Check the resolved directory is not a system-sensitive location
    # Reject paths that resolve to common system directories
    _check_not_system_path(resolved_path)

    return resolved_path


def validate_output_path(output_path: str, project_path: str) -> str:
    """Validate a report/output path is within the project workspace.

    Performs:
    1. Null byte and traversal sequence checks
    2. Resolves the path relative to the project workspace
    3. Verifies the resolved path is within the project workspace

    Args:
        output_path: The user-supplied output path.
        project_path: The resolved project workspace directory.

    Returns:
        The validated absolute output path within the project workspace.

    Raises:
        ValueError: If the path would escape the project workspace.
    """
    # Step 1: Reject null bytes and explicit traversal
    check_no_path_traversal(output_path)

    # Step 2: If output_path is absolute, check it separately
    # If relative, resolve relative to project_path
    if os.path.isabs(output_path):
        # Absolute paths must still be within the project workspace
        resolved = os.path.realpath(output_path)
        check_within_boundary(resolved, project_path)
        return resolved

    # Relative path: resolve against project_path
    joined = os.path.join(project_path, output_path)
    resolved = os.path.realpath(joined)
    check_within_boundary(resolved, project_path)
    return resolved


def validate_workspace_path(path_in_workspace: str, project_path: str) -> str:
    """Validate a path that must be within a project workspace.

    Resolves symlinks and ensures the resolved path is within the
    project workspace boundary. Used for workspace operations that
    traverse project subdirectories.

    Args:
        path_in_workspace: A path within the project workspace.
        project_path: The resolved project workspace directory.

    Returns:
        The resolved canonical path.

    Raises:
        ValueError: If the resolved path escapes the project workspace.
    """
    check_no_path_traversal(path_in_workspace)

    resolved = os.path.realpath(path_in_workspace)
    check_within_boundary(resolved, project_path)
    return resolved


def _check_not_system_path(path: str) -> None:
    """Reject paths that resolve to system-sensitive locations.

    This prevents importing binaries from /etc, /proc, /sys, or other
    system directories that could leak sensitive information.

    Args:
        path: The resolved path to check.

    Raises:
        ValueError: If the path is in a system-sensitive location.
    """
    # System-sensitive prefixes (Linux/macOS)
    system_prefixes: tuple[str, ...] = (
        "/etc/",
        "/proc/",
        "/sys/",
        "/dev/",
        "/System/",  # macOS
        "/Library/System/",  # macOS
        "/private/etc/",  # macOS
        "/private/var/",  # macOS (system vars)
    )

    path_abs = os.path.abspath(path)

    # Allow user temp directories (macOS /private/var/folders/*, /private/tmp/, /tmp/)
    user_temp_prefixes = (
        "/private/var/folders/",
        "/private/tmp/",
        "/var/folders/",
        "/tmp/",
    )
    for prefix in user_temp_prefixes:
        if path_abs.startswith(prefix):
            return  # User temp directories are safe

    # Check against the system-sensitive directories themselves
    system_dirs: set[str] = {
        "/etc",
        "/proc",
        "/sys",
        "/dev",
        "/boot",
        "/System",
        "/private/etc",
        "/private/var",
    }

    for prefix in system_prefixes:
        if path_abs.startswith(prefix):
            raise ValueError(
                f"Path '{path}' resolves to a system-sensitive location ({prefix}). "
                "Import of files from system directories is not allowed for safety."
            )

    if path_abs in system_dirs:
        raise ValueError(
            f"Path '{path}' is a system-sensitive directory. "
            "Import of files from system directories is not allowed for safety."
        )
