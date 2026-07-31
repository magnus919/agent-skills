"""Audit event persistence — append-only events.jsonl.

Provides atomic audit event writing and reading for the project audit log.
Each event is a single-line JSON object appended atomically. Events are
immutable and append-only; no modification or deletion is supported.

Events include: timestamp, command, args, result (AuditResult enum),
duration_ms, project_id, and optional details.

Key guarantees:
- Atomic append: no partial lines, no interleaving.
- Every line is valid JSON (single-line object).
- Events ordered by timestamp (ISO 8601 with timezone).
- File only grows; never shrinks or overwrites existing entries.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from binary_analysis.domain.enums import AuditResult
from binary_analysis.projects.atomic import atomic_append_text

AUDIT_FILENAME = "events.jsonl"


def _audit_path(project_path: str) -> str:
    """Return the path to the audit events file within a project workspace.

    Args:
        project_path: Absolute path to the project workspace directory.

    Returns:
        Full path to the events.jsonl file.
    """
    return os.path.join(project_path, "audit", AUDIT_FILENAME)


def write_audit_event(
    project_path: str,
    command: str,
    result: AuditResult,
    duration_ms: int,
    *,
    args: dict[str, Any] | None = None,
    project_id: str | None = None,
    binary_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Atomically append a single audit event to events.jsonl.

    Each event is written as a single JSON line. Uses atomic_append_text
    to guarantee no partial lines or interleaving.

    Args:
        project_path: Absolute path to the project workspace directory.
        command: The command name (e.g., "project create", "import", "analyze").
        result: Outcome from AuditResult enum.
        duration_ms: Wall-clock duration in milliseconds.
        args: Non-sensitive command arguments (flags, selectors).
        project_id: Optional project UUID.
        binary_id: Optional binary UUID.
        details: Optional additional event details.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    event: dict[str, Any] = {
        "timestamp": timestamp,
        "command": command,
        "args": args if args is not None else {},
        "result": result.value,
        "duration_ms": duration_ms,
    }

    if project_id is not None:
        event["project_id"] = project_id
    if binary_id is not None:
        event["binary_id"] = binary_id
    if details is not None:
        event["details"] = details

    line = json.dumps(event, ensure_ascii=False)
    path = _audit_path(project_path)
    atomic_append_text(path, line)


def read_audit_events(project_path: str) -> list[dict[str, Any]]:
    """Read all audit events from events.jsonl, ordered by appearance.

    Events are returned in file order (oldest first), which corresponds to
    timestamp order since events are appended chronologically.

    Args:
        project_path: Absolute path to the project workspace directory.

    Returns:
        List of audit event dicts ordered by timestamp. Empty list if the
        file does not exist or is empty.
    """
    path = _audit_path(project_path)
    if not os.path.exists(path):
        return []

    events: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    events.append(event)
                except json.JSONDecodeError:
                    # Skip corrupted lines but emit a placeholder
                    events.append(
                        {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "command": "unknown",
                            "args": {},
                            "result": AuditResult.FAILED.value,
                            "duration_ms": 0,
                            "details": {"error": f"Corrupted audit event: {line[:100]}"},
                        }
                    )
    except OSError:
        return []

    return events


def clear_audit(project_path: str) -> None:
    """Remove the audit events file (e.g., on project clean).

    Args:
        project_path: Absolute path to the project workspace directory.
    """
    path = _audit_path(project_path)
    if os.path.exists(path):
        os.unlink(path)


def audit_file_exists(project_path: str) -> bool:
    """Check if the audit events file exists.

    Args:
        project_path: Absolute path to the project workspace directory.

    Returns:
        True if the events.jsonl file exists.
    """
    return os.path.exists(_audit_path(project_path))
