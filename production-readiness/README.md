# Production Readiness

Assemble cross-domain production evidence into a risk-scaled launch decision — from a lightweight documentation release to a full user-facing service launch.

## Why Install This Skill

Every launch decision needs evidence from multiple domains: who owns the service, what SLOs protect it, whether security reviewed it, how to roll back, what it costs. Without a structured evidence packet, teams either launch with invisible gaps or get stuck in review churn. Production-readiness gives your agent a single, risk-scaled framework for assembling that evidence and producing a defensible go / no-go / defer / exception recommendation with an accountable owner attached.

After installing, your agent can run a proportional readiness review for any change — from a docs-only update (three evidence categories, self-review) to a customer-facing service launch (all 11 evidence categories with named sources, formal review, exception routing to explicit human approval). The skill routes detailed technical checks to the existing specialists (release-engineering, SRE, security, data, QA, platform) so it never duplicates what they already own.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Risk-class definitions (Low/Standard/High), 11-category evidence checklist with source/gap fields, four launch-decision outcomes with accountable owners, exception routing to explicit human approval, and a route-to table for 12 specialist skills |
| `README.md` | This human-facing overview |
| `references/discovery-brief.md` | Survey of existing production and engineering skills with ownership boundaries vs release-engineering and site-reliability-engineering |
| `references/readiness-record.md` | Fillable readiness-record template with all 11 evidence categories, risk-class selection, and launch-decision recording |
| `evals/evals.json` | Five output-quality evaluation cases covering low-risk docs, user-facing launch, migration-dependent release, missing owner evidence (blocked), and exception requiring human approval |

## Quick Start

1. Determine the risk class for your change: Low (docs-only, internal tool ≤1 team), Standard (user-facing feature, API addition), or High (customer-facing launch, SLO-bearing, trust-boundary crossing).
2. Fill the readiness record template (`references/readiness-record.md`) — for each of the 11 evidence categories, provide either a named source or an explicit gap with owner and due date.
3. Produce a launch decision: Go (all evidence present), No-go (blocking gap), Defer (postponed with conditions), or Exception (waiver with explicit human approval).
4. Record the decision with the accountable owner.

## Triggers

- "Is this ready to launch?"
- "Run a production-readiness review"
- "Assemble the launch evidence packet"
- "Do we have all the evidence for go/no-go?"
- "Check production readiness for this change"
- "We need a readiness record before the launch review"
- "What evidence is missing before we can launch?"
- A launch-review board or readiness gate is approaching
- A migration-dependent release needs coordinated readiness assessment
- A low-risk change needs a proportional (not full-scale) readiness check

## Requirements

- No runtime dependencies, API keys, or external services.
- The skill routes to existing catalog specialists for detailed technical checks; those skills must be present in the catalog for full routing capability (12 skills routed, all currently exist in the repository).
