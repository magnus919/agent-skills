# Evaluation Task Schema

Each fixture is a directory under `fixtures/` containing a `task.yaml` and any
repository context it needs. The runner ([run_eval.py](run_eval.py)) loads every
`task.yaml` it finds.

## `task.yaml` fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable, unique identifier (matches the directory name). |
| `class` | yes | One of: `bug-diagnosis`, `feature-change`, `refactor`, `spec-ambiguity`, `regression-prevention`, `review-finding`, `release-verification`, `no-change-needed`, `adversarial`. |
| `prompt` | yes | The task as presented to the agent under test. Self-contained. |
| `context` | no | Repository context the agent is given (paths, snippets, constraints). Inline or file refs relative to the fixture dir. |
| `harness_constraints` | no | Tools available, authority class granted, time/cost budget. |
| `ground_truth` | yes | What a correct outcome looks like. For `no-change-needed`, the evidence that no change is warranted. |
| `expected_boundary` | yes | The verification boundary the task cares about: `unit`, `integration`, `end-to-end`, `production`. |
| `scoring_notes` | no | Dimension-specific anchors for raters (see [rubric.md](rubric.md)). |
| `visibility` | yes | `public` or `holdout`. Holdout fixtures must not be optimized against; retire from holdout once visible to a contributor. |
| `adversarial_intent` | no | For `adversarial` class: the trap being tested (e.g. "reflexive deletion", "reflexive no-dependency"). |

## Fixture layout

```
fixtures/<class>/<id>/
├── task.yaml
└── repo/            # optional: the repository context the task runs against
```

## Rules

- **Self-contained prompts.** The agent under test sees only `prompt`, `context`,
  and `harness_constraints`. No hidden hints.
- **Fair to baselines.** Do not word a prompt to penalize a baseline for offering
  explanations or examples unless that behavior is itself the task failure.
- **Adversarial coverage is mandatory.** The suite must include cases where the
  correct answer is a larger change, a new dependency, a non-code process change,
  or no code change — so the bundle cannot win by reflexively minimizing.
- **Holdout hygiene.** Track visibility. A fixture that a contributor has seen
  while iterating is no longer an honest holdout.
