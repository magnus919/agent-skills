# software-architecture

Make consequential system design choices explicit, testable, and easier to evolve.

## Why Install This Skill

Architecture decisions often fail because teams jump from a technology preference to a deployment shape without agreeing on drivers, quality scenarios, ownership, or failure behavior. This skill gives an agent a practical way to compare options and expose the costs of each choice.

It is useful for greenfield systems, target-state design, modular-monolith decisions, distributed workflows, cloud topology discussions, and architecture reviews. It keeps specialist work with the owners that already do it, so an architecture brief can coordinate API, data, backend, platform, security, capacity, diagramming, ADR, and migration follow-ups without absorbing them.

## What You Get

| Path | Provides |
|---|---|
| `SKILL.md` | Thin workflow index and ownership boundaries |
| `references/` | Seven focused decision guides plus public source index |
| `templates/` | Architecture design brief, tradeoff record, and review worksheet |
| `evals/evals.json` | Twelve output-quality cases covering design, distributed-data mechanism choices, and routing boundaries |

## Quick Start

Ask for a concrete architecture decision, for example:

```text
Compare a modular monolith and service decomposition for our checkout system, including data ownership, failure behavior, and an evidence plan.
```

Expected output: a decision brief with scenarios, alternatives, consequences, open evidence, and specialist handoffs.

## Triggers

- Greenfield or target-state software architecture
- Modular monolith versus service decomposition
- Architecture characteristics and tradeoffs
- Distributed workflow consistency and failure design
- Cloud application topology and deployment granularity
- Architecture fitness functions, drift, or evolutionary change
- Facilitated architecture reviews and decision records

## Requirements

No runtime dependencies or API keys. Use the repository's relevant specialist skills and public sources when evidence is needed.
