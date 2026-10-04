# System One model comparison design

Use this reference before comparing model providers, checkpoints, or end-to-end
adapters. It defines what the comparison can establish; use
`templates/benchmark-record.md` to preserve the protocol and results. It
complements `references/evaluation-and-calibration.md`, which covers calibration
and risk/coverage methods.

## Choose the question the experiment answers

Predeclare the comparison unit (for example, one decision judgment or one
complete task), target population, primary metric, meaningful difference, and
operational boundary. A result about model calls does not automatically answer
whether the application improved. Use one of two tracks:

- **Fixed contract:** send the same semantically identical state and typed
  question, criteria, answer labels, candidate set, and ordering policy to every
  candidate. This estimates relative behavior under that shared contract.
  Report unsupported or unfaithful mappings as compatibility failures; do not
  quietly rewrite a candidate's input and attribute the change to its model.
- **Model-adapted:** permit a separately designed and versioned adapter or
  question mapping for each model, chosen on development data. Fit any
  thresholds or probability calibration on a separate calibration split. Freeze
  these choices before final testing. Verify each mapping against the same
  target decision and compare the resulting model-plus-adapter systems.
  Attribute differences to the full system, since prompt, serialization, and
  adapter changes are part of the treatment.

Do not pool the two tracks into one ranking. A model that cannot express the
fixed contract may still be investigated on the adapted track, with that
limitation made explicit.

## Qualify the adapter before scoring the model

Adapters translate the application's state and typed contract into provider
requests, then translate responses back. First verify this boundary with small,
reviewed fixtures. Check question/answer ID preservation, Choice labels, Score
scale and direction, Noul semantics, option ordering, probability normalization
where required, omitted and extra answers, empty or malformed outputs, retries,
request batching, response parsing, and string normalization such as case
folding, whitespace, and Unicode. Exercise boundary-size inputs and explicit
overflow/truncation behavior. Confirm the returned model/checkpoint revision,
tokenizer, runtime, precision, and actual device when the comparison depends on
them. An adapter that drops candidates, changes meanings, substitutes defaults,
or maps unknown to a valid answer must fail qualification before the model
comparison.

If the adapter changes the fixed contract or fails a qualification vector, stop
the substitution comparison and report a compatibility failure. Repair and
requalify, or report the candidate as incompatible with that contract; do not
score its downstream predictions as if they were matched. Once an adapter is
qualified, count per-request runtime failures, malformed answers, timeouts, and
missing outputs in the operational coverage denominator.

Record adapter source and configuration revisions, exact payload serialization
hashes, and the qualification evidence. Test polarity with paired examples
whose correct decisions reverse while irrelevant wording is held stable. Test
both supported and rejected overflow cases. Include a vendor-documented example
request, a satisfying answer, a contradiction that reverses the right answer
despite a tempting keyword, and an answer missing evidence required by the
rubric. Check their serialized requests and parsed responses by hand. A
protocol-shaped response proves compatibility only; it does not prove semantic
parity or model quality.

For self-contained semantic boundary examples and judge-identity checks, use
[portable qualification probes](decision-qualification-probes.md). They are
illustrative fixtures, not a calibration set or production benchmark.

## Build a dataset that can answer the intended question

Define the sampling frame, target period, inclusion rules, unit, deduplication,
and exclusions before looking at candidate results. Keep a representative
sample for workload estimates and report deliberately risk-enriched challenge
cases separately. Preserve enough provenance to explain what the target set
represents without publishing sensitive records.

Write an answer rubric before labeling. Blind reviewers to model identity,
outputs, and predictions when feasible; retain source evidence, disagreements,
adjudication, and an explicit unknown/unanswerable lane. Have reviewers assess
satisfying, contradictory-near-miss, and missing-evidence examples before
expanding the set. Statistical methods quantify uncertainty in labels and
samples; they cannot make weak or disputed domain labels authoritative. Record
whether the correct answer is already exposed in the state, metadata, retrieval
result, identifier, ordering, timestamp, or template. Probe these possible
shortcuts with counterfactual or ablation checks. A high score can reflect
leakage or a shortcut rather than the intended judgment.

Use challenge examples to make the rubric observable. For example:

