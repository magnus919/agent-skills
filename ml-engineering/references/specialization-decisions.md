# Choose the smallest sufficient model and adaptation method

Use when a request says fine-tune, specialize, train a local model, replace a
service with an LLM, or use RL for a domain problem. The user's desired outcome
is the requirement; the named architecture is a candidate. This guide owns
comparison design and evidence interpretation; `unsloth` owns supported local
training operations. Sources are dated in `references/specialization-evidence.md`.

## Start from the output and information requirements

Identify the decision or artifact: binary/class choice, calibrated probability,
ranking, extraction, generated text/code, or multi-turn actions. Describe exactly
what the system sees at prediction time, which labels arrive later, the tolerated
errors and resource budget. A risk label is not itself a probability; a long
reasoning trace is not evidence that reasoning is necessary. Test incremental
value over the current system, not whether a model can imitate its labels.

| Problem shape | Baselines worth testing | More complex candidate when warranted |
|---|---|---|
| Structured/tabular risk prediction with labels | Rules, logistic regression, gradient-boosted trees | Sequence/tabular models, text-aware fusion, decision heads |
| New natural-language label set without task labels | NLI zero-shot classifier, embedding prototype/class similarity | Generative prompt baseline, collected labels plus supervised classifier |
| Stable text categories with reviewed labels | TF-IDF/linear classifier, encoder classifier, embedding plus linear head | Adapted decision model or generative model if it adds value |
| Structured extraction | Parser/schema rules, constrained extraction model | SFT for missing task behavior, with exact field-level scoring |
| Knowledge missing or changing | Retrieval with grounding and a prompt control | Adaptation when behavior, not just facts, is the limiting issue |
| Function/code generation or repository repair | Strong untuned model with fixed harness, retrieval/prompt control | Reviewed SFT, then optional verifier-based RL |
| Subjective style/preferences | Prompt/style examples and reviewed preference evidence | DPO/other preference optimization with separate correctness checks |

A classifier baseline must receive comparable permitted information. Comparing an
LLM given recent sequence history to a classifier denied that history tests input
representation as well as architecture. Separate feature/context ablations from
model comparisons; include the incumbent rules/ML stack and its incremental
review layer. Temporal aggregation, sequence encoders and learned text features
may provide context without autoregressive text generation.

