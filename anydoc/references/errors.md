# Errors, exit codes, and troubleshooting

Every message below is a **verbatim real stderr capture** from the pinned CLI
(`@firecrawl/anydoc@0.2.4`) run against the committed fixtures in `fixtures/`
(and, for resource limits, generated oversized archives). The CLI prints
exactly one line to stderr, prefixed `anydoc: `, and never prompts.

## Exit codes

| Code | Meaning | Triggers |
| --- | --- | --- |
| `0` | Success | Normal conversion; `--help`/`--version`; also on **EPIPE** when the downstream pipe closes early (`anydoc big.xlsx \| head`). |
| `1` | The document could not be read or converted | Any conversion or IO failure below: missing file, unsupported input, scanned/image-only PDF, malformed archive, encrypted document, resource limit, `-o` pointing at a directory. |
| `2` | Usage error | Unknown option, missing input, invalid `--format`, more than one input, an option missing its value, stdin is a terminal. |

## Conversion / IO failures (exit code 1)

### io — the file could not be read

```
anydoc: io error: No such file or directory (os error 2)
```

This is the missing-file case (`to_markdown` path only; stdin and byte APIs
have no io error).

### unsupported — unknown format or unconvertible content

Unknown content **and** unknown extension (the extension is echoed as given):

```
anydoc: unsupported input: unrecognized file content and extension: unsupported.xyz
```

Verified against `fixtures/unsupported.xyz` (run from the fixture directory,
the tail is `unsupported.xyz`; when you pass a longer path, that path is echoed).

Recognized format but unconvertible content — a **scanned or image-only PDF**
(the CLI detects the page count and that it looks scanned):

```
anydoc: unsupported input: PDF has no extractable text (Scanned, 1 pages): OCR is required
```

Verified against `fixtures/scanned-image-only.pdf`: exit 1, empty stdout.

### unsupported — stdin without a format

CSV has no content signature and stdin has no extension, so CSV piped to `-`
without `--format csv` fails:

```
anydoc: unsupported input: unrecognized file content: name the format explicitly
```

Fix: add `--format csv` (e.g. `cat data.csv | npx -y @firecrawl/anydoc@0.2.4 - --format csv`).

### malformed — structurally unusable archive

An empty (0-byte) `.docx` and a truncated `.docx` both produce:

```
anydoc: malformed document: not a readable zip archive: invalid Zip archive: Could not find EOCD
```

Verified against `fixtures/empty--errors.docx`. Any other structurally broken
package surfaces the same class.

### encrypted — password-protected document

```
anydoc: document is encrypted
```

Verified against `fixtures/encrypted--errors.odt`. There is **no password or
decryption option** anywhere in the CLI or library — the only fix is an
unencrypted copy of the file.

### resourceLimit — fixed safety limits (decompression / nesting / node count)

Zip-bomb style DOCX (giant `word/document.xml`):

```
anydoc: resource limit exceeded (max_entry_bytes): word/document.xml declares 201326759 decompressed bytes
```

Image-bomb style DOCX (giant `word/media/image1.png`):

```
anydoc: resource limit exceeded (max_entry_bytes): word/media/image1.png declares 201326592 decompressed bytes
```

The **character-exact prefix** is:

```
anydoc: resource limit exceeded (max_entry_bytes):
```

with a tail naming the offending entry and the declared decompressed size —
the tail varies by entry, so match on the prefix. Verified also with a
generated 250 MB-entry zip (tail: `word/document.xml declares 250000000
decompressed bytes`). anydoc rejects zip/image bombs via `max_entry_bytes`;
conversion is **not streaming**, and the whole entry is checked before use.

### output-is-directory (EISDIR)

`-o` pointing at an existing directory fails with exit 1:

```
anydoc: EISDIR: illegal operation on a directory, open '<path>'
```

Verified: `npx -y @firecrawl/anydoc@0.2.4 report.rtf -o /tmp` prints
`anydoc: EISDIR: illegal operation on a directory, open '/tmp'` and exits 1.
Fix: pass a file path (or a path in a directory that exists); anydoc **does
not create directories**.

## Usage errors (exit code 2)

All verified verbatim:

```
anydoc: missing input: pass a document path, or - for stdin (see anydoc --help)
anydoc: unknown option '--bogus' (see anydoc --help)
anydoc: invalid format 'bogus'; expected one of: doc, docx, odt, pdf, ppt, pptx, rtf, epub, xlsx, ods, odp, csv
anydoc: one document per invocation: unexpected second input '<path>'
anydoc: stdin is a terminal; pipe or redirect a document into anydoc -
anydoc: -o requires a value      (pattern: `<option> requires a value`)
```

Notes:

- `unknown option '--bogus'` echoes the offending token; `one document per
  invocation` echoes the second input path as given; the `-o requires a value`
  pattern applies to `-f` too (`-f requires a value`).
- Usage errors never touch the filesystem and produce no markdown.

## The no-OCR caveat (read before converting PDFs)

- anydoc converts **text-based PDFs locally** via `pdf-inspector`; hosted OCR is
  a separate opt-in path for OCR-required PDFs.
- **Scanned / image-only PDFs fail as `unsupported`** with the exact message
  above (`... OCR is required`). The library's stance: "Scanned and image-only
  PDFs need OCR, which anydoc does not do."
