# Worked design: coding task across a long CI wait

This is a fictional design exercise, not an executed Infinity deployment. It
composes the seams from [runtime design](runtime-design.md), the restore procedure
in [state/recovery](context-and-state.md), and provider/client/bridge contracts in
[tools/events](tool-and-event-contracts.md). Source mechanisms and design proposals
are separated in [findings](infinity-design-findings.md).

## Task and decisions

Task `T42`, accepted requirement revision `R3`: repair a parser in an isolated
candidate, wait for CI, then present the verified diff for human integration.
Authority covers candidate edits and checks; merging into the user's branch is
reserved. Proposed bounds are two child tasks, a shared 20-unit cost budget, and
an eight-hour deadline. These illustrative bounds are not Infinity defaults.

Choose a platform-driven step engine: the service already has a durable input
queue and long tool waits. The engine owns input preparation, conversation
ordering, turn commit and dispatch policy. The platform adapter owns per-thread
serialization, queue acknowledgement/redelivery and retention. A resident local
engine would be simpler if a durable local daemon already met the same bounds;
there is no need to replace the low-level completion pipeline.

| Owner / seam | Record for this design |
|---|---|
| Conversation store | Root `P`, children `C1/C2`, spawn positions, messages and summary indices |
| State store | Processed events, subscription `S9`, pending choice `U7` and metadata |
| Configuration source | Root-to-tenant mapping, repository identity, tool manifest `K4`, prompt revision and child capability ceilings |
| Model source/provider | Persisted provider-scoped selection `M2`; current catalog/capabilities; typed failures and provider timeouts |
| Effect ledger | CI operation `O8` and reconciliation state, separate from conversation persistence |
| Client adapter | Snapshot cursor plus serialized live registration; allowed visible fields only |
| Integration owner | Parent candidate base, each child revision, combined candidate and review evidence |

The effect ledger, paired recovery manifest and task-level budget controls are
proposed application mechanisms. Their presence is not asserted for Infinity.

## Journey and observable contracts

1. **Start.** Persist `T42/R3`, config references, authority references and budget.
   Resolve root-to-tenant ownership, then derive narrower children through explicit
   records. Launch-time tool instances alone are insufficient for this service.
2. **Produce.** Spawn `C1` for parser repair and `C2` for independent test changes
   at recorded parent context/repository positions. Reserve both costs against
   the same ledger. Each child publishes a revision-bound artifact/report.
3. **Integrate children.** Preserve both child revisions/diffs. Compare with the
   current parent base; resolve conflicts under the integration owner's authority.
   Re-run combined checks. A child workspace closing does not imply its changes
   were integrated, and an integrated revision needs new verification.
4. **Dispatch CI.** Commit the call intent with `O8`, then dispatch. A transport
   acknowledgement means CI accepted work. Reconcile ambiguous dispatch through
   `O8`; do not start a duplicate build because the UI detached. Subscription
   `S9` can outlive a slice; finite CI completion is distinct from the ongoing
   subscription stream. Use a bounded result/deadline, not “wait for all events”.
5. **Detach.** The client disconnects; the service retains task ownership and
   waits without a resident core slice. A session-preserving tool bridge may
   still consume compute. UI detachment is not cancellation or merge permission.
6. **Restart.** Fence dispatch and validate a coordinated conversation/state
   recovery point, replay cursor, schema/config versions and external-operation
   disposition. History from checkpoint A plus state from unrelated B is held.
   Reconstruct workspace/bridge resources and `K4/M2`; missing configuration holds
   execution instead of choosing broader defaults. Recheck current grants.
7. **Handle model/tool changes.** If the selected model was removed, surface an
   approved compatible replacement decision; recompute context/image support.
   Back off typed throttling, bound transient retries, stop on fatal errors.
   One oversized tool result can get a visible omitted-evidence marker with a
   retrieval path. If new user instructions cannot fit, stop rather than silently
   retry using only `R3` or an older conversation. Reconstruct current accepted
   intent before continuing.
8. **Recover the choice.** After CI, persist `U7` asking the user to choose between
   two verified candidate approaches; emit it only after persistence. Choice is
   not permission to merge unless the current grant says so. On reconnect, capture
   snapshot plus pending choices and install the subscriber in one serialized
   operation. An event racing attach appears once in replay or live output; no
   second task is launched. Resolve attach before accepting dependent UI commands.
9. **Settle.** Verify that `U7` is still pending for the current call/revision.
   Persist response/dismissal before changing display state. If `R4` arrived while
   children/CI ran, invalidate affected `R3` evidence and retire stale choices.
   Present the verified combined diff and explicit pending human integration.
   Preserve unresolved effects and recovery references; clean up only owned
   resources under the authorized retention policy.

## Challenge receipts required before implementation acceptance

| Scenario | Expected observation |
|---|---|
| Queue redelivers CI completion | Same operation/result recognized; no duplicate effect |
| Process restarts without launch-time objects | Same intended tools/instructions reconstructed from valid references |
| Child ID mapped to wrong tenant | Rejected before tool dispatch, rather than trusted from ID shape |
| State snapshot does not match history | Recovery hold with mismatch evidence; no blind replay |
| Model selection removed / capabilities changed | Explicit compatible disposition and rebuilt context budget |
| New user instruction overflows context | Visible stop/recovery; no execution on silently stale intent |
| Client attaches as choice/event is emitted | Pending choice recovered; replay/live union contains each event once |
| Choice becomes obsolete during disconnect | Old response rejected; persisted dismissal reflected on reconnect |
| Bridge restarts between handle creation and use | State dependency detected; reconstruct or choose session-preserving path |
| Parent advances or integration conflicts | Child recovery artifact retained; combined candidate reverified |

No rows are marked passed here: this example supplies a design and expected
observations only. Record actual runtime receipts and representative model outputs
before claiming recovery, client correctness or task-quality improvement.
