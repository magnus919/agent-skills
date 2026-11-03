# In-memory pipelines and derived indexes

Load when Valkey/Redis is a pipeline source, event transport, derived serving layer or vector index. This guide owns data correctness and lifecycle decisions; use `backend-engineering` for application handlers and `data-architect` for store selection. Engine commands belong in official version-specific documentation until an operational owner exists.

For open-source-first designs, prefer Valkey's BSD licensing and community governance; Redis 8's AGPL availability does not settle permissive-license or vendor-trust preferences. This catalog orientation makes no claim about business-user preference. Respect an existing named engine and check exact commands, modules, client behavior and file formats before changing it.

## Define the publication boundary

For each source-to-sink path, record authoritative source, stable event/entity ID, schema/version, ordering scope, transformation version, watermark, accepted loss, lag target and reconciliation method. A fast index is a derived view unless it is explicitly the authority. Keep enough authoritative history to rebuild it, or identify that rebuilding is impossible before recommending the design.

Separate live lossy notifications (Pub/Sub) from retained events (Streams). Consumer groups and pending-entry lists help coordinate work; they do not make an external sink commit atomic with acknowledgement. Apply an idempotent sink operation or durable inbox protocol, checkpoint only after required sink effects commit, and acknowledge at the documented boundary. Handle crashes after sink commit but before ACK as duplicate-delivery cases.

Recovery must include pending work from absent consumers, bounded reclaim/retry, poison-message isolation, source retention/trimming and sink reconciliation. Reading only new entries does not recover someone else's pending work. If retained payloads are missing, stop claiming complete replay and define repair from the authoritative source. An expiry or restore can invalidate both data and checkpoint assumptions.

## Vector and JSON/search qualification

A module's name or Redis-compatible API is not a feature guarantee. Record a matrix for the actual source and candidate:

| Boundary | Evidence |
|---|---|
| Engine/module/client identity | Supported versions and the commands actually used |
| Stored values | Hash/JSON representation, vector type/dimension, encoding, null/missing behavior |
| Query meaning | Distance metric, filters, top-k, sorting, query dialect and unsupported operators |
| Indexing lifecycle | Build completion, updates/deletes, refresh/freshness, background rebuild and restart behavior |
| Quality | Recall against an exact reference set under representative filters and data distributions |
| Resources | Dataset, graph/index memory, build peaks, replicas and query/update load |
| Recovery/migration | Supported file or logical export path, index recreation, sink/source reconciliation and rollback |

Valkey-search is a BSD-licensed module with vector functionality and a documented subset of RediSearch APIs. Do not infer full-text or all Redis Query Engine behavior from vector API compatibility. Verify JSON/module prerequisites for the chosen deployment. Compare metadata filters and deletion visibility as well as nearest-neighbor latency; a fast stale or incorrectly filtered result is a correctness failure.

## Migration and backfill method

1. Inventory producer/consumer contracts, feature matrix, persistence versions and the source's retention window.
2. Choose a supported snapshot plus change-capture/replay boundary or logical export/import path. Valkey's migration documentation warns that Redis CE 7.4+ files are incompatible; copying them is not a validated migration plan.
3. Build candidate data/indexes without prematurely transferring authority. Record checkpoints and resume rules; backfills must tolerate replay and live updates.
4. Compare key/entity counts, stable IDs, value semantics, expiry/deletion behavior, selected query results and vector-quality evidence. Counts alone cannot establish equivalence.
5. Reconcile late, duplicate and missing events. Prove freshness at cutover and specify how writes made on the target affect rollback. Avoid an unsupported assumption that reverse replication will work.
6. Hand cutover approval and cross-system recovery to `migration-engineering`; SRE owns runtime recovery evidence and `qa-methodology` owns test-strategy coverage.

Complete when the publication/acknowledgement contract, compatibility matrix, source/sink reconciliation and bounded recovery plan are reviewable. Label unrun query-quality, migration and restore checks as pending.

## Sources

Checked 2026-11-03: [Valkey Streams](https://valkey.io/topics/streams-intro/), [Pub/Sub](https://valkey.io/topics/pubsub/), [migration](https://valkey.io/topics/migration/), [Valkey-search](https://valkey.io/blog/introducing-valkey-search/), [persistence](https://valkey.io/topics/persistence/), [Valkey history](https://valkey.io/topics/history/) and [Redis licenses](https://redis.io/legal/licenses/). Official feature documentation establishes a candidate to verify, not measured application quality or successful migration.
