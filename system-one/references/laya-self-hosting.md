# Laya self-hosting: local checkpoint to private service

Use this when a user needs an executable local/VPC path. The script and
Dockerfile here are a **reference adapter**, not a managed deployment or a
substitute for the organization's ingress, secrets, monitoring, and rollout
controls. Checked against upstream Laya runtime and Hugging Face Hub download
documentation on 2026-09-22. Recheck exact releases and licenses before use.

## 1. Select and stage one immutable checkpoint

Use Python 3.10+ and enough disk/RAM for the chosen checkpoint. For English
triage, start with `convaiinnovations/laya`; use the multilingual checkpoint
only when the evaluation workload warrants it. Record the model card, license,
full commit hash, Laya package version, Python/PyTorch/CUDA versions, and
hardware. Do not assume the specialist checkpoint is better on generic work.

From the `system-one` skill root, substitute a reviewed full-length Hugging
Face commit hash and an exact, tested Laya package version:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install 'huggingface_hub[cli]' 'laya==<tested-version>'
hf download convaiinnovations/laya --revision <full-commit-hash> \
  --include rl_agent_config.json model.safetensors 'tokenizer/*' 'encoder/*' \
  --local-dir model
```

`hf download --dry-run` can show size before transfer. Verify the directory
contains `rl_agent_config.json`, `model.safetensors`, and the required
tokenizer/encoder files. Record SHA-256 hashes of the materialized files in
the deployment record; do not rely on mutable `main` or a first-request
download. The upstream loader may repair `tokenizer_config.json` for certain
Transformers versions; perform that preflight on a writable staging copy and
then freeze the *resulting* artifact before a read-only runtime mount.

The underlying Hub supports exact `revision` and filtered `snapshot_download`
as well as the CLI: https://huggingface.co/docs/huggingface_hub/guides/download

## 2. Confirm local inference and actual device

```bash
python - <<'PY'
import laya
agent = laya.load('model', device='cpu')
assert str(agent.device) == 'cpu', agent.device
result = agent.predict({'subject': 'Duplicate charge'}, {
    'route': {'type': 'choice', 'instructions': 'Which queue?',
              'criteria': {'billing': 'Payment issue', 'other': 'Unknown'}}
})
print({'device': str(agent.device), 'model': result['model'],
       'route': result['answers']['route']['choice']})
PY
```

This is a connectivity smoke test, not quality evidence. The answer may vary;
the keys and legal labels should not. For CUDA or MPS, change the requested
device and assert `agent.device` matches. Laya may silently fall back to CPU
when requested acceleration is unavailable or memory placement fails; a
healthy process with the wrong device must not be marked ready. Inspect the
actual source and loaded revision when diagnosing fallback.

## 3. Start the reference HTTP adapter

Set a randomly generated service token through your secret manager, not in
source, an image layer, or a browser. Run the service on loopback for local
development:

```bash
export SYSTEM_ONE_SERVICE_TOKEN='<at-least-16-random-characters>'
python scripts/laya_service.py --model-path model --device cpu
```

Expected startup line includes `"ready": true` and `"device": "cpu"`.
`GET /healthz` means the process is alive. Authenticated `GET /readyz` means
`laya.load()` returned and the model agent reports the requested device; the
adapter's explicit readiness predicate checks only device residency. It does
not separately attest tokenizer or calibration-artifact readiness. Extend the
readiness check to cover every required initialization dependency before routing
production traffic. `POST /v1/systemone` accepts the same `{state, questions}`
contract as the bundled probe. It rejects bodies over 64 KiB, more than 16
questions, or more than 64 options per question; it allows one inference in
flight and returns 503 when busy. These are example limits, not evidence that
64 options fit Laya's head-token budget.

In a second shell, from the skill root:

```bash
python scripts/systemone_probe.py --request examples/request.json --live \
  --url http://127.0.0.1:8788/v1/systemone \
  --api-key-env SYSTEM_ONE_SERVICE_TOKEN
```

The probe prints status, elapsed time, model, and question IDs, not raw state
or answers by default. `--show-response` opts into printing potentially
sensitive answers. If the runtime returns a different optional field shape,
update and test the adapter; do not bypass contract validation to obtain 200.

## 4. Build an immutable image and deploy privately

`templates/laya.Dockerfile` expects the staged `model/` directory in its
build context. Supply an exact Laya package version and a digest-pinned Python
image; do not leave the sample placeholders in automation:

```bash
docker build -f templates/laya.Dockerfile \
  --build-arg PYTHON_IMAGE='python:3.11-slim@sha256:<reviewed-digest>' \
  --build-arg LAYA_VERSION='<tested-version>' \
  -t local/system-one-laya:<release-id> .
```

The sample `CMD` requests CPU. Override it explicitly for a GPU deployment
only after building against a compatible PyTorch/CUDA base and testing the
same artifact there. The image is not exposed safely merely because the
model is local. In a VPC, place the container on a private subnet/interface;
terminate TLS, authenticate callers, enforce request rate/body/concurrency
limits, and set request deadlines at the ingress. Restrict runtime egress,
run with least privilege, and provide the token as a runtime secret. Do not
publish port 8788 directly to the Internet. The stdlib server has no built-in
TLS, distributed rate limiting, graceful in-flight draining, or hard
inference timeout. An ingress timeout cannot cancel a PyTorch call; capacity
planning must account for that work continuing after a client disconnects.

Deploy one checkpoint per worker initially. If English and multilingual
traffic are both required, use explicit language routing and separate workers
or a deliberately preloaded router with enough memory. Default lazy loading
may evict and reload weights on language switches; benchmark actual residency.

## 5. Verify and roll out

Before traffic: confirm artifact hashes, package/image digest, requested and
actual device, readiness, a synthetic typed request, and representative
held-out quality. Then shadow on approved traffic, compare with the current
path, release to a bounded percentage, and retain the previous image,
artifact, policy, and calibration versions as one rollback unit. Record
queue/wait, inference latency, busy/error rate, actual device, option count,
question type, fallback/review lane, and downstream outcome—without raw state
or secrets. Restore the prior unit if device fallback, wrong-action rate,
latency, or malformed-output rate exceeds the agreed gate.

For diagnosis, follow `references/hosting-and-troubleshooting.md`. For the
runtime, checkpoint family, and known head-token/language constraints, read
`references/laya.md`.

## What this guide has and has not verified

The adapter's offline contract and concurrency tests run without weights.
This repository does **not** bundle Laya weights, a paid Jev credential, a GPU,
or a VPC account. Local model loading, the container build, hardware latency,
TLS ingress, and real deployment remain environment-specific acceptance
checks; report them as unverified until run in the target environment.
