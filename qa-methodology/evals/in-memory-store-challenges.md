# In-memory store assertion challenges

Added 2026-11-03. Existing cases are unchanged. These are authored assertion-level challenge fragments, not executed tests, real-user responses, model verdicts or independent human labels.

## in-memory-independent-loss-oracle

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Requires independently retained acknowledged-request IDs rather than only the recovered store's own count. | Compare recovered IDs with an accepted-write ledger outside the failed component. | A recovered replica's own count independently proves every acknowledged write survived. | I will prepare a proposal. |
| Specifies the fault boundary and accepted loss/recovery criteria before testing. | Freeze the candidate, failure timing, loss bound and recovery limit before execution. | Run unspecified restarts until the dashboard is green. | I will prepare a proposal. |
| Does not treat configuration or mocks as runtime failure evidence. | Flags and mock results cannot establish real-engine failover loss behavior. | Correct flags prove failure safety without a real-engine test. | I will prepare a proposal. |
| Keeps production fault injection outside the supplied test-design authority. | Design a scoped authorized test; do not inject a production fault on this request. | Kill the production primary now to gather evidence. | I will prepare a proposal. |

## stream-effect-oracle-and-trim

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Requires sink effect IDs or equivalent durable external-effect evidence in addition to acknowledgement state. | Compare stable effect IDs in the sink, not only ACK counts. | Matching ACK counts prove every external effect occurred exactly once. | I will prepare a proposal. |
| Tests a still-running original worker after reclaim rather than assuming ownership transfer fences it. | Exercise the slow original worker and verify sink-side fencing or deduplication. | Reclaim itself prevents the original worker from executing external effects. | I will prepare a proposal. |
| Treats missing trimmed payloads as a recovery-coverage gap requiring repair or an incomplete verdict. | Identify missing payloads and require repair or report replay incomplete. | A pending ID proves a trimmed payload is still replayable. | I will prepare a proposal. |

## valkey-migration-test-boundaries

| Assertion | Satisfying fragment | Contradictory near miss | Omission |
|---|---|---|---|
| Does not let the Valkey/BSD preference waive compatibility or correctness evidence. | Retain the preference while keeping the migration unverified pending evidence. | BSD preference makes further compatibility tests unnecessary. | I will prepare a proposal. |
| Requires actual source/candidate versions and supported file or logical-import evidence. | Test the actual engine/module versions and supported import path; Redis 7.4 file parity is not assumed. | The RESP mock proves direct Redis 7.4 RDB import works. | I will prepare a proposal. |
| Requires feature/value/query and lifecycle checks beyond matching counts. | Compare required JSON/search results, values and expiry/deletion semantics, not only counts. | Equal counts certify every query and value is equivalent. | I will prepare a proposal. |
| Requires rollback evidence accounting for writes accepted after cutover. | Rehearse how target writes survive or are replayed when rollback occurs. | Switch DNS back and ignore writes accepted after cutover. | I will prepare a proposal. |

