# Evidence-first troubleshooting

## Universal loop

1. State the symptom and boundary: API, object admission, scheduling, startup, readiness, service, external route, storage, node, or control plane.
2. Capture context, versions, namespace, labels, owner references, conditions, events, and recent changes.
3. Form competing hypotheses.
4. Run the least invasive discriminating check.
5. Change one layer at a time.
6. Verify both Kubernetes state and the user-visible boundary.
7. Preserve a bounded report with commands, timestamps, exit codes, and redacted output.

## Common symptoms

- `ImagePullBackOff`: inspect Events, image name/tag, registry auth, node egress, architecture, and image policy.
- `CrashLoopBackOff`: inspect previous logs, termination reason, probes, config/Secret mounts, limits, and recent rollout.
- `Pending`: follow scheduling/resource/taint/quota evidence; do not simply increase replicas or delete Pods.
- `Running` but unavailable: inspect readiness, Service selectors, EndpointSlices, DNS, NetworkPolicy, route/controller status, and external load balancer.
- `Terminating`: inspect finalizers, owner/controller health, admission/webhook behavior, and whether the resource is still in use. Removing finalizers is destructive and requires explicit justification.
- Upgrade blocked: inspect deprecated API use, PDBs, webhooks, node readiness, quotas, provider/distribution upgrade rules, and version skew.

## Output discipline

Use `-o json` or `-o jsonpath` for machine parsing. Bound events and logs by namespace, selector, tail lines, and time. Never present an aggregator, cached page, or intermediate tool result as proof that a live endpoint is healthy.

## Sources

- https://kubernetes.io/docs/tasks/debug/debug-cluster/
- https://kubernetes.io/docs/tasks/debug/debug-application/
- https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/
- https://kubernetes.io/docs/concepts/cluster-administration/logging/
- https://kubernetes.io/docs/concepts/cluster-administration/system-logs/
