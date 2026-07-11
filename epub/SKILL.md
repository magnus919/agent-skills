---
name: epub
description: EPUB file format expert — read, write, and edit EPUB2/EPUB3 ebooks. Extract
  text, metadata, structure, and knowledge from EPUB files for enrichment or memory.
  Create valid EPUBs from scratch. Validate against the EPUB specification. Use when
  the user mentions epub, ebook, EPUB file, ebook format, read epub, write epub, create
  ebook, extract from epub, epub to text, or ebook structure.
license: MIT
compatibility: Python 3.8+ required. Core scripts use EbookLib (pip install EbookLib)
  for reading and creating EPUBs. Optional epublib (pip install epublib) for non-intrusive
  editing. beautifulsoup4 (pip install beautifulsoup4) for text extraction. Optional
  LLM mode via EPUB_LLM_URL + EPUB_LLM_KEY env vars (any OpenAI-compatible provider).
  EPUBCheck (Java, optional) for authoritative validation. Portable across all AgentSkills-compatible
  harnesses — scripts are platform-agnostic.
metadata:
  skills: epub, ebook, publishing, knowledge-extraction, document-processing
  tags: epub, ebook, epub3, epub2, publishing, document-extraction, knowledge
---

# EPUB — Ebook Creation, Extraction & Enrichment

Expert-level EPUB handling: read, write, edit, validate, and extract knowledge
from EPUB 2 and EPUB 3 files. Ships with five Python CLI scripts and five
detailed references covering the entire EPUB domain.

## EPUB Format Essentials

An EPUB file is a **ZIP archive** (Open Container Format, OCF) with a specific
internal layout. The W3C EPUB 3.3 standard uses a "three planes" model:

| Plane | Contains | Key Rule |
|-------|----------|----------|
| **Manifest** | All resources (XHTML, images, CSS, fonts) | Every file must be listed in OPF `<manifest>` |
| **Spine** | Linear reading order | Only XHTML/SVG by default; other types need fallbacks |
| **Content** | Resources embedded within documents | Core media types guaranteed; foreign types need fallbacks |

The package document (`content.opf`) holds metadata (Dublin Core), manifest
(every resource), and spine (reading order). EPUB3 uses an XHTML `nav` document
for navigation; EPUB2 uses `.ncx` XML. Both can coexist for compatibility.

**Critical rules:** `mimetype` must be the first ZIP entry, stored uncompressed.
All content documents must be well-formed XML (XHTML, not HTML5). The manifest
must list every file used in rendering. Read `references/epub-format-internals.md`
for the full structure reference.

## Decision Table — Which Script to Use

| Task | Script | Notes |
|------|--------|-------|
| See structure, metadata, manifest, spine, TOC | `epub-info` | JSON output, `--summary` for compact |
| Extract clean reading-order text | `epub-text` | Per-chapter or single file |
| Create minimal valid EPUB from scratch | `epub-scaffold` | No dependencies needed |
| Extract facts, quotes, definitions, arguments | `epub-extract-knowledge` | Heuristic or LLM mode (env var auto-detect) |
| Validate against EPUB spec | `epub-validate` | EPUBCheck or Python fallback |
| **Edit EPUB** (metadata, chapters, spine, CSS) | **`epub-edit`** | **v2 flagship — 8 subcommands, non-intrusive** |
| Extract images | `epub-images` | List or extract to directory |
| Batch process multiple EPUBs | `epub-batch` | Wrap existing scripts across globs |
| Convert EPUB2 → EPUB3 | `epub-convert` | Add NAV, update NS, keep NCX |
| Diagnose & repair structural issues | `epub-repair` | Auto-fix common validation failures |

## Scripts

All scripts live in `scripts/` relative to this skill's directory. Each follows
cli-builder conventions: `--json` for machine output, `--dry-run` to preview,
non-interactive, errors to stderr. Run with `--help` for full flag details.

### epub-info — Structure & Metadata Dump

```bash
scripts/epub-info book.epub --json
scripts/epub-info book.epub --summary      # compact manifest
scripts/epub-info book.epub --dry-run      # preview
```

