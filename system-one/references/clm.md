# Contrastive Language Models (CLM)

Checked 2026-09-26 against [the upstream repository](https://github.com/Contrastive-LM/CLM), its [source](https://github.com/Contrastive-LM/CLM/tree/main/src/clm), [fine-tuning code](https://github.com/Contrastive-LM/CLM/blob/main/train/finetune.py), and [model card](https://huggingface.co/Contrastive-LM/CLM-v0.1-8B). Source snapshot: `bb42c6c5bf914fd449bed2f6ca65be80602cb1f7`. Pin and recheck revisions before use. The linked Notion research blog was unavailable during this review; treat its unreproduced claims as project claims.

Use this reference for CLM's typed decisions, free-form candidate ranking, head training, or serving. Use `references/ecosystem-radar.md` to select among models and `references/evaluation-and-calibration.md` for a matched target-data comparison. CLM is a model candidate, not an authority or a source of open-ended generated answers.

## How a decision is made

CLM uses a frozen Qwen3-8B encoder with **last-token pooling**. Separate trainable projection heads map a state and each candidate action into a shared space. A scaled cosine similarity scores each pair; softmax over *the supplied candidates* produces the answer distribution. The heads, not the 75 MB checkpoint alone, are the small part: serving still needs the 8B encoder and its memory. The reference head requires the matching Qwen3-8B encoder, pooling, tokenizer, and text recipe; swapping in a generic embedding model changes the model.

The [schema code](https://github.com/Contrastive-LM/CLM/blob/main/src/clm/schema.py) renders object states as prose, appends each question's `instructions` after the state, and embeds a Choice option's description (or its key if empty) as the action text. Score levels are ordered candidate texts. Noul constructs true/false candidates, using supplied criteria or default text. Keep the question in trusted `instructions`, avoid repeating it in state, and freeze serialization, option descriptions, and option sets in a comparison. `confidence` is the top probability minus the mean of the others; it is not calibrated correctness. Score is the expected zero-based level index, not an integer category. `clm-raw` is an encoder-only ablation, not another released decision model.

Independent states and actions can be cached separately. This especially suits repeated actions or large candidate pools, but speed depends on cache hit rate and workload. A probability is conditional on the exact candidate set: changing, shortlisting, or omitting an `other` option changes its meaning. Long texts may be truncated; the default serving limit is 2048 tokens.

## Use the API

The [server](https://github.com/Contrastive-LM/CLM/blob/main/src/clm/server.py) provides `POST /v1/systemone` with Choice, Score, and Noul wire shapes, `POST /v1/rank` for candidate ranking, `GET /v1/models`, and `GET /health`. `CLMClient.system_one(state, questions)` accepts typed SDK objects or wire-format dicts. `Engine.answer` and `Engine.rank` are in-process forms; `CLMClient.rank(context, question, answers)` calls the rank route. The advertised TypeSafe compatibility concerns request/answer shape, not Jev weights, model identity, calibration, or behavior. Verify the returned model as `clm-latest` or the pinned custom name, not `jev-latest`.

For a disposable local smoke test, upstream's two-process shape is:

```bash
pip install 'contrastive-lm[serve,vllm,hf]'
vllm serve Qwen/Qwen3-8B --served-model-name qwen3-8b --runner pooling --max-model-len 2048 --port 8090
# In a second process, after the encoder is healthy:
clm-serve --host 127.0.0.1 --port 8700 --emb-url http://127.0.0.1:8090/v1/embeddings
```

That fetches mutable dependencies and the default head; use pinned artifacts for a controlled service. Confirm the selected package revision still supports these commands before running them.

```python
from clm import CLMClient, Choice, Noul

client = CLMClient()  # CLM_BASE_URL defaults to http://127.0.0.1:8700
result = client.system_one(
    state="The customer reports a duplicate charge and requests a refund.",
    questions={
        "queue": Choice(instructions="Which queue should review this?",
                        criteria={"billing": "Charges and refunds", "other": "No listed queue fits"}),
        "urgent": Noul(instructions="Does this require urgent review?"),
    },
)
```

Validate IDs, types, finite values, the full Choice distribution, and the configured model before policy code. Keep a review/abstain path. For ranking, measure shortlist recall and best-of-N task success, not just top probability; never treat a ranked candidate as a verified solution. The example shows call shape, not predicted answers.

## Fine-tune the heads

The [training script](https://github.com/Contrastive-LM/CLM/blob/main/train/finetune.py) has two distinct tasks. `--task choice` consumes the `LocalLLaMA/typed-decisions` style train/test parquet and `--workflow`; it derives a validation split from train IDs, embeds unique state/candidate texts, and trains projection heads with soft annotator distributions or hard labels and InfoNCE or soft cross-entropy. `--task clm` consumes state/action transitions or precomputed embeddings for trajectory verification and supports task-disjoint `--holdout-tasks` or folds. Both can warm-start from the reference checkpoint with `--init-ckpt`; `best_head.pt` is the selected output. Training the heads does not train the Qwen3 backbone.

From a pinned checkout with its training dependencies, the documented entry points are:

```bash
python train/finetune.py --task choice --data LocalLLaMA/typed-decisions \
  --workflow all --init-ckpt /pinned/reference-head.pt --out-dir /runs/typed
python train/finetune.py --task clm --hf-dataset /pinned/trajectory-embeddings \
  --holdout-tasks /pinned/heldout-tasks.json --init-ckpt /pinned/reference-head.pt \
  --out-dir /runs/verifier
```

The paths illustrate required artifacts; validate dataset format, revisions, and separation before execution. Use `--embed-model`, `--embed-url`, and `--max-len` only with a matching encoder recipe when embedding fresh transitions.

For a target task, first establish the unmodified zero-shot baseline and define candidate text, labels, task identity, and a genuinely held-out test split. For Choice, keep related rows and questions from the same case together across splits and inspect per-question results plus majority and incumbent baselines. For trajectory verification, hold out whole tasks, not merely steps or candidates from the same task; score with the same candidate grouping and best-of-N rule as the intended use. Fit temperature or decision thresholds only on a separate calibration split. Preserve the final test until model, rubric, and selection rule are frozen. Compare against the reference head and the full workflow; a lower training loss alone is not an improvement.

The [fine-tuning guide](https://github.com/Contrastive-LM/CLM/blob/main/docs/FINETUNING.md) is an autonomous experiment protocol, not a turnkey quality guarantee. The published DeepSWE and Terminal-Bench 2.1 verifier results use fine-tuned task heads and small held-out task sets; they do not describe the zero-shot reference head or establish performance on another application. The project-reported Jev speed and quality comparisons also need reproduction under the same input, candidate count, hardware, cache state, and latency boundary.

## Operate a private service

Run the Qwen3-8B vLLM pooling encoder and `clm-serve` as separate pinned components; keep the embedding endpoint private. Pin source/package, base encoder and tokenizer revisions, projection checkpoint hash, pooling and token limits, vLLM/PyTorch/CUDA versions, text recipe, and calibration map. The [head loader](https://github.com/Contrastive-LM/CLM/blob/main/src/clm/heads.py) can download a default checkpoint or load `--ckpt`, `--ckpt-dir`, and named `--model` heads; use an explicitly staged artifact and `--no-download` for controlled release. Check model identity and a representative decision after startup or head reload.

`clm-serve` binds to `0.0.0.0` by default. Bind to loopback or private ingress, set `CLM_API_KEY` for bearer authentication, leave `--cors` off unless required, and use `--no-ui` when the playground is unnecessary. Add ingress limits for request bytes, question count, candidates, concurrency, queue wait, and total deadline: the inspected server validates basic shapes but does not provide these application caps. Avoid storing state text or keys in logs. `GET /health` returns `ok: true` even when its separate `embedder` field is false, so readiness must require an available encoder, expected head, and a representative inference. `--action-cache` reserves device memory at startup; size it against the encoder, or set it to `0` for a constrained test. Record cold/warm p50/p95/p99, cache hit rate, encoder queue time, memory, errors, and fallbacks. Roll back the pinned encoder/head pair together if quality, readiness, or latency regresses.

## Stop rule

Recommend shadow evaluation when the workload has a closed candidate set and sufficient encoder capacity. Do not recommend live substitution until a held-out target comparison beats the current process at the required risk/coverage and latency boundary, with calibrated thresholds, private ingress, readiness, fallback, and rollback verified. For multimodal inputs, exact rules, or open-ended generation, route to the corresponding non-CLM path.

## Eval review examples

Selection: a satisfying answer compares matching held-out cases and cache
conditions; a near miss adopts the published speedup as local proof; omitting
comparison evidence leaves adoption not shown. Training: a satisfying answer
holds out whole tasks and distinguishes zero-shot from fine-tuned heads; a near
miss splits trajectory steps across train and test; naming a training command
alone leaves split integrity not shown. Operations: a satisfying answer requires
encoder availability and representative inference for readiness; a near miss
accepts `ok=true` with `embedder=false`; an answer omitting the readiness predicate
leaves safe promotion not shown. These examples support rubric review, not a
validated model-grade pass.
