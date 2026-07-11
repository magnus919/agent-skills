# Kubernetes upgrade runbook

## Scope

- Cluster/provider:
- Distribution:
- Current server version:
- Target version:
- Context:
- Maintenance window:
- Owner and approver:

## Preflight

- [ ] Current official support/version-skew policy checked
- [ ] Deprecated API usage checked
- [ ] CRDs/operators/webhooks checked for compatibility
- [ ] PDBs, capacity, quotas, and node health checked
- [ ] Backup completed and restore tested or explicitly accepted as a risk
- [ ] Provider/distribution-specific procedure selected
- [ ] Rollback or restore path documented

## Change

Record exact commands, target, operator, start/end time, and output location. Do not paste credentials or Secret values.

## Verification

- [ ] API server/version/discovery
- [ ] Nodes and system workloads
- [ ] CRDs/operators/controllers
- [ ] Representative stateless workloads
- [ ] Stateful workloads and PVCs
- [ ] Services, routes, DNS, and external endpoint
- [ ] Metrics, logs, audit, and alerts

## Sources

-
