---
name: github-runner
version: 1.0.1
description: >-
  Deploy, manage, and troubleshoot self-hosted GitHub Actions runners. Covers
  systemd service, Docker containers, Kubernetes (Actions Runner Controller),
  and the Scale Set Client. Use when setting up a CI runner, debugging
  registration failures, designing autoscaling, or hardening runner security.
license: MIT
compatibility: Linux, macOS, or Windows target hosts. Docker for containerized runners. Kubernetes for ARC deployments.
metadata:
  tags: [github-actions, ci-cd, runners, devops, docker, kubernetes, autoscaling]
  source: https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners
---

# Self-Hosted GitHub Actions Runner

Deploy and manage self-hosted GitHub Actions runners — the machines that execute CI/CD workflow jobs. Self-hosted runners give you control over hardware, OS, and toolchain, at the cost of requiring you to maintain the environment.

## When to Use

| Trigger | What to do |
|---------|------------|
| "Set up CI for my project", "deploy a self-hosted runner for [repo/org]" | Read [deployment](references/deployment.md) — choose systemd, Docker, or ARC |
| "Runner won't register / keeps failing", "runner gets 404", "registration token expired" | Read [management](references/management.md) — ACCESS_TOKEN vs RUNNER_TOKEN, groups |
| "How to scale runners automatically", "auto-scale runners", "too many queued jobs" | Read [scaling](references/scaling.md) — ARC, Scale Set Client, ephemeral |
| "Secure my self-hosted runners", "hardening runners", "runner security", "public repo risk" | Read [security](references/security.md) — public repo risks, ephemeral, JIT, groups |
| "Make a custom runner image", "build a runner Dockerfile", "custom runner with Python" | Read [custom-images](references/custom-images.md) — Dockerfile, ARC container modes |
| "What domains does a runner need to reach?", "runner firewall rules", "runner network setup" | Read [network](references/network.md) — firewall rules, TLS, proxy |
| "Labels, groups, or both for routing?", "how to target specific runners" | Read [management](references/management.md) — labels and groups sections |
| "Monitor / troubleshoot runner issues", "runner offline", "runner not picking up jobs" | Read [management](references/management.md) — monitoring and troubleshooting sections |

## Quick Reference

### Deployment Spectrum

| Approach | Complexity | Autoscaling | Best For |
|----------|------------|-------------|----------|
| systemd service | Low | Manual | Single machine, simple CI |
| Docker container | Medium | Manual replicas | Homelab, small team |
| ARC (Kubernetes) | High | Built-in | Teams with K8s expertise |
| Scale Set Client | High | Custom | Non-K8s platform teams |

### Critical: ACCESS_TOKEN vs RUNNER_TOKEN

This is the most common setup failure. The `myoung34/github-runner` Docker entrypoint **unexports `RUNNER_TOKEN`** at startup — it's only used for **de-registration**. Registration requires `ACCESS_TOKEN` (a GitHub PAT).

| Token | Purpose | Expiry |
|-------|---------|--------|
| `ACCESS_TOKEN` | Registration — generates fresh tokens via GitHub API | Long-lived (PAT) |
| `RUNNER_TOKEN` | **De-registration only** — NOT for initial registration | 60 min |

**PAT scopes:**
- Repo-level: `repo`
- Org-level: `admin:org`
- Enterprise-level: `manage_runners:enterprise`

### Labels Strategy

Default labels: `self-hosted` + OS (`linux`/`windows`/`macOS`) + arch (`x64`/`ARM`/`ARM32`/`ARM64`)

Common convention: `self-hosted,<hostname>,<os>,<arch>,<project>`. In workflows:

```yaml
runs-on: [self-hosted, linux, x64, gpu]
```

All labels must match (AND logic). Use `--no-default-labels` to strip OS/arch auto-labels.

### Key Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| 404 on POST to runner-registration | `RUNNER_TOKEN` used instead of `ACCESS_TOKEN` | Switch to `ACCESS_TOKEN` with PAT |
| "Could not find any self-hosted runner group named 'Default'" | Org uses different group name | Check groups via `gh api`, set `RUNNER_GROUP` |
| "Ephemeral option is enabled" when not wanted | `EPHEMERAL=0` — truthy in bash | Use `EPHEMERAL=false` (string) |
| `docker compose down -v` wipes credentials | Named volumes deleted | With `ACCESS_TOKEN`, auto-recovers |
| Runner can't see host filesystem paths | Runner runs inside Docker container | Write deploy configs inline in workflow |
| Hugo build: "Go not found" | No Go on Ubuntu 20.04 runner | `hugo mod vendor` and commit `_vendor/` |
| GHCR pull "unauthorized" | No Docker registry auth in deploy job | Add `docker/login-action@v4` |
| Runner offline >14 days | Auto-removed by GitHub | Register a new runner |

## Sequential Workflow

### 1. Choose deployment approach

Read [deployment](references/deployment.md) and select systemd, Docker, ARC, or Scale Set Client.

### 2. Figure out what runner scope you need

- **Repo-level**: Runner scoped to a single repo — you need admin access
- **Org-level**: Runner shared across repos in an org — you need org owner access
- **Enterprise-level**: Runner shared across orgs in an enterprise — you need enterprise access

### 3. Register the runner

Read the [architecture](references/architecture.md) reference for the registration flow.

### 4. Route jobs to the runner

Use `runs-on` with labels and optionally groups. Read [management](references/management.md) labels section.

### 5. Monitor and troubleshoot

Read the [management](references/management.md) troubleshooting section when things go wrong.

### 6. Plan for security and scaling

Read [security](references/security.md) and [scaling](references/scaling.md) for production deployments.

## Templates

- [templates/docker-compose.yml](templates/docker-compose.yml) — Docker runner with `myoung34/github-runner`
- [templates/custom-runner.Dockerfile](templates/custom-runner.Dockerfile) — Custom runner image for ARC

## Reference Files

| File | Load when |
|------|-----------|
| [references/architecture.md](references/architecture.md) | You need to understand registration flow, job lifecycle, or runner communication |
| [references/deployment.md](references/deployment.md) | You need to deploy a runner — systemd, Docker, ARC, or Scale Set Client |
| [references/security.md](references/security.md) | You need to harden runners, set up ephemeral/JIT, configure groups |
| [references/scaling.md](references/scaling.md) | You need autoscaling — ARC, Scale Set Client, or webhook-driven |
| [references/management.md](references/management.md) | You need groups, labels, monitoring, troubleshooting, or cleanup |
| [references/custom-images.md](references/custom-images.md) | You need a custom runner Dockerfile, ARC Kubernetes mode |
| [references/network.md](references/network.md) | You need firewall rules, proxy config, or are troubleshooting connectivity |
