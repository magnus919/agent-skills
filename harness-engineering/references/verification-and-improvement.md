# Verification and measured improvement

Distinguish four evidence levels: structure exists; commands executed; behavior
observed at the requested surface; comparable agent task outcomes. A file audit
cannot establish the last three. A provider judge supplies reviewer triage unless
its decision contract and independent validation support more.

Define acceptance before generation and choose the cheapest checks that decide
it: static/contracts for local invariants, integration for component boundaries,
and an end-to-end user journey when that is the requested outcome. Do not force
full browser testing for a documentation edit. Run failure/recovery probes for
stateful or side-effecting changes.

A check must observe its claim. `echo`, a test-name substring, unit-test presence,
zero tests collected, and exit zero from a stub are not behavioral evidence. Use
checks that fail on a plausible near miss and distinguish missing evidence. Keep
acceptance and evaluator inputs outside the maker's unrestricted edit authority
when their integrity matters.

Attach evidence to task, source revision, environment, command, result, and time.
Completion requires the whole relevant contract, not an aggregate score that hides
an authority breach or missing boundary. The bundled runner records command exits
only; it cannot establish test collection or correctness of the commands selected.

## Experiment protocol

State a failure hypothesis. Freeze a representative task set, model/config,
authority, environment, and budgets; compare existing harness with the candidate.
Randomize/counterbalance order and repeat stochastic cases where useful. Retain
raw task outcomes and judge disagreements, including failures and abstentions.
Separate development cases from held-out tasks for generalization claims.

Measure verified acceptance, human interventions, restart/recovery, unauthorized
action attempts, latency, and cost per accepted task. An easy-case speedup does
not outweigh a consequential regression. Record sample size and limits; synthetic
fixtures exercise contracts, not field effectiveness.

Ablate one component at a time if diagnosing marginal contribution. A zero delta
can mean redundancy, poor design, or an unexercised path. Trace attribution is
needed to choose the repair. Roll back a failing experiment rather than weakening
acceptance. Use the catalog evaluation specialist for statistical or grader design.

Periodically remove stale instructions, contradictory sources, unused context,
and duplicated state after checking which behavior depends on them. Preserve
rollback evidence. Harness maintenance should reduce burden as well as add control.

## Optional bounded propose → probe → compose

Use this recipe when recorded failures justify searching among small executable
scaffolding changes with a frozen model. It is optional, not a requirement to run
an optimizer or spend model budget for every harness edit.

1. **Bound and preserve.** Set candidate, iteration, rollout, retry, time and total
   cost caps before starting. Pin an untouched baseline and the comparable-run
   contract below. Keep evaluator definitions, held-out answers, authority and
   safety controls outside candidate edit access. Use an isolated workspace;
   candidate code and retrieved trajectories are untrusted inputs.
2. **Propose.** Give each minimal patch a stable candidate ID, parent revision(s),
   scope, hypothesis and disconfirming outcome. Preserve rejected candidates and
   reasons. Include successful controls as well as motivating failures; do not
   tune only on failures or expose held-out cases to the editor.
3. **Probe.** Execute candidates and the untouched baseline on matched inputs,
   models, environment, tools, authority and budgets. Retain actual trajectories,
   per-case results, failures, abstentions and checker disagreements. A plausible
   proposal or optimizer/model preference is not correctness evidence. Stop at
   the declared caps; degraded or inconclusive candidates are not eligible for
   promotion.
4. **Compose selectively.** Combine only evidence-supported changes with compatible
   scope. Record constituent IDs and exact patch/revision as a new candidate.
   Retest the composition against the untouched baseline under the same contract,
   including held-out regressions and required repeats: individually useful
   changes can interact badly. Do not inherit a pass from constituent scores.
5. **Decide and account.** Record adopt/reject/defer, uncertainty and rollback
   evidence. Review and promotion still follow [lesson-to-PR](lesson-to-pr.md)
   and the [lesson validation packet](../../agent-evals-and-observability/references/lesson-validation.md).
   No live self-modification or automatic promotion is authorized by this loop.

