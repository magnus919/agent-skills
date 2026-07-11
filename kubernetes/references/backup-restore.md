# Backup and restore

## Choose the state to protect

- API/resource state: etcd or the distribution datastore.
- Persistent volume data: CSI snapshots, provider snapshots, application backup, or Velero.
- Cluster identity/configuration: PKI, kubeconfigs, distribution config, manifests, provider resources.
- Observability/policy configuration: audit policy, admission/webhook configuration, monitoring rules.

A YAML export is not an etcd backup. An etcd snapshot is not an application-consistent PV backup.

## Preflight

1. Identify the distribution and datastore.
2. Capture version and snapshot compatibility.
3. Check datastore health, quorum, disk space, and encryption/key custody.
4. Create a backup with a timestamp and retention policy.
5. Verify metadata/checksum and test restore in a disposable environment.

## Distribution boundary

Use the current official procedure for `kubeadm`/etcd, k3s `etcd-snapshot`, RKE2 backup/restore, k0s backup, Talos `talosctl`, or managed-provider backup. Do not improvise a control-plane restore command from a blog post. The exact k3s/k0s restore syntax remains version-sensitive and must be refreshed before execution.

## Velero and CSI

Velero and CSI VolumeSnapshots are ecosystem components, not built-in guarantees. Confirm plugin/provider support, credentials, snapshot class, namespace/resource filters, PV data mode, and restore hooks. Test an actual restore, including application readiness and external dependencies.

## Sources

- https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/
- https://kubernetes.io/docs/concepts/storage/volume-snapshots/
- https://velero.io/docs/latest/
- https://docs.k3s.io/backup-restore
- https://docs.rke2.io/backup_restore/
- https://docs.k0sproject.io/stable/backup/
- https://docs.talos.dev/
