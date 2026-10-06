# Harness Engineering

Make agents easier to start, constrain, verify, recover, and improve.

## Why Install This Skill

An agent can write plausible code and still forget progress, use the wrong tools,
or call unfinished work complete. This skill helps find where execution breaks
and change the environment around the model with evidence.

It covers new harnesses and existing ones: small repository setups, custom
runtimes, session continuity, verification, and bounded autonomous loops. It
builds on WalkingLabs' Harness Creator and course, with clearer evidence limits
and safe local tooling. Structural audits help discovery; real task comparisons
are still needed to establish improvement.

## What You Get

| Contents | Provides |
|---|---|
| `SKILL.md` | Design, diagnosis, implementation, and improvement workflow |
| `references/` | Design procedures, worked use cases, catalog handoffs, source coverage, and conditional System One integration evidence |
| `templates/` | Project instructions, state, handoff, decision placement, tool, bulk-result and experiment contracts |
| `scripts/harness.py` | Audit with optional HTML, preview-first scaffold, explicit check runner |
| `scripts/contracts.py` | State/graph/run declaration checks and compatible-run comparison |
| `scripts/decision_examples.py` | Offline synthetic typed-decision examples for selection, action, and review boundaries |
| `scripts/test_*.py` | Safety, near-miss, and evidence-boundary regression tests |
| `evals/` | Representative output-quality cases and rubric challenge examples |

Run records keep an aggregate human-intervention count by default. When an
evaluation question needs more detail, the guidance defines an optional typed,
privacy-bounded event record; it does not capture message text or infer success
from a lower count.

## Quick Start

From the installed skill directory, audit a project:

```sh
python3 scripts/harness.py audit --target /path/to/project
python3 scripts/harness.py scaffold --target /path/to/project
```

The first command prints JSON findings with behavior marked `not_assessed`.
The second previews files to create or skip. Add `--apply` to create missing files;
existing files are preserved. No API key is required.

To view offline synthetic typed-decision examples:

```sh
python3 scripts/decision_examples.py selection --json
```

Ask your agent: "Diagnose why this agent declares completion too soon," "Design
a durable runtime around these tools," or "Compare this harness change on the
same tasks." For a large integration catalog, ask it to expose tool prerequisites
and dependency order; for oversized outputs, ask for an authorized artifact handle
with provenance, completeness and recovery terms. It selects the relevant
procedure and supporting templates. Small stable catalogs may use a static index.

## Triggers

- An agent loses state, drifts in scope, or claims completion too soon.
- You want to build, audit, simplify, or improve a harness.
- You need tools, context, checkpoints, verification, or recovery around a model.
- You want a bounded autonomous loop or coordinated agent workflow.

## Requirements

Python 3.10+ for bundled scripts. Project-specific tools are required only for
checks you explicitly choose to execute. No provider dependency is bundled.
