# product-lifecycle

Route a product through its full lifecycle — from discovery to post-launch
learning — by composing existing specialist product skills with phase-entry
evidence, handoff artifacts, and escalation rules.

## Why Install This Skill

Product work is naturally multi-phase: you discover a problem, validate a
strategy, design a solution, run experiments, hand off to delivery, drive
adoption, measure success, and decide whether to continue or retire. But the
specialist skills that support each phase — product-discovery,
product-strategy, product-experimentation, product-adoption, and others — don't
connect to each other. An agent that loads product-discovery has no built-in
knowledge of what comes next or what evidence to hand off.

The product-lifecycle bundle fills this gap. It's a thin orchestration layer
that sits above the specialist skills and provides three things:
1. A phase routing table that tells the agent which skill to load at each point
   in the lifecycle.
2. Phase-entry evidence and handoff contracts so the agent knows what to expect
   at each transition and what to produce for the next phase.
3. Stop and escalation rules at every phase so the agent knows when to halt —
   and the lifecycle ledger preserves what was learned even when work stops.

The bundle is thin by design. It never duplicates a specialist's methodology.
If you only need one phase, load that specialist skill directly. If you need to
navigate a product across multiple phases with evidence handoffs between them,
load this bundle.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Thin umbrella with a 9-phase routing table, loading protocol, and "When not to use" boundary |
| `README.md` | This file — human-facing overview |
| `AGENTS.md` | Agent-facing loading and operational instructions |
| `references/phases.md` | Detailed per-phase contracts: entry evidence, output artifacts, escalation behavior, completion criteria, and lifecycle evidence ledger spec |
| `references/discovery-brief.md` | Bounded discovery brief comparing with existing bundles (neckbeard, workflow-architect, tailscale, research-and-vault) and stating the bundle boundary |
| `references/capability-map.md` | Capability area → owning skill lookup table for quick reference without traversing the full lifecycle |
| `evals/evals.json` | Schema-v1 output-quality evaluation cases covering a complete lifecycle, ambiguous requests, failed experiments, non-adoption, and justified retirement |

## Quick Start

Load the umbrella when you need to route a product across multiple lifecycle
phases:

1. Start with the phase routing table in `SKILL.md` to locate your current phase.
2. Load `references/phases.md` for the detailed phase contract.
3. Load the specialist skill(s) named in the phase row and follow their method.
4. Write phase outputs to the lifecycle evidence ledger.
5. The next phase reads the ledger and continues.

For single-phase work, load the specialist skill directly — e.g.,
`product-discovery` for stakeholder interviews, `product-experimentation` for
experiment design, or `product-adoption` for adoption planning.

## Triggers

- Evaluating a new product idea end-to-end.
- Managing a product through its lifecycle phases.
- Connecting product phases that currently operate in isolation.
- Needing phase-entry evidence and handoff contracts between product skills.
- Deciding whether to continue, pivot, or retire a product.
- A stakeholder request that needs to be routed through discovery, strategy, and validation before delivery.
- A product that has launched and needs adoption measurement, success evaluation, and lifecycle review.

Do not trigger for:
- A single product task owned by a specialist skill — load that skill directly.
- Software delivery lifecycle work — route to `neckbeard`.
- Standalone strategic analysis, financial modeling, or GTM planning without a lifecycle context.

## Requirements

- No API keys, services, or network dependencies.
- No environment variables required.
- Compatible with any agent harness that supports the Agent Skills format.
- The specialist skills this bundle routes to must be installed. The bundle
  assumes the following catalog skills are available: `product-discovery`,
  `product-strategy`, `product-roadmapping-and-portfolio`, `product-design-and-ux`,
  `product-experimentation`, `product-analytics-and-measurement`,
  `product-adoption`, `conditional-customer-success`,
  `product-operations-and-governance`, `product-lifecycle-learning`,
  `implementation-planning`, `spec-driven-development`, `production-readiness`,
  `release-engineering`, `product-methodology`, `go-to-market`,
  `financial-modeling`, `data-scientist`.
