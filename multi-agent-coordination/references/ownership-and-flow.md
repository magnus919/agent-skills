# Ownership, identity and flow

## Separate four identities

A role/seat is a persistent responsibility and address. An execution is one
process/session occupying it. A task claim binds work to an execution or role
under a lease. A principal/tool credential determines effective action rights.
Never infer permission from a familiar address or restore an expired grant with
a saved session. Preserve role revision, occupant/run ID, claim epoch and current
authority reference separately.

Define seat creation, activation, handover, replacement, suspension and retirement.
During replacement, inspect pending tasks, messages and external operations;
fence the old occupant's writes before assigning the same responsibility again.
Retiring a seat needs rerouting or explicit closure for its open work, not merely
removal from a roster. Review inherited lessons before use; a prior occupant's
notes are not policy.

## Task state and handoff

Use the host's existing state store. A useful conceptual flow is queued → claimed
→ working → delivered → accepted, with blocked, denied, canceled and failed
branches. Names can differ; semantics must remain distinguishable. Record owner,
requirement revision, inputs, artifact identity, outcome and history. A blocked
task needs blocker, continuation, wake condition and escalation owner.

Prefer a transactional transfer of ownership where the store supports it. Across
stores use a durable transfer ID, sender outbox and receiver deduplication/ack;
retain sender responsibility until transfer is durably reconciled. Never claim
exactly-once external execution from reliable message delivery. If both parties
believe the other owns work, recover from the last acknowledged transition and
observed effects.

## Leases and shared resources

A lease defines who may act until expiry; it does not stop a paused worker from
waking later. Use an epoch/fencing token checked at the write or integration
boundary. Assign disjoint files when possible; serialize changes to shared
interfaces. Worktrees isolate checkouts, not shared databases, caches, deployment
targets, credentials or scarce provider quotas. Enumerate those resources too.

Use atomic reservation for aggregate cost and quotas; include retries, replacements,
review and uncertain charges in one task ledger. Avoid hold-and-wait: acquire
resources in an agreed order, release unused reservations and park work explicitly.
A wait-for graph cycle is a diagnostic candidate; not every communication cycle
is a deadlock. Ask whether progress can occur without an external decision.

## Backpressure

Measure queue age and work in progress at intake, production, verification and
integration. Limit admission at the constrained stage, not just generation. A
review backlog is not solved by more builders. Define priority and starvation
handling under accepted policy. Record denied/canceled/timed-out attempts in
outcome denominators. A heartbeat proves liveness at most; blocked and idle
statuses need source/time and corroboration.

### Worked example: available budget, no downstream capacity

A factory has idle builders and money left, but the required review queue is
full and support cannot absorb another rollout. Stop admitting new feature
work into implementation. Find the oldest eligible review or the dependency
blocking it; route the work to an authorized owner without weakening review
independence. Continue operating capacity checks even if every PR is green.

Reassess the two constraints separately. If reviewers can take more work and
there is room to stage the result safely, resume bounded implementation. Keep
user exposure on hold until the release owner confirms that the target cohort
and support can absorb the change. Maintain a limit on staged work too. Record
queue age and WIP, the release constraint, and what event or threshold should
trigger another admission decision. Do not treat merge or deployment as
customer acceptance. See [release engineering](../../release-engineering/SKILL.md).

[Yegge’s Wyvern account](https://ai.engineer/code/2026/talks/steve-yegge) is
the motivating example: players asked for a slower pace even while enjoying
new features. The above is a proposed operating policy, not a benchmark.

OpenRig's [queue documentation](https://openrig.dev/docs/coordination) motivates
durable owned work and distinguishes closure from acceptance. HERDR's
[README](https://github.com/herdrdev/herdr) separates terminal persistence from
post-restart restoration. These are documented mechanisms, not evidence that
our host implements either guarantee. Exercise a crash around transfer, two
simultaneous claims, expired-worker output and lost wake-up before relying on them.

## Source-traced qualification

Commit source closure, successor and wake intent as one act when the host supports it; dispatch afterward. Give lost-wake recovery a narrow write set that restores liveness without advancing acceptance. See [the pinned source audit](openrig-source-audit.md) and [effect/recovery matrix](../templates/effect-recovery-matrix.md).