Outputs: EPUB version, metadata (title, author, language, identifier),
manifest (all items with id/href/media-type), spine (reading order),
TOC (nested structure). `--summary` reduces manifest to id+href+media-type.

### epub-text — Clean Text Extraction

```bash
scripts/epub-text book.epub                           # plain text to stdout
scripts/epub-text book.epub --json                    # JSON with chapter array
scripts/epub-text book.epub --chapters                # one .txt per chapter
scripts/epub-text book.epub --output book.txt         # single file
scripts/epub-text book.epub --format markdown         # markdown output
```

Extracts text from spine-ordered content documents. Strips HTML tags, preserves
paragraph structure. Requires beautifulsoup4. Respects spine linearity — only
processes documents in the reading order.

### epub-scaffold — Create Valid EPUB from Scratch

```bash
scripts/epub-scaffold --title "My Book" --author "Jane Doe"
scripts/epub-scaffold --title "Novel" --author "Me" --chapters 12 --output novel.epub
scripts/epub-scaffold --title "Guide" --author "Me" --cover cover.jpg
scripts/epub-scaffold --title "Guide" --author "Me" --cover cover.jpg --toc-hidden --dry-run
```

Creates a valid EPUB3 with all content inside `OEBPS/` — required for Apple
Books compatibility. No external dependencies — Python stdlib only.

**Cover handling:** When `--cover` is provided, the scaffold automatically:
- Copies the image to `OEBPS/Images/cover.{ext}`
- Generates `OEBPS/Text/cover.xhtml` — an XHTML wrapper page with full-viewport CSS
- Adds the cover page to the spine as the first item
- Sets `properties="cover-image"` on the raw image for library thumbnails

This follows the Apple Books requirement that covers must be XHTML pages in
the spine, not raw image references (raw images render as blank pages).

**Nav visibility:** `--toc-hidden` sets `linear="no"` on the nav spine item,
hiding it from the reading flow (still accessible via the app's built-in TOC
browser). Default is `--toc-visible` (nav renders as a page).

**CSS:** Ships `OEBPS/Styles/default.css` with Apple Books-compatible typography:
no deprecated `page-break-before`, `margin: 0` on body (padding for whitespace),
proper heading hierarchy, and responsive styling.

**Cover art guidance:** The `--cover` flag accepts a pre-existing image file. If
the user does not have a cover image, offer to generate one using the agent's
image_gen capability. See `references/apple-books-compatibility.md` for the full
cover XHTML and CSS conventions.

### epub-cover — Add Cover to Existing EPUB

```bash
scripts/epub-cover wrap book.epub --image cover.png --output with-cover.epub
scripts/epub-cover wrap book.epub --image cover.png --in-place
```

Adds a cover XHTML wrapper page to an EPUB that already has a cover image in
its manifest. Use when the image exists but isn't rendering in Apple Books.
Requires epublib.

### epub-extract-knowledge — Knowledge Extraction Pipeline

```bash
# LLM mode — set env vars first (see below), then run without flags:
scripts/epub-extract-knowledge book.epub --format json
scripts/epub-extract-knowledge book.epub --format atoms
scripts/epub-extract-knowledge book.epub --format memory

# Force heuristic mode (ignore env vars):
scripts/epub-extract-knowledge book.epub --no-llm --format json

# Custom prompt override:
scripts/epub-extract-knowledge book.epub --prompt "Extract all definitions" --format json
```

Extracts knowledge from EPUB content: facts, definitions, key points, and
arguments. Two modes, auto-selected:

- **LLM mode (auto-detected):** When `EPUB_LLM_URL` and `EPUB_LLM_KEY` env vars
  are set, calls the configured LLM with the chapter text and extraction prompt.
  Produces high-quality structured insights. Falls back to heuristic if the LLM
  call fails.
- **Heuristic mode (fallback):** When env vars are NOT set, or `--no-llm` is
  passed, uses pattern matching (headings, emphasis markers, definition language,
  paragraph density) to identify knowledge-bearing passages. No LLM required.

Output formats:
- `json` — raw structured JSON with types, content, and source chapters
- `atoms` — Obsidian vault atom templates (YAML frontmatter + body)
- `memory` — key-value memory entries suitable for agent persistence

