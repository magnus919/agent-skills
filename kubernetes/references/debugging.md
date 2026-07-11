# Advanced debugging

## Ephemeral containers

Use `kubectl debug` when a running Pod needs inspection without restarting the application. Select an appropriate debug profile, target a container only when necessary, and treat the resulting shell/output as potentially sensitive.

```sh
kubectl debug pod/NAME -n NAMESPACE -it --image=busybox:1.36 --target=CONTAINER
kubectl debug pod/NAME -n NAMESPACE --copy-to=NAME-debug --share-processes --image=busybox:1.36
```

Do not add privileged capabilities, host namespaces, or host mounts as a reflex. Explain why the chosen profile requires them.

## Must-gather pattern

Collect context/version, readiness, nodes, system workloads, CRDs, events, resource conditions, selected logs, policy objects, and provider/distribution markers. Bound every collection, omit Secrets and raw kubeconfig, and write a manifest of commands and timestamps.

## Sources

- https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/
- https://kubernetes.io/docs/tasks/debug/debug-cluster/
- https://kubernetes.io/docs/reference/kubectl/
