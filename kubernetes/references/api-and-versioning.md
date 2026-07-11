# API, discovery, and versioning

## Discovery first

Use the target API server as the authority:

```sh
kubectl version -o json
kubectl api-resources -o wide
kubectl api-versions
kubectl explain deployment.spec --recursive
kubectl get crd
```

Do not infer that an API exists because a YAML example exists. Validate with `api-resources`, `api-versions`, `explain`, and server-side dry-run.

## Resource and scope rules

Every request has a group/version/resource, and resources are either namespaced or cluster-scoped. Subresources such as `status`, `scale`, `logs`, `exec`, and `portforward` have distinct behavior. Discover the resource and scope before constructing a URL or command.

## Server-side apply

Server-side apply is stable and tracks field ownership. Use an explicit field manager. A conflict is a coordination signal, not permission to force overwrite. Resolve by inspecting `metadata.managedFields`, changing intent, or obtaining explicit approval for `--force-conflicts`.

```sh
kubectl apply --server-side --field-manager=agent-kubernetes -f manifest.yaml --dry-run=server
kubectl diff -f manifest.yaml
kubectl apply --server-side --field-manager=agent-kubernetes -f manifest.yaml
```

## Deprecation

GA, beta, and alpha APIs have different stability guarantees. Detect deprecated API use from API warnings, audit annotations, metrics such as `apiserver_requested_deprecated_apis`, and release/deprecation guides. Never use `v1beta1` because it appears in an old tutorial.

## CRDs and operators

Separate these checks:

1. CRD is registered and served.
2. Custom object passes schema/admission.
3. Controller/operator is installed.
4. Controller is healthy and reconciling.
5. Object conditions represent the desired state.

A CRD object can be accepted while no controller exists to act on it. Check controller logs, events, owner references, conditions, and served versions.

## Current feature-state discipline

The 2026-07-11 research pass found version-sensitive features including streaming lists (1.34 beta), Pod-level resource specification (1.34 beta), and newer alpha APIs. Do not operationalize an alpha/beta feature without checking the target server's feature gates and the current official page.

## Sources

- https://kubernetes.io/docs/reference/using-api/api-concepts/
- https://kubernetes.io/docs/reference/using-api/server-side-apply/
- https://kubernetes.io/docs/reference/using-api/deprecation-policy/
- https://kubernetes.io/docs/reference/using-api/deprecation-guide/
- https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/
- https://kubernetes.io/releases/
