# Anti-Patterns

Failure modes recorded in the field (independent teams, 2019–2026) and in agent
workflows (first-party practice plus published practitioner accounts). Method adapted
from Ryan Singer's *Shape Up* ([basecamp.com/shapeup](https://basecamp.com/shapeup));
this file exists because the book reports only its author's successes.

Provenance labels: **[independent]** = a named team's own account; **[first-party]** =
our own operating record; **[practitioner]** = credible published account from tooling
vendors or individual engineers.

## Field-recorded failure modes

**Appetite becomes a target. [independent]** A budget stated as "a three-week project"
invites work that expands to fill it — gold-plating inside the box. State appetites as
maximums tied to worth, and treat "under budget" as success, not slack to spend.
(Source: scalex.dev, "2 years with Shape Up" — Customaite.)

**Small-batch stuffing. [independent]** Teams whose natural work is smaller than the
cycle end up planning two months ahead to fill the bucket — losing reprioritization
flexibility without gaining single-project focus. If your work runs small, shorten the
box instead of force-fitting. (Same source.)

**Cool-down decay. [independent]** The uncommitted buffer between boxes degrades into a
parking lot: urgent spillover eats it, meetings migrate into it "to protect the cycle,"
and small fixes wait up to six weeks for it, losing context by arrival. Protect what
cool-down is for, or shrink the interval. (Same source.)

**Shaping as a separate-caste requirement. [independent]** The method presumes dedicated
shapers working ahead of builders. When one team must do both, either shaping starves or
building stalls; splitting into protected/unprotected teams just relocates the pain
(on-call imbalance, domain-switch whiplash). Mitigations seen in the field: rotating
"distraction shield" duty (Athos Commerce's Bug Hero rotation), or accepting shorter,
less-pure boxes. **[independent]**

**Circuit breaker quietly softened. [independent]** "We refused to delete code at the
end of a cycle if a project was not in a state to be shipped yet, so the deadline lost
its potency." Others consciously de-scope instead of canceling (Athos Commerce) — a
legitimate *declared* adaptation. The failure is silent erosion: keeping the vocabulary
of hard boxes while never letting one break. If you won't let the breaker trip, say so
and manage scope some other way. (Sources: scalex.dev; athoscommerce.com.)

**Betting-table theater. [independent]** Consensus-building re-litigated live at the
betting meeting wastes the meeting and produces worse bets. Desmos fixed it with
"pre-betting": stakeholders review pitches well before the table so the meeting decides.
(Source: engineering.desmos.com.)

**Low-fidelity orthodoxy. [independent]** Fat-marker-only pitches blocked Desmos's
engineers and stressed their designers; they moved concrete design INTO shaping and it
worked — for a small team of very experienced designers. Level of abstraction is a
judgment call tuned to your team, not a rule to enforce against evidence. (Same source.)

**Process instead of direction. [independent]** The sharpest abandonment lesson:
Customaite adopted Shape Up to manufacture focus while the real problem was missing
product direction. Once direction existed (North Star metrics), the heavy process became
a hindrance and they returned to sprints. Diagnose before installing process; no
methodology substitutes for knowing what matters. (Source: scalex.dev.)

**Backlog regrowth under other names. [independent/inference]** Bets-not-backlogs works
when decentralized lists stay personal. In practice they accrete into shadow backlogs —
support tallies nobody lobbies from, engineer bug lists nobody revisits. And "important
ideas come back" fails silently when the idea has no channel to return through: a single
requester with no way to re-raise, or a support firehose drowning the recurrence signal.
Keep recurrence observable (lightweight per-source counts) or accept that you are
choosing to lose ideas on purpose.

## Agent-workflow failure modes

**Unbounded review-fix loops. [first-party]** An automated reviewer finds issues, fixes
spawn new issues, each remediation invalidates prior verification evidence, and rounds
accumulate. Our record includes a nine-round marathon on a merged-anyway PR — with two
regressions introduced by rapid-fire fixes under review pressure. The cure is structural:
bound rounds up front (see references/hybrid-adaptation.md), stop when severity stops
improving, and document residue instead of chasing zero.

**Verification treated as free. [first-party]** Every fix round costs review attention,
CI time, and context rebuild — non-linearly, because a push resets evidence state.
Budget verification inside the appetite or the appetite is fiction.

**Integration deferred to hour eleven. [practitioner]** Agent builders happily produce
disconnected parts that don't assemble. The one-piece-done discipline (walking skeleton
early) is more valuable with agents, not less — integration is where conceptual gaps
surface. (Cursor's scaling-agents write-up documents the coordination failure modes of
structure-free agent fleets: lock contention, duplicated work, risk-averse churn.)

**Structure extremes. [practitioner]** Too little orchestration and agent teams conflict
and drift; too much and the system goes fragile — Cursor found an integrator role created
more bottlenecks than it resolved, and that "many improvements came from removing
complexity rather than adding it." Match orchestration weight to observed failure, not
to org-chart aesthetics. (Source: cursor.com/blog/scaling-agents.)

**Findings-driven infinite improvement. [first-party]** Machine-generated findings feed
on responses: address one batch, the generator produces the next. That is the mechanism
working, not the work converging. Change the mechanism (fix the generator's scope, pin
its version, narrow its domain) or bound the loop — never assume round N+1 converges
because round N felt productive.

## Reading this file correctly

None of these patterns argue against the method. Publicly documented adaptations and a
documented two-year abandonment-with-learnings are signs of a framework people can reason
about and leave — rarer than it sounds. The pattern to avoid is adopting the vocabulary
while silently dropping the enforcement (softened breakers, target-appetites, shadow
backlogs). Adapt declared, or follow faithfully; the failures live in the gap between.
