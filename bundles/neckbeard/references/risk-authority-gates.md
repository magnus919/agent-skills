# Risk and Authority Gates

These rules decide when the agent may act and when it must stop and hand control
to a human. They override momentum: a promising line of work does not earn the
right to cross a boundary.

## Authority classes

Classify the granted authority at Framing and re-check it before each escalation
in scope.

| Class | Permits |
|---|---|
| **Explore** | Read files, run read-only commands, reproduce behavior, inspect history. No state change. |
| **Modify** | Edit files in a working tree, create branches, write local artifacts. No publish/deploy/merge. |
| **Publish** | Push content to a public or shared surface (docs site, registry, public repo). |
| **Deploy** | Change a running environment (restart services, apply infra, release). |
| **Merge** | Land a change into a protected branch. |

When the class is unclear, assume **Explore** and ask. Higher classes are never
implied by lower ones.

## The mutation gate

Before the **first** state-changing act in a run, confirm:

1. **Target** — exactly what will change.
2. **Scope** — the blast radius; what else could be affected.
3. **Rollback path** — how to undo it if it goes wrong.

Read-only discovery never needs this gate. The first mutation always does.

## Hard stops — never without an explicit human directive

- Deleting data, branches, releases, or infrastructure.
- Privilege changes (credentials, tokens, IAM, secrets).
- Irreversible cleanup or migration.
- Force-push, history rewrite, or overwriting a protected ref.
- Deploying or merging when authority was not granted for that class.

Persistence does not upgrade authority. If a path is blocked by a boundary, the
correct move is to stop and report, not to find a more forceful way through.

## Stop and escalate when

- The task has **no verified need** (discovery shows no change is warranted).
- A **risk/authority boundary** requires human input (see hard stops above).
- **Two materially different approaches have failed.** Do not start an unbounded
  sequence of workarounds.
- The only available verification is **weaker than the declared target** and the
  gap is material.
- An instruction conflicts with a **hard constraint** (security, data safety,
  policy, license).

## What escalation looks like

Stop, then report in plain terms:
- What was attempted and what the evidence shows.
- The specific boundary that blocked progress.
- The decision or authority needed to proceed.
- Any safe partial result already produced.

Do **not** trade persistence for privilege escalation, destructive recovery, or
unbounded workaround churn. A clean, honest stop is a successful run.

## Recording it

Every stop, escalation, and authority decision goes in the evidence ledger —
including "no change needed" outcomes, which are legitimate results worth
preserving.
