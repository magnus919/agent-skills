---
name: research-methodology
description: Plan, conduct, evaluate, and synthesize rigorous research. Use for journalistic, industry, or technical investigations that need credible evidence and a traceable method.
license: MIT
compatibility: No runtime dependency. Use appropriate retrieval tools and retain source URLs and access dates in the research log.
metadata:
  source_repo: https://github.com/magnus919/hermes-profiles
  source_commit: 867a555
---


# Research Methodology

Professional research process for a subagent. Three tracks based on the type of research:

- **Journalistic** — investigative pieces, primary source research, source-heavy narrative work
- **Industry analysis** — market research and strategy, signal detection
- **Academic/Comprehensive** — deep systematic research when depth matters most

All three share the same lifecycle (Scope → Gather → Evaluate → Analyze → Synthesize → Report) but differ in evidence standards, speed, and output format.

## The Research Lifecycle

```
SCOPE → GATHER → EVALUATE → ANALYZE → SYNTHESIZE → REPORT
```

## Reference Files

### Tracks

| Track | Reference | When to load |
|-------|-----------|-------------|
| **Journalistic** | `references/journalistic-research.md` | You're researching an investigative piece — primary sources, interviews, documents, series management, pre-publication verification |
| **Industry analysis** | `references/industry-analysis.md` | You're researching an industry analysis piece — signal detection, corporate evidence, competitive intelligence, case study standards |
| **Academic / Comprehensive** | `references/research-lifecycle.md` | You're doing deep systematic research — question scoping, search strategy, inclusion/exclusion criteria |

### Shared Methodology

| Reference | When to load |
|-----------|-------------|
| `references/source-evaluation.md` | You need to judge whether a source is credible — CRAAP test, triangulation, reliability tiers |
| `references/structured-analytic-techniques.md` | You need to evaluate competing explanations — ACH, driving forces, pre-mortem, indicators |
| `references/synthesis-patterns.md` | You need to combine findings from multiple sources into synthesized conclusions |
| `references/technical-verification.md` | You need to test a technical claim by reproducing it — benchmarks, API behavior, configuration |

### Assets

| Asset | What it produces |
|-------|-----------------|
| `assets/research-brief.md` | Structured brief with findings, confidence assessment, evidence table, open questions |
| `assets/research-log.md` | Traceable record of searches, sources, and decisions |

## Pre-Publication Gateway

For any piece that makes factual claims, load the relevant track's verification protocol before reporting back:

- **Journalistic:** 7-step pre-publication protocol from `references/journalistic-research.md`
- **Industry:** 7-step research protocol from `references/industry-analysis.md`
- **Technical:** 5-step reproduction protocol from `references/technical-verification.md`

## Portability

This skill is intentionally host-neutral. Use your agent's normal mechanisms to load the references, templates, and scripts listed here. Do not assume a particular profile system, task orchestrator, memory service, or response-handoff format.