### LLM Configuration Convention

Several scripts in this skill support optional LLM-powered features. Any script
that does auto-detects LLM availability via environment variables. Set them once
and all scripts inherit:

```bash
# Required for LLM mode:
export EPUB_LLM_URL="https://your-provider.example.com/v1"   # OpenAI-compatible endpoint
export EPUB_LLM_KEY="sk-..."                                  # API key

# Optional:
export EPUB_LLM_MODEL="model-name"                            # Defaults to provider default
```

**How it works:**
- If `EPUB_LLM_URL` and `EPUB_LLM_KEY` are both set → LLM mode enabled
- If either is missing → heuristic/deterministic mode (no LLM)
- `--no-llm` flag forces heuristic mode even when env vars are set
- The scripts make OpenAI-compatible `POST /chat/completions` calls — any
  OpenAI-compatible provider works (OpenAI, OpenCode, Anthropic via proxy,
  local llama.cpp, Ollama, vLLM, etc.)

**Which scripts support this:**
| Script | LLM Feature | Fallback |
|--------|------------|----------|
| `epub-extract-knowledge` | Structured knowledge extraction | Heuristic pattern matching |
| `epub-validate` | LLM-generated repair suggestions for errors | Error codes only |
| *(more scripts can adopt this pattern as features are added)* | | |

**Agent instructions:** Before running any extraction pipeline, set these
env vars in your environment. They are inherited by subprocesses, so every
script in the pipeline auto-detects the same LLM configuration. If your
harness provides an LLM natively (e.g., you *are* the LLM), you can skip
the env vars — the heuristic mode is designed for that case. But if you
have access to an external LLM API, wiring it through these env vars
unlocks dramatically better extraction quality without requiring the
agent to manually chunk, prompt, parse, and re-inject results.

### epub-edit — Surgical EPUB Editing (v2)

```bash
scripts/epub-edit info book.epub --json
scripts/epub-edit metadata book.epub --title "New Title" --output out.epub
scripts/epub-edit add-chapter book.epub --content new.xhtml --after chapter3 --output out.epub
scripts/epub-edit remove-chapter book.epub --id chapter5 --output out.epub
scripts/epub-edit reorder-spine book.epub --order chapter3,chapter1,chapter2 --dry-run
scripts/epub-edit rename-resource book.epub --from Images/old.jpg --to Images/new.jpg
scripts/epub-edit inject-css book.epub --css dark.css --output out.epub
scripts/epub-edit update-manifest book.epub --output out.epub
```

Non-intrusive EPUB editing via epublib. Eight subcommands covering the full
edit surface. Never overwrites original — defaults to `--output out.epub`;
use `--in-place` to commit. All subcommands support `--json`, `--dry-run`.

### epub-images — Image Extraction

```bash
scripts/epub-images book.epub --list --json           # list all images
scripts/epub-images book.epub --extract images/       # extract all to directory
scripts/epub-images book.epub --type cover --extract .  # cover image only
```

### epub-batch — Multi-File Processing

```bash
scripts/epub-batch extract-text "books/*.epub" --output texts/
scripts/epub-batch validate "books/*.epub" --json
scripts/epub-batch metadata "books/*.epub" --set-author "Author" --output-dir fixed/
scripts/epub-batch info "books/*.epub" --json
```

### epub-convert — EPUB2 → EPUB3

```bash
scripts/epub-convert old.epub --output new-v3.epub
scripts/epub-convert old.epub --validate --json
```

### epub-repair — Diagnose & Fix

```bash
scripts/epub-repair broken.epub --diagnose --json     # list fixable issues
scripts/epub-repair broken.epub --output fixed.epub   # auto-fix
```

### epub-validate — Structural Validation

```bash
scripts/epub-validate book.epub --json
scripts/epub-validate book.epub --dry-run
```

Tries EPUBCheck (Java JAR) first for authoritative validation. Falls back to
pure-Python structural checks: mimetype position/compression/content,
container.xml parseability, OPF schema, manifest completeness, spine reference
integrity, required metadata, and NAV document presence.

## Capability Discovery & Pipeline Construction

