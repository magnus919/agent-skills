# Workloads and rollouts

## Workload selection

- Deployment: stateless replicated applications and rolling updates.
- StatefulSet: stable identity and persistent storage; inspect ordinal identity, PVCs, and update strategy.
- DaemonSet: one or more Pods per eligible Node; inspect taints, selectors, and update strategy.
- Job: run-to-completion; inspect completions, parallelism, backoff, deadline, and TTL.
- CronJob: scheduled Jobs; inspect schedule, concurrency policy, deadlines, and history limits.

Use the highest-level controller that expresses the intent. Do not hand-edit ReplicaSets or controller-owned Pods unless debugging demands it.

## Evidence collection

```sh
kubectl get deploy,sts,ds,job,cronjob -A -o wide
kubectl describe deployment NAME -n NAMESPACE
kubectl get pods -n NAMESPACE -l app=NAME -o wide
kubectl get events -n NAMESPACE --sort-by=.lastTimestamp
kubectl rollout status deployment/NAME -n NAMESPACE --timeout=120s
```

`Running` means the Pod has been scheduled and containers are running. Readiness controls endpoint membership; liveness controls restart behavior; startup probes protect slow-starting applications. A rollout is not healthy until its conditions, Pods, events, and relevant endpoint agree.

## Safe rollout pattern

1. Render or inspect the intended change.
2. Run `kubectl diff` and `kubectl apply --dry-run=server`.
3. Apply with an explicit field manager.
4. Wait for rollout and inspect conditions/events.
5. Verify Service/EndpointSlice or Gateway/HTTP response as appropriate.
6. Roll back only after recording the failed revision and evidence.

## Sources

- https://kubernetes.io/docs/concepts/workloads/
- https://kubernetes.io/docs/concepts/workloads/pods/probes/
- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
- https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/
- https://kubernetes.io/docs/concepts/workloads/controllers/job/
- https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/
