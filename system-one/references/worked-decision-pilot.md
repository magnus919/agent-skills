# Worked pilot: from a useful judgment to a release decision

This is an illustrative design exercise, not a measured Jev or Laya result.
Use it to choose and evaluate one bounded decision in an existing workflow.
Apply the same steps to another provider only after checking its current
answer contract, input limits, data boundary, and model identity. For
primitive semantics and metrics, read `concepts-and-patterns.md` and
`evaluation-and-calibration.md`.

## 1. Separate the jobs before choosing a model

Suppose a support team receives many messages and currently routes them by
rules plus human review. The same workflow writes replies, detects refund
requests, and reports refund totals. Compare the *jobs*, not model brands:

| Job | Suitable path | Reason |
|---|---|---|
| Match an exact order ID and calculate a refund total | Code against authoritative records | Exact lookup and arithmetic have a determinate answer. |
| Choose `billing`, `technical`, `account`, or `other` for a message | Candidate Choice judgment | A bounded semantic label can be checked against independent human labels. |
| Detect whether a message asks for a refund | Candidate Noul judgment | A single proposition can help tag records; tags must be evaluated before counts are trusted. |
| Write a helpful reply | Generative stage with human or policy checks | The output is open-ended text, not a typed decision. |
| Approve and send a refund | Authorized code and accountable human process | Eligibility, amount, payment state, and authority cannot come from model probability. |

Start with **queue choice** if volume, errors, and review cost make it worth
testing. Do not assume the candidate beats the current rules. Define the
baseline's cost and error rate before enabling the model.

## 2. Write a contract that can fail safely

Use `templates/decision-contract.md` to record the following concrete fields:

| Field | Example contract |
|---|---|
| State | Redacted subject and latest customer message, supported language, source timestamp; no payment credentials or expected label. |
| Question | ID `queue_v1`, Choice: “Which team should first review this customer request?” |
| Options | `billing`, `technical`, `account`, `other`; define each queue's scope in criteria. |
| Policy | Validate answer ID, type, full option set, finite distribution, pinned model. Apply a threshold fitted for **wrong-queue cost**; send `other` or insufficient evidence to review. |
| Side effect | Assign a queue only after deterministic account permissions and routing checks; never send a reply or refund from this answer. |
| Failure | Timeout, missing state, unsupported language, malformed output, or model mismatch takes the current safe routing or human queue. |

`other` is a real answer, not a low-confidence synonym. A high-confidence
wrong queue is still wrong. Choice's reported `confidence` and the selected
option's probability are different fields; neither is a calibrated policy
threshold until tested on the target population. Keep exact question wording,
model revision, state serialization, and policy revision with every result.

## 3. Freeze evidence before tuning

Collect approved, redacted messages that reflect the actual incoming mix.
Independently label the correct first queue, allowing reviewer disagreement
and `other`; keep a separate set enriched for rare but costly wrong routes.
Split by time or source to avoid near-duplicate leakage. Freeze a final test
set before editing criteria or thresholds. Never transmit labels to the model
in the state. For each split, record language, channel, known queue, whether
rules already handled it, and the outcome of the current process.

Run the candidate in shadow mode. On the calibration split, choose a threshold
and review lane based on the cost of a wrong automatic assignment and the
volume a human queue can absorb. On the untouched test split, report:

- confusion counts including `other` and invalid responses;
- wrong automatic assignments per queue and slice;
- accepted-decision coverage and accuracy at the frozen threshold;
- probability calibration where the field has a defined event, plus repeated
  identical-input variance as a *separate* measure;
- end-to-end time and cost including network, queues, retries, and review;
- comparison with current rules and human-routing outcomes.

If labels are disputed, report that disagreement instead of forcing a false
single answer. A challenge set can reveal failure modes, but its intentionally
high share of hard cases cannot estimate normal-workload prevalence. If the
candidate does not improve the chosen outcome at acceptable risk and review
load, keep it in shadow or reject it. A high provider score does not change
that decision.

## 4. Apply the same logic to a QA runner

A test suite is a useful counterexample to “replace every step with a model.”
Freeze representative journeys and tag each step by its actual path:

| Path | What to measure | Failure that matters |
|---|---|---|
| Validated selector replay | Hit rate and replay time | A stale selector silently targets the wrong element. |
| Typed resolution on a changed page | Correct target, abstention, review, and latency | The model confidently proposes a wrong or now-stale target. |
| Visual or generative stage | Success, latency, cost, and review | Text-only state omits a pixel-only control or generated text changes the test's meaning. |
| Exact assertion in code | Correct pass/fail against authoritative values | A test replaces arithmetic or dates with semantic judgment. |

Report the share of steps taking each path and total journey time, including
fallbacks. Then compare failure detection and run-to-run stability on the
*same build* and on builds with known defects. Repeated runs on an unchanged
build test variance; seeded defects test whether the suite catches regressions.
Record selector before/after, page evidence, decision revision, reviewer, and
rollback for each proposed repair. A faster model call alone does not show a
faster or more trustworthy test suite. See `qa-automation-pattern.md` for the
routing details.

## 5. Decide whether a semantic CI check can block

Consider the rule “An error message tells the user what to do next.” First
keep exact checks in code: message exists, localization key resolves, and
required fields are present. A bounded Noul question may judge whether the
displayed message gives a usable next step. The expected answer comes from
reviewers applying a written rubric to real changes, not from the candidate
model or its explanation.

Build cases where a next step is clear, vague, missing, misleading, or only
present in unrelated surrounding text. Include different languages and
product areas. Keep `not_shown` distinct from a proven violation when the
changed artifact lacks enough context. Compare the model's suggestions with
reviewers and the current lint process on a frozen set. Measure false blocks,
false passes, abstentions, review burden, and stability after rubric or model
changes. Start with non-blocking review notes. Promote to a required gate only
when the accountable owner has set an acceptable false-block and false-pass
budget, independent held-out results meet it, missing evidence cannot pass,
and a rollback/disable path is rehearsed. See `use-case-patterns.md` and
`evaluation-and-calibration.md` for the broader gate rules.

## Stop rule

The pilot ends with a written `adopt`, `shadow`, `investigate`, or `reject`
decision in `templates/benchmark-record.md`, backed by the frozen manifest,
baseline, observed outcomes, known failures, owner, and rollback trigger. If
the labels, source boundary, or target action are still undefined, do not
invent a confidence threshold to compensate.
