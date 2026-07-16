# Local development and CLI

Read this for CLI installation, project bootstrap, existing-project adoption, team workflow, managed-project linking, or CI.

## Install and pin

The npm-distributed CLI requires Node.js 20 or later. Prefer a project dev dependency so the team and CI share a pinned version:

```sh
npm install --save-dev supabase
npx supabase --version
```

Homebrew, Scoop, and official Linux packages provide a global `supabase` command. Do not install the npm package globally; follow the current official installation page. Disable telemetry with `supabase telemetry disable`, `SUPABASE_TELEMETRY_DISABLED=1`, or `DO_NOT_TRACK=1` when policy requires it.

The CLI local stack requires a Docker-compatible runtime. Official guidance notes that the full local workflow needs substantial memory; diagnose allocation before interpreting container failures as application defects.

## Project layout

After `supabase init`, commit:

- `supabase/config.toml`
- `supabase/migrations/`
- `supabase/seed.sql` or configured seed files
- `supabase/schemas/` only when the project intentionally uses declarative schemas
- database tests and Functions source

Do not commit CLI state such as `.temp/` and `.branches/`. `config.toml` is safe by default, but secrets added to it must use `env(NAME)` references rather than literal values.

## New project

```sh
supabase init
supabase start
supabase status --output json
```

Choose one schema workflow:

- **Declarative:** edit `supabase/schemas/*.sql`, then `supabase db diff -f name`.
- **Imperative:** create and write `supabase migration new name`; local Studio changes can be captured by `db diff` only when declarative schema files are not in use.

Then replay and test:

```sh
supabase db reset
supabase test db
supabase gen types --lang typescript --local > database.types.ts
```

`supabase start` applies migrations and seed on first setup. `supabase stop` preserves local data. `supabase stop --no-backup` removes local data; capture uncommitted schema/data first.

## Adopt an existing managed project

```sh
supabase init
supabase login
supabase link --project-ref PROJECT_REF
supabase db pull
```

The first pull creates a baseline migration and records it as applied remotely. Review the generated SQL before commit. If the project customized managed schemas, pull them separately after the initial public schema pull:

```sh
supabase db pull --schema auth pull-auth-schema
supabase db pull --schema storage pull-storage-schema
```

Do not dump production data directly into a committed seed. Prefer hand-written representative data. If a dump is necessary, use an explicit linked target, then remove PII, credentials, tokens, customer content, and operational identifiers before commit:

```sh
supabase db dump --data-only --linked > supabase/seed.sql
```

Prove the baseline with `supabase start && supabase db reset` before sharing it.

## Daily workflow

1. Pull team changes.
2. Edit the chosen schema source or create a migration.
3. Generate/review the migration.
4. Replay the complete migration and seed chain with `db reset`.
5. Run database and application tests, including negative authorization cases.
6. Regenerate client types.
7. Commit schema source, migration, tests, and generated types together.

With declarative schemas, `db diff` compares schema files to migration history and ignores ad hoc local Studio/SQL changes. With imperative migrations, it can compare the live local database to migrations. Mixing the mental models silently loses changes.

## Target selection

Pass scope explicitly when a wrong target would be costly. Defaults differ:

- `db diff` and `db reset` default local.
- `db pull`, `db push`, and `db dump` default linked.

Use `supabase projects list`, `supabase migration list`, project configuration, and the intended environment before remote operations.

## Managed deployment

```sh
supabase migration list
supabase db push --dry-run
supabase db push
```

Apply only reviewed migrations. Use `--include-seed` only for explicit non-production environments. `supabase db reset --linked` destroys the linked remote database and is limited to disposable development/staging targets after direct confirmation.

Functions and secrets have separate deployment surfaces:

```sh
supabase functions new FUNCTION_NAME
supabase functions serve
supabase secrets set NAME=value
supabase functions deploy FUNCTION_NAME
supabase functions list
supabase secrets list
supabase config push
```

Use `functions serve` and application tests before deployment. Keep local and platform secrets out of source; `config.toml` should use `env(NAME)` references where supported. `config push`, `functions deploy`, and `secrets set` mutate the linked managed project, so verify the project reference and intended environment first. Read current CLI help and Functions documentation before assuming a flag applies to self-hosted Docker; the platform deploy command and mounted self-hosted Functions workflow are different.

## Managed database perimeter

Treat command discovery, eligibility, mutation, and verification as separate gates. Capture current state first:

```sh
supabase --version
supabase ssl-enforcement get --project-ref PROJECT_REF
supabase network-restrictions get --project-ref PROJECT_REF
supabase network-bans get --project-ref PROJECT_REF
```

Before mutation, confirm the project and account permissions, record the current outputs as rollback evidence, preserve an alternate administrative and database access path, and inspect current command help. Help proves syntax, not plan eligibility or safe operational effect.

```sh
supabase ssl-enforcement update --project-ref PROJECT_REF --enable-db-ssl-enforcement
supabase ssl-enforcement update --project-ref PROJECT_REF --disable-db-ssl-enforcement
supabase network-restrictions update --project-ref PROJECT_REF \
  --db-allow-cidr CIDR_1 --db-allow-cidr CIDR_2
supabase network-bans remove --project-ref PROJECT_REF --db-unban-ip IP_ADDRESS
```

`network-restrictions update` replaces the current CIDR set unless `--append` is chosen deliberately. Do not default to `--bypass-cidr-checks`. Remove only an IP proven by `network-bans get` to be banned; distinguish bans from CIDR restrictions, TLS, credentials, and routing failures first. After a change, repeat the corresponding `get`, then test a real TLS database connection from an allowed source and a denied source. Restore the recorded SSL and restriction state if access or application checks fail. Do not invent `--experimental` requirements or rollback timers.

## Managed branches and previews

Managed-platform branches are isolated preview or persistent environments, not Git branches and not a self-hosted Compose feature. Confirm current availability, pricing, and beta status before designing a workflow around them.

```sh
supabase branches list
supabase branches create BRANCH_NAME
```

Branches start without production data. Use reviewed migrations, representative seed data, Functions, configuration, and branch-specific secrets to make a preview reproducible. GitHub integration can create preview branches for pull requests; verify the branch health and migration result rather than treating branch creation as deployment success. Keep branch state such as `.branches/` out of version control.

## CI baseline

A database CI job should pin/setup the CLI, start the local stack, replay migrations, run pgTAP tests, and run application tests against isolated data. A minimal sequence is:

```sh
supabase start
supabase db reset
supabase test db
```

Add type-generation drift checks when generated types are committed. Do not inject production service-role keys into ordinary pull-request jobs. Stop the local stack after the job according to runner lifecycle.
