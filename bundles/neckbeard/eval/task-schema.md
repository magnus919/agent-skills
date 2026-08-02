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

## Trajectory fixtures

A trajectory fixture describes a **multi-phase change-request journey** rather
than a single task. Where a single-task fixture has one `class` and one
`expected_boundary`, a trajectory fixture records the full sequence of journey
phases traversed, the gates evaluated, routing decisions (selected and skipped
specialists with reasons), and the expected terminal state. Trajectory fixtures
let the harness validate that the journey's observable structure — phases,
gates, skips, head-SHA binding — is internally consistent before any model run.

The runner recognizes a trajectory fixture by `kind: trajectory` and validates
it against the trajectory sub-schema below. Single-task fixtures (no `kind`
field) continue to use the schema above, unchanged.

### Trajectory `task.yaml` fields

| Field | Required | Meaning |
|---|---|---|
| `kind` | yes | Must be `trajectory`. |
| `id` | yes | Stable, unique identifier (must match the directory name). |
| `path` | yes | Journey path: `lightweight`, `full`, `refactor`, or `high-risk`. |
| `prompt` | yes | The change request as presented to the agent under test. Self-contained. |
| `phases` | yes | Pipe-separated journey phases as `N: Phase Name`, using the exact phase names from [../references/journey.md](../references/journey.md) (e.g. `1: Intake and provenance`). |
| `gates` | yes | Pipe-separated gate entries as `gate-N: description: verdict`, where verdict is `pass`, `conditional`, or `blocked`. |
| `terminal_state` | yes | Expected terminal state: `merged`, `closed`, `blocked`, or `released`. |
| `visibility` | yes | `public` or `holdout` (same holdout hygiene as single-task fixtures). |
| `skipped_phases` | no | Pipe-separated `N: Phase Name: reason` entries. Every skipped phase must carry a reason. |
| `skipped_gates` | no | Pipe-separated `gate-N: reason` entries. |
| `final_head_sha` | conditional | The exact commit SHA the final verification verdict binds to. **Required for `full`-path fixtures.** |
| `routing_selected` | no | Comma-separated specialist skills loaded during the run. |
| `routing_skipped` | no | Pipe-separated `skill: reason` entries for specialists not loaded. |

### Full-path constraints

A `full`-path trajectory fixture must:
- traverse **all nine** journey phases in `phases`,
- record **all five** gates (`gate-1` through `gate-5`) in `gates`, and
- bind a `final_head_sha`.

The runner enforces these constraints during `--validate-only`.

### Trajectory fixture layout

```
fixtures/trajectories/<id>/
└── task.yaml
```

Trajectory fixtures live under `fixtures/trajectories/`, separate from
single-task fixtures (which live under `fixtures/<class>/<id>/`).

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
- **Trajectory labels must match journey.md.** Phase numbers and names in
  `phases` and `skipped_phases` must exactly match the canonical journey phases.
  Gate IDs must be `gate-1` through `gate-5`. The runner validates this.
