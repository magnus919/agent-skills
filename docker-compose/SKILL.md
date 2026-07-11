---
name: docker-compose
description: >-
  Use Docker Compose to define, run, debug, and harden multi-container applications.
  Load for compose.yaml design, networking, volumes, secrets, profiles, overrides,
  watch mode, lifecycle operations, or troubleshooting.
license: MIT
compatibility: Docker Compose v2 or another implementation of the Compose Specification; commands require Docker CLI.
metadata:
  source: https://docs.docker.com/compose/
  spec: https://github.com/compose-spec/compose-spec
---

# Docker Compose

Use this skill for the whole Compose lifecycle: model the application, validate the resolved configuration, start or update services, inspect runtime state, and diagnose failures. Prefer the current Compose Specification. Do not add a top-level `version` key to new files: it is obsolete and does not select a schema.

## Operating loop

1. **Discover** the Compose file(s), project directory, env files, profiles, external resources, and whether the task is development, CI, staging, or production.
2. **Model** the application with services, named volumes for durable state, explicit networks for isolation, secrets for sensitive files, and profiles for optional services.
3. **Resolve before running**:
   ```bash
   docker compose -f compose.yaml config --quiet
   docker compose -f compose.yaml config
   docker compose -f compose.yaml config --services
   ```
4. **Operate** with the narrowest command: `up -d SERVICE`, `restart SERVICE`, `run --rm SERVICE COMMAND`, or `exec SERVICE COMMAND`. Avoid `down -v` unless data deletion is intentional and confirmed.
5. **Verify** with `ps`, health status, logs, an in-container check, and the externally published endpoint where applicable.
6. **Diagnose in order**: resolved model → container state → logs → healthcheck → network membership/DNS → mounts/permissions → image/build architecture → host resources.

## Decision rules

- `depends_on` controls creation order, not readiness. Use a real `healthcheck` plus `condition: service_healthy`; use `service_completed_successfully` for migrations or jobs. Do not use `sleep` as readiness logic.
- Containers reach sibling services by **service name** and **container port** (`db:5432`), not host-published ports or container IPs.
- Use the default network for simple projects. Use separate networks to isolate tiers, `internal: true` for a network with no external gateway, and an explicitly named `external: true` network only when it is created outside the project.
- Use bind mounts for source/configuration during development, named volumes for state, and read-only mounts for immutable inputs. Treat host-path mounts as platform-sensitive.
- Put credentials in Compose secrets or an external secret manager, not in images, Git, or ordinary environment variables. Grant each secret only to services that need it. Compose secrets are mounted at `/run/secrets/<name>`.
- Use profiles for optional tools such as debugging, migrations, observability, or GPU workloads. Core services should have no profile.
- Resolve interpolation explicitly. Shell variables override `--env-file`, which overrides the project `.env`; use `${REQUIRED:?explain}` for mandatory values and `$$` for a literal dollar sign. For example, write `test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER}"]` when the container shell, not Compose, must expand the variable. Check with `docker compose config --environment`.
- In multi-file merges, later files are applied to the base. Relative paths resolve from the first/base file. Inspect the result with `docker compose config`; use `!reset` or `!override` when ordinary merge behavior is not what you want.
- Compose Watch is for services built from local source. Use `sync` for hot-reloadable source, `sync+restart` for configuration, and `rebuild` for dependency or image changes. The container user must be able to write to the target path.
- Treat `deploy` fields as implementation-dependent. Verify what the target Compose implementation enforces; the specification explicitly allows partial support.

## Quick command card

```bash
docker compose version
docker compose config --quiet
docker compose up -d --build
docker compose ps
docker compose logs -f --tail=100 SERVICE
docker compose exec SERVICE COMMAND
docker compose run --rm SERVICE COMMAND
docker compose restart SERVICE
docker compose stop
docker compose down                    # preserves named volumes
docker compose down --remove-orphans
docker compose pull && docker compose up -d
docker compose --profile debug up -d
docker compose up --watch
docker compose port SERVICE CONTAINER_PORT
docker network inspect PROJECT_default
docker volume inspect PROJECT_VOLUME
```

## High-value defaults

- When `compose.override.yaml` exists beside `compose.yaml` and no `-f` files are supplied, Compose loads the override automatically; use explicit `-f` files for production combinations.
- **Destructive CI gate:** never run `down --volumes` until `docker compose -p ci-${CI_JOB_ID:?CI_JOB_ID is required} config --services` confirms the isolated project name; on shared environments, omit `--volumes` unless the exact data scope is intentional.
- Treat `deploy` resource and placement fields as target-dependent: a rendered field can be valid while the local implementation ignores it. Verify enforcement at runtime.

### Base/dev/prod command matrix

```bash
# Base or default development override
docker compose config --quiet
docker compose up --watch

# Explicit production model
IMAGE_TAG=release-1 docker compose -f compose.yaml -f compose.prod.yaml config --quiet
IMAGE_TAG=release-1 docker compose -f compose.yaml -f compose.prod.yaml up -d

# Optional tooling
docker compose --profile debug up -d
```

The default `compose.override.yaml` is auto-loaded; production overrides must be selected explicitly.

**Rendered configuration is not runtime proof.** `config` can confirm a secret declaration, resource limit, or healthcheck is present, but only runtime inspection proves the secret file is mounted, the healthcheck passes, or the target implementation enforces `deploy` limits. Verify with `exec`, `ps`, `inspect`, and measured behavior on the target host.

## Reference routing

| Load when | Reference |
|---|---|
| Starting a project or choosing primitives | `references/01-model-and-file-design.md` |
| Dependencies, healthchecks, shutdown, or jobs | `references/02-lifecycle-and-health.md` |
| DNS, ports, networks, volumes, or persistence | `references/03-networking-and-storage.md` |
| `.env`, interpolation, profiles, or overrides | `references/04-configuration-and-overrides.md` |
| Watch, builds, CI, or production operations | `references/05-development-and-production.md` |
| Secrets, least privilege, or supply-chain concerns | `references/06-security.md` |
| A failure needs a systematic workflow | `references/07-troubleshooting.md` |
| CLI command or field lookup | `references/08-command-playbook.md` |
| Source coverage and freshness checks | `references/00-source-index.md` |

## Included artifacts

- `templates/`: portable base, development, production, environment, and secret-file examples.
- `assets/project-review-checklist.md`: handoff and pre-deployment review checklist.
- `scripts/compose-doctor.sh`: deterministic validation and runtime diagnostics with text or JSON output.

## Failure boundaries

- `config --quiet` proves model resolution, not image pulls, startup, or application correctness.
- A running container is not a ready service. A passing healthcheck is not end-to-end verification.
- `docker compose down` removes project containers and networks; it normally preserves named volumes. `down -v` is destructive.

## When not to use this skill

Use an orchestrator-specific skill for Kubernetes, Swarm scheduling, or another platform's deployment controller. Compose can describe some deploy concepts, but is not a substitute for that platform's operational API.
