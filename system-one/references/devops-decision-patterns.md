# Bounded decisions in DevOps workflows

Read this for semantic telemetry routing, incident investigation, optional CI
selection, deployment branching, or durable decision loops. These are proposed
provider-neutral applications of typed judgments, not evidence that every
System One model is suitable. Qualify each adapter and evaluate its workload.

## Ownership and operating boundary

```text
trusted observed state + eligible candidates + maintained question
-> validated typed judgment -> deterministic policy
-> authorized executor -> fresh observations + executable checks
```

System One owns question semantics, candidate coverage, uncertainty, adapter
validation, and failure lanes. Incident command, SLOs, recovery criteria, and
closure belong to `site-reliability-engineering`; root-cause methodology to
`systematic-debugging`; named cluster commands to `kubernetes`. CI dependency
and rollout mechanics belong to `qa-methodology` and `release-engineering`.
`agent-evals-and-observability` owns end-to-end task, trajectory, side-effect,
and cost evidence. These are repository skill names, not prerequisites for
loading every skill at once.

Reuse the authorization and action contract in `references/use-case-patterns.md`
and `templates/action-control-contract.md`; the judgment cannot create a
permission or widen an action's scope. Before any external mutation, confirm
the target, scope, and rollback path. Read-only discovery may proceed without
confirmation. Existing explicit authorization can satisfy that boundary.

## 1. Preserve telemetry; route an analysis branch

Use semantic judgment when exact severity or routing rules leave costly
ambiguous events. Start with annotations and shadow decisions. Keep the
original archive independent of the semantic filter; route only a separate
expensive-analysis branch. Preserve required audit/security events by exact
policy. Missing judgments, timeout, input truncation, queue saturation,
unsupported state, and uncertainty go to the conservative analysis lane.

A fan-out topology is not durable delivery. Verify exporter acknowledgments,
partial-success behavior, buffering, retry/deduplication, and destination
persistence. Redacting the model-bound copy does not redact stored originals.
If classification blocks export, test that provider outage cannot block the
archive. Make missing scores visibly unscored, not low priority.

Report both anomaly misses and analysis calls avoided. Compare severity rules,
current behavior, annotation-only, and the full filter. Count classification,
retries, storage, downstream analysis, review, and delayed incident detection;
high recall with almost no filtering may add cost. Metric metadata alone
cannot establish that a series is unused by a dashboard, alert, or SLO.
Trace operation relevance cannot prove that dropping a span preserves a whole
trace: buffering, late spans, eviction, and trace-ID routing are separate issues.

## 2. Rank diagnostic tests, not unbounded actions

Have the investigating agent propose competing hypotheses, each with a bounded
read-only test, predicted distinguishing observation, and evidence that would
falsify the hypothesis. Exclude unauthorized, secret-exposing, disruptive, or
unbounded probes deterministically. Supply fresh relevant state and ask which
eligible test best distinguishes the hypotheses; rank diagnostic value and
cost separately when useful. The executor runs and interprets the selected
test, records observations, and refreshes the candidate set before the next
judgment. A failed probe is not evidence against the hypothesis unless the
failure itself is diagnostic.

Include an insufficient-evidence/expand-hypotheses lane. A ranker cannot select
a correct explanation absent from its candidates. Measure hypothesis/shortlist
coverage before attributing failure to ranking; bound test count, elapsed time,
context, cost, and no-progress retries. On rejection, gather new evidence or
change the hypotheses rather than paraphrasing a rejected claim until accepted.

## 3. Separate diagnosis, action review, and recovery

Use independently visible requirements, not one broad "is this resolved?":

| Stage | Required evidence | Deterministic boundary |
|---|---|---|
| Diagnosis | Current user-visible failure and supported causal mechanism; alternatives discriminated | Missing observations remain unknown; no repair permission |
| Proposed action | Cause addressed, proportional scope, reversibility, threatened invariants | Exact authorization, target, impact ceiling, approval, rollback |
| Recovery | Executed change, restored user journey, governing invariant, declared stability window | Executable checks and operator closure criteria |

For a rollout failure, Ready replicas now are insufficient: verify the next
rollout preserves the required availability constraint. For credential rotation,
verify new credentials work and old credentials remain invalid; do not accept
restoring the old secret merely because traffic recovers. Keep unknown checks
explicit. A model's assessment of logs cannot substitute for actually executing
postcondition checks. Distinguish current functionality from cause removal and
future durability. Define checks before proposing the repair.

## 4. Select optional CI jobs with dependency closure

Apply exact path rules, required jobs, security checks, and prerequisites first.
Ask semantic relevance questions only for optional jobs on an explicit allowlist;
multiple independent jobs may be relevant, so one exclusive Choice need not fit.
Resolve dependency closure in code and retain required jobs regardless of scores.
Invalid, missing, stale, or unsupported judgments run the conservative full
eligible set. Report omitted-job coverage, missed regressions, wall time, runner
cost, and model overhead against current CI and exact rules. Skipping a job
successfully is not proof it was unnecessary. Replay or shadow omissions against
the full suite before enforcement, retaining representative held-out changes.

