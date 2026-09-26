# Router and cascade economics

Use `scripts/cascade_economics.py` to summarize frozen, per-case outputs from
competing routing policies. It accounts for every executed stage, including
retrieval, router judgment, retries, human review, and fallback. It makes no
model calls and does not infer quality from a model's own confidence.

## Compare the whole policy

Evaluate the same held-out case IDs with the same independent labels across:

- current rules or production behavior;
- retrieval or shortlist without a semantic decision model;
- the best single model at its intended coverage;
- the proposed router without its difficulty/judgment signal;
- the full route including fallback and review.

Include deterministic parsing, retrieval, queueing, retries, review, and
verification costs wherever they are part of the deployed boundary. Count a
failed first attempt and its fallback; do not price only the final answer. If
review time is not priced, report it as calls/minutes in a separate ledger.
Keep task accuracy over all cases, accuracy among resolved cases, coverage,
abstentions, fallback frequency, latency, and cost visible together. Report
important slices separately. A cascade can raise selective accuracy by
abstaining more often, or reduce model cost while increasing human workload.

## Frozen trace format

Create one JSON object per case in JSONL. Labels must be assigned independently
of the policies being compared. Each case must contain every policy so results
are paired. A null `decision` is an abstention and is incorrect for
`accuracy_all_cases`; that metric keeps the denominator fixed. Stage costs must
sum to `cost_usd`, including failed calls and retries, when all stage prices
are known. If a called stage has no known price, set its `cost_usd` and the
pipeline `cost_usd` to `null`; never encode unknown cost as zero. The report
shows price coverage, known-cost subtotal, and `total_cost_usd` as null unless
all cases are priced. Cost deltas and their bootstrap interval use only cases
where both compared policies have a price, and report that paired count. Stage
`calls` counts provider attempts or local invocations; a retry is another
call. Mark every invocation of the fallback branch with `fallback: true`.

```json
{
  "id": "case-001",
  "label": "refund",
  "slice": "email-en",
  "policies": {
    "rules": {
      "decision": "refund",
      "cost_usd": 0,
      "latency_ms": 2,
      "stages": [{"name": "rules", "calls": 1, "cost_usd": 0, "latency_ms": 1}]
    },
    "cascade": {
      "decision": "refund",
      "cost_usd": 0.0004,
      "latency_ms": 82,
      "stages": [
        {"name": "retrieval", "calls": 1, "cost_usd": 0.0001, "latency_ms": 10, "input_tokens": 120, "output_tokens": 0},
        {"name": "router", "calls": 1, "cost_usd": 0.0001, "latency_ms": 20, "input_tokens": 80, "output_tokens": 4},
        {"name": "primary", "calls": 1, "cost_usd": 0.0002, "latency_ms": 40, "input_tokens": 100, "output_tokens": 3},
        {"name": "fallback", "calls": 0, "cost_usd": 0, "latency_ms": 0, "fallback": true}
      ]
    }
  }
}
```

Run the included tiny fixture as a mechanics check:

```bash
python3 scripts/cascade_economics.py \
  --cases examples/cascade.synthetic.jsonl --baseline best_single
```

The report includes all-case accuracy, resolved-case accuracy, coverage,
abstentions, fallback rate, total and per-case cost, end-to-end latency
percentiles, per-stage calls/cost, slice summaries, and paired correctness
wins/losses against the named baseline. It also reports a paired, case-level
bootstrap 95% percentile interval for the candidate-minus-baseline difference
in all-case accuracy, mean cost per case, and mean end-to-end latency. Both
policies use the same resampled cases in each replicate. Cost intervals
resample only the cases with known prices for both policies. Abstentions count
as incorrect for all-case accuracy. The seed defaults to `20260925` and the
resample count to `2000`; set `--bootstrap-seed` and
`--bootstrap-replicates` to record deliberate alternatives. Interval endpoints
use nearest-rank percentiles.

These intervals describe case-sampling variability in the supplied frozen
rows. They do not account for label disagreement, dataset shift, or model
variation across repeated calls for the same case. Resample at the independent
unit of the study; if cases cluster within sessions, users, or tenants, a
case-level bootstrap understates that dependence and a cluster bootstrap is
needed. Cost intervals and deltas apply only to jointly priced cases; when
some called stages are unpriced, they do not represent whole-workflow cost.
Optional `input_tokens`, `output_tokens`, and `total_tokens` are summarized by
stage only when the capture supplies them. The example's six invented rows
exercise the calculation only: its intervals are mechanics checks, not
evidence about a router, fallback design, model, or price.

## Reading a result

- Credit a router only for incremental improvement over both a no-router
  ablation and the best single-model or deterministic baseline. A router that
  selects similar work but adds cost has not shown value.
- Treat paired wins/losses as an error-localization aid. The bootstrap
  interval adds case-sampling uncertainty, but does not certify a result or
  choose a release threshold. Preserve the frozen held-out sample and inspect
  consequential disagreements.
- For a conditional route, verify that the recorded stages match actual branch
  execution. Zero-call stages are allowed to document an unchosen branch; they
  must carry zero cost and latency.
- Supply end-to-end wall latency directly. Summing stage durations is invalid
  when requests overlap or queue concurrently. Record stage durations for
  attribution, and end-to-end latency for user experience.
- If comparing a replay assembled from separately captured model outputs,
  label it counterfactual. Any serial sum of those request latencies excludes
  route computation, queueing, and production overhead; do not present it as
  measured live-cascade latency.
- Record human review workload even when no monetary price is available. A
  model cascade that shifts work to reviewers is not cost-neutral.
- Preserve invalid output, timeout, and provider failure cases in the trace.
  Record their cost and latency and use null decision if no valid final answer
  was produced.

This script validates accounting structure and summarizes supplied decisions;
its case bootstrap cannot validate labels, confirm that the trace reflects
runtime behavior, or establish production economics. Use a
frozen, privacy-safe held-out set and inspect consequential disagreements
before deciding whether to adopt, shadow, investigate, or reject a route.

For rubric judging, read [rubric-judge research](rubric-judge-research.md)
when testing scale placement or whether a fallback corrects shared errors.
