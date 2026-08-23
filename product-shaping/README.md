# product-shaping

Set appetites instead of estimates, shape raw ideas into bounded pitches, and bet on
them with capped downside — Basecamp's Shape Up method, adapted for teams whose builders
include AI agents.

## Why Install This Skill

Most failed work doesn't fail during the build. It fails before it starts: an idea
enters the pipeline with no one having decided what it's worth, gets built to whatever
size the first design implies, and drags past every deadline because nothing defined
where it stops. Teams respond with estimation rituals that produce numbers nobody
believes, or backlogs that grow until nobody reads them.

This skill installs the alternative: a pre-commitment discipline that converts raw
ideas into bounded pitches (problem, appetite, solution, rabbit holes, no-gos), bets a
fixed time budget on them, and governs the build with discovered scopes and deliberate
scope cutting. It is adapted from Ryan Singer's *Shape Up* (Basecamp, 2019) and extends
the method for a reality the book never faced: build teams that include AI agents —
where budgets are measured in sessions and cost ceilings, review time is a first-class
scope cost, and non-converging fix loops need explicit kill criteria.

After installing, an agent can take "customers want a calendar" and return a bounded
pitch for the tenth of a calendar worth building; take a "redesign X" grab-bag and
either re-anchor it on a specific problem or route it to proper discovery; run a build
that integrates one real slice early instead of assembling disconnected parts at hour
eleven; and stop a review/fix spiral at round three instead of round nine.

## What You Get

| Directory | What it provides |
|-----------|-----------------|
| [`SKILL.md`](SKILL.md) | Core loop and entry-point routing: shape → bet → build → move on |
| [`references/principles.md`](references/principles.md) | Appetite vs estimates, fixed-time-variable-scope, the rough/solved/bounded test, evidence boundaries, method lineage |
| [`references/shaping.md`](references/shaping.md) | The four shaping steps in detail, including breadboarding and shaping non-UI work (APIs, infrastructure, agent workflows) |
| [`references/betting.md`](references/betting.md) | Bets vs backlogs, circuit-breaker mechanics, cycle length as a tunable parameter, defect handling between bets |
| [`references/building.md`](references/building.md) | Hand-over-responsibility, one-piece-done integration, scope mapping, uphill/downhill progress tracking, deciding when to stop |
| [`references/hybrid-adaptation.md`](references/hybrid-adaptation.md) | The agent-team extension: budget currencies, batched steering, verification cost inside scope, kill criteria for non-converging loops, earned autonomy |
| [`references/anti-patterns.md`](references/anti-patterns.md) | Documented field failures (2019–2026 independent team records) and agent-workflow failure modes, with mitigations |
| [`templates/PITCH.md`](templates/PITCH.md) | Fillable five-ingredient pitch document |
| [`templates/SCOPE_MAP.md`](templates/SCOPE_MAP.md) | Fillable scope table with hill states and circuit-breaker check |
| [`evals/evals.json`](evals/evals.json) | Output-quality evaluation cases |

## Triggers

Load this skill when:

- A raw idea, feature request, or "redesign/improve X" request needs to become a
  bounded project before work starts
- Someone asks "how much should we invest in this?" or "what's the smallest version
  worth doing?"
- Planning a delegated AI-agent build: budgets, verification cost, steering cadence,
  or kill criteria for loops that won't converge
- A project keeps not finishing and the honest question is whether it was ever shaped
- An epic resists decomposition because nobody can define done
- Post-ship feedback is threatening to become an instant commitment

## Requirements

No software dependencies or credentials. Reference-only skill: it shapes thinking and
documents, not systems.

## Quick Start

No setup needed. Trigger examples:

- Say "help me shape this idea before we commit time to it" or "set an appetite for
  this work" — start at `references/shaping.md`
- Say "write a pitch for this" — fill in `templates/PITCH.md`
- Say "we're delegating this build to an agent, scope it" — load
  `references/hybrid-adaptation.md` for budgets and kill criteria
- Say "this project won't stop running long / this loop won't converge" — load
  `references/anti-patterns.md` first, then hybrid-adaptation kill criteria

Pairs naturally with `product-discovery` (upstream problem validation),
`product-methodology` (downstream prioritization of a won bet), and delegation/kanban
skills when builders are agents.

## Attribution

Method adapted from *Shape Up* by Ryan Singer (Basecamp, 2019), available free at
[basecamp.com/shapeup](https://basecamp.com/shapeup). This skill is an original
distillation with independent field evidence and an original hybrid human+AI adaptation
layer, not a reproduction of the book.
