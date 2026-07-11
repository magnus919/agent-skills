# Docker Compose — Multi-Container Application Operations

This skill gives an agent a portable, current reference for defining and operating Docker Compose applications without relying on one host, repository, or agent framework.

## Why Install This Skill

Your agent can design a Compose model, resolve interpolation and overrides before deployment, operate services safely, and debug the common gap between “the container is running” and “the application is ready.” It includes patterns for networks, storage, secrets, profiles, healthchecks, Compose Watch, and production hygiene.

The references are distilled from the current Compose Specification and Docker documentation, with tutorials and operational failure patterns used as secondary context. The skill favors verification commands and explicit destructive-action boundaries over copy-paste optimism.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating loop and decision rules |
| `references/` | Design, lifecycle, networking, configuration, security, troubleshooting, and command references |
| `templates/` | Base, development, production, environment, and secret-file examples |
| `scripts/` | `compose-doctor.sh` validation and diagnostics helper |

## Quick Start

```bash
docker compose -f templates/compose.yaml config --quiet
bash scripts/compose-doctor.sh ./templates
```

## Triggers

Load for `compose.yaml`, Docker Compose, multi-container applications, `docker compose up`, profiles, healthchecks, services that cannot connect, volume or secret problems, override files, Compose Watch, or Compose production troubleshooting.

## Requirements

Docker Engine with the Docker Compose v2 plugin. The templates assume a POSIX shell; the reference material remains useful on other platforms with equivalent commands.
