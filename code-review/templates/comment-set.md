# Comment set — <PR number or change title>

<!-- Use this sheet before posting. It forces each comment to say what kind of
     claim it is, what evidence supports it, and whether it blocks the change.
     Post the bullets; keep the sheet if the review is consequential. -->

## How to read the labels

| Label | Meaning | Author's obligation |
|---|---|---|
| `[blocking]` | The change is not safe to merge as written. | Fix, or rebut with evidence and ask for re-review. |
| `[should-fix]` | A real defect or risk that does not have to block this merge. | Fix now or record a follow-up with an owner. |
| `[nit]` | Preference or polish. Not a defect. | Take it or leave it; do not negotiate at length. |
| `[question]` | You cannot tell from the diff. | Answer; the answer may become a finding. |
| `[praise]` | Something worth keeping. | Nothing. This is calibration, not flattery. |

Rules that make the set usable:

1. One claim per comment. If it needs "and", split it.
2. Every `[blocking]` and `[should-fix]` names its evidence — a path and line, a command output, a failing test, or a cited requirement.
3. Every `[blocking]` names how the fix will be verified.
4. No comment asks for a rewrite you would not review yourself.
5. Nits are labeled nits. Unlabeled preferences get treated as blocking by authors, which is how review becomes adversarial.

## Comments

- [blocking] <Claim in one sentence.> — evidence: `<path>:<line>` / <observation> — verify: <test or check>
- [blocking] <Claim.> — evidence: <...> — verify: <...>
- [should-fix] <Claim.> — evidence: <...>
- [question] <What the diff cannot tell you.>
- [nit] <Optional change, and why it is optional.>
- [praise] <What the change does well.>

## Worked examples

**Too vague to act on**

> This function is too complex, please simplify.

**Actionable, with a boundary**

> [should-fix] The retry loop has three exit paths and only one clears the timer. — evidence: `worker/retry.py:64-91`; the `except TimeoutError` path returns without `timer.cancel()` — evidence: `worker/retry.py:88` — verify: a test that raises `TimeoutError` on the second attempt and asserts no active timer remains.

**Preference stated as preference**

> [nit] I would inline `parse_header` since it has one caller. Your call — the named version reads fine too.

**Question instead of an assertion**

> [question] Is 3 the intended attempt cap for batch jobs too, or should batch keep retrying until the deadline? The caller at `batch/runner.py:52` passes no cap.

**A blocking claim that is actually blocking**

> [blocking] The new endpoint authorizes on the session tenant but not the path tenant, so a user in tenant A can read tenant B's report by changing the ID. — evidence: `api/reports.py:41` compares `session.tenant` only; `repo/load_report` accepts any `report_id` — verify: an integration test that authenticates as tenant A and requests tenant B's report ID, expecting 404.

## After posting

- [ ] Every blocking comment has an evidence and verify field
- [ ] No comment states a verdict the record does not
- [ ] Questions are questions, not assertions with a question mark
- [ ] Praise is present when the change earned it
