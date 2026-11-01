# Comment quality and communication

A review comment is a small piece of technical writing with an implied obligation
attached. Most review friction comes from comments whose obligation is unclear:
the author cannot tell whether a remark is a blocker, a preference, or a musing,
so they treat everything as a blocker and the review becomes adversarial.

This file covers severity labels, comment anatomy, tone with evidence, author
responsibilities, disagreement, and the anti-patterns that make review expensive.

## Severity labels

Label every comment. Unlabeled comments are read at the severity the author fears
most.

| Label | Meaning | Author's obligation |
|---|---|---|
| `[blocking]` | The change is not safe to merge as written | Fix, or rebut with evidence and request re-review |
| `[should-fix]` | A real defect or risk that need not block this merge | Fix now, or record a follow-up with an owner |
| `[nit]` | Preference or polish; not a defect | Take it or leave it |
| `[question]` | The reviewer cannot tell from the diff | Answer; the answer may become a finding |
| `[praise]` | Something worth keeping | None |

Google's guide uses a compatible three-level vocabulary: `Nit:` for polish,
`Optional`/`Consider` for suggestions, `FYI` for information the author is not
expected to act on in this change. Either vocabulary works; mixing them within one
review does not.

Two rules make labels trustworthy:

1. `[blocking]` is about safety, not importance. An important improvement to a
   working system is `[should-fix]`.
2. If you cannot say what evidence would settle a `[blocking]` comment, it is a
   `[question]`.

## Anatomy of an actionable comment

```
- [blocking] <one-sentence claim> — evidence: <path:line or observation> — verify: <test or check>
```

Four elements, in order:

1. **Claim** — what is wrong, in one sentence. If it needs "and", split it.
2. **Evidence** — where you saw it. A path and line, a command output, a failing
   test, or a cited requirement. "This looks wrong" is not evidence.
3. **Impact** — why it matters, when it is not obvious. One clause is enough.
4. **Verification** — how anyone will know it is fixed. Required for blocking
   comments.

Worked contrast:

> **Weak:** This function is too complex, please simplify.

> **Actionable:** `[should-fix]` The retry loop has three exit paths and only one
> clears the timer — evidence: `worker/retry.py:64-91`; the `TimeoutError` branch
> returns at line 88 without `timer.cancel()` — verify: a test that raises
> `TimeoutError` on the second attempt and asserts no active timer remains.

The second comment can be agreed with, disputed, or fixed. The first can only be
resisted.

## Describe the requirement, not the rewrite

The reviewer's job is to identify what is wrong and, when useful, the shape of an
acceptable fix — not to write the author's code in a comment thread. Google's guide
is explicit that fixing the change is the developer's responsibility, and that
pointing out a problem and letting the author decide often produces a better
solution because the author is closer to the code.

Practical test: if your comment is longer than the code it replaces, you have
probably crossed from review into implementation. Offer the direction and let the
author implement it.

## Questions are a legitimate output

"I cannot tell from this diff whether the tenant check happens before or after the
cache lookup" is a useful review contribution. It surfaces missing context, and it
often turns into the most important finding of the review.

Use questions when:

- the behavior depends on code outside the diff,
- the intent could be read two ways,
- you suspect a problem but cannot name the failing input,
- the description and the code disagree.

Do not use a question mark to smuggle in an accusation. "You didn't think about
concurrency, did you?" is a `[blocking]` claim with the evidence removed.

## Tone: what the evidence says

Bacchelli and Bird identify tone and power as sources of review breakdowns, and
cite sentiment evidence that negatively toned comments are less likely to be
useful. Google's guide gives the canonical rewrite:

> **Bad:** "Why did **you** use threads here when there's obviously no benefit to
> be gained from concurrency?"

> **Good:** "The concurrency model here is adding complexity to the system without
> any actual performance benefit that I can see. Because there's no performance
> benefit, it's best for this code to be single-threaded instead of using multiple
> threads."

The mechanical difference: comment on the code, not the person; state the
observation; state the reasoning. This is not politeness for its own sake — a
comment that reads as an attack gets defended against rather than evaluated, which
costs a round trip and sometimes the finding itself.

## Praise is part of the mechanism

Both Google's guide and the Google case study identify mentoring and knowledge
transfer as core functions of review, not side effects. Naming what a change does
well:

- reinforces the behavior you want to see again,
- calibrates the author's sense of what "good" looks like in this codebase,
- makes the critical comments legible as effort rather than hostility.

Praise must be specific to be worth anything. "Looks good" is a verdict, not
praise. "The failure-path test you added for the partial write is exactly the case
that bit us last quarter" is praise.

## Anti-patterns

| Anti-pattern | What it looks like | Cost |
|---|---|---|
| Rubber stamp | "LGTM" on an unread diff | Approval that certifies nothing; the record becomes dishonest |
| Drive-by rewrite | A comment proposing a full alternative design | Discards the author's context; usually ignored or resented |
| Bikeshedding | Long threads on naming while a boundary bug sits unexamined | Attention spent where risk is lowest |
| Scope creep | "While you're in here, also…" | Blocks a correct change on unrelated work |
| Style as policy | Personal preference enforced without a style guide | Inconsistent, unarguable feedback |
| Sarcasm | "Obviously…", "As I already said…" | Escalation, not correction |
| Silent severity | Unlabeled comments the author reads as blocking | Every comment becomes a negotiation |
| Verdict smuggling | A comment that implies approval or rejection without saying so | The recorded verdict contradicts the thread |

## Author responsibilities

Review is a two-party protocol. The author owes:

- **A stated intent** that is not a restatement of the code: what problem, for
  whom, why now.
- **A reviewable change**: small, scoped, with tests in the same change, and
  formatting separated from behavior.
- **Supplied evidence**: the command that proves it works, and its output.
- **A response to every comment**: fixed, deferred with an owner, or rebutted with
  evidence. Resolving a thread without doing any of these is how findings
  disappear.
- **Explanations in the code, not only in the thread.** If a reviewer needed an
  explanation to understand the code, future readers will too; the explanation
  usually belongs in a comment or a simpler implementation.

## Disagreement and escalation

Google's ordering is a good default:

1. **Technical facts over opinions.** Data and evidence outrank preference. On
   style, the project's style guide is the authority; if it is silent, accept the
   author's choice.
2. **Seek consensus** in the thread, using the project's written standards.
3. **Move to synchronous discussion** when the thread is not converging. Record
   the outcome in the review thread so future readers see the decision.
4. **Escalate** — technical lead, code owner, or manager — rather than letting the
   change sit. A stalled review is a worse outcome than a decision you disagree
   with.

## Reviewing people, not just code

- Reviewers with domain ownership give deeper comments. If you are reviewing
  unfamiliar code, say so and ask for context rather than producing shallow
  comments that look authoritative.
- Tone and power asymmetries matter more when the reviewer is senior. A senior
  reviewer's `[nit]` is often read as `[blocking]`; label it explicitly and say
  it is optional.
- Cross-timezone reviews need fast first responses even when the full review
  takes longer. An immediate "I have this, full review by tomorrow 10:00" is worth
  more than silence followed by a perfect review.

## Triaging comments you receive

When you are the author, or a third reviewer resolving someone else's thread:

- Classify each comment before acting: defect, risk, preference, question,
  information.
- Fix or rebut with evidence; do not "acknowledge" and move on.
- If you defer a `[should-fix]`, create the follow-up and link it in the thread.
- If a comment is wrong, say why in one sentence with the evidence, and move on.
  Long rebuttals of wrong comments are a tax on the review.
