# Valkey-oriented datastore enrichment brief

Researched 2026-11-03 for seven methodology skills following [The Coding Gopher's Redis video](https://www.youtube.com/watch?v=m8_lnw8ORnE). This is a documentary synthesis, not a datastore experiment.

## Findings

1. **Prefer Valkey for open-source-oriented choices.** The author's BSD/community-governance preference remains relevant after Redis 8 added AGPL. Redis acknowledges the 2024 community damage; [Harbor's March 2026 issue](https://github.com/goharbor/harbor/issues/22935) and [April merged PR](https://github.com/goharbor/harbor/pull/23157) supply a named later licensing-risk rationale and adoption decision. Neither proves a community-wide majority or says what business users prefer. Confidence: high in attributed rationale and license facts; population prevalence not assessed.
2. **Primary-store suitability is conditional.** Persistence, HA and sharding have different guarantees. Snapshot/fsync windows, asynchronous promotion, memory pressure and same-slot invariants can invalidate a proposal despite low latency. Confidence: high in documented boundaries; deployment outcomes unassessed.
3. **Application safety needs more than atomic commands.** Native operations avoid simple races; Lua/WATCH address bounded composition, with blocking, runtime-error and retry ambiguity still needing handling. Streams coordinate pending work but do not guarantee exactly-once external effects. Confidence: high in documented mechanisms; application correctness requires tests.
4. **Compatibility must be versioned.** Redis 7.2 lineage and RESP are insufficient evidence for later data-file, JSON/search/vector or rollback compatibility. Confidence: high in the official migration warning and documented search subset; exact deployment parity unassessed.
5. **Performance and cost need representative evidence.** Real pipeline length, network, persistence, working-set overhead, replication, result size, mixed traffic and recovery conditions matter more than an isolated throughput headline. Confidence: high in measurement method; no measured gains claimed.

## Evidence and confidence

| Dimension | Assessment |
|---|---|
| Source quality | Official technical docs and attributed project/vendor statements; source interests recorded |
| Convergence | Valkey and Redis documents agree on the broad persistence/replication boundaries examined; no independent runtime replication here |
| Contradicting values | GNU's AGPL rationale and Google's restriction illustrate differing values/policies, not one universal conclusion |
| Coverage | All consequential video topics mapped; sponsored vendor claims and unverified performance claims excluded |
| Stability | License history is versioned; feature compatibility must be rechecked for the actual deployment |

## Artifacts and application

- [Research log](research-log.md): searches, source evaluation, exclusions, video topic mapping and completion limits.
- [Source ledger](sources.json): URLs, access date, retrieval hashes, individual claims and source-interest notes.
- Focused guides in data-architect, backend-engineering, site-reliability-engineering, data-engineering and performance-optimization; capacity/cost and QA guides are delivered separately to respect the five-skill CI selection cap.
- Skill eval manifests and in-memory-store-challenges.md: stable new cases and assertion-level challenge triads. They specify intended behavior; they do not certify runtime or model quality.

## Open questions for deployment work

Which engine/module/client versions are in use? What loss/freshness and invariant boundary is required? Which failure modes have actually been exercised? How do target writes affect rollback? Which data/query distribution supports the capacity and latency claims? These are intentionally not guessed from a video or vendor announcement.
