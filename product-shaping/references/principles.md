# Principles

The load-bearing ideas behind shaping. Everything else in this skill is an application
of these. Method adapted from Ryan Singer's *Shape Up* (Basecamp, 2019); the free web
edition lives at [basecamp.com/shapeup](https://basecamp.com/shapeup).

## Appetite is not an estimate

An estimate starts with a design and produces a number: "this will take five weeks."
An appetite starts with a number and produces a design: "this problem is worth two weeks
of one team — what solution fits inside that?"

The distinction matters because estimates masquerade as promises. Once a number exists,
everyone treats hitting it as the team's obligation, even though nobody controlled the
unknowns that inflate it. An appetite makes the time budget a *choice made up front*,
which flips the design question: instead of asking how long a full-featured version
takes, you ask which version of the solution is worth the budget. The best solution is
relative to constraints — there is no absolute "best" to estimate toward.

**Agent adaptation:** with delegated builders, the budget can be expressed in whatever
units your harness exposes — wall-clock days, work sessions, token or cost ceilings,
review-round allowances. What must survive translation is the direction of the
commitment: choose the budget first, shape the solution to fit it, and treat the budget
as fixed while scope stays variable.

## Fixed time, variable scope

Time is the one input you cannot flex without breaking trust; scope is the one input
you can always cut. Holding time fixed and letting scope vary forces every trade-off
into the open *while they are still cheap*. Letting scope stay fixed (the implied
promise of an estimate-driven plan) guarantees that quality or the deadline absorbs
every surprise at the worst possible moment.

This applies at each stage: the appetite constrains which solution gets shaped, and the
fixed box pushes the building team to decide what is core versus peripheral while there
is still time to act on the answer.

## Shaped work is rough, solved, and bounded

Work ready to bet on has three properties at once:

1. **Rough** — visibly unfinished, with open spaces where builders will exercise
   judgment. Detail added too early commits everyone to the wrong specifics and invites
   estimation errors: the more polished the artifact, the more hidden implementation
   complexity hides behind it.
2. **Solved** — the main elements exist at the macro level and connect. Open questions
   that could be resolved up front have been resolved; known rabbit holes are patched.
   Rough does not mean vague.
3. **Bounded** — it says where to stop. A stated appetite plus explicit no-gos tell the
   team what not to build.

Roughness without solved-ness is an unshaped idea. Solved-ness without boundedness is a
spec that will grow. Bets need all three.

## The right level of abstraction

Two failure modes bracket good shaping:

- **Too concrete** (wireframes, pixel mocks, detailed specs): over-specifies decisions
  that belong to the people doing the work, hides cost behind polish, and freezes scope
  so trade-offs become impossible.
- **Too abstract** (a phrase like "build a calendar view"): forces builders into
  mind-reading, leaves trade-offs undefined, and lets scope grow without boundary.

Shaped work sits between: concrete enough that anyone can see what the thing does,
abstract enough that the interesting decisions remain open for the team that owns them.

## Target the risk of not shipping

Shape Up optimizes for one specific risk: the risk of getting stuck — projects that
drag, pile up, and never ship. It deliberately does not address the risk of building
the wrong thing; discovery methods own that. Get clear-eyed about which risk a given
tool targets before reaching for it.

Risk reduction happens at three points:

| Stage | Mechanism |
|---|---|
| Before commitment | Shape: resolve visible unknowns and patch rabbit holes before anyone bets time |
| At commitment | Cap the downside: a fixed box means the most you can lose is the box |
| During the build | Integrate early: prove the concept end-to-end on one real slice instead of assembling disconnected parts at the end |

## Basic truths vs specific practices

Singer's appendix draws a line this skill preserves: some parts of the method are basic
truths (work needs shaping before commitment; commitments need capped downside; builds
need discovered structure), and some are practices tuned to Basecamp's scale in 2019
(six-week cycles, cool-downs, a formal betting table). Adopt the truths unconditionally;
treat the practices as defaults to adapt, not requirements to install. Solo operators
and small teams can run the whole loop fluidly by deliberately alternating the shaper
and builder hats — see references/betting.md and references/hybrid-adaptation.md.

## Evidence boundaries

Every practice claim in the source book is Basecamp-reported, from a company whose
product strategy and tooling business aligned with publishing the method. Independent
field evidence through 2026 is mixed-to-positive overall, with recurring failure modes:
shaping becoming a bottleneck when only senior people do it, circuit breakers quietly
turned into extensions, and backlogs regrowing under different names. Those findings,
with sources, live in references/anti-patterns.md — read it before betting anything
that matters. Treat this skill as a strong opinionated framework with documented failure
modes, not settled science.

## Lineage

The method's components have longer pedigrees than the book claims, which matters when
you borrow selectively:

- **Appetite/capped bets** echo flow economics: Don Reinertsen's *The Principles of
  Product Development Flow* (cost of delay, batch-size economics, treating development
  decisions as options with priced downside).
- **Get one piece done** is a walking skeleton (Alistair Cockburn) / tracer bullets
  (*The Pragmatic Programmer*): build the thinnest end-to-end slice first.
- **R&D mode spiking** descends from XP spikes.
- **Problem narrowing** (the calendar story) is demand-side interview craft — Bob Moesta
  and Chris Spiek are thanked in the book's acknowledgements; see references/shaping.md.