| Review dimension | Satisfying evidence | Contradictory near miss | Missing evidence / correct treatment |
|---|---|---|---|
| Polarity | “I cannot access my account” supports an access-help route. | “I can access my account now” contains the same access phrase but should not route as an unresolved access problem. | “I need help” lacks the access detail; return unknown or review if the contract requires that evidence. |
| Fixed contract vs adapted | Both candidates receive the same decision meaning, criteria, and labels through their declared adapters. | A candidate receives reworded criteria or a shortened option list and is ranked as if it were a drop-in substitution. | If an API cannot express the contract, record incompatibility or test separately on the adapted track; do not infer equivalence. |
| Train/test overlap | Candidate succeeds on a source-group-held-out case absent from all tuning and selection data. | A near-duplicate from the same source family appears in prompt/model selection, then the test score is claimed as untouched evidence. | Opaque training overlap is unknown; disclose it and avoid claiming verified decontamination. |
| Equivalence inference | The paired interval lies wholly inside a justified, prespecified equivalence margin. | A test returns p = 0.30 and the report declares the models equal. | The interval is wide or data are too sparse to decide; report inconclusive, not equivalent. |

These are rubric-design illustrations, not benchmark cases or evidence that any
model passed them. Keep the criterion and examples versioned with the evaluation
contract.

Keep related observations together when splitting: the same user, document,
conversation, task, template, near-duplicate, or time sequence can otherwise
leak between training and evaluation. Document separate membership for
training, model/checkpoint selection, prompt or adapter selection, threshold
tuning, calibration, and final testing. If the same labeled cases influence
selection and calibration, state that limitation and acquire a fresh test set
before making a confirmatory claim. Keep final-test labels and outputs hidden
until the analysis protocol is frozen. Count unanswerable cases, adapter
failures, missing outputs, and exclusions in the denominators rather than
silently dropping them. Mark training-data overlap as checked, disclosed, or
unknown; unknown provenance is not proof of no overlap. Keep exact validated
requests and responses, their hashes, model/adapter revisions, and validation
status in access-controlled storage outside the repository. Redact secrets and
minimize personal data.

Compare against the incumbent and relevant simple baselines, such as majority
class, a lexical/rule policy, or a length-only rule. Fit or select those
baselines on development data only. If final-test inspection reveals a trivial
shortcut, a baseline fit on those test rows (including cross-validation over
test rows) is diagnostic evidence of a dataset artifact, not a valid prospective
competitor; create a new artifact-controlled test before making a confirmatory
claim.

## Pair outcomes and quantify uncertainty

Pair candidates on the same decision units and retain a stable pairing key.
Choose the primary metric to match the decision: exact correctness, cost-weighted
error, ranking utility, calibration, coverage, or a task outcome. Report
counts, per-slice results, and uncertainty around paired differences. Preserve
all outcomes, including ties, abstentions, malformed responses, and shared or
unique errors. When multiple questions or records share a scenario, customer,
conversation, or source document, estimate uncertainty at that independent
source cluster rather than treating every judgment as independent. Repeated
calls measure response stability; they do not increase the number of independent
cases. A paired cluster bootstrap is one usable method when its assumptions and
sample size fit the design.

Report task-native quality, costly error types, invalid/missing/error rates,
abstention and coverage, and the policy's actual operating point. For
probability-producing primitives, add calibration and risk/coverage evidence.
Report stability separately from correctness, and include slice counts so a
high aggregate score does not conceal a risky failure lane.

A non-significant difference is inconclusive; it does not establish equality.
If the decision requires parity or non-inferiority, specify a practically
meaningful margin before seeing results, justify it with the accountable owner
and task costs, use a design with enough precision for that margin, and report
the interval against it. Claim equivalence only when a prespecified equivalence
procedure supports it. Predeclare how multiple candidates, metrics, slices,
and interim looks will be handled; otherwise label post-hoc selection
exploratory. Treat secondary slices as exploratory when the design does not
support confirmatory claims.

Run identical inputs more than once when stochastic or service variation
matters. Report within-model stability separately from correctness and
between-model differences. Pin decoding settings and distinguish sampling
variation, provider drift, infrastructure failures, and label disagreement.
Do not repeatedly tune on a known miss and then reuse it as held-out evidence.

## Measure the real timing boundary

