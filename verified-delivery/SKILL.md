---
name: verified-delivery
description: >-
  Implement and deliver an authorized change end to end — verify, open the PR, merge,
  and confirm post-merge state — using live-state gates, durable interruption
  handoffs, and live-state-first resumption. Use when a user grants end-to-end
  delivery authority for a specific change and the work may cross tool-call
  limits, context exhaustion, worker loss, or session interruptions before the
  delivery boundary is reached. Do not use for plain fixes with no delivery
  directive, for granting merge or post-merge authority the user did not grant,
  or for designing release pipelines (use release-engineering for that).
license: MIT
compatibility: No runtime dependency.
---

# Verified Delivery

Carry an authorized change from implementation through merge and post-merge
verification through a sequence of live-state gates. Every gate is verified
against the actual state of the repository, PR, CI, and review system before
the next step runs, and every gate verdict is bound to the exact head SHA it
was verified on. Because hard limits (tool-call budgets, context exhaustion,
worker replacement, session interruptions) can end the work before the
delivery boundary is reached, this skill defines a durable interruption
handoff and a resumption protocol that treats the next re-entry as a resume
of the same directive — not a request to restate it.

## Authorization boundary

Delivery proceeds only under an explicit user directive that names the change
and the gates it authorizes. Never infer permission from context, tone, or a
partial handoff.

> Confirm the target, scope, and rollback path before acting. Read-only
> discovery may proceed without confirmation.

Apply this confirmation before the first mutation, including on resumption.
The target names the repository and PR when one exists, the scope names the
next authorized gated steps, and the rollback path states how the next
mutation can be reversed or contained. A handoff records this confirmation;
it does not widen it.

- The directive states which gated steps are authorized (for example: open a
  PR, merge when CI is green and reviews are satisfied, verify post-merge).
- Steps outside the stated boundary stop at their gate with the exact missing
  authorization reported. Asking the user for an explicit new decision is the
  correct response to a gap; acting anyway is not.
- The authorization travels with the work: it is restated verbatim in the
  interruption handoff (below) so a resumed session inherits the same
  boundary, never a wider one.

Preserved boundaries at every gate:

- **Merge boundary** — merge only when merge is explicitly authorized and the
  CI and review gates pass on the exact head being merged.
- **Review boundary** — address review feedback inside a bounded loop; never
  force past unresolved review objections.
- **Security boundary** — security findings from CI or review are gates, not
  warnings; they are never bypassed, weakened, or retried until clean by
  suppression.
- **Exact-head boundary** — all gate evidence binds to the exact head SHA.
  A moved head invalidates prior evidence until it is re-verified on the new
  head.
- **Non-convergence boundary** — after three non-converging fix or review
  passes at any gate, stop and report the evidence.
- **Post-merge verification boundary** — the delivery is not complete until
  the merged state is verified after the merge.

## Delivery gates

Run the gates in order. At each gate, check live state first, then act, then
record evidence bound to the current head SHA.

1. **Change ready** — implementation complete and local verification passes
   at the working head.
2. **PR open** — the PR exists and its identity and head SHA are recorded.
3. **CI green** — CI passes on the exact PR head SHA.
4. **Review satisfied** — review requirements of the repository's policy are
   met on the exact head SHA.
5. **Merge** — only when gates 3 and 4 hold on the exact head and merge is
   within the granted authorization.
6. **Post-merge verification** — the merged state is confirmed (branch,
   PR status, post-merge checks) before any completion claim.

## Interruption handoff

Any ending — session end, turn end, worker shutdown, or an approaching hard
limit — while a delivery directive is still authorized and gated steps remain
must first record a durable handoff. Ending with remaining steps and no
durable handoff is a protocol failure, even if the remaining steps are
reported clearly. A remaining-steps report is never terminal success for an
end-to-end directive.

The handoff is machine-readable JSON stored durably: by default as a file at
`.verified-delivery/handoff.json` in the repository working tree, excluded
locally from Git and checked as untracked before every commit; alternatively
in a fenced machine-readable block in the PR description after confirming
that external disclosure and its rollback path, or in host-provided durable
storage when configured. The record names its own store. Durability means the
next re-entry can find and read it without user assistance.

