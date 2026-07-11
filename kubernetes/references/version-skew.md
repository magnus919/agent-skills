# Version skew and freshness

## Kubernetes baseline

The official release page checked 2026-07-11 reported maintained minor branches 1.36, 1.35, and 1.34, with approximately one year of patch support for 1.19 and newer. Recheck the page before making a support claim.

## Compatibility checks

Compare client, API server, kubelet, controller, node image, CRD, operator, webhook, CNI, CSI, and provider versions. Kubernetes version skew rules differ by component and release. The API server is authoritative for served APIs; provider support windows can be narrower or differently shaped than upstream support.

## Upgrade evidence

Before upgrade: deprecated API metrics/warnings, CRD served/storage versions, webhook compatibility, PDBs, capacity, backups, and provider/distribution procedure. After upgrade: discovery, nodes, system workloads, controllers, representative workloads, storage, routes, metrics, and alerts.

## Sources

- https://kubernetes.io/releases/
- https://kubernetes.io/docs/setup/release/version-skew-policy/
- https://kubernetes.io/docs/reference/using-api/deprecation-policy/
- https://kubernetes.io/docs/reference/using-api/deprecation-guide/
