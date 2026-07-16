# Supabase skill

Develop, self-host, and operate Supabase without confusing a green container with a working backend or a publishable key with an authorization policy.

## Why Install This Skill

Supabase combines Postgres, Auth, PostgREST, Realtime, Storage, Edge Functions, an API gateway, Studio, and connection pooling. The easy path is productive, but failures cross service boundaries: a URL mismatch breaks OAuth, a plausible migration misses DML, a secret key bypasses RLS, and an image-only upgrade can split a tested service set.

This skill gives your agent one evidence-led workflow for managed projects, CLI-based local development, and the official self-hosted Docker stack. It emphasizes reproducible migrations, negative authorization tests, safe key handling, release-set upgrades, and restores that are actually exercised.

## What You Get

| Resource | Purpose |
|---|---|
| `SKILL.md` | Discovery-first workflow, safety boundaries, routing, and completion checks |
| `references/architecture-and-boundaries.md` | Service map, keys, trust boundaries, and environment differences |
| `references/local-development-and-cli.md` | CLI installation, project layout, local workflow, linking, and deployment |
| `references/database-development-and-testing.md` | Migrations, declarative schemas, seeds, RLS, pgTAP, and type generation |
| `references/application-services.md` | Auth, REST, Realtime, Storage, and Edge Functions integration |
| `references/self-hosting-deployment.md` | Official Docker setup, configuration, TLS, hardening, and smoke testing |
| `references/administration-and-recovery.md` | Backups, restores, updates, Postgres upgrades, observability, and recovery |
| `references/troubleshooting.md` | Layered diagnosis for common local and self-hosted failures |
| `references/source-index.md` | Dated authoritative sources and live validation scope |
| `evals/evals.json` | Development, security, deployment, and recovery regression scenarios |

## Quick Start

For a project-local CLI install:

```sh
npm install --save-dev supabase
npx supabase init
npx supabase start
npx supabase status
```

For an official Linux self-hosted installation, inspect the setup script before running it, then follow the generated project's `run.sh` workflow:

```sh
curl -fsSL https://supabase.link/setup.sh -o setup.sh
less setup.sh
sh setup.sh
cd supabase-project
sh run.sh start
sh tests/test-self-hosted.sh http://localhost:8000
```

## Triggers

Use this skill for Supabase CLI projects, schema migrations, generated database types, Auth and RLS design, Storage or Realtime integration, Edge Functions, managed-project linking, official Docker self-hosting, reverse proxies, secrets, backups, restores, upgrades, health checks, or cross-service troubleshooting.

Do not use it for generic PostgreSQL administration that does not involve Supabase services or conventions.

## Requirements

Local development requires the Supabase CLI plus a Docker-compatible runtime. The npm-distributed CLI requires Node.js 20 or later. The official self-hosted quick start requires a supported Linux system, Git, Docker Engine, Docker Compose, OpenSSL, and `jq`; production operation also needs suitable DNS/TLS, protected secrets, backups, and enough host capacity.
