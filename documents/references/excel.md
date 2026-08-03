# Excel (.xlsx) — Generation & Validation Reference

> **Last Updated:** 2026-08-03

Load this reference when the target format is **Excel** — generating an .xlsx
workbook, modifying one, or validating a spreadsheet artifact. It complements
the shared workflow in `SKILL.md`; this file is the Excel-specific detail for
steps 3-5 (template, render, validate).

## XLSX fundamentals

An .xlsx file is an **OPC ZIP archive**:

- **`[Content_Types].xml`** — content types for workbook and worksheet parts.
- **`_rels/.rels`** — package relationships; points at `xl/workbook.xml`.
- **`xl/workbook.xml`** — sheet list (`<sheets><sheet name=... sheetId=...
  r:id=.../>`); the workbook-level relationships file
  `xl/_rels/workbook.xml.rels` maps each `r:id` to a worksheet part.
- **`xl/worksheets/sheetN.xml`** — cell data: `<sheetData>` with `<row>` and
  `<c r="A1">` cells. Cells hold values in `<v>` (numeric) or inline strings
  via `<is><t>`; shared strings live in `xl/sharedStrings.xml` and are
  referenced by index.
- **`xl/styles.xml`** — number formats, fonts, fills, column widths.
- **`xl/calcChain.xml`** and formula cells — `<f>` elements hold formulas;
  the `<v>` element holds the **cached** result.

The validation script checks the ZIP container, `[Content_Types].xml`,
`xl/workbook.xml`, at least one `xl/worksheets/sheetN.xml`, and their XML
well-formedness.

## Generation paths

### openpyxl (recommended)

`pip install openpyxl`, then build from the data model:

```python
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
ws.title = "Revenue"
ws.append(["Quarter", "Revenue"])   # row 1
ws.append(["Q1", 100])              # row 2
wb.save("data.xlsx")
```

Write headers first, then data rows; let the library handle shared strings and
styles. For large datasets, consider `write_only` mode to keep memory flat.

### Raw OPC construction (small, dependency-free artifacts)

For tiny workbooks, write the OOXML package directly with stdlib `zipfile` +
XML: `[Content_Types].xml`, `_rels/.rels`, `xl/workbook.xml`,
`xl/_rels/workbook.xml.rels`, and `xl/worksheets/sheet1.xml`. This is what the
bundled fixture `fixtures/sample.xlsx` does. Keep the
`xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"` namespace.

### CSV is not Excel

When the consumer only needs tabular data and never needs formatting,
formulas, or multiple sheets, a CSV is simpler and more robust than xlsx. Use
xlsx when the artifact itself is the deliverable.

## Validation specifics

```bash
python3 scripts/validate-documents.py --json data.xlsx
python3 scripts/validate-documents.py --render-check --json data.xlsx
```

Structural checks the script runs for XLSX:

- **ZIP container** — `PK..` magic; the file is a real archive.
- **Content types** — `[Content_Types].xml` present.
- **Workbook part** — `xl/workbook.xml` present and well-formed XML.
- **Worksheets** — at least one `xl/worksheets/sheetN.xml` present.
- **Text content** — informational check for cell markers.

The render check converts the workbook to PDF via LibreOffice and reports
`unavailable` when LibreOffice is not installed.

## Output-quality checklist for Excel

Before delivery, verify:

- **Headers on row 1** — a clear header row with column meaning, so the sheet
  is self-describing.
- **Values, not just formulas** — every `<f>` formula cell has a cached `<v>`
  result; viewers that do not recalculate show the cached value.
- **Number formats are right** — dates and currencies use the intended number
  format instead of raw serial numbers where users will be confused.
- **No broken references** — no `#REF!`/`#VALUE!` errors in cached values.
- **Column widths readable** — data is not clipped in the default view.
- **Sheet names meaningful** — default `Sheet1` is a smell for a deliverable.

See [references/output-quality.md](output-quality.md) for the cross-format
version of this checklist.
