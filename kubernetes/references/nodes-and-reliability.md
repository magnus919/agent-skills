# Nodes, disruption, and reliability

## Node maintenance

```sh
kubectl get nodes -o wide
kubectl describe node NODE
kubectl cordon NODE
kubectl drain NODE --ignore-daemonsets --delete-emptydir-data --grace-period=60 --timeout=10m
kubectl uncordon NODE
```

Cordon prevents new scheduling; drain evicts workloads and is constrained by PodDisruptionBudgets. Review PDBs, daemonsets, local storage, topology, capacity, and workload replicas before draining. Verify the node is empty or only has intentionally retained Pods, then verify replacement workloads and external availability. Do not add `--force`, bypass PDBs, or remove finalizers by default.

## Pressure and conditions

Inspect `Ready`, memory/disk/PID pressure, taints, allocatable capacity, kubelet/runtime evidence, and provider node events. Kubelet eviction and API-initiated eviction are different paths. Resource pressure may be a node symptom of workload requests, image garbage collection, filesystem, or runtime failure.

## PDBs

Use `policy/v1` with one of `minAvailable` or `maxUnavailable`, a selector matching the intended workload, and an explicit disruption expectation. A PDB is not a guarantee against involuntary failure and can block maintenance if replicas or selectors are wrong.

## Sources

- https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/
- https://kubernetes.io/docs/tasks/administer-cluster/out-of-resource/
- https://kubernetes.io/docs/concepts/scheduling-eviction/pod-disruption-budgets/
- https://kubernetes.io/docs/concepts/architecture/nodes/
