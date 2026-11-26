# Selective judgment and validated escalation

Read this before accepting a model verdict based on confidence or escalating
uncertain decisions to a stronger judge. Fill `templates/cascade-qualification.md`.
This procedure applies to any qualified typed model; it does not transfer a
provider's thresholds, probability semantics, or task quality to another model.

## Published evidence and its limits

Li, Miao, Krishnan, and Padman, [JEV-as-a-Judge, revision 3](https://arxiv.org/html/2609.26550v3),
29 September 2026, sections 6–9 and appendices M–N, reviewed 26 November 2026.
This revision adds prospective live calls on two correctness workloads. Using
100 selection pairs per workload, a prespecified threshold selection procedure
matched GPT-6 aggregate accuracy on 570 held-out pairs while escalating about
74% and saving about a quarter of its fee. This is an observed match on these
cases, not demonstrated equivalence or a universal fee or latency promise. The
two workloads use verifiable correctness pairs; some JudgeBench questions
overlap an earlier sample. This is not a live production monitoring trial.

The paper distinguishes a verdict that can be read from supplied evidence from
one that must be derived, such as a difficult code, math, or logic judgment.
Use the distinction to choose the evidence and evaluator, not to route on domain
labels by themselves. For example, identify whether a patch claims recovery
from a log, then run an actual recovery test to establish whether it works.
The paper also finds weaker routing on misleading style and reference-free prose.
It uses maximum label probability, which is not automatically calibrated
correctness or interchangeable with a provider's native confidence field.

[Rao and Callison-Burch](https://arxiv.org/html/2609.29769v1) found that other
judges often shared confident Jev mistakes on graded rubrics. A fallback can
match a baseline in one workload and add little in another if it repeats the
first judge's errors. Read the [rubric judge evidence](rubric-judge-research.md)
before transferring either result. Treat repeatability, agreement with a
reference, and the fallback's ability to catch different errors as distinct.

## 1. Define what the route must preserve

Choose the actual judgment target and its observable evidence. Evidence-grounded
support, rubric compliance, preference, and correctness of a derivation are
separate workloads. A fluent answer, typed response, or agreement with a second
judge does not establish correctness. If the input lacks required evidence,
obtain it or route to review regardless of model confidence. An unsupported
workload may require escalation before the first model call.

Preregister a practical loss tolerance and absolute maximum accepted-case error
for consequential slices, plus coverage, latency, cost, and review constraints.
Relative retention can hide unacceptable errors in both models. Name the owner
and what happens when the fallback is invalid, unavailable, or also uncertain.
Keep permissions and execution gates independent of this semantic acceptance.

## 2. Qualify the uncertainty signal

Specify the signal exactly: maximum label probability, margin, entropy, calibrated
probability, native confidence, or another validated statistic. Do not treat them
as interchangeable. Choice distributions depend on their exact option set;
Score values or reward-model scalars are not automatically probabilities.
Different primitives, request grouping, context, or decoding require rechecking.

Measure three distinct properties against independent labels:

| Property | Question | Evidence |
|---|---|---|
| Decision quality | Is the verdict right? | Confusion/errors, all-case accuracy, important slices |
| Calibration | Do probabilities match empirical frequencies? | Reliability bins/counts, Brier/NLL, label uncertainty |
| Error discrimination | Can the signal find likely mistakes? | Error-detection AUROC/PR, risk–coverage curves, confident errors |

A calibrated constant base-rate prediction can rank no errors. A useful ranker
can have poor probability calibration. Report both, and the denominator of valid
outputs separately from all attempted cases. Validate finite normalized output,
label membership, IDs, and verdict/decoder consistency before acceptance. Invalid
first-stage results defer; unresolved final cases remain unresolved/errors in
all-case quality, not disappearing from a valid-only denominator.

## 3. Fit a policy without leaking the test

1. Use representative privacy-safe outputs labeled independently of both judges.
   Record human/model-teacher/unknown provenance, disagreements, and abstentions.
   Model-teacher labels are a screen, not human ground truth or gate qualification.
2. Split by independent unit: incident, source question, submission, tenant, or
   session as appropriate. Keep paired answers and presentation variants together.
   Maintain a selection split for threshold/temperature/rubric changes and an
   untouched test split; record hashes and overlap checks.
3. Test the intended request shape and model/adapter revisions. For pairwise
   preference, reverse order, map results to response identity, and measure
   inconsistency. If using two-order averaging, freeze that policy and count both
   requests. For binary A/B, aligned p(A) is
   `(p_first(A,B) + 1 - p_first(B,A)) / 2`; this assumes complementary binary
   options, not a tie/unknown class. With extra classes, align the full
   distributions by identity, preserve those classes, and specify tie handling.
4. Choose the greatest useful coverage satisfying the declared risk constraints
   on selection data. Fit any probability map there; freeze all artifacts before
   the test. Never select a threshold on the reported test curve. If test fails,
   reject/revise and obtain a new untouched test before another release claim.
5. Stress unsupported evidence, elaborate false answers, negation, candidate-set
   omissions, rubric paraphrases, order reversal, language/domain shift, and
   transport failures. Do not combine special-case challenges with representative
   prevalence estimates without reporting their sampling weights separately.

## 4. Evaluate the whole cascade and its fallback

On identical held-out cases compare current deterministic behavior, primary
alone, fallback alone, a no-confidence/random-escalation control at matched
budget, and the frozen route. Oracle routing uses labels unavailable at runtime;
report it only as an upper bound. Both-orders-correct quality is a diagnostic,
not the same metric as averaged-route quality.

Record accepted primary errors, escalated cases, fallback rescues (primary wrong,
fallback right), regressions (primary right, fallback wrong), shared errors,
unknowns, and budget exhaustion. Measure these within the actual deferral band
and important slices, not just pooled across all cases. A stronger average judge
may share the primary's errors or worsen the selected cases. A fallback's fluent
rationale is not independent corroboration.

Report all-case and resolved-case accuracy, accepted-case error, coverage,
escalation/review rate, paired quality differences, and uncertainty. Resample the
independent source clusters together for paired intervals; include counts and
label ambiguity. A nonsignificant difference is not equivalence. A noninferiority
claim requires a predeclared margin and an interval satisfying it, not merely a
large relative retention ratio or point estimate within tolerance.

Use `references/cascade-economics.md` for complete accounting. Include both order
calls, classification, fallback, retries, queues, review, verification, and failed
attempts. Unknown cost is unknown, not zero. Counterfactual replay can screen a
policy but cannot establish live cascade latency: measure the real serial or
parallel route, delivery boundary, p50/p95/p99, and deadline/failure behavior.
A cheap first stage with little selective coverage can cost more than fallback
alone. Budget exhaustion routes to the declared review/hold lane; it does not
lower the risk threshold automatically.

## 5. Monitor and requalify

Start in shadow mode, retain a blind sample of accepted and escalated cases,
and review confident errors. Requalify on model alias drift, rubric/adapter or
candidate changes, new domains/languages, prevalence shift, or worse accepted
risk. Record fallback availability and reviewer capacity; define disable/hold
conditions and rollback. Repeated calls on old cases establish repeatability,
not fresh independent evidence. Repeated voting must be evaluated as a separate
policy including correlated errors and every call's cost.

Complete qualification only when the frozen held-out result supports a scoped
adopt/shadow/revise/reject decision and the live failure boundary is tested for
any deployment claim. Missing labels, freshness, fallback evidence, or practical
gates means remain advisory. See `references/rubric-judge-research.md` for graded
scale mismatch and shared errors; apparently favorable cascade results on one
workload do not contradict poor results on a different rubric task.
