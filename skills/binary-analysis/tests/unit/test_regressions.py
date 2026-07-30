"""Regression tests for specific bug scenarios.

These tests guard against regressions in specific behavior that was
fixed or verified to be correct. They cover edge cases and behaviors
that are critical for correctness but not covered by broader test suites.

Tests:
- duration_ms > 0 in audit events
- clamp_page_size warning emission in JSON envelope
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from binary_analysis.cli.main import main
from binary_analysis.reporting.audit import audit_file_exists, read_audit_events

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_binary_fixture(tmpdir: str, content: bytes = b"MZ\x00\x01") -> str:
    """Create a fake PE binary fixture."""
    path = os.path.join(tmpdir, "test_fixture.exe")
    data = bytearray(content)
    while len(data) < 64:
        data.append(0)
    with open(path, "wb") as f:
        f.write(data)
    return path


def _capture_run(argv: list[str]) -> tuple[int, str, dict[str, Any]]:
    """Run the CLI and return (exit_code, stdout, parsed_envelope)."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    exit_code = 0
    try:
        exit_code = main(argv)
    except SystemExit as e:
        exit_code = e.code if isinstance(e.code, int) else 1
    finally:
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

    try:
        envelope = json.loads(output)
    except (json.JSONDecodeError, TypeError):
        envelope = {}
    return exit_code, output, envelope


# ---------------------------------------------------------------------------
# Test: duration_ms > 0 in audit events
# ---------------------------------------------------------------------------


class TestAuditDurationMs:
    """Regression: audit events must have duration_ms > 0."""

    def test_audit_events_have_positive_duration(self, monkeypatch):
        """After a full lifecycle, audit events must have duration_ms > 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            # Run a mini lifecycle
            exit_code, _, _ = _capture_run(["--json", "project", "create", "audit-dur-test"])
            assert exit_code == 0

            exit_code, _, _ = _capture_run(
                ["--json", "import", "--project", "audit-dur-test", binary_path]
            )
            assert exit_code == 0

            exit_code, _, _ = _capture_run(
                ["--json", "analyze", "--project", "audit-dur-test", "--profile", "standard"]
            )
            assert exit_code == 0

            # Read audit events
            project_path = os.path.join(tmpdir, "audit-dur-test")
            assert audit_file_exists(project_path), "Audit file should exist after lifecycle"

            events = read_audit_events(project_path)
            assert len(events) >= 3, (
                f"Expected at least 3 audit events (create, import, analyze), got {len(events)}"
            )

            # Every event must have duration_ms >= 0 (integer, non-negative)
            events_with_positive = 0
            for i, event in enumerate(events):
                duration = event.get("duration_ms", -1)
                assert isinstance(duration, int), (
                    f"Event {i}: duration_ms should be int, got {type(duration).__name__}"
                )
                assert duration >= 0, (
                    f"Event {i} ({event.get('command', 'unknown')}): "
                    f"duration_ms must be >= 0, got {duration}"
                )
                if duration > 0:
                    events_with_positive += 1

            # At least analyze should have > 0 (it involves a slow import)
            assert events_with_positive >= 1, (
                f"Expected at least one audit event with duration_ms > 0, "
                f"got {events_with_positive} out of {len(events)}. "
                f"Events: {json.dumps(events, indent=2)[:500]}"
            )


# ---------------------------------------------------------------------------
# Test: clamp_page_size warning in JSON envelope
# ---------------------------------------------------------------------------


class TestClampPageSizeWarning:
    """Regression: clamp_page_size warning appears in JSON envelope warnings."""

    def test_clamp_warning_in_envelope(self, monkeypatch):
        """When --limit exceeds max, warning appears in JSON envelope."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            _capture_run(["--json", "project", "create", "clamp-warn-test"])
            _capture_run(["--json", "import", "--project", "clamp-warn-test", binary_path])
            _capture_run(
                ["--json", "analyze", "--project", "clamp-warn-test", "--profile", "standard"]
            )

            # Run functions with --limit 5000 (above max 1000)
            exit_code, _, envelope = _capture_run(
                [
                    "--json",
                    "--limit",
                    "5000",
                    "functions",
                    "--project",
                    "clamp-warn-test",
                ]
            )
            assert exit_code == 0

            # Warning should appear in JSON envelope's warnings array
            warnings_list = envelope.get("warnings", [])
            clamp_warnings = [w for w in warnings_list if w.get("category") == "pagination"]
            assert len(clamp_warnings) >= 1, (
                f"Expected pagination warning in envelope, got warnings: {warnings_list}"
            )
            assert "5000" in clamp_warnings[0]["message"]
            assert "1000" in clamp_warnings[0]["message"]
            assert clamp_warnings[0]["severity"] == "WARNING"

            # Verify no warning appears on stderr (was previously the behavior)
            # This regression ensures it goes through the JSON envelope, not stderr

    def test_clamp_warning_appears_for_security_commands(self, monkeypatch):
        """clamp warning appears for security commands too."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                "binary_analysis.projects.workspace.get_workspace_root",
                lambda: Path(tmpdir),
            )
            monkeypatch.setattr(
                "binary_analysis.projects.workspace._DEFAULT_WORKSPACE_ROOT",
                str(tmpdir),
            )

            binary_path = _create_binary_fixture(tmpdir)

            _capture_run(["--json", "project", "create", "clamp-sec-test"])
            _capture_run(["--json", "import", "--project", "clamp-sec-test", binary_path])
            _capture_run(
                ["--json", "analyze", "--project", "clamp-sec-test", "--profile", "standard"]
            )

            # Test triage with excessive limit
            _, _, envelope = _capture_run(
                ["--json", "triage", "--project", "clamp-sec-test", "--limit", "5000"]
            )
            warnings_list = envelope.get("warnings", [])
            clamp_warnings = [w for w in warnings_list if w.get("category") == "pagination"]
            assert len(clamp_warnings) >= 1, (
                f"Expected pagination warning in triage envelope, got: {warnings_list}"
            )

            # Test suspicious-apis with excessive limit
            _, _, envelope = _capture_run(
                ["--json", "suspicious-apis", "--project", "clamp-sec-test", "--limit", "5000"]
            )
            warnings_list = envelope.get("warnings", [])
            clamp_warnings = [w for w in warnings_list if w.get("category") == "pagination"]
            assert len(clamp_warnings) >= 1, (
                f"Expected pagination warning in suspicious-apis envelope, got: {warnings_list}"
            )

            # Test capability-map with excessive limit
            _, _, envelope = _capture_run(
                ["--json", "capability-map", "--project", "clamp-sec-test", "--limit", "5000"]
            )
            warnings_list = envelope.get("warnings", [])
            clamp_warnings = [w for w in warnings_list if w.get("category") == "pagination"]
            assert len(clamp_warnings) >= 1, (
                f"Expected pagination warning in capability-map envelope, got: {warnings_list}"
            )
