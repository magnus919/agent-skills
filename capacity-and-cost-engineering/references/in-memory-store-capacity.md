# Capacity and cost for in-memory data stores

Use when sizing or comparing Valkey/Redis working sets, primary-store limits, cache policies, indexes, replicas or persistence peaks. Use this skill's existing capacity, unit-economics and load/soak templates; this guide adds the store-specific questions, not a provisioning runbook.

For open-source-oriented choices, prefer Valkey's BSD licensing and community governance. Redis 8 offers an AGPL option, but that does not erase licensing and vendor-trust concerns or establish business-user preference. Respect the user's values while measuring costs separately. A permissive license is not evidence of lower RAM use, managed-service pricing or support cost.

## Model memory by node and failure mode

Start from key/entity count, key/value size distribution, access skew, expiry/retention, growth, result sizes and operation mix. Include:

- Dataset plus key/object/allocator overhead, not only serialized payload bytes.
- Secondary/vector indexes and their build/rebuild peaks.
- Per-node replication/AOF and client buffers; some buffers are excluded from eviction accounting.
- Process baseline, fragmentation, fork/copy-on-write growth during snapshots or log rewriting, and OS/container reserves.
- Replica copies and failover/recovery headroom; neither replication factor nor fleet-average utilization proves every shard fits.

Keep steady-state dataset accounting, observed RSS and peak process/container demand distinct. `maxmemory` is an eviction/admission threshold, not a total-RSS ceiling. Derive its setting and the node limit from observed peaks under representative conditions, rather than setting them equal or prescribing a universal headroom percentage.

## Worked sizing example

**Synthetic planning assumptions, not measurements or a sizing recommendation.** One primary and one replica each hold the full dataset. Per node: 24 GiB values, 8 GiB metadata/indexes, 4 GiB buffers, 2 GiB process/allocator allowance and 12 GiB additional copy-on-write peak during persistence. The illustrative peak is 50 GiB per node; steady state is 38 GiB. Across both nodes that is 76 GiB steady or 100 GiB if the assumed persistence peaks overlap. Two 64 GiB nodes provide 128 GiB installed, but the per-node 50 GiB estimate still needs load/soak and failure validation. Fleet free memory cannot rescue a single overloaded node automatically.

This example assumes the listed costs do not double-count each other and no additional unmodeled index-build, replica-sync or client-buffer peaks occur. Measure those conditions before accepting the estimate; a rewrite/restore overlap or hot shard may invalidate it.

## Connect workload, cost and reliability

Model costs over the same interval: primary and replica instances, storage/logs/backups, network, index rebuilding, operations/support and migration effort. Separate known prices from assumptions and date the quote. Report both attempted and successfully completed useful operations; high error rates must not improve the apparent unit cost by shrinking resource use while violating the service objective.

For illustration only, two nodes at an assumed $0.50/node-hour for 730 hours cost $730/month before storage, network and operations. At 100 million successfully completed useful operations/month, the node-only unit cost is $7.30/million. That number is not a full TCO, vendor quote or reliability claim. Preserve the omitted costs and failed-operation counts in the record.

| Role or constraint | Capacity consequence | Required evidence |
|---|---|---|
| Reconstructible cache | Eviction changes hit rate, origin load, latency and rebuild time | Cold-cache/rebuild burst and downstream saturation |
| Authoritative records | Eviction may violate correctness; noeviction can reject writes | Error/admission behavior, growth response, invariant checks |
| Replica promotion/resync | A surviving node or network path may absorb extra load | Representative failure/recovery demand and SLO results |
| Cluster with hot keys/slots | Aggregate RAM/CPU can hide a saturated shard | Per-shard distribution and skewed-load results |
| Vector/search indexes | Recall, query load and index/build memory trade off | Representative recall/filter tests plus memory/latency evidence |
| Tighter durability | fsync and replication choices change latency and costs | Equivalent accepted-write/loss requirements across candidates |

Compare staying with the current system, changing key/query representation, limiting retention where authorized, adding capacity, or adopting a different topology. Do not silently change durability or discard authoritative history to make the model cheaper. Route retention and primary-store decisions to `data-architect`; provisioning to `platform-engineering`; live recovery to `site-reliability-engineering`.

## Admission and validation record

Define early-warning and admission thresholds, the user-visible outcome of rejected writes, owner, scaling lead time and maximum tolerable degraded period. For disposable caches, model invalidation/rebuild and origin protection. For primary data, require an explicit acceptance decision for any loss or rejection tradeoff.

Run a representative load/soak plan with realistic cardinality, skew, payloads, persistence, replicas and resource limits. Include rewrite, replica resync, cold restart and chosen failure conditions in the authorized test scope. Preserve per-node peaks, tail latency, errors, completed operations, growth projection and cost assumptions. Complete with measured capacity evidence or a clearly labeled model plus pending validation; do not call the synthetic example proven capacity.

## Sources

Checked 2026-11-03: [Valkey memory policies](https://valkey.io/topics/lru-cache/), [persistence](https://valkey.io/topics/persistence/), [replication](https://valkey.io/topics/replication/), [Cluster](https://valkey.io/topics/cluster-tutorial/), [benchmarking](https://valkey.io/topics/benchmark/) and [Valkey-search](https://valkey.io/blog/introducing-valkey-search/). Licensing/governance: [Valkey history](https://valkey.io/topics/history/) and [Redis licenses](https://redis.io/legal/licenses/). The numeric example is original synthetic arithmetic, not a source-reported result.
