---
name: aeo
description: Use when designing, implementing, or measuring Answer Engine Optimization (AEO) for AI answers, citations, generative search, or agent-readable web content. Do not use this as a general SEO audit or CMS operations guide; route those parts to seo-audit or the relevant platform skill.
license: MIT
compatibility: Requires access to the target site or content for implementation and verification; bundled scripts use Python 3.9+ standard library only.
metadata:
  related_skills: seo-audit, research-methodology, technical-reference-research
  scope: answer-engine-optimization
---

# Answer Engine Optimization (AEO)

A source-disciplined implementation methodology for making useful, attributable answers discoverable and reusable by AI search and answer systems without treating vendor folklore as a ranking guarantee.

## When to use

Load this skill when the work involves:

- planning or implementing AEO, GEO, LLMO, AI-search visibility, or citation visibility;
- turning a topic into question clusters, answer-first pages, evidence blocks, or reusable knowledge assets;
- implementing or validating answer-oriented HTML, JSON-LD, `llms.txt`, crawler controls, sitemaps, freshness signals, or Markdown delivery;
- designing prompt sets, citation observation logs, share-of-voice experiments, or AI-answer measurement;
- translating an AEO audit into a bounded implementation plan.

Do not load this skill alone for broad technical SEO, keyword research, page-speed work, CMS administration, or ordinary copy-editing. Route those concerns to `seo-audit`, a platform skill, or the appropriate writing skill. AEO cannot guarantee inclusion, ranking, citation, or traffic.

## When not to use

Do not use this skill alone for broad technical SEO, keyword research, page-speed work, CMS administration, or ordinary copy-editing. Route those concerns to `seo-audit`, a platform skill, or the appropriate writing skill.

## Operating model

AEO is an implementation loop, not a bag of hacks:

1. **Scope** the audience, entities, questions, answer surfaces, business outcome, and content boundary.
2. **Research** primary platform guidance and the subject's authoritative evidence.
3. **Map** question clusters to pages and record the intended answer, evidence, entity, freshness, and owner.
4. **Implement** human-useful content first, then machine-readable structure and discovery controls that the target systems actually support.
5. **Measure** with a frozen prompt set and platform-native data where available. Record the full answer, citations, URL, date, model/surface, and failure mode.
6. **Learn** from changes with a bounded experiment. Keep SEO fundamentals and AEO-specific hypotheses separate.

Read `references/implementation-playbook.md` for the full workflow and completion gate. Read `references/evidence-boundaries.md` before adopting a tactic or making a performance claim.

## Decision rules

- **Answer first, not AI-first:** Put a concise, accurate answer near the relevant heading, followed by qualifications, evidence, and useful detail. Do not distort prose into fragments or keyword variants.
- **One question, one canonical answer location:** Consolidate duplicate answers, link related questions, and make ownership and update responsibility explicit.
- **Evidence beats assertion:** Cite primary sources, state scope and date, preserve uncertainty, and distinguish observation, vendor claim, inference, and experiment result.
- **Visible content is the contract:** JSON-LD, `llms.txt`, metadata, and summaries must agree with the rendered page. Structured data does not create facts.
- **Access is a choice:** Robots directives control access only where the relevant crawler honors them. Separate search access, training access, user-triggered fetching, and commercial permissions.
- **No universal AEO signal:** A tactic supported by one provider, experiment, or tool is not a cross-engine law. Label provider scope and confidence.
- **Freshness must be earned:** Change dates, `lastmod`, and update notices only when the underlying content changed. Never manufacture freshness.
- **Measure citation quality, not only count:** A citation that is irrelevant, stale, misattributed, or contradicted is a defect even when the count rises.

## Reference routing

| Need | Read |
|---|---|
| What AEO is, what it is not, and evidence confidence | `references/evidence-boundaries.md` |
| End-to-end implementation sequence and acceptance gate | `references/implementation-playbook.md` |
| Question/topic maps, answer blocks, entity and evidence design | `references/content-and-entity-architecture.md` |
| JSON-LD, visible parity, schema selection, validation | `references/structured-data.md` |
| Crawlers, robots controls, sitemaps, IndexNow, freshness | `references/discovery-and-freshness.md` |
| `llms.txt`, Markdown delivery, and provider-specific support | `references/agent-readable-content.md` |
| Prompt sets, citation logs, metrics, experiments, and limits | `references/measurement-and-experimentation.md` |
| Platform-specific primary guidance and refresh points | `references/platform-guidance.md` |
| Provenance, authority tier, access date, and claim ledger | `references/source-index.md` |

