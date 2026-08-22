# Tenant Domain Model and Boundaries

Start with meanings, not tables. A tenant is the customer boundary whose data, policy, usage, and service promise are managed together. It may be an organization, account, workspace, or another domain object, but the chosen term must be stable and user-visible.

## Minimum vocabulary

| Concept | Decide explicitly |
|---|---|
| Tenant | What customer boundary owns data, configuration, usage, and support history? |
| Account or organization | Is this the commercial payer, the operating group, or both? Can one payer own several tenants? |
| User | Is identity global, tenant-scoped, or federated? Can one user belong to many tenants? |
| Membership | Which tenant-local role and status govern a user's actions? |
| Subscription | What commercial agreement is attached to which account or tenant, for what period and status? |
| Entitlement | Which product capability, limit, region, or support promise is granted, and who may change it? |
| Resource | Which objects are tenant-owned, shared, or platform-owned? |
| Environment | Does a tenant have production, test, or regional environments with separate lifecycle and data rules? |

For each concept record: authoritative owner, identifier, cardinality, state machine, audit requirement, deletion relationship, and cross-tenant visibility rule. A shared identity provider does not make application authorization global; application membership still needs an authoritative decision.

## Boundary tests

- A request can resolve one tenant context before accessing tenant-owned resources.
- A support operator has a separate, reviewable path from ordinary membership.
- A subscription change has one authority and an observable propagation path to entitlements.
- A tenant suspension, export, restore, and deletion operation names every dependent store and derived artifact.
- A tenant move between partitions preserves identity, ownership, and billing references without silently changing the customer promise.

Keep storage schema and API contract mechanics with `data-architect` and `api-design-and-evolution`; keep authorization and isolation controls with `secure-software-engineering`.
