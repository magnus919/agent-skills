# Portable System One decision battery

Use [the v1 synthetic fixture](../examples/decision-battery-v1.jsonl) for the original 48-case bounded label screen. It has eight cases each for handoff, customer intent, employee queue, urgency, observed task completion, and content policy. Keep it intact for historical comparisons.

Use [the v2 synthetic fixture](../examples/decision-battery-v2.jsonl) as a **provisional** cross-domain corpus: 50 distinct scenarios per domain, each with one Choice route, one binary Noul question, and one four-level Score question. That is 150 question judgments per domain and 1,800 judgments across 12 domains: software development, customer support, legal operations, healthcare administration, financial operations, cybersecurity, education, logistics, human resources, manufacturing, research, and public services. Do not equate 150 judgments with 150 independent scenarios. Every domain includes easy, medium, and hard cases. The Score rubric counts three explicitly named evidence fields (0–3), avoiding unstated professional judgment. Cases include stale context, quotation, negation, competing topics, missing data, and explicit escalation cues. The `rationale` field explains each provisional answer; it is **never sent to the endpoint**. These are controlled fictional administrative cases, not legal, medical, or financial advice.

## Design review checkpoint

Before expanding or treating either fixture as comparative evidence, complete [the design review](../templates/decision-battery-design-review.md). State whether the requested count refers to **scenarios, questions, or requests**; define the expected answer and ambiguity rule for every primitive; and review a small varied pilot with the people accountable for the domain. Check satisfying, contradictory, and missing-evidence examples against the rubric and exact endpoint payloads. Stop expansion when the count, oracle, or reviewer labels are unresolved. Freeze the accepted rubric and pilot IDs before generating variants; keep a later independently labeled holdout separate from cases used to revise prompts or thresholds.

## Run and compare

From the skill root, run a GLiNER-style adapter with a `POST /classify` endpoint accepting `{"text": "...", "heads": {"task": ["label", ...]}}` and returning `{"result": {"task": "label"}}`:

```sh
python3 scripts/decision_battery.py --cases examples/decision-battery-v1.jsonl \
  --endpoint http://HOST:8091 --output /tmp/model-predictions.jsonl
```

For Jev, use the exact hosted System One POST URL and an environment variable containing the TypeSafe key:

```sh
python3 scripts/decision_battery.py --cases examples/decision-battery-v1.jsonl \
  --adapter systemone --endpoint https://api.typesafe.ai/v1/systemone \
  --api-key-env TYPESAFE_API_KEY --model jev-latest \
  --output /tmp/jev-predictions.jsonl
```

For the repository's Laya HTTP service, use its exact `/v1/systemone` URL and service token:

```sh
python3 scripts/decision_battery.py --cases examples/decision-battery-v1.jsonl \
  --adapter systemone --endpoint http://HOST:8092/v1/systemone \
  --api-key-env SYSTEM_ONE_SERVICE_TOKEN \
  --output /tmp/laya-predictions.jsonl
```

For v1, the System One adapter sends a separate Choice question for each case. It uses the same text and ordered labels as the GLiNER adapter, with `{label: label}` Choice criteria because Jev requires a criteria object. Its fixed instruction adds only the task name and asks for one of those labels. This is a matched **label-selection screen**, not identical model inputs: native schemas and preprocessing differ. It validates the full typed response before recording the selected label. The v1 label score does not evaluate probability calibration. Never print or save bearer tokens.

For another decision model, write one JSONL row per case with `{"id":"handoff-01","answer":"yes"}`, then score it without an adapter:

```sh
python3 scripts/decision_battery.py --cases examples/decision-battery-v1.jsonl \
  --predictions /tmp/other-model-predictions.jsonl
```

Add `--compare-predictions /tmp/second-model-predictions.jsonl` to print paired counts and every case where the labels differ. The runner never sends expected labels. It reports exact-label accuracy by task and slice, missing/invalid answers, handoff false negatives, case-level misses, and observed client latency. Preserve raw prediction files, model and runtime revisions, exact input serialization, device, warmup, and endpoint topology **outside the repository** using `templates/benchmark-record.md`; add results to a publication only on an explicit request. Keep the same cases, labels, order, and policy interpretation; record model-specific serialization in the adapter. Do not turn a class string into an invented probability. Use `scripts/evaluate_noul.py` only when a model actually returns probabilities and independently assigned binary outcomes are available.

For v2, replace `decision-battery-v1.jsonl` with `decision-battery-v2.jsonl` in those commands. The runner sends the three questions for one scenario in a single request. A v2 GLiNER head carries the authored question as its `prompt` and the four or fewer labels as `labels`. A v2 System One request uses the native `choice`, `noul`, or `score` question type. The diagnostic answer for Noul is the probability projected at 0.5; the diagnostic answer for Score is the highest-probability level. The saved prediction also retains the native Noul probability or Score expectation and level probabilities. The report separates exact-label rates by domain, difficulty, and primitive; counts scenarios with all three correct; and, for typed endpoints only, reports Noul Brier score and Score mean absolute error. GLiNER supplies labels only, so its typed metrics remain empty. These projections support a common case-level screen; they do not make the models' native outputs equivalent or establish calibration.

Each prediction records a shared `request_id`, group size, client request latency, and server latency when the endpoint supplies it. The live report counts each batched request once for client and server latency min/p50/p95/p99/max, and records end-to-end wall time, request count, cases per second, and requests per second. Runs are sequential. Compare latency only with the same client host, endpoint topology, batch shape, model warm state, and concurrency; hosted Jev includes network time that LAN models do not. Save the report alongside predictions because raw prediction rows cannot reconstruct total run wall time.

## Interpret the labels

The expected labels are author-assigned synthetic examples, **not** independently adjudicated ground truth. Some boundaries, especially urgency and policy labels, need a written organization-specific rubric and at least two independent reviewers before they become release evidence. Preserve disagreement and allow a review lane instead of forcing consensus. Do not tune a model, prompt, label wording, or threshold on these cases and then claim the same set as held-out evidence. Version new cases and keep existing IDs stable so comparisons remain interpretable.

The v2 fixture is generated by [`scripts/build_decision_battery_v2.py`](../scripts/build_decision_battery_v2.py). Review or edit its 50 authored seed scenarios and domain-specific combinatorial patterns before regenerating; regeneration overwrites the v2 JSONL. The 1,800 judgments are **not 1,800 independent situations**: three questions share each of 600 scenarios, and generated cases reuse controlled patterns. Report both per-question and all-three-correct per-scenario results. A high aggregate score can hide a weak primitive or domain. Treat prompt wording and the 0.5 Noul projection as fixed diagnostic settings, not calibrated deployment choices. The fixture has not passed the design-review checkpoint; review its rationales and ambiguous labels before using a subset as a release gate.

The battery deliberately includes explicit and negated handoff requests, repeated failures, ordinary requests, quoted instructions, multiple intent classes, an `other` route, task completion versus attempts or drafts, and policy text that mentions harmful concepts in a benign context. Evaluate high-cost errors separately: a handoff false negative, a missed critical incident, or a mistaken allow/block can matter more than an equal number of ordinary routing misses. A correct class label still does not authorize an action.

For production adoption, collect privacy-safe, representative real cases with independently assigned labels; split calibration and final test sets; measure class balance, disagreement, selective coverage, and downstream outcomes. Expand this battery with multilingual, multi-label, high-cardinality, and probability-calibration suites only when the candidate's declared contract supports them. The v1 battery is English and single-label.