Report **optimization cost** separately from **recurring serving cost**. Count all
proposal/editor calls, baseline and candidate probes, compositions, reflection,
retries, evaluation and failed attempts, including tokens, requests, compute and
elapsed time. Report serving cost per accepted task at comparable quality. For a
positive measured saving, estimate break-even volume as total incremental
optimization cost divided by baseline-minus-candidate serving cost per accepted
task, in consistent units. State assumed volume, uncertainty and the quality
constraint; nonpositive savings have no finite break-even. A lower serving bill
alone does not establish net savings or justify a quality/authority regression.

This procedure is informed by [Harness²](https://arxiv.org/html/2610.14224v1)
and its [experiment guide](https://github.com/google-research/harness2/blob/main/docs/EXPERIMENTS.md).
The research explores executable scaffolding optimization with frozen models;
its web benchmark is not evidence of crawl quality. The release's
[web-access warning](https://github.com/google-research/harness2/blob/main/docs/EXPERIMENTS.md#web-access)
reports rubric retrieval and unrestricted network access with the Codex sandbox
disabled. Do not copy those settings. Isolation, protected evaluators, restricted
egress and independent acceptance here are production safeguards, not claims
that the paper demonstrated them.

The [bounded-search assertion challenges](../evals/bounded-search-rubric-challenges.md)
cover the added declarative cases; they are not executed behavioral results.

## Acceptance oracle selection

| Property | Faithful evidence | Plausible false pass |
|---|---|---|
| Endpoint returns bounded page | Execute with enough records to expose the next page | Mocked response or one-record fixture |
| UI action saves state | Real interaction plus persisted state after restart | Button exists in screenshot |
| Tool denial is enforced | Execute prohibited operation in isolated challenge; verify no effect | Prompt includes a denial rule |
| Session recovery is safe | Interrupt after effect/before checkpoint and reconcile | Handoff template populated |
| Architecture boundary holds | Relevant dependency/type/behavior checks | Import-name substring grep only |
| Context retained authority | Probe original constraints after compaction/reset | Summary sounds coherent |

An oracle should fail a known violating near miss. If it only observes part of
the claim, narrow the claim or add the missing evidence. A model judge cannot
infer an external side effect from a statement that it occurred.

## Comparable-run contract

Fix the initial task/workspace input, accepted criteria, provider/model settings,
tool authority, runtime/dependency/service conditions, and budgets. Change the
harness intervention explicitly. Do not accidentally give the candidate a solved
application, more information about hidden tests, or a larger budget and then
attribute all gains to instructions. The upstream starter/solution exercises need
careful reconstruction of equal initial product state for a causal experiment.

The run-record helper fingerprints model_config, environment, taskset, authority,
and verifier; harness_revision is the intended varying field. Fingerprint
normalized actual inputs consistently. The model_config excludes the intentional
harness instructions but includes provider/model/sampling/version settings. Task
inputs include the initial product state; environment includes dependency/runtime
and service identities. If another factor intentionally changes, use a broader
experimental design rather than bypassing the comparison's refusal.

Use stable case IDs and separate repeated attempts by a stable replicate suffix.
Record failed and unknown cases, not just accepted ones. Keep negative cases that
exercise authority, partial effects, denied access, and evidence contamination.
Held-out cases should not guide iterative wording/implementation changes.

## A minimal decision example

Three illustrative paired records (not measured results of this skill):

| Task | Baseline | Candidate | Decision implication |
|---|---|---|---|
| Add pagination | Rejected | Accepted | Useful observed gain on this case |
| Resume import after crash | Accepted | Unknown | Consequential recovery regression blocks adoption |
| Document local setup | Accepted, slow | Accepted, faster | Speed gain does not compensate for unsafe recovery |

Do not average these into a readiness score. Report changed outcomes, references,
confounders, and the responsible adoption decision. A small local sample supports
only its observed tasks; statistical/field claims require additional evidence.

## Evolve and retire controls

When models, tools, policy, or tasks change, recheck old harness assumptions. Pick
one stale/costly rule, state why removing or replacing it could help, and identify
a challenge task that should fail if the rule was necessary. Compare with it on/off,
retain rollback, and inspect adverse outcomes. Control count is not a quality
measure. Keep model selection as an alternative hypothesis when harness probes
cannot explain the failure; do not assume every model failure is a harness defect.
