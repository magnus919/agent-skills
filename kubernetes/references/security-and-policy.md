# Security, identity, and policy

## Access

RBAC permissions are additive. Role is namespaced; ClusterRole is cluster-scoped but can be bound into a namespace. Prefer the narrowest subject, namespace, resource, and verb set. Check effective authorization before changing bindings:

```sh
kubectl auth can-i VERB RESOURCE --namespace NAMESPACE
kubectl auth can-i --list --namespace NAMESPACE
kubectl get role,rolebinding -n NAMESPACE
kubectl get clusterrole,clusterrolebinding
```

Never print `kubeconfig --raw`, token fields, or Secret data. Redact object output before sharing.

## Pod security

Pod Security Standards define Privileged, Baseline, and Restricted profiles. Namespace labels and admission behavior are version-sensitive. Before changing enforcement, audit existing workloads and test in warn/audit modes where supported.

## Admission and encryption

Admission webhooks can block or mutate every matching API request. Enumerate webhook configurations, inspect failure policies/timeouts, and consider built-in CEL admission for simple validation. Encryption at rest is not automatic merely because Secrets exist; inspect the control-plane/provider configuration.

## Network and workload identity

NetworkPolicy requires an enforcing plugin. Managed providers add identity layers: EKS IRSA/Pod Identity, AKS Workload ID/OIDC/Azure RBAC, and GKE Workload Identity Federation. These are not portable Kubernetes instructions.

## Privilege-escalation checks

Treat these permissions as high risk during RBAC review: `escalate`, `bind`, `impersonate`, `nodes/proxy`, `serviceaccounts/token`, CSR approval, admission webhook configuration, and broad access to Secrets. `list` and `watch` on Secrets can expose their contents. Creating workloads can indirectly grant access to mounted Secrets and service-account credentials. Review `system:masters` separately because it bypasses ordinary RBAC rules.

```sh
kubectl auth can-i --list --as=system:serviceaccount:NAMESPACE:SERVICE_ACCOUNT -n NAMESPACE
kubectl get clusterrolebindings -o json
kubectl auth reconcile -f rbac.yaml --dry-run=client
```

Never broaden a RoleBinding merely to make a failing workload work. Identify the denied verb/resource, grant the smallest namespace-scoped permission, and verify with `auth can-i`.

## PSA rollout

Pod Security Admission is namespace-label driven. A safer migration is `warn` and `audit` first, then `enforce` after violations are remediated. Pin the profile version only after checking the target cluster’s supported profile version.

```yaml
pod-security.kubernetes.io/warn: restricted
pod-security.kubernetes.io/audit: restricted
# Add enforce only after reviewing violations.
```

## Secrets and image supply chain

Kubernetes Secrets are API objects, not a complete secrets-management or encryption-at-rest strategy. Secret values are base64-encoded, not encrypted, unless encryption at rest is configured. Avoid putting secret values in manifests, shell history, logs, or agent output. Restrict `get`, `list`, and `watch` access, disable automatic service-account token mounting when a workload does not need the API, and use short-lived workload identity where the provider supports it. External Secret Store CSI providers and admission/image-signature policy are ecosystem overlays that require separate validation. Verify image digest, registry trust, architecture, pull credentials, and admission policy separately.

## Sources

- https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- https://kubernetes.io/docs/concepts/security/pod-security-standards/
- https://kubernetes.io/docs/concepts/security/pod-security-admission/
- https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/
- https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/
- https://kubernetes.io/docs/concepts/security/rbac-good-practices/
- https://kubernetes.io/docs/concepts/security/secrets-good-practices/
- https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html
- https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview
- https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity
