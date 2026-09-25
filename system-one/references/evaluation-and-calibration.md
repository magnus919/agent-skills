# Evaluation and calibration

Use this reference before enabling automatic action or comparing Jev with Laya
or another open candidate.

For an initial cross-model label-selection screen, use the portable synthetic
[decision battery](decision-battery.md) after completing its
[design review](../templates/decision-battery-design-review.md) on a small pilot.
Confirm whether the target count means distinct scenarios, question judgments,
or requests before expansion. Its author-assigned labels do not replace the
independently labeled target-data evaluation described below.

## Worked offline binary evaluation

`scripts/evaluate_noul.py` consumes frozen Noul probabilities and independently
assigned binary outcomes; it never calls a model. Try the synthetic fixture:

```bash
python3 scripts/evaluate_noul.py --cases examples/noul.synthetic.jsonl --threshold 0.8
```

Expected overall result: six cases, two accepted, no false accepts. This is a
mechanics check, **not** evidence for a `0.8` threshold or Jev/Laya quality.
The output includes Brier, log loss, a constant-base-rate Brier comparator,
coverage, accepted precision, false accepts, and per-slice results. An empty
accepted set reports precision `null`, not perfect precision. For real use,
store one JSONL row per held-out case with unique `id`, `probability`, `label`
(`0`/`1`), and optional `slice`; exclude raw personal data. Fit any threshold
or probability mapping on a separate calibration split, freeze it, then run
this script on a test split that was not used for tuning. Inspect false
accepts individually and add a confidence interval before a high-impact
release; six synthetic cases cannot estimate tail risk.

## Build the evaluation set

Use a versioned, representative set of real-shaped but privacy-safe cases:

- common cases and the long tail;
- ambiguous, missing, contradictory, negated, adversarial, and out-of-domain
  cases;
- every answer class including `other`/`unknown`/review;
- language, tenant, channel, and data-shape slices that the deployment sees;
- human labels with disagreement/abstention retained rather than forced into a
  false single truth;
- a frozen test split that is not used for rubric, threshold, temperature, or
  prompt tuning.

Never send the expected label to a live provider as part of state or question
text. Keep evaluation fixtures synthetic or approved for external processing.

## Metrics

Report metrics by primitive and risk lane:

- Choice: accuracy, macro-F1, confusion matrix, top-k if relevant, selective
  accuracy by coverage, and cost per accepted decision.
- Noul: Brier score, log loss, AUROC/PR-AUC only as descriptive ranking
  measures, and precision/recall at the actual policy threshold.
- Score: expected-value MAE, ordinal accuracy/within-one, ranked probability
  score, and calibration by level.
- Probabilities: reliability diagram, ECE with bin details, Brier/log loss,
  worst-slice calibration, and abstention/coverage curves.
- Operations: cold and warm latency p50/p95/p99, queue time, throughput,
  memory, error/fallback rate, provider cost or local resource cost.

Accuracy alone hides whether a 0.95 answer is actually right 95% of the time.
Calibration alone can reward a model that is cautious but useless. Keep both
quality and action-coverage evidence.

## Threshold selection

Treat each action as a cost-sensitive decision. A read-only route can use a
lower threshold than a destructive write, financial approval, safety block, or
external send. Choose thresholds on a calibration split, then lock them before
the final test. Consider three lanes:

```text
high evidence + permitted action -> automate
middle evidence or high-risk action -> confirm/review
low evidence, invalid, unavailable, or out-of-domain -> abstain/fallback
```

Do not use the top Choice probability as a universal confidence threshold when
the number of options, language, checkpoint, or class prior changes.

## Compare models fairly

Run byte-identical states/questions, the same option order policy, the same
labels, and the same policy code. Record whether Jev is a remote API and Laya is
local; latency and cost are not comparable unless network, warmup, hardware,
batching, and accounting boundaries are explicit. Do not compare a specialist
Laya checkpoint against Jev on a workflow that only one model trained on and
call it general superiority.

For app-control loops, also compare full **sequences**: wrong target, stale
action attempts, premature action on partial input, repeated no-progress
steps, `DONE` without independently satisfied goal, and cost per completed
task. A per-question accuracy number is not an end-to-end controller result.
For ranking, report shortlist recall before reranking and use labels not
generated solely by the candidate under test. Archive raw responses and the
exact model, question, policy, and artifact revisions; repeated calls on the
same prompt do not substitute for diverse cases.

Use deterministic baselines: majority class, lexical/rule baseline, embedding
shortlist, and current production behavior. A model that does not beat the
baseline at its intended coverage is not ready for automation.

## Calibration repair

Temperature scaling or another calibration map must be fit on held-out data,
versioned, and applied after the model logits/probabilities are produced. Fit
separately when evidence shows material differences by question type, option
count, language, or domain. Recheck calibration after model, rubric, label,
serialization, or preprocessing changes.

## Release gate

Require:

1. Frozen evaluation manifest and baseline results.
2. Target-slice quality, calibration, and risk-coverage evidence.
3. Shadow result review and known-failure list.
4. Threshold/policy review by the accountable owner.
5. Load, timeout, fallback, and rollback rehearsal.
6. Monitored rollout with a kill switch and reassessment trigger.

Use `templates/benchmark-record.md` to keep comparisons reproducible.
