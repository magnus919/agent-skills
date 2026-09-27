# system-one — Typed probabilistic decisions inside deterministic software

## Why Install This Skill

Use System One when software needs a bounded judgment—such as a ticket route,
risk flag, or tool choice—while exact policy and actions remain inspectable
code. The skill covers hosted Jev, local Laya and CLM, and newer open candidates;
it helps teams evaluate outputs without treating confidence as permission or
ground truth.

You'll find decision contracts, integration patterns, calibration and
comparison methods, and private-model operations. DevOps examples cover
diagnostic tests, repair invariants, telemetry routing, and durable decisions. Cascade guidance shows how
to validate confidence-based escalation. Use these to compare actual
workloads, establish fallback and readiness behavior, and avoid copying a demo
threshold into production.

For semantic code linting, the skill shows how to turn a maintained rule into a
typed check, distinguish local post-edit feedback from a repository scan, and
evaluate detection separately from verified repairs and completed tasks. It
starts semantic checks as advisory and requires independent evidence before a
blocking CI gate.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Decision contracts, integrations, evaluation boundaries, and task routing |
| `references/` | Pilot design, model/provider guides, comparisons, DevOps decisions, validated escalation, semantic linting, hosting, and troubleshooting |
| `templates/` | Decision/action contracts, cascade qualification, execution records, benchmarks, lint rules, and feedback evaluation |
| `scripts/` | Offline probes and demos, analyzers, private adapters, and optional evaluation tools |
| `examples/`, `tests/`, `evals/` | Synthetic fixtures, offline tests, and versioned output-quality cases |

## Quick Start

Try the offline probe and routing demo (no model call):

```bash
python3 scripts/systemone_probe.py --request examples/request.json
python3 scripts/decision_demo.py
```

Then open `references/worked-decision-pilot.md` for a first evaluation, or
`references/semantic-lint-feedback.md` for post-edit and repository-wide lint
feedback. For incident workflows use `references/devops-decision-patterns.md`;
for confidence-based escalation use `references/selective-judgment.md`.
Live Jev probes require `--live` and a provider credential in an environment
variable; never place credentials in source or browser code.

## Triggers

Use this skill for Jev, Laya, or CLM; typed Choice/Score/Noul decisions; routing
or calibration based on model judgment; DevOps decision support; validated
escalation; private model hosting; and semantic code linting or post-edit feedback. It is not for style-only linting, exact policy
checks, ordinary open-ended generation, or generic model serving.

## Requirements

- Current provider documentation access for revisions and licenses.
- Jev: a TypeSafe or supported gateway credential and outbound HTTPS.
- Laya: Python 3.10+, PyTorch/Transformers, Hugging Face access or a pinned
  local model bundle, and enough CPU/GPU/MPS memory for the selected checkpoint.
- CLM: a pinned Qwen3-8B pooling encoder and matching projection head; local
  serving uses vLLM, PyTorch, and enough accelerator memory for the encoder.
- Offline probes and demos use Python's standard library. Live inference needs
  the relevant provider or model dependencies and access.
- Docker is optional for the private-service container example; TLS ingress,
  secret management, and operational monitoring are supplied by your platform.
