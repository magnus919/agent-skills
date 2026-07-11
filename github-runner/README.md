# Self-Hosted GitHub Actions Runners

Deploy, manage, and troubleshoot self-hosted GitHub Actions runners. Covers systemd, Docker, Kubernetes (ARC), and Scale Set Client deployments.

## Why Install This Skill

When your agent loads this skill, it becomes a **CI/CD infrastructure engineer** who can:

- **Choose the right deployment** — systemd for single machines, Docker for homelabs, ARC for Kubernetes teams
- **Troubleshoot registration failures** — the critical ACCESS_TOKEN vs RUNNER_TOKEN distinction
- **Design autoscaling** — ARC, Scale Set Client, ephemeral runners
- **Harden runner security** — public repo risks, JIT tokens, runner groups
- **Build custom runner images** — Dockerfiles with custom toolchain, Python, Ruby
- **Solve network issues** — firewall rules, TLS, proxy configuration

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Deployment spectrum, quick reference, label strategy |
| `references/` | 7 reference files: deployment, management, scaling, security, custom images, network, monitoring |

## Quick Start

Start with the setup and first workflow in SKILL.md, then use the linked resources for the specific task you need to complete.

## Triggers

Load this when setting up CI, troubleshooting runner registration failures, designing autoscaling, or hardening runner security.

## Requirements

Linux, macOS, or Windows target hosts. Docker for containerized runners. Kubernetes for ARC deployments.
