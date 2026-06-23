# Deployment Approaches

Four primary approaches to deploying self-hosted runners.

## 1. systemd Service (Linux)

Simplest approach. Download the runner binary, configure, install as a service.

```bash
mkdir actions-runner && cd actions-runner
curl -o runner.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.322.0/actions-runner-linux-x64-2.322.0.tar.gz
tar xzf runner.tar.gz
./config.sh --url https://github.com/org/repo --token <token>
sudo ./svc.sh install
sudo ./svc.sh start
```

**Pros:** Minimal dependencies, full control, direct filesystem access
**Cons:** Manual updates, no built-in lifecycle management, state lives on the host

## 2. Docker Container (myoung34/github-runner)

Ubuntu 20.04-based image wrapping the runner binary with Docker-specific lifecycle management.

```yaml
services:
  runner:
    image: myoung34/github-runner:latest
    container_name: runner
    restart: unless-stopped
    environment:
      - RUNNER_NAME=my-runner
      - RUNNER_SCOPE=org
      - ORG_NAME=myorg
      - ACCESS_TOKEN=ghp_...
      - RUNNER_GROUP=self-hosted
      - LABELS=self-hosted,linux,x64
      - DISABLE_AUTO_UPDATE=1
      - EPHEMERAL=false
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - runner-data:/runner
    networks:
      - traefik

volumes:
  runner-data:

networks:
  traefik:
    external: true
```

**Pros:** Container isolation, named volume for credentials, Docker socket for DinD builds, easy multi-replica
**Cons:** Cannot see host filesystem paths, Ubuntu 20.04 base (Python 3.8), needs Docker socket for builds

**Critical environment variables:**

| Variable | Purpose | Notes |
|----------|---------|-------|
| `ACCESS_TOKEN` | GitHub PAT for registration | Use this, NOT `RUNNER_TOKEN` |
| `RUNNER_SCOPE` | `org` or `repo` | Determines registration endpoint |
| `ORG_NAME` | GitHub org | Required for org scope |
| `REPO_URL` | Full repo URL | Required for repo scope |
| `RUNNER_GROUP` | Target group | Fails if group doesn't exist |
| `LABELS` | Comma-separated | Job routing |
| `EPHEMERAL` | `false` or `true` | Use string, not `0` |
| `DISABLE_AUTO_UPDATE` | `1` | Docker handles version management |
| `RUNNER_WORKDIR` | `/runner/work` | Job working directory |

```bash
# Use .env file for the token
echo "ACCESS_TOKEN=ghp_..." > .env
# In docker-compose.yml: ${ACCESS_TOKEN} or inline
```

## 3. Actions Runner Controller (ARC) — Kubernetes

GitHub's reference implementation — a Kubernetes operator that orchestrates runner scale sets.

**Architecture:**
1. Controller manager deploys in specified namespace
2. AutoScalingRunnerSet resource registers runner scale set with GitHub API
3. Runner ScaleSet Listener establishes HTTPS long-poll connection
4. When a job arrives, listener patches EphemeralRunnerSet with desired replica count
5. EphemeralRunner Controller requests JIT tokens and creates runner pods
6. Runner pod executes job, deregisters, pod is deleted

**Quickstart:**
```bash
# Install the controller
helm install arc-controller \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller \
  --namespace arc-system --create-namespace

# Deploy a runner scale set
helm install arc-runner-set \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set \
  --namespace arc-runners --create-namespace \
  --values values.yaml
```

**Container modes:**
- **Docker-in-Docker (dind)**: Runner pod runs Docker inside — heavier, for workflows needing Docker actions
- **Kubernetes mode**: Steps run as individual pods — lighter, cleaner isolation
- **Default**: Runner binary runs directly in container

**Required CRDs:**
- `AutoScalingRunnerSet`
- `EphemeralRunnerSet`
- `RunnerScaleSetListener`

## 4. GitHub Actions Runner Scale Set Client

Standalone Go module for building custom autoscaling outside Kubernetes. Handles GitHub API interactions while you handle infrastructure provisioning.

**Use case:** Platform teams who need custom autoscaling across VMs, containers, on-prem, or cloud. Supports Windows, Linux, macOS.

**Key properties:**
- Orchestrates GitHub API interactions for scale set registration
- Leaves infrastructure provisioning to you
- Multiple labels for flexible job routing
- Real-time telemetry for job execution
- Extensible — customize for specific requirements

**Note:** This is NOT a replacement for ARC. ARC remains the reference Kubernetes implementation. The Scale Set Client is for non-Kubernetes environments.

**Repository:** `actions/scaleset` on GitHub

## Deployment Comparison

| Approach | Complexity | Autoscaling | Security | Best For |
|----------|------------|-------------|----------|----------|
| systemd | Low | Manual | Low | Single machine, simple CI |
| Docker | Medium | Manual replicas | Medium | Small team, homelab |
| ARC (K8s) | High | Yes (Kubernetes) | High | Teams with K8s expertise |
| Scale Set Client | High | Yes (custom) | High | Platform teams, non-K8s |
