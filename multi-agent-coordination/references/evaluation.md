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

## Test what communication contributes

| Task | Comparisons | Interpretation |
| --- | --- | --- |
| Each worker holds a required piece of information | Compare the candidate with a simple authorized collector or fixed handoff under the same access policy. A run without sharing can test the information dependency. A full-input solo run can help diagnose synthesis if that access is in scope. | A no-sharing run that lacks required facts establishes an information dependency. Use the collector comparison to assess whether the candidate protocol adds value. |
| A worker can solve the whole task | Compare a strong single agent at the aggregate allowance, independent best-of-N with an available selector, and N communicating agents. Add a fixed partition where disjoint assignments are viable. To test the contribution of a channel, disable it in the same harness and control other paths for sharing. | The independent arm measures the value of additional attempts. The channel control measures dependence on sharing within that harness. A separately trained solo policy and a same-policy channel control answer different questions. |

Use the same held-out roster, eligible search scope, model revision, tool access and
acceptance rule. Keep state isolated between independent attempts and verify the relevant
isolation boundary with a benign fixture. Keep reference answers outside the selector's
reach. A verifier may select the result when it is available and authorized in the evaluated
workflow. Report retrospective selection using hidden answers as an upper bound.
Charge selection and integration to their arms. Record both the allowed resources and
actual use, including received context, rereads, tool calls and retries. Keep training
interventions and costs distinct from the inference comparison.

Follow a required fact from its source through delivery, use and correct synthesis.
Deduplicate repeated deliveries by stable source or assignment identity while preserving
equal facts from different sources. For exploration, look for a verified finding that
redirects a worker or prevents a repeated search. Distinguish avoidable overlap from shared
prerequisites and deliberate corroboration. Count each task once, and report conduct
violations independently of correctness. Establish evidence at any wider team size or lower
per-worker allowance before applying the verdict there.

[s³](https://arxiv.org/html/2611.08615v1) and [Scaling Discovery through Test-Time Communication](https://arxiv.org/html/2609.21032v1)
motivate these comparisons. Their results vary with the task, baseline and budget.

### Worked comparison: finding an answer in product documentation

Use one held-out roster where every arm can search the same documentation. Give
each arm the same total budget and deadline. Compare one agent using the full
allowance, four isolated attempts with an in-budget selector, and four workers
who can exchange evidence. Reserve budget for the communicating arm's synthesis.
Run the same team with messages and shared notes disabled if the question is
whether that channel contributes. Give all final answers to the same blinded
reviewer with one citation and correctness rubric. Count one outcome per task
and charge failed attempts, selection and synthesis to their arms.

If the team exceeds solo but ties independent attempts, the result supports
additional attempts. If the team also exceeds independent attempts and loses
the gain with sharing disabled, inspect which verified findings were reused and
whether the improvement clears the declared threshold at actual cost. Use a
separate fixture with one necessary fact held by each worker to check handoff
reliability. Compare peer sharing with a fixed authorized collector on that fixture.

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

## Test factory economics, not production volume

When a factory requests more capacity, compare a bounded cohort of real product
work against a simpler baseline, including a way to finish work already started.
Count accepted integrated outcomes and retain time, spend, failed attempts, rework,
and review/support effort. Report human effort in hours unless a declared rate
converts it to dollars. Do not treat idle seats, larger token budgets, or more
patches as better outcomes. Report zero accepted outcomes explicitly; its unit
cost is undefined, not zero. If a change to handoff context or model routing is
claimed to save tokens, rerun comparable tasks and check repeated reads, total
cost, accepted quality and authority violations before rollout.

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
