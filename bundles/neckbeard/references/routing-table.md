# Routing Table — Compose, Don't Swallow

neckbeard owns the **cross-stage contracts**: the change contract, the evidence
ledger, the stop/escalation rules, and the evaluation protocol. It does **not**
own domain method. When a stage has a specialist skill, load it and follow it
instead of re-deriving its method here.

This table prevents the omnibus bundle from swallowing the specialist catalog.
Rule of thumb: if a row's specialist skill is installed and the task matches its
trigger, **the specialist leads the stage**; neckbeard supplies the contract and
ledger around it.

## Stage routing

| If the current work is… | Load this catalog skill | neckbeard still provides |
|---|---|---|
| Stakeholder discovery, requirements, acceptance criteria, edge cases | `product-discovery` | Change contract, ledger |
| Turning approved scope into user-facing behavior, interaction, or information architecture | `product-design-and-ux` | Contract, ledger |
| A formal specification with phase gates | `spec-driven-development` | Contract, ledger, stop rules |
| Reverse-engineering / understanding an existing codebase | `software-architecture-analysis` | Ledger, assumptions list |
| Designing or evolving an API / interface contract | `api-design-and-evolution` | Contract, ledger, boundary verification |
| Root-cause debugging of a bug or failure | `systematic-debugging` | Contract, ledger, boundary verification |
| Security review, threat modeling, or secure design/implementation | `secure-software-engineering` | Contract, ledger, trust-boundary checks |
| Accessibility (WCAG, keyboard/focus contracts, error recovery) | `web-accessibility` | Ledger, non-negotiable confirmation |
| Test strategy, regression testing, or CI quality gates | `qa-methodology` | Ledger, boundary verification |
| Writing or reviewing docs, README, API reference | `technical-documentation` | Ledger |
| Producing a pass/conditional/blocked verdict with evidence | `verification-methodology` | Ledger boundary rules |
| Reliability objectives, incident response, operational recovery, or delivery | `site-reliability-engineering` | Contract, ledger, rollback evidence |
| Architecture decision records | `adr-authoring` | Decision-record template, ledger |
| Code review, refactoring, or implementation quality assessment against classic engineering principles | `programming-principles` | Contract, ledger, boundary verification |

Two further specialists compose well but are narrower: `product-methodology`
(prioritization, backlog, documented decisions) for the requirements stage, and
`c4-diagramming` for communicating architecture in the design stage. Load them
when their trigger matches; neckbeard still supplies the contract and ledger.

## "Use the existing skill instead" conditions

Route entirely to a specialist — do **not** run the neckbeard spine — when:

- The task is a pure documentation job with no delivery-boundary risk →
  `technical-documentation`.
- The task is a self-contained debugging request and the user only wants the root
  cause and fix → `systematic-debugging` (neckbeard's ledger is still worth
  appending if the fix is non-trivial).
- The task is a formal spec authoring exercise → `spec-driven-development`.

## When no specialist is installed

neckbeard's [stages.md](stages.md) gives a minimal fallback method per stage.
Use it, but record in the ledger that the specialist skill was absent, so a
reviewer knows the method was the fallback rather than the full specialist.

## What neckbeard never does

- It does not re-implement a specialist's internal method.
- It does not override a repository's own contribution rules, review process, or
  human accountability.
- It does not automate privileged, destructive, deployment, or merge actions
  beyond the host agent's existing authority and confirmation controls.
- It does not treat a benchmark win as proof of production effectiveness.
