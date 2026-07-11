---
name: kubernetes
description: >-
  Operate, troubleshoot, secure, upgrade, and automate Kubernetes clusters and workloads safely across upstream Kubernetes, k3s, RKE2, MicroK8s, k0s, Talos, OpenShift/OKD, kind, Minikube, Rancher-managed clusters, EKS, AKS, and GKE. Use when a task involves kubectl, Kubernetes APIs, Pods, Deployments, StatefulSets, Services, Ingress or Gateway API, CRDs, RBAC, NetworkPolicy, storage, scheduling, autoscaling, cluster lifecycle, or the bundled agent-first k8s-cli.
---

# Kubernetes

Use this skill as a decision and routing layer. Do not treat it as a static kubectl cheat sheet.

## Operating contract

1. Identify the target: distribution, provider, cluster version, client version, context, namespace, access mode, and whether the cluster is production.
2. Discover before assuming: query served API resources, API versions, CRDs, system workloads, nodes, and distribution markers.
3. Separate portable Kubernetes behavior from distribution/provider overlays. Load the matching reference before using lifecycle, networking, identity, storage, or upgrade instructions.
4. For mutations, preview first (`k8s-cli ... --dry-run` or `kubectl diff` / server dry-run), state scope, require explicit confirmation for destructive actions, then verify conditions, events, rollout, and the external boundary.
5. Prefer stable APIs and server-side validation. Treat beta/alpha APIs, feature gates, provider defaults, and version numbers as time-sensitive.
6. Keep evidence bounded and structured. Never dump kubeconfigs, Secret values, tokens, or unbounded logs into chat.

## Choose the operating path

| Situation | First move | Do not do |
|---|---|---|
| Live cluster operation | Run `doctor`, `context`, and `discover`; record context, namespace, distribution, and versions | Do not infer cluster state from configuration or a prior command |
| No cluster access | Produce a bounded plan and name the missing prerequisite | Do not claim a diagnosis, success, or invented command output |
| Any mutation | Render, diff/server-dry-run, state scope, obtain the required confirmation, then mutate and verify the relevant boundary | Do not treat command exit 0 as operational success |
| Provider or distribution present | Load the matching overlay before applying portable guidance | Do not apply upstream instructions unchanged |

## First-response discovery

```sh
scripts/k8s-cli --json doctor
scripts/k8s-cli --json context
scripts/k8s-cli --json discover
```

If the wrapper is unavailable, use the equivalent native commands from `references/cli-reference.md`. If `kubectl` is absent, stop and report the prerequisite rather than inventing cluster state.

## Routing

| Scenario | Load |
|---|---|
| API discovery, SSA, CRDs, or deprecations | `references/api-and-versioning.md` |
| Workloads, probes, rollouts, jobs, or controllers | `references/workloads-and-rollouts.md` |
| Scheduling, scaling, storage, node disruption, or reliability | `references/scheduling-scaling-storage.md` and `references/nodes-and-reliability.md` |
| Services, DNS, NetworkPolicy, Ingress, or Gateway API | `references/networking.md` |
| RBAC, Pod Security, admission, audit, secrets, or policy engines | `references/security-and-policy.md` and `references/policy.md` |
| Evidence-first diagnosis or advanced debugging | `references/troubleshooting.md` and `references/debugging.md` |
| Backups, upgrades, HA, or observability | `references/operations.md`, `references/backup-restore.md`, and `references/observability.md` |
| Distribution/provider overlays or version matrix | `references/distributions.md`, `references/version-skew.md`, and `references/source-index.md` |
| Native command details or output contracts | `references/cli-reference.md` |
| Mutation safety gates | `references/safety-gates.md` |

## Templates and scripts

- `templates/diagnostic-report.md`: human-readable incident report
- `templates/cluster-inventory.json`: bounded inventory schema
- `templates/upgrade-runbook.md`: preflight, change, and verification runbook
- `scripts/k8s-cli`: agent-first wrapper around kubectl
- `scripts/test-k8s-cli.sh`: deterministic tests using a fake kubectl
- `scripts/gather-cluster-state.sh`: bounded diagnostic collection for incident reports
- `scripts/verify-cluster-health.sh`: bounded post-operation health verification
- `scripts/refresh-version-matrix.sh`: refreshes dated release observations, never silently edits guidance

## Version policy

The research baseline was checked 2026-07-11. The Kubernetes project page reported maintained minors 1.36, 1.35, and 1.34. This is not a permanent claim. Refresh `references/distributions.md` and the source index before asserting current versions or support status.

## Verification boundary

| Claim | Minimum evidence |
|---|---|
| Pod is healthy | Pod conditions, readiness, events, and relevant EndpointSlice or external boundary |
| Rollout succeeded | Controller conditions, resulting Pods, events, and the relevant Service or external check |
| API/resource is available | Served API discovery, installed CRDs/controller support, and server-side validation |
| Command succeeded operationally | Bounded command result plus the resource condition and user-visible boundary |

A component-level command result is evidence about that component only; do not promote it to a cluster or integration claim.

## Hard boundaries

- Never expose Secret data or raw kubeconfig credentials.
- Never use `--force-conflicts`, `delete`, `drain`, `patch`, `upgrade`, or cluster-reset procedures without explaining scope and obtaining the required confirmation.
- Never call a Pod `healthy` from `Running` alone.
- Never call an integration successful from a component-level test alone.
- Never apply an upstream procedure to k3s, RKE2, a managed provider, Talos, or OpenShift without loading its overlay.
