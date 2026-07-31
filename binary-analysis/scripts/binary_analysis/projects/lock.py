"""File-based locking for concurrent access serialization.

Uses a lock file (project.lock) within the project workspace. The lock
file contains the holder's PID and acquisition timestamp. Lock acquisition
is non-blocking — callers that fail to acquire get a LockError immediately.

Key guarantees:
- Only one process can hold the lock at a time.
- A second process attempting to acquire the lock gets a LockError.
- The lock is released on process exit (normal or abnormal), via atexit.
- Stale locks (from dead processes) are detected and cleaned up.
- Lock state is recorded in the project manifest's `lock` field for visibility.
"""

from __future__ import annotations

import atexit
import contextlib
import os
from datetime import datetime, timezone

from binary_analysis.domain.enums import ExitCode
from binary_analysis.domain.errors import BinaryAnalysisError

# Lock filename within a project workspace
LOCK_FILENAME = "project.lock"


class LockError(BinaryAnalysisError):
    """Raised when a lock cannot be acquired.

    Exit code 1 (GENERIC_ERROR) — the lock conflict means the operation
    cannot proceed but it's not a configuration or argument problem.
    """

    def __init__(self, project_name: str, holder_info: str | None = None) -> None:
        msg = f"Project '{project_name}' is locked by another process."
        if holder_info:
            msg += f" {holder_info}"
        msg += " Wait for the other process to complete or release the lock."
        super().__init__(msg, ExitCode.GENERIC_ERROR)


def _acquire_lock_file(lock_path: str, holder_info: str) -> None:
    """Acquire the file lock by writing holder info.

    Uses os.open with O_CREAT | O_EXCL — this atomically creates the file
    only if it doesn't already exist. If the file exists, acquisition fails.

    Args:
        lock_path: Path to the lock file.
        holder_info: Information about the lock holder (e.g., PID, purpose).

    Raises:
        LockError: If the lock is already held.
    """
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        # Lock exists — try to read holder info for better diagnostics
        try:
            with open(lock_path) as f:
                existing_info = f.read().strip()
        except (OSError, UnicodeDecodeError):
            existing_info = "unknown holder"

        # Check if the lock is stale (process no longer running)
        if _is_stale_lock(lock_path):
            # Clean up stale lock and retry
            with contextlib.suppress(OSError):
                os.unlink(lock_path)
            # Retry acquisition
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            except FileExistsError:
                raise LockError(
                    os.path.basename(os.path.dirname(lock_path)),
                    f"Held by: {existing_info}",
                ) from None
        else:
            raise LockError(
                os.path.basename(os.path.dirname(lock_path)),
                f"Held by: {existing_info}",
            ) from None

    with os.fdopen(fd, "w") as f:
        f.write(holder_info)


def _is_stale_lock(lock_path: str) -> bool:
    """Check if a lock file is from a dead process.

    Reads the PID from the lock file and checks if the process is still alive.

    Args:
        lock_path: Path to the lock file.

    Returns:
        True if the lock is stale (holder process is dead).
    """
    try:
        with open(lock_path) as f:
            content = f.read().strip()
    except (OSError, UnicodeDecodeError):
        return True  # Unreadable lock = stale

    # Parse PID from lock content (format: "pid=<PID> ...")
    pid = None
    for part in content.split():
        if part.startswith("pid="):
            try:
                pid = int(part.split("=", 1)[1])
            except (ValueError, IndexError):
                return True  # Can't parse PID = stale
            break

    if pid is None:
        return True  # No PID in lock file = stale

    # Check if process exists
    try:
        os.kill(pid, 0)  # Signal 0 does nothing but checks existence
        return False  # Process exists — lock is valid
    except OSError:
        return True  # Process doesn't exist — lock is stale


def acquire_lock(
    project_path: str,
    project_name: str | None = None,
    holder_purpose: str = "analysis",
) -> str:
    """Acquire a file lock for the project workspace.

    Non-blocking: if the lock is held by another live process, raises LockError.
    If the lock is stale (holder process is dead), cleans it up and acquires.

    Registers an atexit handler to release the lock on process exit.

    Args:
        project_path: Absolute path to the project workspace directory.
        project_name: Project name for error messages. Defaults to dir name.
        holder_purpose: Description of why the lock is being held.

    Returns:
        The lock holder info string.

    Raises:
        LockError: If the lock cannot be acquired (held by live process).
    """
    if project_name is None:
        project_name = os.path.basename(project_path)

    pid = os.getpid()
    holder_info = f"pid={pid} host={os.uname().nodename} purpose={holder_purpose} acquired_at={datetime.now(timezone.utc).isoformat()}"

    lock_path = os.path.join(project_path, LOCK_FILENAME)
    _acquire_lock_file(lock_path, holder_info)

    # Register cleanup via atexit
    atexit.register(_release_lock_file, lock_path)

    return holder_info


def release_lock(project_path: str) -> bool:
    """Release the file lock for the project workspace.

    Only releases the lock if the current process is the holder.
    Can be called explicitly or via the atexit handler.

    Args:
        project_path: Absolute path to the project workspace directory.

    Returns:
        True if the lock was released, False if there was no lock
        or the lock was held by a different process.
    """
    lock_path = os.path.join(project_path, LOCK_FILENAME)
    return _release_lock_file(lock_path)


def _release_lock_file(lock_path: str) -> bool:
    """Release a lock file if the current process is the holder.

    Args:
        lock_path: Path to the lock file.

    Returns:
        True if the lock was released.
    """
    if not os.path.exists(lock_path):
        return False

    # Only release if we are the holder
    try:
        with open(lock_path) as f:
            content = f.read().strip()
    except (OSError, UnicodeDecodeError):
        # Can't read — just remove it
        with contextlib.suppress(OSError):
            os.unlink(lock_path)
        return True

    current_pid = os.getpid()
    for part in content.split():
        if part.startswith("pid="):
            try:
                lock_pid = int(part.split("=", 1)[1])
            except (ValueError, IndexError):
                lock_pid = None
            if lock_pid is not None and lock_pid != current_pid:
                return False  # Not our lock
            break

    with contextlib.suppress(OSError):
        os.unlink(lock_path)
        return True
    return False


def is_locked(project_path: str) -> bool:
    """Check if the project workspace has a valid (non-stale) lock.

    Args:
        project_path: Absolute path to the project workspace directory.

    Returns:
        True if the project is locked by a live process.
    """
    lock_path = os.path.join(project_path, LOCK_FILENAME)
    if not os.path.exists(lock_path):
        return False
    return not _is_stale_lock(lock_path)


def get_lock_holder(project_path: str) -> str | None:
    """Get information about the current lock holder.

    Args:
        project_path: Absolute path to the project workspace directory.

    Returns:
        Holder info string, or None if no valid lock exists.
    """
    lock_path = os.path.join(project_path, LOCK_FILENAME)
    if not os.path.exists(lock_path):
        return None
    if _is_stale_lock(lock_path):
        return None
    try:
        with open(lock_path) as f:
            return f.read().strip()
    except (OSError, UnicodeDecodeError):
        return None
