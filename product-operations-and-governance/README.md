# Product Operations and Governance

Define and run the recurring system that keeps product decisions disciplined: who decides what, with what evidence, on what cadence, and what happens when decisions are contested or evidence is missing.

## Why Install This Skill

Product teams make hundreds of decisions every quarter — what to build first, whether an experiment result is strong enough to ship, when to retire a feature. Without an explicit governance system, these decisions default to the loudest voice, the most senior person in the room, or (worst) no decision at all. Governance isn't bureaucracy; it's the answer to "how do we decide, and how do we know we decided well?"

This skill gives your agent the ability to design and operate a product governance model that fits your team, not a generic org chart. It distinguishes product governance (intake, portfolio reviews, roadmap decisions, experiment and launch reviews, lifecycle choices) from executive governance (capital allocation, org structure) and from technical delivery gates (CI/CD, deployment checklists) — so your agent routes each question to the right place.

After installing, your agent can: map decision rights with named accountable owners, configure six recurring review cadences (intake through lifecycle), set evidence standards that scale from lightweight startup mode to high-assurance regulated mode, record exceptions so waivers don't become the default, and track escalations so the governance system learns and improves. The result is a product operating model that's lightweight enough for a 5-person startup and rigorous enough for a safety-critical medical device — because the mode is a configuration choice, not a one-size-fits-all assumption.

## What You Get

| File | What it provides |
|------|-----------------|
| `SKILL.md` | Core methodology: governance boundary, two operating modes (lightweight and high-assurance), four configurable governance patterns, decision-rights framework, six review cadences, evidence standards, exception and escalation handling, routing table |
| `README.md` | This file — human-facing overview |
| `references/discovery-brief.md` | Bounded discovery brief distinguishing product governance from executive governance and delivery gates, with ownership boundaries and routing rules |
| `templates/operating-model.md` | Fillable template for configuring a complete product operating model (mode, pattern, cadences, decision rights, evidence standards) |
| `templates/decision-rights-map.md` | Fillable template for mapping who decides, who is consulted, who is informed, evidence required, and escalation path per decision type |
| `templates/review-cadence.md` | Fillable template for configuring each review cadence with purpose, participants, inputs, outputs, and decision authority |
| `templates/exception-record.md` | Fillable template for recording waived or deferred governance requirements with revisit conditions |
| `templates/escalation-record.md` | Fillable template for recording an escalation through the governance system with resolution and closure evidence |
| `evals/evals.json` | Six output-quality eval cases covering lightweight mode, high-assurance regulated mode, contested roadmap decision, exception request, evidence-missing escalation, and an adversarial case |

## Quick Start

To design a product operating model from scratch:

1. Choose the operating mode: lightweight (small team, non-regulated) or high-assurance (regulated, safety-critical).
2. Select a governance pattern: single accountable owner, product council, tiered review, or delegated authority with escalation.
3. Fill the decision-rights map for your six decision types.
4. Configure review cadences with purpose, participants, inputs, outputs, and authority.
5. Define minimum evidence standards per decision type, scaled to your mode.

Start with `SKILL.md` for the framework, then use the templates in `templates/` for each step.

## Triggers

Load this skill when your agent is asked to:

- Design or configure a product operating model or product governance system
- Map decision rights and accountable owners for a product or portfolio
- Set up recurring product review cadences (intake, portfolio, roadmap, experiment, launch, lifecycle)
- Establish evidence standards for product decisions
- Resolve a contested or deadlocked product decision through governance
- Record a governance exception or track an escalation
- Build cross-functional operating contracts (product, engineering, design, data, security, support, leadership)
- Distinguish product governance from executive governance or technical delivery gates

Do NOT load this skill for executive governance (capital allocation, org structure, strategic company bets), technical delivery gates (CI/CD, deployment checklists), or single one-off decisions without a recurring system.

## Requirements

- No external dependencies, API keys, or services required.
- Works with any agent framework supporting the Agent Skills format.
- Templates are plain markdown — use any text editor or documentation tool.
- For high-assurance mode in regulated environments, the evidence standards assume access to experiment results, risk analyses, and compliance reviews; the skill does not perform those analyses itself (route to `product-experimentation`, `secure-software-engineering`, or domain specialists).
