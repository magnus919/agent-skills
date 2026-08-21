# Coupling, Modularity, And Data Ownership

Assess a candidate boundary across several coupling surfaces:

- **Policy coupling:** one invariant requires coordinated changes;
- **data coupling:** components share tables, records, keys, or write authority;
- **temporal coupling:** one step must be available or ordered before another;
- **runtime coupling:** latency, availability, or resource pressure propagates;
- **deployment coupling:** changes must ship together;
- **organizational coupling:** ownership, incentives, or skills require coordination.

High coupling is not automatically bad. Shared coupling can be cheaper inside one process when the invariant is strong and the team is one owner. The question is whether the proposed boundary reduces the costly coupling without creating a worse failure or coordination surface.

## Modularity checks

Inspect change history, dependency direction, call paths, data access, transaction scope, and operational ownership when evidence exists. For a greenfield design, mark these as hypotheses and define a probe. Prefer a cohesive module with a narrow interface over a distributed component whose interface exposes internal data or transaction assumptions.

## Data authority

For each important fact, identify the authoritative writer, derived views, caches, replicas, audit history, and deletion authority. State who may mutate it, what an accepted write means, and how conflicting updates are resolved. Data platform and data-model decisions belong to `data-architect`; architecture owns the cross-boundary ownership decision.

## Decomposition decision

Recommend a modular monolith or staged boundary when ownership is unclear, transactions span the candidate, consumers bypass an interface, load is not independently shaped, or recovery cannot be tested. Recommend separate deployment only when the benefit is concrete and the team can own the new operational surface. Hand an approved transition to `migration-engineering`.
