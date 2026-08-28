# Workflows: recipes for converting documents to markdown

All recipes use the pinned CLI `npx -y @firecrawl/anydoc@0.2.4` (ground truth)
and the skill's wrapper `scripts/anydoc` where it adds value. Commands are
shown relative to the repository root; `anydoc/fixtures/...` paths can be
replaced with any document path. The vault-ingestion recipe (section 5) is
written to be run from a temp or vault directory holding *your own*
documents. Each raw-CLI invocation converts **exactly one document** — there
is no batch mode.

## 1. Single conversion

```bash
# Markdown to stdout
npx -y @firecrawl/anydoc@0.2.4 anydoc/fixtures/fixture-handmade-outline.docx

# Markdown to a file (stdout stays silent; existing file is overwritten)
npx -y @firecrawl/anydoc@0.2.4 anydoc/fixtures/fixture-handmade-outline.docx -o outline.md

# Same jobs through the wrapper
python3 anydoc/scripts/anydoc convert anydoc/fixtures/fixture-handmade-outline.docx
python3 anydoc/scripts/anydoc convert anydoc/fixtures/fixture-handmade-outline.docx -o outline.md
```

Expected result: exit code 0, empty stderr, and GitHub-Flavored Markdown on
stdout (or written to the `-o` output file) containing `#`/`##`/`###` heading
lines.

## 2. Force the input format

```bash
# Extensionless or mislabeled file: name the format explicitly
npx -y @firecrawl/anydoc@0.2.4 ./data --format csv
npx -y @firecrawl/anydoc@0.2.4 ./report --format docx
```

Use `--format <name>` only when detection cannot work (CSV from stdin, or a
missing/wrong extension). Aliases resolve: `--format xls`, `--format docm`,
`--format ppsx` are accepted. An invalid name exits 2 with
`anydoc: invalid format 'bogus'; expected one of: ...`.

## 3. Read a document from stdin

```bash
# CSV from stdin requires --format csv (no signature, no extension)
printf 'name,role\nAlice,Engineer\n' | npx -y @firecrawl/anydoc@0.2.4 - --format csv

# Any document type can come from stdin; detection reads the bytes
curl -s https://example.com/paper.pdf | npx -y @firecrawl/anydoc@0.2.4 -
```

The wrapper supports the same: `cat data.csv | python3 anydoc/scripts/anydoc convert - -f csv`.

Piping notes:

- Markdown goes to **stdout only**; diagnostics are the single
  `anydoc: <message>` stderr line.
- **EPIPE is handled**: if the downstream pipe closes early
  (`... anydoc@0.2.4 big.xlsx | head -n 1`), the CLI exits 0 with no stderr
  noise — piping into `head` is safe and is not a failure.

## 4. Batch conversion (raw CLI)

The raw CLI takes one document per invocation, so batch with a shell loop:

```bash
mkdir -p out
for f in anydoc/fixtures/*.docx; do
  npx -y @firecrawl/anydoc@0.2.4 "$f" -o "out/$(basename "${f%.docx}").md"
done
```

Each failed document (error fixtures, scanned PDFs, encrypted files) exits 1
with its `anydoc: <message>` on stderr and produces no output file; the loop
continues with the next input. Handle or route those per
[errors.md](errors.md).

Or the wrapper, which is built for this (per-file status, continues past
failures, summary, and a non-zero exit when any input failed):

```bash
python3 anydoc/scripts/anydoc batch \
  anydoc/fixtures/fixture-handmade-outline.docx \
  anydoc/fixtures/fixture-sheet.csv \
  --out-dir out/
```

`batch --dry-run --json` prints the plan (input → output, dry-run marker)
without converting or creating anything:

```bash
python3 anydoc/scripts/anydoc batch anydoc/fixtures/fixture-handmade-outline.docx \
  anydoc/fixtures/fixture-sheet.csv --out-dir out/ --dry-run --json
```

## 5. Vault-ingestion pattern

Convert a folder of mixed office documents to markdown for ingestion into a
vault or knowledge base:

1. **Collect** the documents into a folder (mixed docx/xlsx/pptx/csv/odt/pdf
   is fine — text-based PDFs only; see the no-OCR caveat in
   [errors.md](errors.md)).
2. **Batch-convert** with the wrapper into a markdown folder:

   ```bash
   python3 anydoc/scripts/anydoc batch notes/*.docx notes/*.xlsx notes/*.csv --out-dir vault/inbox/
   ```

   (or the raw-CLI loop above if you are not using the wrapper).

   > **Run this from a temp or vault directory — never from the agent-skills
   > repo root.** The glob matches whatever directory you name, and the
   > repository tracks a top-level `docs/` directory (distinct from the
   > `documents/` skill): globbing `docs/*.docx` there, or deleting/cleaning
   > those matches, would damage tracked repository files. Keep the source
   > documents in their own folder (here `notes/`) and convert into a
   > separate `vault/inbox/` folder.
