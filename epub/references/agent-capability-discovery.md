# Agent Capability Discovery & Pipeline Construction

This reference teaches the agent how to discover its own capabilities before
constructing an EPUB extraction or construction pipeline. The skill must be
portable across any agent harness — this discovery step is how it adapts.

## Why Discovery Matters

Different agent platforms have different capabilities:

| Platform | File I/O | Subagents | Cron | Kanban | Vector DB | Vault |
|----------|----------|-----------|------|--------|-----------|-------|
| Hermes Agent | terminal/write_file | delegate_task | cronjob | kanban | LightRAG | Obsidian vault |
| Claude Code | Bash/Write | Task tool | Scheduled tasks | — | — | — |
| OpenCode | Terminal/File | Subagents | — | — | — | — |
| GitHub Copilot | Terminal/File | — | — | — | — | — |
| Cursor | Terminal/File | — | — | — | — | — |
| Basic harness | Terminal only | — | — | — | — | — |

The extraction pipeline works on any of these — but the *shape* of the pipeline
changes based on what's available.

## Step 1: Enumerate Available Capabilities

Before building a pipeline, probe the agent's toolset. The exact method depends
on the platform, but the principle is the same: check what's available.

Several scripts in this skill use an **LLM auto-detection convention:** if the
environment variables `EPUB_LLM_URL` and `EPUB_LLM_KEY` are set, the scripts
enable LLM-powered features automatically. If they're absent, the scripts fall
back to heuristic/deterministic mode. This means you don't need to pass
`--no-llm` flags or state — the scripts detect it.

```bash
# Set once for all scripts:
export EPUB_LLM_URL="https://your-provider.example.com/v1"
export EPUB_LLM_KEY="sk-..."
export EPUB_LLM_MODEL="model-name"  # optional
```

Any OpenAI-compatible provider works — OpenAI, Anthropic via proxy, local
llama.cpp, Ollama, vLLM, OpenCode, etc.

### What to check

| Capability | How to detect |
|-----------|---------------|
| **Terminal / shell access** | Can you run shell commands? |
| **File write** | Can you create files on disk? |
| **Web access** | Can you make HTTP requests, scrape URLs, search the web? |
| **Subagents / task delegation** | Can you spawn child agents for parallel work? |
| **Scheduling / cron** | Can you schedule jobs to run later? |
| **Persistent memory** | Can you save facts that survive this session? |
| **Vector / semantic search** | Can you search by meaning, not keywords? |
| **Kanban / workflow boards** | Can you create and track tasks on boards? |
| **Vault / knowledge base** | Is there a structured note system (Obsidian, etc.)? |
| **LLM access** | Can you call an LLM for text extraction/classification? |
| **Browser automation** | Can you interact with web pages dynamically? |

### Decision: Do you have what this skill's scripts need?

At minimum, you need:
- Terminal/shell access (to run Python scripts)
- File write (to save output)

Everything else enriches the pipeline but isn't required.

## Step 2: Classify Into Pipeline Stages

An EPUB knowledge extraction pipeline has five stages:

```
EPUB file
  ↓
[INGEST] — get the EPUB (local file, URL download, etc.)
  ↓
[PARSE] — extract content (text, images, metadata, structure)
  ↓
[EXTRACT] — identify knowledge (key passages, facts, quotes, arguments)
  ↓
[FORMAT] — structure the output (atoms, memory entries, JSON, markdown)
  ↓
[SINK] — deliver to destination (vault, memory, vector DB, file, etc.)
```

### INGEST options

| If you have... | Use... |
|---------------|--------|
| Local file access | Direct path to EPUB |
| Web access + download | `curl` or web tools to fetch EPUB |
| User provides path | Prompt user for file location |

### PARSE options

| If you have... | Use... |
|---------------|--------|
| Python + pip | `scripts/epub-text` or `scripts/epub-info` |
| Python only (no pip) | `zipfile` + `xml.etree.ElementTree` (stdlib) |
| Neither | Ask user to unzip and provide the OPF/XHTML files |

### EXTRACT options

| If you have... | Use... |
|---------------|--------|
| LLM access | `scripts/epub-extract-knowledge` with LLM mode |
| No LLM | `scripts/epub-extract-knowledge --no-llm` (heuristic mode) |
| | Manual keyword/phrase extraction |

### FORMAT options

| If you have... | Output format |
|---------------|---------------|
| Vault (Obsidian) | Atom/molecule templates |
| Persistent memory | Memory entry format |
| Vector DB / LightRAG | JSON with title + content + source |
| File only | Markdown files, one per chapter |

### SINK options

| If you have... | Destination |
|---------------|------------|
| Vault write | Obsidian vault atoms/molecules |
| Memory tool | Direct memory entries |
| Vector DB ingestion | LightRAG / equivalent |
| File write | `.md`, `.json`, `.txt` files |
| None | Print to terminal (ephemeral) |

## Step 3: Construct and Propose a Pipeline Plan

Based on what's available, build a specific plan. Present it to the user for
approval before executing.

### Example: Full Hermes Agent Pipeline

```
INGEST:   Read EPUB from local path
PARSE:    epub-text --json → extract per-chapter text
EXTRACT:  epub-extract-knowledge --format atoms → identify facts/quotes/arguments
FORMAT:   Render as Obsidian vault atom templates
SINK:     write_file → vault atoms in 1 - Atoms/
VERIFY:   obsidian-wiki-link-verification → backlink audit
ENRICH:   LightRAG insert → semantic association
```

### Example: Minimal Pipeline (Terminal Only)

```
INGEST:   User provides EPUB path
PARSE:    epub-text → plain text file
EXTRACT:  epub-extract-knowledge --no-llm → heuristic extraction to JSON
FORMAT:   JSON → markdown summary
SINK:     write_file → output.md
```

### Example: Batch Pipeline (with Delegation)

```
INGEST:   Find all EPUBs in directory
FOR EACH EPUB:
  PARSE:   Delegate to subagent → epub-text + epub-info
  EXTRACT: Delegate to subagent → epub-extract-knowledge --no-llm
  SINK:    Collect outputs, write summary
```

## Step 4: Execute with User Approval

1. **Present the pipeline plan** — what stages, what tools, what outputs
2. **Ask for confirmation** — or proceed if the user has said to go ahead
3. **Execute each stage** — report progress at each boundary
4. **Handle failures** — if a tool is missing, fall back to the next option

## Principles

1. **Don't assume capabilities exist.** Check before building the pipeline.
2. **Default to the simplest pipeline that works.** Extra complexity without
   extra value is noise.
3. **Fall back gracefully.** If LLM isn't available, use heuristics. If pip
   isn't available, use stdlib. If nothing works, explain what's missing.
4. **Report at stage boundaries.** Don't make the user ask "what's happening?"
5. **This skill ships the scripts.** All parsing and extraction logic is in
   `scripts/`. The agent uses them — it doesn't reimplement them.
