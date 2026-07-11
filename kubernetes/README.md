# Kubernetes skill

Operate Kubernetes with evidence instead of guesswork. This skill covers upstream Kubernetes and the major self-managed, lightweight, immutable, local, enterprise, and managed-cloud variants, with first-class k3s guidance.

## Why Install This Skill

Kubernetes is a distributed control plane, not just a command-line tool. This skill keeps discovery, safety, version drift, and post-change verification in the same operating loop.

## What You Get

- A discovery-first operating contract
- Deep references for workloads, networking, security, storage, lifecycle, and troubleshooting
- Distribution overlays, including first-class k3s guidance
- A structured, bounded `k8s-cli` wrapper and deterministic tests

## Quick Start

```sh
scripts/k8s-cli --json doctor
scripts/k8s-cli --json discover
scripts/k8s-cli --json get pods --namespace default
```

## Triggers

Use when operating Kubernetes clusters or workloads, debugging Pods, designing APIs or policies, managing k3s or another distribution, or writing automation around kubectl.

## Requirements

`kubectl` and valid cluster credentials/context are required for live operations. The wrapper does not create credentials or bypass RBAC.

## Contents

It includes:

- Discovery-first workflows for clusters, APIs, contexts, namespaces, CRDs, nodes, workloads, and conditions
- Workload, networking, storage, scheduling, autoscaling, security, upgrade, backup, and troubleshooting references
- Distribution overlays for kubeadm/upstream, k3s, RKE2, MicroK8s, k0s, Talos, OpenShift/OKD, kind, Minikube, Rancher, EKS, AKS, and GKE
- A safe, structured `scripts/k8s-cli` wrapper that delegates Kubernetes semantics to native `kubectl`
- Dry-run, confirmation, bounded output, redaction, and post-operation verification patterns
- Dated source and version metadata so stale guidance can be identified

## Quick start

```sh
scripts/k8s-cli doctor --json
scripts/k8s-cli discover --json
scripts/k8s-cli get pods --namespace default --json
scripts/k8s-cli events --namespace default --json
```

The wrapper requires `kubectl` and an already configured kubeconfig or in-cluster environment. It does not create credentials, bypass RBAC, or conceal failed commands.

## Scope

This skill is an operational guide and agent-facing command wrapper. It is not a replacement for provider consoles, a Kubernetes client SDK, a policy engine, a CNI/CSI implementation, or a full observability platform. Provider-specific instructions are linked to current official documentation and must be refreshed as releases change.
