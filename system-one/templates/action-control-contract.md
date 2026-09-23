# Observed-action control contract

Copy this checklist into a design review before a System One model controls a
browser, desktop app, API client, robot, or other stateful tool. It is a
template, not a grant of authority.

## Observation and candidates

- Observation source and timestamp: `<source / time>`
- Stable action IDs and meanings: `<id → effect>`
- State freshness limit: `<duration>`; stale state means `<refresh / stop>`
- Candidate generator: `<deterministic function>`
- Model question: `<one choice, score, or Noul question>`
- Valid output schema and legal labels: `<schema / IDs>`

## Authorization and execution

- Read-only actions: `<IDs>`
- Reversible mutations: `<IDs>`; rollback: `<mechanism>`
- Irreversible or externally consequential actions: `<IDs>`; explicit human
  confirmation point: `<where / who>`
- Idempotency key and duplicate suppression: `<key / retention>`
- Preconditions to re-check immediately before execution: `<list>`
- Maximum model calls, observations, actions, and elapsed time: `<limits>`
- If confidence or evidence is insufficient: `<abstain / review / safe action>`
- If model, tool, or network fails: `<bounded fallback>`

## Evidence and operations

- Held-out task set and outcome metric: `<dataset / metric>`
- Unsafe-action, false-approval, and abstention metrics: `<thresholds>`
- Latency budget including observation + inference + action: `<p95 / deadline>`
- Trace fields (without secrets or raw sensitive state): `<fields>`
- Kill switch, owner, and rollback rehearsal: `<details>`

Never treat a high model probability as permission to bypass an execution
precondition or human confirmation. See `references/use-case-patterns.md` for
browser, voice, trading, and deadline-loop applications.
