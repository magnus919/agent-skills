# Review record — PR #900 (retry scheduling rework)

<!-- Counterexample fixture for eval `audit-partial-approval-record`.
     The record is intentionally flawed: it approves a change it did not fully
     read, cites no executed evidence, and dismisses residual risk without basis.
     It is not a model of a good record; see templates/review-record.md for that. -->

## Scope

- Base: `1a2b3c4`
- Head: `9d8e7f6`
- Files changed: 14 (+742/-460, 1,202 effective lines)
- Attention tier: large
- Attention spent: ~25 minutes of ~240 estimated
- Coverage: partial (unit 1 of 3: worker/retry.py)
- Change type: refactor
- Review authority: approve-and-merge

## Intent

"Rework retry scheduling so exhausted batches surface the last error instead of returning
None, and make the retry budget configurable."

## Evidence

- Read `worker/retry.py` — the new branch structure looks correct.

## Findings

- [nit] `attempt_idx` could be named `attempt_number` for consistency with the scheduler module.
- [praise] The refactor separates the backoff calculation from the retry loop.

## Verdict

APPROVE WITH COMMENTS

## Residual risk

- None — the code I read was fine.

## Not reviewed

- Units 2 and 3 (the scheduler config and the docs updates).
