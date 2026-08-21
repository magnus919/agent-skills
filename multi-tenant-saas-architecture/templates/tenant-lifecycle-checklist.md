# Tenant Lifecycle Checklist

Use one row per tenant state transition. Mark unknowns instead of assuming success.

| Stage | Authority and input | Idempotency key | User-visible state | Failure/retry path | Evidence and owner | Done |
|---|---|---|---|---|---|---|
| Prospect/account accepted | | | | | | |
| Identity and membership established | | | | | | |
| Tenant desired state created | | | | | | |
| Resources provisioned | | | | | | |
| Configuration and entitlements active | | | | | | |
| Usage metering active | | | | | | |
| Billing handoff verified | | | | | | |
| Suspension or grace period | | | | | | |
| Export or deletion requested | | | | | | |
| Data purged and evidence retained | | | | | | |
| Restore or reactivation | | | | | | |

## Boundary checks

- [ ] Tenant context is derived and validated at each application access path; route control verification to `secure-software-engineering`.
- [ ] API and event contracts have an owner and compatibility policy; route contract work to `api-design-and-evolution`.
- [ ] Data, replicas, backups, caches, indexes, logs, and derived data are named; route implementation to `data-architect`, `data-engineering`, and `privacy-engineering` as applicable.
- [ ] Placement moves have a migration owner and recovery classification.
- [ ] Hot-tenant and noisy-neighbor behavior has measured capacity evidence.
- [ ] Pricing, invoice, churn, and margin claims have a financial-modeling owner.
