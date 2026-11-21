# Implementation and evaluation

## Personal vault or assistant

Use a local directory or source API as the authority and a rebuildable index.
Persist source IDs, revision hashes and precise locations in a manifest. Start
with local full-text search and add passage embeddings if the held-out
paraphrase cases need them. Preserve original files alongside derived assets.
On edits, deletes, or moves, reconcile by stable identity and version. Keep a
small authorized, exact search path available during rebuilding.

For example, search a personal notebook by title, tags, and exact phrases.
Add semantic passage search for remembered concepts, and resolve to exact
sections for citations. Track an explicit profile preference that supersedes
its predecessor. Keep inferred notes reviewable and reversible. Add graph
edges when backlink or relationship questions need evidence beyond passages.
Use a scoped local or explicitly selected remote model and decide which
documents and screenshots may leave the device.

## Shared enterprise service

Define resource ownership before building a connector. A central group can
operate the service while teams own source ACLs, classification, and
publication. One gateway authenticates principals and delegates scoped
queries to tenant-specific resources or pooled storage. Keep tenant ID and
policy data in job, storage, graph, cache, metrics, and backup keys. An
approved tenant can publish a sanitized collection to another tenant through
a versioned share policy.

Example flow for an operations and finance knowledge service:

1. A connector reads approved source locations and captures content,
   authoritative ACLs, and revision IDs. Missing or unmapped ACLs keep records
   unavailable. The catalog maps source group identities to tenant principals.
2. Workers stage section-level evidence and image crops by policy boundary.
   An index points at immutable source versions, and publication selects a
   complete eligible snapshot. The connector cannot publish inferred financial
   guidance, grant access, or move records across tenants.
3. The query planner binds tenant and acting user, scopes each retriever, and
   checks approved content before reranking and generation. An authorized
   reader can query an ops policy while finance-only appendices, graphs, and
   analytics remain inaccessible. Exact citations carry policy checks through
   the UI and export endpoint.
4. A finance steward can supersede guidance. A revoked group loses service-side
   access within the agreed budget even when old vector, visual, and graph
   artifacts still await cleanup. A permissions-only change propagates without
   relying on file content modification. Restore replays authority changes
   before reopening reads. Paused connectors, stale sources, and partial
   indexes have explicit user-visible behavior.

## Evaluate before rollout

Build a frozen set of cases tagged by evidence type, principal, authorization
policy and version, time cutoff, and valid citation locators. Compare the same
generation conditions and token budgets across retrieval variants. Track:

| Layer | Evidence and pass criteria to define |
|---|---|
| Retrieval | Authorized recall@k or nDCG by category and ACL selectivity, evidence coverage across hops, correct page/region/time localization |
| Answer | Claim support, completeness, precise citation resolution, abstention when evidence is missing or denied |
| Temporal | Correct validity and recording cutoffs, compatible windows/units, deterministic statistic, held-out forecast calibration by horizon |
| Access | Allowed and denied retrieval/write/serve cases, including same role in another tenant, restricted fragments, and service principals |
| Lifecycle | Revocation under warm caches and delayed jobs, source corrections, partial reindex, restore, deletion of descendants and derived media |
| Operations | p50/p95 latency by branch and tenant, index lag, cost, storage, job backlog and capacity under skewed tenants |

Use an allow/deny pair with high semantic similarity and vary one permission at
a time. Include canary evidence in denied test fixtures. Verify its absence
from outputs, model-bound requests, caches served to the caller, and citation
resolution. Inspect authorized evidence reachability separately from answer
value. An expected denial passes only while the legitimate access path still
works. Diagnostics must protect caller identities and evidence.

Run tests under the actual retrieval credentials and installed datastore or
connector versions. Required safety properties are gates independent of
relevance metrics. Roll out in shadow mode or to an explicit subset, retain
authorized baseline retrieval, and rehearse rollback with current deletion
and access state. Define owners and thresholds before comparing variants.
