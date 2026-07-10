# Project Gutenberg — Public Domain Book Toolkit

Search, download, and extract clean text from 70,000+ free public-domain ebooks. Ships a portable CLI with zero external dependencies.

## Why Install This Skill

When your agent loads this skill, it can **work with the world's largest library of free ebooks**. That means:

- **Search by title, author, or keyword** — find any public-domain book
- **Download plain text or EPUB** — choose the format that suits your use case
- **Extract clean content** — strips Project Gutenberg licensing boilerplate automatically
- **Classify fiction vs non-fiction** — categorize what you find
- **Full search-to-text pipeline** — one command from title to clean text

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Quick start, how it works, command reference |
| `scripts/gutenberg` | Portable Python CLI — search, download, extract, classify, pipeline |

## Quick Start

```bash
python3 scripts/gutenberg search "Moby Dick"
python3 scripts/gutenberg download 2701 --format txt
python3 scripts/gutenberg extract 2701
python3 scripts/gutenberg pipeline "Alice's Adventures in Wonderland"
```

## Triggers

Load this when someone mentions "Gutenberg," "public domain," "download a book," "classic literature," or any public-domain title or author.

## Requirements

Python 3.8+ with **zero external dependencies** — uses only the standard library.
