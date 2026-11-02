# OpenRig: pinned source-to-contract audit

Accessed 2026-11-02 UTC. Scope and method: [audit brief](openrig-audit-brief.md).
Extraction provenance: [documentation receipt](openrig-audit-receipt.md).
Source S40: OpenRig commit `22b574983e840f4a664abf46787e7d8949ed6de4` (package 0.7.1), Apache-2.0.
This is original analysis; no implementation was copied into this MIT catalog.

## Architecture and effect map

The inspected repository uses a local daemon with SQLite state and external tmux
sessions/harness adapters. CLI, TUI and MCP surfaces converge on daemon HTTP;
routes call domain services/repositories, which persist state and invoke adapters.
That shared control plane is a useful location for invariants across entry points,
but an architecture diagram alone does not demonstrate that every effect uses it.

Trace: request → actor/provenance resolution → domain transition/transaction →
durable work and intent → post-commit delivery → guarded adapter effect → receipt
→ workflow projection/acceptance. Recovery observes the ledger and restores
liveness; it must not silently substitute for the acceptance owner. Context packs
and team archives move configuration and evidence through separate resolution and
installation paths; their successful assembly does not prove a coordinated run.

The public architecture map and most retrieved guides describe 0.6.6; the pinned
source is 0.7.1. Treat those guides as navigation and documented intent, not an
exact current implementation inventory. The source map itself names an older
checked revision. Source/test links below resolve the inspected bytes.

## Mechanism ledger

Every test below was **read, not executed**. Test names/assertions disclose intended
checks; they are not a passing run receipt, production observation or independent
replication. In particular, SQLite/Vitest dependencies were not installed and no
daemon, fleet, plugin or agent was launched. Findings are bounded to these paths.

### Atomic transfer, durable wake

- Source: [QueueRepository.handoff](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/src/domain/queue-repository.ts).
- Inspected tests: [seat-delivery-guard.test.ts](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/test/seat-delivery-guard.test.ts).
- Observation: Source closure, successor, transition records, wake intent and persisted events share a SQLite transaction. The test includes precommit quota rollback and retained handoff intent.
- Portable inference: Commit the obligation and notification intent together; dispatch afterward. Reconcile the commit/effect gap, rather than equating a notification with ownership transfer.
- Challenge / limit: Crash after commit before dispatch; retry with the same intent identity; quota refusal must not close the source without its successor.

### Restart restores liveness, not completion

- Source: [runWorkflowBootSweep](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/src/domain/workflow-boot-sweep.ts).
- Inspected tests: [workflow-boot-sweep.test.ts](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/test/workflow-boot-sweep.test.ts).
- Observation: Active/waiting instances get keepalives; pending frontier packets with no nudge attempt enter recovery. Deadline evaluation includes unclaimed work. Recovered packet IDs prevent a second deadline nudge in the same pass. The sweep does not project advancement.
- Portable inference: Give restart reconciliation a narrow write set: restore observation and delivery, preserve current workflow state, and expose failures.
- Challenge / limit: Commit-then-crash, missing keepalive, overdue unclaimed work and an already retained wake; none may silently advance acceptance.

### Check the final recipient, not just its name

- Source: [SeatDeliveryGuard.checkInput / beforeInput / reconcileBinding](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/src/domain/seat-delivery-guard.ts).
- Inspected tests: [seat-delivery-guard.test.ts](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/test/seat-delivery-guard.test.ts).
- Observation: A target captures node, session, occupant and pane before waiting. The final synchronous check rejects changed targets or inactive leases. Draft-aware checks hold unknown/busy input; custody cleanup cannot authorize typing.
- Portable inference: Bind delayed effects to an execution generation and validate at the effect boundary. Separate observation, cleanup and input capabilities.
- Challenge / limit: Replace the occupant during an awaited observation, detach work beyond its lease, or let human input arrive between paste and submit. Default off means draft protection is configuration-dependent.

### Protect invariants on every mutation path

- Source: [createWorkflowFrontierPredicate](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/src/domain/workflow-frontier-guard.ts).
- Inspected tests: [workflow-frontier-guard.test.ts](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/test/workflow-frontier-guard.test.ts).
- Observation: An injected predicate identifies live workflow-frontier packets; queue terminal closure rejects bypasses unless using workflow verbs. Missing pre-workflow table is tolerated; other SQL errors propagate. Tests cover ordinary items and terminal instances as negative cases.
- Portable inference: Put cross-domain invariants beneath all public mutation paths, with dependency injection where needed. Distinguish intended absence from broken enforcement.
- Challenge / limit: Close through a convenience route or in-transaction primitive; inject a schema fault; verify unrelated work still works. This is not a complete authorization audit.

### Recovery evidence has a revision

- Source: [recoveryId / findQueueRecovery](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/src/domain/queue-recovery.ts).
- Inspected tests: [queue-recovery-read-work.test.ts](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/test/queue-recovery-read-work.test.ts).
- Observation: Recovery identity incorporates the original meaningful transition and failed/retained nudge evidence. Lookup prefers active recovery; terminal dispositions become stale when newer obligation evidence exists. Tests inspect exact tag membership and error propagation.
- Portable inference: Deduplicate diagnosis against the evidence version, not a task ID forever. Reopen investigation when meaningful evidence changes; do not count retry chatter as product progress.
- Challenge / limit: A completed recovery must not suppress a later failed attempt; a partial tag match must not attach another task’s recovery.

