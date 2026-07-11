# Source index and maintenance contract

Research and verification date: 2026-07-11

## Primary sources

### Kubernetes core

- https://kubernetes.io/docs/
- https://kubernetes.io/releases/
- https://kubernetes.io/docs/setup/release/version-skew-policy/
- https://kubernetes.io/docs/reference/using-api/api-concepts/
- https://kubernetes.io/docs/reference/using-api/deprecation-policy/
- https://kubernetes.io/docs/reference/using-api/deprecation-guide/
- https://kubernetes.io/docs/reference/kubectl/
- https://kubernetes.io/docs/concepts/workloads/
- https://kubernetes.io/docs/concepts/scheduling-eviction/
- https://kubernetes.io/docs/concepts/storage/
- https://kubernetes.io/docs/concepts/services-networking/
- https://kubernetes.io/docs/concepts/security/
- https://kubernetes.io/docs/tasks/debug/
- https://kubernetes.io/docs/tasks/administer-cluster/

### Distribution and provider overlays

- https://docs.k3s.io/
- https://docs.rke2.io/
- https://microk8s.io/docs
- https://docs.k0sproject.io/stable/
- https://docs.talos.dev/
- https://docs.openshift.com/container-platform/latest/
- https://docs.okd.io/latest/
- https://docs.rancher.com/rancher/
- https://kind.sigs.k8s.io/
- https://minikube.sigs.k8s.io/docs/
- https://docs.aws.amazon.com/eks/latest/userguide/
- https://learn.microsoft.com/en-us/azure/aks/
- https://cloud.google.com/kubernetes-engine/docs/

### Ecosystem overlays

- https://gateway-api.sigs.k8s.io/docs/
- https://helm.sh/docs/
- https://velero.io/docs/latest/
- https://open-policy-agent.github.io/gatekeeper/website/docs/
- https://kyverno.io/docs/
- https://docs.sigstore.dev/cosign/overview/

## Verified release observations

| Product | Observation | Verification |
|---|---|---|
| Kubernetes | 1.36, 1.35, 1.34 maintained branches | Official release page scrape |
| k3s | `v1.36.2+k3s1` | GitHub release API, 2026-07-11 |
| RKE2 | `v1.36.2+rke2r1` | GitHub release API, 2026-07-11 |
| k0s | `v1.36.2+k0s.0` | GitHub release API, 2026-07-11 |
| Talos | `v1.13.6` | GitHub release API, 2026-07-11 |
| kind | `v0.32.0` | GitHub release API, 2026-07-11 |
| Minikube | `v1.38.1` | GitHub release API, 2026-07-11 |

## Refresh procedure

1. Run `scripts/refresh-version-matrix.sh`.
2. Re-scrape the official Kubernetes release, version-skew, deprecation, distribution, and provider pages.
3. Compare release values, defaults, feature-state labels, and upgrade instructions against this reference.
4. Record discrepancies in the project’s research reconciliation log before editing guidance.
5. Do not update a version number without its source URL, retrieval date, and support interpretation.
6. Re-run the CLI tests, skill validator, and any available disposable-cluster integration tests.

The skill intentionally excludes unsupported or unverified alpha-feature instructions from executable command guidance. A source can be listed for future research without becoming an operational recommendation.
