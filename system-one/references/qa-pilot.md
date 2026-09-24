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

For the separate main-branch paired-eval audit's setup, verification,
failure paths, and rollback, read `references/jev-ci-reference-deployment.md`.

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

Check the paired-eval selection summary before interpreting audit coverage.
Any changed file in a skill directory, including a reference or template,
selects that skill when it has an eval manifest. More than five eligible skills
fails selection without evaluating a subset. The audit's coverage percentage
counts only prose assertions in comparison reports actually produced; it does
not establish coverage of omitted skills, skipped model jobs, or the catalog.
The model job records selected case IDs before generation. The audit compares
that expected set with observed reports and lists missing or unexpected cases;
only a matching set can support a complete selected-case coverage claim.

For local inspection, first download a trusted paired-eval artifact and run
the audit offline. Add `--live` only after reviewing the generated responses
for data allowed to leave the environment and setting `TYPESAFE_API_KEY`.
The audit limits response size, file size, call count, and assertion count;
its report contains verdict metadata and response hashes but no generated
text. Its `question_contract_sha256` fingerprints the pinned model and one
placeholder request's trusted question/state shape, including Choice criteria;
compare this with the source revision before treating two runs as the same
input contract. It is not a hash of private generated responses or individual
eval assertions. Each result row also records `question_input_sha256`, which
fingerprints the exact model, question instructions, assertion text, and Choice
criteria for that group while excluding generated response text. Use it with
the separate `response_sha256` and case/side identity for like-for-like input
comparisons. The private calibration helper verifies this row fingerprint
against the matching comparison artifact when present, rejects mixed legacy
and fingerprinted rows, and accepts wholly legacy audits without claiming
they had exact-question provenance. A hash proves identity, not grading
quality or consent to replay an artifact.
When multiple skills compete for the budget, it visits one complete
candidate/baseline case pair per skill before taking another, using stable
hash order within each skill. This spreads limited coverage; it is not a
random or representative sample, and budget omissions remain explicit. Treat
downloaded artifact text as untrusted data, never executable
instructions. An unavailable endpoint, malformed artifact, skipped response,
or budget omission is missing audit evidence, not a pass.

The current synthetic semantic-audit fixture is
`examples/jev-eval-benchmark.json`; use `scripts/jev_eval_benchmark.py` with
`--split dev` for iteration and `--split test` once for a frozen check. The
labels are author-constructed and do not establish real-world calibration.
The additional `examples/jev-ci-coverage.synthetic.json` probes selected-case
identity and count reconciliation. Its `dev` and `test` splits were both opened
in the 2026-09-23 input experiment, so neither is a fresh holdout. Use
`--question-variant mismatch-shadow-v1` in the benchmark for the experimental
instruction, and keep the default `deployed` variant for the existing CI
contract. The normal `skill-eval.yml` audit always uses the `deployed` variant.
The separate, main-only manual workflow
`.github/workflows/jev-eval-replay.yml` can replay a successful main-branch
model artifact with an explicitly selected question variant, including
`all-requirements-shadow-v1` for list completeness and contradictory
instructions. It requires a per-run egress authorization input that defaults
to false, verifies source-run provenance, and treats the downloaded artifact
as data. A replay sends the same generated response text to TypeSafe again;
do not dispatch it without specific data-flow authorization. The replay is
not part of required CI and never changes the deterministic evaluation result.
Record the source run ID, selected question variant, question-contract
fingerprint, and completeness counts. Do not treat a shadow result as
calibrated, deployed, or eligible for release gating.

`examples/jev-procedure-conflict.synthetic.json` contains a separate screen
for prose summaries that conflict with concrete pseudocode. Both splits have
now been opened. Candidate v1 failed its development Brier stop rule; candidate
v2 improved a single `not_shown` development label, but tied the deployed
wording on all six test labels and had worse Brier. Neither candidate is
promoted. Use these examples to reproduce that limited experiment, not as
production calibration data.
The focused `examples/jev-atomic-assertion-screen.json` has three synthetic
evidence shapes for each of two decision/attempt/outcome assertions. Run it
with `--split dev` as a wording regression screen only; its six obvious
examples are neither a held-out set nor a substitute for real-output labels.
Before promoting any advisory label into a gate, collect independent
human labels on representative real outputs and measure false accepts,
abstentions, subgroup behavior, and drift at the actual decision boundary.

### Private review packet for real-output calibration

Use `scripts/jev_eval_calibration.py` locally after downloading a **complete**
default-branch paired-eval model artifact and its matching Jev audit artifact.
The helper rejects an audit with omitted, oversized, unpaired, or errored
assertions. Packet preparation also requires the frozen selected-case list to
match the observed reports; an audit with unknown or incomplete selected-case
coverage cannot be calibrated as a full run. The helper verifies response
hashes and assertion text before sampling.
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

