# Output-Quality Validation — All Four Formats

> **Last Updated:** 2026-08-03

Load this reference when you need to **verify a produced document before
delivery**, regardless of format. It is step 5 (validate) of the shared
workflow in `SKILL.md`, expanded into a checklist that applies to PDF, Word,
Excel, and PowerPoint alike, plus the exact behavior of the validation script.

## Why validate at all

The most common document defects are structural, not typographical: a file
that opens in one application and corrupts in another, a spreadsheet whose
cells are invisible to formulas, a deck whose slides do not render. Structural
validation catches these before delivery, cheaply and deterministically, and a
render check catches the next class (layout, fonts, overflow) whenever a
renderer is available.

## Two layers of checking

### 1. Structural sanity (always available, stdlib only)

The validation script checks properties that any reader depends on:

| Format | Checks |
|--------|--------|
| PDF | `%PDF-` header, `%%EOF` trailer, at least one page object |
| Word (.docx) | ZIP container, `[Content_Types].xml`, `word/document.xml` well-formed |
| Excel (.xlsx) | ZIP container, `[Content_Types].xml`, `xl/workbook.xml` + worksheet parts well-formed |
| PowerPoint (.pptx) | ZIP container, `[Content_Types].xml`, `ppt/presentation.xml` + slide parts well-formed |

These checks need no third-party packages, so validation always runs.

### 2. Render check (best effort, graceful)

When an external renderer is installed, the script additionally **renders the
file** — `pdftoppm`/`mutool`/`gs` rasterize PDF page 1; LibreOffice converts
Office formats to PDF. When no renderer is available for a format, the render
check reports `unavailable` in the JSON and exits 0: a missing renderer is an
environment fact, not a document defect. Never block delivery on a render
check you could not run; say so in the provenance instead.

## Running the validation script

```bash
python3 scripts/validate-documents.py report.pdf brief.docx data.xlsx deck.pptx
python3 scripts/validate-documents.py --render-check --json report.pdf data.xlsx
```

Exit codes:

- **0** — every file passes structural validation (and any attempted render
  succeeded, or no renderer was available).
- **1** — at least one file fails structure or an attempted render failed.
- **2** — usage/I/O error (missing or unreadable path).

JSON report (`--json`): top-level `status` is `ok`, `fail`, `unavailable`, or
`error`; each file carries per-check results and a `render` object. The
`summary` block gives the pass/fail/skip/error counts.

## Content-completeness checks

Structure passing does not mean the content is right. Before delivery, confirm
the artifact matches the agreed scope:

- **Expected sections present** — the scope's headings/slides/sheets all exist.
- **No placeholder remnants** — no unresolved `[fill: ...]` markers, `TODO`
  text, or lorem ipsum from the template.
- **Data intact** — for Excel, spot-check cell values against the source data;
  for prose, check a few paragraphs verbatim.
- **Metadata set** — title/author where the reader displays it.

## Visual and layout quality

Renderer-dependent, so verify when a renderer is available or by opening the
artifact:

- **No overflow** — text fits boxes/cells/slides; no clipped content.
- **No missing glyphs** — fonts embedded (PDF) or available (Office); no
  `tofu` boxes.
- **Consistent styling** — headings use styles; decks use one layout family.
- **Page/slide count matches the scope** — no blank trailing pages/slides.

## Accessibility basics

Accessibility is part of output quality, not a separate concern:

- **PDF** — tagged PDFs with real text (not scans) and a reading order.
- **Word** — heading styles (they become the navigation/outline), alt text on
  images, real tables with header rows.
- **Excel** — header rows on row 1, no blank separator rows inside tables,
  meaningful sheet names.
- **PowerPoint** — alt text on images, sensible shape reading order, notes.

## The deliverable gate

A document is ready to deliver when:

1. `scripts/validate-documents.py` exits 0 on it (structure passed).
2. The render check is `ok` (renders) **or** honestly reported as
   `unavailable` (no renderer present).
3. Content-completeness and visual checks pass against the scope.
4. The provenance records the content model, template version, and validation
   result, so the artifact can be regenerated and re-verified.

Anything less is a known deviation — record it rather than hiding it.
