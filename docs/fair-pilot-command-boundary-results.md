# Non-chat proposal command-boundary mechanics

## Evidence classification

This is deterministic **reference contract/mechanics evidence** for the open `pydanticai/non-chat-proposal` P0 case. It is not production runtime evidence, does not close the P0 deployment gap, and does not establish the behavior of a deployed application.

The frozen v2 pilot evidence contract requires command-time permission, expected/current record revision, exact approved action, and policy version to match. A permission revocation or stale revision returns the item to review without execution. This change adds a small in-memory model and isolated tests for those mechanics; it does not edit the frozen pilot contract, dossier, historical results, or pinned PydanticAI reference.

The harness receives an `Approval` as a trusted, application-owned fixture. It does not authenticate the approver, verify approval provenance, or query an application approval registry. That trust assumption is explicit and remains outside this reference evidence.

## Bounded outcomes

The action is limited to non-empty, trimmed string identifiers and version fields. Parameters are immutable key/value string tuples, sorted by key; duplicate or empty keys and non-string values are rejected before comparison. Approval, command, completion-cache, and write records each receive an independent action snapshot.

The tests assert outcomes against literal expected status, reason, write count, and payload values:

| Condition at command time | Expected outcome | In-memory writes |
| --- | --- | ---: |
| Permission revoked | Return to review | 0 |
| Current record revision changed | Return to review | 0 |
| Command's expected revision differs from approved revision | Return to review | 0 |
| Current policy version changed | Return to review | 0 |
| Command policy version differs from approved version | Return to review | 0 |
| Approval ID, operation, target, or parameter differs | Return to review | 0 |
| Malformed command or current permission | Return to review before equality | 0 |
| Empty required ID or version, mutable nested parameter, or non-string parameter value | Reject input before execution | 0 |
| Equal action built independently with parameters in a different order | Execute canonical approved action | 1 |
| All values match | Execute approved action | 1 |
| Identical completed command is replayed after permission revocation | Return deduplicated result | Still 1 |
| Completed idempotency key is reused with a different action | Return to review | Still 1 |

The post-approval changes are meaningful negative mutations. The independently constructed, reordered equal action is a harmless positive control. A rejected approval remains in review even if the old record value is restored, so the harness cannot silently revive that approval.

## Local verification

Checks ran with Python 3.14.7 from the available repository virtual environment:

Focused test: 30 passed.

```sh
python3 -m pytest eval_runner/tests/test_fair_pilot_command_boundary.py -q --no-cov
```

Core aggregate: 330 passed, 31 subtests passed, and 71.88% total coverage against the 60% threshold. This used every path in `scripts/core-test-files.txt`:

```sh
python3 -m pytest \
  scripts/test-eval-validation.py scripts/test-eval-coverage.py \
  scripts/test_check_skill_tests.py scripts/test_core_test_selection.py \
  scripts/test_check_catalog_set.py scripts/test_validate_case_checklist.py \
  eval_runner/tests/ docs/experiments/agent-ui/test_synthetic_matrix.py \
  docs/experiments/agent-ui/test_live_fixture.py \
  -q --durations=10 --cov=scripts --cov=eval_runner \
  --cov-fail-under=60 --cov-report=term
```

Lint (`python3 -m ruff check scripts/ eval_runner/`), formatting (`python3 -m ruff format --check scripts/ eval_runner/`), and typing (`python3 -m mypy scripts/ eval_runner/`) all passed.

The aggregate run included the entire `eval_runner/tests/` directory. It was local verification, not a GitHub CI run; CI currently uses Python 3.12.

## Scope and limits

`eval_runner/fair_pilot_command_boundary.py` records writes only in a Python list. It has no connection to production state, authorization services, policy storage, or persistence. It does not test authenticated approver provenance, concurrent requests, cross-process idempotency, transaction isolation, policy-clause correctness, or runtime integration. The scenario does not require authoritative real-policy clauses or production access; if either becomes necessary to state a new requirement, stop this reference-only lane for owner input.

The work adds no model or Jev calls. `eval_runner/tests/` is already part of the core test route in `scripts/core-test-files.txt`, so no workflow change was needed.

## Source revision note

This local commit remains based on cached `22b4723c549e2851ebae7e739cc5bd980ff4884a`; it is not integrated with current main at `42b3086c5d68bcba4b012c8f6bc19fe562ce6c62`. The publisher will apply these files on current main and use its full remote CI to establish integration. Local checks here do not establish compatibility with that current base.
