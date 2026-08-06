# anydoc — office documents to GitHub-Flavored Markdown

Convert Word, PowerPoint, Excel, OpenDocument, RTF, EPUB, CSV, and PDF files into clean, LLM-friendly GitHub-Flavored Markdown — entirely on your own machine, with no API keys and no file uploads. One command turns a report, spreadsheet, or slide deck into markdown you (or an agent) can read, summarize, quote, and feed into a knowledge base.

## Why Install This Skill

Office documents are opaque to agents. A `.docx` or `.pptx` is a binary zip; a `.xls` is an OLE container; a PDF can be anything. Reading them directly means parsing formats, handling encodings, and reconstructing structure by hand — exactly the work anydoc automates. This skill gives your agent a single, verified command that converts all 8 format families (21 extensions) into GitHub-Flavored Markdown with headings, GFM tables, slide structure, and footnotes preserved, plus the knowledge of exactly where fidelity is lost (Excel number formats, legacy PowerPoint tables, PDF tables).

The skill wraps the pinned `@firecrawl/anydoc` v0.1.6 CLI with a small helper script that adds input checks, friendly error hints for the known failure classes (scanned PDFs, encrypted files, malformed archives), batch conversion, dry-run planning, and JSON output — so an agent gets predictable exit codes and messages instead of guessing. It also documents the exact error vocabulary of the real CLI, so failures like "PDF has no extractable text ... OCR is required" are recognized and routed correctly (to OCR tooling) rather than retried blindly.

## What You Get

| Directory / file | What it provides |
| --- | --- |
| `SKILL.md` + `README.md` | The skill index (trigger, command map, verification steps) and this human-facing guide |
| `scripts/` | `anydoc` — an executable Python 3 wrapper with `convert` (single file or stdin, `-o` output), `batch` (many files, per-file status, summary), and `info` (tool + pinned CLI version), plus global `--json` and `--dry-run` |
| `references/` | Five focused guides: `formats.md` (what GFM each format produces, with fidelity caveats), `cli-reference.md` (verbatim `--help`, every flag, stdout/stderr conventions), `errors.md` (exit codes and the exact error messages), `workflows.md` (recipes: single conversion, batch, vault ingestion, piping, output verification), `sources.md` (upstream URLs, fixture provenance, verification procedure) |
| `tests/` | Unit tests for the wrapper (argparse, pre-validation, hints, dry-run, JSON, batch) — runnable offline |
| `evals/` | An eval manifest with fixture-backed cases covering docx→headings, xlsx→tables, pptx→slide structure, csv→table, legacy `.doc`, ODS preserved values, ODT, and the image-only-PDF OCR failure |
| `fixtures/` | 24 tiny sample documents (all < 5 MB): valid samples for every family plus error cases (image-only PDF, encrypted ODT, empty DOCX, unsupported extension) — used by the tests, evals, and recipes |

## Quick Start

You need Node.js 20+ and `npx` (no other install — the CLI and its native binary are fetched on first use):

```bash
cd anydoc
npx -y @firecrawl/anydoc@0.1.6 fixtures/fixture-handmade-outline.docx
```

This converts the sample Word document and prints GitHub-Flavored Markdown to stdout (note the `#`/`##`/`###` heading lines). To write to a file instead:

```bash
npx -y @firecrawl/anydoc@0.1.6 fixtures/fixture-handmade-outline.docx -o outline.md
```

Or use the wrapper for the same job:

```bash
python3 scripts/anydoc convert fixtures/fixture-handmade-outline.docx -o outline.md
```

## Triggers

Load this skill when the task involves any of these:

- "Convert this Word/Excel/PowerPoint/PDF/EPUB/CSV file to markdown"
- "Extract the headings, tables, or slide content from this document"
- "Summarize this report / spreadsheet / deck"
- "Turn this CSV into a markdown table"
- "Read this document into markdown for a knowledge base or vault"
- "Convert this PDF to markdown" — but only for text-based PDFs; scanned or image-only PDFs fail (anydoc does not OCR)

Do **not** load this skill for document generation or editing ("create a docx report", "build a PDF proposal", "validate this document") — that is the `documents` skill's job — or for EPUB authoring (`epub` skill).

## Requirements

- **Node.js >= 20** and `npx` (the CLI is distributed via npm; the native binary ships as a platform-specific npm `optionalDependency`, so there is no manual install or compilation).
- **Network once** — the first `npx` run downloads the package and binary; later runs use the npm cache. For permanent or fully offline use, run `npm install -g @firecrawl/anydoc` once.
- **Python 3** (standard library only) if you use the `scripts/anydoc` wrapper.
- **No API keys, no services** — conversion happens locally; files never leave your machine.
