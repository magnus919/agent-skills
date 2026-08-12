# Promise Theory

Coordinate hybrid human + AI agent workforces with promises, acceptances, and assessments — the promise-theory method of Mark Burgess and Jan Bergstra, made practical for agents.

## Why Install This Skill

Multi-agent systems fail in predictable ways: agents over-promise, refuse what was sent to them, drift from their instructions, and afterward nobody can say who promised what, who accepted, and whether it was kept. This skill gives your agent a vocabulary and a working method for that problem: model delegation as voluntary promises plus acceptance, then verify and renegotiate on a schedule instead of guessing.

After installing, your agent can draft a promise manifest for a team of agents and humans, turn it into a signed agent contract with acceptance criteria, verification, and escalation rules, and run retrospectives that turn breaches into renegotiated promise sets rather than blame. The skill is grounded in promise theory's academic foundations and its proven use in infrastructure (CFEngine, Kubernetes-style convergence) and applies both to today's hybrid human + agent teams.

## What You Get

| Contents | Provides |
|---|---|
| `SKILL.md` | When to use promise theory, when not to, and what to load for the task at hand |
| `references/` | Seven load-on-demand references: foundations, infrastructure applications, agent coordination, coordination patterns, trust and verification, diagnosis and debugging, glossary |
| `templates/` | Fillable `promise-manifest.yaml.tmpl`, `agent-contract.md.tmpl`, and `promise-review.md.tmpl` |
| `scripts/promise-contract.py` | Stdlib-only CLI that lints promise manifests and renders the promise graph |
| `evals/` | Output-quality evals for the skill |
| `tests/` | Trigger probes and unit tests |
| `LICENSE` | MIT license |

## Quick Start

Copy `templates/promise-manifest.yaml.tmpl` to a working file, fill in your agents, promises, and expectations (every field has a comment), then lint it:

```
python3 scripts/promise-contract.py lint promise-manifest.yaml
```

Exit 0 means the manifest is valid and every expectation maps to a promise. Then fill `agent-contract.md.tmpl` from the manifest for the humans and agents involved, and run `promise-review.md.tmpl` retrospectives on a cadence.

## Triggers

- Modeling delegation between humans and AI agents
- Designing capability manifests or agent contracts
- Diagnosing coordination failures: unkept promises, refused acceptances, missing assessments
- Calibrating how much to verify an agent, at what rate, and at what cost
- Designing self-healing or convergent systems
- Converting obligation-based designs to promise-based ones

## Requirements

Python 3.10+ for the bundled `promise-contract.py` (standard library only, no dependencies). Everything else is plain Markdown and YAML.
