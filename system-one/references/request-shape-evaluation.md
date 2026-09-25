# Request shape, batching, and calibration

Use this guide when moving independent System One questions from separate calls
into one request, changing batch size/order, or comparing a hosted model with a
local System One checkpoint. “Batching” can describe two different changes:

1. **Question co-batching:** several typed questions for the same state are sent
   in one provider request. This is the API shape documented for Jev.
2. **Record aggregation:** an application packs several records into one shared
   state and asks questions about each. This changes state content and input
   size as well as call count. It is not equivalent to question co-batching.

Test the exact production transformation. Keep an identity hash for each
decision’s own state and question, and a separate hash for the complete request
payload. The per-decision hashes should match between solo and batch conditions;
the complete request hashes usually should differ.

## Avoid confounded comparisons

- Freeze exact model revision, state serialization, question wording, option
  order, policy, preprocessing, and gold labels. Record the requested alias and
  returned revision; do not combine results from different revisions.
- Use the same cases in both conditions. Pair each decision by model revision,
  split, replicate, case ID, question ID, state hash, question hash, and contract
  hash. Treat missing, malformed, timed-out, or unavailable responses as
  failures in operational coverage; do not silently drop them.
- Randomize which cases share a request and their position. Repeat with new
  permutations. Include the actual batch sizes, maximum question count, and
  question positions that production will use.
- Keep development, probability-calibration, and final test data separate.
  Choose any action threshold on calibration data, freeze it, then score the
  held-out test. Do not use the analyzer’s illustrative `0.5` Noul conversion as
  a production threshold.
- Compare independent questions only. If one answer changes the next question,
  candidate set, or state, that is a sequential workflow: evaluate the full
  sequence with the real dependency, fallback, and action logic.
- When a decision changes under batching, first verify that its per-decision
  state, question, and contract hashes are unchanged. Then compare the returned
  class probabilities and selected class, confirm the answer is mapped to the
  correct question ID, and inspect its position and co-batched peers across
  seeded regroupings. This separates a model response shift from a client-side
  association, parsing, or tie-breaking defect.
- Verify the checkpoint identity and intended task/domain before interpreting
  scores. A service alias or a broad family label does not establish that the
  loaded checkpoint was tuned for the tested task. If the provider cannot
  expose a checkpoint revision or digest, record that uncertainty and avoid
  attributing poor task performance to batching or the model family.
- Measure both question quality and the complete request/workflow: class
  accuracy, probability quality, confidence/coverage, error rate, p50/p95/p99
  latency, timeout/retry behavior, throughput, and cost per resolved decision.
  A batch may reduce round trips while increasing tail latency or correlated
  failure impact.

Batching can change outcomes even when the application believes it is asking
the same independent questions. Treat that as a testable hypothesis, not a
universal batching defect: provider, model revision, state serialization,
question order, and batch size can all affect observed behavior. Do not turn a
single field report or pilot into a cross-model rule.

## Offline paired analyzer

`scripts/batch_request_shape.py` reads captured JSONL; it makes no model calls.
Run its mechanics fixture:

```bash
python3 scripts/batch_request_shape.py \
  --cases examples/batch-request-shape.synthetic.jsonl
```

Each line represents one case/question answer and includes `model`,
`model_revision`, `split`, `condition` (`solo` or `batch`), `request_id`,
`batch_size`, zero-based `position`, `replicate`, `case_id`, `question_id`,
`label`, `contract_sha256`, `state_sha256`, `question_sha256`,
`request_sha256`, `status`, and—on success—`prediction` and a `probabilities`
object over the complete class set. `slice` is optional. Hashes are lowercase
SHA-256 hex. `state_sha256` is for the decision's individual state, even when
that state is one part of an aggregate request; `request_sha256` identifies the
exact serialized full request and is expected to vary by condition. Error rows
must retain their error status/reason rather than invent an answer.

The analyzer validates request membership, class probabilities, hashes,
gold-label consistency, and paired identity. It reports paired answer changes,
per-condition accuracy, all-attempt accuracy, error rate, multiclass Brier
score, log loss, fixed-width top-confidence ECE bins, and a deterministic
case-cluster bootstrap interval for the accuracy difference. Keep all exact
response artifacts private when they contain real data. The analyzer’s
confidence interval assumes cases are the independent clusters; tiny samples
and narrow synthetic fixtures are only a check that the pipeline works.

### Frozen row example

```json
{"model":"jev","model_revision":"jev-1.x","split":"test","condition":"batch","request_id":"r-14","batch_size":2,"position":0,"replicate":2,"case_id":"ticket-014","question_id":"refund","contract_sha256":"<64 lowercase hex>","state_sha256":"<64 lowercase hex>","question_sha256":"<64 lowercase hex>","request_sha256":"<64 lowercase hex>","label":"no","prediction":"no","probabilities":{"yes":0.08,"no":0.92},"slice":"en"}
```

Replace placeholders with actual digests; do not copy raw personal state into
the report. Keep a private manifest mapping hashes to the frozen, approved
dataset and exact request bytes when reproducibility requires it.

## Live contract checks and matched studies

For one-request endpoint and response-contract checks, use the generic
`scripts/systemone_probe.py` with `--live` only after the target endpoint,
credential, and safe request are configured. Its default offline mode validates
the request without network access. A successful contract probe establishes
only that one request was accepted and returned the expected shape; it is not
a quality or calibration benchmark.

For model-level quality conclusions, assemble a licensed, privacy-safe
human-labeled corpus and run a paired held-out study. Public availability does
not by itself authorize sending all text to a third-party API; check its license
and remove personal/sensitive fields first. If no suitable corpus and
transmission basis are available, stop at mechanics and report that gap.

## Interpret with care

- A changed response is not necessarily an error; compare it with frozen gold
  labels and task costs. A stable response is not necessarily correct.
- Calibration is distribution-specific. Report reliability by class, language,
  domain, question type, batch size, position, and risk slice when sample sizes
  support it. Do not transfer one model’s probability map to another.
- Use a per-decision comparison when questions are independent. Use full
  workflow replay when batch aggregation changes context, dependencies, action
  ordering, or fallback behavior.
- Keep raw outputs and provider accounting private. Log exact prompt/question,
  model revision, request ID, payload hash, batching policy, response status,
  latency, and credits/tokens if returned; never log credentials.
