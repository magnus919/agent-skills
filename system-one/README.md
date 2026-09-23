# system-one — Typed probabilistic decisions inside deterministic software

## Why Install This Skill

System One models are useful when an application needs a fast judgment—route a
ticket, score urgency, flag a risk, choose a tool—but the rest of the workflow
should remain ordinary, inspectable code. This skill teaches an agent how to
use TypeSafe Jev, self-host Convai Innovations Laya, and compare newer open
decision-model candidates without mistaking a probability for permission or
truth.

It covers the path from a small API call to a reference private Laya service:
decision contracts, typed questions, deterministic policy gates, evaluation,
model lifecycle, readiness, and troubleshooting. It also deconstructs working
patterns in browser/voice control, routing, ranking, agent permissions, and
deadline-bound applications. The bundled service is a starting adapter—not a
prebuilt production VPC deployment—and live model quality must be evaluated
on your own workload.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Core integration workflow, model-selection rules, guardrails, and stopping criteria |
| `references/` | Jev and Laya guides, local/VPC service walkthrough, use-case recipes, evaluation, troubleshooting, and model survey |
| `templates/decision-contract.md` | Fillable contract for state, questions, thresholds, authority, and fallback |
| `templates/action-control-contract.md` | Preflight for observed app actions, confirmation, freshness, and rollback |
| `templates/benchmark-record.md` | Reproducible model/latency/calibration comparison record |
| `examples/` | Synthetic request, response, and labeled evaluation cases |
| `scripts/` | Offline/live probe, read-only routing demo, synthetic QA pilot, binary evaluator, and private Laya HTTP adapter |
| `templates/laya.Dockerfile` | Container starting point using a pinned local model artifact |
| `tests/` and `scripts/test_*.py` | Offline checks for contracts, policy, evaluation, and service behavior |
| `evals/evals.json` | Nine output-quality cases for model integration and operations |

## Quick Start

Read the guide for your task:

```text
references/jev.md     # hosted Jev
references/laya.md    # self-hosted Laya
references/laya-self-hosting.md  # local-to-private-service walkthrough
references/use-case-patterns.md # browser, routing, ranking, guardrail recipes
```

Validate a request contract without calling a model:

```bash
python3 scripts/systemone_probe.py --request examples/request.json
python3 scripts/decision_demo.py
python3 scripts/evaluate_noul.py --cases examples/noul.synthetic.jsonl --threshold 0.8
python3 scripts/jev_qa_pilot.py  # synthetic rules-only baseline; no API call
```

For Laya, follow `references/laya-self-hosting.md` to stage a commit-pinned
checkpoint and verify actual CPU/GPU placement. That guide shows how to
start the authenticated reference adapter, smoke-test it, and build an image.
Live Jev probes require an explicit `--live` flag and the provider credential
in an environment variable. Do not put credentials in source or browser code.

## Triggers

Load this skill when the task mentions System One, Jev, Laya, typed decisions,
Choice/Score/Noul, calibrated probabilities, deterministic routing from model
judgment, Laya self-hosting, or a Jev-compatible decision API. Do not load it
for ordinary chat completion, generic LLM serving, exact policy evaluation, or
open-ended reasoning without a typed decision contract.

## Requirements

- Current documentation access for provider/model revisions and licenses.
- Jev: a TypeSafe or supported gateway credential and outbound HTTPS.
- Laya: Python 3.10+, PyTorch/Transformers, Hugging Face access or a pinned
  local model bundle, and enough CPU/GPU/MPS memory for the selected checkpoint.
- The probe, routing demo, evaluator, and HTTP adapter use Python's standard
  library; actual Laya inference requires the upstream package and weights.
- Docker is optional for the private-service container example; TLS ingress,
  secret management, and operational monitoring are supplied by your platform.
