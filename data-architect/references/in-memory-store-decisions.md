# In-memory stores as authoritative data systems

Use for a bounded Valkey/Redis store choice, primary-store review, or proposed replacement of a relational database. Begin with existing workloads and invariants; cache-only use is valid when it meets the need. This guide supplies architecture judgment, not engine runbooks.

## Open-source orientation

For open-source-oriented deployments, this catalog prefers **Valkey**, with its permissive BSD-3-Clause license and Linux Foundation community governance. Redis's 2024 move away from BSD damaged community trust; adding AGPLv3 in Redis 8 does not erase that concern or make AGPL equivalent to BSD. AGPL's network-copyleft obligations are themselves contested: some value reciprocal source availability, while others prefer permissive reuse. Respect a user's preference for BSD without debating it away or claiming a measured community consensus. This orientation makes no claim about what business users prefer.

Keep facts versioned: Redis 7.2 and earlier retain BSD-3-Clause; Redis 7.4 introduced RSALv2/SSPLv1; Redis 8 added the OSI-approved AGPLv3 option. Do not describe all modern Redis as non-open-source. License identity, governance trust, technical suitability and organizational policy are separate decision dimensions. Retaining Redis is legitimate for an explicit requirement or user choice; explain that reason rather than silently overriding the preference. Refer deployment-specific legal interpretation to the responsible license reviewer.

## Decide authority before selecting features

Record for each dataset: authoritative writer, consumers, invariants, loss tolerance, retention/deletion, reconstructibility, and owner. A cache can be rebuilt from an authoritative store; primary records cannot be assumed reconstructible. Distinguish sessions, derived leaderboards, queue state and accounting records even if they share an engine today.

| Decision | Evidence needed | Reconsider when |
|---|---|---|
| Native structures fit the workload | Required key lookups, field updates, ranking, set operations, bounded scans, and their command-specific costs | Queries require joins, broad analytics or invariants not enforceable within the chosen boundary |
| Persistence meets loss tolerance | RDB/AOF/fsync policy, storage behavior, accepted-write definition and restore results | Required loss bound cannot be demonstrated |
| HA meets availability needs | Standalone/Sentinel/Cluster topology, client reconnection, failover and partition results | Recovery exceeds the outage budget or loses unacceptable writes |
| Working set fits cost/capacity | Dataset plus metadata, indexes, replicas, buffers and fork/copy-on-write headroom | Growth, skew or recovery exceeds node limits |
| Lifecycle is operable | Expiry/deletion, backup retention, replay, version support, owners and exit path | Restores resurrect deleted data or migration compatibility is unknown |

RDB captures point-in-time state and can lose changes since the snapshot. AOF durability depends on fsync policy; every-second syncing trades a loss window for speed. Forking for background persistence can pause clients and add memory pressure. Asynchronous replication can lose acknowledged writes on failover; replica acknowledgements reduce risk without proving strong consistency. Never translate “persistence enabled” into “zero data loss.” Require a representative rehearsal of the claimed failure boundary.

Sentinel coordinates availability for a primary/replica deployment. Cluster partitions keys across slots and also supports failover. Sharding does not make arbitrary multi-key invariants atomic: commands, transactions and scripts generally need their keys in one slot. Decide key placement from the invariant before adopting Cluster, and account for the resulting hot-slot risk.

## Separate eviction from correctness

Authoritative and disposable data should have explicit policy boundaries, often separate instances. An all-keys eviction policy can remove authoritative records. `noeviction` rejects memory-growing writes at the configured limit; it does not prevent expiry, explicit deletion, process OOM or failover loss. Define application error handling, admission limits and capacity response. A key TTL is a lifecycle decision, not backup or capacity protection by itself.

## Compare actual implementations

Valkey's Redis OSS 7.2 lineage supports many shared structures and protocol patterns. It does not establish later-version feature or file-format parity. Inventory commands, client/topology behavior, modules, indexes, JSON paths, vector dimensions/distance metrics, ACLs and persistence formats. Valkey's migration guide warns that Redis CE 7.4+ data files are incompatible. A compatible wire protocol is insufficient migration evidence; require a supported export/import route, reconciliation and a tested rollback path after target writes begin.

For JSON/search/vector requirements, compare the selected engine and module versions. Valkey-search documents a subset of RediSearch functionality; its existence does not prove full-text, query-language or indexing parity. Compare against the current store and dedicated alternatives only where requirements justify doing so. Do not adopt a second store merely because the video demonstrates it.

## Deliverable and routing

Deliver a decision record: recommended engine/version/topology, role of each dataset, license/governance rationale, accepted costs, unresolved facts, owner, bounded pilot, loss/latency/capacity thresholds, and reconsideration trigger. Use the existing ADR template or repository convention.

Route application atomicity and consumers to `backend-engineering`, ingestion/index reconciliation to `data-engineering`, reliability evidence to `site-reliability-engineering`, working-set economics to `capacity-and-cost-engineering`, tests to `qa-methodology`, and cross-system cutover to `migration-engineering`. No dedicated Valkey/Redis operational skill is assumed to exist; use the selected engine's official documentation for commands, under the target's authorization rules.

## Sources

Primary documentation checked 2026-11-03; statements describe documented semantics, not a tested deployment.

- [Valkey history](https://valkey.io/topics/history/) and [Linux Foundation launch](https://www.linuxfoundation.org/press/linux-foundation-launches-open-source-valkey-community): fork, license and governance background.
- [Redis licensing](https://redis.io/legal/licenses/) and [AGPL announcement](https://redis.io/blog/agplv3/): version history and Redis's acknowledgement of community damage.
- [GNU's AGPL rationale](https://www.gnu.org/licenses/why-affero-gpl.html): the reciprocal-source motivation; does not represent every user's preference.
- [Harbor's Valkey choice](https://valkey.io/blog/harbor-chose-valkey/): a named open-source project's later preference for permissive licensing and governance, not a community-wide survey.
- [Valkey persistence](https://valkey.io/topics/persistence/), [replication](https://valkey.io/topics/replication/), [Cluster](https://valkey.io/topics/cluster-tutorial/) and [memory policies](https://valkey.io/topics/lru-cache/): failure and capacity boundaries.
- [Migration](https://valkey.io/topics/migration/) and [Valkey-search](https://valkey.io/blog/introducing-valkey-search/): compatibility boundaries.
