# Tenancy and Data Partitioning Models

Choose an isolation shape per resource. A product can pool application compute, bridge selected data or compute, and silo high-sensitivity or high-demand resources at the same time.

| Shape | Strength | Cost or risk to test |
|---|---|---|
| Pooled | Efficient utilization and simple fleet-wide change | Strong tenant context, query scoping, fairness, and restore targeting are required |
| Bridge | Shared control or compute with selected dedicated resources | Placement rules and cross-resource consistency become more complex |
| Silo | Clear blast-radius and performance boundary | Provisioning, upgrades, idle cost, and fleet variation increase |
| Hybrid | Matches different tiers, regions, or resource classes | Policy drift and migration paths need explicit governance |

Evaluate each resource class separately: primary records, object storage, cache, queue, search index, analytics copy, encryption keys, backups, and runtime capacity. For each, record tenant boundary, authoritative identifier, access path, failure blast radius, operational owner, cost attribution, and migration trigger.

## Decision pressures

Use actual promises and evidence: regulatory or contractual isolation, tenant data volume, peak skew, region/residency, recovery scope, support model, deployment cadence, team capability, and unit economics. Do not claim that a silo is automatically safer or that pooling is automatically cheaper. Both require controls and evidence.

Security threat modeling and enforcement belong to `secure-software-engineering`; data storage architecture and schema choices belong to `data-architect`; moving a tenant between shapes belongs to `migration-engineering`; quantitative load and cost evidence belongs to `capacity-and-cost-engineering`.
