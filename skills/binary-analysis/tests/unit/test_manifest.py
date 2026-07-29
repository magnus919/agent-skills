"""Tests for the project manifest module (projects/manifest.py).

Validates that:
- New manifests have correct defaults (UUID, name, state CREATED, timestamps).
- Manifest save is atomic (valid JSON after any write).
- Manifest load correctly reads and validates manifests.
- Loading corrupted JSON raises InvalidConfigError with exit code 4.
- Loading manifests with missing required fields raises InvalidConfigError.
- update_manifest_field atomically updates and saves.
- Timestamps are ISO 8601 with timezone.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest
from binary_analysis.domain.enums import ProjectState
from binary_analysis.domain.errors import InvalidConfigError
from binary_analysis.projects.manifest import (
    _WORKSPACE_VERSION,
    create_manifest,
    load_manifest,
    save_manifest,
    update_manifest_field,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def project_dir(tmp_path: Path) -> str:
    """Fixture: a temp directory acting as a project workspace."""
    return str(tmp_path)


# ---------------------------------------------------------------------------
# Create manifest
# ---------------------------------------------------------------------------


class TestCreateManifest:
    """Tests for create_manifest."""

    def test_defaults(self) -> None:
        """New manifest has all required fields with correct defaults."""
        manifest = create_manifest("my-project")
        assert "id" in manifest
        assert "name" in manifest
        assert "state" in manifest
        assert "created_at" in manifest
        assert "updated_at" in manifest
        assert "workspace_version" in manifest
        assert "binary_count" in manifest
        assert "is_stale" in manifest

    def test_state_is_created(self) -> None:
        """New manifest has state CREATED."""
        manifest = create_manifest("my-project")
        assert manifest["state"] == ProjectState.CREATED.value

    def test_binary_count_zero(self) -> None:
        """New manifest has binary_count 0."""
        manifest = create_manifest("my-project")
        assert manifest["binary_count"] == 0

    def test_not_stale(self) -> None:
        """New manifest has is_stale False."""
        manifest = create_manifest("my-project")
        assert manifest["is_stale"] is False

    def test_lock_is_none(self) -> None:
        """New manifest has lock set to None."""
        manifest = create_manifest("my-project")
        assert manifest["lock"] is None

    def test_workspace_version(self) -> None:
        """New manifest has current workspace version."""
        manifest = create_manifest("my-project")
        assert manifest["workspace_version"] == _WORKSPACE_VERSION

    def test_id_is_valid_uuid(self) -> None:
        """The project ID is a valid UUID."""
        manifest = create_manifest("my-project")
        UUID(manifest["id"])  # Raises ValueError if invalid

    def test_custom_uuid(self) -> None:
        """A custom UUID can be provided."""
        from uuid import uuid4

        custom_id = uuid4()
        manifest = create_manifest("my-project", project_id=custom_id)
        assert manifest["id"] == str(custom_id)

    def test_name_matches(self) -> None:
        """The project name matches the input."""
        manifest = create_manifest("my-analysis-project")
        assert manifest["name"] == "my-analysis-project"

    def test_timestamps_are_iso8601(self) -> None:
        """Timestamps are ISO 8601 formatted."""
        manifest = create_manifest("my-project")
        datetime.fromisoformat(manifest["created_at"])
        datetime.fromisoformat(manifest["updated_at"])


# ---------------------------------------------------------------------------
# Save and Load manifest
# ---------------------------------------------------------------------------


class TestSaveAndLoadManifest:
    """Tests for save_manifest and load_manifest."""

    def test_save_and_load_roundtrip(self, project_dir: str) -> None:
        """Saving and loading a manifest preserves all fields."""
        manifest = create_manifest("roundtrip-test")
        save_manifest(project_dir, manifest)
        loaded = load_manifest(project_dir)
        assert loaded["id"] == manifest["id"]
        assert loaded["name"] == manifest["name"]
        assert loaded["state"] == manifest["state"]
        assert loaded["binary_count"] == manifest["binary_count"]

    def test_file_is_valid_json(self, project_dir: str) -> None:
        """The saved project.json is valid JSON and parseable by json.load."""
        manifest = create_manifest("my-project")
        save_manifest(project_dir, manifest)
        manifest_path = os.path.join(project_dir, "project.json")
        with open(manifest_path) as f:
            parsed = json.load(f)
        assert parsed == manifest

    def test_load_nonexistent_raises(self, project_dir: str) -> None:
        """Loading a manifest that doesn't exist raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            load_manifest(project_dir)

    def test_load_corrupted_json_raises(self, project_dir: str) -> None:
        """Loading corrupted (invalid) JSON raises InvalidConfigError, exit code 4."""
        manifest_path = os.path.join(project_dir, "project.json")
        with open(manifest_path, "w") as f:
            f.write("{invalid json")

        with pytest.raises(InvalidConfigError, match="Corrupted project manifest") as excinfo:
            load_manifest(project_dir)
        assert excinfo.value.exit_code == 4

    def test_load_malformed_json_random_text(self, project_dir: str) -> None:
        """Loading non-JSON text raises InvalidConfigError with exit code 4."""
        manifest_path = os.path.join(project_dir, "project.json")
        with open(manifest_path, "w") as f:
            f.write("just some random text, not JSON at all")

        with pytest.raises(InvalidConfigError, match="Corrupted project manifest") as excinfo:
            load_manifest(project_dir)
        assert excinfo.value.exit_code == 4

    def test_load_truncated_json(self, project_dir: str) -> None:
        """Loading truncated JSON raises InvalidConfigError (exit code 4)."""
        manifest_path = os.path.join(project_dir, "project.json")
        valid = create_manifest("my-project")
        json_str = json.dumps(valid)
        # Truncate mid-key
        truncated = json_str[: len(json_str) // 2]
        with open(manifest_path, "w") as f:
            f.write(truncated)

        with pytest.raises(InvalidConfigError, match="Corrupted project manifest") as excinfo:
            load_manifest(project_dir)
        assert excinfo.value.exit_code == 4

    def test_load_empty_file(self, project_dir: str) -> None:
        """Loading an empty file raises InvalidConfigError (exit code 4)."""
        manifest_path = os.path.join(project_dir, "project.json")
        with open(manifest_path, "w") as f:
            f.write("")

        with pytest.raises(InvalidConfigError, match="Corrupted project manifest") as excinfo:
            load_manifest(project_dir)
        assert excinfo.value.exit_code == 4

    def test_load_list_not_dict(self, project_dir: str) -> None:
        """Loading a JSON array instead of object raises InvalidConfigError."""
        manifest_path = os.path.join(project_dir, "project.json")
        with open(manifest_path, "w") as f:
            json.dump([1, 2, 3], f)

        with pytest.raises(InvalidConfigError, match="Corrupted project manifest") as excinfo:
            load_manifest(project_dir)
        assert excinfo.value.exit_code == 4

    def test_load_missing_required_fields(self, project_dir: str) -> None:
        """Loading manifest with missing required fields raises InvalidConfigError."""
        manifest = {"id": "123", "name": "test"}  # Missing state, created_at, etc.
        manifest_path = os.path.join(project_dir, "project.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)

        with pytest.raises(InvalidConfigError, match="missing required fields") as excinfo:
            load_manifest(project_dir)
        assert excinfo.value.exit_code == 4

    def test_atomic_save(self, project_dir: str) -> None:
        """Save is atomic — no .tmp files remain, file is valid JSON."""
        manifest = create_manifest("atomic-test")
        save_manifest(project_dir, manifest)
        # No temp files left behind
        project_path = Path(project_dir)
        tmp_files = list(project_path.glob("*.tmp"))
        assert len(tmp_files) == 0
        # File is valid JSON
        manifest_path = project_path / "project.json"
        loaded = json.loads(manifest_path.read_text("utf-8"))
        assert loaded["name"] == "atomic-test"


# ---------------------------------------------------------------------------
# Update manifest
# ---------------------------------------------------------------------------


class TestUpdateManifestField:
    """Tests for update_manifest_field."""

    def test_update_state(self, project_dir: str) -> None:
        """Updating fields atomically updates state in project.json."""
        manifest = create_manifest("update-test")
        save_manifest(project_dir, manifest)

        updated = update_manifest_field(
            project_dir,
            {"state": ProjectState.IMPORTED.value, "binary_count": 1},
        )
        assert updated["state"] == ProjectState.IMPORTED.value
        assert updated["binary_count"] == 1
        assert updated["name"] == "update-test"  # Unchanged

    def test_updated_at_changes(self, project_dir: str) -> None:
        """updated_at is refreshed on every update."""
        manifest = create_manifest("update-test")
        save_manifest(project_dir, manifest)
        original_updated_at = manifest["updated_at"]

        updated = update_manifest_field(project_dir, {"binary_count": 5})
        assert updated["updated_at"] != original_updated_at

    def test_update_nonexistent_raises(self, project_dir: str) -> None:
        """Updating a nonexistent project raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            update_manifest_field(project_dir, {"state": "CREATED"})

    def test_update_to_stale(self, project_dir: str) -> None:
        """Staleness can be updated atomically."""
        manifest = create_manifest("stale-test")
        save_manifest(project_dir, manifest)

        updated = update_manifest_field(project_dir, {"is_stale": True})
        assert updated["is_stale"] is True

    def test_update_lock(self, project_dir: str) -> None:
        """Lock status can be updated."""
        manifest = create_manifest("lock-test")
        save_manifest(project_dir, manifest)

        lock_info = {"holder": "process-12345", "acquired_at": "2026-07-29T12:00:00Z"}
        updated = update_manifest_field(project_dir, {"lock": lock_info})
        assert updated["lock"] == lock_info

    def test_update_lock_release(self, project_dir: str) -> None:
        """Lock can be released (set to None)."""
        manifest = create_manifest("lock-test")
        manifest["lock"] = {"holder": "process-12345"}
        save_manifest(project_dir, manifest)

        updated = update_manifest_field(project_dir, {"lock": None})
        assert updated["lock"] is None


# ---------------------------------------------------------------------------
# Save validation
# ---------------------------------------------------------------------------


class TestSaveValidation:
    """Tests for save_manifest validation."""

    def test_save_rejects_missing_required_fields(self, project_dir: str) -> None:
        """Saving a manifest with missing fields raises InvalidConfigError."""
        bad_manifest = {"name": "test"}  # Missing required fields
        with pytest.raises(InvalidConfigError, match="missing required fields"):
            save_manifest(project_dir, bad_manifest)

    def test_save_rejects_partial_manifest(self, project_dir: str) -> None:
        """Saving a manifest with only some required fields raises InvalidConfigError."""
        bad_manifest = {
            "id": "123",
            "name": "test",
            "state": "CREATED",
            # Missing created_at, workspace_version, binary_count, is_stale
        }
        with pytest.raises(InvalidConfigError, match="missing required fields"):
            save_manifest(project_dir, bad_manifest)
