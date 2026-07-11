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

## First-response discovery

```sh
scripts/k8s-cli --json doctor
scripts/k8s-cli --json context
scripts/k8s-cli --json discover
```

If the wrapper is unavailable, use the equivalent native commands from `references/cli-reference.md`. If `kubectl` is absent, stop and report the prerequisite rather than inventing cluster state.

## Routing

- API, discovery, SSA, CRDs, deprecations: `references/api-and-versioning.md`
- Workloads, probes, rollout, jobs, controllers: `references/workloads-and-rollouts.md`
- Scheduling, scaling, storage, node disruption, reliability: `references/scheduling-scaling-storage.md`, `references/nodes-and-reliability.md`
- Services, DNS, NetworkPolicy, Ingress, Gateway API: `references/networking.md`
- RBAC, Pod Security, admission, audit, secrets, policy engines: `references/security-and-policy.md`, `references/policy.md`
- Evidence-first diagnosis and advanced debugging: `references/troubleshooting.md`, `references/debugging.md`
- Backups, upgrades, HA, observability, reliability: `references/operations.md`, `references/backup-restore.md`, `references/observability.md`
- Distribution/provider overlays and version matrix: `references/distributions.md`, `references/version-skew.md`, `references/source-index.md`
- Native command details and output contracts: `references/cli-reference.md`
- Safety gates for mutations: `references/safety-gates.md`

## Templates and scripts

- `templates/diagnostic-report.md`: human-readable incident report
- `templates/cluster-inventory.json`: bounded inventory schema
- `templates/upgrade-runbook.md`: preflight, change, and verification runbook
- `scripts/k8s-cli`: agent-first wrapper around kubectl
- `scripts/test-k8s-cli.sh`: deterministic tests using a fake kubectl
- `scripts/refresh-version-matrix.sh`: refreshes dated release observations, never silently edits guidance

## Version policy

The research baseline was checked 2026-07-11. The Kubernetes project page reported maintained minors 1.36, 1.35, and 1.34. This is not a permanent claim. Refresh `references/distributions.md` and the source index before asserting current versions or support status.

## Hard boundaries

- Never expose Secret data or raw kubeconfig credentials.
- Never use `--force-conflicts`, `delete`, `drain`, `patch`, `upgrade`, or cluster-reset procedures without explaining scope and obtaining the required confirmation.
- Never call a Pod `healthy` from `Running` alone.
- Never call an integration successful from a component-level test alone.
- Never apply an upstream procedure to k3s, RKE2, a managed provider, Talos, or OpenShift without loading its overlay.
