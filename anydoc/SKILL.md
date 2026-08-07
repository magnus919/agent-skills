---
name: anydoc
description: >-
  Convert Word (.doc/.docx/.docm), PowerPoint (.ppt/.pps/.pot/.pptx/.pptm/.ppsx/.ppsm),
  Excel (.xls/.xlsx/.xlsm/.xlsb), OpenDocument (.odt/.ods/.odp), RTF, EPUB, CSV, and
  PDF documents to clean GitHub-Flavored Markdown locally with the Any Doc CLI
  (npx -y @firecrawl/anydoc@0.1.6): headings, GFM tables, slide structure, and
  footnotes in one pass. Use when a task needs the contents of an office document,
  spreadsheet, presentation, ebook, or PDF you cannot read directly. Do not use for
  generating, editing, or validating documents (use documents), for ebook packaging
  (use epub), or for OCR of scanned or image-only PDFs (anydoc does not OCR; route
  to OCR tooling).
license: MIT
compatibility: >-
  Node.js >= 20 and npx. The pinned CLI is @firecrawl/anydoc@0.1.6; the native
  binary ships via npm optionalDependencies (no install step, no postinstall, no
  compilation). Conversion runs entirely on your machine — no services, no API
  keys, no uploads. The first npx run downloads the package once (network
  required); later runs use the npm cache.
metadata:
  skills: anydoc, markdown, conversion, docx, xlsx, pptx, pdf, odt, ods, odp, rtf, epub, csv, office, documents, firecrawl
  tags: conversion, markdown, office, documents
  source: https://github.com/firecrawl/anydoc
allowed-tools: Bash Read
---

# Any Doc — office documents to GitHub-Flavored Markdown

The `anydoc` skill converts office documents, spreadsheets, presentations,
ebooks, CSV, and text-based PDFs into GitHub-Flavored Markdown using the pinned
Any Doc CLI (`@firecrawl/anydoc` v0.1.6). One shared document model and one GFM
serializer produce the same logical output across formats, and conversion runs
locally in milliseconds — no service, no API key, no file upload.

## Overview

Load this skill when a task needs the *contents* of a document the agent cannot
read directly: a Word report to summarize, a spreadsheet to turn into a table,
a slide deck to extract, a CSV to analyze, or an ebook or PDF to quote from.

The skill ships a small Python helper (`scripts/anydoc`) that wraps the pinned
CLI and adds input pre-validation, friendly error hints, batch conversion, and
`--dry-run`/`--json` output. Every recipe in [references/workflows.md](references/workflows.md)
also shows the raw `npx` invocation, so the skill works with or without the
helper.

## When to use

- **Convert a document to markdown** — Word, PowerPoint, Excel, OpenDocument,
  RTF, EPUB, CSV, or text-based PDF.
- **Extract structure** — headings, GFM tables, slide titles, speaker notes
  (as blockquotes), and footnotes.
- **Feed documents to an LLM** — one-pass conversion to clean markdown for
  summarization, extraction, or retrieval ingestion.
- **Batch a folder** — convert a directory of mixed office files for a vault
  or knowledge base.
- **Read a document from stdin** — pipe bytes into `anydoc -`.

## Format coverage (summary)

anydoc covers **8 format families / 21 extensions** through **12 canonical
parsers**. The canonical formats are `doc, docx, odt, pdf, ppt, pptx, rtf,
epub, xlsx, ods, odp, csv`; extension aliases map through them (`.docm`→docx,
`.xls`→xlsx, `.pptm`→pptx, and so on).

| Family | Extensions | Expected GFM output |
| --- | --- | --- |
| Word | `.doc` `.docx` `.docm` | `#`–`######` headings, GFM tables, `[^n]` footnotes |
| PowerPoint | `.ppt` `.pps` `.pot` `.pptx` `.pptm` `.ppsx` `.ppsm` | slide titles as plain paragraphs, bullet lists, speaker notes as `>` blockquotes, GFM tables (PPTX/ODP; legacy `.ppt` flattens tables to text lines) |
| Excel | `.xls` `.xlsx` `.xlsm` `.xlsb` | `## <sheet name>` heading + one GFM table per worksheet; number formats dropped (raw cell values) |
| OpenDocument | `.odt` `.ods` `.odp` | same document/slide shapes as DOCX/PPTX; ODS keeps formatted display values |
| Rich Text Format | `.rtf` | same document shape as DOCX/ODT |
| EPUB | `.epub` | `#` chapter headings, GFM tables, internal anchor links |
| CSV | `.csv` | one GFM table; label-like first row promoted to header; delimiter sniffing; UTF-16 with BOM |
| PDF | `.pdf` | headings + inline emphasis, but a lower-fidelity pipeline: tables flatten to text, footnotes and links degrade. **Scanned or image-only PDFs fail** — anydoc does not OCR |

See [references/formats.md](references/formats.md) for the full per-format
expectations and fidelity caveats, and [references/errors.md](references/errors.md)
for the exact failure messages (including the no-OCR error).

## Command Map

Commands are shown relative to the repository root. `<file>` is any document
path (for example `anydoc/fixtures/fixture-handmade-outline.docx`); `-` reads
the document from stdin.