Each private packet now includes `review.html`, an offline form containing the
same blinded responses and assertions as the Markdown review packet. It embeds no
external assets, sends no requests, and does not use browser storage. A
reviewer can enter an ID, label each item with `met`, `not_met`, `not_shown`,
or `uncertain`, add a short evidence note, download an incomplete draft, and
reload that draft later. Final export requires every label and evidence note
plus an explicit prediction-blinding attestation; it produces the same v1
labels JSON accepted by `compare` and `score`. A draft is **not** a frozen
review and cannot be scored. If a browser will not open the local form, use
the Markdown packet and a separate copy of `labels-template.json` instead.

Have each reviewer who has not seen Jev's answers fill a **separate** label
file. Freeze both files before comparison.
The offline form and new human label template set `reviewer_kind: human`.
For an inference-model review, set `reviewer_kind: model_teacher` explicitly;
do not pass a model-produced label file off as human review. Older files
without this field are scored as `unknown` provenance, never assumed human.
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

### Model-teacher screen without manual labeling

When human review is unavailable, `prepare` also writes a private
`review-items.json` containing only IDs, assertions, and generated responses.
It excludes Jev predictions, sample stratum, and candidate/baseline metadata.
The main-branch-only manual workflow `.github/workflows/jev-teacher-calibration.yml`
downloads a successful main-branch paired-eval run, creates that packet, and
asks the separate Nous Portal inference model for two blind label passes.
Different assertion order reduces a small presentation bias; it does **not**
make the passes independent judges. Disagreement or either pass's `uncertain`
becomes consensus `uncertain`, never a forced pass. The workflow uses the
existing `NOUS_API_KEY` secret and uploads only hashed item IDs, labels, and
aggregate Jev-versus-teacher counts. Generated responses, Jev's private map,
and teacher rationales remain private in the runner workspace.

For a local authorized run from the skill root:

```bash
python3 scripts/jev_teacher_label.py \
  --items /private/path/review-v1/review-items.json \
  --output-dir /private/path/teacher-v1
python3 scripts/jev_eval_calibration.py score \
  --private-map /private/path/review-v1/private-map.json \
  --labels /private/path/teacher-v1/consensus-labels.json \
  --output /private/path/teacher-score.json
```

This is pseudo-labeling for **advisory error discovery and rubric iteration**,
not training Jev weights, human-grounded calibration, or a release gate. Jev
is a managed API with no public fine-tuning path. Do not use Jev outputs as
training targets for an imitation model; review the current TypeSafe account
agreement before any distillation project. Tune on one frozen development
slice and evaluate changes on a separate held-out slice; report teacher
uncertainty and known counterexamples rather than treating agreement as truth.

The separate manual `.github/workflows/jev-local-teacher-calibration.yml`
offers a diagnostic screen on the existing self-hosted evaluation
runner. It uses only reviewed `main` code and the already configured
`host.docker.internal:8080` model service, so it adds no inference-provider
egress. It checks the label contract with synthetic text before downloading
the frozen response artifacts. The default `small` profile reviews four
candidate/baseline pairs and four risk-enriched items; the manual `full`
profile uses 16 pairs plus 12 challenge items. Use seed `jev-543-blind-v1`
with `full` to replay the original frozen 44-item packet. Only hashed IDs,
labels, and aggregate counts are uploaded. The local teacher may be the
**same model that generated the answers**; even two blind passes are
correlated self-review, not independent labels or accuracy. Do not promote
its score to a Jev threshold or gate. The first full-profile live run failed
closed on a non-JSON model response after a successful synthetic preflight;
it produced no score. Treat this profile as a diagnostic, not a reliable
calibration path for the current local checkpoint.

### Repeatability without new provider calls

When two complete Jev audit artifacts already exist, compare them offline
*only if* their generated response hashes, assertion text/order, model, and
auditor implementation match. Pass the exact full Git commit SHAs for the
auditor source in each run; the helper reads those commits locally and rejects
a changed implementation. Do not use branch names or abbreviated revisions.
Run from the skill root:

```bash
python3 scripts/jev_eval_calibration.py stability \
  --first-audit /private/path/first-jev-eval-audit.json \
  --second-audit /private/path/second-jev-eval-audit.json \
  --first-revision 0123456789abcdef0123456789abcdef01234567 \
  --second-revision fedcba9876543210fedcba9876543210fedcba98 \
  --output /private/path/stability-report.json
```

Use the *actual* commit SHAs from the two source runs. The report contains
response/assertion hashes, verdict flips, and probability/confidence movement,
but no generated response or assertion text. Identical inputs and stable
verdicts still do not establish correctness or calibrated probabilities.
Keep this output private alongside the audits. A failed network replay is
missing evidence; do not retry by another execution route when external
transmission has not been authorized for the specific payload and destination.