### Attribution is not authentication

- Source: [resolveRecordedIdentity / resolveRecordedProvenance](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/src/routes/require-sender-identity.ts).
- Inspected tests: [sender-identity-canonical.test.ts](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/test/sender-identity-canonical.test.ts).
- Observation: The helper explicitly treats the session header as attribution, not authentication. It labels claimed, transport, relay and unknown provenance; principal recording has direct-loopback/shape conditions. A body claim does not override the transport actor.
- Portable inference: Document identity assurance independently from authorization. Preserve weaker provenance rather than calling a self-reported sender authenticated; do not copy deliver-and-label policy into a hostile network.
- Challenge / limit: An untrusted caller supplies a plausible header. Require the actual authenticated principal and scoped grant at consequential effects. These route-helper reads do not establish end-to-end access control.

### Suspicion is not measured waste

- Source: [PassiveCeremonySource](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/src/domain/health-passive-ceremony.ts).
- Inspected tests: [health-passive-ceremony.test.ts](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/test/health-passive-ceremony.test.ts).
- Observation: Passive lineage observation leaves productStateChanges null and requests diagnosis. Assessment basis includes transitions, context and workflow receipts; changed evidence invalidates assessment. Coverage limits expose omitted families. Tests distinguish uncertainty, stale basis, clipped intervals and recursive diagnosis traffic.
- Portable inference: Detect coordination amplification without inventing an outcome denominator. Bind judgments to inspected evidence and observation coverage; keep missing outcomes unknown.
- Challenge / limit: Many handoffs and proof files with no accepted product evidence; truncation or stale receipts must not yield a confirmed waste ratio or all-clear.

### Context identity follows resolution rules

- Source: [ContextPackLibraryService](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/src/domain/context-packs/context-pack-library-service.ts).
- Inspected tests: [context-pack-store-recursion.test.ts](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/test/context-pack-store-recursion.test.ts).
- Observation: Configured roots are scanned for manifest packs; refs are path-like. Tests cover nested discovery, leaf boundaries, distinct refs with identical name/version, same-ref last-root precedence, and skipped unsafe refs.
- Portable inference: Record the resolved context reference, source root, version and override order. Equal display names do not imply identical evidence; file presence does not prove startup or compaction retrieval.
- Challenge / limit: Two roots contain the same ref or two refs share a name/version. Inspect actual resolution and exercise the consumer route separately.

### Portable context is an explicit closure

- Source: [vendorContextPackDir](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/src/domain/bundle-carried-context-pack.ts).
- Inspected tests: [bundle-carried-context-pack.test.ts](https://github.com/mvschwarz/openrig/blob/22b574983e840f4a664abf46787e7d8949ed6de4/packages/daemon/test/bundle-carried-context-pack.test.ts).
- Observation: Only the manifest and declared files are carried. Realpath checks reject files outside the pack; duplicate pack names and missing files fail.
- Portable inference: Declare the transferable dependency closure and host-resolved exclusions. Verify confinement and collisions independently of archive integrity or team behavior.
- Challenge / limit: A repository-root pack contains unrelated files or an escaping symlink. A valid archive still cannot grant recipient permissions or prove team effectiveness.

## Scope gaps and contrary evidence

Single-writer classifier leasing was also inspected (`classifier-lease-manager.ts`):
expiry marks deadness, while reclaim is an operator verb. This is a useful separation
of diagnosis and transfer authority; it is not evidence that arbitrary shared files,
external services or GPUs have fencing. No comprehensive resource-lock inventory
or resource-contention runtime test was performed. Retain the skill’s resource
contract and require per-resource evidence before claiming enforcement.

The audit does not certify security, throughput, delivery exactly-once semantics,
recipient comprehension, startup/post-compaction navigation, actual package launch,
or quality improvement. SQLite atomicity is local; external effects still need
idempotency and uncertainty handling. A held wake is neither lost work nor a
successful recipient action. The guard’s default is off for ordinary seats; do not
advertise draft-aware safety as unconditional. Sender labels are not credentials.
Older public docs and explicit compatibility fallbacks prevent a blanket claim
that every deployment has these mechanisms.

## Apply and qualify

Use [the effect/recovery matrix](../templates/effect-recovery-matrix.md) before
selecting a coordination stack or approving a retry policy. Trace one normal and
one bypass path per consequential transition. Ask which record commits, which
external effect may already have happened, what identity is checked immediately
before it, and who can authorize recovery. Preserve a negative control so adding
a guard does not disable ordinary work.

Promote these as design hypotheses with adverse-case qualification, not universal
OpenRig defaults. Keep installation commands and tool-specific operating runbooks
in a future named-tool skill if requested. The existing read-only snapshot helper
cannot execute this matrix or establish runtime acceptance; another script would
add no evidence without a real host adapter and a separately authorized test.
