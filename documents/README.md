# Documents — PDF, Word, Excel & PowerPoint Skill

One skill that lets your agent generate, inspect, validate, and fix PDF, Word (.docx), Excel (.xlsx), and PowerPoint (.pptx) files — with a shared workflow, per-format references, and a validation script that verifies output quality before anything ships.

## Why Install This Skill

Document output is one of the most common things people ask agents to produce, yet it is easy to get subtly wrong: files that open in one viewer but corrupt in another, spreadsheets with broken cell references, decks with missing slide relationships. This skill packages the full generation-to-delivery loop so your agent produces files that are structurally sound and actually render.

After installing, your agent can turn a markdown brief into a formatted PDF, build a Word report with proper headings and tables, generate a spreadsheet from CSV data, assemble a slide deck from an outline — and then run the included validation script on every artifact to prove it is well-formed before you ever open it. Because the four formats share one workflow, one skill covers them all; you do not need four overlapping skills with four sets of instructions to maintain.

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Shared six-step workflow (scope → content model → template → render → validate → deliver) with per-format load-on-demand |
| `references/pdf.md` | PDF generation, tooling, and validation specifics |
| `references/word.md` | Word (.docx) package layout, generation, and validation specifics |
| `references/excel.md` | Excel (.xlsx) workbook structure, generation, and validation specifics |
| `references/powerpoint.md` | PowerPoint (.pptx) deck structure, generation, and validation specifics |
| `references/output-quality.md` | Cross-format output-quality checklist for all four formats |
| `scripts/validate-documents.py` | Stdlib-only validation script: structural sanity + optional render check, with `--json` output and graceful degradation when no renderer is installed |
| `templates/pdf-template.md` | Fillable generation template for PDF (print-ready HTML/CSS or LaTeX) |
| `templates/word-template.md` | Fillable generation template for Word documents |
| `templates/excel-template.md` | Fillable generation template for Excel workbooks |
| `templates/powerpoint-template.md` | Fillable generation template for PowerPoint decks |
| `fixtures/` | One small valid sample per format, used to smoke-test the validation script |

## Quick Start

```bash
# Validate a finished artifact (human report)
python3 scripts/validate-documents.py report.pdf

# Validate with a render check and machine-readable output
python3 scripts/validate-documents.py --render-check --json report.pdf data.xlsx deck.pptx

# Smoke-test the script against the bundled per-format fixtures
python3 scripts/validate-documents.py --json fixtures/sample.pdf fixtures/sample.docx fixtures/sample.xlsx fixtures/sample.pptx
```

The render check uses `pdftoppm` (poppler-utils) for PDF and LibreOffice for Office formats when they are installed. When neither is present, validation still performs full structural checks and reports the render check as `unavailable` instead of failing — no renderer required to use the skill.

## Triggers

Load this skill when the user mentions any of:

- **Generating documents**: "create a PDF report", "make a Word document", "turn this CSV into a spreadsheet", "build a slide deck"
- **Editing documents**: "update the docx", "change the Excel file", "fix this presentation"
- **Extracting from documents**: "read the text from this PDF", "pull the table out of this xlsx"
- **Converting**: "docx to PDF", "export this data as an Excel file"
- **Validating**: "check that this document is valid", "why won't this file open", "verify the output before sending"

Do not load for ebooks (use the `epub` skill), image/video/media production, or data pipeline work (use `data-engineering`).

## Requirements

- Python 3.8+ — the validation script uses only the standard library.
- Optional renderers (only for the render-check step): `pdftoppm`/`mutool`/`ghostscript` for PDF, `libreoffice`/`soffice` for Office formats. Generation libraries such as python-docx, openpyxl, or python-pptx are optional per format and documented in the references.
