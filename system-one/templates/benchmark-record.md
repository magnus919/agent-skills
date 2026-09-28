# System One benchmark record

## Run identity

- Date/time and operator:
- Commit/config hash:
- Model/provider/revision:
- Runtime/image digest:
- Device/driver/precision:
- Dataset and split/checksum:
- Dataset construction protocol and inclusion/exclusion revision:
- Label source, disagreement, and approval for provider transmission:
- Blind-label packet and rubric revision; reviewer identity/provenance:
- Known label source and label visibility to developers/model authors:
- Provider's training-data provenance: [ ] documented [ ] partially known
  [ ] unknown; evidence or uncertainty:
- Selection, training, threshold-tuning, calibration, and test split relationship:
- Distinct scenarios / question judgments / network requests:
- Question-contract/policy hash:
- Raw response artifact location/checksum (redacted or access-controlled):
- Exact serialized request/payload hash per model (store sensitive payloads privately):
- Adapter source revision, config hash, and qualification record:

## Comparison track

Choose one primary track before running. Do not combine its conclusions with the
other track without a separate analysis.

- [ ] **Fixed contract:** exact state, question wording, criteria, labels, option
  order, and task definition are held semantically constant across models;
  native serialization may differ and must be recorded. Record any model that
  cannot represent the contract faithfully; do not silently adapt it.
- [ ] **Model-adapted:** each candidate receives a separately authored and
  versioned adapter/question mapping that is intended to express the same
  decision. Give each candidate the same bounded development budget and record
  changes to questions, criteria, and thresholds. Select or tune only on dev
  and calibration partitions; evaluate all candidates on the untouched common
  test. Preserve mappings and rationale. This compares model-plus-adapter
  systems, not isolated model weights.
- Primary estimand and unit of comparison (scenario, judgment, request, or task):
- What can and cannot be attributed to the model under this track:

## Adapter qualification

- Adapter implementation/revision and maintainer:
- Qualification cases and expected semantic mapping:
- Tests for response IDs, types, options, normalization, missing/extra answers,
  order sensitivity, batching, overflow/truncation, retries, and abstentions:
- Golden protocol examples from the provider or maintained reference client:
- Polarity reversal examples with the same decisive evidence and irrelevant
  lexical cues counterbalanced:
- Device/checkpoint identity and actual residency check (when locally hosted):
- Verified behavior on malformed, unsupported, and boundary-size requests:
- Which mismatches reject a run rather than count as model errors:
- Adapter contract mismatch before qualification aborts comparison. Once
  qualified, operational failures, malformed responses, timeouts, abstentions,
  and missing outputs remain in the denominator under the predeclared scoring
  rule; do not drop them after observing results:
- Independent reviewer and approval evidence:

## Dataset, labels, and leakage controls

- Sampling frame, target population, time window, filters, deduplication, and
  exclusions:
- Representative sample versus separately reported risk-enriched challenge set:
- Label rubric, examples, annotator blinding, adjudication, disagreement, and
  unknown/unanswerable labels:
- Known answer source and whether it is visible in state, metadata, retrieval,
  template artifacts, or prior model outputs:
- Shortcut checks (source IDs, duplicates, timestamp, position/order, lexical
  cues, data provenance, and split membership):
- Grouping unit used to keep related users, documents, tasks, or near-duplicates
  within one split:
- Training, checkpoint selection, and benchmark data known/unknown provenance
  for each provider/model; distinguish vendor training data from this study's
  split membership:
- Training / model selection / prompt or adapter selection / threshold tuning /
  calibration / final test: identify each split and any overlap explicitly:
- Final test access and unsealing rule:
- Missing labels, excluded failures, and denominator accounting:

## Matched conditions

- State serialization:
- Question and option order:
- Batch/concurrency:
- Warmup and cache state:
- Network region/endpoint:
- Request timeout/retry policy:
- Response ID/type/option validation and missing-answer count:
- Pilot review and answer-rubric revision:
- Result storage outside the repository:
- Request-shape and concurrency parity; report unsupported shapes separately:
- Immutable model/checkpoint, tokenizer, adapter, and runtime identities:

## Quality

| Slice / primitive | N | Accuracy / MAE | Brier / log loss | ECE | Coverage | Notes |
|---|---:|---:|---:|---:|---:|---|
| | | | | | | |

- Paired unit and pairing key:
- Primary metric and direction; decision-relevant margin:
- Simple deterministic/current-process baseline and any baseline parameters
  fit only on development data:
- Decision-specific cost of false accept, false reject, abstain/review, and
  operational failure:
- Paired uncertainty method and interval/confidence level:
- Cluster/resampling unit (such as user, document, conversation, or task); the
  count of correlated rows is not the independent sample size:
- Multiplicity plan for models, metrics, slices, and interim looks:
- Equivalence or non-inferiority margin and predeclared decision rule, if used:
- Repeated identical-input runs, stochastic settings, and run-to-run stability:
- Whether repeats are summarized within unit; repeated calls do not multiply
  the independent number of labeled units:
- Errors, abstentions, malformed outputs, missing answers, and exclusions retained:
- Per-slice counts and uncertainty; do not infer parity from a non-significant test:

## Operations

| Metric | p50 | p95 | p99 | Mean | Notes |
|---|---:|---:|---:|---:|---|
| End-to-end latency | | | | | |
| Queue time | | | | | |
| Inference time | | | | | |

- Timing start/end boundary (client, network, queue, retries, fallback, review,
  and action completion included or excluded):
- Warmup policy, measurement window, repetitions, clock source, and timeout rule:
- Report cold start separately from warm steady state:

- Throughput:
- Peak memory:
- Provider cost or local resource cost:
- Error/fallback/abstention rate:
- Cost boundary (retrieval, classifier, retries, fallback, review, final action):
- Paired baseline and uncertainty method:
- Actual device/checkpoint residency:
- Adapter and serialization overhead:
- Raw response, normalized output, and timing-log checksums/location:

## Decision

- Baseline comparison:
- Known failures:
- Outcome: `adopt` / `shadow` / `investigate` / `reject`
- Accountable decision owner:
- Rollback/reassessment trigger:
- Evidence gaps and claims this run cannot support:
