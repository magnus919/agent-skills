# Control Plane and Application Plane

Use the planes as responsibility lenses, not mandatory deployment units.

## Control plane

The control plane owns tenant-facing and operator-facing policy and lifecycle decisions: registration, tenant records, identity federation configuration, plan and entitlement state, provisioning intent, placement, configuration, suspension, export/deletion requests, and administrative audit. It should be authoritative for desired state and expose operation status rather than pretending provisioning is instantaneous.

## Application plane

The application plane serves tenant work: request admission, tenant context propagation, business workflows, tenant data access, usage events, and user-visible results. It should consume versioned control-plane state with an explicit freshness and failure policy. It must not infer entitlements from a client claim or silently bypass a missing control-plane decision.

## Handoff record

For every cross-plane flow, name:

- command or event and its authority;
- state transition and idempotency key;
- propagation delay and stale-state behavior;
- retry, duplicate, timeout, and reconciliation behavior;
- customer-visible status and support action;
- audit evidence and owner.

Examples include tenant creation followed by resource provisioning, plan change followed by entitlement update, suspension followed by request denial, and deletion followed by tombstone or purge confirmation.

Do not turn this guide into an API contract or deployment runbook. Route interface details to `api-design-and-evolution` and substrate implementation to `platform-engineering`.
