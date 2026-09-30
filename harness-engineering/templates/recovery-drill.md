# Recovery drill

- Target/scope/authority and isolated exercise environment:
- User outcome, candidate identity, dependencies:
- Expected invariant and side-effect owner:
- Checkpoint/operation IDs and reconciliation source:

| Injection boundary | Failure | Expected durable fact | Replay/reconcile decision | Acceptance evidence |
|---|---|---|---|---|
| Before execution | Process death | Intent, no confirmed effect | Check before retry | Define |
| Effect before checkpoint | Process death | Operation may have happened | Reconcile; no blind replay | Define |
| Checkpoint before ack | Lost acknowledgement | Effect/result durable | Return prior result | Define |
| During check | Timeout/cancellation | Acceptance unknown | Resume/recheck | Define |
| Lease expires | Stale worker returns | New owner/version | Reject stale publish | Define |

- Restore procedure and rollback:
- Owned resource cleanup; preserved unrelated work:
- Observed duplicate/lost effects and incomplete evidence:
- Supported conclusion, remaining failure cases, owner/next step:
