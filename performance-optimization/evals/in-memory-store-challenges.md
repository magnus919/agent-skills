# In-memory store assertion challenges

Added 2026-11-03. Existing case IDs and assertions are unchanged. These are authored rubric challenge fragments, not generated model outputs, executed tests, human adjudication or release evidence. Each row isolates an assertion. The omission response is intentionally non-evidential.

## valkey-benchmark-durability-parity

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Does not treat different persistence policies as an equivalent performance comparison. | Compare under equivalent durability requirements before claiming a win. | Disabling persistence is a free optimization with unchanged guarantees. | I will prepare a proposal. |
| Requires pipeline length and concurrency representative of the real endpoint. | Match batching and concurrency to the endpoint's achievable request shape. | Use pipeline 1000 even if production requests cannot batch. | I will prepare a proposal. |
| Requires end-to-end latency and error/timeout evidence beyond component throughput. | Measure endpoint percentiles and completion/error/timeout rates, not only operations per second. | Higher component throughput proves the endpoint meets its latency target. | I will prepare a proposal. |
| Separates a Valkey licensing preference from an unmeasured performance advantage. | Valkey may remain preferred on licensing without a demonstrated speed advantage. | BSD licensing itself proves lower latency. | I will prepare a proposal. |

## leaderboard-lua-collateral-latency

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Identifies server-side script blocking as a hypothesis requiring measurement. | Correlate script execution/queueing with collateral stalls before assigning cause. | Lua cannot block unrelated commands. | I will prepare a proposal. |
| Includes unrelated traffic and tail latency in the comparison. | Measure unrelated endpoints' p99 under representative mixed traffic. | Only the optimized endpoint's successful median matters. | I will prepare a proposal. |
| Requires preservation of ranking/order or snapshot requirements when batching reads. | Verify tie ordering and required snapshot semantics for a bounded native/batched candidate. | Pipelined reads automatically form a consistent snapshot. | I will prepare a proposal. |
| Retains failures and timeouts in the evidence rather than dropping them from the conclusion. | Report all attempts and completion rate beside successful-run latency. | Discard timeouts before computing whether the candidate helped. | I will prepare a proposal. |

