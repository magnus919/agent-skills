# Steer production already in flight

Load for changed intent, reprioritization, new responsibilities or cancellation during a factory job. Reuse the durable state owner; do not add a second competing task database. Source S6 illustrates message semantics; this protocol is portable synthesis, not a Temporal runbook.

1. Classify the input: status query, new queued work, requirement change, authority change, or cancellation. A status query must not mutate production. Confirm ambiguity with the owner while unaffected work continues.
2. Record a unique change ID, actor, old/new accepted contract, changed artifacts, scope, effective time and rollback. Deduplicate retries. Serialize conflicting changes or reject a stale expected version; do not silently overwrite a newer intent.
3. Compute affected direct tasks and transitive consumers using pinned input/dependency versions. Explicitly record unaffected work and why reuse is valid. Stop affected integration immediately; decide continue-under-old-version, migrate-at-checkpoint, cancel/restart or escalate.
4. Send the exact new assignment and require acknowledgement of its change ID/version. Distinguish sent, received, adopted and verified. Missing acknowledgement stays pending. If the host cannot steer a live worker, checkpoint/cancel and launch replacement within authority; do not claim live adoption.
5. Fence obsolete commits and late artifacts at integration/execution. Acknowledgement does not prevent old effects: reconcile external operations, reservations and leases before retry. Cancellation is not rollback. Apply narrowed authority immediately even if requirements migration is deferred.
6. Replan and reserve remaining cost against the original shared budget. Preserve prior spend and uncertain charges. Mark old relevant check evidence stale, including transitive consumers. Verify the revised integrated journey before authorized delivery.
7. Update the user with the accepted change, affected work, acknowledged/pending workers, preserved results and delivery uncertainty. On restart recover from the durable record and authoritative effects, not the last conversational summary.

Use templates/factory-change.md. Run scripts/factory.py against templates/factory-snapshot.json after tailoring it; it screens the declared snapshot for affected tasks, version mismatches, expired leases and missing acknowledgement. It neither sends changes nor inspects the real host. A clean snapshot does not prove current authority, correct artifacts or acceptance.

Challenge at least: duplicate change, stale update, simultaneous conflicting updates, old result after acknowledgement, lost director after sending, queued child after cancellation, external effect before checkpoint and exhausted shared budget. Record actual host outcomes separately from a plan or synthetic fixture.