Required fields — `schema` (handoff schema version), `status` (`open` or
`closed`), `store` (durable location), `directive` (verbatim user directive),
`authorization_boundary` (gates authorized, and anything explicitly out of
scope), `repository` (remote identity), `pull_request` (PR identity or null),
`branch` (delivery branch), `head_sha` (head at handoff time),
`completed_steps` (gates done, with SHA-bound evidence), `pending_steps` (next
authorized gated steps in order), `watchers` (active watcher, process, or
worker identifiers, or empty), `stop_reason` (observed interruption class),
and `updated_at`. The full field schema, durability rules, and worked examples
are in
[references/interruption-handoff.md](references/interruption-handoff.md).

## Resumption on re-entry

Re-entry means a new session, turn, or worker touching the repository while a
handoff with `status: open` exists. Scan the documented store locations at
re-entry. An open handoff makes the re-entry a resume of the recorded
directive: do not ask the user to restate or repeat the instruction, and do
not re-plan from scratch.

First action: read-only live-state verification. No mutation before it
completes.

1. Repository — the remote matches the handoff's `repository`; branch state
   is identified.
2. PR — it exists, is open, and its head SHA is compared with the handoff's
   `head_sha`.
3. CI — status on the exact head.
4. Reviews — state against the repository's policy on the exact head.
5. Watchers — whether recorded watchers, processes, or workers are still
   alive; never spawn a duplicate of a live one.

Then continue with the next already-authorized gated step. Gate evidence
recorded in the handoff stays valid only for the head it was verified on.
If the head moved (new commits, rebase, force push), reconcile first: fetch,
re-verify CI and review on the new head, update the handoff's `head_sha`, and
only then continue. Mutations — commits, pushes, merges, comments — happen
only after verification.

## Stop at the boundary

Stop and report the exact reason, taking no further action, when:

- there is no directive and no open handoff (treat the input as a fresh
  request, not a resume);
- the handoff is corrupt — unparseable, missing required fields, or
  internally inconsistent;
- the handoff is stale — the PR was closed without the recorded change,
  rolled back, merged with a conflicting head, the repository does not match,
  or the recorded authorization no longer applies; a matching completed merge
  with authorized post-merge verification pending is reconciled and resumed;
- authorization for the next step is absent or ambiguous;
- live state is ambiguous — a gate result or the merge state cannot be
  determined.

Never infer permission from a partial or stale handoff. The stop report
states what was found, what could not be verified, and the exact reason for
stopping.

## Closing an end-to-end directive

- **Delivery boundary reached** — close the handoff (`status: closed`) and
  report the SHA-bound evidence for the boundary.
- **Steps remain** — record the handoff first, then close with a message that
  names the handoff store and the explicit next trigger: the next re-entry
  resumes the directive. This is the only acceptable way to end with steps
  outstanding.

## Runtime honesty

No skill content can force a host runtime to continue past a hard tool-call
or context limit, and this protocol never promises that. What it guarantees
is observable behavior: a durable handoff written before the limit lands, and
a resumption path that the next re-entry can follow from verified live state.
Do not claim that the runtime will resume automatically — the next trigger is
an explicit re-entry.

## Completion and exit conditions

Exit when one of these holds:

- the delivery boundary is reached, the handoff is closed, and the evidence
  is reported; or
- work stopped at a boundary, the exact reason is reported, and — when steps
  remain — an open durable handoff exists.

After three non-converging passes at any gate, stop and report rather than
looping.

## When not to use

Do not use this skill for a plain fix, refactor, or review that carries no
end-to-end delivery directive — a normal change workflow is the nearest
alternative. Do not use it to design release pipelines, trains, or
progressive-delivery mechanics — use [release-engineering](../release-engineering/SKILL.md).
Do not use it to manufacture authority: this skill executes only what the
user explicitly granted.

## Related skills

- [release-engineering](../release-engineering/SKILL.md) — release pipeline
  mechanics, progressive delivery, and rollback planning beyond a single
  authorized change.
- [verification-methodology](../verification-methodology/SKILL.md) — evidence
  and verdict standards for the live-state checks at each gate.

## Reference files

| Reference | When to load |
|-----------|-------------|
| `references/interruption-handoff.md` | You are recording, locating, validating, or reconciling an interruption handoff — field schema, durability rules, and worked examples |
