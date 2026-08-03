# Word (.docx) — Generation & Validation Reference

> **Last Updated:** 2026-08-03

Load this reference when the target format is **Word** — generating an
editable .docx, modifying one, or validating a Word artifact. It complements
the shared workflow in `SKILL.md`; this file is the Word-specific detail for
steps 3-5 (template, render, validate).

## DOCX fundamentals

A .docx file is an **OPC (Open Packaging Conventions) ZIP archive**:

- **`[Content_Types].xml`** — declares the content type of every part.
- **`_rels/.rels`** — package relationships; points at the main document part.
- **`word/document.xml`** — the document body: `w:p` (paragraphs) containing
  `w:r` (runs) containing `w:t` (text); `w:tbl` for tables; `w:sectPr` for
  section properties.
- **`word/styles.xml`** — named styles (`w:style` with `w:styleId`); the
  document references them with `w:pStyle`/`w:rStyle`.
- **`word/media/`** — embedded images referenced via relationships in
  `word/_rels/document.xml.rels`.
- **`word/header*.xml` / `word/footer*.xml`** — headers and footers.
- **`docProps/core.xml`** — metadata (title, author, dates).

Content lives in `word/document.xml`; everything else supports it. The
validation script checks the ZIP container, `[Content_Types].xml`, the
`word/document.xml` part, and its XML well-formedness.

## Generation paths

### python-docx (recommended for prose documents)

`pip install python-docx`, then build from the content model:

```python
from docx import Document
doc = Document()
doc.add_heading(title, level=0)
for heading, body in sections:
    doc.add_heading(heading, level=1)
    doc.add_paragraph(body)
doc.save("report.docx")
```

Use styles (`add_heading` applies built-in heading styles) rather than
manual formatting so the document stays navigable and re-styleable.

### Pandoc (markdown → docx)

`pandoc report.md -o report.docx` produces clean, style-based output and is
ideal when the content model is markdown. Use a reference doc (`--reference-doc`)
to control styles.

### Raw OPC construction (small, dependency-free artifacts)

For tiny or highly controlled documents, write the OOXML package directly with
stdlib `zipfile` + XML: `[Content_Types].xml`, `_rels/.rels`,
`word/document.xml`, and optional `word/styles.xml`. This is what the bundled
fixture `fixtures/sample.docx` does. Keep the XML namespaced correctly
(`xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"`).

## Validation specifics

```bash
python3 scripts/validate-documents.py --json brief.docx
python3 scripts/validate-documents.py --render-check --json brief.docx
```

Structural checks the script runs for DOCX:

- **ZIP container** — `PK..` magic; the file is a real archive.
- **Content types** — `[Content_Types].xml` present.
- **Main part** — `word/document.xml` present and well-formed XML.
- **Text content** — informational check for `w:t` text markers.

The render check converts the file to PDF via LibreOffice (`--headless
--convert-to pdf`) and reports `unavailable` when LibreOffice is not installed.

## Output-quality checklist for Word

Before delivery, verify:

- **Styles, not ad-hoc formatting** — headings use heading styles so the
  navigation pane and TOC work.
- **Tables are real tables** — `w:tbl` structure, not tab-separated text.
- **Images are embedded** — media parts exist and are referenced, not hot-linked.
- **No unresolved fields** — update or remove stale TOC/field placeholders.
- **Spellable, openable text** — text is in `w:t` runs, not encoded oddly.
- **Header/footer present when required** — page numbers, document title.

See [references/output-quality.md](output-quality.md) for the cross-format
version of this checklist.