## Reusable assets

- `templates/aeo-implementation-plan.md` — scope, hypotheses, changes, owners, risks, and verification.
- `templates/question-cluster.md` — question-to-page and evidence mapping.
- `templates/citation-observation-log.md` — reproducible answer/citation observations.
- `templates/llms.txt.template` — optional proposal-format `llms.txt`, clearly marked non-universal.
- `templates/robots-ai-crawlers.txt` — decision-oriented crawler policy template; do not copy without reviewing provider semantics.

## Available Scripts

Run bundled scripts non-interactively from the skill directory (`aeo/`). They never publish, edit, submit URLs, call an LLM, or change robots policy.

| Script | Purpose | Invocation |
|---|---|---|
| `scripts/aeo_audit.py` | Read-only structural audit of a local HTML file or an HTTP(S) URL, emitting JSON findings. Run it after implementing answer-oriented markup to verify structure at the source level before making claims about a page. | `python3 scripts/aeo_audit.py <page.html-or-URL>` |
| `scripts/build_prompt_matrix.py` | Deterministic prompt-matrix generator from a JSON topics file; writes the matrix to the path given with `--output`. Run it when starting measurement, to freeze the prompt set before collecting any citation observations. | `python3 scripts/build_prompt_matrix.py <topics.json> --output prompt-matrix.json` |
| `scripts/test_aeo_scripts.py` | Offline pytest suite covering the two scripts above. Run it if you modify either script or when auditing a change to their output. | `python3 -m pytest scripts/test_aeo_scripts.py` |

## Routing to and from SEO

Use `seo-audit` for broad crawlability, indexability, on-page SEO, schema eligibility, and site-level search audits. When its work reaches AI-answer structure, citation measurement, provider-specific crawler semantics, or `llms.txt`, load this skill. Conversely, use this skill to identify AEO changes, then route platform mutations and general SEO remediation to the relevant existing skill.

## Common failure modes

- Treating Google AI Overviews guidance as proof of how ChatGPT, Perplexity, or every answer engine works.
- Calling `llms.txt`, FAQ schema, headings, short paragraphs, or “mentions” guaranteed ranking or citation levers.
- Inventing question pages at scale, duplicating near-identical answers, or adding boilerplate that helps neither people nor retrieval.
- Publishing schema or summaries that say more than the visible content proves.
- Using third-party citation counts without the prompt set, date, surface, model, URL, and retrieval method.
- Confusing being mentioned, being cited, ranking, receiving a click, and producing a conversion.
- Disallowing a crawler without separating search visibility from training or user-triggered fetch behavior.
- Calling a script or validator “AEO complete” without checking the rendered page and an answer surface.

## Prerequisites

- Python 3.9+ with standard library only; the bundled scripts require no third-party packages.
- Access to the target site or content being implemented and verified: `aeo_audit.py` accepts a local HTML file or fetches an HTTP(S) URL directly.

## Limitations

- The scripts inspect source HTML, not rendered pages: they do not execute JavaScript, call LLMs, publish anything, submit URLs to indexes, or change crawler directives.
- No script can observe whether an answer engine cites a page; citation observation must be collected manually following `references/measurement-and-experimentation.md`.
- A passing structural audit is evidence of implemented structure only — it does not establish inclusion, ranking, citation, or traffic in any AI answer surface.

## Verification checklist

- [ ] Scope names target entities, questions, surfaces, outcomes, and exclusions.
- [ ] Primary provider guidance is current and its limits are recorded.
- [ ] Every target question maps to one canonical page/section and a responsible owner.
- [ ] Opening answers, evidence, caveats, links, and update dates are visible and accurate.
- [ ] Structured data parses and matches visible content; unsupported types are not added for decoration.
- [ ] Robots, sitemap, and freshness changes were previewed and verified at the public boundary.
- [ ] Optional files such as `llms.txt` are labeled as proposals or provider-specific aids, not universal requirements.
- [ ] Prompt observations preserve exact answers and citations, with a frozen test set and access dates.
- [ ] Completion distinguishes implemented, verified, observed, inferred, and unresolved claims.
