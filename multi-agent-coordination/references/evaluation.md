# Evaluate the team, its boundaries and its cost

Preregister the decision, failure hypothesis, task population, baseline, candidate,
acceptance, hard invariants, budgets, improvement threshold and stopping rule.
Use the experiment template; leave unknown measurements unknown.

## Compare fairly

Hold task/input revisions, tool access, environment, acceptance, provider/model
settings and total available compute comparable. If model mix changes, report it
as part of the intervention rather than attributing everything to topology.
Include a single strong agent and a simpler sequential workflow where applicable.
Measure both quality under fixed budget and full cost at comparable quality.
Preserve unsuccessful, canceled, denied and timed-out attempts. Repeated runs and
held-out cases are needed when claiming general improvement; one worked example
is an integration exercise.

## Observe more than task status

| Dimension | Measure | Limitation |
|---|---|---|
| Delivery | Accepted integrated outcomes / attempted jobs | Needs independent acceptance and stable task mix |
| Flow | End-to-end lead time, queue age, WIP at constrained stage | Faster generation can hide slower integration |
| Cost | Tokens, tool spend, retries, review/human time per accepted outcome | Missing usage is not zero |
| Coordination | Messages, handoffs, approval wait, repeated context fetches | Volume is a diagnostic signal, not work value |
| Conduct | Scope/authority violations and external effects | A correct answer cannot offset a hard invariant breach |
| Resilience | Recovered / injected failure cases; unresolved effects | Plans and static snapshots do not establish recovery |
| Learning | Recurrence under observed exposure; invalidated consumers adopting correction | Incomplete lineage cannot prove eradication |

To test ceremony, compare equivalent observation windows and task mix. Investigate
rising coordination cost alongside flat accepted milestones; also inspect risk,
review completeness and defects. Do not optimize the ratio by deleting necessary
checks, inflating milestones or dividing one job into many accepted subtasks.
Thresholds need local baseline/error analysis and an owner, not a vendor default.

## Challenge roster

Exercise duplicate delivery, worker/coordinator loss, stale intent, late output,
expired authority, cancellation of descendants, contradictory peer advice, missing
source access, memory supersession and actual integration conflicts. Include a
valid near miss for each detector: necessary high assurance, harmless exposed-but-
unused notes, legitimate changed requirements, and a task better solved sequentially.
Use synthetic benign payloads for security tests. Never collect secrets as proof.

[MultiAgentBench](https://aclanthology.org/2025.acl-long.421/) includes intermediate
milestone measures alongside task outcomes and compares several coordination
shapes. This motivates process-aware evaluation, not the assumption that its best
shape transfers to coding or a live business workflow. The cited scaling study
also provides counterevidence to agent-count heuristics.

Use agent-evals-and-observability for dataset/grader/statistical design. Keep
script execution, assertion completeness, semantic review and release authority
separate. The portable eval manifest supplies representative cases; its existence
and schema validity do not establish runtime or release evidence.

## Source-traced qualification

Challenge the commit-before-dispatch window, replacement after an awaited observation, alternate mutation paths, and partial health coverage. Retain negative controls. Distinguish tests read from tests executed. See [the pinned source audit](openrig-source-audit.md) and [effect/recovery matrix](../templates/effect-recovery-matrix.md).
