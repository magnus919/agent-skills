# Review record — <change title or PR number>

<!-- Copy this file into the review thread, the PR, or a durable record.
     Fill every section; delete these guidance comments before posting.
     Check it with: python3 scripts/review_record_check.py this-file.md -->

## Scope

- Base: <sha or ref>
- Head: <sha or ref>
- Files changed: <n> (+<added>/-<deleted>, <effective lines> effective)
- Attention tier: <small | standard | large | oversized>
- Attention spent: <minutes> of ~<estimated minutes>
- Change type: <feature | fix | refactor | migration | config | docs | dependency | test-only>
- Review authority: <comment-only | approve | approve-and-merge>

## Intent

<What the author says the change does, quoted or linked — not what you assume it does.
 If the stated intent and the diff disagree, that disagreement is itself a finding.>

## Evidence

<!-- One line per thing you actually ran or read. Not "tests pass" — the command and
     its result. Evidence you did not gather is not evidence. -->

- `<command>` — <result, exit status, or observation>
- Read `<path>:<line>` — <what it showed>

## Findings

<!-- One bullet per finding, severity label first. Blocking findings carry both an
     evidence: field and a verify: field, for example:
     - [blocking] Retry loop drops the final error — evidence: `worker/retry.py:88` — verify: `test_retry_keeps_final_error` fails before the fix and passes after
     Describe the requirement; do not rewrite the author's code in the comment. -->

- [should-fix] <what to change> — evidence: <observation or `path:line`>
- [nit] <optional polish> — evidence: <observation or `path:line`>
- [question] <what the diff cannot tell you — ask, do not assert>
- [praise] <what the change does well and should keep>

## Verdict

APPROVE WITH COMMENTS

<!-- Exactly one of: APPROVE | APPROVE WITH COMMENTS | REQUEST CHANGES | NEEDS MORE EVIDENCE -->

## Residual risk

- <What could still be wrong even if every finding is fixed, and why that is acceptable now.>

## Not reviewed

- <Path, behavior, runtime, or environment you did not inspect, and why.
  Write "nothing" only when that is literally true.>
