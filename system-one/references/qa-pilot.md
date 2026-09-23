# Synthetic Jev QA pilot

Use this when testing whether a typed model could assist QA, not when deciding
whether CI is green or whether a release may ship. It exercises three bounded
questions: investigate a CI failure, prioritize **one additional** regression
test, and assess whether observed evidence satisfies a criterion. Mandatory
tests and red results remain under deterministic control.

Run from the skill root:

```bash
python3 scripts/test_jev_qa_pilot.py
python3 scripts/jev_qa_pilot.py
python3 scripts/jev_qa_pilot.py --live  # requires TYPESAFE_API_KEY in the environment
```

The 22 cases are synthetic and pre-labeled. The script does not transmit the
labels. It reports each model judgment and a deliberately simple rules-only
baseline, stopping on the first provider or response-contract error. The first
13 cases were tried live before the challenge cases were added; do not compare
the 13-case live score to the 22-case baseline as if they were the same set.
The baseline is transparent but not an optimized production comparator.
The report keeps selected-option probability and provider-reported confidence
separate for Choice; Noul reports the probability of `yes`, not a confidence
rating. None is treated as calibrated without held-out outcome evidence.

The 2026-09-22 local run of the pinned `jev-1.13.0` API returned 22 valid
responses: Jev matched 20/22 analyst labels (triage 8/9, extra-test choice
6/6, semantic grading 6/7); the simple rules matched 17/22 (7/9, 5/6,
5/7). Jev's misses were T9, an ambiguous exit-1 log containing an injected
instruction (model chose `code` with 0.45 top probability, label `unknown`),
and G7, a payment/shipment criterion (model Noul 0.43, label 1). The labels
and cases were written by one author and are not independent operational
ground truth. This result demonstrates mechanics and failure modes, not a
measured production improvement or a calibrated action threshold.

A second local run on 2026-09-22, made to inspect the newly separated
confidence fields, matched 21/22 labels. T9 was wrong again (`code`, selected
option probability 0.44, provider confidence 0.30). G7 moved from Noul 0.43
to 0.51 and crossed the pilot's 0.50 cutoff with no input change. Count both
runs; do not select the better one. The movement near the cutoff is a warning
against automating semantic grades from this tiny fixture. The seven Noul
cases have too few outcomes to calibrate a probability scale; a high cutoff
would abstain on all three correctly graded positive cases in the second run.

For repository CI, `.github/workflows/jev-qa-pilot.yml` is manual-only and
uses the `TYPESAFE_API_KEY` repository secret on a GitHub-hosted runner. Review
workflow and script changes before running. It does not run on pull requests,
publish secrets, post a PR verdict, or alter required quality gates. If the
secret is absent, the run fails visibly rather than reporting zero model calls
as a passing experiment.

For an actual product decision, replace synthetic cases with approved,
redacted, independently labeled cases from the intended workflow. Freeze a
held-out split; include missing and contradictory evidence, wrong-run logs,
prompt injection in data, all classes and `unknown`, and baseline comparisons.
Record a confusion matrix and calibrated risk/coverage measures with model,
rubric, and policy revisions. A probability is not proof or authorization.
