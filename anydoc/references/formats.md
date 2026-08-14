# Formats: what anydoc converts and what GFM you get

This reference documents every input format the pinned CLI (`@firecrawl/anydoc`
v0.1.6) accepts, the GitHub-Flavored Markdown each one produces, and the
fidelity caveats you must know before trusting the output. Every claim below
was verified by running the real CLI against the committed fixtures in
`fixtures/` (see [sources.md](sources.md) for provenance and the verification
procedure).

## Coverage: 8 families / 21 extensions / 12 parsers

| Family | Extensions | Canonical parser |
| --- | --- | --- |
| Word | `.doc`, `.docx`, `.docm` | `doc` (legacy OLE) / `docx` (`.docm` aliases to `docx`) |
| PowerPoint | `.ppt`, `.pps`, `.pot`, `.pptx`, `.pptm`, `.ppsx`, `.ppsm` | `ppt` (`.pps`, `.pot` alias to `ppt`) / `pptx` (`.pptm`, `.ppsx`, `.ppsm` alias to `pptx`) |
| Excel | `.xls`, `.xlsx`, `.xlsm`, `.xlsb` | `xlsx` (all four; calamine reads both OLE and ZIP) |
| OpenDocument | `.odt`, `.ods`, `.odp` | `odt`, `ods`, `odp` |
| Rich Text Format | `.rtf` | `rtf` |
| EPUB | `.epub` | `epub` |
| CSV | `.csv` | `csv` |
| PDF | `.pdf` | `pdf` |

That is **8 families, 21 extensions, 12 canonical parsers**: `doc, docx, odt,
pdf, ppt, pptx, rtf, epub, xlsx, ods, odp, csv`. These 12 names are also the
values accepted by `--format`; extension aliases resolve through the same
mapping (verified: `--format xls` and `--format docm` are accepted).

Format detection reads the file *bytes* first (PDF header, RTF open group, OLE
stream names, ZIP mimetype/content types). CSV has no content signature, so it
falls back to the extension or to an explicit `--format`.

## Shared output behavior

All document formats flow through one shared document model and one GFM
serializer, so identical logical structure yields near-identical Markdown
across formats. Behaviors you can rely on everywhere:

- Headings render as `#`–`######` with anchors.
- Inline runs preserve **bold**, *italic*, ~~strike~~, `` `code` ``, and lists
  (bullet, numbered, nested, roman).
- GFM tables with header rows; merged cells render as **empty covered spans**.
- Footnotes/endnotes: `[^n]` reference inline, with `[^n]: ...` definition
  lines at the end of the document.
- Markdown specials in source text are escaped (`\*stars*`, `\| pipe`).
- Embedded images render as their **alt text only** — raw image bytes never
  survive into Markdown.
- Bookmarks/anchor targets render as raw `<a id="..."></a>` markers.

## Word (`.doc`, `.docx`, `.docm`)

Expected output: `#` title, `##`/`###` section headings, inline emphasis,
GFM tables, `[^n]` footnotes. DOCX, DOC, ODT, and RTF all share this document
shape; the same fixture converted as `.doc`, `.odt`, and `.rtf` produced
near-identical markdown.

Real conversion of `fixtures/fixture-handmade-outline.docx`:

```markdown
## Style heading stays a heading

### Direct level overrides the style

Direct nine turns the style heading off

# Direct outline without a style

Child style nine stops inheritance
```

Headings come from Word styles and direct formatting; `#`–`######` levels map
onto heading levels. Real conversion of `fixtures/text.doc` shows the full
document shape:

```markdown
# Fixture Document

Plain paragraph with **bold**, *italic*, and ~~struck~~ runs.

## Table

|  |  |  |
| --- | --- | --- |
| Wide head |  | End |
| Tall | B2 | C2 |
|  | B3 | C3 |

## Notes and special text

Music clef 𝄞 appears before this footnote[^1] reference.

[^1]: Footnote after an astral character.
```

Caveats:

- **Merged cells** in Word tables render as empty covered spans (the covered
  cells are blank, not repeated or filled).
- **Nested tables** flatten into a single cell (GFM cannot nest tables) — a
  known limitation of the library.
- Legacy `.doc` (OLE) converts through the same document serializer with the
  same shape; only the relative-link target rendering differs cosmetically
  between sources.
- Fillable-form controls (DOCX content controls) lose their field layer;
  labels and underline glyphs survive.

## PowerPoint (`.ppt`, `.pps`, `.pot`, `.pptx`, `.pptm`, `.ppsx`, `.ppsm`)

Expected output: **slide titles as plain paragraphs** (never markdown
headings), bullet lists, speaker notes as `>` blockquotes, and — for PPTX and
ODP — slide tables as proper GFM tables. Legacy `.ppt` flattens tables to bare
text lines (see caveat).

