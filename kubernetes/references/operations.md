# Reliability, upgrades, backup, and observability

## Inventory before change

Record distribution/provider, control-plane and node versions, contexts, API resources, CRDs, CNI/CSI, admission, system workloads, nodes, quotas, and representative application health. Use the inventory template and redact credentials.

## Upgrade pattern

1. Confirm support window and version skew from current official docs.
2. Scan deprecated API usage and operator/webhook compatibility.
3. Verify backups and restore procedure, not only backup creation.
4. Check PDBs, capacity, quotas, maintenance windows, and external dependencies.
5. Upgrade according to the distribution/provider overlay, never generic Kubernetes memory.
6. Verify API discovery, nodes, system workloads, controllers, representative workloads, storage, routes, and observability.

Upgrades are not reversible by default. A provider may roll back infrastructure while a self-managed distribution may require restore or re-provisioning.

## Backups

Back up the actual stateful substrate: etcd or the distribution's datastore, PKI/configuration, manifests, persistent data, and provider resources. Test restoration into a disposable environment. An etcd snapshot alone is not automatically an application-consistent backup.

## Observability

Collect API audit, events, control-plane/component logs where accessible, node conditions, workload logs, metrics, HPA signals, and provider control-plane events. Distinguish “metrics unavailable” from “metric is zero.”

## Sources

- https://kubernetes.io/docs/tasks/administer-cluster/cluster-management/
- https://kubernetes.io/docs/setup/release/version-skew-policy/
- https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/
- https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/
- https://docs.k3s.io/backup-restore
- https://docs.rke2.io/backup_restore/
- https://docs.aws.amazon.com/eks/latest/userguide/update-cluster.html
- https://learn.microsoft.com/en-us/azure/aks/upgrade-aks-cluster
- https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-upgrades
