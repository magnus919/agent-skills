# Sources, provenance, and verification

## Upstream project

| Resource | URL / identifier |
| --- | --- |
| Repository | https://github.com/firecrawl/anydoc |
| npm package | `@firecrawl/anydoc` — https://www.npmjs.com/package/@firecrawl/anydoc |
| PyPI package | `firecrawl-anydoc` (imports as `anydoc`) — https://pypi.org/project/firecrawl-anydoc/ |
| crates.io crate | `anydoc` (same release train) |
| Browser demo (WASM) | https://firecrawl.github.io/anydoc/ |
| License | MIT |

## Access and verification dates

- Research and empirical verification performed **2026-08-05** and **2026-08-06**
  on macOS (arm64) with Node v22.22.3, network access, and the pinned CLI
  `npx -y @firecrawl/anydoc@0.2.4`.
- The pinned release **0.2.4** was published to npm at
  **2026-08-05T18:29:40Z**; PyPI wheels for the same version were uploaded
  **2026-08-05T18:29Z**. First release was 0.1.1 (2026-08-04).

## Fixture provenance

The committed fixtures under `fixtures/` come from two sources, both documented
here per the repository's attribution policy:

1. **The MIT-licensed upstream test suite.** Most fixtures were downloaded from
   `https://github.com/firecrawl/anydoc/tree/main/tests/fixtures` (raw files
   via `https://raw.githubusercontent.com/firecrawl/anydoc/main/tests/fixtures/...`).
   They retain the upstream naming and structure:
   - CSV: `fixture-handmade-quoted.csv`, `fixture-handmade-semicolon.csv`,
     `fixture-handmade-utf16.csv`, `fixture-sheet.csv`
   - DOCX: `fixture-handmade-numbering.docx`, `fixture-handmade-outline.docx`,
     `fixture-handmade-rich.docx`, `fixture-handmade-tables.docx`
   - Word legacy: `text.doc`; OpenDocument: `text.odt`, `sheet.ods`, `pres.odp`
   - RTF: `text.rtf`; EPUB: `book.epub`
   - PowerPoint: `pres.ppt`, `pres.pptx`; Excel: `sheet.xls`, `sheet.xlsx`,
     `handmade-merged.xlsx`
   - PDF: `fixture-text.pdf`
   - Error cases from the upstream `*--errors.*` corpus:
     `empty--errors.docx`, `encrypted--errors.odt`
2. **Generated samples** (created during research for cases the upstream suite
   does not cover; deterministic, reproducible):
   - `scanned-image-only.pdf` — a PDF with a single grayscale image and no
     text layer, generated with Pillow, to exercise the no-OCR error path.
   - `unsupported.xyz` — a small text file with an unsupported extension, to
     exercise the unrecognized-content error path.

All fixtures are tiny (largest: `pres.ppt` at ~454 KB) and each is well under
the 5 MB repository limit. All committed copies are byte-identical to the
staged originals used during research (verified by sha256).

MIT license notice: the upstream anydoc project is MIT-licensed (Copyright
Firecrawl); the fixture files above are used under that license. The generated
samples carry no upstream copyright.

## Verification procedure

Every factual claim in this skill was confirmed against the **real pinned CLI**
(v0.2.4), not inferred from documentation:

1. **Environment warm-up**: `node --version` (v22.22.3 ≥ 20), then
   `npx -y @firecrawl/anydoc@0.2.4 --version` → prints `0.2.4`; `--help` →
   the verbatim help block reproduced in
   [cli-reference.md](cli-reference.md).
2. **Positive conversions**: the pinned CLI was run on every committed fixture
   with stdout and stderr captured separately and the exit code recorded. All
   20 positive fixtures converted with exit 0 and empty stderr; the captured
   markdown was compared against the output expectations documented in
   [formats.md](formats.md) (headings, table rows, slide structure, footnote
   definitions, CSV header promotion, UTF-16/delimiter handling, merged-cell
   covered spans).
3. **Error paths**: each error fixture and each usage error was run with
   stderr captured verbatim and the exit code recorded (1 for conversion/IO
   failures, 2 for usage errors). The exact messages appear in
   [errors.md](errors.md) character-for-character, including
   `anydoc: unsupported input: PDF has no extractable text (Scanned, 1 pages): OCR is required`.
4. **Special behaviors**: `-o` overwrite and EISDIR, stdin via `-` with and
   without `--format csv`, `--format=x` inline syntax, `--` end-of-options,
   extension aliases (`--format xls`, `--format docm`), EPIPE (`| head` exits
   0 with empty stderr), the stdin-is-a-terminal usage error (via a
   pseudo-TTY), and resource limits (run on the upstream `zipbomb`/`imagebomb`
   fixtures and on a generated 250 MB-entry archive — all exit 1 with the
   documented `max_entry_bytes` prefix).
5. **First-run/offline**: a fresh empty npm cache was used to verify the
   first-run download path (`env npm_config_cache=$(mktemp -d) npx -y
   @firecrawl/anydoc@0.2.4 --version` → `0.2.4`, exit 0).
6. **Startup timing**: repeated warm invocations were timed
   (`/usr/bin/time -p npx -y @firecrawl/anydoc@0.2.4 ...`) — ~0.32–0.35 s each,
   consistent with the documented ~0.33–0.55 s warm-cache startup range.

Repository checks applied after authoring: frontmatter and structure
(`ruby scripts/validate-skills.rb`), skill quality (`ruby
scripts/validate-skill-quality.rb --base origin/main`), reference caps and link
resolution, eval-manifest validation (`scripts/validate-evals.py`), and no
machine-specific paths or credentials in any committed file.
