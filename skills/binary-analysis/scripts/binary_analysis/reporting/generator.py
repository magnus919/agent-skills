"""Report generation — Markdown, JSON, HTML, PDF.

Produces self-contained reports from project analysis data. Markdown and JSON
are authoritative formats per ADR-008. HTML and PDF are optional renderings
derived from the canonical formats.

Every report includes:
- Methodology section: profile, rules_version, backend, adapter, parameters
- Full provenance: cli_version, project_id, binary_id, binary_sha256,
  analysis_id (UUID), generated_at

Report types:
- triage: Structured triage analysis output (observations, heuristics, unknowns)
- focused: Analysis focused on a specific entity (requires selector)
- project: Full project analysis state summary
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from binary_analysis import __version__ as _cli_version
from binary_analysis.domain.enums import ReportType

# ---------------------------------------------------------------------------
# Methodology builder
# ---------------------------------------------------------------------------


def build_methodology(
    profile: str = "standard",
    rules_version: str = "1.0.0",
    backend: str = "none",
    adapter: str = "none",
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the methodology section for a report.

    All fields must be non-null per the validation contract.

    Args:
        profile: Analysis profile used (e.g., "standard", "quick", "deep").
        rules_version: Version of the rules engine used.
        backend: Backend name (e.g., "Ghidra", "none").
        adapter: Adapter name (e.g., "ghidra", "fake").
        parameters: Any parameter overrides from defaults.

    Returns:
        Methodology dict with profile, rules_version, backend, adapter, parameters.
    """
    return {
        "profile": profile,
        "rules_version": rules_version,
        "backend": backend,
        "adapter": adapter,
        "parameters": parameters if parameters is not None else {},
    }


# ---------------------------------------------------------------------------
# Provenance builder
# ---------------------------------------------------------------------------


