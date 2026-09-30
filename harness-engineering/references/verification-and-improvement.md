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