Real conversion of `fixtures/pres.pptx`:

```markdown
Deck Title Slide

- Top level point

  - Nested detail

- Second point with emphasis

> Speaker note for the intro slide.

Numbers Slide

| Region | Total |
| --- | --- |
| North | 42 |

Grouped shapes below.
```

Caveat — **legacy `.ppt` flattens tables to bare text lines.** The same deck
converted from `fixtures/pres.ppt` renders the Numbers Slide table as plain
lines with no `|` table syntax:

```markdown
Numbers Slide

Region

Total

North

42
```

If the presentation's tables matter, use PPTX or ODP and verify the `|` rows
survived (see [workflows.md](workflows.md), "Output verification").

## Excel (`.xls`, `.xlsx`, `.xlsm`, `.xlsb`)

Expected output: each worksheet becomes a `## <sheet name>` heading followed by
a GFM table; the first row is used as the table header when it looks
label-like.

Real conversion of `fixtures/sheet.xlsx` (first table):

```markdown
## Values

| Kind | Value | Note |
| --- | --- | --- |
| Percent | 0.155 | fifteen and a half |
| Currency | 1234.5 | dollars |
| Thousands | 9876543 | grouped |
| Date | 2026-03-15 | ides of March |
| Duration | 26:30:15 | over a day |
| Tiny | 0.0000004 | four ten-millionths |
| Boolean | TRUE | yes |
```

Caveats:

