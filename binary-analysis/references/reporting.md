# Reports: Generation & Interpretation

How to generate and interpret analysis reports with `binary export-report`.
Load this when the user asks to "generate a report," when presenting final
findings, or when you need to understand report structure and content.

## Report Overview

The `binary export-report` command produces durable, auditable reports from
project analysis data. Reports serve as the handoff artifact between the agent
and the user.

### Report Types

| Type | Flag | What It Contains | When to Use |
|------|------|-----------------|-------------|
| Triage | `--type triage` | Observations, heuristics, unknowns, methodology, provenance | After running `binary triage` on an unknown binary. The default report type. |
| Focused | `--type focused` | Analysis of a specific function with decompilation, xrefs, and call graph | After deep-diving into a specific function. Requires `--selector`. |
| Project | `--type project` | Full project summary: all binaries, analyses, timeline, audit trail | For comprehensive documentation of an entire analysis project. |

### Report Formats

| Format | Flag | Authoritative? | Notes |
|--------|------|---------------|-------|
| Markdown | `--format markdown` | **Yes** | Self-contained, diffable, structured with headings, tables, code blocks. Default. |
| JSON | `--format json` | **Yes** | Canonical schema, machine-readable. Full fidelity. |
| HTML | `--format html` | No | Rendered from Markdown. Optional — if rendering dependency is unavailable, exits 0 with a warning. |
| PDF | `--format pdf` | No | Rendered from Markdown. Optional — same fallback behavior as HTML. |

Markdown and JSON are the authoritative formats. They are committed to the
project's `reports/` directory. HTML and PDF are renderings — they may not
include every detail (e.g., very long code blocks may be truncated in PDF
pagination).

## Generating Reports

### Triage Report

```bash
binary export-report --project <proj> --type triage --format markdown --json
```

Produces a Markdown report with sections for:
- **Binary Identity**: SHA-256, format, architecture, size, compile timestamp.
- **Methodology**: Analysis profile, rules version, backend, adapter,
  parameters.
- **Structural Summary**: Sections, entry points, import/export counts.
- **Observations**: Deterministic facts from the backend.
- **Heuristics**: Rule-derived interpretations with confidence scores.
- **Unknowns**: Unresolved questions at specific addresses.
- **Security Assessment**: Suspicious API matches and capability map.
- **Diagnostics**: Any analysis limitations, timeouts, or partial failures.
- **Provenance**: CLI version, schema version, adapter, backend, binary SHA-256,
  analysis ID (UUID), generation timestamp.

### Focused Report

```bash
binary export-report --project <proj> --type focused --selector function:main --format markdown --json
```

Produces a Markdown report focused on a single function:
- **Function Identity**: Name, address, size, name source, confidence.
- **Pseudocode**: Reconstructed C-like code with address map.
- **Disassembly** (optional, if requested): Instruction listing.
- **Callers**: Functions that call this function.
- **Callees**: Functions called by this function.
- **Cross-References**: References to and from this function.
- **Agent Assessment Section** (empty — for you to fill in).

`--selector` is required for focused reports. Use standard selector syntax:
`function:<name>` or `function:<address>`.

### Project Report

```bash
binary export-report --project <proj> --type project --format markdown --json
```

Produces a comprehensive project report:
- **Project Summary**: Creation date, last updated, total binaries, current
  state.
- **Binary List**: All binaries in the project with SHA-256, format, import
  counts.
- **Analysis Timeline**: When each analysis was run, profiles used, durations.
- **Audit Trail**: Key events from `events.jsonl`.
- **Report Inventory**: All previously generated reports in this project.

## Report Structure (Markdown)

Every Markdown report follows this structure:

```
# <Report Title>
**Generated:** <timestamp>
**Analysis ID:** <uuid>

## Binary Identity
| Field | Value |
|-------|-------|
| SHA-256 | <hash> |
| Format | PE |
| Architecture | x86-64 |
| Size | 45,632 bytes |
| Entry Point | 0x140001000 |

## Methodology
| Parameter | Value |
|-----------|-------|
| Profile | standard |
| Rules Version | 1.0.0 |
| Backend | Ghidra 12.1.2 |
| Adapter | PyGhidra 3.1.0 |
| Timeout | 300s |
...

## Structural Summary
...

## Observations
...

## Heuristics
...

## Unknowns
...

## Security Assessment
...

## Diagnostics
...

## Provenance
| Field | Value |
|-------|-------|
| CLI Version | 0.1.0 |
| Schema Version | 1.0.0 |
| Binary SHA-256 | <hash> |
| Analysis ID | <uuid> |
| Generated At | <timestamp> |
```

## Report Structure (JSON)

JSON reports follow the canonical schema. The top-level structure mirrors the
CLI envelope but with report-specific metadata:

