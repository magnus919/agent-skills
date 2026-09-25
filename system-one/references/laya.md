# Convai Innovations Laya: local and VPC guide

Checked 2026-09-22 against the upstream repository, runtime source, model cards,
and the Node/ONNX adapter. Re-check revisions and licenses before deployment.

## Current model family

The upstream Python package is `laya` and requires Python 3.10+. The repository
currently documents three checkpoints:

For domain adaptation of the English checkpoint, read `references/laya-fine-tuning.md`.

| Checkpoint | Backbone/size | Context | Intended use |
|---|---|---:|---|
| `convaiinnovations/laya` | ModernBERT-large, 421M | 512 | English |
| `convaiinnovations/laya-multilingual` | mmBERT-base, 322M | 1024 | 100+ languages |
| `convaiinnovations/laya-typed-decisions` | ModernBERT-large, 421M | 1024 | four specialist workflows |

The names and benchmark numbers are not interchangeable. The specialist
checkpoint was fine-tuned on four synthetic workflows and should not silently
become a general default. The upstream README reports that base checkpoints
can be near or below simple baselines on typed-decision data; evaluate your own
domain before relying on them.

## Direct Python use

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install laya
```

```python
import laya

agent = laya.load("convaiinnovations/laya", device="cuda")
result = agent.predict(
    {"subject": "Duplicate charge", "body": "Refund the second charge."},
    {
        "queue": {
            "type": "choice",
            "instructions": "Which queue should handle this?",
            "criteria": {"billing": "Payments and refunds", "other": "Unknown"},
        },
        "refund": {
            "type": "noul",
            "instructions": "Does the customer explicitly request a refund?",
        },
        "urgency": {
            "type": "score",
            "instructions": "How urgent is this?",
            "criteria": ["routine", "soon", "blocking"],
        },
    },
)
```

The loader downloads from Hugging Face unless given a local model path. For
repeatable deployments, pre-download a specific revision, verify its files and
license, bake or mount the artifact, and set an explicit model directory. Do
not let every replica download mutable `main` on first request.

## Router and residency

`Router()` can choose a checkpoint by explicit model, task, language, or script.
For a server, preload the checkpoints that traffic actually needs:

```python
from laya import Router

router = Router(preload=True, device="cuda", max_loaded=2)
result = router.predict(state, questions)
```

Lazy loading with the default one-model LRU can rebuild weights whenever traffic
switches language. That is a correctness/latency deployment bug, not a model
latency result. Keep the intended checkpoints resident or route workloads to
separate workers. Attach an already-loaded agent instead of loading a duplicate.

## Private service architecture

The upstream Python package is an inference runtime, not a promised production
HTTP service. A safe VPC pattern is:

1. Build a pinned image with Python, the selected Laya version, and a pinned
   model revision; preflight-load the model during startup.
2. Wrap one resident agent/router in a small authenticated HTTP service. Bound
   body size, question count, option count, concurrency, queue time, and total
   request deadline.
3. Expose `/healthz` for process liveness and `/readyz` only after the model,
   tokenizer, device, and calibration artifact load successfully. Do not call
   inference from a liveness probe.
4. Bind the model service to a private interface; put TLS/auth/rate limiting at
   the intended ingress; restrict egress to the artifact source during build
   and to required telemetry at runtime.
5. Emit model revision, contract hash, device, queue time, inference time,
   response validation outcome, and fallback lane. Never log credentials or raw
   sensitive state.
6. Roll out shadow traffic first, then a bounded percentage, and keep the
   previous image plus model/config hashes as the rollback unit.

An OpenAI-shaped or Jev-shaped endpoint is a convenience, not proof of semantic
compatibility. Keep a provider-neutral internal contract and test each adapter.

## ONNX/Node option

`receptron/laya` provides an ONNX Runtime Node/TypeScript adapter. Its README
states that PyTorch/Python are not needed at runtime, the weights are roughly
1.7 GB fp32, and the model cache is configurable with `LAYA_CACHE`. Use this
when a Node service or a non-PyTorch runtime is a real constraint; verify the
adapter's bundle checksum and output parity against the Python reference before
using it as a production replacement.

For native C++ inference with CUDA, Vulkan, or CPU and a Jev-compatible HTTP
endpoint, read `references/laya-cpp.md`. It is a separate community runtime;
do not assume Python, Node, and C++ have identical latency or calibration.

## Known limits and fixes

- The option list shares a fixed head token budget. Large Choice sets can make
  labels indistinguishable. Shortlist deterministically, use hierarchy, or
  raise the head/context budget only after measuring truncation and quality.
  Probabilities after shortlisting are conditional on the shortlist.
- State and question text are truncated at configured limits. Log effective
  token counts and test long, adversarial, multilingual, and missing-field cases.
- `laya-multilingual` and English Laya have different language strengths. Do not
  use confidence to rescue a checkpoint that cannot read the input language;
  route before inference.
- If model construction hangs with TensorFlow installed, the upstream release
  notes recommend `USE_TF=0`. Treat environment changes as part of the pinned
  deployment record.
- The runtime can fall back from CUDA/MPS to CPU on unavailable devices or
  placement errors. Verify the actual device after startup; otherwise a healthy
  endpoint can hide a 10x latency regression.
- Calibrate probabilities on held-out target data. The upstream model cards
  explicitly discuss over-confidence and temperature fitting; do not copy a
  vendor threshold such as `0.85` into a high-stakes workflow.

## Primary sources

- Upstream runtime: https://github.com/NandhaKishorM/laya
- Python runtime source: https://github.com/NandhaKishorM/laya/blob/main/laya/agent.py
- Router source: https://github.com/NandhaKishorM/laya/blob/main/laya/router.py
- Model family: https://huggingface.co/convaiinnovations/laya
- Specialist model card: https://huggingface.co/convaiinnovations/laya-typed-decisions
- Node/ONNX runtime: https://github.com/receptron/laya