- **XLS/XLSX drop number formats (issue #27).** Cells carry their *raw*
  values, not the formatted display values: `Percent → 0.155` (not `15.5%`),
  `Currency → 1234.5` (not `$1,234.50`), thousands `9876543`. A percentage
  reading as a raw fraction is wrong by 100x in meaning — warn consumers and
  sanity-check spreadsheets. Dates survive as ISO strings (`2026-03-15`).
- **ODS is the contrast case:** it keeps the formatted display values
  (`15.5%`, `$1,234.50`, `9,876,543`) on the same logical content. If display
  values matter, prefer ODS or a CSV export.
- **Merged cells render as empty covered spans** within the populated range
  only. Real conversion of `fixtures/handmade-merged.xlsx`:

  ```markdown
  |  |  |  |
  | --- | --- | --- |
  | Merged across |  | padded |
  | tall | b2 | 3.5 |
  |  | b3 |  |
  ```

- Hidden rows and columns are treated as visible and appear in the output
  (known limitation) — check for hidden template or calculation content before
  feeding output to an LLM.

## OpenDocument (`.odt`, `.ods`, `.odp`)

- `.odt`: same document shape as DOCX/DOC/RTF — `#`/`##` headings, GFM
  tables, `[^n]` footnotes. Real conversion of `fixtures/text.odt` matches the
  `text.doc` output structure line-for-line (only relative-link targets differ
  in depth).
- `.ods`: same spreadsheet shape as XLSX (`## Values` + GFM table) but with
  **formatted display values preserved** — the Excel number-format caveat does
  not apply. Real conversion of `fixtures/sheet.ods`:

  ```markdown
  ## Values

  | Kind | Value | Note |
  | --- | --- | --- |
  | Percent | 15.5% | fifteen and a half |
  | Currency | $1,234.50 | dollars |
  | Thousands | 9,876,543 | grouped |
  ```

- `.odp`: **same slide serializer as PPTX** — slide titles as plain
  paragraphs, speaker notes as blockquotes, and GFM tables **kept** (unlike
  legacy `.ppt`). Real conversion of `fixtures/pres.odp`:

  ```markdown
  Deck Title Slide

  - Top level point

  - - Nested detail
  - Second point with emphasis

  > Speaker note for the intro slide.

  Numbers Slide

  | Region | Total |
  | --- | --- |
  | North | 42 |
  ```

  One cosmetic difference vs PPTX: a nested bullet renders as `- - Nested
  detail` on one line rather than as an indented sub-list. The table,
  blockquote notes, and paragraph titles are identical in shape to PPTX.

## Rich Text Format (`.rtf`)

Expected output: the same document shape as DOCX/ODT (`# Fixture Document`,
`##` sections, GFM tables, `[^n]` footnote definitions). Real conversion of
`fixtures/text.rtf` matches `text.odt` structure; the one notable difference is
that relative link targets render with a `file:///` absolute path, e.g.
`[a sibling file](file:///anydoc/tests/fixture-src/sibling.odt)`, instead of a
relative path — a known cosmetic quirk.

## EPUB (`.epub`)

Expected output: `#` chapter headings (plus the book metadata title), GFM
tables, preserved inline emphasis/code, and **internal anchor links resolved to
fragments**. Real conversion of `fixtures/book.epub`:

```markdown
# Fixture Book

# Fixture Book

anydoc tests

<a id="epub-text-ch001-xhtml-chapter-one"></a>

# Chapter One

Opening paragraph with **bold**, *italic*, and `code` runs.

See [Chapter Two](#epub-text-ch002-xhtml-chapter-two) for the table, or jump straight to [the marked paragraph](#epub-text-ch002-xhtml-markpoint).

<a id="epub-text-ch002-xhtml-chapter-two"></a>

# Chapter Two

| Name | Qty |
| --- | --- |
| Bolts | 12 |
| Nuts | 30 |
```

Notes: the book title may appear twice (metadata title + injected title);
internal links keep working as `[text](#fragment)` links; external links stay
as normal markdown links.

## CSV (`.csv`)

Expected output: the file renders as **one GFM table**. The first row is
**promoted to the header row** when it looks like labels (≥ 2 columns,
non-empty, non-numeric, distinct fields) — this behavior ships in 0.1.6.
Quoted fields with embedded commas and newlines are preserved.

Real conversion of `fixtures/fixture-handmade-quoted.csv`:

```markdown
| name | desc | qty |
| --- | --- | --- |
| padded | comma, inside | 3 |
| plain | multi line | 4 |
```

Also verified:

- **Delimiter sniffing** — a semicolon-delimited file with decimal commas
  splits on `;` and keeps `1,5` intact (real output of
  `fixtures/fixture-handmade-semicolon.csv`):

  ```markdown
  | a | b | c |
  | --- | --- | --- |
  | 1,5 | 2,5 | x |
  | 3,0 | y | z |
  ```

- **UTF-16 (with BOM)** decodes to correct Unicode (real output of
  `fixtures/fixture-handmade-utf16.csv`):

  ```markdown
  | col1 | col2 |
  | --- | --- |
  | naïve | café |
  | Αθήνα | 数据 |
  ```

CSV has no content signature, so **`--format csv` is required when reading CSV
from stdin** (see [cli-reference.md](cli-reference.md)).

## PDF (`.pdf`) — the lower-fidelity pipeline

Text-based PDFs convert **locally** through a separate pipeline (`pdf-inspector`)
that emits Markdown directly — PDF has no document model, so only Markdown
output exists. Real conversion of `fixtures/fixture-text.pdf`:

```markdown
# Fixture Document

Plain paragraph with **bold**, *italic*, and struck runs. **Style-bold paragraph with a** NotBold-styled span **inside.**

## Lists

1.First numbered
2.Second numbered
a)Alpha sub one
b)Alpha sub two
i.Roman sub sub
3.Third numbered Interrupting paragraph between lists.

## Table

Wide head End Tall B2 C2 B3 C3
```

**Fidelity caveats (verified on the real output):**

- **No GFM tables.** Table cell text flattens into a plain paragraph run
  (`Wide head End Tall B2 C2 B3 C3`) — there is no `|` table.
- **No `[^n]` footnotes.** Footnote markers degrade to inline superscript
  glyphs (`¹`) and the note bodies drop into the flow; there is no `[^1]:`
  definition block.
- **Links are not emitted as markdown links.** They degrade to `<u>underlined
  text</u>`.
- Numbered/bulleted list structure compresses (markers inline), and some
  Unicode degrades (e.g. emoji without ZWJ).

### Scanned or image-only PDFs — no OCR

A PDF with **no extractable text layer** fails as `unsupported` with this exact
message (exit code 1):

```
anydoc: unsupported input: PDF has no extractable text (Scanned, 1 pages): OCR is required
```

anydoc **does not perform OCR** — the library's stance is explicit, and there
is no password, retry, or OCR option. When this message fires: report the exact
error, state that OCR is required, and route the file to OCR tooling or the
hosted Firecrawl Parse API. Do not retry the same file locally and do not claim
anydoc can OCR it. See [errors.md](errors.md) for the full routing guidance.

## Formats anydoc does NOT support

- HTML/SingleFile (open feature request only) — not an input format.
- Images (`.png`, `.jpg`, ...) — no image-to-text conversion.
- Password-protected/encrypted documents — fail with
  `anydoc: document is encrypted` (see [errors.md](errors.md)).
- Anything without a recognized signature and extension — fails as
  `unsupported input: unrecognized file content and extension: <path>`.

## Output-shape invariants to remember

1. One serializer: the same logical structure yields near-identical Markdown
   across docx/odt/rtf — do not re-test each office format for the same
   feature.
2. Spreadsheets: expect `## <sheet name>` + GFM tables; warn that xlsx/xls
   drop number formats (issue #27) while ODS keeps display values.
3. Legacy `.ppt` and all PDFs lose tabular structure — add a
   "verify the table survived" step or use PPTX/ODP and text PDFs.
4. Images never survive as bytes in Markdown — only alt text.
