# PDF — Generation & Validation Reference

> **Last Updated:** 2026-08-03

Load this reference when the target format is **PDF** — generating a
fixed-layout document, converting content to PDF, or validating a PDF artifact.
It complements the shared workflow in `SKILL.md`; this file is the PDF-specific
detail for steps 3-5 (template, render, validate).

## PDF fundamentals

A PDF file is a linear byte stream, not a container:

- **Header** — `%PDF-1.x` near the start (x = 2..7 in practice).
- **Body** — numbered indirect objects (`N 0 obj ... endobj`): a catalog
  (`/Type /Catalog`), page tree (`/Type /Pages` with `/Kids` and `/Count`),
  page objects (`/Type /Page`), content streams, and font objects.
- **Cross-reference table (xref)** — byte offsets of every object, which lets
  readers jump straight to an object; followed by the `trailer` with `/Root`.
- **`startxref`** — byte offset of the xref table; **`%%EOF`** terminates the
  file.

The validation script checks exactly the properties that break in real life:
the `%PDF-` header, the `%%EOF` trailer, and the presence of page objects. A
file that opens in one viewer but not another is almost always a broken xref
or a stream whose `/Length` does not match its content — see
`references/output-quality.md` for the cross-format checklist.

## Generation paths

PDF is a **fixed-layout** format: the author, not the reader, decides where
every glyph lands. Choose the path by how much layout control you need.

### Print-ready HTML/CSS (recommended for reports and memos)

Author the document as HTML with print CSS (`@page` rules, page breaks,
`@media print`), then render to PDF with a print-capable engine:

- **WeasyPrint** (Python, pip installable) — excellent CSS paged-media support;
  embed fonts via `@font-face`.
- **Headless Chromium** (`--headless --print-to-pdf`) — full CSS support, best
  for complex layouts; pass `--no-pdf-header-footer` for clean output.

Keep the content in the content model (step 2 of the shared workflow), fill
[templates/pdf-template.md](../templates/pdf-template.md), and render. The
template is the layout contract; the HTML/CSS is where fonts, margins, and
page breaks live.

### LaTeX (best for technical and long-form documents)

Write LaTeX source from the content model and compile with a TeX toolchain
(`pdflatex`, `xelatex`). Gives precise typography, references, and TOC
control. Costs: a toolchain dependency and a longer render cycle.

### Direct PDF construction (small, dependency-free artifacts)

For tiny fixed artifacts (a one-page certificate, a label), a minimal PDF can
be written by hand with stdlib only: build the objects, compute the xref
offsets, and write the trailer. Keep streams short and compute `/Length`
exactly. This is what the bundled fixture `fixtures/sample.pdf` does.

### What not to do

- Do not fake a PDF by renaming a text file — every PDF must start with the
  `%PDF-` header and end with `%%EOF`; readers will reject anything else.
- Do not generate a PDF that relies on fonts that will not be embedded;
  unembedded fonts render as garbage or get substituted (see output quality).
- Do not rasterize text to images unless the document is genuinely a scan;
  text should stay selectable.

## Text extraction (reading a PDF)

PDF is a rendering format, so "reading" it means extracting text:

- **pypdf** (`pip install pypdf`) — extract text per page: `PageObject.extract_text()`.
- **pdfminer.six** — more accurate layout-aware extraction for complex layouts.
- **pdftotext** (poppler-utils) — fast CLI extraction for simple documents.

Extraction quality varies with how the PDF was produced. Scanned PDFs contain
no text layer at all — they are images; extraction requires OCR, which is
outside this skill's scope.

## Validation specifics

```bash
python3 scripts/validate-documents.py --json report.pdf
python3 scripts/validate-documents.py --render-check --json report.pdf
```

Structural checks the script runs for PDF:

- **PDF header** — `%PDF-` signature near the start.
- **EOF marker** — `%%EOF` trailer near the end.
- **Page objects** — at least one `/Type /Page` object.

The render check renders page 1 to a raster via `pdftoppm` (or `mutool`/`gs`)
and reports `unavailable` when no renderer is installed.

## Output-quality checklist for PDF

Before delivery, verify:

- **Pages render** — the render check succeeds; no blank or corrupt pages.
- **Text is selectable** — a content-stream text marker (BT/ET) is present
  unless the document is intentionally a scan.
- **Fonts are embedded** — no `missing glyph` boxes; embed via the generator's
  font options.
- **Page count matches the scope** — no accidental blank trailing pages.
- **Links and bookmarks** — internal links and the outline are functional.
- **Metadata** — title/author set where the reader will show them.

See [references/output-quality.md](output-quality.md) for the cross-format
version of this checklist.
