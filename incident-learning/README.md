# Incident Learning

Convert operational incidents, near misses, and exercise findings into verified, owned improvements across product, engineering, test, evaluation, and governance — with closure evidence, not just tickets.

## Why Install This Skill

Most teams create tickets after incidents. Few verify that the intended change actually happened and had the intended effect. This skill provides a structured method for converting raw incident evidence into durable follow-up work with verified closure — separating what was observed from what was inferred, mapping each finding to the right domain (product, code, tests, evals, operations, governance), and tracking every follow-up through to verified completion.

Install this skill when your agent needs to help teams move from "we filed tickets after the postmortem" to "we verified that the monitoring gap was closed, the regression test was added, and the eval case now catches the failure mode." It composes specialist capabilities from SRE, QA, verification, agent evaluation, product lifecycle learning, implementation planning, resilience-and-recovery, and production-readiness without duplicating their methodology, and it feeds learning records into the production-excellence and agent-production-operations bundles.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Trigger conditions, core principles, the incident learning record structure, loading guide, template index, routing table, and ownership boundaries |
| `references/discovery-brief.md` | Survey of adjacent skills (SRE, QA, verification, agent evals, product lifecycle learning, implementation planning, resilience-and-recovery, production-readiness) with ownership boundaries and routing decisions |
| `references/evidence-inference-taxonomy.md` | Full taxonomy for separating observed facts, causal hypotheses (with confidence levels), contributing conditions, and unresolved uncertainty |
| `references/escaped-from-analysis.md` | Method for mapping incidents to originating gaps: escaped requirements, missing monitoring/observability, unsafe authority/access, migration gaps, adoption consequences |
| `references/follow-up-domains.md` | Six-domain follow-up taxonomy (product, code, tests, evals, operations, governance) with ownership patterns and verification methods per domain |
| `references/verification-and-closure.md` | Closure standard requiring implementation evidence, verification evidence, and effect evidence; explicit rejection of ticket-only closure |
| `templates/incident-learning-record.md` | Structured record template with fields for observed facts, causal hypotheses, contributing conditions, unresolved uncertainty, and escaped-from mapping |
| `templates/causal-evidence-ledger.md` | Ledger template for tracking each causal claim with supporting evidence, confidence level, and alternative explanations |
| `templates/follow-up-work-map.md` | Six-domain follow-up work map with ownership, verification method, and status tracking per finding |
| `templates/verification-and-closure-record.md` | Per-follow-up closure record requiring implementation evidence, verification evidence, and effect evidence |
| `evals/evals.json` | Five output-quality eval cases covering: noisy incident report, monitoring gap, process failure, agent authority failure, and non-actionable follow-up rejection |

## Quick Start

Start with the incident-learning record template to structure the raw incident evidence — separating facts from hypotheses from uncertainty, and mapping the escaped-from gap. Then use the follow-up work map to assign each finding to a domain and owner. Track each follow-up through the verification and closure record.

Ask your agent to "convert this incident into a learning record" or "build a follow-up work map from this postmortem" and the skill's triggers will route the work.

## Triggers

- Converting operational incidents, near misses, or exercise findings into structured learning records with follow-up work.
- Separating observed facts from causal hypotheses and unresolved uncertainty in incident analysis.
- Mapping incident findings to follow-up work across product, code, tests, evals, operations, and governance domains.
- Tracking incident follow-up work to verified closure with implementation, verification, and effect evidence.
- Linking incidents to escaped requirements, missing monitoring, unsafe authority, migration gaps, or adoption consequences.
- Auditing incident follow-up closure rates or detecting unverified closures.

## Requirements

No runtime dependencies. The methodology is host-neutral and requires no specific tools, platforms, or API keys. The skill provides templates and method; incident data and follow-up work tracking must be supplied by the user's environment.
