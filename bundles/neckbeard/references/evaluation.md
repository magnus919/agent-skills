# Evaluation Methodology

The evaluation harness lives in [../eval/](../eval/). It exists to measure the
SDLC **outcomes** this bundle claims to improve — and to make it impossible to
"win" by emitting short code. This file is the method; `eval/` is the tooling.

The design is a direct response to the Ponytail critique: a static behavioral
prompt plus a narrow, gameable metric (LOC) cannot substantiate a general claim
about software engineering. So the metric here is never LOC or brevity.

## What is measured (outcome rubric)

Score each run on these dimensions. LOC may appear only as **diagnostic
metadata**, never as a success proxy.

| Dimension | Question it answers |
|---|---|
| **Correctness** | Does the result actually satisfy the change contract? |
| **Regression safety** | Did it avoid breaking existing behavior/tests? |
| **Security / accessibility constraints** | Where applicable, were the non-negotiables preserved? |
| **Test adequacy** | Are the checks sufficient for the declared boundary? |
| **Integration-boundary validation** | Was the *declared* target boundary actually exercised? |
| **Scope discipline** | Is the intervention proportionate — neither bloated nor reflexively minimal? |
| **Maintainability** | Can a human read, review, and extend it? |
| **Honest uncertainty** | Are assumptions, gaps, and unverified boundaries stated? |
| **Time / cost** | Only if measured; reported, never used alone to claim a win. |

Full rubric with scoring anchors: [../eval/rubric.md](../eval/rubric.md).

## Task fixtures

Representative, repository-backed tasks across these classes:

- bug diagnosis
- feature change
- refactor
- specification ambiguity
- regression prevention
- review finding
- release verification
- **"no change needed"** cases

Plus **adversarial / counterfactual** cases where the correct answer is a
*larger* change, a new dependency, a non-code process change, or no code change
at all. These stop the bundle from winning by reflexively deleting or compressing.

Each fixture carries its repository context and harness constraints. Schema:
[../eval/task-schema.md](../eval/task-schema.md). Fixtures: [../eval/fixtures/](../eval/fixtures/).

## Holdout discipline

Keep a task set **separate** from author iteration. Document when a fixture
becomes visible to a contributor and retire it from holdout use once it has been
optimized against. Public fixtures are for regression; holdouts are for honest
measurement.

## Fair baselines

Compare against a **context-equivalent** agent/harness. Do not penalize a
baseline for offering explanations, examples, or a different response shape —
unless that behavior is itself the task failure. The baseline must see the same
repository context and constraints.

## Multi-run, multi-model reporting

Report, for every result:
- model and model version (where available)
- harness / system prompt
- tools available
- fixture revision
- randomization settings
- run count and variance / confidence intervals

Never collapse one favorable point estimate into a universal claim.

## Reproducible artifacts

Retain: prompts, fixtures, scoring rubric, commands, raw anonymized outputs
(when licensing permits), and the aggregation script. Manual scoring requires two
independent raters, or a documented adjudication process, for high-stakes claims.

## Regression gate

A change to the bundle cannot claim improvement without running the public suite
and reporting holdout results through the maintainers' controlled workflow.

## Claims policy

Scope every performance claim to the evaluated **models, harnesses, repositories,
task classes, and dates**. Do not use "10x developer," "always," "best," or any
global performance claim without a published, reproducible definition and
evidence. Report template: [../templates/eval-report.md](../templates/eval-report.md).
