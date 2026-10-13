# Decision models: a separate training and serving path

Research checked 2026-10-12. Documented/source-inspected; GPU training, calibration
and Decision API execution **not run**. The validated text-SFT stack does not
establish compatibility here. Sources: [training guide](https://unsloth.ai/docs/new/train-your-own-decision-model-with-unsloth),
[serving guide](https://unsloth.ai/docs/models/decision-laya), and
[original Clef architecture](https://blog.cloudflare.com/clef-decision-models/).

## Select the right objective

Use this path to return choices, yes/no probabilities or ordinal scores from a
state and question schema. Converting an LLM uses a trained Clef-style head;
asking a chat model to emit JSON is a different mechanism. A public decision
model such as Laya, a converted Qwen backbone, and hosted Jev need separate
baselines. API-shaped compatibility does not establish equivalent probabilities,
context handling, confidence, calibration or task accuracy.

For Jev input/rubric tuning, route to `agent-evals-and-observability` rather than
silently starting weight training. Do not train on Jev suggestions as if they
were independently labeled truth. Preserve reviewer provenance for any labels.

## Prepare three independent splits

A conservative hard-label training row looks like:

```json
{"group_id":"invoice-4411","state":"Invoice 4411 was charged twice; refund today.","questions":{"team":{"type":"choice","instructions":"Which team owns this?","criteria":{"billing":"Payments and refunds","technical":"Bugs and outages"}},"refund":{"type":"noul","instructions":"Is a refund requested?"},"urgency":{"type":"score","instructions":"How urgent?","criteria":["routine","soon","today"]}},"gold":{"team":"billing","refund":true,"urgency":2}}
```

`gold` answers are option keys for choice, booleans for noul, and zero-based
integer levels for score. A request can contain several questions. Upstream also
supports soft targets and JSON-string columns; the bundled helper deliberately
supports only object-valued rows with hard labels and string states. It rejects
other shapes rather than pretending to validate them.

Split source/customer/conversation groups before deriving rows. Keep training,
calibration and final test files separate. The upstream `split_holdout` groups
items by original row, not by semantic source identity, and a tiny dataset can
produce an empty holdout. Check both group separation and nonempty splits.

```bash
python3 scripts/decision_audit.py assets/decision-train.jsonl \
  --calibration-file assets/decision-calibration.jsonl \
  --test-file assets/decision-test.jsonl --json
```

This read-only audit checks hard-label shapes, duplicates and cross-split state
or explicit group overlap. It performs no tokenization, semantic leakage check,
probability calibration or GPU test. The fixtures are examples, not enough data
to establish useful model quality. Inspect lengths using the actual tokenizer
and `FastDecisionModel.build_dataset`; record total/skipped decisions and each
reason. Inspect rendered state/questions/options in long examples. At the pinned
source revision, the reported `truncated` count uses length >= max_len; treat it
as a warning requiring inspection, not an exact lost-token count.

## Build a bounded GPU experiment

Use the official [decision notebook pinned at 87c1e89](https://github.com/unslothai/notebooks/blob/87c1e89e973562a5fa94aaffe523e2da84f75785/nb/Qwen3_5_%284B%29-Decision.ipynb)
as an inspected starting point. Its installer includes mutable upstream Git
references and upgrades: pin and resolve them in a new environment before
execution. Do not copy its Colab stack over the working RTX 5070 Ti environment.
Pin backbone revision, Unsloth/Zoo revisions, tokenizer and dependency versions.
Choose a small public model that the installed decision loader actually supports.

The workflow is `FastDecisionModel.from_pretrained` → `get_peft_model` →
`build_dataset` per split → `DecisionTrainer` → train → `calibrate` → save →
fresh reload → `evaluate` on the untouched final test. Inspect the installed
signatures. The notebook uses rank/alpha 16, LR 2e-4 and 60 steps; the current
guide's code uses LR 2e-5 and 240 steps, while its recommendation differs again.
Select and record one recipe; those values are not a reproduced optimum.

Before training, evaluate the untrained converted model and a relevant released
baseline on fixed questions. Start with a bounded smoke budget and finite-loss
stop. For GPU-only work, inspect all model/head parameter devices and backend
logs before inference/training; GPU availability alone is insufficient. End on
contention or fallback. Keep the same resource guard used by the validated SFT
run; do not stop another user's GPU job.

Upstream [issue #13160](https://github.com/unslothai/unsloth/issues/13160)
reported compiled layer-normalization failure when training before inference.
[Fix #13176](https://github.com/unslothai/unsloth/pull/13176) merged at
`3b0e721bdd1fa50b785ad156ca556334bfd67c9f`. This is upstream evidence, not a local
reproduction. Verify whether the chosen package contains the fix. Baseline
evaluation belongs in the experiment anyway; do not hide a compiler failure by
calling it a successful compatibility check or globally upgrading packages.

## Calibrate, reload and evaluate the actual decision artifact

Calibrate only on the calibration split; compare pre/post calibration on the
untouched test split. Report class coverage, per-type accuracy, macro-F1 for
imbalanced choices, Brier/log loss and calibration error with its binning method,
and ordinal error for scores where meaningful. Report abstention/coverage and
false positive/negative costs at thresholds chosen without viewing test results.
Small synthetic cases screen plumbing only; confidence is not a release gate.

Save the decision head, calibration configuration, adapter/backbone reference,
tokenizer and full trainer checkpoint separately. The pinned Clef layout names
`joint_head.safetensors`, `joint_head_config.json` and
`unsloth_decision_config.json`; inspect the actual saved directory. Compare
probabilities and predictions after fresh reload, not only generated text.
The decision-specific GGUF exporter has an `export.json` with a source
fingerprint that includes head/configuration; recalibration can invalidate an
older export. Do not reuse the text-only GGUF converter and claim head parity.

## Local Decision API boundaries

The documented endpoint is `/v1/systemone`, using state/questions and authenticated
requests. Discover the running URL and selected model instead of assuming a port.
`jev-latest` is an alias to the selected local model; it does not mean hosted Jev
is executing. Noul returns a yes probability; score can return an expected
ordinal value, which differs from the discrete `predict()['answer']` level.

The serving guide warns that Laya confidence uses a different formula from Jev
and choice descriptions may be shortened when many options share a token budget.
Revalidate probabilities, option-order sensitivity and long-option behavior on
real held-out data. Never transfer confidence thresholds by name alone.

Laya defaults to CPU and can fall back to CPU on OOM; the source also chooses CPU
while training occupies the GPU. Converted Clef-style models have different
backend requirements. Under a GPU-only directive, choose GPU explicitly and
verify observed placement after load and requests. A response after fallback
fails that directive. Do not claim the GUI enforces a fail-closed GPU policy.
