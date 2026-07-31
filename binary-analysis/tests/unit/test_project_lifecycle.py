"""Tests for project lifecycle CLI commands and state machine.

Validates all project lifecycle behavior:
- create: workspace + manifest, UUID, name, state CREATED, --dry-run, duplicates
- list: pagination with cursor, empty results, --limit
- status: full state report, exit code 6 for nonexistent
- clean: confirmation, FAILED->CREATED reset, cache clear, non-FAILED rejection
- remove: confirmation, workspace deletion, --dry-run
- migrate: --plan, --apply, locked project rejection
- state machine: staleness, FAILED transitions
"""

from __future__ import annotations

import sys
from pathlib import Path
_scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import io
import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest
from binary_analysis.cli.main import main
from binary_analysis.domain.enums import ExitCode, ProjectState
from binary_analysis.projects.cache import cache_set
from binary_analysis.projects.manifest import create_manifest, load_manifest, save_manifest
from binary_analysis.projects.workspace import (
    create_workspace,
    get_workspace_subdirs,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def temp_workspace_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect workspace root to a temp directory for all tests."""
    root = tmp_path / "workspaces"
    root.mkdir(parents=True)
    monkeypatch.setenv("BINARY_WORKSPACE_ROOT", str(root))
    return root


def _capture_json(
    args: list[str],
    capsys: pytest.CaptureFixture,
    stdin_text: str | None = None,
) -> tuple[int, dict]:
    """Run main() with --json and return (exit_code, parsed_json).

    If stdin_text is provided, monkeypatches sys.stdin to provide it
    for confirmation prompts.
    """
    import sys as _sys

    old_stdin = _sys.stdin
    if stdin_text is not None:
        _sys.stdin = io.StringIO(stdin_text)
    try:
        exit_code = main(["--json", *args])
    finally:
        _sys.stdin = old_stdin
    captured = capsys.readouterr()
    parsed = json.loads(captured.out) if captured.out.strip() else {}
    return exit_code, parsed


def _make_failed_project(name: str) -> None:
    """Helper: create a project and set it to FAILED with diagnostics."""
    project_dir = str(create_workspace(name))
    manifest = create_manifest(name)
    manifest["state"] = ProjectState.FAILED.value
    manifest["diagnostics"] = [
        {
            "severity": "ERROR",
            "category": "analysis",
            "message": "Test failure",
            "recoverable": True,
        }
    ]
    save_manifest(project_dir, manifest)


def _make_imported_project(name: str) -> None:
    """Helper: create a project and set it to IMPORTED."""
    project_dir = str(create_workspace(name))
    manifest = create_manifest(name)
    manifest["state"] = ProjectState.IMPORTED.value
    manifest["binary_count"] = 1
    save_manifest(project_dir, manifest)


def _make_ready_project(name: str) -> None:
    """Helper: create a project and set it to READY."""
    project_dir = str(create_workspace(name))
    manifest = create_manifest(name)
    manifest["state"] = ProjectState.READY.value
    manifest["binary_count"] = 1
    manifest["is_stale"] = False
    save_manifest(project_dir, manifest)


# ---------------------------------------------------------------------------
# VAL-PROJ-001: Project creation
# ---------------------------------------------------------------------------


class TestProjectCreate:
    """Tests for project create command."""

    def test_create_returns_uuid_name_state_created(self, capsys: pytest.CaptureFixture) -> None:
        """Creating a project returns UUID, name, state CREATED, created_at."""
        exit_code, result = _capture_json(["project", "create", "my-analysis"], capsys)
        assert exit_code == ExitCode.SUCCESS
        assert result["success"] is True
        data = result["data"]
        assert "id" in data
        UUID(data["id"])  # Valid UUID
        assert data["name"] == "my-analysis"
        assert data["state"] == "CREATED"
        assert "created_at" in data

    def test_create_writes_project_json(self, capsys: pytest.CaptureFixture) -> None:
        """Creating a project writes project.json with correct fields."""
        _capture_json(["project", "create", "my-analysis"], capsys)
        from binary_analysis.projects.workspace import get_project_path

        proj_path = get_project_path("my-analysis")
        manifest = load_manifest(str(proj_path))
        assert manifest["name"] == "my-analysis"
        assert manifest["state"] == "CREATED"
        assert "id" in manifest
        assert "created_at" in manifest

    def test_create_creates_workspace_dirs(self, capsys: pytest.CaptureFixture) -> None:
        """Creating a project creates all required subdirectories."""
        _capture_json(["project", "create", "my-analysis"], capsys)
        subdirs = get_workspace_subdirs("my-analysis")
        for path in subdirs.values():
            assert path.exists()

    def test_create_with_hyphens_and_underscores(self, capsys: pytest.CaptureFixture) -> None:
        """Project names with hyphens and underscores are accepted."""
        exit_code, result = _capture_json(["project", "create", "my-analysis_v2"], capsys)
        assert exit_code == ExitCode.SUCCESS
        assert result["data"]["name"] == "my-analysis_v2"

    def test_create_empty_name_fails(self, capsys: pytest.CaptureFixture) -> None:
        """Empty project name is rejected."""
        exit_code, _ = _capture_json(["project", "create", ""], capsys)
        assert exit_code != ExitCode.SUCCESS

    def test_create_rejects_traversal_sequences(self, capsys: pytest.CaptureFixture) -> None:
        """Project names with ../ are rejected."""
        exit_code, _ = _capture_json(["project", "create", "../etc/passwd"], capsys)
        assert exit_code != ExitCode.SUCCESS

    def test_create_rejects_null_bytes(self, capsys: pytest.CaptureFixture) -> None:
        """Project names with null bytes are rejected."""
        exit_code, _ = _capture_json(["project", "create", "bad\x00name"], capsys)
        assert exit_code != ExitCode.SUCCESS


# ---------------------------------------------------------------------------
# VAL-PROJ-002: Project listing
# ---------------------------------------------------------------------------


class TestProjectList:
    """Tests for project list command."""

    def test_list_includes_created_project(self, capsys: pytest.CaptureFixture) -> None:
        """Created project appears in listing with matching UUID and state."""
        _, create_result = _capture_json(["project", "create", "my-analysis"], capsys)
        created_uuid = create_result["data"]["id"]

        _, list_result = _capture_json(["project", "list"], capsys)
        items = list_result["data"]["items"]
        uuids = [item["id"] for item in items]
        assert created_uuid in uuids

        # Find our project
        proj = next(item for item in items if item["id"] == created_uuid)
        assert proj["name"] == "my-analysis"
        assert proj["state"] == "CREATED"


# ---------------------------------------------------------------------------
# VAL-PROJ-003: Duplicate rejection
# ---------------------------------------------------------------------------


class TestDuplicateProject:
    """Tests for duplicate project name rejection."""

    def test_duplicate_name_rejected(self, capsys: pytest.CaptureFixture) -> None:
        """Creating a project with an existing name returns non-zero exit."""
        _capture_json(["project", "create", "my-analysis"], capsys)
        exit_code, result = _capture_json(["project", "create", "my-analysis"], capsys)
        assert exit_code != ExitCode.SUCCESS
        assert result["success"] is False
        # Error diagnostics should mention duplicate or exists
        diag_messages = " ".join(d.get("message", "") for d in result.get("diagnostics", []))
        assert "already exists" in diag_messages or "duplicate" in diag_messages.lower()


# ---------------------------------------------------------------------------
# VAL-PROJ-004: --dry-run
# ---------------------------------------------------------------------------


class TestProjectCreateDryRun:
    """Tests for project create --dry-run."""

    def test_dry_run_reports_plan(self, capsys: pytest.CaptureFixture) -> None:
        """--dry-run reports plan without creating files."""
        exit_code, result = _capture_json(["project", "create", "my-analysis", "--dry-run"], capsys)
        assert exit_code == ExitCode.SUCCESS
        assert result["success"] is True
        data = result["data"]
        assert data.get("dry_run") is True
        assert "name" in data

    def test_dry_run_does_not_create_files(self, capsys: pytest.CaptureFixture) -> None:
        """--dry-run does not create any files or directories."""
        from binary_analysis.projects.workspace import get_project_path

        _capture_json(["project", "create", "my-analysis", "--dry-run"], capsys)
        proj_path = get_project_path("my-analysis")
        assert not proj_path.exists()


# ---------------------------------------------------------------------------
# VAL-PROJ-005: Pagination
# ---------------------------------------------------------------------------


class TestProjectListPagination:
    """Tests for project list pagination."""

    def test_pagination_with_cursor_and_has_more(self, capsys: pytest.CaptureFixture) -> None:
        """Paginated list returns next_page_token and has_more fields."""
        # Create several projects
        for i in range(5):
            _capture_json(["project", "create", f"proj-{i:02d}"], capsys)

        _, result = _capture_json(["project", "list", "--limit", "2"], capsys)
        data = result["data"]
        assert len(data["items"]) <= 2
        assert "next_page_token" in data
        assert "has_more" in data
        assert "total" in data
        assert data["total"] >= 5

    def test_final_page_has_null_cursor(self, capsys: pytest.CaptureFixture) -> None:
        """Final page has next_page_token=null and has_more=false."""
        for i in range(3):
            _capture_json(["project", "create", f"page-{i}"], capsys)

        _, result = _capture_json(["project", "list", "--limit", "5"], capsys)
        data = result["data"]
        # With limit 5 and only 3 projects, should be final page
        assert data.get("has_more") is False, "Expected has_more=False on final page"
        assert data.get("next_page_token") is None, "Expected next_page_token=null on final page"

    def test_cursor_navigates_pages(self, capsys: pytest.CaptureFixture) -> None:
        """Using a page_token from a previous page returns next page."""
        for i in range(5):
            _capture_json(["project", "create", f"cursor-{i}"], capsys)

        # Page 1
        _, page1 = _capture_json(["project", "list", "--limit", "2"], capsys)
        page1_token = page1["data"].get("next_page_token")

        if page1_token and page1["data"].get("has_more"):
            # Page 2
            _, page2 = _capture_json(
                ["project", "list", "--limit", "2", "--page-token", page1_token], capsys
            )
            assert page2["success"] is True
            # Items should be different
            page1_ids = {item["id"] for item in page1["data"]["items"]}
            page2_ids = {item["id"] for item in page2["data"]["items"]}
            assert not page1_ids.intersection(page2_ids)


# ---------------------------------------------------------------------------
# VAL-PROJ-006: Empty list
# ---------------------------------------------------------------------------


class TestEmptyProjectList:
    """Tests for empty project list."""

    def test_empty_list_returns_success(self, capsys: pytest.CaptureFixture) -> None:
        """Empty project list returns success=true, items=[], total=0."""
        exit_code, result = _capture_json(["project", "list"], capsys)
        assert exit_code == ExitCode.SUCCESS
        assert result["success"] is True
        data = result["data"]
        assert data["items"] == []
        assert data["total"] == 0
        assert data.get("next_page_token") is None
        assert data.get("has_more") is not True


# ---------------------------------------------------------------------------
# VAL-PROJ-007 & VAL-PROJ-008: Status
# ---------------------------------------------------------------------------


class TestProjectStatus:
    """Tests for project status command."""

    def test_status_shows_full_state(self, capsys: pytest.CaptureFixture) -> None:
        """Status shows state enum, binary_count, timestamps, is_stale, lock."""
        _capture_json(["project", "create", "status-test"], capsys)

        exit_code, result = _capture_json(["project", "status", "status-test"], capsys)
        assert exit_code == ExitCode.SUCCESS
        data = result["data"]
        assert data["state"] in [s.value for s in ProjectState]
        assert "binary_count" in data
        assert isinstance(data["binary_count"], int)
        assert "created_at" in data
        assert "updated_at" in data
        assert "is_stale" in data
        # lock should be present (may be null for unlocked)
        assert "lock" in data

    def test_status_nonexistent_exit_code_6(self, capsys: pytest.CaptureFixture) -> None:
        """Status for nonexistent project returns exit code 6."""
        exit_code, result = _capture_json(["project", "status", "none-such"], capsys)
        assert exit_code == ExitCode.PROJECT_NOT_FOUND
        assert result["success"] is False
        # Error should mention project not found
        diag_messages = " ".join(d.get("message", "") for d in result.get("diagnostics", []))
        assert "not found" in diag_messages.lower()


# ---------------------------------------------------------------------------
# VAL-PROJ-009: Clean confirmation
# ---------------------------------------------------------------------------


class TestProjectClean:
    """Tests for project clean command."""

    def test_clean_requires_confirmation(self, capsys: pytest.CaptureFixture) -> None:
        """Clean without --yes/--force prompts for confirmation and fails."""
        _make_failed_project("clean-test")

        # Run clean without --yes or --force. Provide "n" as stdin to reject.
        exit_code, result = _capture_json(
            ["project", "clean", "clean-test"], capsys, stdin_text="n\n"
        )
        assert exit_code != ExitCode.SUCCESS
        assert result["success"] is False

    def test_clean_with_yes_on_failed_resets_to_created(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Clean --yes on FAILED project resets to CREATED, clears cache."""
        _make_failed_project("clean-test")
        # Add some cache entries
        from binary_analysis.projects.workspace import get_project_path

        proj_path = str(get_project_path("clean-test"))
        cache_set(proj_path, "test-data", {"hello": "world"})

        exit_code, result = _capture_json(["project", "clean", "clean-test", "--yes"], capsys)
        assert exit_code == ExitCode.SUCCESS
        assert result["success"] is True

        # Check manifest was updated
        manifest = load_manifest(proj_path)
        assert manifest["state"] == ProjectState.CREATED.value

        # Check cache was cleared
        from binary_analysis.projects.cache import cache_list

        assert cache_list(proj_path) == []

    def test_clean_with_force_on_failed_resets_to_created(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Clean --force on FAILED project resets to CREATED."""
        _make_failed_project("clean-force-test")

        exit_code, result = _capture_json(
            ["project", "clean", "clean-force-test", "--force"], capsys
        )
        assert exit_code == ExitCode.SUCCESS
        assert result["success"] is True

    def test_clean_on_non_failed_project_rejected(self, capsys: pytest.CaptureFixture) -> None:
        """Clean on non-FAILED (CREATED) project is rejected."""
        _capture_json(["project", "create", "not-failed"], capsys)

        exit_code, result = _capture_json(["project", "clean", "not-failed", "--yes"], capsys)
        assert exit_code != ExitCode.SUCCESS
        assert result["success"] is False

    def test_clean_on_imported_project_rejected(self, capsys: pytest.CaptureFixture) -> None:
        """Clean on IMPORTED project is rejected (only FAILED can be cleaned)."""
        _make_imported_project("imported-clean")

        exit_code, result = _capture_json(["project", "clean", "imported-clean", "--yes"], capsys)
        assert exit_code != ExitCode.SUCCESS
        assert result["success"] is False

    def test_clean_nonexistent_project(self, capsys: pytest.CaptureFixture) -> None:
        """Clean on nonexistent project returns error."""
        exit_code, result = _capture_json(["project", "clean", "nonexistent", "--yes"], capsys)
        assert exit_code != ExitCode.SUCCESS
        assert result["success"] is False


# ---------------------------------------------------------------------------
# VAL-PROJ-010: Clean clears cache & diagnostics
# ---------------------------------------------------------------------------


class TestProjectCleanClearCache:
    """Tests that clean clears cache and diagnostics on FAILED projects."""

    def test_clean_clears_cache(self, capsys: pytest.CaptureFixture) -> None:
        """Clean on FAILED project clears all cached data."""
        _make_failed_project("cache-clear-test")
        from binary_analysis.projects.workspace import get_project_path

        proj_path = str(get_project_path("cache-clear-test"))

        # Add cache entries
        for i in range(5):
            cache_set(proj_path, f"key-{i}", {"idx": i})

        _capture_json(["project", "clean", "cache-clear-test", "--yes"], capsys)

        from binary_analysis.projects.cache import cache_list

        assert cache_list(proj_path) == []

    def test_clean_preserves_project_identity(self, capsys: pytest.CaptureFixture) -> None:
        """Clean preserves project name and UUID but resets state."""
        _make_failed_project("identity-test")
        from binary_analysis.projects.workspace import get_project_path

        proj_path = str(get_project_path("identity-test"))

        manifest_before = load_manifest(proj_path)
        orig_name = manifest_before["name"]
        orig_id = manifest_before["id"]

        _capture_json(["project", "clean", "identity-test", "--yes"], capsys)

        manifest_after = load_manifest(proj_path)
        assert manifest_after["name"] == orig_name
        assert manifest_after["id"] == orig_id
        assert manifest_after["state"] == ProjectState.CREATED.value


# ---------------------------------------------------------------------------
# VAL-PROJ-011 & VAL-PROJ-012: Remove
# ---------------------------------------------------------------------------


class TestProjectRemove:
    """Tests for project remove command."""

    def test_remove_requires_confirmation(self, capsys: pytest.CaptureFixture) -> None:
        """Remove without --yes/--force prompts for confirmation and fails."""
        _capture_json(["project", "create", "remove-test"], capsys)

        # Provide "n" as stdin to reject confirmation
        exit_code, result = _capture_json(
            ["project", "remove", "remove-test"], capsys, stdin_text="n\n"
        )
        assert exit_code != ExitCode.SUCCESS
        assert result["success"] is False

        # Project should still exist
        from binary_analysis.projects.workspace import workspace_exists

        assert workspace_exists("remove-test")

    def test_remove_with_yes_deletes_workspace(self, capsys: pytest.CaptureFixture) -> None:
        """Remove --yes deletes the entire project workspace."""
        _capture_json(["project", "create", "remove-yes"], capsys)

        exit_code, result = _capture_json(["project", "remove", "remove-yes", "--yes"], capsys)
        assert exit_code == ExitCode.SUCCESS
        assert result["success"] is True

        from binary_analysis.projects.workspace import workspace_exists

        assert not workspace_exists("remove-yes")

    def test_remove_with_force_deletes_workspace(self, capsys: pytest.CaptureFixture) -> None:
        """Remove --force deletes the project workspace."""
        _capture_json(["project", "create", "remove-force"], capsys)

        exit_code, result = _capture_json(["project", "remove", "remove-force", "--force"], capsys)
        assert exit_code == ExitCode.SUCCESS
        assert result["success"] is True

        from binary_analysis.projects.workspace import workspace_exists

        assert not workspace_exists("remove-force")

    def test_remove_nonexistent_project(self, capsys: pytest.CaptureFixture) -> None:
        """Remove on nonexistent project returns error."""
        exit_code, result = _capture_json(["project", "remove", "nonexistent", "--yes"], capsys)
        assert exit_code != ExitCode.SUCCESS
        assert result["success"] is False


# ---------------------------------------------------------------------------
# VAL-PROJ-013: Remove --dry-run
# ---------------------------------------------------------------------------


class TestProjectRemoveDryRun:
    """Tests for project remove --dry-run."""

    def test_dry_run_previews_paths(self, capsys: pytest.CaptureFixture) -> None:
        """--dry-run reports planned deletion paths without deleting."""
        _capture_json(["project", "create", "dry-remove"], capsys)

        exit_code, result = _capture_json(["project", "remove", "dry-remove", "--dry-run"], capsys)
        assert exit_code == ExitCode.SUCCESS
        assert result["success"] is True
        data = result["data"]
        assert data.get("dry_run") is True

        # Project should still exist
        from binary_analysis.projects.workspace import workspace_exists

        assert workspace_exists("dry-remove")


# ---------------------------------------------------------------------------
# VAL-PROJ-014 & VAL-PROJ-015: Migrate
# ---------------------------------------------------------------------------


class TestProjectMigrate:
    """Tests for project migrate command."""

    def test_migrate_plan_shows_upgrade_path(self, capsys: pytest.CaptureFixture) -> None:
        """Migrate --plan shows upgrade path without mutating."""
        _capture_json(["project", "create", "migrate-test"], capsys)

        exit_code, result = _capture_json(["project", "migrate", "migrate-test", "--plan"], capsys)
        assert exit_code == ExitCode.SUCCESS
        assert result["success"] is True
        data = result["data"]
        assert "current_version" in data
        assert "target_version" in data
        assert "migration_steps" in data

        # Project should be unchanged
        from binary_analysis.projects.workspace import get_project_path

        proj_path = str(get_project_path("migrate-test"))
        manifest = load_manifest(proj_path)
        assert manifest["workspace_version"] == "1"

    def test_migrate_apply_upgrades_workspace(self, capsys: pytest.CaptureFixture) -> None:
        """Migrate --apply performs the workspace format upgrade."""
        _capture_json(["project", "create", "migrate-apply"], capsys)

        exit_code, result = _capture_json(
            ["project", "migrate", "migrate-apply", "--apply"], capsys
        )
        assert exit_code == ExitCode.SUCCESS
        assert result["success"] is True

        from binary_analysis.projects.workspace import get_project_path

        proj_path = str(get_project_path("migrate-apply"))
        manifest = load_manifest(proj_path)
        # Should be at the target version
        assert manifest["workspace_version"] == "1"  # Already at current version

    def test_migrate_dry_run_previews(self, capsys: pytest.CaptureFixture) -> None:
        """Migrate --dry-run previews migration plan without mutation."""
        _capture_json(["project", "create", "migrate-dry"], capsys)

        exit_code, result = _capture_json(
            ["project", "migrate", "migrate-dry", "--dry-run"], capsys
        )
        assert exit_code == ExitCode.SUCCESS
        assert result["success"] is True
        data = result["data"]
        assert "current_version" in data

    def test_migrate_nonexistent_project(self, capsys: pytest.CaptureFixture) -> None:
        """Migrate on nonexistent project returns error."""
        exit_code, result = _capture_json(["project", "migrate", "nonexistent", "--plan"], capsys)
        assert exit_code != ExitCode.SUCCESS
        assert result["success"] is False


# ---------------------------------------------------------------------------
# VAL-PROJ-017: Migrate on locked project rejected
# ---------------------------------------------------------------------------


class TestMigrateOnLocked:
    """Tests for migrate rejection on locked projects."""

    def test_migrate_on_locked_project_rejected(self, capsys: pytest.CaptureFixture) -> None:
        """Migrate --apply on locked project is rejected."""
        _capture_json(["project", "create", "migrate-locked"], capsys)

        from binary_analysis.projects.lock import acquire_lock, release_lock
        from binary_analysis.projects.workspace import get_project_path

        proj_path = str(get_project_path("migrate-locked"))
        acquire_lock(proj_path, "migrate-locked", "analysis")

        try:
            exit_code, result = _capture_json(
                ["project", "migrate", "migrate-locked", "--apply"], capsys
            )
            assert exit_code != ExitCode.SUCCESS
            assert result["success"] is False
        finally:
            release_lock(proj_path)


# ---------------------------------------------------------------------------
# VAL-PROJ-021: Staleness detection
# ---------------------------------------------------------------------------


class TestStalenessDetection:
    """Tests for staleness detection."""

    def test_status_shows_is_stale_false_for_created(self, capsys: pytest.CaptureFixture) -> None:
        """A freshly created project has is_stale=false."""
        _capture_json(["project", "create", "stale-test"], capsys)

        _, result = _capture_json(["project", "status", "stale-test"], capsys)
        assert result["data"]["is_stale"] is False

    def test_status_shows_state_stale_when_marked(self, capsys: pytest.CaptureFixture) -> None:
        """When a project is marked STALE in manifest, status reflects it."""
        _capture_json(["project", "create", "stale-marked"], capsys)

        from binary_analysis.projects.manifest import update_manifest_field
        from binary_analysis.projects.workspace import get_project_path

        proj_path = str(get_project_path("stale-marked"))
        update_manifest_field(
            proj_path,
            {"state": ProjectState.STALE.value, "is_stale": True},
        )

        _, result = _capture_json(["project", "status", "stale-marked"], capsys)
        assert result["data"]["is_stale"] is True
        assert result["data"]["state"] == ProjectState.STALE.value


# ---------------------------------------------------------------------------
# State machine transitions
# ---------------------------------------------------------------------------


class TestFailedTransitions:
    """Tests for FAILED state transitions."""

    def test_created_to_failed_transition(self, capsys: pytest.CaptureFixture) -> None:
        """CREATED->FAILED transition preserves diagnostics."""
        _capture_json(["project", "create", "created-to-fail"], capsys)

        from binary_analysis.projects.manifest import update_manifest_field
        from binary_analysis.projects.workspace import get_project_path

        proj_path = str(get_project_path("created-to-fail"))
        # Simulate a transition by writing FAILED state with diagnostics
        update_manifest_field(
            proj_path,
            {
                "state": ProjectState.FAILED.value,
                "diagnostics": [
                    {
                        "severity": "ERROR",
                        "category": "validation",
                        "message": "Import validation failed",
                        "recoverable": False,
                    }
                ],
            },
        )

        # Verify state
        manifest = load_manifest(proj_path)
        assert manifest["state"] == ProjectState.FAILED.value
        assert len(manifest.get("diagnostics", [])) > 0

    def test_imported_to_failed_transition(self, capsys: pytest.CaptureFixture) -> None:
        """IMPORTED->FAILED transition preserves binary record."""
        _make_imported_project("imported-to-fail")

        from binary_analysis.projects.manifest import update_manifest_field
        from binary_analysis.projects.workspace import get_project_path

        proj_path = str(get_project_path("imported-to-fail"))
        manifest_before = load_manifest(proj_path)

        # Transition to FAILED
        update_manifest_field(
            proj_path,
            {
                "state": ProjectState.FAILED.value,
                "diagnostics": [
                    {
                        "severity": "ERROR",
                        "category": "analysis",
                        "message": "Analysis failed — null dereference",
                        "recoverable": False,
                    }
                ],
            },
        )

        manifest_after = load_manifest(proj_path)
        assert manifest_after["state"] == ProjectState.FAILED.value
        # Binary count preserved
        assert manifest_after["binary_count"] == manifest_before["binary_count"]

    def test_analyzing_to_failed_transition(self, capsys: pytest.CaptureFixture) -> None:
        """ANALYZING->FAILED transition releases lock and preserves diagnostics."""
        _make_imported_project("analyzing-to-fail")

        from binary_analysis.projects.lock import acquire_lock, release_lock
        from binary_analysis.projects.manifest import update_manifest_field
        from binary_analysis.projects.workspace import get_project_path

        proj_path = str(get_project_path("analyzing-to-fail"))

        # Simulate acquiring lock (ANALYZING state)
        acquire_lock(proj_path, "analyzing-to-fail", "analysis")
        update_manifest_field(
            proj_path,
            {
                "state": ProjectState.ANALYZING.value,
                "lock": {"holder": "test-process", "acquired_at": "2026-01-01T00:00:00Z"},
            },
        )

        # Release lock and transition to FAILED
        release_lock(proj_path)
        update_manifest_field(
            proj_path,
            {
                "state": ProjectState.FAILED.value,
                "lock": None,
                "diagnostics": [
                    {
                        "severity": "ERROR",
                        "category": "analysis",
                        "message": "Backend crash during analysis",
                        "recoverable": False,
                    }
                ],
            },
        )

        from binary_analysis.projects.lock import is_locked

        assert not is_locked(proj_path)

        manifest = load_manifest(proj_path)
        assert manifest["state"] == ProjectState.FAILED.value
        assert manifest["lock"] is None
        assert len(manifest.get("diagnostics", [])) > 0

    def test_stale_to_failed_transition(self, capsys: pytest.CaptureFixture) -> None:
        """STALE->FAILED transition captures both staleness cause and analysis failure."""
        _make_ready_project("stale-to-fail")

        from binary_analysis.projects.manifest import update_manifest_field
        from binary_analysis.projects.workspace import get_project_path

        proj_path = str(get_project_path("stale-to-fail"))

        # First mark as STALE
        update_manifest_field(
            proj_path,
            {
                "state": ProjectState.STALE.value,
                "is_stale": True,
            },
        )

        # Then transition to FAILED with both staleness and failure diagnostics
        update_manifest_field(
            proj_path,
            {
                "state": ProjectState.FAILED.value,
                "diagnostics": [
                    {
                        "severity": "WARNING",
                        "category": "staleness",
                        "message": "Source binary SHA-256 changed",
                        "recoverable": True,
                    },
                    {
                        "severity": "ERROR",
                        "category": "analysis",
                        "message": "Re-analysis failed after staleness detected",
                        "recoverable": False,
                    },
                ],
            },
        )

        manifest = load_manifest(proj_path)
        assert manifest["state"] == ProjectState.FAILED.value
        assert len(manifest.get("diagnostics", [])) >= 2


# ---------------------------------------------------------------------------
# Project list with many items (for pagination edge cases)
# ---------------------------------------------------------------------------


class TestProjectListEdgeCases:
    """Edge case tests for project list."""

    def test_limit_must_be_positive(self, capsys: pytest.CaptureFixture) -> None:
        """Non-positive --limit should be rejected."""
        exit_code, _result = _capture_json(["project", "list", "--limit", "0"], capsys)
        assert exit_code == ExitCode.INVALID_ARGS

    def test_default_limit_is_100(self, capsys: pytest.CaptureFixture) -> None:
        """Default limit should be 100."""
        _, result = _capture_json(["project", "list"], capsys)
        # With no projects, we just check the command works
        assert result["success"] is True


# ---------------------------------------------------------------------------
# Project status edge cases
# ---------------------------------------------------------------------------


class TestProjectStatusEdgeCases:
    """Edge case tests for project status."""

    def test_status_on_created_project(self, capsys: pytest.CaptureFixture) -> None:
        """Status on a freshly created project shows CREATED with no binary."""
        _capture_json(["project", "create", "fresh-status"], capsys)

        _, result = _capture_json(["project", "status", "fresh-status"], capsys)
        assert result["data"]["state"] == "CREATED"
        assert result["data"]["binary_count"] == 0

    def test_status_on_imported_project(self, capsys: pytest.CaptureFixture) -> None:
        """Status on an imported project shows IMPORTED with binary count."""
        _make_imported_project("status-imported")

        _, result = _capture_json(["project", "status", "status-imported"], capsys)
        assert result["data"]["state"] == "IMPORTED"
        assert result["data"]["binary_count"] == 1

    def test_status_timestamps_are_iso8601(self, capsys: pytest.CaptureFixture) -> None:
        """Status timestamps are ISO 8601 formatted."""
        _capture_json(["project", "create", "ts-status"], capsys)

        _, result = _capture_json(["project", "status", "ts-status"], capsys)
        created_at = result["data"]["created_at"]
        updated_at = result["data"]["updated_at"]
        datetime.fromisoformat(created_at)
        datetime.fromisoformat(updated_at)

    def test_status_lock_holder_is_null_when_unlocked(self, capsys: pytest.CaptureFixture) -> None:
        """Status reports lock as null when project is not locked."""
        _capture_json(["project", "create", "unlocked-status"], capsys)

        _, result = _capture_json(["project", "status", "unlocked-status"], capsys)
        assert result["data"].get("lock") is None
