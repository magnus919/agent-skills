# Verdicts, evidence, and approval authority

A verdict is the most consequential sentence a reviewer writes. It authorises
someone else to ship. It is also the sentence most often written carelessly,
because the tooling makes approval a button and the social pressure makes
withholding it expensive.

This file defines what each verdict claims, what evidence justifies it, and when
an approval stops being valid.

## Verdict semantics

| Verdict | What it asserts | What it does not assert | Preconditions |
|---|---|---|---|
| `APPROVE` | The scope examined is correct and complete enough for the decision at hand | That the change is correct, or that unexamined scope is fine | No open blocking findings; residual risk and unreviewed scope recorded |
| `APPROVE WITH COMMENTS` | The change may merge now; the remaining comments do not need to block | That the comments will be ignored, or that they are unimportant | No open blocking findings; each non-blocking comment has an owner or a disposition |
| `REQUEST CHANGES` | At least one finding must be fixed before merge | That the whole change is wrong | Every blocking finding has evidence and a verification method |
| `NEEDS MORE EVIDENCE` | You cannot decide, and you can name what is missing | That the change is suspect | The specific evidence gap and who can supply it |

Google's "LGTM With Comments" is the same idea as `APPROVE WITH COMMENTS`, with an
explicit requirement: say which comments you expect to be addressed and which are
optional. An approval that leaves the author guessing about unresolved comments is
not a lighter verdict, it is a deferred argument.

### Choosing between APPROVE WITH COMMENTS and REQUEST CHANGES

Ask one question: *if this merged exactly as it is, would I be comfortable being
named as the reviewer?*

- Yes, and the comments are polish, questions, or follow-ups → `APPROVE WITH
  COMMENTS`.
- No, because a specific defect or risk remains → `REQUEST CHANGES`, and that
  finding is `[blocking]`.

The most common review failure is using `APPROVE WITH COMMENTS` to avoid the
social cost of blocking. The second most common is blocking on a preference. Both
destroy the signal value of the verdict.

## Evidence: what counts

Rank evidence by how directly it shows the claimed behavior:

| Rank | Evidence | Example |
|---|---|---|
| 1 | Executed behavior | You ran the test or the endpoint and observed the result |
| 2 | Reproducible check derived from the requirement | A failing test written from the spec, run against the change |
| 3 | Direct source reading | You read the code path and traced the data |
| 4 | Author-supplied artifact | CI output, benchmark, screenshot |
| 5 | Inference from convention | "This pattern usually means…" |

Rank 4 is legitimate but weaker than it looks: a green CI run proves the pipeline
passed, not that the behavior is correct, and a benchmark proves what it measured,
not what the change affects. Rank 5 is a hypothesis; write it as a question.

Two failure modes to name explicitly in the record:

- **Author-supplied evidence presented as reviewer-verified.** Say "author reports"
  when the author reports.
- **Coverage implied by silence.** If you did not run it, say you did not. A record
  that lists only what you checked is honest; one that omits the gap is not.

## Independence

The reviewer must be a different person from the author, and — for anything above
the routine tier — should not be the same model session that produced the change.
Independence is about uncorrelated errors, not about ceremony:

- A reviewer who already knows the author's rationale anchors on it. That is often
  useful (context is the main review bottleneck) and always a bias worth naming.
- A model reviewing its own output shares its priors and its blind spots. It is not
  independent verification, whatever its confidence.
- A second human who shares the author's assumptions is only partly independent.
  Check the oracle, not just the verdict.

## Approval authority

- **Ownership is not approval.** A code owner can require review; only a reviewer
  who examined the change can approve it.
- **Specialist sign-off is scoped.** A security or privacy reviewer approves the
  security or privacy aspects they examined, not the change as a whole. Record the
  scope of each sign-off rather than aggregating them into one green check.
- **Approval cannot be delegated to a tool.** Linters, coverage gates, and model
  reviewers produce evidence; a person remains accountable for the decision.
- **The approver must be reachable.** An approval from someone who has left the
  team, or who approved a materially different revision, is not an approval.

## When an approval lapses

An approval covers the revision the reviewer examined. It lapses when:

- The change is materially altered after approval — new files, new dependencies,
  changed contracts, changed error semantics.
- A rebase or force-push changes the diff. Confirm the approved commit is an
  ancestor of what merges.
- The base branch moved in a way that changes the assumptions (a dependency
  upgrade, a schema change, a policy change).
- The evidence expired — a test suite that passed a week ago on a different base
  is stale evidence for a merge today.

Say that the approval lapsed, and re-review the delta. "It was approved
yesterday" is how unreviewed code ships.

## Emergencies

Google's guide allows relaxed quality in a genuine emergency and defines one
narrowly: a change that must go in immediately to resolve a production problem,
where waiting would cause more harm. An urgent deadline is not an emergency.

If you use the emergency path:

- Name it as an emergency in the record, with the production impact that justified
  it.
- Review what you can — scope, blast radius, rollback — even if the full pass is
  deferred.
- Schedule the deferred review and record it as an open item. An emergency review
  that is never revisited becomes the new normal.

## The record

A verdict without a record is an assertion without scope. The record states:

1. **Scope** — base, head, files, tier, time spent, authority, coverage.
2. **Intent** — what the change claims to do, and where that claim comes from.
3. **Evidence** — what was run or read, and what was not.
4. **Findings** — labeled, with evidence and verification for blocking items.
5. **Verdict** — one of the four, consistent with the findings.
6. **Residual risk** — what could still be wrong and why that is acceptable now.
7. **Not reviewed** — explicit gaps.

`templates/review-record.md` is the fillable form;
`scripts/review_record_check.py` enforces completeness and verdict consistency.
The checker cannot judge whether your findings are true — only that the record is
not self-contradictory.

## Partial coverage

`Coverage: full` means every changed unit was read. `Coverage: partial (unit 1 of 3)`
means exactly that, and it changes what a verdict can assert.

Approving with partial coverage is only honest when another named reviewer covered the
remainder. Otherwise the remainder is unexamined, and the verdict is
`NEEDS MORE EVIDENCE` with the missing evidence named — not `APPROVE WITH COMMENTS`.
Google's reviewer guide allows an "LGTM with comments" after confirming other reviewers
covered other parts, but the confirmation has to exist in the thread.

The record checker warns when a partial review carries an approving verdict, so the
claim is at least visible to whoever reads the record later.

## Residual risk is not a disclaimer

"Residual risk: none" on a T3 change is almost always false, and it teaches
readers to skip the section. Write the specific residual risks:

- behavior that cannot be exercised outside production,
- a concurrency property that was reasoned about but not tested,
- a migration validated on a sample rather than full volume,
- a dependency whose upstream behavior is trusted but not audited,
- an operational path (rollback, on-call response) that was not rehearsed.

Each line should say why it is acceptable *now* — and what would make it
unacceptable, which is often the trigger for revisiting the decision.

## Failure modes this file exists to prevent

- A verdict that contradicts the findings in the same review.
- An approval that silently covers unexamined scope.
- A specialist sign-off read as whole-change approval.
- An approval that outlived the revision it approved.
- "Approved with comments" used to avoid blocking a real defect.
- A record with no evidence, written after the fact to satisfy a process.
