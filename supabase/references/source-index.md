# Source index

Research checked: **2026-07-16**.

Use current official documentation and source before making version-sensitive claims. Supabase services are released independently, while the self-hosted Docker directory pins a tested combination.

## Primary documentation

| Topic | Authoritative source |
|---|---|
| Documentation index | https://supabase.com/docs |
| CLI local development | https://supabase.com/docs/guides/local-development/cli/getting-started |
| Local workflow | https://supabase.com/docs/guides/local-development/cli-workflows |
| CLI command reference | https://supabase.com/docs/reference/cli |
| Database migrations | https://supabase.com/docs/guides/local-development/database-migrations |
| Declarative schemas | https://supabase.com/docs/guides/local-development/declarative-database-schemas |
| Seed data | https://supabase.com/docs/guides/local-development/seeding-your-database |
| Database testing | https://supabase.com/docs/guides/local-development/testing/overview |
| Generated types | https://supabase.com/docs/guides/database/api/generating-types |
| Row Level Security | https://supabase.com/docs/guides/database/postgres/row-level-security |
| Edge Functions | https://supabase.com/docs/guides/functions |
| Managed branching | https://supabase.com/docs/guides/deployment/branching |
| GitHub integration | https://supabase.com/docs/guides/deployment/branching/github-integration |
| Self-hosting overview | https://supabase.com/docs/guides/self-hosting |
| Docker deployment | https://supabase.com/docs/guides/self-hosting/docker |
| HTTPS proxy | https://supabase.com/docs/guides/self-hosting/self-hosted-proxy-https |
| New API keys/asymmetric auth | https://supabase.com/docs/guides/self-hosting/self-hosted-auth-keys |
| Self-hosted Functions | https://supabase.com/docs/guides/self-hosting/self-hosted-functions |
| Postgres 17 upgrade | https://supabase.com/docs/guides/self-hosting/postgres-upgrade-17 |
| Platform-to-self-host restore | https://supabase.com/docs/guides/self-hosting/restore-from-platform |

## Canonical source repositories

- Main repository and official Docker stack: https://github.com/supabase/supabase/tree/master/docker
- Supabase CLI: https://github.com/supabase/cli
- Auth: https://github.com/supabase/auth
- Realtime: https://github.com/supabase/realtime
- Storage: https://github.com/supabase/storage
- Edge Runtime: https://github.com/supabase/edge-runtime
- Supavisor: https://github.com/supabase/supavisor
- Supabase Postgres: https://github.com/supabase/postgres
- PostgREST: https://github.com/PostgREST/postgrest

Within the official Docker directory, read `README.md`, `CONFIG.md`, `CHANGELOG.md`, `versions.md`, `.env.example`, `docker-compose.yml`, `run.sh`, and the relevant `tests/` file together. `CONFIG.md` explicitly distinguishes source-derived facts from interpretive descriptions; use each service's own documentation or source when intent matters.

## Freshness rules

1. Prefer current source and dated changelog entries over older prose examples.
2. Treat exact image tags, CLI flags, environment variables, routes, defaults, and platform parity as version-sensitive.
3. Do not assume the CLI local stack and self-hosted Compose stack run identical versions or expose identical management features.
4. When official pages disagree, reconcile against the current Docker Compose file, Docker changelog, and service source. For example, an older restore page may mention Postgres 15 while the current Docker release and upgrade guide establish Postgres 17 as the default.
5. Record the source URL and access date for operational decisions that will outlive the session.

## Live validation performed

The skill was refined against the official self-hosted Docker configuration from the `supabase/supabase` default branch at commit `ae957414b46527249c22bd9b81f0338bd0956a05` and the stable Supabase CLI `2.109.1` available on 2026-07-16. Validation covered configuration resolution, Linux Docker deployment, service health, the official 35-check end-to-end self-hosted smoke suite, and the current CLI command/help surface. This is execution evidence for that release set, not a guarantee for future images or every infrastructure topology.