- Route, don't retry unchanged. Report the exact error and choose local OCR or,
  after explicit authorization, `--ocr hosted --allow-hosted-upload`. Hosted
  mode sends the whole document to Firecrawl Parse and has no page selection.
  Do not fabricate the document's content or silently upload it.

## Troubleshooting recipes

| Symptom | Message to match | Fix |
| --- | --- | --- |
| File not found | `io error: No such file or directory` | Check the path; anydoc does not glob or resolve relative to the skill. |
| Unknown file type | `unsupported input: unrecognized file content and extension: <path>` | Confirm the extension is one of the 21 supported; or force it with `--format <name>`. |
| Scanned PDF | `PDF has no extractable text (Scanned, N pages): OCR is required` | Route to OCR tooling / Firecrawl Parse. Never retry locally. |
| Encrypted file | `document is encrypted` | Ask for an unencrypted copy; there is no password option. |
| Empty/truncated archive | `malformed document: not a readable zip archive` | Re-download or re-export the file. Note: some damaged files still convert partially (see below). |
| Huge or malicious archive | `resource limit exceeded (max_entry_bytes):` | anydoc rejected the entry by design; do not bypass. For genuinely large real documents, use `-o out.md`. |
| `-o` "failed" | `EISDIR: illegal operation on a directory, open '<path>'` | Point `-o` at a file path inside an existing directory. |
| CSV from stdin failed | `unsupported input: unrecognized file content: name the format explicitly` | Add `--format csv`. |
| Command rejected | any `anydoc: ...` exit-2 message | Re-read the usage: one input only, valid `--format`, options before/after correctly placed. |

## Graceful recovery — exit 0 is not byte-perfect fidelity

The library skips broken parts rather than failing whenever some meaningful
Markdown is still producible. The upstream test suite ships `*--recovers.*`
and `*--skips.*` fixtures (e.g. `mismatched--recovers.docx`,
`unbalanced--recovers.rtf`, `corrupt-styles--skips.docx`): structurally damaged
documents often convert with exit 0, dropping only the broken part. So a
conversion that exits 0 can still be incomplete — run the output-verification
steps in [workflows.md](workflows.md) and [SKILL.md](../SKILL.md) when fidelity
matters.

## Wrapper (`scripts/anydoc`) error behavior

The wrapper mirrors the CLI's contract and adds pre-validation and hints:

- **Pre-validation errors (exit 1)**: a missing input path, a directory-as-
  input, or an `-o` path that is an existing directory is caught before the
  CLI runs — stderr names the path and the problem (e.g.
  `anydoc: input file not found: <path>`,
  `anydoc: input path is a directory, not a file: <path>`,
  `anydoc: output path is a directory: <path> (pass a file path; -o does not
  create directories)`), with no traceback and no prompt.
- **Usage errors (exit 2)**: an unknown option, a missing input, or an invalid
  `-f` value exits 2 with a usage message on stderr before any CLI invocation.
  The accepted `-f` names are the 12 canonical formats plus the 9 aliases
  (`anydoc: invalid format 'bogus'; expected one of: ...`).
- **Friendly hints (exit 1)**: known failure classes get a hint plus a next
  step on stderr — no-OCR (`scanned-image-only.pdf` → "anydoc does not
  perform OCR. Route the file to OCR tooling or the hosted Firecrawl Parse
  API; do not retry it locally."), encrypted ("the document is encrypted or
  password-protected — supply an unencrypted copy"), malformed ("the document
  is malformed or corrupt (not a readable zip archive) — re-export or
  re-download the file and retry"), unsupported ("unsupported or unrecognized
  file type — check that the extension is one of the supported formats, or
  force it with `-f <format>`"). The raw CLI error line is always printed
  first, verbatim.
- **Node check (exit 1)**: if `node` is missing or older than v20, stderr
  states that Node.js >= 20 is required (`anydoc: Node.js >= 20 is required
  but `node` was not found on PATH ...` / `anydoc: Node.js version v18.20.0 is
  too old; anydoc requires Node.js >= 20 ...`), before any CLI invocation.
- **npx missing (exit 1)**: stderr names `npx` and the pinned package
  (`@firecrawl/anydoc@0.2.4`): `anydoc: `npx` was not found on PATH —
  conversion runs via `npx -y @firecrawl/anydoc@0.2.4`. Install Node.js >= 20
  (which ships npx), or install the CLI permanently with `npm install -g
  @firecrawl/anydoc`.`.
- **Batch exit policy**: `batch` exits 1 when any input failed; per-file
  status lines (`ok <file> -> <out.md>` / `FAIL <file>`) and a summary
  (`summary: N total, S succeeded, F failed`) print to stdout, failure detail
  to stderr.
- **`--json`**: exactly one JSON document on stdout in success and failure
  (result, exit code, output path, optional embedded markdown for `convert`;
  per-file status plus summary for `batch`); human diagnostics stay on stderr.
- **`--dry-run`**: prints the plan (the exact `npx` command line and output
  paths) and executes nothing — no CLI spawn, no output files, no directory
  creation.
- The wrapper always passes `-y` to npx and never prompts, even on a cold
  cache.