```json
{
  "report_type": "triage",
  "report_id": "<uuid>",
  "generated_at": "<iso8601>",
  "methodology": {
    "profile": "standard",
    "rules_version": "1.0.0",
    "backend": {"name": "Ghidra", "version": "12.1.2"},
    "adapter": {"name": "PyGhidra", "version": "3.1.0"}
  },
  "provenance": {
    "cli_version": "0.1.0",
    "project_id": "<uuid>",
    "binary_id": "<uuid>",
    "binary_sha256": "<hex>",
    "analysis_id": "<uuid>"
  },
  "content": {
    "observations": [...],
    "heuristics": [...],
    "unknowns": [...]
  },
  "diagnostics": [...]
}
```

## Understanding Report Content

### Provenance Block

Every report includes full provenance. **Always include provenance when citing
report findings:**

- `cli_version`: The exact CLI version used to generate this report. Important
  for reproducibility.
- `binary_sha256`: The SHA-256 of the analyzed binary. Findings are only valid
  for this exact binary.
- `analysis_id`: A UUID uniquely identifying this analysis run. Used to trace
  back to audit events.
- `backend` / `adapter`: The specific versions used. Different versions may
  produce different results.

### Methodology Section

Documents HOW the analysis was performed:
- Which analysis profile was used (`standard`, `quick`, `deep`).
- Which rule set version was evaluated.
- Operation parameters (timeout, limit, etc.).
- This allows someone to reproduce the analysis by running the same commands.

### Observations (Deterministic)

These are facts. They have no `confidence` field. They are true regardless of
interpretation. When you cite an observation in your agent assessment, you're
citing a verified measurement.

### Heuristics (Rule-Derived)

These are interpretations with `confidence` levels. Each heuristic lists:
- The `rule_id` that produced it.
- The `confidence` score.
- The `evidence` that triggered the rule.

When you cite a heuristic, always include the confidence level.

### Unknowns (Gaps)

These are explicit "we don't know" entries. Each has:
- An `address` where the unknown was identified.
- A `question` that could not be answered.

Unknowns are not failures — they are a structured way to identify next steps.

## Custom Output Path

By default, reports are written to `<project-dir>/reports/`. Use `--output` to
specify a custom path (must be within the project directory):

```bash
binary export-report --project <proj> --type triage --output reports/my-triage-report.md --json
```

The path is validated for workspace containment — paths outside the project
directory are rejected.

## Report Limits

- Maximum report size follows the global `--max-output-size` limit (default
  64MB, max 256MB). If the report would exceed this, it is truncated with a
  diagnostic.
- JSON reports may be large for complex binaries. Use Markdown for human
  consumption unless you need programmatic access.
- Focused reports with very large functions (thousands of basic blocks) may
  time out during pseudocode generation. The report includes a diagnostic.

## Audit Trail

The audit command provides a chronological log of all operations on a project:

```bash
binary audit --project <proj> --json
```

Each audit event is a single-line JSON object in `events.jsonl`:
- `command`: The CLI command that was run.
- `args`: The arguments passed.
- `result`: SUCCESS, PARTIAL, FAILED, CANCELLED, or REFUSED.
- `duration_ms`: How long the command took.
- `timestamp`: When the command was executed.

**Audit events are append-only and atomic** — each event is written as a single
line with no interleaving. Audit events are never modified or deleted.

### Using Audit for Verification

The audit trail allows you to verify:
- Which analysis steps were actually performed (not just claimed).
- Whether the analysis profile matches what the report says.
- Whether any commands failed or returned partial results.
- The timeline of the analysis (did triage run before or after focused
  analysis?).

## Generating Reports Without Ghidra

Reports require a project with analyzed data. If Ghidra is not available:

1. The project must have been previously analyzed with Ghidra.
2. The analysis output (in the project's cache) is used to generate reports.
3. You cannot generate a report for an unanalyzed project without Ghidra.

## After Generating a Report

1. **Read the report** — it's in the project's `reports/` directory.
2. **Fill in the Agent Assessment section** — the report has a placeholder for
   your synthesis. Write your interpretation there, clearly separated from CLI
   evidence.
3. **Verify completeness:**
   - All evidence categories are populated.
   - Diagnostics are acknowledged (don't hide partial results).
   - Provenance is correct (binary SHA-256, tool versions).
4. **Present to the user:**
   - Summarize key findings.
   - Point to the report file for the full details.
   - Note any limitations or recommended follow-ups.

## Report Inventory

List all reports generated for a project:

```bash
ls <project-dir>/reports/
```

Each report filename includes the report type and timestamp:
```
triage-2026-07-30T120000Z.md
focused-main-2026-07-30T121500Z.md
project-2026-07-30T123000Z.md
```

## Comparison Across Reports

When you generate multiple reports for the same binary (e.g., a triage report
and a focused report on a suspicious function), they share:
- The same `binary_sha256`.
- The same `project_id`.
- Different `analysis_id` values (each report run is uniquely identified).

This means findings can be cross-referenced across reports by binary hash.
