# EPUB — Ebook Creation, Extraction & Enrichment

Expert-level EPUB handling for reading, writing, editing, and extracting knowledge from EPUB2 and EPUB3 files. Ships a CLI tool and five detailed references.

## Why Install This Skill

When your agent loads this skill, it becomes an **ebook format specialist** who can:

- **Inspect EPUB structure** — see manifest, spine, TOC, metadata
- **Extract clean text** — per-chapter or single-file, stripped of boilerplate
- **Edit EPUBs non-intrusively** — metadata, chapters, spine, CSS — without breaking the file
- **Create valid EPUBs from scratch** — scaffold new ebooks
- **Extract knowledge with LLM mode** — facts, quotes, definitions, arguments via configurable LLM
- **Convert EPUB2 to EPUB3** — add NAV, update namespace, keep NCX compatibility
- **Batch process hundreds of EPUBs** — wrap any script across file globs
- **Validate against the spec** — EPUBCheck or Python fallback

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Decision table mapping tasks to scripts, EPUB format essentials |
| `scripts/` | 10 Python CLI scripts: info, text, scaffold, edit, images, batch, convert, validate, extract-knowledge |
| `references/` | 8 reference files: format internals, Python libraries, spec/validation, tutorials, fixed-layout, accessibility, media overlays |

## Triggers

Load this when you encounter EPUB files — to read, create, edit, extract, convert, or validate them.

## Requirements

Python 3.8+ with `EbookLib`. Optional: `beautifulsoup4`, `epublib`, Java (for EPUBCheck), and an LLM endpoint for knowledge extraction.


## Quick Start

Start with the setup and first workflow in SKILL.md, then use the linked resources for the specific task you need to complete.
