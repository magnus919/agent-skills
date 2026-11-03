# Failure-oriented tests for in-memory stores

Load when reviewing Valkey/Redis primary-store safety, atomic updates, stream consumers, or migration compatibility. This guide specifies risks, observable oracles and coverage. It does not provide engine operations or authorize destructive fault injection. Use `backend-engineering` for implementation, `data-engineering` for pipeline reconciliation, `data-architect` for requirements, SRE for authorized runtime recovery and `migration-engineering` for cutover.

For open-source-oriented selection, preserve the catalog's Valkey/BSD and community-governance preference. Redis's AGPL option does not resolve every permissive-license or trust concern. This orientation does not establish a business-community preference or waive equivalent correctness tests. Pin actual engine/version/modules/client; a Redis-compatible mock is not sufficient evidence of Valkey failure behavior.

## Start with a guarantee and independent oracle

Record the system boundary, invariant, accepted-write definition, loss/duplicate tolerance, freshness, latency and recovery limits before running tests. Freeze the candidate/configuration, fixture, load, fault trigger, observation interval, success criteria, cleanup/rollback and owner. Execute only in a scoped authorized environment; production mutation needs its own approval under the owning policy.

Keep test input IDs and an externally recorded accepted-request/effect ledger outside the component being failed. Use durable sink effect IDs and direct artifact/query inspection for correctness; configuration flags, dashboards and an agent's narrative are not substitute oracles. Distinguish an attempted request, an acknowledged write, a recovered record, a delivery acknowledgement and a completed external effect.

## Risk-to-test matrix

| Scenario | Trigger/boundary | Observable oracle |
|---|---|---|
| RDB or AOF loss window | Crash at a controlled point after recorded acknowledgements | Accepted IDs versus recovered records; measured loss against the agreed bound |
| Failover/partition | Primary fails or is isolated after accepting writes | External accepted-write history versus promoted state, client retries and errors |
| Memory pressure | Representative buffers/indexes and persistence activity approach the actual limit | RSS, rejected writes, evictions/expiry, service completion and record invariants |
| Concurrent counter/update | Competing clients at the invariant boundary | Expected effect count and final state, including ambiguous/lost replies |
| Script runtime error | Valid first mutation followed by a controlled failure | Direct state inspection showing what persisted and how detection/repair handles it |
| Cross-slot composition | Keys deliberately placed in different Cluster slots | Rejection/handled boundary rather than a false atomicity claim |
| Pub/Sub disconnect | Subscriber offline during publication | Missing live events and any separately specified resynchronization path |
| Stream effect-before-ACK crash | Sink commits, worker stops before acknowledgement | Pending state, replay and sink effect IDs; no duplicate consequential effects |
| Reclaim while original is slow | New owner begins while original can still act | External effect fencing/deduplication evidence, not merely consumer ownership |
| Trimmed pending payload | Retention removes data still required for recovery | Identified replay gap plus authoritative repair or an incomplete result |
| Engine/module migration | Real source/candidate versions and representative features | Supported import path, value/query/TTL equivalence and target-write rollback rehearsal |
| Restore after deletion | Restore predates a required deletion | Deletion authority reapplied and absence verified before access resumes |

Prioritize by impact and plausible failure mechanisms. Change fault timing and inputs around meaningful boundaries; repeated success at one timing is not coverage of every possible interleaving. Account for failed and timed-out attempts rather than analyzing only successful runs.

## Choose evidence at the right level

- Unit tests cover argument/type validation, conflict/retry decisions, deterministic transformations and compensation choices.
- Real-engine integration tests cover actual command errors, slots, persistence formats, client redirect/reconnection and script behavior. A fake adapter cannot establish them.
- Controlled failure/load tests cover loss, duplicates, tail latency, recovery time and memory under representative configurations. Use capacity/cost methodology for capacity claims and SRE's separate authority/closure gates for incident outcomes.
- Migration acceptance compares source and target IDs/values, required queries, expiry/deletion, indexes and post-cutover writes. Matching counts alone can hide different missing/extra records.

A consumer group is not an exactly-once effect oracle. An ACK can be lost after an effect commits, and a reclaimed old worker can still perform external work. Use the business effect ledger to verify the stated boundary. A test environment without the real sink can only establish the narrower simulated boundary.

## Test report and exit

Report candidate SHA/build, actual server/module/client versions, persistence/topology, input identity, fault interval, independent observations, expected versus observed loss/duplicates, latency/completion, recovery outcome and unexercised scenarios. Link raw results and state the evidence class: mock, real-engine integration, controlled failure or observed deployment. Do not invent results for unrun scenarios.

Developer tests remain appropriate; independent acceptance requires a separate evaluator and reviewed oracles, not a claim that a fresh model session removes correlated error. A schema-valid skill eval manifest is unrelated to whether a deployed datastore survived a fault test. Complete when the scoped strategy maps each consequential guarantee to evidence and names remaining gaps; route the verdict to `verification-methodology` and release decisions to `release-engineering`.

## Sources

Primary documentation checked 2026-11-03: [Valkey persistence](https://valkey.io/topics/persistence/), [replication](https://valkey.io/topics/replication/), [memory policies](https://valkey.io/topics/lru-cache/), [transactions](https://valkey.io/topics/transactions/), [Lua](https://valkey.io/topics/eval-intro/), [Cluster](https://valkey.io/topics/cluster-tutorial/), [Pub/Sub](https://valkey.io/topics/pubsub/), [Streams](https://valkey.io/topics/streams-intro/) and [migration](https://valkey.io/topics/migration/). Licensing context: [Valkey history](https://valkey.io/topics/history/) and [Redis licenses](https://redis.io/legal/licenses/). The matrix is a synthesized test design; no drills are claimed executed.
