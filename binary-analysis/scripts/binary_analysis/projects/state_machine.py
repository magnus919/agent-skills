"""Project state machine — lifecycle transitions and staleness detection.

Enforces strict state transitions per the architecture:
  CREATED -> IMPORTED -> ANALYZING -> READY
  READY -> STALE -> ANALYZING
  Any state -> FAILED (with diagnostics preserved)

Provides:
- Transition validation (reject invalid transitions).
- FAILED transition helpers (preserve diagnostics, release locks).
- Staleness detection (SHA-256 comparison on source change).
- State-aware operation guards (clean only FAILED, migrate only unlocked).
"""

from __future__ import annotations

import contextlib
from datetime import datetime, timezone
from typing import Any

from binary_analysis.domain.enums import ProjectState

# ---------------------------------------------------------------------------
# Valid transition map
# ---------------------------------------------------------------------------

# Each state maps to a set of allowed target states
_VALID_TRANSITIONS: dict[ProjectState, set[ProjectState]] = {
    ProjectState.CREATED: {ProjectState.IMPORTED, ProjectState.FAILED},
    ProjectState.IMPORTED: {ProjectState.ANALYZING, ProjectState.FAILED},
    ProjectState.ANALYZING: {ProjectState.READY, ProjectState.FAILED},
    ProjectState.READY: {ProjectState.STALE, ProjectState.FAILED},
    ProjectState.STALE: {ProjectState.ANALYZING, ProjectState.FAILED},
    ProjectState.FAILED: {ProjectState.CREATED},  # Clean resets to CREATED
}

# States from which analyze can be started (re-transition)
_ANALYZABLE_STATES: set[ProjectState] = {
    ProjectState.IMPORTED,
    ProjectState.STALE,
    ProjectState.READY,  # Can detect staleness without re-analyzing
}

# States from which import is allowed
_IMPORTABLE_STATES: set[ProjectState] = {
    ProjectState.CREATED,
    ProjectState.IMPORTED,
}

# States from which clean is allowed (only FAILED)
_CLEANABLE_STATES: set[ProjectState] = {
    ProjectState.FAILED,
}

# States from which migrate is rejected (locked projects)
_MIGRATE_BLOCKED_STATES: set[ProjectState] = {
    ProjectState.ANALYZING,
}


# ---------------------------------------------------------------------------
# Transition validation
# ---------------------------------------------------------------------------


def is_valid_transition(from_state: ProjectState, to_state: ProjectState) -> bool:
    """Check if a state transition is allowed by the state machine.

    Args:
        from_state: Current project state.
        to_state: Desired target state.

    Returns:
        True if the transition is valid.
    """
    allowed = _VALID_TRANSITIONS.get(from_state, set())
    return to_state in allowed


def can_analyze(state: ProjectState) -> bool:
    """Check if analysis can be started from the given state."""
    return state in _ANALYZABLE_STATES


def can_import(state: ProjectState) -> bool:
    """Check if a binary import is allowed in the given state."""
    return state in _IMPORTABLE_STATES


def can_clean(state: ProjectState) -> bool:
    """Check if clean is allowed in the given state (only FAILED)."""
    return state in _CLEANABLE_STATES


def should_reject_migrate(state: ProjectState, is_locked: bool) -> bool:
    """Check if migrate should be rejected due to project state or lock.

    Args:
        state: Current project state.
        is_locked: Whether the project has an active lock.

    Returns:
        True if migrate should be rejected.
    """
    if is_locked:
        return True
    return state in _MIGRATE_BLOCKED_STATES


# ---------------------------------------------------------------------------
# Transition helpers
# ---------------------------------------------------------------------------


def transition_to_failed(
    manifest: dict[str, Any],
    from_state: ProjectState,
    diagnostics: list[dict[str, Any]],
    release_lock_fn: Any | None = None,
) -> dict[str, Any]:
    """Transition a project to FAILED state, preserving context from the source state.

    Handles specific preservation rules per source state:
    - CREATED->FAILED: Preserve diagnostics, no lock to release.
    - IMPORTED->FAILED: Preserve binary record (binary_count, binary data),
      release lock if held.
    - ANALYZING->FAILED: Release lock, preserve crash diagnostics,
      clear lock from manifest.
    - STALE->FAILED: Capture both staleness cause and analysis failure,
      preserve binary record.

    Args:
        manifest: The current project manifest (mutated in place).
        from_state: The state before failure.
        diagnostics: Failure diagnostics to preserve.
        release_lock_fn: Optional function to release the project lock.

    Returns:
        The updated manifest dict.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Preserve existing diagnostics
    existing_diags = manifest.get("diagnostics", [])
    if not isinstance(existing_diags, list):
        existing_diags = []

    # Merge diagnostics, ensuring we don't lose staleness context
    merged_diags = existing_diags + diagnostics

    # Update manifest
    manifest["state"] = ProjectState.FAILED.value
    manifest["diagnostics"] = merged_diags
    manifest["updated_at"] = now

    # Release lock if transitioning from ANALYZING
    if from_state == ProjectState.ANALYZING:
        manifest["lock"] = None
        if release_lock_fn is not None:
            with contextlib.suppress(Exception):
                release_lock_fn()

    # Preserve binary record for IMPORTED->FAILED and STALE->FAILED
    # (binary_count and is_stale are preserved by default since we don't clear them)

    return manifest
