# Native CLI reference

## Context and discovery

The bundled wrapper places global options before the subcommand:

```sh
scripts/k8s-cli --json get pods --namespace default
```

Native examples:

```sh
kubectl config get-contexts
kubectl config current-context
kubectl version -o json
kubectl api-resources -o wide
kubectl api-versions
kubectl get nodes -o wide
kubectl get --raw='/readyz?verbose'
```

## Bounded inspection

```sh
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.lastTimestamp
kubectl logs POD -n NS --all-containers --tail=200 --since=1h
kubectl describe pod POD -n NS
```

Always add an explicit namespace, context, selector, tail, since, or timeout where the operation allows it.

## Validation and mutation

```sh
kubectl diff -f manifest.yaml
kubectl apply --server-side --field-manager=agent-kubernetes --dry-run=server -f manifest.yaml
kubectl apply --server-side --field-manager=agent-kubernetes -f manifest.yaml
kubectl delete -f manifest.yaml --dry-run=server
kubectl rollout status deployment/NAME -n NS --timeout=120s
kubectl wait --for=condition=available deployment/NAME -n NS --timeout=120s
```

## Output safety

Prefer `-o json` for machine parsing. Use `-o name`, `-o wide`, JSONPath, or custom columns for bounded views. Never use `kubectl config view --raw`, `get secret -o yaml`, or unbounded `logs -f` in chat output.

## Sources

- https://kubernetes.io/docs/reference/kubectl/
- https://kubernetes.io/docs/reference/kubectl/quick-reference/
- https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/
