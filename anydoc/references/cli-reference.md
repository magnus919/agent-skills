# CLI reference: the Any Doc CLI (pinned @firecrawl/anydoc@0.1.6)

Everything here was captured by running the pinned CLI on this machine
(`npx -y @firecrawl/anydoc@0.1.6`, version 0.1.6, Node v22). The CLI is a 4.7 KB
Node wrapper (`bin.anydoc = cli.js`) around a native NAPI binding that ships as
an npm `optionalDependency` per platform.

## Verbatim `--help` output

```
anydoc: convert documents to GitHub-Flavored Markdown

Usage:
  anydoc <file> [options]
  anydoc - [options] < file

Converts one document per invocation and writes the Markdown to stdout.
Pass - as the input to read the document from stdin. Never prompts; all
diagnostics go to stderr.

Options:
  -o, --output <path>    Write the Markdown to <path> instead of stdout
  -f, --format <format>  Name the input format instead of detecting it:
                         doc, docx, odt, pdf, ppt, pptx, rtf, epub, xlsx, ods, odp, csv
                         (extension aliases like xls, docm, ppsx resolve
                         to these)
  -h, --help             Print this help and exit
  -V, --version          Print the version and exit

The format is detected from the file content; the file extension is the
fallback for signature-less formats (CSV). stdin has no extension, so CSV
input from stdin needs --format csv. Scanned or image-only PDFs need OCR,
which anydoc does not do, and error as unsupported.

Exit codes:
  0  success
  1  the document could not be read or converted
  2  usage error: unknown option, missing input, or invalid --format

Examples:
  anydoc report.docx
  anydoc slides.pptx -o slides.md
  anydoc - --format csv < data.csv
  curl -s https://example.com/paper.pdf | anydoc -
```

`anydoc --version` prints exactly `0.1.6` (verified; both `--help` and
`--version` exit 0 and write to stdout).

## Invocation forms

```text
anydoc <file> [options]        # convert a path on disk
anydoc - [options] < file      # read the document from stdin
```

- `-` as the input reads the document from **stdin**.
- The CLI accepts **exactly one document per invocation** — there is no batch
  mode. Passing a second input exits 2:
  `anydoc: one document per invocation: unexpected second input '<path>'`.
  For multiple documents use a shell loop or `scripts/anydoc batch`
  (see [workflows.md](workflows.md)).

## Flag reference

| Token | Behavior (verified) |
| --- | --- |
| `<file>` | Input path. Format detected from content; extension is the fallback for signature-less formats (CSV). |
| `-` | Read the document from stdin. If stdin is a TTY, exits 2 with `anydoc: stdin is a terminal; pipe or redirect a document into anydoc -`. |
| `-o <path>`, `--output <path>` | Write the Markdown to `<path>` instead of stdout. **Silently overwrites** an existing file (verified). Writing to a directory fails with exit 1: `anydoc: EISDIR: illegal operation on a directory, open '<path>'`. With `-o`, stdout stays silent. |
| `-f <fmt>`, `--format <fmt>` | Force the input format instead of detecting it. Values: `doc, docx, odt, pdf, ppt, pptx, rtf, epub, xlsx, ods, odp, csv`. Extension aliases resolve through the parser mapping (verified: `--format xls`, `--format docm` accepted). Invalid value → exit 2: `anydoc: invalid format 'bogus'; expected one of: doc, docx, odt, pdf, ppt, pptx, rtf, epub, xlsx, ods, odp, csv`. |
| `-h`, `--help` | Print help to stdout, exit 0. Works even when the native binding is unavailable. |
| `-V`, `--version` | Print the version (`0.1.6`) to stdout, exit 0. Binding-independent like `--help`. |
| `--format=x` | Inline `=` value syntax is supported for long options (verified: `--format=rtf` works). |
| `--` | End of options: everything after `--` is treated as a positional input (a filename starting with `-`). |
| Missing option value | `anydoc: <option> requires a value` → exit 2 (e.g. `anydoc: -o requires a value`). |
| Unknown option | `anydoc: unknown option '--bogus' (see anydoc --help)` → exit 2. |
| No input | `anydoc: missing input: pass a document path, or - for stdin (see anydoc --help)` → exit 2. |

## stdin / stdout / stderr conventions

- **stdin input** via `-`. Because stdin has no file extension, **CSV from
  stdin requires `--format csv`** (CSV has no content signature). Without it,
  CSV bytes fail with exit 1:
  `anydoc: unsupported input: unrecognized file content: name the format explicitly`.
  Verified success pattern:

  ```bash
  printf 'name,role\nAlice,Engineer\n' | npx -y @firecrawl/anydoc@0.1.6 - --format csv
  ```

- **Markdown goes to stdout only.** With `-o`, stdout stays silent.
- **All diagnostics go to stderr** as exactly one `anydoc: <message>` line per
  failure. Nothing is ever printed to stdout on failure.
