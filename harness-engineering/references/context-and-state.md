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

## Challenge recovery

Inject cancellation/process death, failed checkpoint write, stale cache,
expired lease, duplicate event, and dependency version change. Verify user outcome,
no duplicate/lost effects, evidence invalidation, and recoverable handoff. Record
which failures were exercised and which remain hypotheses. In-memory savers cannot
support process-death recovery; a worktree alone cannot isolate shared services.
