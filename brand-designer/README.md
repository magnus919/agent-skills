# Brand Designer — Document and Generate Brand Identity

A systematic toolkit for capturing brand identity in structured, durable form. Produces markdown specs, compiled brand books, and brand-compliant images.

## Why Install This Skill

When your agent loads this skill, it becomes a **brand identity specialist** who can:

- **Scaffold complete brand documentation** — strategy, visual identity, voice & tone, application guidelines
- **Validate brand consistency** — checks completeness of your brand documentation
- **Compile brand deliverables** — one-page brand cards or full brand books
- **Generate brand-compliant images** — reference-image-aware generation for consistent visuals

Reference-led direction helps you turn rough visual preferences into a usable style
guide, refine editable concepts, and preserve approved examples without reinventing
your brand on every task. Customer message handoffs carry the approved offer into
your strategy and voice guidelines while keeping evidence, claim limits, and
review decisions visible. Worked adaptations show how the same offer can sound
different across channels while keeping its meaning intact. Final-copy review
compares polished expressions with supplied facts and uncertainties; it is not an
automatic verifier.

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete workflow guide from scaffold to delivery |
| `templates/` | 7 brand documentation templates (strategy, visual identity, voice, application, governance, asset inventory) |
| `scripts/brand-book` | CLI for init, validate, and compile operations |
| `scripts/generate` | Image generation for brand cards and mockups |
| `references/` | Component decisions, visual direction, and customer-message handoffs |

## Triggers

Load this when you need a brand card for press/stakeholders, visual identity documentation, brand voice guidelines, a full brand book for agency handoff, an inventory of brand assets, or approved customer messages translated into brand voice.

## Requirements

Python 3.8+ for the CLI; image generation requires a compatible backend. Templates are plain markdown.


## Quick Start

```sh
python3 brand-designer/scripts/brand-book init /tmp/my-brand --name "Acme"
```

This creates seven Markdown templates. Fill strategy and voice with your approved
message brief, then validate and compile the brand documentation.