Before executing a multi-step EPUB pipeline, **discover what tools are available**
on your agent platform. This skill is portable — the exact pipeline shape
depends on your harness's capabilities.

### Discovery Protocol

1. **Enumerate:** What tools do you have? File write? Web access? Subagents?
   Cron? Persistent memory? Vector DB? Vault? LLM?
2. **Classify:** Map available tools to pipeline stages (Ingest → Parse →
   Extract → Format → Sink)
3. **Construct:** Build a specific pipeline from available pieces
4. **Propose:** Present the plan to the user before executing

### Pipeline Stages

```
EPUB file
  ↓ INGEST   — local path, URL download, or user provides file
  ↓ PARSE    — epub-text, epub-info, or stdlib zipfile+XML
  ↓ EXTRACT  — epub-extract-knowledge (heuristic or LLM)
  ↓ FORMAT   — vault atoms, memory entries, JSON, markdown
  ↓ SINK     — file write, memory tool, vector DB, vault, terminal
```

### Example Pipelines

**Full (Hermes Agent):**
Ingest EPUB → epub-text (JSON) → epub-extract-knowledge → vault atoms →
wiki-link-verification → LightRAG ingest

**Minimal (any harness with terminal + file write):**
Ingest EPUB → epub-text → epub-extract-knowledge --no-llm → write output.md

**Batch (multi-file):**
Find *.epub → for each: epub-text --chapters → epub-extract-knowledge --no-llm → collect
results → summary report

See `references/agent-capability-discovery.md` for the full protocol with
worked examples for different platforms.

## Knowledge Extraction Deep Dive

EPUB files are dense sources of structured knowledge. The extraction process
targets specific knowledge types:

| Type | Detection | Example |
|------|-----------|---------|
| **Fact** | Headings, list items, named entities | "Python 3.13 added the `@override` decorator" |
| **Definition** | Paragraphs with definition markers | "A coroutine is defined as a function that can suspend execution" |
| **Key point** | Emphasized text (bold, italic) | Important conclusions, takeaways |
| **Argument** | Dense paragraphs (>200 chars) | Multi-sentence reasoning chains |

### Prompt Design for LLM Mode

When using LLM extraction, provide a focused prompt:

```
Extract from this chapter:
1. All technical definitions (term + definition)
2. Key facts (concise, standalone statements)
3. Notable quotes (exact wording)
4. Core arguments (the main thesis and supporting points)

Format as JSON with fields: type, content, context
```

### Sink Options by Platform

| Sink | Platform | Format to use |
|------|----------|---------------|
| Vault atoms | Obsidian | `--format atoms` |
| Agent memory | Most harnesses | `--format memory` |
| Vector DB | LightRAG, Chroma | `--format json` → insert |
| Plain files | Any | `--output DIR` |

## Common Workflows

### Create EPUB from Markdown Files

```bash
# 1. Scaffold the EPUB
scripts/epub-scaffold --title "My Book" --author "Me" --chapters 3 --output book.epub

# 2. Use epublib (Python) to inject real content into each chapter
# See references/tutorials-and-guides.md for the editing pattern
```

### Extract All Images from EPUB

```bash
scripts/epub-images book.epub --extract images/
```

### Edit an EPUB

```bash
# Update metadata
scripts/epub-edit metadata book.epub --title "New Title" --output revised.epub

# Add a chapter
scripts/epub-edit add-chapter book.epub --content new.xhtml --output expanded.epub

# Inject dark theme
scripts/epub-edit inject-css book.epub --css dark.css --output dark.epub
```

### Fix a Broken EPUB

```bash
scripts/epub-repair broken.epub --diagnose --json     # see what's broken
scripts/epub-repair broken.epub --output fixed.epub   # auto-fix
```

### Batch Extract Text from a Library

```bash
scripts/epub-batch extract-text "books/*.epub" --output texts/
```

### Convert EPUB2 to EPUB3

```bash
scripts/epub-convert old.epub --output old-v3.epub --validate
```

## Apple Books Compatibility

Apple Books on macOS/iOS enforces requirements beyond the EPUB spec. These
rules were verified by building and testing on macOS 26.

