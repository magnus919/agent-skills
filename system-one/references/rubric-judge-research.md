# Rubric judges: correlated errors and scale conventions

Read this when replacing an LLM rubric judge, designing graded criteria, or
proposing confidence-based escalation to another judge.

## Source and evidence boundary

Rao and Callison-Burch, [JEV vs. LLMs as Rubric Judges: Cheaper, Faster, and
Wrong in the Same Places](https://arxiv.org/html/2609.29769v1), v1,
24 September 2026; reviewed 26 September 2026. The supplied
[author thread](https://x.com/deliprao/status/2103585684736954718) could not be
retrieved; no thread claims are attributed here.

The study compares Jev and three flash-tier judges on 5,003 criterion pairs
across nine panels. Only 8/27 paired accuracy intervals exclude zero; an
inconclusive difference does not establish equivalence. Jev has substantial
cost/time advantages under a batched-per-unit versus per-criterion-call protocol.
These ratios are not universal deployment estimates.

Graded judges agree with each other more than with labels and mostly grade
lower. Missing rater conventions are one observational explanation; rubric
rewrites and exemplars were not experimentally tested. On sampled confident
Jev errors, LLM verdicts repeat the wrong answer 96% of the time. Cross-fitted
cascade replay gains at most 1.5 percentage points over the best single judge;
it estimates costs rather than measuring a live cascade.

The study tests one typed classifier, English graded panels, undated model
aliases, and limited repeated runs. Choice includes an NA option; Score lacks
that abstention option. Confidence ranks uncertainty here, not calibrated
correctness. See sections 3, 6–7 and Limitations for protocol details.

## Apply this to a decision contract

1. Define the actual target: observable checklist compliance, an ordinal
   judgment, or a population-relative convention. Preserve original rater
   instructions and label provenance. Keep disagreement visible; distinguish
   unanimous and split labels rather than calling every disagreement a model
   failure.
2. Freeze primitive, options, option order, criterion text, state fields,
   aggregation, numeric decoding, and tie-rounding rules. Do not silently
   compare rounded Score with argmax Choice as if they were identical tests.
   Provide a separate insufficient-evidence lane when the chosen primitive
   cannot express abstention.
3. Evaluate exact agreement and per-criterion signed level offset alongside
   ordinal/rank metrics. A rank metric can miss consistent under-scoring.
   Inspect confusion and level occupancy for unused middle or top levels.
4. If evidence suggests missing scale conventions, propose a versioned input
   experiment: observable level descriptions, trusted exemplars, or original
   rater instructions. State the failure hypothesis, change one factor, fit on
   calibration data, and compare on untouched labeled units. Do not apply an
   offset fitted on the evaluation cases as a demonstrated repair.
5. Before adding a fallback or jury, record paired outcomes for both judges
   against independent labels. Count shared wrong answers and fallback rescue
   and regression cases within the intended deferral band; also inspect
   confident errors that the route will retain. Agreement between providers
   is not independent corroboration of correctness.
6. Compare a frozen route with the best single judge using quality, coverage,
   cost, review workload, and end-to-end latency. Split by independent unit so
   criteria from one submission cannot leak across fit/test sets. Distinguish
   an oracle ceiling, cross-fitted replay, and measured live behavior.

Stop when the comparison supports an explicitly scoped adoption, shadow,
revision, or rejection decision. Missing independent labels or an untouched
test set supports an advisory screen only. This research does not authorize a
release gate or prescribe a production confidence threshold.

## Reviewable challenge examples

For cascade claims, a satisfying answer measures shared errors and paired
rescue/regression on held-out units; a near miss assumes another provider
corrects uncertainty; an answer with no error analysis leaves that evidence
not shown. For scale repair, a satisfying answer tests a frozen revision on
untouched labels; a near miss adds a level to the same scored examples; an
answer naming only a rank metric omits evidence of level placement. For
comparability, a satisfying answer records decoding and abstention differences;
a near miss calls Score and Choice interchangeable; naming models alone leaves
the comparison contract not shown.
