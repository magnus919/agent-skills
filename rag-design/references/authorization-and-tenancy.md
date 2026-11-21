# Authorization and tenancy

A tenant owns a security and lifecycle boundary. A corpus is a searchable
collection inside a boundary. A workspace, department, group, or independent
customer may have different meanings in the identity model. Establish
cross-tenant federation or publication as an explicit policy owned by the
source tenant.

| Topology | Fit | Design obligation |
|---|---|---|
| Personal, local | One principal and a laptop, workstation, or private service | Scope file roots and accounts, isolate private and shared spaces, secure remote providers and sync |
| Pooled | Shared serving and indexes for many tenants | Server-bound tenant routing and mandatory per-object gates on every path, plus quotas and restore isolation |
| Bridge | Shared service with dedicated tenant indexes, graph partitions, or stores | Map security and lifecycle boundaries per resource, reconcile routing during moves |
| Silo | Dedicated tenant deployment or data plane | Validate identity, keys, backups, noisy-neighbor constraints and operator access per silo |

## Roles and the evidence atom

RBAC assigns actions to tenant roles. Use resource scopes or source ACLs,
relationship checks, and context rules to evaluate a particular action on a
particular object. A tenant reader may search an approved corpus and still be
denied a private document or section. An index write credential supplies
technical ability. User or service authorization supplies the right to write
the particular resource.

| Example role | Example grant | Additional boundary |
|---|---|---|
| Reader | Search, read, resolve citations | Effective source grants and release scope |
| Contributor | Submit or update drafts in assigned workspace | Cannot publish, share, or edit others' drafts unless explicitly granted |
| Steward | Publish, supersede, reclassify, or revoke within owned corpus | Source policy governs expansion of audience |
| Connector/worker | Ingest, project, reindex, or propose enrichment | Tenant-bound service identity, named sources and destinations, separate publish capability |
| Tenant admin | Manage configuration and roles for tenant | Content access requires its own policy grant |
| Auditor | Read permitted decision and lineage metadata | Payload, export, and break-glass access are separately controlled |

Choose the smallest **independently governable** evidence unit. It could be a
document version, a section or span, a table row or field, a graph assertion
or property, an image region, or a metric series and interval. Ordinary chunks
inherit parent policy. If a source can restrict a section, split it along that
boundary before embedding, summarizing or rendering. Never widen access when
expanding a chunk into its parent, fusing with related hits, or generating a
thumbnail from a restricted page. If policy cannot safely express the desired
fragment scope, redact at ingestion or withhold the object.

Record tenant, immutable object/version ID, source and locator, policy reference,
classification, ownership, validity, deletion state, and dependencies. A
single-source projection inherits source constraints. Default to access only
when the caller may use **every contributing dependency** for the requested
operation. A derived assertion supported by several independent sources can
have separately published renderings based on an authorized evidence set.
A broad aggregate, summary, or redaction needs a defined declassification
decision and separate release policy. Check metadata and existence as well as
payload. Apply the rule at construction and publication as well as retrieval.

## Enforce along both paths

1. Bind identity and tenant from a verified session or delegation. Evaluate
   requested action and candidate scopes. Define deny, freshness, group
   membership, inherited policy, export, and data-provider rules with owners.
2. Use datastore-native constraints where available and require scoped
   queries for lexical, vector, graph, time-series, and object retrieval.
   For a relationship policy service, compare entitlement enumeration,
   filtering on scope tags, and bounded batch checks. Candidate IDs inside
   a trusted retrieval boundary can be rechecked before reading payload.
   Track policy-filtered recall and existence/aggregate disclosure risks.
3. Confirm source/version and current authorization before content leaves
   the trusted boundary for reranking, model calls, rendering or exports.
   Recheck citation and object URLs on dereference. Apply the same policy to
   history, autocomplete, graph expansion, fallback, jobs, and telemetry.
4. On write, verify the user/worker grant for the operation and target, bind
   tenant and ACL server-side, and validate source/provenance. Store changes
   with version preconditions and invalidate projections and caches. Require
   separate authority for sharing or promoting agent proposals.
5. Define a maximum revocation lag. Change canonical authority first, and
   suppress stale projections until caught up via policy versions, tombstones,
   or authoritative checks. Cache by effective scope and source/policy
   versions or reauthorize every dependency at reuse. Recheck on new reads
   of stored conversations or exports served by the system. For streaming,
   define the point of authorization and cancellation behavior. Previously
   delivered copies require their own handling. Reconcile descendants,
   permissions-only updates, expiry and deletes. Apply current policy and
   tombstones before serving a restored index or backup.

PostgreSQL row-level policies can enforce database read and write boundaries
with a restricted runtime role. Verify whether owners, privileged roles,
or other endpoints bypass the policy and which resources the database policy
covers. Qdrant tenant payloads and Graphiti namespaces provide routing and
partitioning. Bind them to application authority. Onyx and Azure provide
examples of indexed document ACLs with connector-dependent freshness. Read
the [research log](research-log.md) for specific limitations and versions.
