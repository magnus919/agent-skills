# Interruption Handoff Reference

Field schema, durability rules, validation, and worked examples for the
verified-delivery interruption handoff. Load this file when recording,
locating, validating, or reconciling a handoff.

## Store locations and durability

A handoff is durable when the next re-entry can find and read it without user
assistance. Choose the first available store:

1. **Repository working-tree file (default).** `.verified-delivery/handoff.json`
   in the repository root. Keep it untracked so it never becomes part of the
   delivered change. Survives session and worker replacement on the same
   working tree.
2. **PR description block.** A fenced machine-readable block in the PR
   description, usable when a PR exists and working-tree state may not
   survive (ephemeral runners, disposable containers). Survives local loss
   because it lives on the forge.
3. **Host-provided durable storage**, when the host documents a store that
   survives session and worker replacement.

The handoff's `store` field names the location actually used. On re-entry,
scan in the same order; the first open handoff found governs. Never rely on
volatile session memory, chat scrollback, or a stale copy in a screenshot or
summary as the handoff store.

## Field schema

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `schema` | string | yes | Literal `verified-delivery/handoff-v1` |
| `status` | string | yes | `open` while steps remain; `closed` at the delivery boundary or an authorized stop |
| `store` | string | yes | Where this record lives (path, PR block, or host store name) |
| `directive` | string | yes | The user's delivery directive, verbatim |
| `authorization_boundary` | object | yes | `authorized`: gated steps granted; `out_of_scope`: steps explicitly withheld |
| `repository` | string | yes | Remote identity of the repository (remote URL or `host/org/repo` form) |
| `pull_request` | string or null | yes | PR identity, or `null` before a PR exists |
| `branch` | string | yes | Delivery branch name |
| `head_sha` | string | yes | Full head SHA at handoff time |
| `completed_steps` | array | yes | Gates completed; each entry names the gate, its verdict, and SHA-bound evidence |
| `pending_steps` | array | yes | Next authorized gated steps, in order |
| `watchers` | array | yes | Active watcher, process, or worker identifiers; empty array when none |
| `stop_reason` | string | yes | Observed interruption class: `tool-limit`, `context-limit`, `worker-loss`, `session-end`, `user-pause`, `boundary-stop` |
| `stop_detail` | string | no | Exact reason when `stop_reason` is `boundary-stop` |
| `updated_at` | string | yes | UTC timestamp of the last update |

## Example: open handoff at a tool-limit interruption

The directive authorized implementation, PR creation, merge when green, and
post-merge verification. The session hit the tool-call limit after opening
the PR and starting CI, with a CI watcher running.

```json
{
  "schema": "verified-delivery/handoff-v1",
  "status": "open",
  "store": ".verified-delivery/handoff.json",
  "directive": "Implement the retry-backoff fix, open a PR, and run it end to end: merge when CI is green and reviews are satisfied, then verify post-merge state.",
  "authorization_boundary": {
    "authorized": ["open-pr", "merge-when-green", "post-merge-verify"],
    "out_of_scope": []
  },
  "repository": "git.example.com/example-org/example-repo",
  "pull_request": "<pr-number>",
  "branch": "fix/retry-backoff",
  "head_sha": "<40-character-head-sha>",
  "completed_steps": [
    {
      "gate": "change-ready",
      "verdict": "pass",
      "evidence": "local verification suite passed at head <40-character-head-sha>"
    },
    {
      "gate": "pr-open",
      "verdict": "pass",
      "evidence": "PR <pr-number> open with head <40-character-head-sha>"
    }
  ],
  "pending_steps": [
    "ci-green",
    "review-satisfied",
    "merge",
    "post-merge-verify"
  ],
  "watchers": ["ci-watch:pr-<pr-number>@head-<40-character-head-sha>"],
  "stop_reason": "tool-limit",
  "updated_at": "<utc-timestamp>"
}
```

Placeholder values in angle brackets stand in for real identifiers; a real
handoff carries the actual values.

## Closing the handoff

- **Delivery boundary reached:** set `status` to `closed`, move the
  post-merge evidence into `completed_steps`, and empty `pending_steps`.
- **Authorized stop with steps remaining** (for example, the non-convergence
  boundary): set `stop_reason` to `boundary-stop`, describe the exact reason
  in `stop_detail`, keep `pending_steps` as recorded, and leave `status`
  `open` only if resumption remains authorized; otherwise close it.
- A closed handoff never resumes. A new directive is a new delivery.

## Validation on re-entry

An open handoff is usable only when all of these hold. Any failure stops the
resumption at that boundary with the exact reason reported:

- **Parseable and complete** — valid JSON; every required field present;
  `schema` is `verified-delivery/handoff-v1`. Otherwise: corrupt handoff.
- **Repository match** — the live remote equals `repository`. Otherwise:
  stale handoff.
- **Authorization current** — the recorded `authorization_boundary` still
  reflects a directive the user has not withdrawn. Otherwise: absent or
  ambiguous authorization.
- **Live state consistent** — the PR (when recorded) exists and is open, and
  the merge state is determinable. A PR merged or closed by someone else, or
  a rolled-back change, makes the handoff stale: the recorded pending steps
  no longer describe reality.
- **Head reconciliation** — if the live branch head differs from
  `head_sha`, head-bound evidence in `completed_steps` is invalid. Re-verify
  CI and review on the new head, update `head_sha` and `completed_steps`,
  then continue.

## Re-entry scan order

1. Check the default store (`.verified-delivery/handoff.json`).
2. If absent or closed, check the PR description block for an open handoff
   (fetch the PR live; do not trust a remembered copy).
3. If absent, check host-provided durable storage when configured.
4. If no open handoff exists anywhere, treat the input as a fresh request —
   there is nothing to resume.

## Reconciliation rules

- Read-only verification always precedes mutation on a resume.
- Gate evidence binds to the head it was verified on; a moved head
  invalidates it until re-verified.
- A live watcher recorded in `watchers` is never duplicated; wait on it or
  supersede it explicitly and record the change.
- Every mutation after resumption updates the handoff (`head_sha`,
  `completed_steps`, `pending_steps`, `updated_at`) so the next interruption
  resumes from an accurate record.
