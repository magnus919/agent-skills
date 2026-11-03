# Evaluate event-driven runtimes

Load for hibernation, high-concurrency claims, callbacks, subscriptions or event
interleavings. Based on the
[Infinity source investigation](../../harness-engineering/references/infinity-sources.md)
(S4–S9, checked 2026-11-03). This is an evaluation procedure, not a claimed result.

## Separate four questions

| Question | Evidence |
|---|---|
| What does an idle continuation cost? | Resident RSS/storage versus history size after the workload settles |
| How much active work can run? | Concurrent completions/tools, rate limits, queue depth/age, latency and burst/fairness measurements |
| Does recovery preserve effects? | Fault injection plus durable history and independent external-effect observations |
| Does event handling deliver useful work? | Representative task and trajectory outcomes under specified arrival/interruption schedules |

Infinity's published memory headline uses a simulated provider and in-memory
stores on server hardware, extrapolated to an 8 GB Pi memory budget. Its scripted
example measures idle RSS after waves finish. Neither establishes active Pi
throughput, real-model reasoning quality, production cost, or advantage over
another harness. Retain hardware, revision, agent/history/turn counts, model type,
store backend, wave shape and sampling phase. Label reported, reproduced and
projected numbers distinctly. No fixed target count here is a release threshold.

## Build schedules and oracles

Use immutable event fixtures with stable IDs, causal relationships and task
revisions. Preserve baseline/candidate model, tools, authority and environment.
Vary timing and order deliberately; preserve actual observed order because real
model and infrastructure variability can change it. Repeat where it affects the
inference; do not call one successful schedule proof for all interleavings.

Include: duplicate event; wrong-thread result; forged callback using a known call
ID; synthetic-event receiver requested by the model; user interrupt before/after
tool commit; crash between history and dedup writes; crash between intent and
dispatch; effect before callback; advisory cancel racing a late effect; process
death with deferred input; event flood with duplicate child creation; parent
revision change during child work; compaction before/after child spawn; and grant
revocation while asleep.

Observe the property at its owner: queue receipts for delivery, durable store rows
for persistence, operation ledger or target state for external effects, current
independent control evidence for permission, and accepted outputs for task quality.
Well-formed synthetic call/result pairs alone cannot prove payload authenticity,
summary fidelity or correct decisions. Model-teacher verdicts stay advisory unless
a separately validated gate contract authorizes their use.

## Connect a trajectory across sleeps

Use minimized event references: run/task version, thread/parent, source event,
originating call, dispatch attempt, callback receipt, dedup disposition, checkpoint
position, spawn/compaction boundary, authority decision, effect receipt and
terminal disposition. Distinguish occurrence, receipt, processing and effect
observation times. A trace may span processes and long waits; one worker span
cannot stand for the full task. Avoid raw prompts, payloads, credentials or hidden
reasoning by default; retain accessible protected evidence references when needed.

Report delivery, correlation, authenticity, state consistency, effect correctness,
semantic task success and resource cost separately. Distinguish no observed effect
from an unknown effect. Idle memory gains do not compensate for duplicate writes,
authority violations or starvation. Stop with a supported decision and explicit
unassessed dimensions; route runtime repair to harness-engineering and operating
hold/rollback to agent-production-operations.
