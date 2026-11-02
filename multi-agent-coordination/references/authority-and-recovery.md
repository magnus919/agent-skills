# Cross-agent authority and recovery

## Supply obligations to the runtime owner

For each boundary record current grant, scope, expiry, delegated ceiling,
resources, operation identity, protected controls and evidence owner. Children
and peer requests stay within the intersection of assigned rights and applicable
ancestor restrictions. A read-only coordinator cannot authorize a write-capable
worker to mutate. An agent-written approval is not an independent grant.

Use harness-engineering for executor checks, credential/session authority,
protected supervision and atomic accounting. This reference specifies what must
remain consistent across agents; it does not implement enforcement. Independent
control evidence must exist outside controlled workers' writable authority.
Route rights/exception decisions to ai-governance and production containment to
agent-production-operations.

## Plan recovery before dispatch

| Failure | Reconcile first | Safe continuation |
|---|---|---|
| Worker disappears | Lease, last artifact, pending external operation | Fence old writer, resume/reassign under same budget |
| Coordinator disappears | Durable assignments, acknowledgements and grant | Restore one decision owner; avoid split-brain dispatch |
| Message retried or reordered | Transfer/operation ID and accepted requirement revision | Deduplicate; defer missing prerequisite; reject obsolete change |
| User narrows scope/cancels | Descendant queue, active grants, effects already committed | Stop dispatch and invalidate queued/late work; reconcile effects |
| Tool timeout after a write | Query actual system by operation ID | Retry only if repeat is safe; otherwise owned unknown state |
| Artifact arrives after intent changed | Input and acceptance versions | Quarantine affected output; reverify if reuse is justified |
| Mandatory monitor fails | Independent control-integrity evidence | Hold consequential work; protected escalation |
| Shared fact is invalidated | Source lineage, derived summaries, consumers and effects | Contain affected paths and verify correction adoption |

Cancellation is not rollback. Define which effects are reversible, compensatable,
or irreversible. [Sagas](https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf)
supply a foundation for compensating partial multi-step work; a compensating
message or refund cannot necessarily undo disclosure, publication or reputational
effects. Record residual effects with an accountable owner.

## Exercise the boundary

Inject safe synthetic failures before relying on a live mechanism: kill between
commit and ack; duplicate a handoff; delay an old-epoch writer; cancel a parent
with queued descendants; partition coordinator from workers; make the escalation
recipient unavailable. Observe actual effects, not just state declarations.
Keep tests isolated from production and within the user's authorization.

The [OpenAI incident report](https://openai.com/index/hugging-face-incident-and-the-road-ahead/)
documents unauthorized channels, persistence and peer-goal adoption alongside
other contributing factors. Our inference is to test cross-agent boundaries in
addition to individual-agent checks. Better context is useful but does not prove
containment or eliminate misalignment.

## Source-traced qualification

Bind delayed effects to the captured execution generation and revalidate immediately before the write. Observation or custody cleanup cannot authorize input. Sender provenance labels do not establish authentication. See [the pinned source audit](openrig-source-audit.md) and [effect/recovery matrix](../templates/effect-recovery-matrix.md).
