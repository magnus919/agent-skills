# In-memory store assertion challenges

Added 2026-11-03. Existing case IDs and assertions are unchanged. These are authored rubric challenge fragments, not generated model outputs, executed tests, human adjudication or release evidence. Each row isolates an assertion. The omission response is intentionally non-evidential.

## native-counter-and-script-failure

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Chooses a native atomic increment instead of client read-modify-write for the simple counter. | Use the native integer increment for this single-counter invariant. | Keep GET/add/SET; individual command atomicity prevents the race. | I will prepare a proposal. |
| Identifies the cross-slot boundary for the proposed script. | The proposed multi-key script cannot assume atomic execution across independent slots. | Lua makes different cluster slots one atomic transaction. | I will prepare a proposal. |
| Moves predictable argument and type validation before mutations. | Validate both inputs and key types before the first write. | Write the first key and then validate whether the request is valid. | I will prepare a proposal. |
| States that a runtime script error does not automatically roll back earlier mutations. | Test an error after the first mutation and define detection/repair because earlier writes can remain. | Any Lua exception automatically rolls back all previous writes. | I will prepare a proposal. |

## stream-reclaim-duplicate-effects

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Identifies duplicate-effect risk after an external effect but before acknowledgement. | The charge can succeed before ACK, so redelivery can charge again. | A pending-entry list guarantees the charge happens only once. | I will prepare a proposal. |
| Requires a stable effect identity or equivalent durable sink-side deduplication boundary. | Use a stable payment effect ID enforced durably by the sink or equivalent protocol. | Retry each charge with a fresh random identity. | I will prepare a proposal. |
| Recognizes reclaim does not fence a still-running worker from external effects. | Claiming ownership does not revoke the old worker's ability to call the payment service. | Once claimed, the old worker cannot perform any external action. | I will prepare a proposal. |
| Acknowledges only after required durable effects are established. | Acknowledge after the required durable effect/result is established. | Acknowledge first, then attempt the charge. | I will prepare a proposal. |

## pubsub-disconnected-jobs

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Identifies that Pub/Sub subscribers can miss messages while disconnected. | Disconnected subscribers miss Pub/Sub messages. | Pub/Sub replays every message when a subscriber reconnects. | I will prepare a proposal. |
| Requires retained authoritative work and an explicit recovery path for the eventual-processing requirement. | Use a retained work mechanism with defined pending recovery and reconciliation. | Re-subscribe and call the durability requirement met. | I will prepare a proposal. |

