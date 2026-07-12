---
name: seo-audit
description: Audit websites and pages for technical SEO, on-page SEO, schema markup, content discoverability, and answer-engine readiness. Use when prioritizing search visibility improvements.
license: MIT
compatibility: Requires access to the site or page being audited. Platform-specific references are optional and must be applied only when relevant.
metadata:
  source_repo: https://github.com/magnus919/hermes-profiles
  source_commit: 867a555
---


# SEO Audit

Full-spectrum audit for sites, articles, and content strategies. Covers both traditional SEO and Answer Engine Optimization (AEO/GEO) — the practice of structuring content so LLMs and AI answer engines (ChatGPT, Perplexity, Gemini, Claude, Google AI Overviews) extract and cite it.

All output is artifact-pyramid-compliant. The only response to the caller is the absolute path to `00-index.md`.


## SEO + AEO Audit: [Site/Page URL]

**Overall Health:** [Good / Fair / Poor]
**Score:** [N/100]

### SEO Priority Findings
1. [Critical] → [Action]

### AEO Priority Findings
1. [Critical] → [Action]

### Quick Wins
1. [Low effort, high impact] → [Action]

### Verdict
[One paragraph summarizing the single most important thing to fix and expected impact.]
```

## Contents

| File | What it covers |
|------|----------------|
| `references/technical-seo.md` | Crawlability, indexability, robots.txt, sitemaps, page speed, Core Web Vitals, mobile-friendliness, HTTPS, canonical URLs, hreflang |
| `references/onpage-seo.md` | Title tags, meta descriptions, heading hierarchy, keyword placement, content quality, internal linking, image optimization |
| `references/schema-markup.md` | Schema.org types (TechArticle, FAQPage, HowTo, Article, BlogPosting, BreadcrumbList, Organization), JSON-LD format, Google rich results, validation |
| `references/content-strategy-seo.md` | Topic clusters, pillar pages, keyword research, gap analysis, SERP feature targeting, topical authority |
| `references/ghost-metadata.md` | Ghost CMS metadata fields (meta_title, meta_description, custom_excerpt), social media cards (OG, Twitter), code-injected schema (JSON-LD, FAQPage, TechArticle, @graph), per-post and site-wide injection, validation |
| `references/aeo-methodology.md` | Answer Engine Optimization — LLM RAG pipeline, answer-first content architecture, AEO-specific schema (FAQPage 3.2× boost), Ethan Smith/Graphite frameworks, question clusters, llms.txt, content negotiation, measurement |
| `assets/audit-report-template.md` | Blank report scaffold for new audits |

## When to Use

Load this skill when:
- Auditing a site for technical SEO issues
- Optimizing a new article for search and AI citation before publication
- Validating structured data on an existing page
- Completing Ghost CMS metadata (meta, social cards, schema injection) before publish
- Running an AEO readiness audit (llms.txt, content negotiation, question-cluster coverage)
- Developing a content strategy with SEO + AEO in parallel
- Diagnosing why a site or page isn't performing in search or AI citation

Do NOT load when:
- Only mechanical content fixes are needed (use `copy-edit`)
- Only writing is needed (use `writer` profile)

## Portability

This skill is intentionally host-neutral. Use your agent's normal mechanisms to load the references, templates, and scripts listed here. Do not assume a particular profile system, task orchestrator, memory service, or response-handoff format.