- **The CLI never prompts** — no confirmation, no interaction. (`-y` on the
  `npx` invocation exists only to answer *npx's* package-install prompt.)
- **EPIPE is handled**: if the downstream pipe closes early
  (`anydoc big.xlsx | head -n 1`), the CLI exits **0** with no stderr noise
  (verified). Piping into `head` is not treated as a conversion failure.
- **No environment variables** — the CLI uses only argv, stdin, and the
  filesystem (verified by reading `cli.js`).

## Running it: npx invocation

```bash
npx -y @firecrawl/anydoc@0.1.6 report.docx                # markdown to stdout
npx -y @firecrawl/anydoc@0.1.6 slides.pptx -o slides.md   # to a file
npx -y @firecrawl/anydoc@0.1.6 - --format csv < data.csv  # stdin (CSV needs --format)
curl -s https://example.com/paper.pdf | npx -y @firecrawl/anydoc@0.1.6 -   # URL → stdin
```

### Version pinning

Always pin the version: `npx -y @firecrawl/anydoc@0.1.6`. An unpinned
invocation (`npx -y @firecrawl/anydoc` with no `@version` suffix) floats to the
latest published tag, so conversions are not reproducible across time. All
behavior in this skill is documented against **0.1.6**. The `-y` flag answers
npx's "Ok to proceed?" install prompt non-interactively — omitting it means npx
asks for confirmation before installing a cold-cache package.

### First run and offline behavior

- The **first** `npx` invocation downloads the npm package plus the native
  platform binary (network required once). Verified with a fresh empty npm
  cache: `env npm_config_cache=$(mktemp -d) npx -y @firecrawl/anydoc@0.1.6 --version`
  prints `0.1.6` and exits 0.
- Later runs reuse the npm cache; measured warm startup is ~0.33–0.55 s per
  invocation (see [workflows.md](workflows.md)).
- **Cold-cache offline**: if the package is not cached and there is no network,
  npx itself fails with a clear fetch error before anydoc runs. The conversion
  itself is fully local — only package retrieval needs network.
- **Permanent / offline-capable alternative**: `npm install -g @firecrawl/anydoc`
  once, then invoke `anydoc` directly (still pinning is up to you). This
  satisfies the skill's "no service dependency" claim: there is no server, no
  API key, and no upload — the only network use is downloading the tool.

## Distribution and system requirements

- **Node.js >= 20** (package `engines`). Verified under Node v22.
- The native binary ships via npm **`optionalDependencies`** — one small
  package per platform (`darwin-x64`, `darwin-arm64`, `linux-x64-gnu`,
  `linux-arm64-gnu`, `linux-x64-musl`, `linux-arm64-musl`, `win32-x64-msvc`),
  with **no postinstall script and no compilation**.
- The npm package `@firecrawl/anydoc` 0.1.6 is ~48 KB unpacked (the binding
  package is a few MB per platform); published 2026-08-05T18:29:40Z.
- The Rust crate `anydoc` (crates.io) and Python wheels `firecrawl-anydoc`
  (PyPI, imports as `anydoc`, Python >= 3.10) ship in the same release train.
  There is no standalone Rust CLI binary (`cargo install anydoc` is an open
  feature request) — the CLI exists only through the npm package.

## The wrapper: `scripts/anydoc`

The skill ships a Python 3 standard-library wrapper at `scripts/anydoc` that
delegates to the pinned CLI. It adds value beyond a thin npx alias:

- **`convert <file|-> [-o out.md] [-f <format>] [--json] [--dry-run]`** —
  pre-validates the input path (missing file, directory input) and the `-o`
  path (existing directory) before invoking the CLI, validates `-f` against
  the 21 accepted format names (the 12 canonical parsers plus the 9 aliases,
  exit 2 on an invalid name), maps known failure classes to friendly hints
  (no-OCR, encrypted, malformed, unsupported), and forwards the CLI's exit
  code. Stdin input via `-` is passed straight through. A dash-leading
  filename is supported through the CLI's `--` marker with the options first:
  `anydoc convert -f csv -- -weird` (the wrapper emits `-o`/`-f` before `--`,
  since npx forwards `--` to the CLI and anything after it reads as an extra
  input). Absolute paths never need this.
- **`batch <inputs...> [--out-dir DIR] [--json] [--dry-run]`** — converts many
  documents one at a time, prints per-file status, continues past failures,
  and exits 1 when any input failed. Output naming is deterministic: each
  input becomes `<stem>.md` under `--out-dir`, which is created when missing
  and defaults to the current working directory. Duplicate inputs convert per
  occurrence (a later conversion overwrites the earlier output); same-basename
  inputs from different directories collide on the same `<stem>.md` and the
  last one wins.
- **`info [--version]`** — reports the tool name and the pinned CLI version
  (`anydoc 0.1.6 (wraps @firecrawl/anydoc@0.1.6)`) without invoking the
  converter; `info --version` prints exactly `0.1.6`.
- Global **`--json`** (exactly one JSON document on stdout; diagnostics stay
  on stderr) and **`--dry-run`** (print what would run — the exact `npx`
  command line and output paths — and execute nothing: no CLI spawn, no
  output files, no directory creation). With `--json`, `convert` embeds the
  converted markdown in the JSON document when `-o` is not given.
- Checks for Node >= 20 (missing `node`, or a version below 20, exits 1 with
  a clear message naming Node.js and the required version) and for `npx`
  (missing `npx` exits 1 naming `npx` and the pinned package
  `@firecrawl/anydoc@0.1.6`); always invokes npx with `-y`; never prompts;
  exit codes 0/1/2 mirror the CLI.

Run it as `anydoc/scripts/anydoc <subcommand> ...` from the repository root,
`scripts/anydoc <subcommand> ...` from the skill directory, or
`python3 anydoc/scripts/anydoc <subcommand> ...` anywhere (the executable bit
and `#!/usr/bin/env python3` shebang let it run directly). See
[workflows.md](workflows.md) for recipes and [errors.md](errors.md) for the
error vocabulary.
