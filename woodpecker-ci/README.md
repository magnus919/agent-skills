# Woodpecker CI — Self-Hosted CI Operations

A practical reference for running Woodpecker CI from first deployment through pipeline design and incident response.

## Why Install This Skill

Woodpecker is small enough to self-host, but the important failures are distributed across the forge, OAuth, server, agent, container backend, and workflow file. This skill gives your agent a repeatable way to locate the failing boundary instead of guessing at YAML.

After installing it, your agent can set up a Docker Compose server and agent, connect Forgejo or Gitea, write workflows with conditions and services, manage secrets safely, choose Docker versus Kubernetes execution, and troubleshoot clone, scheduling, image, and permission failures.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating loop and routing guide |
| `references/` | Setup, syntax, operations, troubleshooting, security, advanced patterns, failure signatures, CLI, and source notes |
| `templates/` | Compose deployment, Forgejo environment contract, and workflow skeleton |
| `assets/` | Human-readable incident checklist |
| `scripts/` | Dependency-free connectivity and configuration doctor |

## Quick Start

```bash
cp templates/docker-compose.yml compose.yaml
cp templates/forgejo.env.example .env
openssl rand -hex 32  # put the result in WOODPECKER_AGENT_SECRET

docker compose config --quiet && docker compose up -d
```

## Triggers

Use for Woodpecker CI, `.woodpecker.yml`, `.woodpecker/` workflows, Woodpecker agents, Forgejo/Gitea CI integration, pipeline secrets, plugins, Docker/Kubernetes backends, failed builds, clone errors, or agent scheduling problems.

## Requirements

Docker Compose for the included deployment template. A supported forge and OAuth application are required for normal server use. `woodpecker-cli` is optional for linting and local execution. Kubernetes deployments additionally require cluster access and appropriate RBAC.
