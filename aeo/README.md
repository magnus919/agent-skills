# AEO

A focused implementation methodology for Answer Engine Optimization: making useful, attributable answers discoverable and reusable by AI search systems without relying on folklore or guaranteed “AI ranking” hacks.

## Why Install This Skill

AEO advice is full of confident claims that collapse different systems, measurements, and goals into one vague promise. This skill gives your agent a disciplined way to research the actual target surface, map questions to owned answers, implement useful content and machine-readable signals, and measure citations with reproducible evidence.

It is intentionally narrower than SEO. Use it for answer architecture, question clusters, entities, citations, provider crawler controls, optional agent-readable files, and AI-answer experiments. Hand broad search audits and CMS-specific changes to the existing SEO and platform skills.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | AEO routing, implementation loop, decision rules, and completion gate |
| `references/` | Evidence boundaries, implementation, content architecture, structured data, discovery, platform guidance, and measurement |
| `templates/` | Implementation plan, question cluster, citation log, `llms.txt`, and crawler policy templates |
| `scripts/aeo_audit.py` | Read-only structural audit of a local HTML file or URL |
| `scripts/build_prompt_matrix.py` | Deterministic prompt-set generation from topics and questions |
| `scripts/test_aeo_scripts.py` | Offline regression tests for the bundled scripts |
| `evals/evals.json` | Output-quality evaluation cases |

## Quick Start

```bash
python3 scripts/aeo_audit.py https://example.com/article --json
python3 scripts/build_prompt_matrix.py topics.json --output prompts.json
```

Both commands are read-only and use only Python's standard library. They do not call an LLM or modify the target site.

## Triggers

- Implement Answer Engine Optimization, AEO, GEO, LLMO, or AI-search visibility
- Make a page more likely to be understood, retrieved, cited, or correctly summarized by answer engines
- Build question clusters, answer-first content, evidence blocks, or citation measurement
- Implement or assess `llms.txt`, AI crawler controls, Markdown delivery, schema parity, or freshness signals
- Design a reproducible prompt set or AI-answer citation experiment

## Requirements

- Python 3.9+ for bundled scripts
- Network access only when auditing a URL; local HTML files work offline
- No API keys required
- Provider dashboards, CMS credentials, and search-console access are optional and must be handled by their own operational skills
