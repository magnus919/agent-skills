# Migration Coexistence Patterns

Load this reference when an implementation must run beside an older path during an
authorized service or interface transition. It does not decide whether to decompose
the system or own the cross-system migration lifecycle. Use `migration-engineering`
for classification, compatibility windows, reconciliation, cutover, recovery,
deprecation, and cleanup; use `software-architecture` for the target boundary.

## Make The Seam Explicit

Before changing behavior, record the capability, current path, candidate path,
callers, data touched, invariant, authority, and interruption point. Choose a seam
that can be observed and selected without making both implementations the permanent
source of truth.

| Pattern | Implementation responsibility | Evidence to collect |
|---|---|---|
| Adapter | Translate the old request/response shape into the new port or the reverse | Translation rules, lost information, error mapping, and contract tests |
| Strangler handoff | Route a bounded operation or cohort to the new path while the old path remains selectable | Traffic, outcome, latency, and failure comparison by route/cohort |
| Anti-corruption boundary | Keep legacy or foreign vocabulary out of the local domain/application model | Explicit mapping, ownership of translation, and tests for unknown/obsolete states |
| Dual path | Execute or read through both paths only when side effects can be isolated or deduplicated | Authority, comparison tolerance, mismatch categories, and cost guardrail |

These patterns are different. An adapter translates; strangler routing selects; an
anti-corruption boundary protects a model; a dual path creates comparison evidence.
Combine them only when each role and failure behavior is named.

## Authority And Handoff

For every operation and important field, state one authority during each coexistence
phase. A read switch is not an ownership transfer. The handoff record should answer:

- Which path accepts writes, and how are old writes detected or rejected?
- Which store is authoritative, and are other values derived, cached, or shadow-only?
- Can the invariant be maintained without a distributed transaction?
- Are duplicate, out-of-order, missing, and deleted records represented?
- What does the non-authoritative path do on disagreement: compare, alert, serve, or
  remain unused?
- What customer-visible staleness, ordering, latency, or error change is accepted?
- Who can change the selector, and what evidence permits the next increment?

Prefer one writer. If a second representation must be kept current, use an explicit
outbox/CDC or other owned synchronization mechanism and reconcile it. Avoid a
permanent synchronous dual-write in request code when neither side is clearly
authoritative; it creates two failure-prone commits without removing the ownership
ambiguity.

## Safe Handoff Sequence

1. Add the port, adapter, selector, and characterization/contract tests while the old
   path remains the default.
2. Establish the new path's input/output contract and translation boundary. Do not
   hide a breaking consumer contract in an adapter; route that decision to
   `api-design-and-evolution`.
3. Populate or synchronize data using the migration owner's chosen backfill/CDC
   method. Track lag, duplicates, deletes, and reconciliation failures.
4. Compare shadow or parallel outcomes while the old path remains authoritative. Do
   not duplicate irreversible side effects merely to obtain a comparison.
5. Shift a bounded cohort or operation. Define a precondition, abort signal,
   customer-impact check, and recovery classification for the increment. Route
   rollout and flag mechanics to `release-engineering`.
6. Transfer authority explicitly: update the source-of-truth record, enable the new
   path, and verify that it accepts writes authoritatively before disabling old
   writers. Confirm old-path accesses are observable and denied or harmless in the
   same cutover step; abort and restore the prior selector if the new write path is
   not proven authoritative.
7. Remove adapters, selectors, old reads/writes, synchronization feeds, flags, and
   credentials only when their individual removal conditions pass. Keep a tested
   forward repair or restore path where rollback is no longer possible.

## Removal Conditions

Removal is justified by evidence, not elapsed time alone. Record conditions such as:

- no registered or observed callers use the old route for a defined observation window;
- new and old outcomes reconcile within an agreed tolerance across the required
  population and time range;
- the new path owns all writes and old writes are blocked or detected;
- queued, delayed, and replayed work is handled by the new consumer;
- dashboards, alerts, runbooks, support procedures, and security controls use the new
  path;
- the old data, contract, adapter, flag, and credentials have an owner-approved
  recovery classification before removal.

If any condition is unknown, keep the old path selectable and stop the handoff rather
than calling the coexistence complete. Once the old store or contract is removed,
do not promise rollback by default; classify roll-forward, restore, or irreversible
recovery with `migration-engineering` and `release-engineering`.

## Failure Cases To Exercise

- Selector points to a path whose dependency is unavailable.
- Adapter receives an unknown legacy enum or a response with missing fields.
- Both paths observe the same command and an external side effect is attempted twice.
- Old and new reads disagree because of lag or a mapping defect.
- A late old write arrives after authority transfer.
- A replayed event reaches both old and new consumers.
- Removal hides a caller that was not in the inventory.

For each case, specify whether to reject, queue, serve the authoritative result, alert,
or halt promotion. Include correlation IDs and path/version labels in the evidence,
without logging sensitive payloads.