State whether latency begins at the application call or at provider receipt and
whether it ends at the parsed decision or at the completed workflow. Identify
serialization, network transit, queueing, retries, fallback, human review,
validation, and action completion as included or excluded. Report cold start
separately from warm operation, and record region, concurrency, batch shape,
timeout, and measurement window. Compare like boundaries and include repeated
runs; a warmed inference-only number cannot stand in for end-to-end latency.
Report client end-to-end time, server-reported inference time, and queue time as
separate measures when available. Do not subtract a measured network round trip
from p95 or p99: network tail variation makes that subtraction unreliable.
Include sample counts with p50/p95/p99 and throughput, and measure under the
production-relevant load and hardware before making a capacity claim.

Keep decision-model quality and model-call latency separate from application
outcomes, trajectory, side effects, and full workflow cost. Route full agent
task comparisons to `agent-evals-and-observability`.

## Source basis and limits

The test-selection guidance follows [Dror et al., ACL 2018](https://aclanthology.org/P18-1128/),
which explains that the valid significance test depends on task and metric.
The warning about treating a null result as equivalence follows [Lakens et al.,
2018](https://doi.org/10.1177/2515245918770963); a useful equivalence bound
must be justified for the task, and that work gives no universal model-quality
margin. NIST's [AI Technology Evaluation program](https://pages.nist.gov/ai-technology-evaluation/)
describes blind, sequestered data as one way to reduce train/test contamination.
LLM benchmark contamination and limits on measuring it are discussed in
[Sainz et al. (2023)](https://arxiv.org/abs/2310.18018) and [Li et al. (2024)](https://aclanthology.org/2024.findings-emnlp.30/).
The [MLPerf Inference rules](https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc)
illustrate why latency claims need a declared sample unit, scenario, and
quality/service boundary.

The fixed/adapted comparison split, adapter checklist, three-way reviewer
packet, retention advice, and operational gates here are recommendations for
this skill, not prescriptions uniquely established by those sources. Domain
owners still need to judge whether the rubric captures the real decision. As
secondary inspiration, [LangWatch's Jev comparison](https://langwatch.ai/compare/jev-vs-all)
reports development-set tuning, truncation, training disclosure, and
hardware-specific latency, while also noting that labels were not re-reviewed
and trivial baselines were cross-validated on test items; treat it as a case
study, not independent methodological authority.

## Keep evidence bounded

A benchmark record should let another reviewer identify the exact data split,
label rubric, contract, model, adapter, request bytes, runtime, timing boundary,
analysis choices, and exclusions. Keep sensitive raw inputs and outputs in
access-controlled storage; put hashes and redacted artifact locations in the
record. A synthetic fixture can test the harness and adapter contract, but it
cannot establish target-workload quality. Vendor and secondary-source results
can nominate candidates and hypotheses; verify capabilities from primary
artifacts and evaluate them on the intended task before adoption.

## Eval challenge mapping

The skill's v1 evals include focused cases that exercise the review boundaries
above. For semantic assertions, reviewers should distinguish a response that
shows the required evidence, a contradiction that chooses the wrong behavior,
and an answer that omits the evidence; these cases are manual-review contracts,
not validated model passes.

| Case ID | Revision focus | Satisfying evidence | Contradictory near miss | Missing-evidence result |
|---|---|---|---|---|
| `calibration-review` | Existing rubric extended for grouped source splits and shortcut probes | Related conversations stay in one partition; source IDs are tested as possible label leakage | Duplicate source groups cross the split or the ID shortcut remains after claiming target quality | Report contamination and require a fresh holdout rather than claim independent calibration |
| `rubric-study-comparison-boundaries` | Existing rubric extended for paired uncertainty, stability, multiplicity, and timing | Uses account/task clusters, an explicit equivalence procedure, repeated-run stability, and the stated timing boundary | Treats repeated calls as new independent cases or calls a non-significant result equivalent | Leave parity and fastest-model claims unresolved without a margin, uncertainty, or timing boundary |
| `comparison-track-separation` | New fixed-contract versus adapted-system comparison | Keeps the fixed semantic contract separate from an equally developed adapter comparison on common held-out cases | Pools tailored prompts with the fixed-contract ranking or tunes on final labels | State that attribution or ranking is unsupported until track and test split are specified |
| `adapter-polarity-and-overflow` | New adapter qualification boundary | Reverses the decision under counterbalanced evidence and handles the exact option boundary explicitly | Returns valid JSON while flipping labels or silently truncating options | Reject model scoring until adapter qualification evidence exists |