| Rule | Why |
|------|-----|
| All content inside `OEBPS/` directory | Files at ZIP root render as blank pages |
| Cover must be XHTML page in spine | Raw `<itemref>` to `image/png` renders blank |
| `margin: 0` on body, use `padding` | Apple Books applies its own margins; they stack |
| No `page-break-before` (use `break-before: page` or omit) | Deprecated; Apple Books ignores it |
| `xmlns:epub` only on nav document | Unused namespace declarations can trigger parser failures |
| Cover image keeps `properties="cover-image"` | Used for library thumbnail on raw image, not on wrapper page |
| `linear="no"` hides page from reading flow | Nav still accessible via app's built-in TOC browser |

**Spine ordering patterns:**
| Pattern | Order | Use case |
|---------|-------|----------|
| No cover | `nav → chapters` | Simplest |
| Cover only | `cover-page → nav(linear="no") → chapters` | Cover visible, ToC via app browser |
| Full | `cover-page → nav → chapters` | Most commercial ebooks (scaffold default) |

See `references/apple-books-compatibility.md` for the full reference with
CSS examples, cover XHTML template, and validation quirks.

## Gotchas

- **mimetype compression:** Python's `zipfile` compresses by default. Always use
  `ZIP_STORED` for the mimetype entry. A compressed mimetype silently breaks
  reading systems.
- **XHTML ≠ HTML5:** Content documents must be well-formed XML. Self-closing
  tags required (`<br/>` not `<br>`). Use `xmlns:epub="http://www.idpf.org/2007/ops"`.
- **Manifest is exhaustive:** Every file in the EPUB must be listed. Missing
  manifest entries cause validation failures. Images, CSS, fonts — no exceptions.
- **AGPL boundary:** EbookLib is AGPL; scripts call it at runtime but don't
  bundle it. Users install it themselves via pip. This skill and its scripts
  are MIT.
- **EPUBCheck needs Java:** The authoritative validator requires Java. The
  fallback Python checks catch structural issues but not XHTML schema violations
  or CSS validity.
- **Spine references manifest IDs:** An `idref` in the spine must match an `id`
  in the manifest. Broken references cause the EPUB to fail validation.
- **Navigation document:** EPUB3 requires a NAV with `properties="nav"`.
  Without it, reading systems may not show a table of contents.
- **Language is required:** Both `<dc:language>` and `xml:lang`/`lang`
  attributes on content documents. Missing language = invalid EPUB.

## Pitfalls

- **Don't skip capability discovery.** Assuming a tool exists that doesn't
  leads to broken pipelines. Always check before building.
- **Don't assume LLM availability.** Always offer `--no-llm` fallback for
  extraction. Heuristic mode works surprisingly well for well-structured books.
- **Don't modify EPUBs in place without backup.** EPUB editing is surgery —
  always keep the original.
- **Don't mix EbookLib and epublib on the same file in the same session.**
  They have different memory models and may conflict. Pick one library per task.
- **Don't assume the OPF is at `OEBPS/content.opf`.** Always read
  `container.xml` to find the actual path. The root directory varies.

## References

- `references/epub-format-internals.md` — Full structural reference (OCF, OPF,
  XHTML, NCX/NAV, spine, three planes, core media types, EPUB2 vs EPUB3)
- `references/python-libraries.md` — EbookLib vs epublib comparison, code
  examples, when to use which, license notes
- `references/spec-and-validation.md` — W3C EPUB 3.3 spec access points,
  EPUBCheck usage, Ace accessibility validation, key constraints summary
- `references/tutorials-and-guides.md` — Beginner to advanced guides, common
  workflows, manual OPF editing, batch operations, pitfalls
- `references/agent-capability-discovery.md` — Protocol for probing agent tools,
  constructing extraction pipelines, worked examples across platforms
- `references/fixed-layout-epub.md` — Fixed-layout detection and properties
  (rendition:layout, orientation, spread, viewport meta)
- `references/accessibility.md` — WCAG alignment, alt text, heading hierarchy,
  ARIA roles, Ace integration, accessibility metadata
- `references/media-overlays.md` — SMIL synchronization, audio-text pairing,
  skippability/escapability, detection from manifest
