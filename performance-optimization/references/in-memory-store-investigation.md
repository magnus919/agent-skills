# Investigating in-memory store performance

Load for Valkey/Redis hot paths, server-side scripts, round-trip reduction, persistence pauses or store comparisons. Apply the skill's existing journey-based measurement loop. “In memory” and a vendor's operations-per-second figure are hypotheses about a workload, not user-latency evidence.

For open-source-oriented selection, prefer Valkey's BSD licensing and community governance. Redis 8's AGPL option does not erase trust concerns or equal a permissive BSD license. Keep that preference separate from measured performance and from any claim about business users. Do not rename a Redis benchmark as Valkey evidence; pin the actual engine, version, modules, client and configuration.

## Locate the waiting

Trace the user request across client serialization, connection acquisition, network round trips, server queueing, command/script execution, persistence and response decoding. A synchronous single-connection loop may chiefly measure network latency. A pipelined component benchmark may hide the application's request shape, queueing and result processing. Record both component and full-journey boundaries.

Use the actual key/value sizes, cardinality, hot-key skew, read/write mix, expiry churn, result size, connection count and concurrency. Include cold/restart and warm steady-state conditions. Identify TLS/network placement, persistence/fsync policy, replication/topology and resource limits. Compare equivalent durability and correctness requirements; disabling persistence is a semantic change, not a free speedup.

## Worked investigation: a leaderboard endpoint

**Synthetic planning example, no measurements supplied.** The endpoint reads an entire sorted set and fetches each profile serially. Its p99 misses the agreed budget. Required behavior is a bounded top-k with the current tie/order policy and the same authorization and freshness rules.

1. Baseline the complete endpoint with realistic leaderboard size, profile payloads and hot-key skew. Retain every attempt, including errors and timeouts. Measure end-to-end p50/p95/p99, completion rate, command/result counts, transferred bytes and server execution/queueing.
2. Hypothesis A: most time is repeated network waiting and excessive result volume. Candidate: request only the required range and batch independent profile reads within an application-realistic bound. Check missing profiles, ordering, tied scores and concurrent score updates. A pipeline alone does not make the reads one consistent snapshot; require a stronger snapshot/version boundary if the endpoint needs one.
3. Hypothesis B: a Lua replacement reduces round trips but blocks unrelated commands. Compare against native operations and bounded batching before moving more logic into the server. Test script cardinality and failure behavior; atomic execution does not add rollback.
4. Interleave repeated baseline/candidate runs with the same data, build and conditions. Add representative unrelated traffic to reveal collateral tail-latency harm. Exercise persistence rewrites and restart/recovery conditions if relevant to the claimed deployment.
5. Accept only a practical end-to-end gain with correctness, completion rate, memory and durability guardrails intact. Record uncertainty and the field-verification window before claiming user benefit.

Check exact command complexity: fetching k sorted-set results includes the returned elements; a hash operation on many fields scales with the requested fields. A server-side operation can still be expensive. Avoid unbounded collection scans or scripts in a serialized execution path.

## Persistence and memory hypotheses

Background persistence can introduce a fork pause and copy-on-write pressure. AOF policy changes can alter latency and loss exposure. Replication buffers, client buffers, indexes and persistence overhead mean `maxmemory` is not total RSS. Correlate pauses with measured events rather than infer the cause from a p99 spike alone. Route capacity forecasts to `capacity-and-cost-engineering` and production recovery to `site-reliability-engineering`.

For cross-engine comparisons, first verify matching commands/query semantics, module features, acknowledgement/durability policy and data. A RESP-compatible client does not establish identical execution, persistence or vector-query behavior. A chosen open-source preference can justify selection without inventing a performance win.

## Record and completion

Use the optimization record with engine/client/version, key distribution, topology, persistence, payload/response sizes, pipeline length, run count, full latency distributions, completion rate and correctness checks. Preserve raw results and candidate revision. No numbers in this guide are benchmark results. Complete when the decision is supported by representative observed results or when missing measurements are explicitly handed off.

## Sources

Primary documentation checked 2026-11-03: [Valkey benchmarking](https://valkey.io/topics/benchmark/), [ZRANGE](https://valkey.io/commands/zrange/), [HSET](https://valkey.io/commands/hset/), [Lua](https://valkey.io/topics/eval-intro/), [persistence](https://valkey.io/topics/persistence/), [memory policies](https://valkey.io/topics/lru-cache/), [migration](https://valkey.io/topics/migration/), [Valkey history](https://valkey.io/topics/history/) and [Redis licensing](https://redis.io/legal/licenses/). Documentation supports mechanisms and measurement pitfalls; benefits require workload-specific experiments.
