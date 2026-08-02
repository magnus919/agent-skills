# Production Excellence

Assemble cross-domain production evidence into a defensible launch or operational decision — go, no-go, defer, exception, or escalation — with an accountable owner and a post-launch learning path.

## Why Install This Skill

When a service or change is heading to production, evidence is scattered across multiple domains: a readiness review in one place, a migration plan in another, recovery-exercise results somewhere else, a capacity model in a spreadsheet, and incident history in yet another tool. Without a single acceptance layer, teams either launch with invisible gaps or drown in coordination overhead. Production Excellence gives your agent that layer — a thin, structured gate model that reads evidence from every specialist domain and produces one of five clear, defensible outcomes with an accountable owner attached.

After installing, your agent can run a production gate review for any change — from a low-risk docs update to a high-risk customer-facing launch with migration, recovery, and cost/SLO tradeoffs. The bundle composes the specialist catalog (production-readiness, migration-engineering, resilience-and-recovery, capacity-and-cost-engineering, incident-learning, plus SRE, release, platform, security, data, and QA) without copying a single runbook. Post-launch, it routes outcomes into incident-learning and product-lifecycle-learning so production evidence flows back into decisions instead of being forgotten.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Thin umbrella entry point: readiness routing table for 5 production-domain routes and 7 supporting specialists, cross-domain entry evidence requirements, gate/exception model (go/no-go/defer/exception/escalation), operational handoff, and post-launch learning paths |
| `AGENTS.md` | Agent-specific loading notes: nested-skill behavior, harness compatibility, and progressive-disclosure guidance |
| `README.md` | This human-facing overview |
| `references/discovery-brief.md` | Bounded discovery brief comparing the bundle against 13 existing production and release skills (SRE, release, platform, security, data, QA, plus the 5 milestone production skills and verification/lifecycle-learning) |
| `references/evidence-packet.md` | Production evidence packet specification: entry-evidence requirements for readiness, migration, recovery, capacity/cost, and incident-learning domains — usable for both new services and changes to existing systems |
| `references/gates.md` | Full gate and exception model: go, no-go, defer, exception, and escalation outcomes, each with conditions, evidence requirements, risk-class applicability, and post-gate handoff rules |
| `references/handoff-record.md` | Operational handoff record template: service identification, gate outcome, evidence summary, gap register, post-launch learning paths (incident-learning and product-lifecycle-learning), and sign-off fields |
| `evals/evals.json` | Five integrated evaluation cases covering normal release, untested rollback, data migration, dependency outage, and cost/SLO conflict |
| `manifest.yaml` | Machine-readable bundle manifest (schema v1): purpose, audience, stages, included skills, prerequisites, outputs, handoffs, conflicts, and eval suite |

## Quick Start

1. Identify the service or change and its risk class (Low / Standard / High per production-readiness).
2. Gather entry evidence from each applicable domain using the evidence packet (`references/evidence-packet.md`). Every domain needs a named source or an explicit gap with an owner and due date.
3. Run the gate model (`references/gates.md`): evaluate the evidence against the five outcomes. Record the outcome with the accountable owner.
4. Populate the operational handoff record (`references/handoff-record.md`) — even for non-Go outcomes.
5. Route post-launch observations to incident-learning and product-lifecycle-learning per the handoff record's learning path.

## Triggers

- "Is this ready for production?"
- "Run a production gate review"
- "Assemble the production evidence packet"
- "We need a go/no-go decision for this launch"
- "Coordinate the production readiness review across teams"
- "What evidence is missing before we can launch?"
- "We have a migration, a recovery exercise, and a capacity model — are we clear to go?"
- "Route this launch outcome into our incident-learning process"
- A cross-team launch needs a single acceptance contract before proceeding
- A cost/SLO conflict needs a structured decision with accountable owners

## Requirements

- No runtime dependencies, API keys, or external services.
- The bundle routes to 12 specialist skills for detailed domain work; those skills must be present in the catalog for full routing capability (production-readiness, migration-engineering, resilience-and-recovery, capacity-and-cost-engineering, incident-learning, site-reliability-engineering, release-engineering, platform-engineering, secure-software-engineering, data-engineering, qa-methodology, verification-methodology — all currently exist in the repository).
