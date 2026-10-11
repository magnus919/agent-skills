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

## Finite source mutation sensitivity

On 2026-10-10, the existing reference harness was exercised with five actual source-code mutants. Each mutant was applied to a temporary module overlay and run against the existing focused regression tests; the checked-in source was not changed during mutation runs. The unmutated baseline passed all 30 tests.

| Source mutant | Regression outcome |
| --- | --- |
| Bypass current-permission gate | Killed: 1 failing regression case |
| Bypass expected and current record-revision gates | Killed: 2 failing regression cases |
| Bypass command and current policy-version gates | Killed: 2 failing regression cases |
| Bypass exact approved-action gate | Killed: 3 failing regression cases |
| Bypass identical-replay response deduplication | Killed: 1 failing regression case; the replay returns `review` instead of `deduplicated`. The separate executed-state gate still prevents a second write. |
| Equivalent boolean spelling (`is not True` → `is False`) | Passed all 30 focused tests |

The equivalent control is valid because current permission is type-checked as a boolean before reaching the gate. Invalid-mutant outcomes and infrastructure errors are reported separately; both counts were zero. The replay mutation measures response-deduplication sensitivity only; it does not exercise duplicate-write prevention. The result measures sensitivity of this pinned reference test set only. It does not establish production coverage, deployed authority, or closure of the P0 deployment gap.

The mutation runner is `eval_runner/fair_pilot_command_boundary_mutations.py`; its core tests are in `eval_runner/tests/test_fair_pilot_command_boundary_mutations.py`, including a check that overlay execution uses captured test bytes after the backing test file changes. Run the six bounded source mutations with:

```sh
python3 -m eval_runner.fair_pilot_command_boundary_mutations --json
```

Frozen mutation inputs:

| Input | SHA-256 |
| --- | --- |
| `eval_runner/fair_pilot_command_boundary.py` | `b5777c9d7f69e370e3aa96c5b19918d525ba2557514a97b8ed0534485878a7fc` |
| `eval_runner/tests/test_fair_pilot_command_boundary.py` | `a963f2e8184b5c423f4f56d2a3c1e3317737a16dfd652d92f179d6aec98ee8d2` |

## Local verification

The 2026-10-10 follow-up checks ran with Python 3.14.7 in this executor.

Focused harness and mutation tests: 32 passed.

```sh
python3 -m pytest \
  eval_runner/tests/test_fair_pilot_command_boundary.py \
  eval_runner/tests/test_fair_pilot_command_boundary_mutations.py \
  -q --no-cov
```

Core aggregate: 332 passed, 31 subtests passed, and 71.81% total coverage against the 60% threshold. This used every path in `scripts/core-test-files.txt`:

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

Lint (`python3 -m ruff check scripts/ eval_runner/`) and formatting (`python3 -m ruff format --check scripts/ eval_runner/`) passed. Module-level mypy for the new runner and its test passed with `--follow-imports=skip`. The full `python3 -m mypy scripts/ eval_runner/` check could not be reproduced in this system environment: `types-jsonschema` is missing, and the installed NumPy stub uses syntax unsupported by the repository's configured Python 3.10 target.

The aggregate run included the entire `eval_runner/tests/` directory. These are local checks, not a GitHub CI run; CI currently uses Python 3.12.

## Scope and limits

`eval_runner/fair_pilot_command_boundary.py` records writes only in a Python list. It has no connection to production state, authorization services, policy storage, or persistence. It does not test authenticated approver provenance, concurrent requests, cross-process idempotency, transaction isolation, policy-clause correctness, or runtime integration. The scenario does not require authoritative real-policy clauses or production access; if either becomes necessary to state a new requirement, stop this reference-only lane for owner input.

Policy-fidelity work still needs actual clauses and an owner-approved fixture. UX and stakeholder outcomes need real evidence. This mutation batch adds no implementation in those areas.

The work adds no model or Jev calls. `eval_runner/tests/` is already part of the core test route in `scripts/core-test-files.txt`, so no workflow change was needed.

## Source revision note

The command-boundary reference harness and its focused regression tests were integrated through PR #695 on 2026-10-10 at main commit `91e93627542d636d24545427d0d77b112ea1adf3`. This local mutation run used the source and test hashes listed above in a worktree based on cached HEAD `f632ac910ee47c6be1cfece1599872fdc5d1adb6`, descended from `22b4723c549e2851ebae7e739cc5bd980ff4884a`. The pinned source and test blob IDs match that merged main commit. The combined tree's mutation run and test-route inventory were not repeated locally; the follow-up files are applied on a branch from that commit, with integration checked by this pull request's CI. The local mutation result does not establish production authority or runtime behavior.