| Need | Command |
| --- | --- |
| Convert one file (markdown to stdout) | `anydoc/scripts/anydoc convert <file>` |
| Convert one file to a markdown file | `anydoc/scripts/anydoc convert <file> -o out.md` |
| Convert many files to a directory | `anydoc/scripts/anydoc batch <file1> <file2> ... --out-dir out/` |
| Show the tool and pinned CLI version | `anydoc/scripts/anydoc info` |
| Raw pinned CLI, one document | `npx -y @firecrawl/anydoc@0.1.6 <file> [-o out.md]` |
| Raw pinned CLI, read stdin | `cat data.csv \| npx -y @firecrawl/anydoc@0.1.6 - --format csv` |

Notes:

- `scripts/anydoc` is an executable Python 3 script (shebang `#!/usr/bin/env
  python3`); `python3 anydoc/scripts/anydoc ...` is equivalent when the
  executable bit is unavailable.
- The raw `npx -y @firecrawl/anydoc@0.1.6` rows are the ground truth for
  conversion behavior; the wrapper delegates to exactly that command.
- Always pin `@0.1.6` for reproducible conversions. `-y` answers npx's
  "Ok to proceed?" prompt non-interactively — the CLI itself never prompts.
- Both forms share the same contract: one document per invocation, exit code
  `0` success / `1` conversion or IO failure / `2` usage error, diagnostics as
  exactly one `anydoc: <message>` line on stderr, and no prompts.

## Reference Routing

Load these on demand — one per topic:

- [references/formats.md](references/formats.md) — the 8 families / 21
  extensions / 12 parsers, what GFM each format produces, and the fidelity
  caveats (xlsx/xls number-format drop vs ODS preserved display values, legacy
  `.ppt` table flattening, PDF lower-fidelity pipeline, merged-cell covered
  spans, ODP same-serializer).
- [references/cli-reference.md](references/cli-reference.md) — verbatim
  `--help`, every flag (`-o`, `-f`, `-h`, `-V`, `--format=x`, `--`), stdin via
  `-`, stdout/stderr conventions including EPIPE, version pinning, Node >= 20,
  and first-run/offline network behavior.
- [references/errors.md](references/errors.md) — exit codes 0/1/2, the verbatim
  error-message vocabulary (io, unsupported, malformed, encrypted, EISDIR,
  resource-limit, usage errors), the no-OCR caveat, and troubleshooting recipes.
- [references/workflows.md](references/workflows.md) — single conversion,
  batch loops, vault ingestion, stdin/stdout piping, output verification,
  large-file/resource-limit behavior, and startup cost.
- [references/sources.md](references/sources.md) — upstream URLs, access dates,
  fixture provenance, and how every documented claim was verified against the
  real CLI.

## When not to use

- **Generating, editing, or validating documents** — anydoc only converts
  existing documents *to markdown*; it never creates, edits, or checks
  documents. Use the `documents` skill for generation, inspection, and
  validation of PDF/Word/Excel/PowerPoint artifacts.
- **Ebook packaging or EPUB authoring** — use the `epub` skill. anydoc reads
  EPUBs to markdown but never writes or validates EPUB containers.
- **Scanned or image-only PDFs (OCR)** — anydoc does not perform OCR. Such
  PDFs fail as `unsupported` with the OCR message; route the file to OCR
  tooling or the hosted Firecrawl Parse API instead of retrying locally. Do
  not claim local OCR support.
- **HTML and other web content** — HTML is not a supported input format; use a
  web-scraping skill instead.
- **Binary media (images, video, audio)** — embedded images render as alt text
  only; anydoc cannot transcribe media content.
- **Layout or rendering work** — output is GitHub-Flavored Markdown only; there
  is no pagination, font, or template control.
- **Password-protected files** — encrypted documents fail with
  `anydoc: document is encrypted`; there is no password or decryption option.

## Verification

Confirm a conversion before reporting it as done:

1. **Check the exit code.** `0` means the CLI produced markdown. `1` means the
   document could not be read or converted — read the single `anydoc: <message>`
   stderr line and match it against [references/errors.md](references/errors.md).
   `2` means the command itself was a usage error (bad flag, missing input,
   invalid `--format`).
2. **Check the output shape.** The markdown must contain the structural markers
   your format actually produces:
   - Word / ODT / RTF / text-based PDF: `#`/`##` headings. For PDF, do not
     expect GFM tables or `[^1]:` footnote definitions — that pipeline
     flattens them.
   - Spreadsheets (xlsx/xls/ods) and CSV: `|`-delimited GFM tables. xlsx/xls
     show raw cell values (`0.155`, `1234.5`); ODS shows formatted display
     values (`15.5%`, `$1,234.50`).
   - Presentations (pptx/odp): slide titles as plain paragraphs, `>`
     blockquote speaker notes, GFM tables. Legacy `.ppt` flattens tables to
     bare text lines.
   - EPUB: `#` chapter headings and internal anchor links.
3. **Write large outputs to a file with `-o`.** `-o out.md` keeps stdout silent
   and gives a reviewable file instead of streaming the whole document into
   context.
4. **Verify tables survived.** If the source had tables and the output has no
   `|` rows, consult the format caveats — PDF and legacy `.ppt` flatten tables
   by design, not by error.

**Stop when** the conversion exits 0 and the structural markers match the
source format. Do not re-run or retry on a documented failure mode (encrypted,
malformed, scanned/image-only, unsupported) without changing the input; report
the documented message and route as [references/errors.md](references/errors.md)
instructs.