The [tabular benchmark](https://arxiv.org/abs/2207.08815) supports strong tree
baselines on its medium-sized datasets. The
[Booking.com fraud study](https://arxiv.org/abs/2405.13692) reports benefits from
self-supervised tabular transformers over its GBDT setup. Neither proves which
model wins on Coinbase's unavailable dataset. Broad claims such as "a zero-shot
classifier would be better" remain hypotheses until the matched comparison exists.

## Zero-shot classification is a specific contract

[Yin et al.](https://aclanthology.org/D19-1404/) formulate text labels as entailment
hypotheses. The [Transformers pipeline](https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.ZeroShotClassificationPipeline)
uses a sequence-classification model trained on NLI: input text is the premise
and each candidate label is rendered into a hypothesis. Label wording/template,
long-input truncation, domain shift and number of candidates affect behavior and
cost. Candidate labels are not a trained payments-risk probability head.

In single-label mode scores are normalized across candidates; adding/removing a
candidate can change them. Multi-label mode compares entailment and contradiction
for each candidate separately. Neither output is automatically a calibrated
fraud probability. Distinguish "zero-shot" meaning no task-specific labels from
in-context/few-shot classification, a supervised classifier and a generative LLM
returning a label. NLI models still have pretrained weights and a training history.
For numerical/time-dependent fraud patterns, textual entailment may omit the
needed signal; verify representation and source/time leakage before adoption.

Route decision-head/typed-output execution through `unsloth` and `system-one` as
appropriate; probability calibration/experimental analysis through `data-scientist`.
Do not create a new skill just to wrap a zero-shot pipeline. Classifier training
is already part of ML engineering; named tool runbooks belong in their tool skills.

## Task-specific inference and the CDM announcement

The [ScaleDown announcement](https://x.com/neal_k_patel/status/2109978626124898587)
provides another architecture hypothesis: specialize inference for classification,
span extraction or summarization rather than ask one autoregressive generalist to
serve every workload. Treat “Constrained Decoding Model” as the vendor's product
term until implementation evidence establishes the underlying mechanisms. It is
not automatically equivalent to token-level JSON/grammar-constrained decoding,
an NLI classifier, an embedding scorer or our local decision-head trainer.

The inspected [classify contract](https://docs.scaledown.ai/api-reference/classify-overview)
uses rubric-defined labels and softmax-normalized scores. It also offers a
Jev-compatible Decisions API over the same scoring model. Compatible request
shape does not preserve calibration, abstention behavior, latency or thresholds.
Test each question's semantic contract and probability behavior independently;
route existing typed-decision integration work to `system-one`, not a new wrapper.

The [extract contract](https://docs.scaledown.ai/api-reference/extract-overview)
returns described entity spans with offsets, context and scores; categorical
schema fields can route to classification. Evaluate exact source-span/offset
agreement, missing or invented entities, overlapping labels, schema correctness,
OCR/source identity for images and downstream false-negative harm. For redaction,
a valid JSON response is not proof that all sensitive spans were found. A score
or context snippet is evidence to inspect, not automatically a grounded citation
or calibrated confidence. Compare parsers, NER/encoder extraction and a generative
structured-output baseline on the same documents.

The [summarize contract](https://docs.scaledown.ai/api-reference/summarize-overview)
explicitly describes an abstractive rewrite, with tuned/fixed sampling parameters.
That establishes the advertised output contract, not a non-autoregressive
implementation. Compare an extractive or task-specific summarizer with a general
LLM using salient-fact retention, false/invented claims, source support, length,
latency/cost and downstream task outcomes. Context compaction must preserve the
information needed by the downstream decision/agent; shorter input alone is not
an improvement. Image/PDF input adds a separate OCR/vision evidence boundary.

The post's calibration, context, cost/speed and DecisionBench scores are vendor
claims, not measured here. The [Vercel provider listing](https://vercel.com/ai-gateway/models/providers/scaledown)
can corroborate catalog presence, not production compatibility or quality. Do not
infer downloadable open weights, fine-tuning access, offline/local execution or
GPU-only operation from a hosted API. No provider calls, private-data uploads or
new service integration were performed. Add a named operational skill only after
its actual API/version/privacy/rollback workflow is required and validated.

## Interpret Coinbase as three experiments, not one conclusion

Part One measures an added selective contextual-review layer over an existing
risk stack. Part Two compares LLM versions on historical replay. Part Three
compares a post-trained open-weight LLM to its base and a frontier LLM, and
separately compares online serving latency. These do not establish superiority
over a zero-shot, supervised, boosted-tree or sequence classifier with matched
context. Post-training success does not prove every backend service should
become a language model.

Pre-intervention historical cohorts help avoid outcomes censored by the deployed
agent's own blocks. Delayed fraud labels need a maturity window. Sampling legitimate
traffic changes prevalence: report PR curves, recall at a fixed false-positive or
review budget, calibrated probabilities where used, value-weighted exposure and
blocking harm, not only F1 or unadjusted replay precision. Group transactions by
user and respect prediction-time information cutoffs. Fit thresholds/calibration
on development/calibration data, not the final outcomes.

## Select the training objective from the failure

LoRA is parameter-efficient adaptation, not an objective. SFT learns reviewed
examples; GRPO optimizes sampled outputs against relative rewards; preferences
optimize a comparison signal; continued pretraining adapts token prediction to
a corpus. Prefer the simplest route that addresses a measured failure.

[SWE-Gym](https://arxiv.org/abs/2412.21139) and
[SWE-smith](https://arxiv.org/abs/2504.21798) support runnable tasks and agent
trajectory data for specialization. Their environment/harness and sampling are
part of the system. [DeepSWE](https://www.together.ai/blog/deepswe) reports an RL
agent at 32B with substantial GPU resources; its test-time-scaled score is not
its single-attempt score and its resource regime is not local consumer training.
Start with reviewed SFT for tool/output consistency when needed; RL is a candidate
when task truth can be checked and the policy produces useful reward variation.

[SFT vs RL](https://arxiv.org/abs/2501.17161) reports better RL generalization
in arithmetic-rule and visual-navigation tasks, with SFT useful for format
stabilization. That is not a universal coding comparison. The
[RLVR limit study](https://arxiv.org/abs/2504.13837) reports improved low-k
sampling efficiency but weaker high-k coverage in its settings, while
[Wen et al.](https://arxiv.org/abs/2506.14245) challenge that interpretation using
additional reasoning-aware metrics and different training/evaluation conditions.
Reasoning judges add their own error. Preserve the disagreement; benchmark the
actual task under fixed attempts and budgets instead of promising new capability.

[LoRA retention research](https://arxiv.org/abs/2405.09673) reports lower forgetting
alongside learning tradeoffs and hyperparameter sensitivity. Preserve a broad
regression suite and tune on development data. QLoRA reduces frozen-weight memory,
not activations or all optimizer state; paged optimizers may use host memory.
Hardware feasibility is an observed representative workload, not vendor arithmetic.

## Design a falsifiable comparison

Use `templates/specialization-study.md`. Before candidate outcomes exist freeze:

1. task roster, independent source groups, temporal cutoffs, labels/permission;
2. incumbent, simple classifiers/rules, prompt/retrieval controls and trained
   candidates, with comparable information and explicit policy differences;
3. model/artifact/tokenizer revisions, environment/harness/verifier hashes,
   label set/thresholds, generation/tool/attempt budgets and timeout policy;
4. primary quality threshold, critical regressions, operational resource ceilings,
   sample sufficiency/uncertainty method and stopping rules;
5. training/development/calibration/final split roles and checkpoint selection;
6. whether comparisons isolate weights, representation, policy or whole systems.

For coding, score independent executable tests and preserved existing behavior;
for classification, measure appropriate precision/recall/calibration at agreed
cost/decision constraints. Report per-task paired gains/losses and per-segment
regressions, not just an aggregate. Account for verifier false acceptances, failed
execution and missing reports. Timeout consumes budget and is an operational
failure; infrastructure errors are incomplete evidence rather than task truth.
Never discard unresolved tasks to improve the score.

Compare pass@1 to pass@1 and matched-budget best-of-k to best-of-k. A larger k
with a learned selector is a different system from a single pass. Repeated training
seeds and generation seeds address different uncertainty. Shared repository/task
families are dependent; group bootstrap by the unit of independence, not individual
near-duplicate examples. Small or unrepresentative sets support pilot decisions
only. Document multiple comparisons and avoid selecting the best noise spike.

## Saved-receipt comparison helper

`scripts/compare_task_runs.py` compares one attempt per task from two pinned JSON
records without generating text, running tests or accessing the network. Each
record declares `schema_version: 1`, lowercase 64-hex artifact/dataset/harness/
decoding/budget hashes, an explicit `expected_case_ids` roster, and task cases:

```json
{"id":"repair-1","group_id":"repo-family-a","status":"passed","critical_failure":false,"latency_seconds":1.2}
```

Status is `passed`, `failed`, `timeout`, `infrastructure_error` or `not_run`.
Incomplete statuses require null latency; completed/timeout cases require finite
nonnegative latency. Complete synthetic records are in
`templates/task-run-baseline.json` and `templates/task-run-candidate.json`.

```bash
python3 scripts/compare_task_runs.py baseline.json candidate.json --bootstrap 2000
```

Dataset, harness, decoding and budget pins must match; artifact hashes may differ.
Both expected rosters must match and all cases must appear exactly once with the
same groups. Missing tasks, incomplete execution or unequal comparison pins yield
inconclusive status and exit 1. Exit 2 is invalid CLI arguments. Complete comparison
exits 0 regardless of improvement or critical failures: **it is not a release gate**.
It reports solve rates (timeouts remain in the denominator), paired gains/losses,
critical failures, P50/P95 complete-task latency and a descriptive paired group
percentile-bootstrap delta interval. One group leaves uncertainty unassessed.

The helper trusts supplied hashes, outcomes and group labels; verify original
harness logs and manifest binding separately. It cannot detect false receipt claims,
pretraining contamination, judge errors, uncaptured costs, repeated-seed variance,
or permission violations. Latency summaries include timeouts and must not be
presented as successful-completion latency. Use separate per-status telemetry and
actual cost/VRAM/resource logs for an acceptance decision.

## Promotion and finish

Keep structural tests, executed runtime stages, task metrics and release approval
separate. A receipt audit clears consistency only; an eval manifest is not executed
quality evidence. A local training scaffold remains not run until hardware-tested.
Preserve rejected/inconclusive outcomes. Hold promotion if any required guardrail,
lineage link or final task roster is unresolved, even when average quality improves.
After merge/quantization, repeat independent task scoring in the target runtime.
Finish with a sourced decision, measured comparison and limitations; training and
serving execution route to `unsloth`, `llama-cpp` and `vllm`.