3. **Verify each output** (step 6) — at minimum confirm exit 0 and that the
   structural markers your formats produce are present (headings for Word/PDF,
   `|` tables for spreadsheets/CSV).
4. **Failures are per-file**: the batch summary names what failed; route those
   files per [errors.md](errors.md) (scanned PDF → OCR tooling, encrypted →
   unencrypted copy, unsupported → check extension) and re-run only the
   failures.

## 6. Output verification

Before treating a conversion as done:

1. **Exit code 0** — the CLI produced markdown. Exit 1: read the
   `anydoc: <message>` stderr line and match it against
   [errors.md](errors.md). Exit 2: fix the command (usage error).
2. **Structural markers** — check the markers your format actually produces:
   - Word / ODT / RTF / text-based PDF: `#`/`##` heading lines
     (`grep -E '^#{1,6} ' out.md`).
   - Spreadsheets (xlsx/xls/ods) and CSV: `## <sheet>` headings and
     `|`-delimited rows (`grep -E '^\|' out.md`).
   - Presentations (pptx/odp): slide titles as plain paragraphs, `>`
     blockquote speaker notes, `|` table rows (legacy `.ppt` has no `|` rows —
     that is by design, not an error).
   - EPUB: `#` chapter headings and `[text](#fragment)` internal links.
3. **Tables survived?** If the source had tables and the output has no `|`
   rows, check the caveats: PDF and legacy `.ppt` flatten tables by design.
4. **Large outputs**: convert with `-o out.md` and inspect the file rather
   than streaming everything into context.

Use the committed fixtures to sanity-check an environment once:

```bash
npx -y @firecrawl/anydoc@0.2.4 anydoc/fixtures/fixture-handmade-outline.docx   # headings
npx -y @firecrawl/anydoc@0.2.4 anydoc/fixtures/sheet.xlsx                      # ## Values + table
npx -y @firecrawl/anydoc@0.2.4 anydoc/fixtures/fixture-text.pdf                # headings, no table
```

## 7. Large files and resource limits

- **Conversion is not streaming** — the document is read and processed as a
  whole, and safety limits protect against decompression and nesting bombs.
- **Zip/image bombs are rejected via `max_entry_bytes`** with exit 1 and the
  prefix `anydoc: resource limit exceeded (max_entry_bytes):` (full examples
  in [errors.md](errors.md)). This is by design — do not try to bypass it.
- **`-o out.md` is recommended for large documents** so the output is written
  to a reviewable file instead of filling stdout/context; you can then read
  the parts you need.
- Genuinely large real documents (as opposed to bombs) convert normally; the
  per-document limit only rejects entries whose declared decompressed size
  exceeds the cap.
- If a resource-limit error fires on a *real* file, the archive is malformed
  or hostile — re-export the document rather than disabling the limit.

## 8. Startup cost and performance

Each `npx -y @firecrawl/anydoc@0.2.4` invocation costs roughly **0.33–0.55 s
of warm-cache startup** (npm/npx process startup) on top of the conversion
itself, which is a few milliseconds (measured ~5 ms for a PDF, <1 ms for a
DOCX once the process is warm). There is no progress output; conversions are
effectively instant. Plan for ~0.5 s per document in batch loops, and prefer a
single `npx` process per document (you cannot batch inside one invocation).

## 9. Hosted OCR workflow

The local default is safe for sensitive documents and never uploads them. For a
scanned PDF, obtain explicit authorization for whole-document upload, then run:

```bash
python3 anydoc/scripts/anydoc convert scan.pdf --ocr hosted --allow-hosted-upload
```

Set `FIRECRAWL_API_KEY` only in the trusted environment when higher hosted limits
are needed. Never pass it on the command line. The hosted route uses Firecrawl
Parse, has no page-selection option, and does not silently fall back to another
endpoint after authentication, quota, or transport failure. Verify the output
and report that the result came from hosted OCR.

## 10. Offline / cold-cache behavior

- The first `npx` run downloads the package plus the native binary (network
  required once); later runs use the npm cache. A cold-cache offline run fails
  with a clear npx fetch error before anydoc executes.
- For permanent or fully offline use, install once:
  `npm install -g @firecrawl/anydoc`, then call `anydoc <file>` directly.
- The wrapper always invokes npx with `-y` (non-interactive), so it never
  hangs on npx's install prompt — even on a cold cache it fails fast if the
  package cannot be fetched.
