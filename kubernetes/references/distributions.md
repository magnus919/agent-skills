# Distribution and provider overlays

Use this matrix as routing, not as a timeless release catalog. Refresh release/support fields before relying on them.

| Family | Distinguishing lifecycle/defaults | Load before |
|---|---|---|
| upstream/kubeadm | static control-plane Pods, etcd, install CNI separately, `kubeadm upgrade` | bootstrap, HA, upgrade |
| k3s | single binary, SQLite/embedded etcd/Kine, Flannel, Traefik, ServiceLB, local-path storage, `k3s etcd-snapshot` | any self-managed edge or lightweight operation |
| RKE2 | Rancher enterprise distribution, static Pods, etcd, Canal/Calico/Flannel, Rancher lifecycle | FIPS, Rancher, upgrade |
| MicroK8s | snap packaging, dqlite HA, addons, `microk8s` wrapper | snap/addon/HA operation |
| k0s | single binary, controller/worker separation, SQLite/etcd/Kine, k0sctl | k0sctl, backup, upgrade |
| Talos | immutable API-only OS, no SSH/shell/package manager, `talosctl`, etcd | node-level operations |
| OpenShift/OKD | Operators, CVO, OAuth, `oc`, OVN/Router | OpenShift-specific lifecycle/policy |
| Rancher | management platform, not a distribution; manages/imports downstream clusters | Fleet, Rancher auth, provisioning |
| kind | Docker/Podman node containers, disposable test clusters | local integration tests |
| Minikube | local single-node VM/container cluster, driver/addon lifecycle | local development |
| EKS | AWS-managed control plane, VPC CNI, EKS API, IRSA/Pod Identity, Standard/Auto Mode | AWS identity, load balancer, upgrade |
| AKS | Azure-managed control plane, Azure CNI/Cilium, Workload ID, Standard/Automatic | Azure identity, upgrade, node pools |
| GKE | Google-managed control plane, Standard/Autopilot, release channels, Workload Identity | GCP identity, upgrade, networking |

## Detection

Use explicit operator input first. Then inspect server version, node labels, system namespaces, component names, and provider CLI context. Detection is a hypothesis. Confirm against official docs and cluster evidence before applying defaults.

## Version baseline checked 2026-07-11

- Kubernetes project: maintained minor branches 1.36, 1.35, 1.34.
- k3s release: `v1.36.2+k3s1`.
- RKE2 release: `v1.36.2+rke2r1`.
- k0s release: `v1.36.2+k0s.0`.
- Talos release: `v1.13.6`.
- kind release: `v0.32.0`.
- Minikube release: `v1.38.1`.

These values are observations, not promises. Use the official release pages below for refresh.

## k3s first-class notes

Server nodes run control-plane and datastore components; agents run kubelet, runtime, and CNI. Single-server SQLite, HA embedded etcd, and external datastore/Kine topologies differ. K3s bundles CoreDNS, Traefik, ServiceLB, local-path storage, and networking services. Upgrade servers before agents and use the current k3s upgrade/backup procedure.

## Managed provider boundary

Do not inspect or mutate managed control-plane processes as if they were kubeadm static Pods. Use the provider API/CLI for cluster lifecycle and Kubernetes APIs for workloads. Provider identity and load-balancer resources require provider credentials and must be validated outside the cluster too.

## Sources

- https://kubernetes.io/docs/reference/setup-tools/kubeadm/
- https://docs.k3s.io/architecture
- https://docs.k3s.io/datastore
- https://docs.k3s.io/upgrades
- https://docs.rke2.io/architecture
- https://docs.rke2.io/upgrade
- https://microk8s.io/docs
- https://docs.k0sproject.io/stable/architecture/
- https://docs.talos.dev/
- https://docs.openshift.com/container-platform/latest/
- https://docs.rancher.com/rancher/
- https://kind.sigs.k8s.io/
- https://minikube.sigs.k8s.io/docs/
- https://docs.aws.amazon.com/eks/latest/userguide/
- https://learn.microsoft.com/en-us/azure/aks/
- https://cloud.google.com/kubernetes-engine/docs/
- https://kubernetes.io/releases/
