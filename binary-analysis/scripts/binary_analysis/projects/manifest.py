"""Project manifest — load, save, validate, and atomically write project.json.

Uses the atomic write utility (tempfile + os.rename) to ensure that
project.json is never partially written. A process crash during a write
leaves the previous valid manifest (or no manifest) but never a corrupted one.

Key guarantees:
- Loads project manifests as typed dicts with validation.
- Saves project manifests atomically via atomic_write_json.
- Detects corrupted manifests (invalid JSON) and raises InvalidConfigError
  with exit code 4.
- Detects missing required fields in manifest and treats as corruption.
- Provides helpers to create new project manifests with proper defaults.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from binary_analysis.domain.enums import ProjectState
from binary_analysis.domain.errors import InvalidConfigError
from binary_analysis.projects.atomic import atomic_write_json

# Required top-level fields in project.json
_REQUIRED_FIELDS: tuple[str, ...] = (
    "id",
    "name",
    "state",
    "created_at",
    "workspace_version",
    "binary_count",
    "is_stale",
)

# Current workspace format version
_WORKSPACE_VERSION = "1"

# Manifest filename within a project workspace
MANIFEST_FILENAME = "project.json"


def create_manifest(
    project_name: str,
    project_id: UUID | None = None,
) -> dict[str, Any]:
    """Create a new project manifest dict with default values.

    The manifest is in the CREATED state, with a new UUID and current timestamp.

    Args:
        project_name: The project name.
        project_id: Optional UUID; auto-generated if not provided.

    Returns:
        A dict representing the project manifest, ready to be saved.
    """
    now = datetime.now(timezone.utc).isoformat()
    if project_id is None:
        project_id = uuid4()

    return {
        "id": str(project_id),
        "name": project_name,
        "state": ProjectState.CREATED.value,
        "created_at": now,
        "updated_at": now,
        "workspace_version": _WORKSPACE_VERSION,
        "binary_count": 0,
        "is_stale": False,
        "lock": None,
        "description": None,
        "max_binary_size_bytes": None,
    }


def save_manifest(project_path: str, manifest: dict[str, Any]) -> None:
    """Atomically save a project manifest to project.json.

    Uses tempfile + os.rename to guarantee the file is never partially
    written. If the process crashes mid-write, the previous valid manifest
    (or no file) is left intact.

    Args:
        project_path: Absolute path to the project workspace directory.
        manifest: The manifest dict to save.

    Raises:
        ValueError: If the manifest is missing required fields.
    """
    _validate_manifest(manifest)
    manifest_path = f"{project_path}/{MANIFEST_FILENAME}"
    atomic_write_json(manifest_path, manifest)


def load_manifest(project_path: str) -> dict[str, Any]:
    """Load a project manifest from project.json.

    Reads and validates the manifest. If the file is missing, raises
    FileNotFoundError. If the JSON is invalid, raises InvalidConfigError
    (exit code 4) with a diagnostic explaining the corruption.
    If required fields are missing, raises InvalidConfigError.

    Args:
        project_path: Absolute path to the project workspace directory.

    Returns:
        The parsed and validated manifest dict.

    Raises:
        FileNotFoundError: If project.json does not exist.
        InvalidConfigError: If the manifest is corrupted (invalid JSON or
            missing required fields). Exit code 4.
    """
    manifest_path = f"{project_path}/{MANIFEST_FILENAME}"

    try:
        with open(manifest_path, encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Project manifest not found: {manifest_path}") from None

    # Parse JSON — detect corruption
    try:
        manifest = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise InvalidConfigError(
            f"Corrupted project manifest at {manifest_path}: invalid JSON. "
            f"Parse error: {e.msg} at line {e.lineno}, column {e.colno}. "
            f"The file must be repaired or the project workspace re-created."
        ) from e

    if not isinstance(manifest, dict):
        raise InvalidConfigError(
            f"Corrupted project manifest at {manifest_path}: "
            f"expected a JSON object, got {type(manifest).__name__}."
        )

    # Validate required fields
    _validate_manifest(manifest)

    return manifest


def _validate_manifest(manifest: dict[str, Any]) -> None:
    """Validate that a manifest dict has all required fields.

    Args:
        manifest: The manifest dict to validate.

    Raises:
        InvalidConfigError: If required fields are missing.
    """
    missing = [field for field in _REQUIRED_FIELDS if field not in manifest]
    if missing:
        raise InvalidConfigError(
            f"Corrupted project manifest: missing required fields: {', '.join(missing)}."
        )


def update_manifest_field(
    project_path: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    """Load, update fields, and atomically save a project manifest.

    This is a convenience for state transitions and field updates.
    Automatically updates the `updated_at` timestamp.

    Args:
        project_path: Absolute path to the project workspace directory.
        updates: Dict of field names to new values.

    Returns:
        The updated manifest dict (post-save).

    Raises:
        FileNotFoundError: If the project doesn't exist.
        InvalidConfigError: If the current or updated manifest is corrupted.
    """
    manifest = load_manifest(project_path)
    manifest.update(updates)
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_manifest(project_path, manifest)
    return manifest
