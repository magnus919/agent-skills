# Bounded loops, graphs, and coordination

## Select the smallest control shape

| Shape | Appropriate trigger | Required control |
|---|---|---|
| One bounded execution | A clear task with a decision surface | Acceptance, budget, stop/escalation |
| Goal loop | Repeated attempts can improve one outcome | No-progress and retry limits; meaningful verifier |
| Scheduled task | Work should recur at a known cadence | Scheduling authorization, run deduplication, overlap policy |
| Event-triggered work | Eligible external events create tasks | Event identity/cursor, replay/deduplication, authority |
| Explicit graph | Branching, dependencies or safe parallelism need coordination | Typed shared state, routing, ownership, durable checkpoints |

A loop is already a graph in a mathematical sense. Drawing a graph does not
create independent judgment or fix a bad goal. Use explicit nodes only when they
make coordination/recovery easier than the simpler alternative.

## Goal and acceptance integrity

Record the business outcome, eligibility, exclusions, authority, and checker
criteria before execution. The maker can suggest changes but cannot weaken the
criteria, expand scope, or authorize itself to pass. A human/business anchor
reviews whether the goal remains worthwhile and whether a metric is being gamed.
Multiple loops need an owner for conflicting goals and scarce shared resources.

## Typed routing

| Outcome | Route | State/evidence |
|---|---|---|
| Acceptance observed | Integrate within authority or finish | Bind actual evidence to candidate |
| Meaningful check fails | Bounded repair | Keep failed check and hypothesis |
| Evidence missing/unknown | Research or escalate | Never take the pass path |
| Denied action | Report authority boundary | Do not evade through another tool |
| Dependency unavailable | Bounded retry/backoff or defer | Record prerequisite and retry safety |
| Timeout/partial effect | Reconcile before repeat | Operation ID and unknown-effect state |
| Attempts/time/cost exhausted | Stop/escalate | Last durable state and next action |
| No measurable progress | Stop/reframe with owner | Do not redefine progress to continue |
| Cancelled | Drain owned work and hand off | Preserve acknowledged/partial effects |

Limits belong to the task coordinator and action executor, not just the prompt.
Increment counters on every attempted action/check cycle, including failures.
An unattended goal must have a no-progress bound and a total budget, even if
individual commands have timeouts. Infinite autoresearch-style loops are not a
safe default for a user task.

## Maker/checker separation

Supply the checker acceptance, candidate artifact, environment, and evidence
sources. Avoid the maker's persuasive narrative and mutable private criteria.
A fresh context or different model reduces shared bias but does not guarantee
correctness. Calibrate semantic graders with the eval specialist; use real
checks for observable behavior. Mixed subjective/functional tasks need separate
criteria and a human owner for taste/authority, rather than one averaged score.

## Shared state and graph design

Define node input/output, owner, tool authority, resources, checkpoint point,
error taxonomy, and terminal outcome. Define shared-state merge behavior, not
just a common dictionary. Parallel appends may commute; edits to a contract or
migration usually need serialization. Route recovery at the earliest responsible
boundary instead of replaying the whole graph.

For each handoff record task/run/candidate identity, accepted contract, resource
lease, evidence references, and pending effects. Durable state enables recovery;
an in-memory checkpointer only enables recovery while that process lives.
The bundled graph validator screens declarations for referenced nodes, verifier
pass/fail/unknown routes, reachability, terminal paths, bounded limits, and a
non-memory checkpoint declaration. It does not prove the store persists or the
executor obeys its declared limits.

## Parallel work and integration

Assign disjoint ownership or serialize the overlap; use isolated checkouts where
needed. Worktrees prevent checkout clobbering, not shared-database or API conflict.
Freeze/version interfaces and nominate an integration owner. That owner checks
combined behavior and invalidates evidence affected by integration changes.
Expired workers need fencing so late outputs cannot silently win.

Include review, comprehension, reconciliation, and rework time in comparisons.
Extra workers can make generation faster while making the actual delivery slower.
If a graph adds more cost than it removes, simplify it. Business anchors and
human authority remain necessary regardless of graph shape.

## Exercise every exit

Use the loop and graph templates to walk success, failing check, unknown evidence,
denied action, exhausted budget, lost worker, duplicate event, partial effect,
and resume. Do not ship a design that only walks the happy path. Follow the host's
actual delegation/scheduling authorization; this reference grants neither.
