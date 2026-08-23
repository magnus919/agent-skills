# LLM Configuration & Knowledge Extraction

Load this file before running any knowledge-extraction pipeline: it documents
the shared environment-variable convention that turns on optional LLM-powered
features across this skill's scripts, and the deep-dive guidance for
extracting structured knowledge from EPUB content.

## LLM Configuration Convention

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
