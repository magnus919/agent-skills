# Open Knowledge Format (OKF) — Google's AI Agent Knowledge Standard

Google's vendor-neutral format for representing knowledge as markdown files with YAML frontmatter, designed for AI agent consumption. Create, validate, and consume knowledge bundles.

## Why Install This Skill

When your agent loads this skill, it can **create and validate OKF knowledge bundles** — the emerging standard for AI agent knowledge. That means:

- **Structure knowledge for AI consumption** — bundles of markdown with YAML frontmatter
- **Validate bundle integrity** — check frontmatter, cross-links, and directory structure
- **Create from templates** — scaffold new concepts and bundles
- **Cross-link between concepts** — express relationships between knowledge units
- **Distribute without vendor lock-in** — plain markdown, cloneable via git

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Core concepts, spec overview, quick start |
| `scripts/okf-bundle-validate.py` | OKF bundle validation script |
| `assets/` | Concept template, example bundle |
| `references/` | Spec summary, bundle architecture, use cases |

## Triggers

Load this when working with OKF, creating knowledge bundles for AI agents, or converting documentation into agent-consumable format.

## Requirements

Python 3.8+ with PyYAML for validation. No API keys needed.


## Quick Start

Start with the setup and first workflow in SKILL.md, then use the linked resources for the specific task you need to complete.
