# Strands Decider: experimental local typed judgments

Checked 2026-10-04. Strands Labs announced this experimental contribution on
2026-10-01. It is a separate project from Mapika's Decider family. Investigate
it for a small local Choice/Noul/Score pilot, not as an established replacement
for Jev, Laya, or a generative reasoning model. No head-to-head quality win,
production SLA, or universal confidence threshold is established here.

## Pin the implementation and artifact

This profile checks official source at
[`75c9fd3`](https://github.com/strands-labs/strands-decider/tree/75c9fd32e664954cdc18481434018aa507eee8fb)
and `StrandsAgents/strands-decider-2B-hobson-v19` at
[`bb282d7`](https://huggingface.co/StrandsAgents/strands-decider-2B-hobson-v19/tree/bb282d786bc251fd4e3068de3ada9ddbb38127cd).
The Apache-2.0 adapter uses `Qwen/Qwen3.5-2B-Base`, about 1.9B parameters,
rank-16 LoRA and a roughly 1M-parameter pointer head. It discards the language
model's generation head: an answer-position query scores option-token hidden
states in a forward pass. It does not generate an explanation or free text.
Inspect code, adapter, base, dependencies, and dataset terms independently.

The export's base revision is `b1485b2fa6dfa1287294f269f5fb618e03d52d7c`;
upstream provenance says this is **inferred** from training-time Hub main,
not a verified training-time pin. Record that uncertainty. Use the safetensors
export and its manifest checks (`python -m strands_decider.hf_export verify
<checkpoint-directory>`); do not enable remote code or deserialize an
untrusted legacy pickle to reproduce this profile.

[PyPI 0.1.0](https://pypi.org/project/strands-decider/0.1.0/) and the checked
Git source are different feature snapshots. The 0.1.0 wheel has `train` and
`dev` extras but no vision module or request `images` field. Current-source
vision and device extras must not be attributed to that wheel. Follow the
pinned source's [inference guide](https://github.com/strands-labs/strands-decider/blob/75c9fd32e664954cdc18481434018aa507eee8fb/docs/inference.md)
and lock the actual serving dependencies before installation or use.

## Native decision contract

The pinned [schema](https://github.com/strands-labs/strands-decider/blob/75c9fd32e664954cdc18481434018aa507eee8fb/src/strands_decider/schema.py)
accepts state plus named typed questions. Keep native question instructions
in the question, not transplanted into state to hide a compatibility failure.

| Primitive | Native meaning | Qualification requirement |
|---|---|---|
| Choice | 2–255 named options; argmax, normalized option probabilities, derived confidence | Preserve IDs, descriptions and option order; test missing-fit and permutations |
| Noul | P(true), with optional true/false criteria; no separate confidence field | Verify true/false polarity with counterbalanced evidence and changed questions |
| Score | 2–10 ordered levels; expected ordinal index, not a selected integer level | Preserve level order and index scale; verify probability-to-score mapping |

Choice confidence is `(N * p_max - 1) / (N - 1)`, the top probability's
rescaling relative to a uniform distribution. It is not a learned probability
of correctness. Score confidence derives from ordinal distribution spread,
with a correction for the head's ordinal smoothing; it is not Choice's formula.
Noul's probability likewise needs workload-specific calibration. Do not import
Jev thresholds or the upstream example action cutoffs into policy.

The HTTP server exposes `/v1/systemone`, but upstream explicitly says actual
Jev API compatibility is unverified. An unchanged JevBench adapter and matching
JSON shape do not establish semantic parity. Apply [comparison design](comparison-design.md)
before scoring: IDs, labels, polarity, scales, option coverage, response errors,
finite probabilities, and returned deployment identity must pass qualification.
The native server defaults to local loopback without authentication. Any
externally reachable adoption needs private authenticated ingress and bounded
requests/concurrency/deadlines before caller traffic.

## Context, batching, and images

The serving default is 4,096 tokens; the preregistered text evaluation uses
3,072. The 255-option schema ceiling does not prove those descriptions fit or
that quality holds at that cardinality. In the pinned runtime, `strict_window`
defaults to false: the engine reserves question space, can truncate the front
of a question while keeping its tail, and truncates state to the remaining
budget. This can lose instructions, options, or decisive evidence.

Enable strict-window rejection for qualification: native overflow raises an
error, and the server returns 422. Test exact tokenized boundary behavior
before production; do not describe a silently shortened request as the same
contract. Shortlisting changes the candidate set, so measure recall and treat
probabilities as conditional on that shortlist.

Prefix caching is enabled by default, but the shared-prefix inference path
requires more than one question in a chunk. A singleton's timing does not
measure multiquestion sharing or batching throughput. Compare the exact
production request shape using [request-shape evaluation](request-shape-evaluation.md).

The pinned Git source's experimental `--vision` route adds a frozen ~331M
parameter tower (~0.66 GB BF16), up to four images, and a 448-pixel long-side
limit. Images share the 4,096-token window with text and question reserve.
A text-only server rejects images. This is a source-version feature, not a
0.1.0 wheel guarantee. The v19 adapter was text-trained; small upstream vision
comparisons do not establish general image robustness. Qualify image evidence,
preprocessing and context separately; the local smoke below did not test vision.
See the pinned [vision guide](https://github.com/strands-labs/strands-decider/blob/75c9fd32e664954cdc18481434018aa507eee8fb/docs/vision.md).

## Published limits: preserve them when a demo passes

The upstream [evaluation report](https://github.com/strands-labs/strands-decider/blob/75c9fd32e664954cdc18481434018aa507eee8fb/evaluation/README.md)
reports weak question sensitivity: with state/options fixed, approximately
94% of answers stay unchanged when the question changes. A negated question
such as “which does this NOT fit?” often gets the positive interpretation.
It also reports 61.4% for novel Noul tasks and 49.9% for an unseen Score rubric.
Use these as failure hypotheses, not target-workload accuracy estimates.

The preregistered JevBench result is 167/231 (72.3%) at 3,072 tokens. The
repository reports 168 at 4,096, whereas the pinned model card reports 167;
probability metrics also differ between those reports. Preserve the source
and configuration instead of combining them into one result. These are small
public single-run evaluations, not a matched local comparison with Jev, proof
of equivalence, or a production reliability claim. One temperature per
primitive can drift across domains; independently qualify calibration.

## Scoped local smoke evidence

On 2026-10-04 an isolated RTX 5070 Ti pilot used the pinned source/model/base
above, Python 3.11.16, PyTorch 2.14.1, Transformers 5.18.0 and PEFT 0.21.2,
with PyTorch fallback kernels and strict-window rejection. No vision, training,
optimized CUDA kernels, serving load or head-to-head comparison was tested.

- Eight authored short scenarios, repeated three times: four Choice routes
  (billing, technical, no action, unknown) and four Noul down/restored
  availability judgments. All 24 expected labels passed. Separately, all 24
  parsed with matching options and valid probability ranges; Choice sums were
  within 0.001 of one. Noul's predeclared 0.5 diagnostic cutoff is not an
  approved production threshold.
- Four literal-NOT availability variants, repeated three times: all 12
  expected labels passed. They reuse two simple down/restored states, so they
  do not rebut the upstream arbitrary-question failure results.
- Original inputs were 88–115 reported tokens. CUDA-synchronized host timing
  around sequential singleton `engine.ask` calls: warm median 27.07 ms,
  range 26.57–28.14 ms over 16 calls after excluding the first eight. First
  inference was 1,927 ms; loading and downloads are excluded from warm latency.
  Default prefix caching was configured, but singleton requests do not exercise
  the shared-prefix path.
- Peak PyTorch allocation was 3.621 GiB (reserved 3.678 GiB). This excludes
  other processes and some driver memory; it is not total-device peak usage.

These repeated authored diagnostics establish scoped compatibility and
feasibility, not independent held-out accuracy, calibration, throughput,
long-context quality, Score quality, or superiority to another model. Raw
private execution reports are not part of this skill's public corpus.

For adoption, freeze a small independently labeled target pilot first. Include
question-only counterfactuals, literal negation, missing-fit cases, option
permutations, long decisive evidence, context overflow, novel Noul tasks and
ordered Score rubrics. Separate development, calibration and untouched grouped
test cases. Report risk/coverage and fallback outcomes alongside quality,
client-boundary cold/warm latency, request shape and measured resources.
Use [decision-battery design](decision-battery.md) only after adapter and pilot
review; the bundled battery does not supply a qualified Strands adapter.

## Training is a separate qualification task

The [official recipe](https://github.com/strands-labs/strands-decider/blob/75c9fd32e664954cdc18481434018aa507eee8fb/training/README.md)
builds corpora, labels with a frozen Qwen3.5-4B teacher, trains a v14 parent,
relabels with replay, trains v19, calibrates and evaluates. Published timings
are ~11 hours on one 24 GiB RTX 3090 or ~1 hour 10 minutes on eight H100s via
the AWS runner. `FAST=1` belongs to `training/run_recipe.sh`, not `recipe.sh`;
these are reported configurations, not promises for another GPU.

Training requires its separately pinned Linux/WSL2 NVIDIA kernel environment;
the serving smoke's fallback dependencies do not qualify it. Frozen targets
join corpus rows by position: preserve `data/SHA256SUMS` checks, row order,
source/license provenance and evaluation splits. The recipe does not require a
paid labeling API, but still downloads base/teacher/data artifacts. A
nonsignificant difference is not evidence of statistical equivalence. Training
or production deployment needs its own authorized scope and validation.

## Primary sources

- [Official October 1 launch](https://strandsagents.com/blog/introducing-strands-decider/)
- [Pinned architecture](https://github.com/strands-labs/strands-decider/blob/75c9fd32e664954cdc18481434018aa507eee8fb/docs/architecture.md)
- [Pinned runtime context and caching behavior](https://github.com/strands-labs/strands-decider/blob/75c9fd32e664954cdc18481434018aa507eee8fb/src/strands_decider/infer.py)
- [Pinned model card](https://huggingface.co/StrandsAgents/strands-decider-2B-hobson-v19/blob/bb282d786bc251fd4e3068de3ada9ddbb38127cd/README.md)
