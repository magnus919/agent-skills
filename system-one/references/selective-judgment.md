# Selective judgment and validated escalation

Read this before accepting a model verdict based on confidence or escalating
uncertain decisions to a stronger judge. Fill `templates/cascade-qualification.md`.
This procedure applies to any qualified typed model; it does not transfer a
provider's thresholds, probability semantics, or task quality to another model.

## Evidence from the supplied paper

Li, Miao, Krishnan, and Padman,
[JEV-as-a-Judge: Accept When Confident, Escalate When Unsure](https://arxiv.org/html/2609.26550v1),
arXiv:2609.26550v1, submitted 22 September 2026; reviewed 27 September 2026.

Its frozen two-order policy accepted 53.7% of 510 held-out extension preference
pairs: 92.5% accuracy versus 93.1% for GPT-6, fee ratio 0.568 (conservative 0.622).
The -0.59-point paired interval was [-1.78, 0.59]. This is relative accuracy
retention, not 99% correctness or established equivalence. Cascades were offline
simulations; live sequential latency remains unmeasured. Selection used 96 pairs.

On reference-free prose, Jev scored 52.5% with mean maximum probability 0.90 and
error-detection AUROC 0.518. Elaborate wrong answers weakened confidence routing.
One frozen fallback policy exceeded its loss tolerance. Confidence used maximum
label probability, not native confidence. Human adjudication covered selected
disagreements by one blinded author; benchmark contamination is unknown.

Take the workload-specific procedure, not a universal threshold. The proprietary
Jev version and heterogeneous baseline configurations are not a compute-matched
architecture comparison. Sections 3–7 and Limitations separate frozen policies,
post-hoc curves, validity, estimated fees, and adjudication provenance.

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
