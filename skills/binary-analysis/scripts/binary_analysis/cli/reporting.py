"""Reporting CLI commands — export-report and audit.

Implements the reporting commands for milestone: security-ship.

export-report: Produces Markdown (authoritative) and JSON (authoritative)
reports with methodology and provenance sections. HTML and PDF are optional
renderings only. Supports triage, focused (requires --selector), and project
report types.

audit: Lists append-only events from events.jsonl ordered by timestamp.
Events are atomic single-line JSON objects with command, args, result
(AuditResult enum), and duration_ms.
"""

from __future__ import annotations

import argparse
import time
from typing import Any

from binary_analysis.adapters.fake import FakeAdapter
from binary_analysis.cli.helpers import make_diagnostic, make_warning
from binary_analysis.domain.enums import AuditResult, ExitCode, ReportType
from binary_analysis.domain.errors import (
    BinaryNotFoundError,
    ProjectNotFoundError,
)
from binary_analysis.projects.manifest import load_manifest
from binary_analysis.projects.path_security import (
    validate_output_path,
)
from binary_analysis.projects.workspace import get_project_path, workspace_exists
from binary_analysis.reporting.audit import read_audit_events, write_audit_event
from binary_analysis.reporting.generator import (
    build_methodology,
    build_provenance,
    collect_focused_data,
    collect_project_data,
    collect_triage_data,
    write_report,
)

# ---------------------------------------------------------------------------
# Argument registration
# ---------------------------------------------------------------------------


def add_subparser(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Register export-report and audit subcommands."""
    report_parser = sub.add_parser(
        "export-report",
        help="Export analysis report in Markdown, JSON, HTML, or PDF",
        description=(
            "Export an analysis report from a project. Markdown and JSON "
            "are authoritative formats with methodology and provenance "
            "sections. HTML and PDF are optional renderings — if a rendering "
            "dependency is unavailable, the command exits 0 with a warning "
            "and the canonical Markdown path."
        ),
    )
    report_parser.add_argument(
        "--project",
        required=True,
        help="Project name or UUID containing the analysis.",
    )
    report_parser.add_argument(
        "--type",
        choices=["triage", "focused", "project"],
        default="triage",
        help="Report type: triage, focused, or project (default: triage).",
    )
    report_parser.add_argument(
        "--format",
        choices=["markdown", "json", "html", "pdf"],
        default="markdown",
        help="Output format: markdown, json, html, or pdf (default: markdown).",
    )
    report_parser.add_argument(
        "--selector",
        default=None,
        help="Entity selector for focused reports (e.g., 'function:main'). "
        "Required when --type focused.",
    )
    report_parser.add_argument(
        "--profile",
        default="standard",
        help="Analysis profile to reference in methodology (default: standard).",
    )
    report_parser.add_argument(
        "--output",
        default=None,
        help="Custom output path (must be within the project directory).",
    )

    audit_parser = sub.add_parser(
        "audit",
        help="List append-only audit events from events.jsonl",
        description=(
            "List all audit events from project/audit/events.jsonl ordered "
            "by timestamp. Events are atomic single-line JSON objects with "
            "command, args, result (AuditResult enum), and duration_ms. "
            "The audit file is append-only — events cannot be modified or "
            "deleted after being written."
        ),
    )
    audit_parser.add_argument(
        "--project",
        required=True,
        help="Project name or UUID to retrieve audit events for.",
    )


# ---------------------------------------------------------------------------
# Export-report command
# ---------------------------------------------------------------------------


def execute_export_report(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the export-report command.

    Produces a report file in the project's reports/ directory. Markdown
    and JSON are authoritative formats. HTML and PDF are optional renderings.

    Returns:
        A result dict with success, partial, warnings, diagnostics, data,
        and optional _exit_code for non-success paths.
    """
    t_start = time.perf_counter()
    project_name = args.project
    report_type_str = getattr(args, "type", "triage")
    output_format = getattr(args, "format", "markdown")
    selector = getattr(args, "selector", None)
    profile_name = getattr(args, "profile", "standard")

    # Validate report type
    try:
        report_type = ReportType(report_type_str.upper())
    except ValueError:
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                make_diagnostic(
                    f"Invalid report type: {report_type_str}. "
                    "Must be one of: triage, focused, project.",
                    severity="ERROR",
                    category="invalid-args",
                ),
            ],
            "data": None,
            "_exit_code": ExitCode.INVALID_ARGS,
        }

    # Focused requires --selector
    if report_type == ReportType.FOCUSED and not selector:
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                make_diagnostic(
                    "Focused report requires --selector (e.g., 'function:main').",
                    severity="ERROR",
                    category="invalid-args",
                ),
            ],
            "data": None,
            "_exit_code": ExitCode.INVALID_ARGS,
        }

    # Validate output format
    valid_formats = {"markdown", "md", "json", "html", "pdf"}
    if output_format not in valid_formats:
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                make_diagnostic(
                    f"Invalid output format: {output_format}. "
                    "Must be one of: markdown, json, html, pdf.",
                    severity="ERROR",
                    category="invalid-args",
                ),
            ],
            "data": None,
            "_exit_code": ExitCode.INVALID_ARGS,
        }

    # Validate project exists
    if not workspace_exists(project_name):
        raise ProjectNotFoundError(project_name)

    project_path = str(get_project_path(project_name))

    # Validate custom output path (VAL-SAFE-014)
    custom_output = getattr(args, "output", None)
    if custom_output:
        try:
            validated_output = validate_output_path(custom_output, project_path)
        except ValueError as e:
            return {
                "success": False,
                "partial": False,
                "warnings": [],
                "diagnostics": [
                    make_diagnostic(
                        f"Invalid output path: {e}",
                        severity="ERROR",
                        category="path_security",
                    ),
                ],
                "data": None,
                "_exit_code": ExitCode.GENERIC_ERROR,
            }
        _custom_output: str | None = validated_output
    else:
        _custom_output = None

    # Load project manifest
    manifest = load_manifest(project_path)

    # Check for binary
    current_binary = manifest.get("current_binary")
    if current_binary is None:
        raise BinaryNotFoundError()

    binary_id = current_binary.get("id", "unknown")
    binary_sha256 = current_binary.get("sha256", "unknown")
    binary_format = current_binary.get("format", "unknown")
    binary_arch = current_binary.get("architecture", "unknown")

    _prov_project_id = manifest.get("id")
    _prov_binary_id = binary_id
    _prov_binary_sha256 = binary_sha256
    _prov_project_state = manifest.get("state")

    # Build methodology
    methodology = build_methodology(
        profile=profile_name,
        rules_version="1.0.0",
        backend="FakeAdapter",
        adapter="fake",
        parameters={},
    )

    # Build provenance (with new analysis_id each time)
    provenance = build_provenance(
        project_id=_prov_project_id,
        binary_id=_prov_binary_id,
        binary_sha256=_prov_binary_sha256,
    )

    # Create adapter and load binary
    adapter = FakeAdapter()
    adapter.initialize()

    if binary_format == "ELF":
        fixture_name = "test-bin"
        adapter.set_fixture(fixture_name, FakeAdapter.elf_fixture())
    elif binary_format == "Mach-O":
        fixture_name = "test-bin"
        adapter.set_fixture(fixture_name, FakeAdapter.macho_fixture())
    else:
        fixture_name = "test-bin"
        adapter.set_fixture(fixture_name, FakeAdapter.pe_fixture())

    from uuid import UUID

    from binary_analysis.domain.entities import Binary

    binary = Binary(
        id=UUID(binary_id) if binary_id != "unknown" else UUID(int=0),
        sha256=binary_sha256,
        path=current_binary.get("path", ""),
        format=binary_format,
        architecture=binary_arch,
        size_bytes=current_binary.get("size_bytes", 0),
        analysis_profile=profile_name,
    )
    adapter._binaries[str(binary.id)] = {"binary": binary, "fixture_name": fixture_name}

    # Collect report data based on type
    report_data: dict[str, Any] = {}
    if report_type == ReportType.TRIAGE:
        report_data = collect_triage_data(manifest, adapter, binary, profile_name)
    elif report_type == ReportType.FOCUSED:
        report_data = collect_focused_data(adapter, binary, selector or "unknown")
    elif report_type == ReportType.PROJECT:
        report_data = collect_project_data(manifest, adapter, binary)

    # Write report
    try:
        output_path, write_warnings_list = write_report(
            project_path,
            report_type,
            output_format,
            report_data,
            methodology,
            provenance,
        )
    except ValueError as e:
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                make_diagnostic(
                    str(e),
                    severity="ERROR",
                    category="report-generation",
                ),
            ],
            "data": None,
            "_exit_code": ExitCode.GENERIC_ERROR,
            "_provenance_project_state": _prov_project_state,
            "_provenance_analysis_profile": profile_name,
            "_provenance_project_id": _prov_project_id,
            "_provenance_binary_id": _prov_binary_id,
            "_provenance_binary_sha256": _prov_binary_sha256,
        }

    # Build warnings from write_report and rendering fallback
    all_warnings: list[dict[str, Any]] = []
    for w in write_warnings_list:
        all_warnings.append(make_warning(w, category="report-rendering"))

    # Write audit event for report generation
    duration_ms = int((time.perf_counter() - t_start) * 1000)
    write_audit_event(
        project_path,
        command="export-report",
        result=AuditResult.SUCCESS,
        duration_ms=duration_ms,
        args={
            "type": report_type.value,
            "format": output_format,
            "selector": selector,
            "profile": profile_name,
        },
        project_id=_prov_project_id,
        binary_id=_prov_binary_id,
        details={"output_path": output_path},
    )

    return {
        "success": True,
        "partial": False,
        "warnings": all_warnings,
        "diagnostics": [],
        "data": {
            "report_path": output_path,
            "report_type": report_type.value,
            "format": output_format,
            "analysis_id": provenance.get("analysis_id"),
        },
        "_provenance_project_state": _prov_project_state,
        "_provenance_analysis_profile": profile_name,
        "_provenance_project_id": _prov_project_id,
        "_provenance_binary_id": _prov_binary_id,
        "_provenance_binary_sha256": _prov_binary_sha256,
    }


# ---------------------------------------------------------------------------
# Audit command
# ---------------------------------------------------------------------------


def execute_audit(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the audit command.

    Lists all audit events from events.jsonl ordered by timestamp. Events
    are atomic single-line JSON objects.

    Returns:
        A result dict with success, partial, warnings, diagnostics, data.
    """
    project_name = args.project

    # Validate project exists
    if not workspace_exists(project_name):
        raise ProjectNotFoundError(project_name)

    project_path = str(get_project_path(project_name))

    # Load project manifest
    manifest = load_manifest(project_path)

    _prov_project_id = manifest.get("id")
    _prov_project_state = manifest.get("state")

    # Read audit events
    events = read_audit_events(project_path)

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": {
            "events": events,
            "total": len(events),
        },
        "_provenance_project_state": _prov_project_state,
        "_provenance_project_id": _prov_project_id,
    }