def build_provenance(
    *,
    cli_version: str | None = None,
    project_id: str | None = None,
    binary_id: str | None = None,
    binary_sha256: str | None = None,
    analysis_id: UUID | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build the provenance section for a report.

    Every report must include cli_version, project_id, binary_id,
    binary_sha256, analysis_id (UUID), and generated_at (ISO 8601).

    Two sequential reports on the same binary have different analysis_id values.

    Args:
        cli_version: CLI version string.
        project_id: Project UUID.
        binary_id: Binary UUID.
        binary_sha256: Binary SHA-256 hash (64 hex chars).
        analysis_id: Unique UUID for this analysis run (auto-generated if None).
        generated_at: ISO 8601 timestamp (auto-generated if None).

    Returns:
        Provenance dict with all required fields.
    """
    if analysis_id is None:
        analysis_id = uuid4()
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()

    return {
        "cli_version": cli_version or _cli_version,
        "project_id": project_id,
        "binary_id": binary_id,
        "binary_sha256": binary_sha256,
        "analysis_id": str(analysis_id),
        "generated_at": generated_at,
    }


# ---------------------------------------------------------------------------
# Report data collection
# ---------------------------------------------------------------------------


def collect_triage_data(
    manifest: dict[str, Any],
    adapter: Any,
    binary: Any,
    profile_name: str,
) -> dict[str, Any]:
    """Collect triage data from the analysis for a triage report.

    Args:
        manifest: Project manifest dict.
        adapter: Backend adapter instance.
        binary: Binary domain entity.
        profile_name: Analysis profile name.

    Returns:
        Dict with observations, heuristics, unknowns from triage analysis.
    """
    try:
        triage_result = adapter.run_triage(binary)
    except Exception:
        return {
            "observations": [],
            "heuristics": [],
            "unknowns": [],
            "partial": True,
            "error": "Triage analysis could not be completed.",
        }

    observations_data: list[dict[str, Any]] = []
    for obs in triage_result.observations:
        obs_dict: dict[str, Any] = {
            "category": obs.category,
            "description": obs.description,
            "source": obs.source,
        }
        if obs.address is not None:
            obs_dict["address"] = obs.address.to_dict()
        if obs.evidence is not None:
            obs_dict["evidence"] = obs.evidence
        observations_data.append(obs_dict)

    heuristics_data: list[dict[str, Any]] = []
    for heur in triage_result.heuristics:
        heur_dict: dict[str, Any] = {
            "name": heur.name,
            "description": heur.description,
            "confidence": heur.confidence.value,
        }
        if heur.rule_id is not None:
            heur_dict["rule_id"] = heur.rule_id
        if heur.evidence:
            heur_dict["evidence"] = heur.evidence
        heuristics_data.append(heur_dict)

    unknowns_data: list[dict[str, Any]] = []
    for unk in triage_result.unknowns:
        unk_dict: dict[str, Any] = {"question": unk.question}
        if unk.address is not None:
            unk_dict["address"] = unk.address.to_dict()
        if unk.category is not None:
            unk_dict["category"] = unk.category
        unknowns_data.append(unk_dict)

    return {
        "observations": observations_data,
        "heuristics": heuristics_data,
        "unknowns": unknowns_data,
        "partial": triage_result.partial,
    }


def collect_focused_data(
    adapter: Any,
    binary: Any,
    selector: str,
) -> dict[str, Any]:
    """Collect focused analysis data for a specific entity.

    Args:
        adapter: Backend adapter instance.
        binary: Binary domain entity.
        selector: Entity selector string (e.g., "function:main").

    Returns:
        Dict with focused entity data (decompilation, xrefs, etc.).
    """

    selector_lower = selector.lower()
    data: dict[str, Any] = {"selector": selector, "entity_type": "unknown"}

    if selector_lower.startswith("function:"):
        func_name = selector.split(":", 1)[1]
        try:
            functions = adapter.get_functions(binary)
            target = None
            for f in functions:
                if f.name == func_name or (
                    f.address is not None and f.address.display == func_name
                ):
                    target = f
                    break

            if target is None:
                data["error"] = f"Function not found: {func_name}"
                return data

            data["entity_type"] = "function"
            data["entity"] = {
                "name": target.name,
                "address": target.address.to_dict() if target.address else None,
                "size_bytes": target.size_bytes,
                "confidence": target.confidence.value,
                "name_source": target.name_source.value,
            }

            # Decompile
            try:
                decomp = adapter.decompile(binary, target)
                data["pseudocode"] = decomp.pseudocode if decomp else ""
                if decomp and decomp.address_map:
                    data["address_map"] = [
                        {
                            "line": am.line,
                            "address": am.address.to_dict() if am.address else None,
                        }
                        for am in decomp.address_map
                    ]
            except Exception:
                data["pseudocode"] = "(decompilation not available)"

            # Xrefs
            try:
                xrefs = adapter.get_xrefs(binary, target)
                data["xrefs"] = [
                    {
                        "from": x.from_addr.to_dict() if x.from_addr else None,
                        "to": x.to_addr.to_dict() if x.to_addr else None,
                        "kind": x.kind.value,
                        "confidence": x.confidence.value,
                    }
                    for x in xrefs
                ]
            except Exception:
                data["xrefs"] = []

            # Callers / Callees
            try:
                callers = adapter.get_callers(binary, target)
                data["callers"] = [
                    {
                        "name": c.caller_name if hasattr(c, "caller_name") else "unknown",
                        "address": c.caller_address.to_dict()
                        if hasattr(c, "caller_address") and c.caller_address
                        else None,
                    }
                    for c in callers
                ]
            except Exception:
                data["callers"] = []

            try:
                callees = adapter.get_callees(binary, target)
                data["callees"] = [
                    {
                        "name": c.callee_name if hasattr(c, "callee_name") else "unknown",
                        "address": c.callee_address.to_dict()
                        if hasattr(c, "callee_address") and c.callee_address
                        else None,
                    }
                    for c in callees
                ]
            except Exception:
                data["callees"] = []

        except Exception as e:
            data["error"] = str(e)

    return data


def collect_project_data(
    manifest: dict[str, Any],
    adapter: Any,
    binary: Any,
) -> dict[str, Any]:
    """Collect full project analysis state summary.

    Args:
        manifest: Project manifest dict.
        adapter: Backend adapter instance.
        binary: Binary domain entity.

    Returns:
        Dict with project metadata, sections, functions, etc.
    """
    data: dict[str, Any] = {
        "project": {
            "name": manifest.get("name", "unknown"),
            "state": manifest.get("state", "unknown"),
            "created_at": manifest.get("created_at"),
            "binary_count": manifest.get("binary_count", 0),
            "is_stale": manifest.get("is_stale", False),
        },
        "binary": {
            "id": str(binary.id) if binary else None,
            "sha256": binary.sha256 if binary else None,
            "format": binary.format if binary else None,
            "architecture": binary.architecture if binary else None,
            "size_bytes": binary.size_bytes if binary else 0,
        },
        "sections": [],
        "functions": [],
        "imports": [],
        "exports": [],
    }

    if binary is None:
        return data

    # Sections
    try:
        sections = adapter.get_sections(binary)
        data["sections"] = [
            {
                "name": s.name,
                "address": s.address.to_dict() if s.address else None,
                "virtual_size": s.virtual_size,
                "raw_size": s.raw_size,
                "flags": s.flags,
                "entropy": s.entropy,
            }
            for s in sections
        ]
    except Exception:
        pass

    # Functions
    try:
        functions = adapter.get_functions(binary)
        data["functions"] = [
            {
                "name": f.name,
                "address": f.address.to_dict() if f.address else None,
                "size_bytes": f.size_bytes,
                "confidence": f.confidence.value,
            }
            for f in functions[:100]
        ]
        data["function_count"] = len(functions)
    except Exception:
        data["function_count"] = 0

    # Imports
    try:
        imports = adapter.get_imports(binary)
        data["imports"] = [
            {
                "module": imp.module,
                "symbol": imp.symbol,
                "resolution": imp.resolution.value,
            }
            for imp in imports[:100]
        ]
        data["import_count"] = len(imports)
    except Exception:
        data["import_count"] = 0

    # Exports
    try:
        exports = adapter.get_exports(binary)
        data["exports"] = [
            {
                "name": exp.name,
                "address": exp.address.to_dict() if exp.address else None,
                "kind": exp.kind,
            }
            for exp in exports[:100]
        ]
        data["export_count"] = len(exports)
    except Exception:
        data["export_count"] = 0

    return data


# ---------------------------------------------------------------------------
# JSON report generation
# ---------------------------------------------------------------------------


def generate_json_report(
    report_type: ReportType,
    report_data: dict[str, Any],
    methodology: dict[str, Any],
    provenance: dict[str, Any],
) -> str:
    """Generate a JSON report as a string.

    The JSON output uses the canonical domain model schemas and is
    considered an authoritative format alongside Markdown per ADR-008.

    Args:
        report_type: Type of report (triage, focused, project).
        report_data: The collected report data.
        methodology: Methodology section dict.
        provenance: Provenance section dict.

    Returns:
        JSON string with the complete report envelope.
    """
    report = {
        "schema_version": "1.0.0",
        "report_type": report_type.value,
        "methodology": methodology,
        "provenance": provenance,
        "data": report_data,
    }
    return json.dumps(report, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Markdown report generation
# ---------------------------------------------------------------------------

# At module level for reusability in HTML conversion

_MD_HEADER_TPL = """# Binary Analysis Report

**Type:** {report_type}
**Generated:** {generated_at}

---

## Methodology

| Field | Value |
|-------|-------|
| Profile | {profile} |
| Rules Version | {rules_version} |
| Backend | {backend} |
| Adapter | {adapter} |

### Parameters

{parameters}

---

## Provenance

| Field | Value |
|-------|-------|
| CLI Version | {cli_version} |
| Project ID | {project_id} |
| Binary ID | {binary_id} |
| Binary SHA-256 | {binary_sha256} |
| Analysis ID | {analysis_id} |
| Generated At | {generated_at} |

---
"""


def _format_parameters(parameters: dict[str, Any]) -> str:
    """Format parameters dict as markdown table rows."""
    if not parameters:
        return "No parameter overrides."
    lines = ["| Parameter | Value |", "|-----------|-------|"]
    for k, v in parameters.items():
        lines.append(f"| {k} | {v} |")
    return "\n".join(lines)


def _format_address(addr: dict[str, Any] | None) -> str:
    """Format an address dict as a markdown code span."""
    if addr is None:
        return "`(null)`"
    return f"`{addr.get('display', addr.get('offset', 'unknown'))}`"


def generate_markdown_report(
    report_type: ReportType,
    report_data: dict[str, Any],
    methodology: dict[str, Any],
    provenance: dict[str, Any],
) -> str:
    """Generate a self-contained Markdown report.

    The Markdown output is self-contained with structured sections,
    headings, tables, and code blocks. It is an authoritative format
    alongside JSON per ADR-008.

    Args:
        report_type: Type of report (triage, focused, project).
        report_data: The collected report data.
        methodology: Methodology section dict.
        provenance: Provenance section dict.

    Returns:
        Markdown string with the complete report.
    """
    lines: list[str] = []

    # Header
    lines.append(
        _MD_HEADER_TPL.format(
            report_type=report_type.value,
            generated_at=provenance.get("generated_at", ""),
            profile=methodology.get("profile", "unknown"),
            rules_version=methodology.get("rules_version", "unknown"),
            backend=methodology.get("backend", "unknown"),
            adapter=methodology.get("adapter", "unknown"),
            parameters=_format_parameters(methodology.get("parameters", {})),
            cli_version=provenance.get("cli_version", "unknown"),
            project_id=provenance.get("project_id", "N/A"),
            binary_id=provenance.get("binary_id", "N/A"),
            binary_sha256=provenance.get("binary_sha256", "N/A"),
            analysis_id=provenance.get("analysis_id", "N/A"),
        )
    )

    # Report-specific content
    if report_type == ReportType.TRIAGE:
        _build_md_triage(lines, report_data)
    elif report_type == ReportType.FOCUSED:
        _build_md_focused(lines, report_data)
    elif report_type == ReportType.PROJECT:
        _build_md_project(lines, report_data)

    return "\n".join(lines)


def _build_md_triage(lines: list[str], data: dict[str, Any]) -> None:
    """Build Markdown sections for a triage report."""
    lines.append("## Triage Analysis\n")

    # Observations
    observations = data.get("observations", [])
    lines.append(f"### Observations ({len(observations)})\n")
    if observations:
        lines.append("| Category | Description | Source | Address |")
        lines.append("|----------|-------------|--------|---------|")
        for obs in observations:
            addr = _format_address(obs.get("address"))
            lines.append(
                f"| {obs.get('category', '')} | {obs.get('description', '')} "
                f"| {obs.get('source', '')} | {addr} |"
            )
    else:
        lines.append("_No observations recorded._")
    lines.append("")

    # Heuristics
    heuristics = data.get("heuristics", [])
    lines.append(f"### Heuristics ({len(heuristics)})\n")
    if heuristics:
        lines.append("| Name | Description | Confidence | Rule ID |")
        lines.append("|------|-------------|------------|---------|")
        for heur in heuristics:
            lines.append(
                f"| {heur.get('name', '')} | {heur.get('description', '')} "
                f"| {heur.get('confidence', '')} | {heur.get('rule_id', '')} |"
            )
    else:
        lines.append("_No heuristics generated._")
    lines.append("")

    # Unknowns
    unknowns = data.get("unknowns", [])
    lines.append(f"### Unknowns ({len(unknowns)})\n")
    if unknowns:
        for unk in unknowns:
            addr = _format_address(unk.get("address"))
            lines.append(f"- **Q:** {unk.get('question', '')}  ")
            lines.append(f"  Address: {addr}  ")
            if unk.get("category"):
                lines.append(f"  Category: {unk['category']}  ")
    else:
        lines.append("_No unresolved questions._")
    lines.append("")

    if data.get("partial"):
        lines.append("> **Note:** This report contains partial results.\n")


def _build_md_focused(lines: list[str], data: dict[str, Any]) -> None:
    """Build Markdown sections for a focused report."""
    lines.append("## Focused Analysis\n")
    lines.append(f"**Selector:** `{data.get('selector', 'N/A')}`\n")

    entity = data.get("entity", {})
    entity_type = data.get("entity_type", "unknown")

    if entity:
        lines.append(f"### {entity_type.title()}: {entity.get('name', 'unknown')}\n")
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        for k, v in entity.items():
            if k == "address" and isinstance(v, dict):
                lines.append(f"| {k} | {_format_address(v)} |")
            else:
                lines.append(f"| {k} | {v} |")
        lines.append("")

    # Pseudocode
    pseudocode = data.get("pseudocode")
    if pseudocode:
        lines.append("### Pseudocode\n")
        lines.append("```c")
        lines.append(pseudocode)
        lines.append("```\n")

    # Xrefs
    xrefs = data.get("xrefs", [])
    if xrefs:
        lines.append(f"### Cross-References ({len(xrefs)})\n")
        lines.append("| From | To | Kind | Confidence |")
        lines.append("|------|----|------|------------|")
        for x in xrefs:
            lines.append(
                f"| {_format_address(x.get('from'))} | {_format_address(x.get('to'))} "
                f"| {x.get('kind', '')} | {x.get('confidence', '')} |"
            )
        lines.append("")

    # Callers
    callers = data.get("callers", [])
    if callers:
        lines.append(f"### Callers ({len(callers)})\n")
        lines.append("| Name | Address |")
        lines.append("|------|---------|")
        for c in callers:
            lines.append(f"| {c.get('name', '?')} | {_format_address(c.get('address'))} |")
        lines.append("")

    # Callees
    callees = data.get("callees", [])
    if callees:
        lines.append(f"### Callees ({len(callees)})\n")
        lines.append("| Name | Address |")
        lines.append("|------|---------|")
        for c in callees:
            lines.append(f"| {c.get('name', '?')} | {_format_address(c.get('address'))} |")
        lines.append("")

    if data.get("error"):
        lines.append(f"> **Error:** {data['error']}\n")


def _build_md_project(lines: list[str], data: dict[str, Any]) -> None:
    """Build Markdown sections for a project report."""
    lines.append("## Project Summary\n")

    # Project metadata
    proj = data.get("project", {})
    bin_info = data.get("binary", {})

    lines.append("### Project\n")
    lines.append("| Property | Value |")
    lines.append("|----------|-------|")
    lines.append(f"| Name | {proj.get('name', 'unknown')} |")
    lines.append(f"| State | {proj.get('state', 'unknown')} |")
    lines.append(f"| Created | {proj.get('created_at', 'N/A')} |")
    lines.append(f"| Binary Count | {proj.get('binary_count', 0)} |")
    lines.append(f"| Stale | {proj.get('is_stale', False)} |")
    lines.append("")

    # Binary info
    lines.append("### Binary\n")
    lines.append("| Property | Value |")
    lines.append("|----------|-------|")
    lines.append(f"| ID | `{bin_info.get('id', 'N/A')}` |")
    lines.append(f"| SHA-256 | `{bin_info.get('sha256', 'N/A')}` |")
    lines.append(f"| Format | {bin_info.get('format', 'N/A')} |")
    lines.append(f"| Architecture | {bin_info.get('architecture', 'N/A')} |")
    lines.append(f"| Size | {bin_info.get('size_bytes', 0)} bytes |")
    lines.append("")

    # Sections
    sections = data.get("sections", [])
    lines.append(f"### Sections ({len(sections)})\n")
    if sections:
        lines.append("| Name | Address | Virtual Size | Raw Size | Flags | Entropy |")
        lines.append("|------|---------|-------------|----------|-------|---------|")
        for s in sections:
            lines.append(
                f"| {s.get('name', '')} | {_format_address(s.get('address'))} "
                f"| {s.get('virtual_size', 0)} | {s.get('raw_size', 0)} "
                f"| {', '.join(s.get('flags', []))} | {s.get('entropy', 'N/A')} |"
            )
    else:
        lines.append("_No sections available._")
    lines.append("")

    # Functions
    func_count = data.get("function_count", 0)
    functions = data.get("functions", [])
    lines.append(f"### Functions ({func_count})\n")
    if functions:
        lines.append("| Name | Address | Size | Confidence |")
        lines.append("|------|---------|------|------------|")
        for f in functions[:50]:
            lines.append(
                f"| {f.get('name', '')} | {_format_address(f.get('address'))} "
                f"| {f.get('size_bytes', 0)} | {f.get('confidence', '')} |"
            )
        if func_count > 50:
            lines.append(f"\n_Showing 50 of {func_count} functions._")
    else:
        lines.append("_No functions available._")
    lines.append("")

    # Imports
    imp_count = data.get("import_count", 0)
    imports = data.get("imports", [])
    lines.append(f"### Imports ({imp_count})\n")
    if imports:
        lines.append("| Module | Symbol | Resolution |")
        lines.append("|--------|--------|------------|")
        for imp in imports[:50]:
            lines.append(
                f"| {imp.get('module', '')} | {imp.get('symbol', '')} "
                f"| {imp.get('resolution', '')} |"
            )
        if imp_count > 50:
            lines.append(f"\n_Showing 50 of {imp_count} imports._")
    else:
        lines.append("_No imports available._")
    lines.append("")

    # Exports
    exp_count = data.get("export_count", 0)
    exports = data.get("exports", [])
    lines.append(f"### Exports ({exp_count})\n")
    if exports:
        lines.append("| Name | Address | Kind |")
        lines.append("|------|---------|------|")
        for exp in exports[:50]:
            lines.append(
                f"| {exp.get('name', '')} | {_format_address(exp.get('address'))} "
                f"| {exp.get('kind', '')} |"
            )
        if exp_count > 50:
            lines.append(f"\n_Showing 50 of {exp_count} exports._")
    else:
        lines.append("_No exports available._")
    lines.append("")


# ---------------------------------------------------------------------------
# HTML report generation (optional rendering)
# ---------------------------------------------------------------------------


def generate_html_report(
    report_type: ReportType,
    report_data: dict[str, Any],
    methodology: dict[str, Any],
    provenance: dict[str, Any],
) -> str:
    """Generate an HTML report derived from the canonical Markdown output.

    HTML is an optional rendering format (not authoritative). If a dependency
    is missing for rendering, the caller should fall back to the canonical
    Markdown path with a warning.

    Args:
        report_type: Type of report.
        report_data: The collected report data.
        methodology: Methodology section dict.
        provenance: Provenance section dict.

    Returns:
        HTML string with the rendered report.
    """
    md = generate_markdown_report(report_type, report_data, methodology, provenance)

    # Simple built-in Markdown-to-HTML conversion (no external dependency)
    html_lines: list[str] = []
    in_code_block = False
    in_table = False

    html_lines.append("<!DOCTYPE html>")
    html_lines.append('<html lang="en">')
    html_lines.append("<head>")
    html_lines.append('<meta charset="utf-8">')
    html_lines.append(f"<title>Binary Analysis Report — {report_type.value.title()}</title>")
    html_lines.append("<style>")
    html_lines.append(
        "body { font-family: system-ui, sans-serif; max-width: 900px; "
        "margin: 2rem auto; padding: 0 1rem; line-height: 1.6; }"
    )
    html_lines.append("table { border-collapse: collapse; width: 100%; margin: 1rem 0; }")
    html_lines.append("th, td { border: 1px solid #ccc; padding: 0.5rem; text-align: left; }")
    html_lines.append("th { background: #f5f5f5; }")
    html_lines.append("code { background: #f0f0f0; padding: 0.15em 0.3em; border-radius: 3px; }")
    html_lines.append(
        "pre { background: #f5f5f5; padding: 1rem; overflow-x: auto; border-radius: 4px; }"
    )
    html_lines.append("pre code { background: none; padding: 0; }")
    html_lines.append(
        "blockquote { border-left: 4px solid #ddd; margin: 1rem 0; "
        "padding: 0.5rem 1rem; color: #666; }"
    )
    html_lines.append("h2 { border-bottom: 1px solid #eee; padding-bottom: 0.3rem; }")
    html_lines.append("hr { border: none; border-top: 1px solid #eee; margin: 2rem 0; }")
    html_lines.append("</style>")
    html_lines.append("</head>")
    html_lines.append("<body>")

    for line in md.split("\n"):
        stripped = line.strip()

        # Code blocks
        if stripped.startswith("```"):
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
            else:
                html_lines.append("<pre><code>")
                in_code_block = True
            continue
        if in_code_block:
            html_lines.append(_html_escape(line))
            continue

        # Tables
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                html_lines.append("<table>")
                in_table = True
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            if all(c.startswith("-") for c in cells if c):
                continue  # Separator row
            # Determine if header row
            if html_lines[-1] == "<table>":
                tag = "th"
            else:
                prev = html_lines[-1]
                if prev.startswith("<tr>") and "</tr>" not in prev:
                    tag = "th"
                elif prev.startswith("</thead>"):
                    tag = "td"
            html_lines.append(
                "<tr>" + "".join(f"<{tag}>{_html_escape(c)}</{tag}>" for c in cells) + "</tr>"
            )
            continue
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False

        # Headings
        if stripped.startswith("# "):
            html_lines.append(f"<h1>{_html_escape(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{_html_escape(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{_html_escape(stripped[4:])}</h3>")
        elif stripped == "---":
            html_lines.append("<hr>")
        elif stripped.startswith("> "):
            html_lines.append(f"<blockquote>{_html_escape(stripped[2:])}</blockquote>")
        elif stripped.startswith("- "):
            html_lines.append(f"<li>{_html_escape(stripped[2:])}</li>")
        elif stripped.startswith("  "):
            html_lines.append(f"<br>{_html_escape(stripped)}")
        elif stripped.startswith("**") and stripped.endswith("**"):
            html_lines.append(f"<p><strong>{_html_escape(stripped[2:-2])}</strong></p>")
        elif stripped:
            # Inline code spans
            line_html = _html_escape_with_code(stripped)
            if not html_lines[-1].startswith("<"):
                html_lines.append(f"<p>{line_html}</p>")
            elif html_lines[-1] == "<body>" or html_lines[-1].startswith("<h"):
                pass  # Skip empty lines after body/headings
            else:
                html_lines.append(f"<p>{line_html}</p>")
        else:
            html_lines.append("")

    if in_table:
        html_lines.append("</table>")
    if in_code_block:
        html_lines.append("</code></pre>")

    html_lines.append("</body>")
    html_lines.append("</html>")
    return "\n".join(html_lines)


def _html_escape(text: str) -> str:
    """Escape HTML special characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _html_escape_with_code(text: str) -> str:
    """Escape HTML but preserve inline code spans."""
    result = _html_escape(text)
    # Restore code spans: `...` -> <code>...</code>
    import re

    result = re.sub(r"`([^`]+)`", r"<code>\1</code>", result)
    return result


# ---------------------------------------------------------------------------
# PDF report generation (optional rendering)
# ---------------------------------------------------------------------------


def generate_pdf_report(
    report_type: ReportType,
    report_data: dict[str, Any],
    methodology: dict[str, Any],
    provenance: dict[str, Any],
) -> tuple[str | None, str | None]:
    """Attempt to generate a PDF report.

    PDF is an optional rendering format (not authoritative). Requires a PDF
    generation dependency. Returns (pdf_path, error_message).

    If no PDF engine is available, returns (None, error_message) so the
    caller can fall back with a warning and the canonical path.

    Args:
        report_type: Type of report.
        report_data: The collected report data.
        methodology: Methodology section dict.
        provenance: Provenance section dict.

    Returns:
        Tuple of (output_path_or_None, error_message_or_None).
    """
    # Try to use weasyprint if available
    try:
        import weasyprint  # type: ignore[import-not-found] # noqa: F401
    except ImportError:
        pass
    else:
        html_content = generate_html_report(report_type, report_data, methodology, provenance)
        return (html_content, None)  # caller will write and convert

    # Try reportlab
    try:
        import reportlab  # type: ignore[import-untyped] # noqa: F401
    except ImportError:
        pass
    else:
        html_content = generate_html_report(report_type, report_data, methodology, provenance)
        return (html_content, None)

    # No PDF engine available
    return (None, "PDF rendering dependency unavailable (install weasyprint or reportlab)")


# ---------------------------------------------------------------------------
# High-level report generation
# ---------------------------------------------------------------------------


def write_report(
    project_path: str,
    report_type: ReportType,
    output_format: str,
    report_data: dict[str, Any],
    methodology: dict[str, Any],
    provenance: dict[str, Any],
) -> tuple[str, list[str]]:
    """Write a report file to the project's reports/ directory.

    Markdown and JSON are authoritative formats. HTML and PDF are optional
    renderings derived from the canonical formats.

    Args:
        project_path: Absolute path to the project workspace.
        report_type: Type of report (triage, focused, project).
        output_format: Output format (markdown, json, html, pdf).
        report_data: The collected report data.
        methodology: Methodology section dict.
        provenance: Provenance section dict.

    Returns:
        Tuple of (output_path, warnings_list).

    Raises:
        ValueError: If output_format is unsupported.
    """
    reports_dir = os.path.join(project_path, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    analysis_id = provenance.get("analysis_id", "unknown")[:8]
    fmt_ext = output_format.lower()
    # "markdown" maps to .md
    if fmt_ext == "markdown":
        fmt_ext = "md"

    filename = f"report-{report_type.value.lower()}-{analysis_id}.{fmt_ext}"
    output_path = os.path.join(reports_dir, filename)
    warnings: list[str] = []

    if output_format in ("markdown", "md"):
        content = generate_markdown_report(report_type, report_data, methodology, provenance)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    elif output_format == "json":
        content = generate_json_report(report_type, report_data, methodology, provenance)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    elif output_format == "html":
        content = generate_html_report(report_type, report_data, methodology, provenance)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    elif output_format == "pdf":
        html_content, pdf_error = generate_pdf_report(
            report_type, report_data, methodology, provenance
        )
        if pdf_error is not None:
            # PDF engine unavailable; write canonical Markdown instead
            md_filename = f"report-{report_type.value.lower()}-{analysis_id}.md"
            md_path = os.path.join(reports_dir, md_filename)
            content = generate_markdown_report(report_type, report_data, methodology, provenance)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(content)
            warnings.append(f"{pdf_error}. Wrote canonical Markdown report instead at: {md_path}")
            return md_path, warnings

        # Write the HTML, then convert to PDF if weasyprint is available
        try:
            import weasyprint

            pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
        except (ImportError, Exception) as e:
            # Fall back to canonical Markdown
            md_filename = f"report-{report_type.value.lower()}-{analysis_id}.md"
            md_path = os.path.join(reports_dir, md_filename)
            content = generate_markdown_report(report_type, report_data, methodology, provenance)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(content)
            warnings.append(
                f"PDF rendering failed: {e}. Wrote canonical Markdown report instead at: {md_path}"
            )
            return md_path, warnings

    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    return output_path, warnings
