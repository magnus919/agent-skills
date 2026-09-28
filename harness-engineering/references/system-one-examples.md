# System One decision examples for harnesses

Run `python3 scripts/decision_examples.py` from the installed `harness-engineering/` skill directory to print all three offline examples. Select one with `selection`, `action`, or `review`; add `--json` for structured output. The script exits `0` when the examples render and `2` for an invalid contract. Run regression checks with `python3 scripts/test_decision_examples.py`.

Every answer is labeled **SYNTHETIC OFFLINE FIXTURE**. No model is called, no calibration is performed, and the action executor is represented by injected observations. The `0.70` selection cutoff is an explicit fixture setting, not a recommended or calibrated threshold. These examples teach decision boundaries; they do not replace a runtime framework.

## Select an applicable skill or tool

The finite candidate list is supplied by the harness, and the decision names only one listed ID. `no_match` is a valid result when no candidate applies; `unavailable` routes to escalation instead of pretending that missing evidence proves no match. The example validates candidate identity and finite probability shape, while the example cutoff remains policy configuration. Relative ranking alone cannot establish applicability. Real deployments need representative labels for candidate recall, wrong selection, no-match, and abstention under their own candidate set and task distribution.

```sh
python3 scripts/decision_examples.py selection --json
```

## Choose a concrete action and verify it

The action proposal selects from an allowlist and binds its evidence revision to current state. A stale binding is rejected before execution. After a fresh proposal, the deterministic harness checks the observed effect and an independent outcome; a launch error is `unknown`, no effect is `failed`, and an unverified outcome stays `incomplete`. The included observations are fixtures only. Real execution needs the actual authority boundary, reconciliation path, and verifier appropriate to the action.

```sh
python3 scripts/decision_examples.py action --json
```

## Return semantic review to deterministic policy

A semantic review cites evidence IDs and a revision. The harness rejects stale or unbound evidence and returns a structured proposal with `permission: not_granted`. A separate deterministic policy consumes that proposal and the host authorization result. Positive semantic support cannot override host denial; review evidence cannot create permission. In a deployed system, host identity, scope, operation, and resource checks belong at the executor boundary, independently of the model.

```sh
python3 scripts/decision_examples.py review --json
```

## Scope and completion boundary

These examples complete when the selected scenario prints and the focused tests pass. They demonstrate contract shape and negative paths only: they provide no empirical evidence about model quality, calibration, latency, or end-to-end task success. For model-specific decision contracts, answer semantics, evaluation, calibration, and substitution, route to [System One](../../system-one/SKILL.md). For task trajectories, graders, side effects, and end-to-end outcomes, route to [Agent Evals and Observability](../../agent-evals-and-observability/SKILL.md). For the host authority design, continue with [Secure Software Engineering](../../secure-software-engineering/SKILL.md) and the executor's own policy contract.
