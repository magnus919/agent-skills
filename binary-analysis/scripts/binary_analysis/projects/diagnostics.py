"""Diagnostics persistence — accumulate and retrieve diagnostics across commands.

Diagnostics are persisted as JSONL in project/diagnostics.jsonl, one
JSON object per line. Each entry has: severity, category, message, recoverable,
command, and timestamp.

The diagnostics file grows across the project lifecycle: warnings and errors
from analyze, triage, suspicious-apis, and other commands are accumulated
and retrievable via the `binary diagnostics` command.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from binary_analysis.projects.atomic import atomic_append_text

DIAGNOSTICS_FILENAME = "diagnostics.jsonl"


def _diagnostics_path(project_path: str) -> str:
    """Return the path to the diagnostics file within a project workspace."""
    return os.path.join(project_path, DIAGNOSTICS_FILENAME)


def persist_diagnostics(
    project_path: str,
    diagnostics: list[dict[str, Any]],
    command: str = "unknown",
) -> None:
    """Persist diagnostic entries to the project's diagnostics file.

    Each diagnostic entry is augmented with a command field and timestamp
    before being appended atomically to the JSONL file.

    Args:
        project_path: Absolute path to the project workspace directory.
        diagnostics: List of diagnostic dicts to persist.
        command: Name of the command that produced these diagnostics.
    """
    if not diagnostics:
        return

    path = _diagnostics_path(project_path)
    timestamp = datetime.now(timezone.utc).isoformat()

    for diag in diagnostics:
        entry = {
            "severity": diag.get("severity", "INFO"),
            "category": diag.get("category", "general"),
            "message": diag.get("message", ""),
            "recoverable": diag.get("recoverable", True),
            "command": command,
            "timestamp": timestamp,
        }
        # Preserve optional fields
        if "component" in diag:
            entry["component"] = diag["component"]
        if "remediation" in diag:
            entry["remediation"] = diag["remediation"]

        line = json.dumps(entry, ensure_ascii=False)
        atomic_append_text(path, line)


def load_diagnostics(project_path: str) -> list[dict[str, Any]]:
    """Load all accumulated diagnostics from the project's diagnostics file.

    Returns an empty list if the file does not exist or is empty.

    Args:
        project_path: Absolute path to the project workspace directory.

    Returns:
        List of diagnostic dicts ordered by appearance in the file
        (oldest first).
    """
    path = _diagnostics_path(project_path)
    if not os.path.exists(path):
        return []

    diagnostics: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    diagnostics.append(entry)
                except json.JSONDecodeError:
                    # Skip corrupted lines but note in a diagnostic
                    diagnostics.append(
                        {
                            "severity": "WARNING",
                            "category": "diagnostics-file",
                            "message": f"Corrupted diagnostics entry at line {line_num}",
                            "recoverable": True,
                            "command": "diagnostics",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )
    except OSError:
        return []

    return diagnostics


def clear_diagnostics(project_path: str) -> None:
    """Remove the diagnostics file (e.g., on project clean).

    Args:
        project_path: Absolute path to the project workspace directory.
    """
    path = _diagnostics_path(project_path)
    if os.path.exists(path):
        os.unlink(path)


def get_diagnostics_summary(
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute a summary of diagnostic entries.

    Args:
        diagnostics: List of diagnostic dicts.

    Returns:
        Dict with total count and breakdown by severity.
    """
    by_severity: dict[str, int] = {"INFO": 0, "WARNING": 0, "ERROR": 0}
    for d in diagnostics:
        sev = d.get("severity", "INFO")
        if sev in by_severity:
            by_severity[sev] += 1

    return {
        "total": len(diagnostics),
        "by_severity": by_severity,
    }
