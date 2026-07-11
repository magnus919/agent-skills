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

## Sources

- https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- https://kubernetes.io/docs/concepts/security/pod-security-standards/
- https://kubernetes.io/docs/concepts/security/pod-security-admission/
- https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/
- https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/
- https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html
- https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview
- https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity
