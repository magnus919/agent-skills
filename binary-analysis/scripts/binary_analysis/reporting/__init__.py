"""Report generation — Markdown, JSON, HTML, PDF.

Provides authoritative Markdown and JSON report generation alongside optional
HTML and PDF renderings. Every report includes methodology and provenance
sections per the validation contract.

Also provides the audit event system for append-only, atomic event logging
to events.jsonl.
"""

from binary_analysis.reporting.audit import (
    audit_file_exists,
    clear_audit,
    read_audit_events,
    write_audit_event,
)
from binary_analysis.reporting.generator import (
    build_methodology,
    build_provenance,
    collect_focused_data,
    collect_project_data,
    collect_triage_data,
    generate_html_report,
    generate_json_report,
    generate_markdown_report,
    generate_pdf_report,
    write_report,
)

__all__ = [
    "audit_file_exists",
    "build_methodology",
    "build_provenance",
    "clear_audit",
    "collect_focused_data",
    "collect_project_data",
    "collect_triage_data",
    "generate_html_report",
    "generate_json_report",
    "generate_markdown_report",
    "generate_pdf_report",
    "read_audit_events",
    "write_audit_event",
    "write_report",
]
