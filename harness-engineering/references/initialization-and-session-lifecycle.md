# Initialization, fresh-session discovery, and handoff

## Separate setup from the worker loop

An initializer creates the environment and durable task contract. A worker then
resumes bounded tasks through a stable path. They may be the same agent in two
phases; separate personas are optional. Initialization is complete only when a
fresh worker can act from the resulting artifacts.

| Initializer responsibility | Worker responsibility |
|---|---|
| Identify user outcome and missing decisions | Read accepted contract and current state |
| Discover runtime, dependencies, services and actual check commands | Check readiness without unnecessary reinstall |
| Decompose tasks and dependencies with meaningful acceptance | Pick bounded eligible work and preserve ownership |
| Establish state/evidence owner and recovery path | Reconcile state, implement, verify, checkpoint |
| Prove startup and one baseline journey | Record incomplete checks and leave next action |

Do not infer readiness from a generated startup script. A package manifest is
not a lockfile, and a version range is not a pinned runtime. Setup may run package
scripts or access credentials: review it within the confirmed scope.

## Fresh-session discovery protocol

Start without the previous working transcript. Allow the sources the actual
agent will have: repo, authorized connectors, runtime state, and indexed docs.
For each answer require a source and distinguish absent knowledge from denied
access or conflicting sources.

1. What system and user outcome am I working on?
2. Where are the relevant responsibilities and architecture boundaries?
3. How do I start it, and how do I establish readiness?
4. What checks decide the requested outcome?
5. What is active, blocked, verified, or stale on this revision?
6. What authority do I have, and where do I stop/escalate?

Record discovery latency, wrong assumptions, repeated human questions, and
source conflicts. Improving this test can reduce startup friction, but it is not
by itself evidence of end-to-end task quality. Do not ban remote knowledge: the
requirement is discoverable, authorized, current information with a clear owner.

## Startup sequence

1. Confirm the workspace, identity, instruction precedence, and authorized scope.
2. Inspect revision/dirty work, task state, and any incomplete side effects.
3. Resolve policy/acceptance conflicts; do not silently select convenient text.
4. Read bounded context for the selected task and retain original references.
5. Probe dependencies with non-mutating readiness checks where feasible.
6. Acquire the work lease or ownership before executing concurrent writes.
7. Start only if prerequisites and the failure/escalation path are understood.

If readiness fails, record the specific dependency and bounded remediation.
Do not consume the implementation budget in infinite setup retries.

## End of session: restartable, not cosmetically clean

Record candidate revision and dirty changes, evidence and its scope, blockers,
partial operations, owned resources, next action, and rollback. Stop/transfer only
resources this run owns. Preserve work that cannot yet be verified and label it;
a forced commit/reset or deletion is not a recovery design.

Use a two-phase checkpoint: write durable facts/results, then publish the pointer
or updated task version. With concurrent writers use a transaction or compare-and-
swap. A rename makes one file atomic, not a multi-file transaction.

## Exercise the lifecycle

Interrupt at these boundaries: before action, after side effect before checkpoint,
after checkpoint before acknowledgement, during verification, and before handoff.
Check no duplicate effects, no loss of accepted work, stale evidence invalidation,
and clear escalation when reconciliation is impossible. Include disk-full/failed
checkpoint and a stale worker attempting to complete an expired lease.

Use [templates/session-protocol.md](../templates/session-protocol.md) to record
startup and handoff acceptance, and [templates/recovery-drill.md](../templates/recovery-drill.md)
for failure probes. For system-wide RTO/RPO/restore design, compose the recovery
specialist rather than prescribe an arbitrary recovery target.
