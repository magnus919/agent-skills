# SEO

One umbrella skill for technical SEO, on-page optimization, Answer Engine Optimization (AEO), and Generative Engine Optimization (GEO). It helps an agent improve search discoverability and AI-answer visibility without confusing provider-specific evidence with universal ranking rules.

## Why Install This Skill

Search visibility now spans ranked results, direct answers, AI Overviews, conversational search, and generated answers. This skill consolidates the former SEO audit and AEO workflows so an agent can inspect the technical foundation, improve human-useful content, implement supported controls, and measure citations and referrals with explicit evidence boundaries.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Umbrella routing, terminology, workflow, evidence rules, and completion boundary |
| `references/` | Technical SEO, on-page SEO, schema, content strategy, AEO/GEO implementation, provider guidance, agent-readable content, and measurement |
| `templates/` | Implementation plan, question cluster, citation observation, optional `llms.txt`, and crawler-policy templates |
| `scripts/aeo_audit.py` | Read-only structural audit of local HTML or a URL |
| `scripts/build_prompt_matrix.py` | Deterministic prompt-set generation |
| `scripts/test_aeo_scripts.py` | Offline regression tests for the scripts |
| `evals/evals.json` | Output-quality evaluation cases |

## Quick Start

```bash
python3 scripts/aeo_audit.py https://example.com/article --json
python3 scripts/build_prompt_matrix.py topics.json --output prompt-matrix.json
python3 -m pytest scripts/test_aeo_scripts.py
```

The scripts are read-only and use Python's standard library. They do not call an LLM, publish, submit URLs, or modify robots policy.

## Triggers

- Audit or improve technical SEO, on-page SEO, schema, content discoverability, or search visibility
- Implement or assess AEO, GEO, LLMO, AI-search optimization, or generative search visibility
- Make content easier for people and answer systems to understand, retrieve, cite, and verify
- Build question clusters, answer-first content, evidence blocks, entity architecture, or canonical topic maps
- Assess AI crawler controls, preview controls, sitemaps, freshness, `llms.txt`, Markdown delivery, or content negotiation
- Design frozen prompt sets, citation logs, share-of-voice checks, or bounded AI-search experiments
- Complete Ghost metadata, social cards, or schema injection in support of search visibility

## Requirements

- Python 3.9+ for bundled scripts
- Network access when auditing a URL; local HTML works offline
- Provider dashboards, CMS credentials, and Search Console access are optional and belong to the relevant platform workflow
