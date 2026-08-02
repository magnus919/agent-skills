# CNCF Landscape

Discover cloud-native technologies and turn the result into a decision-ready shortlist with evidence, trade-offs, and a validation plan.

## Why Install This Skill

When an architecture question starts with “what exists for this?”, an agent can easily return a familiar-name list or rank projects by stars. This skill gives it a live, source-grounded discovery path through the CNCF Landscape and a disciplined way to separate catalog facts from engineering judgment.

It is useful for architects and engineers exploring a capability that is not yet in their stack. The bundled query tool handles the static API’s filtering and bounded JSON output; the skill then asks the questions the catalog cannot answer: who will operate it, what constraints matter, what evidence is missing, and what small experiment could falsify the recommendation.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Trigger boundaries, query workflow, evidence discipline, and completion criteria |
| `scripts/landscape_query.py` | Read-only stdlib CLI for live project/member queries and local filtering |
| `references/api.md` | Verified endpoint map, field semantics, and static-site caveats |
| `references/decision-framework.md` | Candidate comparison and recommendation method |
| `references/output-template.md` | Reusable decision artifact structure |
| `tests/test_landscape_query.py` | Offline client and filter tests |
| `evals/evals.json` | Six output-quality cases covering normal and failure paths |
| `evals/trigger-queries.json` | Three should-trigger and two should-not-trigger routing probes |

## Quick Start

Requires Python 3.8+ and outbound HTTPS access. No API key is required.

```bash
python3 scripts/landscape_query.py \
  --category "Observability and Analysis" \
  --subcategory Observability \
  --search tracing \
  --maturity graduated \
  --has-license --has-release \
  --sort stars --limit 10
```

The command emits a JSON envelope containing the source endpoint, retrieval time, filters, counts, and matching records. Ask an Agent Skills-compatible assistant to interpret that evidence against your workload and constraints rather than treating the result as an automatic ranking.

## Triggers

Use when discovering or comparing CNCF/cloud-native projects, building a shortlist for an architecture decision, filtering technology candidates by maturity or repository evidence, or investigating what tools exist for a capability missing from the current stack.

Do not use it for operating a named project, general architecture methodology, or legal/procurement conclusions.

## Requirements

- Python 3.8 or newer
- Network access to `https://landscape.cncf.io`
- No credentials or third-party Python packages
