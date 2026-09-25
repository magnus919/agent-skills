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

The field and implementation references distill bounded use cases, failure
patterns, and safeguards from Jev projects. The request-shape and cascade
guides show how to test batching and whole-workflow economics without copying
a demo threshold or treating model confidence as authority.

For model comparisons, start with the battery design review. It makes the
test count, expected answers, and pilot case review explicit before a large
corpus or benchmark run. Keep run outputs outside the skill repository.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Core integration workflow, model-selection rules, guardrails, and stopping criteria |
| `references/` | First-pilot guide, field and implementation patterns, request-shape and cascade methods, QA automation, Jev and Laya guides, GLiNER2.5-Decide, hosting, evaluation, and troubleshooting |
| `templates/decision-contract.md` | Fillable contract for state, questions, thresholds, authority, and fallback |
| `templates/action-control-contract.md` | Preflight for observed app actions, confirmation, freshness, and rollback |
| `templates/benchmark-record.md` | Reproducible model/latency/calibration comparison record |
| `templates/decision-battery-design-review.md` | Pilot review of the test unit, answer rules, case mix, and comparison conditions before expansion |
| `examples/` | Synthetic request, response, provisional labeled decision corpora, and a frozen Jev semantic-audit fixture |
| `scripts/` | Offline/live probe, request-shape and cascade analyzers, decision-battery runner, routing demo, Jev QA pilot, advisory eval audit, private review and model-teacher screening, binary evaluator, and private Laya HTTP adapter |
| `templates/laya.Dockerfile` | Container starting point using a pinned local model artifact |
| `tests/` and `scripts/test_*.py` | Offline checks for contracts, policy, evaluation, and service behavior |
| `evals/evals.json` | Output-quality cases for model integration, field evidence, and operations |

## Quick Start

Read the guide for your task:

```text
references/jev.md     # hosted Jev
references/laya.md    # self-hosted Laya
references/laya-self-hosting.md  # local-to-private-service walkthrough
references/use-case-patterns.md # browser, routing, ranking, guardrail recipes
references/worked-decision-pilot.md # choose and evaluate a first bounded decision
references/field-patterns-and-antipatterns.md # cross-project use and failure patterns
references/implementation-audit.md # four original implementation patterns
references/request-shape-evaluation.md # singleton-vs-batch comparison
references/cascade-economics.md # router ablations and whole-pipeline accounting
references/jev-ci-reference-deployment.md # reproduce and operate this repo's Jev CI audit
```

Validate a request contract without calling a model:

```bash
python3 scripts/systemone_probe.py --request examples/request.json
python3 scripts/decision_demo.py
python3 scripts/evaluate_noul.py --cases examples/noul.synthetic.jsonl --threshold 0.8
python3 scripts/batch_request_shape.py --cases examples/batch-request-shape.synthetic.jsonl
python3 scripts/cascade_economics.py --cases examples/cascade.synthetic.jsonl --baseline best_single
python3 scripts/decision_battery.py --help
# Before a live run, review templates/decision-battery-design-review.md.
# Keep --output and full run reports outside this repository.
python3 scripts/jev_qa_pilot.py  # synthetic rules-only baseline; no API call
python3 scripts/jev_eval_audit.py --reports /path/to/paired-eval-artifacts  # offline selection check
python3 scripts/jev_eval_calibration.py --help  # private review, scoring, and offline repeatability
python3 scripts/jev_teacher_label.py --help  # optional blind model-teacher screening
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
