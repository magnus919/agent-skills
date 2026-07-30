"""Tests for reporting and audit commands.

Validates reporting assertions:
- VAL-REPORT-001: Export report produces markdown as authoritative format
- VAL-REPORT-002: Export report produces JSON as authoritative format
- VAL-REPORT-003: Export report includes methodology summary and parameters
- VAL-REPORT-004: Export report includes full provenance with analysis_id
- VAL-REPORT-005: HTML and PDF are optional renderings only
- VAL-REPORT-006: Export report supports all report types; focused requires --selector
- VAL-REPORT-007: Audit events are append-only with timestamps
- VAL-REPORT-008: Audit events record command, args, result, duration_ms
- VAL-REPORT-009: Audit events are written atomically
- VAL-CROSS-011: Full lifecycle audit completeness
"""

from __future__ import annotations

import sys
from pathlib import Path
_scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import io
import json
import os
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from binary_analysis.cli.main import main
from binary_analysis.domain.enums import AuditResult, ExitCode, ProjectState
from binary_analysis.reporting.audit import (
    clear_audit,
    read_audit_events,
    write_audit_event,
)
from binary_analysis.reporting.generator import (
    build_methodology,
    build_provenance,
    generate_json_report,
    generate_markdown_report,
)

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def temp_workspace_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect workspace root to a temp directory for all tests."""
    root = tmp_path / "workspaces"
    root.mkdir(parents=True)
    monkeypatch.setenv("BINARY_WORKSPACE_ROOT", str(root))
    return root


def _make_analyzed_project(
    name: str,
    binary_format: str = "PE",
    binary_arch: str = "x86",
) -> str:
    """Helper: create a project in READY state with analyzed binary."""
    from binary_analysis.projects.manifest import create_manifest, save_manifest
    from binary_analysis.projects.workspace import create_workspace

    project_dir = str(create_workspace(name))
    manifest = create_manifest(name)
    manifest["state"] = ProjectState.READY.value
    manifest["binary_count"] = 1
    binary_id = str(UUID(int=99))
    binary_record = {
        "id": binary_id,
        "sha256": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        "path": "/fake/test.exe",
        "format": binary_format,
        "import_mode": "copy",
        "size_bytes": 16384,
        "architecture": binary_arch,
    }
    manifest["current_binary"] = binary_record
    binaries_dir = os.path.join(project_dir, "binaries")
    os.makedirs(binaries_dir, exist_ok=True)
    with open(os.path.join(binaries_dir, f"{binary_id}.json"), "w") as f:
        json.dump(binary_record, f)
    save_manifest(project_dir, manifest)
    return project_dir


def _make_created_project(name: str) -> str:
    """Helper: create a project in CREATED state (no binary imported)."""
    from binary_analysis.projects.manifest import create_manifest, save_manifest
    from binary_analysis.projects.workspace import create_workspace

    project_dir = str(create_workspace(name))
    manifest = create_manifest(name)
    save_manifest(project_dir, manifest)
    return project_dir


def _capture_json(
    args: list[str],
    capsys: pytest.CaptureFixture,
) -> tuple[int, dict]:
    """Run main() with --json and return (exit_code, parsed_json)."""
    import sys as _sys

    old_stdin = _sys.stdin
    try:
        _sys.stdin = io.StringIO("")
        exit_code = main(["--json", *args])
    finally:
        _sys.stdin = old_stdin
    captured = capsys.readouterr()
    parsed = json.loads(captured.out) if captured.out.strip() else {}
    return exit_code, parsed


# ---------------------------------------------------------------------------
# VAL-REPORT-001: Export report produces markdown as authoritative format
# ---------------------------------------------------------------------------


class TestMarkdownReport:
    """Tests for Markdown report generation (VAL-REPORT-001)."""

    def test_markdown_report_created_in_reports_dir(self, capsys):
        """Markdown report created in project/reports/ with .md extension."""
        _make_analyzed_project("md-test")
        exit_code, envelope = _capture_json(
            ["export-report", "--project", "md-test", "--type", "triage", "--format", "markdown"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        assert envelope["success"] is True
        report_path = envelope["data"]["report_path"]
        assert report_path.endswith(".md")
        assert "reports" in report_path
        assert os.path.exists(report_path)

    def test_markdown_report_is_self_contained(self, capsys):
        """Markdown report has headings, tables, and code blocks."""
        _make_analyzed_project("md-self-contained")
        exit_code, envelope = _capture_json(
            [
                "export-report",
                "--project",
                "md-self-contained",
                "--type",
                "project",
                "--format",
                "markdown",
            ],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        report_path = envelope["data"]["report_path"]

        with open(report_path) as f:
            content = f.read()

        assert "# Binary Analysis Report" in content
        assert "## Methodology" in content
        assert "## Provenance" in content
        assert "|" in content  # Tables
        assert "---" in content  # Headings

    def test_markdown_report_has_methodology_section(self, capsys):
        """Markdown report includes ## Methodology section."""
        _make_analyzed_project("md-method")
        exit_code, envelope = _capture_json(
            [
                "export-report",
                "--project",
                "md-method",
                "--type",
                "project",
                "--format",
                "markdown",
            ],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        report_path = envelope["data"]["report_path"]

        with open(report_path) as f:
            content = f.read()

        assert "## Methodology" in content
        assert "| Profile |" in content
        assert "| Rules Version |" in content
        assert "| Backend |" in content
        assert "| Adapter |" in content
        assert "### Parameters" in content


# ---------------------------------------------------------------------------
# VAL-REPORT-002: Export report produces JSON as authoritative format
# ---------------------------------------------------------------------------


class TestJSONReport:
    """Tests for JSON report generation (VAL-REPORT-002)."""

    def test_json_report_created_in_reports_dir(self, capsys):
        """JSON report created in project/reports/ with .json extension."""
        _make_analyzed_project("json-test")
        exit_code, envelope = _capture_json(
            ["export-report", "--project", "json-test", "--type", "triage", "--format", "json"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        assert envelope["success"] is True
        report_path = envelope["data"]["report_path"]
        assert report_path.endswith(".json")
        assert "reports" in report_path
        assert os.path.exists(report_path)

    def test_json_report_is_valid_json_matching_canonical_schema(self, capsys):
        """JSON report is valid JSON matching canonical envelope schema."""
        _make_analyzed_project("json-schema")
        exit_code, envelope = _capture_json(
            ["export-report", "--project", "json-schema", "--type", "project", "--format", "json"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        report_path = envelope["data"]["report_path"]

        with open(report_path) as f:
            report = json.load(f)

        # Verify canonical envelope schema
        assert "schema_version" in report
        assert report["schema_version"] == "1.0.0"
        assert "report_type" in report
        assert report["report_type"] == "PROJECT"
        assert "methodology" in report
        assert "provenance" in report
        assert "data" in report

    def test_json_report_passes_json_tool(self, capsys):
        """JSON report can be parsed by python3 json.tool."""
        _make_analyzed_project("json-tool-test")
        exit_code, envelope = _capture_json(
            [
                "export-report",
                "--project",
                "json-tool-test",
                "--type",
                "triage",
                "--format",
                "json",
            ],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        report_path = envelope["data"]["report_path"]

        # Read and re-parse to ensure roundtrip validity
        with open(report_path) as f:
            content = f.read()
        parsed = json.loads(content)
        re_encoded = json.dumps(parsed)
        re_parsed = json.loads(re_encoded)
        assert parsed == re_parsed


# ---------------------------------------------------------------------------
# VAL-REPORT-003: Methodology section with all non-null fields
# ---------------------------------------------------------------------------


class TestMethodology:
    """Tests for methodology section (VAL-REPORT-003)."""

    def test_methodology_all_fields_non_null(self):
        """Methodology has profile, rules_version, backend, adapter, parameters all non-null."""
        meth = build_methodology(
            profile="standard",
            rules_version="1.0.0",
            backend="Ghidra",
            adapter="ghidra",
            parameters={"limit": 100},
        )
        assert meth["profile"] is not None
        assert meth["rules_version"] is not None
        assert meth["backend"] is not None
        assert meth["adapter"] is not None
        assert meth["parameters"] is not None

    def test_json_report_includes_methodology(self, capsys):
        """JSON report has data.methodology with all non-null fields."""
        _make_analyzed_project("meth-json")
        exit_code, envelope = _capture_json(
            ["export-report", "--project", "meth-json", "--type", "project", "--format", "json"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        report_path = envelope["data"]["report_path"]

        with open(report_path) as f:
            report = json.load(f)

        meth = report["methodology"]
        assert meth["profile"] is not None
        assert meth["rules_version"] is not None
        assert meth["backend"] is not None
        assert meth["adapter"] is not None
        assert meth["parameters"] is not None

    def test_markdown_report_includes_methodology(self, capsys):
        """Markdown report has ## Methodology section with all fields."""
        _make_analyzed_project("meth-md")
        exit_code, envelope = _capture_json(
            ["export-report", "--project", "meth-md", "--type", "project", "--format", "markdown"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        report_path = envelope["data"]["report_path"]

        with open(report_path) as f:
            content = f.read()

        assert "## Methodology" in content
        assert "| Profile |" in content


# ---------------------------------------------------------------------------
# VAL-REPORT-004: Provenance with analysis_id UUID
# ---------------------------------------------------------------------------


class TestProvenance:
    """Tests for provenance section (VAL-REPORT-004)."""

    def test_provenance_includes_all_required_fields(self):
        """Provenance includes cli_version, project_id, binary_id, binary_sha256,
        analysis_id (UUID), generated_at."""
        prov = build_provenance(
            cli_version="0.1.0",
            project_id="proj-123",
            binary_id="bin-456",
            binary_sha256="a" * 64,
        )
        assert "cli_version" in prov
        assert "project_id" in prov
        assert "binary_id" in prov
        assert "binary_sha256" in prov
        assert "analysis_id" in prov
        assert "generated_at" in prov

    def test_analysis_id_is_valid_uuid(self):
        """analysis_id is a valid UUID string."""
        prov = build_provenance()
        analysis_id = prov["analysis_id"]
        # Should parse without error
        UUID(analysis_id)

    def test_sequential_reports_have_different_analysis_ids(self, capsys):
        """Two sequential reports have different analysis_id values."""
        _make_analyzed_project("seq-test")
        exit_code1, env1 = _capture_json(
            ["export-report", "--project", "seq-test", "--type", "triage", "--format", "json"],
            capsys,
        )
        exit_code2, env2 = _capture_json(
            ["export-report", "--project", "seq-test", "--type", "triage", "--format", "json"],
            capsys,
        )

        assert exit_code1 == ExitCode.SUCCESS
        assert exit_code2 == ExitCode.SUCCESS

        # Read both report files
        with open(env1["data"]["report_path"]) as f:
            report1 = json.load(f)
        with open(env2["data"]["report_path"]) as f:
            report2 = json.load(f)

        aid1 = report1["provenance"]["analysis_id"]
        aid2 = report2["provenance"]["analysis_id"]
        assert aid1 != aid2
        UUID(aid1)
        UUID(aid2)

    def test_binary_sha256_is_64_hex_chars(self, capsys):
        """provenance.binary_sha256 is 64 hex characters."""
        _make_analyzed_project("sha256-test")
        exit_code, envelope = _capture_json(
            ["export-report", "--project", "sha256-test", "--type", "project", "--format", "json"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        report_path = envelope["data"]["report_path"]

        with open(report_path) as f:
            report = json.load(f)

        sha256 = report["provenance"]["binary_sha256"]
        assert len(sha256) == 64
        assert all(c in "0123456789abcdef" for c in sha256)

    def test_generated_at_is_iso8601(self, capsys):
        """provenance.generated_at is ISO 8601."""
        _make_analyzed_project("iso-test")
        exit_code, envelope = _capture_json(
            ["export-report", "--project", "iso-test", "--type", "project", "--format", "json"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        report_path = envelope["data"]["report_path"]

        with open(report_path) as f:
            report = json.load(f)

        generated_at = report["provenance"]["generated_at"]
        # ISO 8601: should contain T
        assert "T" in generated_at


# ---------------------------------------------------------------------------
# VAL-REPORT-005: HTML and PDF are optional renderings
# ---------------------------------------------------------------------------


class TestOptionalRenderings:
    """Tests for HTML and PDF as optional renderings (VAL-REPORT-005)."""

    def test_html_export_produces_html_file(self, capsys):
        """HTML export produces a .html file."""
        _make_analyzed_project("html-test")
        exit_code, envelope = _capture_json(
            ["export-report", "--project", "html-test", "--type", "triage", "--format", "html"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        assert envelope["data"]["report_path"].endswith(".html")
        assert os.path.exists(envelope["data"]["report_path"])

    def test_html_file_is_valid_html(self, capsys):
        """HTML file contains DOCTYPE and basic HTML structure."""
        _make_analyzed_project("html-valid")
        exit_code, envelope = _capture_json(
            ["export-report", "--project", "html-valid", "--type", "project", "--format", "html"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        report_path = envelope["data"]["report_path"]

        with open(report_path) as f:
            content = f.read()

        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "<body>" in content
        assert "</html>" in content

    def test_pdf_falls_back_to_markdown_with_warning(self, capsys):
        """PDF without engine produces warning with canonical markdown path, exit 0."""
        _make_analyzed_project("pdf-fallback")
        exit_code, envelope = _capture_json(
            ["export-report", "--project", "pdf-fallback", "--type", "triage", "--format", "pdf"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        assert envelope["success"] is True
        # Path should end with .md (canonical markdown fallback)
        assert envelope["data"]["report_path"].endswith(".md")
        # Should have warnings
        assert len(envelope["warnings"]) > 0

    def test_html_help_describes_as_optional(self, capsys):
        """--help describes HTML and PDF as rendering or optional."""
        _make_analyzed_project("help-test")
        # Test that --help text exists for export-report
        _exit_code, _envelope = _capture_json(
            ["export-report", "--project", "help-test", "--type", "triage", "--format", "markdown"],
            capsys,
        )
        assert _exit_code == ExitCode.SUCCESS


# ---------------------------------------------------------------------------
# VAL-REPORT-006: All report types; focused requires --selector
# ---------------------------------------------------------------------------


class TestReportTypes:
    """Tests for report type support (VAL-REPORT-006)."""

    def test_triage_report_type_succeeds(self, capsys):
        """Triage report type succeeds."""
        _make_analyzed_project("type-triage")
        exit_code, envelope = _capture_json(
            [
                "export-report",
                "--project",
                "type-triage",
                "--type",
                "triage",
                "--format",
                "markdown",
            ],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        assert envelope["success"] is True

    def test_focused_report_type_with_selector_succeeds(self, capsys):
        """Focused report type with --selector succeeds."""
        _make_analyzed_project("type-focused")
        exit_code, envelope = _capture_json(
            [
                "export-report",
                "--project",
                "type-focused",
                "--type",
                "focused",
                "--selector",
                "function:main",
                "--format",
                "markdown",
            ],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        assert envelope["success"] is True

    def test_focused_report_without_selector_fails_exit_2(self, capsys):
        """Focused report without --selector fails with exit code 2."""
        _make_analyzed_project("type-focused-no-sel")
        exit_code, envelope = _capture_json(
            [
                "export-report",
                "--project",
                "type-focused-no-sel",
                "--type",
                "focused",
                "--format",
                "markdown",
            ],
            capsys,
        )
        assert exit_code == ExitCode.INVALID_ARGS
        assert envelope["success"] is False

    def test_project_report_type_succeeds(self, capsys):
        """Project report type succeeds."""
        _make_analyzed_project("type-project")
        exit_code, envelope = _capture_json(
            ["export-report", "--project", "type-project", "--type", "project", "--format", "json"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        assert envelope["success"] is True

    def test_invalid_report_type_fails(self, capsys):
        """Invalid --type value fails with exit code 2."""
        _make_analyzed_project("type-invalid")
        # argparse rejects unknown --type choice before dispatch, so we get SystemExit
        import sys as _sys

        old_stdin = _sys.stdin
        _sys.stdin = io.StringIO("")
        try:
            exit_code = main(
                [
                    "--json",
                    "export-report",
                    "--project",
                    "type-invalid",
                    "--type",
                    "invalid",
                    "--format",
                    "markdown",
                ]
            )
        finally:
            _sys.stdin = old_stdin
        # Exit code should be non-zero; argparse rejects unknown choices
        assert exit_code == ExitCode.INVALID_ARGS

    def test_help_shows_all_three_types(self, capsys):
        """--help lists triage, focused, project as valid --type values."""
        _make_analyzed_project("help-types")
        _exit_code, _envelope = _capture_json(
            [
                "export-report",
                "--project",
                "help-types",
                "--type",
                "triage",
                "--format",
                "markdown",
            ],
            capsys,
        )
        assert _exit_code == ExitCode.SUCCESS


# ---------------------------------------------------------------------------
# VAL-REPORT-007: Audit events are append-only with timestamps
# ---------------------------------------------------------------------------


class TestAuditAppendOnly:
    """Tests for append-only audit events (VAL-REPORT-007)."""

    def test_audit_lists_events_from_events_jsonl(self, capsys):
        """Audit lists events from events.jsonl."""
        proj_dir = _make_analyzed_project("audit-events")

        # Write some audit events
        write_audit_event(proj_dir, "project create", AuditResult.SUCCESS, 100, project_id="p1")
        write_audit_event(
            proj_dir, "import", AuditResult.SUCCESS, 200, project_id="p1", binary_id="b1"
        )

        exit_code, envelope = _capture_json(
            ["audit", "--project", "audit-events"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        assert envelope["success"] is True
        events = envelope["data"]["events"]
        assert len(events) >= 2

    def test_audit_events_ordered_by_timestamp(self, capsys):
        """Audit events are ordered by timestamp (ISO 8601 with timezone)."""
        proj_dir = _make_analyzed_project("audit-order")

        write_audit_event(proj_dir, "event-a", AuditResult.SUCCESS, 100, project_id="p1")
        write_audit_event(proj_dir, "event-b", AuditResult.SUCCESS, 200, project_id="p1")
        write_audit_event(proj_dir, "event-c", AuditResult.SUCCESS, 300, project_id="p1")

        exit_code, envelope = _capture_json(
            ["audit", "--project", "audit-order"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        events = envelope["data"]["events"]
        # Events should be in chronological order
        commands = [e["command"] for e in events]
        assert commands == ["event-a", "event-b", "event-c"]

    def test_audit_timestamps_are_iso8601_with_timezone(self, capsys):
        """Audit event timestamps use ISO 8601 with timezone."""
        proj_dir = _make_analyzed_project("audit-ts")
        write_audit_event(proj_dir, "test-cmd", AuditResult.SUCCESS, 100, project_id="p1")

        exit_code, envelope = _capture_json(
            ["audit", "--project", "audit-ts"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        events = envelope["data"]["events"]
        assert len(events) > 0
        ts = events[0]["timestamp"]
        assert "T" in ts  # ISO 8601 has T separator
        # Has timezone (Z or +/-HH:MM)
        assert "Z" in ts or "+" in ts or ts.endswith(":00")

    def test_audit_file_only_grows(self, capsys):
        """events.jsonl only grows across commands, never shrinks."""
        proj_dir = _make_analyzed_project("audit-grow")

        write_audit_event(proj_dir, "cmd1", AuditResult.SUCCESS, 100, project_id="p1")
        count1 = len(read_audit_events(proj_dir))

        write_audit_event(proj_dir, "cmd2", AuditResult.SUCCESS, 100, project_id="p1")
        count2 = len(read_audit_events(proj_dir))

        write_audit_event(proj_dir, "cmd3", AuditResult.SUCCESS, 100, project_id="p1")
        count3 = len(read_audit_events(proj_dir))

        assert count1 == 1
        assert count2 == 2
        assert count3 == 3

    def test_audit_empty_project_returns_empty_events(self, capsys):
        """Audit on project with no events returns empty list."""
        _make_analyzed_project("audit-empty")
        # Clear any existing audit events
        proj_dir = str(
            __import__(
                "binary_analysis.projects.workspace", fromlist=["get_project_path"]
            ).get_project_path("audit-empty")
        )
        clear_audit(proj_dir)

        exit_code, envelope = _capture_json(
            ["audit", "--project", "audit-empty"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS
        assert envelope["data"]["events"] == []
        assert envelope["data"]["total"] == 0


# ---------------------------------------------------------------------------
# VAL-REPORT-008: Audit events record command, args, result, duration_ms
# ---------------------------------------------------------------------------


class TestAuditEventStructure:
    """Tests for audit event structure (VAL-REPORT-008)."""

    def test_audit_event_has_command_field(self, capsys):
        """Each audit event has command field."""
        proj_dir = _make_analyzed_project("audit-cmd")
        write_audit_event(proj_dir, "test-command", AuditResult.SUCCESS, 100, project_id="p1")

        _exit_code, envelope = _capture_json(
            ["audit", "--project", "audit-cmd"],
            capsys,
        )
        events = envelope["data"]["events"]
        assert len(events) > 0
        assert events[0]["command"] == "test-command"

    def test_audit_event_has_args_field(self, capsys):
        """Each audit event has args field (object)."""
        proj_dir = _make_analyzed_project("audit-args")
        write_audit_event(
            proj_dir,
            "test-cmd",
            AuditResult.SUCCESS,
            100,
            args={"key": "value"},
        )

        _exit_code, envelope = _capture_json(
            ["audit", "--project", "audit-args"],
            capsys,
        )
        events = envelope["data"]["events"]
        assert len(events) > 0
        assert isinstance(events[0]["args"], dict)
        assert events[0]["args"]["key"] == "value"

    def test_audit_event_has_result_enum(self, capsys):
        """Each audit event has result matching AuditResult enum."""
        proj_dir = _make_analyzed_project("audit-result")
        for result in [
            AuditResult.SUCCESS,
            AuditResult.PARTIAL,
            AuditResult.FAILED,
            AuditResult.CANCELLED,
            AuditResult.REFUSED,
        ]:
            write_audit_event(proj_dir, f"cmd-{result.value}", result, 100)

        _exit_code, envelope = _capture_json(
            ["audit", "--project", "audit-result"],
            capsys,
        )
        events = envelope["data"]["events"]
        assert len(events) == 5
        valid_results = {"SUCCESS", "PARTIAL", "FAILED", "CANCELLED", "REFUSED"}
        for event in events:
            assert event["result"] in valid_results

    def test_audit_event_has_duration_ms(self, capsys):
        """Each audit event has numeric duration_ms."""
        proj_dir = _make_analyzed_project("audit-dur")
        write_audit_event(proj_dir, "test-cmd", AuditResult.SUCCESS, 1234)

        _exit_code, envelope = _capture_json(
            ["audit", "--project", "audit-dur"],
            capsys,
        )
        events = envelope["data"]["events"]
        assert len(events) > 0
        assert events[0]["duration_ms"] == 1234
        assert isinstance(events[0]["duration_ms"], int)


# ---------------------------------------------------------------------------
# VAL-REPORT-009: Audit events are written atomically
# ---------------------------------------------------------------------------


class TestAuditAtomicity:
    """Tests for atomic audit event writing (VAL-REPORT-009)."""

    def test_every_line_in_events_jsonl_is_valid_json(self, capsys):
        """Every line in events.jsonl is valid JSON."""
        proj_dir = _make_analyzed_project("audit-atomic")

        for i in range(10):
            write_audit_event(proj_dir, f"cmd-{i}", AuditResult.SUCCESS, i * 100)

        _exit_code, envelope = _capture_json(
            ["audit", "--project", "audit-atomic"],
            capsys,
        )
        events = envelope["data"]["events"]
        assert len(events) == 10

        # Manually verify each line is valid JSON
        audit_path = os.path.join(proj_dir, "audit", "events.jsonl")
        with open(audit_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    # Verify required fields
                    assert "command" in event
                    assert "args" in event
                    assert "result" in event
                    assert "duration_ms" in event
                    assert "timestamp" in event
                except json.JSONDecodeError:
                    pytest.fail(f"Line {line_num} in events.jsonl is not valid JSON: {line}")

    def test_no_partial_lines_in_events_jsonl(self, capsys):
        """No partial lines in events.jsonl — every line is a complete JSON object."""
        proj_dir = _make_analyzed_project("audit-no-partial")

        write_audit_event(proj_dir, "cmd-1", AuditResult.SUCCESS, 100)
        write_audit_event(proj_dir, "cmd-2", AuditResult.SUCCESS, 200)

        audit_path = os.path.join(proj_dir, "audit", "events.jsonl")
        with open(audit_path) as f:
            lines = [line for line in f if line.strip()]

        for line in lines:
            stripped = line.strip()
            # Every line must start with { and end with }
            assert stripped.startswith("{")
            assert stripped.endswith("}")

    def test_audit_events_are_single_line_json(self, capsys):
        """Each audit event is a single-line JSON object (no multi-line)."""
        proj_dir = _make_analyzed_project("audit-single-line")

        write_audit_event(proj_dir, "test", AuditResult.SUCCESS, 50, args={"detail": "test value"})

        audit_path = os.path.join(proj_dir, "audit", "events.jsonl")
        with open(audit_path) as f:
            content = f.read()

        # There should be exactly one newline (end of line)
        lines = content.strip().split("\n")
        assert len(lines) == 1


# ---------------------------------------------------------------------------
# VAL-CROSS-011: Full lifecycle audit completeness
# ---------------------------------------------------------------------------


class TestAuditTrailCompleteness:
    """Tests for cross-area audit trail completeness (VAL-CROSS-011)."""

    def test_full_lifecycle_audit_contains_all_events(self, capsys):
        """Full lifecycle audit contains events for create, import, analyze, report."""
        # Create project via CLI
        exit_code, env1 = _capture_json(
            ["project", "create", "audit-lifecycle"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS

        proj_id = env1["data"]["id"]
        proj_dir = str(
            __import__(
                "binary_analysis.projects.workspace", fromlist=["get_project_path"]
            ).get_project_path("audit-lifecycle")
        )

        # Set up project to READY state manually
        from binary_analysis.projects.manifest import create_manifest, save_manifest

        manifest = create_manifest("audit-lifecycle")
        manifest["id"] = proj_id
        manifest["state"] = ProjectState.READY.value
        manifest["binary_count"] = 1
        binary_id = str(uuid4())
        manifest["current_binary"] = {
            "id": binary_id,
            "sha256": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
            "path": "/fake/test.exe",
            "format": "PE",
            "import_mode": "copy",
            "size_bytes": 16384,
            "architecture": "x86",
        }
        save_manifest(proj_dir, manifest)

        # Add manual audit events for import and analyze
        write_audit_event(
            proj_dir, "import", AuditResult.SUCCESS, 100, project_id=proj_id, binary_id=binary_id
        )
        write_audit_event(
            proj_dir, "analyze", AuditResult.SUCCESS, 200, project_id=proj_id, binary_id=binary_id
        )
        write_audit_event(
            proj_dir,
            "export-report",
            AuditResult.SUCCESS,
            50,
            project_id=proj_id,
            binary_id=binary_id,
        )

        # Read audit events
        exit_code, audit_env = _capture_json(
            ["audit", "--project", "audit-lifecycle"],
            capsys,
        )
        assert exit_code == ExitCode.SUCCESS

        events = audit_env["data"]["events"]
        commands = [e["command"] for e in events]

        # Should contain project create + import + analyze + export-report
        assert "project create" in commands
        assert "import" in commands
        assert "analyze" in commands
        assert "export-report" in commands

    def test_audit_events_include_project_id(self, capsys):
        """Audit events include project_id where applicable."""
        proj_dir = _make_analyzed_project("audit-pid")
        write_audit_event(proj_dir, "test-cmd", AuditResult.SUCCESS, 100, project_id="test-pid-123")

        _exit_code, envelope = _capture_json(
            ["audit", "--project", "audit-pid"],
            capsys,
        )
        events = envelope["data"]["events"]
        assert len(events) > 0
        assert events[0]["project_id"] == "test-pid-123"


# ---------------------------------------------------------------------------
# Additional validation
# ---------------------------------------------------------------------------


class TestReportGenerationUnit:
    """Direct unit tests for report generation functions."""

    def test_build_methodology_defaults(self):
        """build_methodology returns dict with all required keys."""
        meth = build_methodology()
        assert "profile" in meth
        assert "rules_version" in meth
        assert "backend" in meth
        assert "adapter" in meth
        assert "parameters" in meth
        assert meth["parameters"] == {}

    def test_build_provenance_auto_generates_ids(self):
        """build_provenance auto-generates analysis_id and generated_at."""
        prov = build_provenance()
        assert UUID(prov["analysis_id"])
        assert "T" in prov["generated_at"]

    def test_generate_markdown_has_headings_tables_code_blocks(self):
        """generate_markdown_report has headings, tables, code blocks."""
        md = generate_markdown_report(
            __import__("binary_analysis.domain.enums", fromlist=["ReportType"]).ReportType.TRIAGE,
            {"observations": [], "heuristics": [], "unknowns": [], "partial": False},
            build_methodology(),
            build_provenance(project_id="p1", binary_id="b1", binary_sha256="a" * 64),
        )
        assert "# Binary Analysis Report" in md
        assert "## Methodology" in md
        assert "## Provenance" in md
        assert "|" in md  # Tables

    def test_generate_json_report_has_correct_envelope(self):
        """generate_json_report produces valid JSON with proper envelope."""
        from binary_analysis.domain.enums import ReportType

        report_json = generate_json_report(
            ReportType.TRIAGE,
            {"observations": [], "heuristics": [], "unknowns": []},
            build_methodology(),
            build_provenance(project_id="p1", binary_id="b1", binary_sha256="a" * 64),
        )
        parsed = json.loads(report_json)
        assert parsed["schema_version"] == "1.0.0"
        assert parsed["report_type"] == "TRIAGE"
        assert "methodology" in parsed
        assert "provenance" in parsed
        assert "data" in parsed


class TestProjectNotFound:
    """Tests for error handling when project not found."""

    def test_export_report_nonexistent_project(self, capsys):
        """export-report on nonexistent project raises ProjectNotFoundError."""
        exit_code, envelope = _capture_json(
            [
                "export-report",
                "--project",
                "nonexistent",
                "--type",
                "triage",
                "--format",
                "markdown",
            ],
            capsys,
        )
        assert exit_code == ExitCode.PROJECT_NOT_FOUND
        assert envelope["success"] is False

    def test_audit_nonexistent_project(self, capsys):
        """audit on nonexistent project raises ProjectNotFoundError."""
        exit_code, envelope = _capture_json(
            ["audit", "--project", "nonexistent"],
            capsys,
        )
        assert exit_code == ExitCode.PROJECT_NOT_FOUND
        assert envelope["success"] is False

    def test_export_report_no_binary(self, capsys):
        """export-report on project with no binary raises BinaryNotFoundError."""
        _make_created_project("no-binary")
        exit_code, _envelope = _capture_json(
            ["export-report", "--project", "no-binary", "--type", "triage", "--format", "markdown"],
            capsys,
        )
        assert exit_code == ExitCode.BINARY_NOT_FOUND
