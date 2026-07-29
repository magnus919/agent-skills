"""Tests for the workspace directory structure management (projects/workspace.py).

Validates that:
- Workspace root discovery with env var and default fallback.
- Project workspace creation produces all required subdirectories.
- Workspace removal deletes everything recursively.
- Workspace existence checks and listing work correctly.
- Subdirectory path resolution returns correct paths.
- Project name validation rejects invalid characters.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from binary_analysis.projects.workspace import (
    create_workspace,
    get_project_path,
    get_workspace_root,
    get_workspace_subdirs,
    list_workspaces,
    remove_workspace,
    validate_project_name,
    workspace_exists,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_workspace_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Fixture: redirect workspace root to a temp directory."""
    monkeypatch.setenv("BINARY_WORKSPACE_ROOT", str(tmp_path))
    return tmp_path


# ---------------------------------------------------------------------------
# Workspace root
# ---------------------------------------------------------------------------


class TestWorkspaceRoot:
    """Tests for get_workspace_root and env var resolution."""

    def test_env_var_resolution(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """BINARY_WORKSPACE_ROOT env var takes precedence."""
        custom = tmp_path / "custom-workspaces"
        monkeypatch.setenv("BINARY_WORKSPACE_ROOT", str(custom))
        root = get_workspace_root()
        assert root == custom.resolve()

    def test_default_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without env var, falls back to XDG default."""
        monkeypatch.delenv("BINARY_WORKSPACE_ROOT", raising=False)
        root = get_workspace_root()
        assert ".local/share/binary-analysis/workspaces" in str(root)


# ---------------------------------------------------------------------------
# Project workspace creation
# ---------------------------------------------------------------------------


class TestCreateWorkspace:
    """Tests for create_workspace."""

    def test_creates_all_subdirectories(self, temp_workspace_root: Path) -> None:
        """Creating a workspace produces all required subdirectories."""
        project_dir = create_workspace("my-project")
        assert project_dir.exists()
        assert (project_dir / "binaries").is_dir()
        assert (project_dir / "samples").is_dir()
        assert (project_dir / "audit").is_dir()
        assert (project_dir / "reports").is_dir()
        assert (project_dir / "exports").is_dir()
        assert (project_dir / "cache").is_dir()
        assert (project_dir / "backend" / "ghidra").is_dir()

    def test_creates_project_root_directory(self, temp_workspace_root: Path) -> None:
        """The project root directory exists after creation."""
        create_workspace("test-proj")
        assert (temp_workspace_root / "test-proj").is_dir()

    def test_different_project_names(self, temp_workspace_root: Path) -> None:
        """Multiple projects can be created in the same root."""
        create_workspace("project-a")
        create_workspace("project-b")
        assert workspace_exists("project-a")
        assert workspace_exists("project-b")
        assert (temp_workspace_root / "project-a") != (temp_workspace_root / "project-b")

    def test_rejects_duplicate_names(self, temp_workspace_root: Path) -> None:
        """Creating a project with an existing name raises FileExistsError."""
        create_workspace("my-project")
        with pytest.raises(FileExistsError, match="already exists"):
            create_workspace("my-project")

    def test_get_project_path(self, temp_workspace_root: Path) -> None:
        """get_project_path returns the correct path."""
        path = get_project_path("my-project")
        assert path == temp_workspace_root / "my-project"


# ---------------------------------------------------------------------------
# Workspace removal
# ---------------------------------------------------------------------------


class TestRemoveWorkspace:
    """Tests for remove_workspace."""

    def test_removes_directory_and_contents(self, temp_workspace_root: Path) -> None:
        """Removing a workspace deletes the entire directory tree."""
        create_workspace("to-remove")
        # Create some files inside
        (temp_workspace_root / "to-remove" / "project.json").write_text("{}")
        (temp_workspace_root / "to-remove" / "audit" / "events.jsonl").write_text("line1\n")

        assert workspace_exists("to-remove")
        remove_workspace("to-remove")
        assert not workspace_exists("to-remove")

    def test_nonexistent_project_raises(self, temp_workspace_root: Path) -> None:
        """Removing a nonexistent project raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            remove_workspace("nonexistent")


# ---------------------------------------------------------------------------
# Workspace existence and listing
# ---------------------------------------------------------------------------


class TestWorkspaceExists:
    """Tests for workspace_exists."""

    def test_exists_after_creation(self, temp_workspace_root: Path) -> None:
        """Workspace exists after creation."""
        assert not workspace_exists("my-project")
        create_workspace("my-project")
        assert workspace_exists("my-project")

    def test_not_exists_after_removal(self, temp_workspace_root: Path) -> None:
        """Workspace does not exist after removal."""
        create_workspace("my-project")
        remove_workspace("my-project")
        assert not workspace_exists("my-project")


class TestListWorkspaces:
    """Tests for list_workspaces."""

    def test_empty_workspace_root(self, temp_workspace_root: Path) -> None:
        """Empty workspace root returns empty list."""
        assert list_workspaces() == []

    def test_lists_created_projects(self, temp_workspace_root: Path) -> None:
        """Lists all created project names sorted."""
        create_workspace("zzz")
        create_workspace("aaa")
        assert list_workspaces() == ["aaa", "zzz"]

    def test_skips_dot_directories(self, temp_workspace_root: Path) -> None:
        """Dot-directories are excluded from listings."""
        create_workspace("my-project")
        (temp_workspace_root / ".hidden").mkdir(exist_ok=True)
        projects = list_workspaces()
        assert "my-project" in projects
        assert ".hidden" not in projects

    def test_skips_files(self, temp_workspace_root: Path) -> None:
        """Regular files are excluded from listings."""
        create_workspace("my-project")
        (temp_workspace_root / "not-a-dir.txt").write_text("hello")
        projects = list_workspaces()
        assert "my-project" in projects
        assert "not-a-dir.txt" not in projects


# ---------------------------------------------------------------------------
# Subdirectory resolution
# ---------------------------------------------------------------------------


class TestGetWorkspaceSubdirs:
    """Tests for get_workspace_subdirs."""

    def test_all_subdirs_present(self, temp_workspace_root: Path) -> None:
        """All standard subdirectories are returned."""
        create_workspace("my-project")
        subdirs = get_workspace_subdirs("my-project")
        expected_keys = {
            "root",
            "binaries",
            "samples",
            "audit",
            "reports",
            "exports",
            "cache",
            "backend_ghidra",
        }
        assert set(subdirs.keys()) == expected_keys
        for path in subdirs.values():
            assert path.exists()

    def test_nonexistent_project_raises(self, temp_workspace_root: Path) -> None:
        """Subdir lookup on nonexistent project raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            get_workspace_subdirs("nonexistent")


# ---------------------------------------------------------------------------
# Project name validation
# ---------------------------------------------------------------------------


class TestValidateProjectName:
    """Tests for validate_project_name."""

    def test_valid_names(self) -> None:
        """Various valid project names are accepted."""
        valid_names = [
            "my-project",
            "project_123",
            "a",
            "my_analysis",
            "test-project-v2",
            "123project",
        ]
        for name in valid_names:
            assert validate_project_name(name) == name

    def test_empty_name_raises(self) -> None:
        """Empty or whitespace-only names are rejected."""
        with pytest.raises(ValueError, match="must not be empty"):
            validate_project_name("")
        with pytest.raises(ValueError, match="must not be empty"):
            validate_project_name("   ")

    def test_null_bytes_raises(self) -> None:
        """Names containing null bytes are rejected."""
        with pytest.raises(ValueError, match="null bytes"):
            validate_project_name("bad\x00name")

    def test_path_separators_raises(self) -> None:
        """Names containing path separators are rejected."""
        for sep in ["/", "\\"]:
            with pytest.raises(ValueError, match="path separators"):
                validate_project_name(f"evil{sep}name")

    def test_dot_prefix_raises(self) -> None:
        """Names starting with a dot are rejected."""
        with pytest.raises(ValueError, match="dot"):
            validate_project_name(".hidden")

    def test_dot_and_dotdot_raises(self) -> None:
        """The names . and .. are rejected."""
        with pytest.raises(ValueError, match="Invalid project name"):
            validate_project_name(".")
        with pytest.raises(ValueError, match="Invalid project name"):
            validate_project_name("..")

    def test_invalid_characters_raises(self) -> None:
        """Names with special characters are rejected."""
        invalid_names = [
            "my project",  # space
            "proj$",  # dollar sign
            "proj@test",  # at sign
            "proj!",  # exclamation
            "proj#",  # hash
            "proj%",  # percent
        ]
        for name in invalid_names:
            with pytest.raises(ValueError, match="invalid characters"):
                validate_project_name(name)

    def test_absolute_path_rejected(self, temp_workspace_root: Path) -> None:
        """Absolute paths as project names are rejected."""
        with pytest.raises(ValueError, match="path separators"):
            validate_project_name("/etc/passwd")

    def test_dotdot_traversal_rejected(self) -> None:
        """Directory traversal via .. is rejected."""
        with pytest.raises(ValueError, match="path separators"):
            validate_project_name("../escape")
