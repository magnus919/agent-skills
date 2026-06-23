# Autoscaling

Four approaches to autoscaling self-hosted runners.

## 1. Actions Runner Controller (ARC) — Reference Implementation

ARC is GitHub's recommended Kubernetes-based autoscaling solution.

**How it scales:**
1. Runner ScaleSet Listener holds HTTPS long-poll connection to GitHub Actions Service
2. When a job matches the scale set's labels, the listener receives a "Job Available" message
3. The listener checks if it can scale up (within configured max limits)
4. If yes, it acknowledges and patches the EphemeralRunnerSet to increase replica count
5. EphemeralRunner Controller creates runner pods with JIT tokens
6. Each pod runs one job as ephemeral runner, then is deleted
7. Idle runners are scaled down when no jobs are queued

**Helm chart configuration controls:**
- `minReplicas` / `maxReplicas` — scaling boundaries
- `scaleDownDelaySecondsAfterScaleUp` — cooldown timer
- `scaleUpAdjustment` / `scaleDownAdjustment` — scaling step size
- `scaleDownDelaySeconds` — idle timeout before scale down

## 2. GitHub Actions Runner Scale Set Client

Standalone Go module for custom autoscaling outside Kubernetes.

**Use when:**
- You need VM-based autoscaling (AWS EC2, Azure VMSS, GCP)
- You have on-premise infrastructure
- You need multi-platform support (Windows, Linux, macOS)
- ARC's Kubernetes dependency is not a fit

The client handles GitHub API interactions for scale sets. You write the infrastructure provisioning layer that creates and destroys runner instances.

**Repository:** `actions/scaleset` on GitHub

## 3. Webhook-Driven Autoscaling

Use the `workflow_job` webhook to detect job lifecycle events:

| Event Action | Scaling Action |
|--------------|----------------|
| `workflow_job` with `action: queued` | Scale up — deploy new runner |
| `workflow_job` with `action: completed` | Scale down — remove idle runners |

**Considerations:**
- Webhook delivery is not guaranteed timely — can introduce delays
- For larger volumes, use ARC or Scale Set Client instead
- Requires building and maintaining custom automation

## 4. Ephemeral Runner Pattern (Simple Deployments)

For Docker Compose or script-based setups:

1. Listen for `workflow_job` webhooks at org/repo level
2. When jobs queue, deploy new ephemeral runner containers
3. Each container runs with `--ephemeral` flag
4. After one job, runner deregisters and container exits
5. Cleanup process removes exited containers and prunes credentials

**Not recommended** for persistent runner autoscaling — GitHub cannot guarantee jobs aren't assigned to runners being shut down.

## Scaling Recommendations

| Scale | Approach | Complexity | Efficiency |
|-------|----------|------------|------------|
| 1-5 runners | Static Docker Compose | Low | Good |
| 5-50 runners | ARC (K8s) or Scale Set Client | High | Best |
| 50+ runners | ARC (K8s) | High | Best |
| Mixed platform | Scale Set Client | High | Best |
| PoC / low budget | Webhook + Docker | Medium | Moderate |

## Ephemeral vs Persistent

| Aspect | Persistent | Ephemeral |
|--------|------------|-----------|
| Job isolation | Low — shared environment | High — clean per job |
| Auto-scaling | NOT recommended | Recommended |
| Deregistration | Manual / auto after 14d offline | Auto after 1 job |
| Log retention | On-disk in `_diag/` | Must forward externally |
| Setup complexity | Lower | Higher (need provisioning) |
