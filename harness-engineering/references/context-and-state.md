# Durable state and recovery

Separate human-curated policy, task state, reusable memory, and scratch work.
Each has a source owner, scope, version, retention, and update mechanism. Reuse
an authoritative issue tracker/database when available; a second file tracker
can make startup less reliable by creating contradictory truth.

## Task state contract

Use stable IDs, objective/acceptance, owner, status, dependencies, candidate
revision, evidence references, blockers, next action, and unresolved side effects.
States may be pending → active → blocked/verified/stale. Blocked includes a reason
and owner; verified applies to a particular candidate and verifier/environment.
A later change invalidates evidence rather than inheriting permanent completion.

A status field is a claim. Runtime write controls or transition validation enforce
a gate. An agent with unrestricted file writes can edit JSON; instructions alone
cannot prevent it. Store sensitive acceptance/evidence under the appropriate
integrity boundary and reconcile state against actual artifacts on startup.

The bundled state declaration validator checks task IDs, dependency cycles,
WIP limits, owner for active tasks, and revision-matched passing references for
all verification criteria in a verified task. It does not run those checks or
confirm that a referenced report is true. Historical evidence can remain attached;
only one current record per criterion/revision is permitted by this example
contract. More elaborate evidence ledgers should preserve attempts separately.

## Transaction and checkpoint design

Atomic file replacement protects one file from partial writes; it does not make
several state/evidence files atomic. Choose a transactional store, manifest/pointer
publication protocol, or recovery journal for multi-artifact operations.
Concurrent writers need locking/compare-and-swap and fencing for expired leases.

Publish durable evidence before the pointer that announces completion. If a
consumer loses acknowledgement, let it retrieve the prior durable result rather
than repeat a consequential action. Retain outputs until the consumer can recover
them under the retention policy; notification does not make deleted output durable.

## Side-effect recovery table

| Last durable/observed fact | Interpretation | Safe next step |
|---|---|---|
| Intent only; no action observed | Could still have happened if observation incomplete | Query operation/resource state before retry |
| Action started; timeout | Unknown effect | Reconcile; no blind retry |
| Effect observed; checkpoint absent | State publication failed | Record/reconcile existing effect |
| Checkpoint durable; acknowledgement lost | Result may already be complete | Return prior result |
| Candidate changed after acceptance | Evidence stale | Reverify affected criteria/dependencies |
| Worker lease expired | Ownership moved | Reject stale publication; hand off evidence |

Persist operation IDs, resource identity, observed effect, and candidate/version
needed to reconcile. A filesystem checkpoint does not guarantee exactly-once
behavior in a remote service. Use idempotency keys where supported and verify
what replay actually means. Escalate unresolved ambiguity instead of guessing.

## Memory and background extraction

Keep topic detail durable before updating its index. Record source/version and
scope; recover orphaned entries. Derived facts can often be retrieved again rather
than memorized. Background extraction needs version checks or mutual exclusion
with current writes; stale extraction must not override a newer user correction.
Use retention/access controls and exclude secrets. Product-specific memory
caps and precedence are adapters, not discipline-wide rules.

When transferring memory between assistants, follow
[memory import acceptance](memory-import-acceptance.md) for staging, provenance,
conflict review, authority rejection, restart and batch rollback.

## Challenge recovery

Inject cancellation/process death, failed checkpoint write, stale cache,
expired lease, duplicate event, and dependency version change. Verify user outcome,
no duplicate/lost effects, evidence invalidation, and recoverable handoff. Record
which failures were exercised and which remain hypotheses. In-memory savers cannot
support process-death recovery; a worktree alone cannot isolate shared services.

## Restore the logical deployment, not only its transcript

Separate conversation history from runtime state without treating either as
optional. In the inspected Infinity design, one store owns messages, ancestry and
compaction summaries; another owns processed IDs, thread metadata, subscriptions
and pending user choices. A successful history restore can still leave a broken
continuation if the other store is missing or belongs to a different snapshot.

Define a recovery manifest or equivalent transactional boundary containing logical
deployment/tenant identity, store schema versions, snapshot/checkpoint lineage,
configuration references, pending-operation identities and an input replay cursor.
This manifest is a recommended design control, not an observed Infinity feature.
A shared timestamp alone does not prove two snapshots are consistent.

A coordinated restore drill should:

1. Pause or fence admission and consequential dispatch through authorized controls.
   Inventory in-flight operations and preserve their unknown-effect dispositions.
2. Restore both stores from a compatible recovery point; validate parent/spawn
   references, summary positions, processed-event coverage, subscription ownership
   and pending-choice-to-call links. Reject missing or incompatible lineage.
3. Reconstruct configuration, external workspace/session resources and current
   permissions. Retire stale callback destinations without losing the reconciliation
   path for already dispatched operations.
4. Replay only eligible events under stable identities. Reconcile effects outside
   the restored checkpoint before allowing a mutation to run again.
5. Verify a recovered pending choice, a duplicate callback, and a child spanning
   compaction; then let the accountable owner release the hold with evidence.

Preserve the distinction between an input admitted in memory, a validated turn,
a durable checkpoint and an observed tool effect. Never fabricate user acceptance
for a UI choice merely because the transcript mentions it. Record rollback and
recovery-point limits when transactions cannot span all state.

Source and limits: [follow-up findings](infinity-design-findings.md), S10/S12.
For a complete example see [coding task](event-runtime-worked-example.md).

## Keep causal records separate from compacted prompt views

Use compaction as a derived context view, not the operation ledger. Preserve the
stable call/event identities, ancestry positions and reconciliation references
needed to recover pending effects even when their prose leaves the model window.
A summary must not synthesize a new call identity or erase an unknown effect.
Retrieve the authorized original record when resolving a disputed result; fail
visibly if its retention deadline has passed instead of inferring it from a
fluent summary. This complements the spawn-position rules in
[event-driven continuations](event-driven-continuations.md#keep-ancestry-and-compaction-coherent).

Compaction is not deletion or privacy erasure. Declare retention/access separately
for original transcripts, causal metadata, summaries, artifacts, logs and backups;
retain only what each recovery requirement justifies. Challenge a pending call
spanning two compactions and an expired original record. Observe the recovered
operation identity and explicit missing-evidence disposition, not only summary
fidelity. This is a reusable design requirement, not a claim that Infinity offers
a deletion protocol or immutable audit ledger.
