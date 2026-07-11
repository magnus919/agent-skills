# Observability and metrics

## Minimal health evidence

```sh
kubectl get --raw='/readyz?verbose'
kubectl get nodes
kubectl get pods -A
kubectl events -A --types=Warning
kubectl top nodes
kubectl top pods -A --sort-by=memory
```

`kubectl top` depends on the resource metrics pipeline and may be unavailable even when the API server is healthy. Distinguish missing metrics, stale metrics, and a measured zero.

## Logging

Use bounded `kubectl logs` with `--tail`, `--since`, and `--previous`. Cluster-level logging is normally implemented by a node agent, sidecar, or application-direct path. Container log rotation and runtime behavior are node/distribution concerns.

## Events and audit

Events are short-lived diagnostic evidence and should be correlated by involved object, reason, type, count, and timestamp. Audit logs answer who called the API and at which stage, but require a configured policy and backend. Keep audit policy changes separate from ordinary workload changes.

## Metrics selection

Use API-server deprecation metrics to locate deprecated API use. Use controller/node/workload metrics for health and capacity. Prometheus Operator, kube-state-metrics, and provider monitoring are ecosystem overlays; route to their official docs rather than pretending they are Kubernetes core.

## Sources

- https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/
- https://kubernetes.io/docs/concepts/cluster-administration/logging/
- https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/
- https://kubernetes.io/docs/reference/instrumentation/metrics/
