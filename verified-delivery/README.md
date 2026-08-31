# Verified Delivery

Deliver an authorized change end to end — implement, verify, merge, and confirm the merged state — without losing the thread when a hard limit interrupts the work.

## Why Install This Skill

End-to-end delivery directives ("fix this, open a PR, and merge when it's green") routinely die halfway: the agent runs out of tool calls, the context window fills, a worker is replaced, or the session ends. The agent reports the remaining steps, and the user has to re-type the whole instruction in a fresh session — hoping nothing was lost in translation.

This skill fixes both halves of that failure. Before any interrupted ending, the agent writes a durable, machine-readable handoff (directive, repository and PR identity, head SHA, completed and pending gated steps, authorization boundary, active watchers) so nothing lives only in the conversation. On the next re-entry, the agent treats the open handoff as a resume: it verifies live repository, PR, CI, review, and watcher state first — read-only — and then continues the next already-authorized gated step on its own. No re-instruction, no re-planning, no guessing.

Just as importantly, the skill never manufactures authority. It preserves explicit boundaries for merge, review, security findings, exact-head verification, non-convergence, and post-merge verification, and it stops at a boundary with the exact reason rather than inferring permission. A "remaining steps" report is never presented as done.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | The authorization boundary, delivery gates, interruption handoff requirement, resumption protocol, and stop-at-boundary rules. |
| `references/interruption-handoff.md` | Handoff field schema, store durability rules, validation and reconciliation rules, and a worked example. |
| `evals/evals.json` | Regression cases covering the interruption-resume signature, the positive control for uninterrupted delivery, and the boundary-stop behaviors. |

## Quick Start

No setup or credentials required. Expose this directory through your agent's standard skills mechanism, then grant an end-to-end directive that names its boundaries, for example:

> Implement the retry-backoff fix, open a PR, and run it end to end: merge when CI is green and reviews are satisfied, then verify the post-merge state.

If the session is interrupted before the delivery boundary, re-enter and simply continue — the agent picks up from the recorded handoff and verified live state.

## Triggers

- A user grants an end-to-end delivery directive for a specific change (implement → PR → merge → post-merge verification).
- A delivery was interrupted by tool-call limits, context exhaustion, worker loss, or a session end, and work is re-entered.
- A session is about to end while an authorized delivery still has gated steps outstanding.
- Deciding whether a remaining-steps report can count as delivery completion (it cannot, without a recorded handoff and an explicit next trigger).

## Requirements

No runtime dependency. Live-state verification works best when the environment can read repository, PR, CI, and review state through the tools the host already provides.