## 5. Branch within a deployment state machine

Code determines eligible transitions from observed rollout state, change
freezes, health checks, budgets, and authority. The model may choose only among
those options. Hold, review, and abort must remain reachable; promotion is not a
reward for merely returning a valid answer. Version rollout state and expire
judgments before consequential transitions. Measure the rollout outcome and
user boundary; a captured trace is not a live deployment experiment.

## 6. Persist decisions separately from execution attempts

Fill `templates/decision-execution-record.md`. Bind a validated judgment to its
workflow/event ID, exact target, observation time/version, candidate set, question,
model/adapter/calibration revisions, and policy. Record the permitted command
and authorization separately from the model output. Persist only privacy-safe
references or integrity hashes where raw state would expose secrets.

An execution retry can reuse a decision only while it remains the same
currently authorized operation with valid preconditions. After response loss,
reconcile the operation's effect by ID before retrying. Use idempotent activities
or an explicit deduplication mechanism; durable workflow history alone does not
make external effects exactly once. Reobserve and redecide after state change,
evidence expiry, revised policy, or changed action parameters. Recheck after a
human approval wait; the world may have changed while waiting.

Handle provider retries separately: a judgment request can itself be duplicated
or produce a new answer after an ambiguous failure. Preserve attempts and the
selected final decision identity. Separate kill switches for model calls,
autonomous writes, and individual actions. Bound pending approvals and retries;
unknown completion means reconcile or hand off, never assume failure and repeat.

## Evidence ledger: inspected sources, not deployment endorsements

Reviewed 27 September 2026. The discovery article is Josh Rosen's
[JevOps](https://x.com/JoshARosen/status/2104201747732271519); it collects projects,
not a controlled comparison. The design rules above are our synthesis.

| Primary source | Observed evidence | Limit |
|---|---|---|
| [Jev Logs README at 217d2b7](https://github.com/reachjalil/jevlogs/blob/217d2b70bfb327a0038b21851c1c9c143eb80469/README.md) | Original archive plus separately filtered analysis branch; uncertainty stays eligible | Export acknowledgment does not establish durable storage; classifier still incurs work |
| [Log benchmark card](https://huggingface.co/datasets/reachjalil/jevlogs-log-triage-benchmark) | Author reports 99.33%/100% HDFS/BGL anomaly recall while skipping only 0.84%/0.12% of analysis; assumed HDFS cost rises 2.55% | BGL alerts were severity-protected; block labels propagated to lines and anomalies oversampled; estimated costs, not invoices or reproduced production results |
| [Jev Metrics at d8d9c32](https://github.com/ishantanu/jevmetrics/blob/d8d9c325242d6b2ce38f715a0d536f68185b761d/README.md) | Annotation-first and separate archive routing examples | Metadata judgments do not inspect historical dependencies; fresh cached drops can persist during outage |
| [Jev Traces at 79fb688](https://github.com/ishantanu/jevtraces/blob/79fb6886ca29be5f978e229701ab74956c3dcf27/README.md) | Span annotation plus separate opt-in tail-sampling experiment | Synthetic/mock experiment; sampling/delivery failures remain |
| [SREGym-Lite report](https://sregym.com/blog/jev-sregym-lite) | Ten incidents, five attempts per condition: 20/50 baseline versus 24/50 assisted; test ranking and submission review | Two incidents regress; diagnosis speed unmeasured. Missing hypotheses and accepted non-durable repairs remain. Continuous action guidance and prospective safety review are proposed, not tested |
| [dsh-jev README](https://github.com/buberlo/dsh-jev) | Harness separates typed assessment from policy; permissions cannot widen | Kubernetes comparison is recorded replay without live replanning and includes a false positive; source behavior is not general safety validation |
| [Temporal workflow at bec51c2](https://github.com/thenoahhein/jev-temporal-demo/blob/bec51c28217f329a011cf39d8162725136b23561/src/workflows/incident-response.ts) and [tests](https://github.com/thenoahhein/jev-temporal-demo/blob/bec51c28217f329a011cf39d8162725136b23561/src/workflows/incident-response.test.ts) | Separates workflow decision, policy, execution, and metric refresh; simulated rollback retry without another decision | Timeout test is pre-effect; no proof of response-loss reconciliation or worker-restart safety. No explicit evidence TTL or fresh check after approval |
| [Deployment state-machine demo](https://stacktoheap.com/demos/jev-deployment-state-machine/) | Enabled choices, policy result, and transition shown | Captured synthetic replay, not live inference or deployment evidence |

Complete a pattern design when the contract, failure lanes, verification checks,
ownership, and bounded evaluation plan exist. Do not declare an integration
successful until authorized execution, independent outcomes, fallback behavior,
readiness, and rollback are verified. Insufficient evidence supports shadow or
revision, not automatic operational adoption.
