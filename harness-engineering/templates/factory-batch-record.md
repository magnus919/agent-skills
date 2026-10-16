# Factory batch reconciliation record

- Batch ID, accepted scope and contract hash:
- Supervisor/integration owner and authorized actions:
- Trigger, observation time and authoritative source revisions:
- Dependency graph/interface versions and shared resources:
- Total attempt/time/cost limits, consumed budget and no-progress limit:
- Escalation recipient and default when unreachable:

| Task/run | Candidate and input contract versions | Lease owner/expiry/fencing evidence | Observed effect and evidence | Dependency drift / affected downstream tasks | Disposition and next owner |
|---|---|---|---|---|---|
| | | | | | |

## Control integrity

| Protected artifact/configuration | Owner and accepted hash | Worker/supervisor access boundary | Trusted enforcement and challenge evidence | Revision path |
|---|---|---|---|---|
| | | | | |

- Unknown effects reconciled before retry or reassignment:
- Stale worker publication prevented by:
- Integrated candidate hash and environment:
- Combined journey/architecture checks and results:
- Superseded evidence and affected checks to rerun:
- Unaffected evidence reused with justification:
- Actions taken within authority; unresolved conditions and budget remaining:
- Pass disposition: reconciled / repair pending / escalated / evidence unknown:

A reconciled pass is not release approval. Preserve history across worker replacement;
a new worker does not create a fresh batch budget.
