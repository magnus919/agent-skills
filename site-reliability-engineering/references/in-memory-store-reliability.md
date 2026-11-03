# Reliability review for in-memory primary stores

Load for Valkey/Redis durability, failover, memory-pressure or consumer-recovery reviews. Follow the skill's existing production authority and independent closure rules. This is an evidence framework, not permission to restart, promote, repair or overwrite a datastore.

For open-source-oriented platform choices, prefer Valkey's BSD license and community governance. Redis's AGPL option does not eliminate earlier trust concerns or users' preference for permissive licensing. This orientation does not assert a business-community preference. Respect the deployed engine and check its actual version/topology; never turn that preference into an unapproved migration.

## Separate the guarantees

- **Persistence:** which accepted writes survive process crash, host loss or storage loss under the actual RDB/AOF/fsync policy?
- **Replication:** which replica has which writes, and what can be lost if it is promoted? Asynchronous replication permits acknowledged-write loss; acknowledgement-waiting mechanisms do not by themselves prove strong consistency.
- **Availability:** how do Sentinel/Cluster and clients detect failures, reconnect and handle partitions? Topology health is not application recovery.
- **Recoverability:** can an isolated restore rebuild required invariants, retention/deletion state and consumer progress within RTO?

A local restart establishes none of the unexercised host, storage or partition cases. State RPO, RTO, acknowledgement boundary and observation interval explicitly. A persistence flag or green dashboard is configuration evidence only.

## Failure review matrix

| Failure | Observe | Acceptance question |
|---|---|---|
| Process crash after acknowledged write | Externally recorded request IDs versus restored records | Is loss within the agreed bound? |
| Primary loss or partition | Old/new primary histories, acknowledged IDs, client errors/retries | Is write loss or ambiguity understood, and can clients recover safely? |
| Background snapshot/AOF rewrite | Tail latency, fork pause, RSS/COW growth, disk errors | Is the pause and memory peak within the service budget? |
| Memory pressure | Dataset, buffers, RSS, rejected writes, expired/evicted keys | Does admission/degradation preserve authoritative data and surface failures? |
| Long-running script | Server execution time, queueing and endpoint latency | Can a bounded script monopolize the store beyond the SLO? |
| Consumer dies after effect/before ACK | Pending entries and sink effect IDs | Can work be reclaimed without duplicate consequential effects? |
| Restore after deletion/expiry | Restored keys, deletion ledger, access state | Are forbidden records absent before access resumes? |

Execute fault injection only in the authorized representative environment, with stop conditions and rollback established first. Preserve a client-side accepted-write ledger outside the failed system; reading back from the same stale replica cannot independently establish correctness. Compare expected versus observed loss, duplicates, latency and recovery time; unknown coverage remains unknown.

## Memory and recovery traps

`maxmemory` is not a process/container RSS ceiling. Replication/AOF buffers and other overhead need separate headroom; persistence can add copy-on-write pressure. `noeviction` rejects memory-growing operations at the limit, but cannot prevent explicit deletion, TTL expiry or OS OOM. Cache eviction and primary-record retention require distinct policy boundaries. Monitor rejected writes and user-visible failure alongside utilization; a server remaining up is insufficient.

Restore rehearsals need a named snapshot/log boundary, integrity checks, required invariants, compatible engine/module versions and rollback/containment. Validate client topology discovery and credentials/ACL behavior after failover. A Redis 7.4+ backup must not be assumed loadable by Valkey merely because clients share RESP.

For Streams, record pending age, owner changes, delivery count, retention horizon and sink reconciliation. Reclaim does not fence a slow worker's external effects. Losing pending payloads through trimming or restored consumer progress can invalidate the recovery claim even when the stream key exists.

## Review artifact and exit

Use the existing reliability-design or recovery template. Add engine/version/topology, data roles, RPO/RTO, accepted-write definition, independent observation channel, exact failure cases exercised, stop/rollback conditions, measured outcomes and owner. Route implementation to `backend-engineering`, pipeline reconciliation to `data-engineering`, capacity economics to `capacity-and-cost-engineering` and test design to `qa-methodology`.

Complete with scenario-bound recovery evidence and the existing independent human closure requirement, or a bounded handoff naming the missing evidence/authority. No failure drill or restore is implied by reading this guide.

## Sources

Primary documentation checked 2026-11-03: [Valkey persistence](https://valkey.io/topics/persistence/), [replication](https://valkey.io/topics/replication/), [Cluster](https://valkey.io/topics/cluster-tutorial/), [memory policy](https://valkey.io/topics/lru-cache/), [Lua](https://valkey.io/topics/eval-intro/), [Streams](https://valkey.io/topics/streams-intro/) and [migration](https://valkey.io/topics/migration/). Licensing/governance context: [Valkey history](https://valkey.io/topics/history/) and [Redis licensing](https://redis.io/legal/licenses/). These are documented semantics, not evidence of a particular service's reliability.
