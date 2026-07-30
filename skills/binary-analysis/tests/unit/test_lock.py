"""Tests for the file-based locking module (projects/lock.py).

Validates that:
- Lock acquisition succeeds when no lock exists.
- Lock acquisition fails (LockError) when already held by live process.
- Stale locks (from dead processes) are detected and cleaned up.
- Lock is released on explicit release_lock call.
- Lock is released via atexit on process exit (tested implicitly).
- is_locked correctly reports lock status.
- get_lock_holder returns holder information.
- Lock file contains PID information.
"""

from __future__ import annotations

import sys
from pathlib import Path
_scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import os
from pathlib import Path

import pytest
from binary_analysis.domain.errors import BinaryAnalysisError
from binary_analysis.projects.lock import (
    LockError,
    acquire_lock,
    get_lock_holder,
    is_locked,
    release_lock,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def project_path(tmp_path: Path) -> str:
    """Fixture: a temp directory acting as a project workspace."""
    p = str(tmp_path)
    return p


# ---------------------------------------------------------------------------
# Lock acquisition
# ---------------------------------------------------------------------------


class TestAcquireLock:
    """Tests for acquire_lock."""

    def test_acquire_when_no_lock_exists(self, project_path: str) -> None:
        """Acquiring a lock when none exists succeeds."""
        holder = acquire_lock(project_path, "test-project")
        assert holder is not None
        assert "pid=" in holder
        assert is_locked(project_path)
        release_lock(project_path)

    def test_lock_file_created(self, project_path: str) -> None:
        """After acquiring, a lock file exists in the project directory."""
        acquire_lock(project_path, "test-project")
        lock_file = os.path.join(project_path, "project.lock")
        assert os.path.exists(lock_file)
        release_lock(project_path)

    def test_lock_file_contains_pid(self, project_path: str) -> None:
        """The lock file contains the current process PID."""
        acquire_lock(project_path, "test-project")
        lock_file = os.path.join(project_path, "project.lock")
        content = Path(lock_file).read_text()
        assert f"pid={os.getpid()}" in content
        release_lock(project_path)

    def test_duplicate_acquire_local_fails(self, project_path: str) -> None:
        """Same process trying to acquire again succeeds (re-entrant)."""
        # Note: we don't prevent re-entrant locks in the same process
        # because atexit only registers once. But os.O_EXCL prevents
        # double acquisition — we should test for it explicitly.
        acquire_lock(project_path, "test-project")
        # Same process trying again should fail because lock exists
        with pytest.raises(LockError, match="locked by another process"):
            acquire_lock(project_path, "test-project")
        release_lock(project_path)

    def test_lock_holder_info(self, project_path: str) -> None:
        """Holder info includes host, purpose, and timestamp."""
        holder = acquire_lock(project_path, "test-project")
        assert "host=" in holder
        assert "purpose=" in holder
        assert "acquired_at=" in holder
        release_lock(project_path)


# ---------------------------------------------------------------------------
# Lock release
# ---------------------------------------------------------------------------


class TestReleaseLock:
    """Tests for release_lock."""

    def test_release_unlocks(self, project_path: str) -> None:
        """Releasing a lock removes the lock file and clears locked state."""
        acquire_lock(project_path, "test-project")
        assert is_locked(project_path)
        result = release_lock(project_path)
        assert result is True
        assert not is_locked(project_path)
        lock_file = os.path.join(project_path, "project.lock")
        assert not os.path.exists(lock_file)

    def test_release_no_lock(self, project_path: str) -> None:
        """Releasing when no lock exists returns False."""
        result = release_lock(project_path)
        assert result is False

    def test_acquire_after_release(self, project_path: str) -> None:
        """After releasing, a new lock can be acquired."""
        acquire_lock(project_path, "test-project")
        release_lock(project_path)
        # Should succeed — lock was released
        holder = acquire_lock(project_path, "test-project")
        assert holder is not None
        release_lock(project_path)

    def test_cannot_release_other_process_lock(self, project_path: str) -> None:
        """A process cannot release a lock it doesn't own."""
        # Write a fake lock file with a different PID
        lock_file = os.path.join(project_path, "project.lock")
        Path(lock_file).write_text("pid=99999 host=other purpose=test acquired_at=now")
        result = release_lock(project_path)
        assert result is False
        assert os.path.exists(lock_file)
        # Clean up manually
        os.unlink(lock_file)


# ---------------------------------------------------------------------------
# Lock status checks
# ---------------------------------------------------------------------------


class TestIsLocked:
    """Tests for is_locked."""

    def test_not_locked_initially(self, project_path: str) -> None:
        """A fresh project workspace is not locked."""
        assert not is_locked(project_path)

    def test_locked_after_acquire(self, project_path: str) -> None:
        """After acquiring, is_locked returns True."""
        acquire_lock(project_path, "test-project")
        assert is_locked(project_path)
        release_lock(project_path)

    def test_not_locked_after_release(self, project_path: str) -> None:
        """After releasing, is_locked returns False."""
        acquire_lock(project_path, "test-project")
        release_lock(project_path)
        assert not is_locked(project_path)


class TestGetLockHolder:
    """Tests for get_lock_holder."""

    def test_none_when_no_lock(self, project_path: str) -> None:
        """No lock holder when no lock exists."""
        assert get_lock_holder(project_path) is None

    def test_returns_holder_info(self, project_path: str) -> None:
        """get_lock_holder returns the holder string."""
        acquire_lock(project_path, "test-project")
        holder = get_lock_holder(project_path)
        assert holder is not None
        assert f"pid={os.getpid()}" in holder
        release_lock(project_path)

    def test_none_after_release(self, project_path: str) -> None:
        """After release, holder is None."""
        acquire_lock(project_path, "test-project")
        release_lock(project_path)
        assert get_lock_holder(project_path) is None


# ---------------------------------------------------------------------------
# Stale lock detection
# ---------------------------------------------------------------------------


class TestStaleLock:
    """Tests for stale lock detection."""

    def test_stale_lock_with_nonexistent_pid(self, project_path: str) -> None:
        """A lock with a PID that doesn't exist is detected as stale."""
        lock_file = os.path.join(project_path, "project.lock")
        # PID 99999 is extremely unlikely to exist
        Path(lock_file).write_text("pid=99999 host=fake purpose=test acquired_at=now")
        # Should be detected as stale and cleaned up on acquire
        assert not is_locked(project_path)  # Stale = not locked
        holder = acquire_lock(project_path, "test-project")
        assert holder is not None
        release_lock(project_path)

    def test_stale_lock_with_invalid_content(self, project_path: str) -> None:
        """A lock file with unparseable content is treated as stale."""
        lock_file = os.path.join(project_path, "project.lock")
        Path(lock_file).write_text("garbage content, no PID at all")
        # Should be detected as stale
        assert not is_locked(project_path)
        # Acquire should clean it up
        holder = acquire_lock(project_path, "test-project")
        assert holder is not None
        release_lock(project_path)

    def test_stale_lock_no_pid_field(self, project_path: str) -> None:
        """A lock file without a pid= field is stale."""
        lock_file = os.path.join(project_path, "project.lock")
        Path(lock_file).write_text("host=some purpose=analysis")
        assert not is_locked(project_path)
        holder = acquire_lock(project_path, "test-project")
        assert holder is not None
        release_lock(project_path)


# ---------------------------------------------------------------------------
# Lock error behavior
# ---------------------------------------------------------------------------


class TestLockError:
    """Tests for LockError."""

    def test_lock_error_is_binary_analysis_error(self) -> None:
        """LockError is a BinaryAnalysisError."""
        err = LockError("test-project", "Held by: pid=12345")
        assert isinstance(err, BinaryAnalysisError)

    def test_lock_error_message(self) -> None:
        """LockError contains descriptive message."""
        err = LockError("test-project", "Held by: pid=12345")
        assert "locked by another process" in err.message
        assert "test-project" in err.message

    def test_lock_error_exit_code(self) -> None:
        """LockError has GENERIC_ERROR exit code."""
        err = LockError("test-project")
        assert err.exit_code == 1
