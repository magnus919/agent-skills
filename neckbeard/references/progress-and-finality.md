# Progress and Finality

How to judge whether work is advancing, when to keep going, when a bounded
check of an asynchronous dependency is justified, and when to stop or
escalate. One rule governs every section: **decide on semantic state — never
on elapsed time, iteration counts, timestamps, request IDs, or how many times
the same state has been observed.**

## Semantic progress, not iteration count

Progress means the world changed in a way that moves an acceptance criterion
forward: a changed artifact, a confirmed or falsified hypothesis, a new stage,
a changed dependency state, or a new output cursor from an asynchronous
system. An advancing timestamp, a fresh request ID, a poll counter, or the
continued existence of a process is *volatile churn* — it is not progress and
must never be recorded as evidence of progress.

Judge churn by content, not by source. A heartbeat whose only change is its
timestamp is churn. But a heartbeat that carries an advancing payload — a new
phase or step, a processed-item count, a new output cursor — is reporting
semantic state: record that payload in the declared semantic state, and it
counts as progress. The timestamp itself stays out of the fingerprint either
way.

The failure mode this page prevents is not "too many turns." It is repeated
observation of an unchanged semantic state while the declared stage action
remains untaken.

## The dependency contract

When a stage hands off to an asynchronous system, record — in the change
contract and the evidence ledger — whether a dependency is required for the
next stage:

- **Accepted/finished output with no required dependency:** the next action is
  to advance or deliver, or to declare the run terminal-complete. A status
  poll before that action is never justified.
- **A pending or failed dependency explicitly required for the next stage:**
  a bounded check is justified once (see below). Required-or-not is part of
  the contract, not something to re-derive mid-run.

Treat `accepted`/`finished` as a stage output, not automatically as whole-run
completion. Terminality is declared only when the contract has no required
dependency left.

## Bounded checks

One infrastructure check per normalized state fingerprint. The fingerprint is
computed from: stage, deliverable state, dependency state, whether the
dependency is required, and the declared semantic state. Volatile fields —
timestamps, request IDs, raw poll counters — are excluded from the
fingerprint, so a timestamp-only heartbeat difference is unchanged state. An
advancing heartbeat payload (a new phase, step count, or output cursor)
belongs in the declared semantic state; when it advances, the fingerprint
changes and the new state receives its own check allowance.

- First observation of a fingerprint: one check is allowed.
- The fingerprint changes (pending → succeeded, or a new output cursor):
  continue; the new fingerprint gets its own check allowance.
- The fingerprint is unchanged: do not re-check. Change the mechanism or
  escalate. An identical re-poll is a finality failure even when the
  timestamp and request ID differ.

## Complex work

There is no arbitrary turn cap. Continue while each turn produces new
evidence or a changed semantic state and at least one acceptance criterion
remains unmet. Multi-turn diagnosis, design iteration, and long test loops
are productive work when the semantic state keeps changing; a turn-count
ceiling must never stop them.

## Active-process ledger

The evidence ledger stays canonical. When work is asynchronous — or an
escalation is being considered — extend the run's record with an
active-process entry:

| Field | Content |
|---|---|
| `id` | Stable identifier for the asynchronous hand-off. |
| `status` | Current normalized state. |
| `output` | Latest meaningful output or artifact reference. |
| `normalized_state` | Fingerprint inputs: stage, deliverable state, dependency state, dependency-required flag, semantic state. |
| `dependency_required` | Whether the dependency gates the next stage. |
| `next_action` | The declared stage action: `work`, `check`, `advance`, `deliver`, `complete`, `mechanism_change`, or `escalate`. |
| `expected_transition` | What the next *semantic* change would look like. |
| `checks_for_state` | How many checks this fingerprint has consumed. |
| `escalation_trigger` | The condition under which the next unchanged observation escalates. |

## Examples

**Accepted but not blocked.** The deliverable is accepted; a publish job is
pending, but nothing requires it before delivery. Correct: deliver or
complete now. Wrong: check the publish job first.

**Genuinely pending dependency.** The delivery stage requires a published
release. One check is spent; the next observation shows the dependency
succeeded with a new output cursor. Correct: proceed to delivery. If the
observation had been unchanged, the correct move is a mechanism change or
escalation — not a second check.

**Productive multi-step work.** Three turns on an in-progress deliverable,
each with a new hypothesis, benchmark, or artifact, ending in verification
and delivery. Correct at any length: every turn changed the semantic state.

**Identical re-poll (failure).** Two observations with identical semantic
state but different timestamps and request IDs, with a check on each, while
the delivery action stays untaken. This fails finality: the second check was
an identical re-poll; the response to the unchanged result should have been a
mechanism change or escalation.

## Non-portable examples excluded

Keep this contract harness-neutral. Do not express the rules in terms of
specific tool names, scheduler or cron identifiers, process IDs, platform API
names, or any vendor's polling semantics. Describe state, dependencies,
actions, and terminality; each harness maps them to its own mechanisms.
