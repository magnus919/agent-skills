# Onboarding, Identity, Entitlements, Metering, and Billing

Model the commercial path as a set of authorities and handoffs, not one synchronous signup transaction.

## Lifecycle path

1. Capture a prospective account and the intended tenant, region, plan, and owner.
2. Establish identity and membership using an agreed identity authority; record invitations, federation, and deprovisioning expectations.
3. Create tenant desired state and provision resources idempotently.
4. Publish configuration and entitlement state with effective time, version, and reason.
5. Serve requests using server-derived tenant context and an entitlement decision appropriate to the operation.
6. Emit usage facts with a stable tenant, subject, meter, event time, quantity, and deduplication identity.
7. Hand usage to the billing authority for rating, invoicing, payment state, credits, disputes, and tax treatment.
8. Propagate payment or contract state back to entitlements and support workflows with explicit grace and suspension behavior.

## Questions that prevent hidden policy

- Is the plan change effective immediately, at renewal, or after provisioning succeeds?
- What happens if usage arrives late, twice, or after a tenant is suspended?
- Which system is authoritative when entitlement and billing disagree?
- Can support grant a temporary override, who approves it, and when does it expire?
- Are quotas product promises, operational protections, or both?

Keep pricing, ARR, churn, margin, and forecast outcomes with `financial-modeling`. Keep contract schemas and webhook compatibility with `api-design-and-evolution`; keep identity and authorization controls with `secure-software-engineering`; keep service implementation with `backend-engineering`.
