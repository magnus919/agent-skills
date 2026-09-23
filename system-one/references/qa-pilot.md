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

## Advisory audit of paired skill evals

The repository's `skill-eval.yml` can run `scripts/jev_eval_audit.py` after a
default-branch real-model paired evaluation. This is a different experiment
from the 22-case QA pilot: it reads completed comparison artifacts, selects
only `manual_review` prose assertions, and asks Jev whether each assertion is
`met`, `not_met`, or `not_shown`. Existing deterministic assertion grades stay
untouched. `not_shown` means the generated text does not establish the claim;
it is not interchangeable with a demonstrated contradiction.

For local inspection, first download a trusted paired-eval artifact and run
the audit offline. Add `--live` only after reviewing the generated responses
for data allowed to leave the environment and setting `TYPESAFE_API_KEY`.
The audit limits response size, file size, call count, and assertion count;
its report contains verdict metadata and response hashes but no generated
text. Treat downloaded artifact text as untrusted data, never executable
instructions. An unavailable endpoint, malformed artifact, skipped response,
or budget omission is missing audit evidence, not a pass.

The current synthetic semantic-audit fixture is
`examples/jev-eval-benchmark.json`; use `scripts/jev_eval_benchmark.py` with
`--split dev` for iteration and `--split test` once for a frozen check. The
labels are author-constructed and do not establish real-world calibration.
Before promoting any advisory label into a gate, collect independent
human labels on representative real outputs and measure false accepts,
abstentions, subgroup behavior, and drift at the actual decision boundary.

### Private review packet for real-output calibration

Use `scripts/jev_eval_calibration.py` locally after downloading a **complete**
default-branch paired-eval model artifact and its matching Jev audit artifact.
The helper rejects an audit with omitted, oversized, unpaired, or errored
assertions and verifies response hashes and assertion text before sampling.
It makes a private, prediction-blinded review packet: the sampled assertions
and generated responses are visible, but the Jev answers, sample class, and
candidate/baseline metadata live only in a separate private map. Generated
text itself can still reveal provenance or contain adversarial instructions.
Review it as data, not directions.

Run from the skill root with a **new** output directory:

```bash
python3 scripts/jev_eval_calibration.py prepare \
  --reports /private/path/model-artifact \
  --audit /private/path/jev-eval-audit.json \
  --output-dir /private/path/review-v1 \
  --run-id <github-run-id> --seed <frozen-sample-seed>
```

The default selection is 16 uniformly hash-selected assertion *pairs* (32
candidate/baseline judgments) plus 12 remaining Jev-suggested `met` items
selected for high probability. These are different evidence classes: the
challenge set is intentionally enriched for false accepts and must not be
reported as workload prevalence. Change the counts before freezing the packet
if the decision risk needs broader coverage. All packet files are written
with private permissions and must not be committed or uploaded as CI artifacts.

Have each reviewer who has not seen Jev's answers fill a **separate copy** of
`labels-template.json` using `met`, `not_met`, `not_shown`, or `uncertain`, with
a short evidence note for every item. Freeze both files before comparison.
Do not share a first reviewer's labels with the second reviewer. Compare the
frozen labels *without* opening `private-map.json`:

```bash
python3 scripts/jev_eval_calibration.py compare \
  --first /private/path/reviewer-a-labels.json \
  --second /private/path/reviewer-b-labels.json \
  --output /private/path/reviewer-disagreements.json
```

The comparison lists disagreements and uncertain items without any Jev
predictions. Agreement is not correctness. Adjudicate substantive disagreements
against the visible response and rubric, retaining both original reviews and
the adjudication record. Only after labels are frozen and disagreements are
resolved should the private map be opened and the labels scored:

```bash
python3 scripts/jev_eval_calibration.py score \
  --private-map /private/path/review-v1/private-map.json \
  --labels /private/path/adjudicated-labels.json \
  --output /private/path/review-v1/reviewer-a-score.json
```

The score report separates the population sample from the risk-enriched
challenge set and exposes confusion counts, suggested-`met` false accepts,
and a `met` probability Brier score only when the stratum is fully resolved.
One reviewer and one run cannot establish a gate threshold. Preserve the
artifact hashes, seed, model/rubric revision, disagreement record, and missing
labels; repeat after any model, rubric, or workload change.
