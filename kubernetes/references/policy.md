# Policy selection

Choose the smallest policy mechanism that satisfies the requirement:

| Need | Prefer | Boundary |
|---|---|---|
| Basic Pod hardening | Pod Security Admission | Namespace labels and workload compatibility |
| Quotas/defaults | ResourceQuota, LimitRange, built-in admission | Namespace/resource scope |
| Simple declarative validation/mutation | ValidatingAdmissionPolicy / MutatingAdmissionPolicy with CEL | Check target version and parameter support |
| Rego-based enterprise policy and audit | Gatekeeper | Install and maintain CRDs/webhooks; provider-specific |
| YAML-native validate/mutate/generate/verify | Kyverno | Install and maintain policy reports/webhooks |
| Image provenance/signatures | Sigstore/cosign plus an admission integration | Registry, identity, and key policy |

Policy is additive and can conflict operationally. Inventory existing policies, webhooks, failure policies, and exemptions before adding another enforcement layer. Test in audit/warn mode where supported and verify rejected objects plus user-facing diagnostics.

## Sources

- https://kubernetes.io/docs/concepts/security/pod-security-admission/
- https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/
- https://open-policy-agent.github.io/gatekeeper/website/docs/
- https://kyverno.io/docs/
- https://docs.sigstore.dev/cosign/overview/
