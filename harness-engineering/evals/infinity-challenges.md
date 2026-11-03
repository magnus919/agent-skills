# Infinity enrichment assertion challenges

Rubric addition dated 2026-11-03. Existing case IDs/assertions are unchanged.
New cases below use semantic assertions because design correctness is not a
literal-match property. These are authored challenge examples, not generated
agent outputs, human adjudication or executed behavioral evidence. A reviewer
must score the named claim, using the row's local evidence only; satisfying
examples do not claim their proposed side effects were executed.

Each row maps to a new case and its 1-based assertion position. “Omitted” means
not shown, not an inferred pass. Case-level expected outcomes remain in each
owner's v1 manifest. No grader prefixes, release thresholds or Jev policy changed.

| Skill / case / assertion | Claim | Satisfying evidence | Contradictory near miss | Omitted evidence |
|---|---|---|---|---|
| `harness-engineering/event-continuation-boundary` #1 | Identifies durable pending-operation and configuration state needed in addition to conversation text. | Persist call identity, config revision and subscription state alongside history. | The transcript alone restores every pending resource. | Discusses history only; pending state unspecified. |
| `harness-engineering/event-continuation-boundary` #2 | Distinguishes transport acknowledgement from the eventual tool outcome. | HTTP 200 acknowledges receipt; later callback carries outcome. | HTTP 200 proves tool success. | Does not distinguish ack from outcome. |
| `harness-engineering/event-continuation-boundary` #3 | Allows synchronous loop-back to use multiple completions within a slice. | Inline synchronous tools may loop into another completion in this slice. | Every slice always has exactly one completion. | No account of synchronous exceptions. |
| `harness-engineering/event-continuation-boundary` #4 | Defines a bound on synchronous loop-back execution. | Limit inline loops by completion budget or deadline. | Continue inline until the model eventually stops, without a bound. | No inline-loop budget or deadline. |
| `harness-engineering/event-commit-crash-window` #1 | Identifies the crash window between history append and separate processed-ID persistence. | A crash after append but before dedup storage can lose the dedup marker. | The two stores commit atomically because they are called sequentially. | Only dispatch failures are discussed. |
| `harness-engineering/event-commit-crash-window` #2 | Identifies the crash window between durable intent and external dispatch. | After commit but before POST the intent exists without a known dispatch. | A committed call is proof the tool received it. | No commit-to-dispatch gap considered. |
| `harness-engineering/event-commit-crash-window` #3 | Requires external-effect reconciliation or effect idempotency before replaying an unknown payment outcome. | Inspect payment ledger or reuse an effect idempotency key before replay. | No callback means failed; charge again. | No disposition for unknown payment effects. |
| `harness-engineering/event-routing-and-deferral` #1 | Rejects appending multiple ordinary results to the already answered subscription call. | Create a new synthetic call/result pair linked to the subscription. | Append another ordinary result to the settled call. | No conversation-pairing policy. |
| `harness-engineering/event-routing-and-deferral` #2 | Distinguishes a child inheriting history at spawn from an explicitly empty or fresh context. | A normal child inherits the spawn snapshot; fresh context is explicit. | Every event child starts with no parent history. | Only says isolated child, with no inheritance detail. |
| `harness-engineering/event-routing-and-deferral` #3 | Identifies loss of in-memory deferred events on process death. | Process death loses held in-memory events unless backed by another durable mechanism. | The durable transcript also makes this in-memory defer queue durable. | No process-loss discussion. |
| `harness-engineering/event-routing-and-deferral` #4 | Bounds event child fan-out or its shared execution budget. | Cap children at a declared quota or shared cost budget. | Spawn unbounded children because each idle agent is cheap. | No fan-out or shared-budget limit. |
| `harness-engineering/event-cancel-compaction` #1 | Binds child reconstruction to its spawn position when choosing compacted history. | Use a summary compatible with the child spawn boundary at 40. | Give every child the latest parent summary through 80. | No spawn-position treatment. |
| `harness-engineering/event-cancel-compaction` #2 | Requires a revision check before accepting the child report against changed requirements. | Compare the report revision with current requirements before integration. | Accept old child success for new requirements unchanged. | No report-revision check. |
| `harness-engineering/event-cancel-compaction` #3 | Distinguishes cancellation acknowledgement from evidence that external effects stopped. | Observe whether the external operation stopped; cancel ack alone is insufficient. | Cancel HTTP 200 proves all effects rolled back. | No distinction between requested cancel and actual effect. |
| `agent-production-operations/wake-revocation-and-disablement` #1 | Requires current permission verification on wake rather than trusting the persisted grant. | Resolve current deployment permission; revoked permission holds execution. | Restore yesterday’s grant from the persisted conversation. | No current-grant check. |
| `agent-production-operations/wake-revocation-and-disablement` #2 | Includes callback or queue admission in disablement rather than stopping only the current worker. | Disable admission or execution for later callback/queue wake-ups. | Stopping this process fully disables the agent. | No treatment of future wake-ups. |
| `agent-production-operations/wake-revocation-and-disablement` #3 | Assigns disposition or cleanup ownership for pending subscriptions, timers or tool effects. | Name an owner to reconcile pending tools and clean up subscriptions/timers. | Leave timers and tools running without ownership because the worker stopped. | Pending cleanup/disposition owner absent. |
| `agent-production-operations/wake-backlog-and-unknown-effects` #1 | Distinguishes receipt acknowledgement from tool completion. | 200 accepted the request, not completed its write. | 200 confirms the external write succeeded. | No ack/outcome distinction. |
| `agent-production-operations/wake-backlog-and-unknown-effects` #2 | Requires effect reconciliation before replay of the unknown write outcome. | Reconcile target state before replaying the write. | Replay immediately because the callback is overdue. | Unknown-effect replay policy absent. |
| `agent-production-operations/wake-backlog-and-unknown-effects` #3 | Tracks queue age or active/pending load separately from idle resident-agent count. | Measure oldest-event age and pending load apart from resident histories. | Tiny idle memory proves the burst needs no admission control. | Only idle memory is measured. |
| `agent-evals-and-observability/idle-capacity-evidence` #1 | Identifies the Raspberry Pi claim as a memory-capacity extrapolation rather than a measured Pi deployment. | 75,000 in 8 GB is projected from the server memory slope. | The experiment ran 75,000 agents on a Pi. | Does not say whether the Pi result was measured or projected. |
| `agent-evals-and-observability/idle-capacity-evidence` #2 | Distinguishes scripted idle-memory evidence from real-model task quality. | Scripted idle RSS says nothing about real-model task success. | The fixed scripted output proves useful reasoning at scale. | Model/task-quality scope omitted. |
| `agent-evals-and-observability/idle-capacity-evidence` #3 | Requires active-load or latency measurement before claiming simultaneous useful throughput. | Measure active tool/model concurrency and accepted-work latency. | Idle RSS alone proves simultaneous useful throughput. | No active-load/latency measurement proposed. |
| `agent-evals-and-observability/event-trajectory-oracles` #1 | Includes an authenticity challenge using a callback whose correlation IDs look valid. | Send a forged callback with a real-looking thread/call ID to test producer authentication. | Matching IDs authenticate the producer. | Only wrong IDs are tested. |
| `agent-evals-and-observability/event-trajectory-oracles` #2 | Uses external target state or an operation ledger to determine tool-effect correctness. | Inspect target state or the operation ledger for the actual effect. | The success string or process exit proves the external effect. | No independent effect observation. |
| `agent-evals-and-observability/event-trajectory-oracles` #3 | Links event or call identity to persisted checkpoint state across process restarts. | Correlate event/call IDs with durable checkpoint positions across workers. | Each worker success span alone reconstructs the whole task. | No linkage across restarts. |
| `agent-evals-and-observability/event-trajectory-oracles` #4 | Includes process death with deferred input in the proposed recovery tests. | Kill the process with held deferred inputs and inspect loss/redelivery. | Queue tests need no process-loss case for deferred input. | No deferred-input process-death case. |

Review performed against the authored triples: every new assertion has a
satisfying example, a direct contradiction, and an evidence omission. This checks
rubric discriminability on these examples only. The deterministic grader leaves
these prose assertions at manual_review; schema validity and model-judge triage
cannot manufacture a semantic pass. Real-agent generations and external-effect
fault injection remain not assessed by this change.
