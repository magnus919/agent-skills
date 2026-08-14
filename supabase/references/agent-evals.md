# Agent evals harness

Read this when measuring how well an agent can use Supabase, comparing agent setups on scored Supabase scenarios, or evaluating an agent's competence on a workflow this skill already covers (RLS/security, migrations, Auth, Storage, Functions, self-hosting).

## What it is

[supabase/evals](https://github.com/supabase/evals) is the official harness that answers "how well can agents use Supabase across various tasks" by running agents against scored scenarios. It is an external benchmark owned by Supabase, not part of this repository: this change adds no submodule, and the harness's results do not replace this skill's `evals/evals.json` output-quality contract. The harness sources its own skills from the separate [supabase/agent-skills](https://github.com/supabase/agent-skills) repository, pinned as a git submodule inside supabase/evals; do not confuse that submodule with this catalog skill.

## Concepts

- An **eval** is one scenario under `evals/<id>/`. It contains `evals/<id>/PROMPT.md` (frontmatter metadata plus the task the agent sees), `evals/<id>/EVAL.ts` (a default-exported scorer), and optional starting state for two environments: `remote/` (the hosted project's state, seeded into a platform-lite mock) and `local/` (files copied into the agent's workspace).
- An **experiment** is one agent/runtime/model setup under `experiments/<name>.ts`.
- An **eval suite** is a named set of evals to run together; an **experiment suite** is a named set of experiments with related configurations for head-to-head comparison.
- An **agent** is the model driver that receives the eval prompt and calls the configured tools; a **runtime** is the local Supabase-like environment and tool surface an experiment gives to the agent.
- `platform-lite` exposes a Supabase Management API-compatible HTTP surface backed by `@supabase/lite`, so real tools such as `@supabase/mcp-server-supabase` can run against a lightweight project.

Frontmatter in `evals/<id>/PROMPT.md` (stage, suite, product, topic, motivation) drives eval discovery and web-app filters. `suite` is required on every eval and is one of `benchmark`, `regression`, or `other`.

## Two runtimes

The harness picks the runtime per eval:

- **Tools evals** run the agent against the experiment's MCP/tool surface with no filesystem (no `local/` directory and no `interface: cli`), then score the resulting project state or report.
- **Local-stack evals** run the agent inside a Docker sandbox that has a `bash` tool, file tools, and the real Supabase CLI installed, so it can run `supabase init/start/db/test` against a real local stack. An eval uses this runtime when it ships a `local/` workspace or declares `interface: cli`; `interface` (`mcp` | `cli`) is otherwise a benchmark dimension, not the runtime switch.

Local-stack evals require a running Docker daemon. Each attempt boots a fresh sandbox container on host networking and mounts the host Docker socket, so `supabase start` spawns the stack as sibling containers on the sandbox's `127.0.0.1`. Supabase default ports (54321-54329) must be free — stop any local `supabase start` stacks before running. A `services:` frontmatter list limits which local-stack services the scenario starts (an empty list starts only the database; omitting the key starts the full stack), and `cliVersion: x.y.z` pins a specific Supabase CLI release. After the agent finishes, the harness copies the workspace out of the sandbox so scorers can run host tooling (for example repo-root `vite`/`vitest`) against the produced files; scorers may also run commands and SQL inside the sandbox against the live stack.

## How to run

```sh
git clone --recurse-submodules git@github.com:supabase/evals.git
cd evals
pnpm install
cp .env.example .env   # add the provider key(s) agent-backed runs need
pnpm eval -- --eval resolve-dataapi-001-empty-results --experiment claude-code-sonnet-5
```

`--eval`, `--experiment`, `--suite`, and `--experiment-suite` each accept repeated flags and comma-separated values. Example selections:

```sh
pnpm eval -- \
  --experiment claude-code-sonnet-5 \
  --experiment claude-code-opus-5 \
  --eval build-rls-002-own-todos-client \
  --eval resolve-security-001-rls-cross-user-leak

pnpm eval -- --suite benchmark --experiment-suite benchmark,no-skills
```

Runs write local result files under `results/`. After running, export and view results in the harness web app:

```sh
pnpm export-results   # writes eval-results.json for the web app
pnpm web
```

The sandbox plumbing has its own smoke test (`pnpm --filter @supabase-evals/sandbox test:docker`), and `pnpm check` runs typechecks plus local smoke tests. Verify current scenario IDs, commands, and metadata values against the repo before citing them; the harness evolves.

## Mapping to this skill's workflows

The harness's `evals/` scenarios map directly onto the skill's operating references, which is what makes running them actionable from this skill's contract:

| Skill workflow | Reference | Example eval scenarios |
|---|---|---|
| RLS, security, and authorization testing | [database development and testing](database-development-and-testing.md) | `build-rls-002-own-todos-client`, `build-rls-003-org-roles-permissions`, `build-security-001-public-table`, `resolve-security-001-rls-cross-user-leak`, `resolve-security-002-rls-cross-tenant-leak`, `build-tests-001-rls-tenant-isolation` |
| Migrations, bootstrap, and schema authoring | [database development and testing](database-development-and-testing.md), [local development and CLI](local-development-and-cli.md) | `build-cli-001-bootstrap-app`, `build-cli-002-declarative-schema`, `build-database-001-migrate-postgres-to-supabase`, `resolve-database-001-migration-history-mismatch` |
| Auth | [application services](application-services.md) | `build-auth-001-email-password-flow`, `investigate-auth-001-deleted-user-access`, `build-functions-005-dual-auth-user-secret` |
| Storage | [application services](application-services.md) | `build-storage-001-private-bucket-access`, `resolve-storage-001-upsert-missing-update-policy` |
| Edge Functions | [application services](application-services.md) | `build-functions-002-edge-auth-db`, `build-functions-004-service-role-bypass`, `deploy-functions-001-edge-function-secrets`, `investigate-functions-001-546-resource-limit` |
| Realtime | [application services](application-services.md) | `build-realtime-001-live-chat-updates`, `investigate-realtime-001-subscribed-no-events` |
| Self-hosting | [self-hosting deployment](self-hosting-deployment.md), [administration and recovery](administration-and-recovery.md) | `deploy-self-hosting-001-docker-compose`, `deploy-database-001-prometheus-metrics` |
| Troubleshooting and diagnosis | [troubleshooting](troubleshooting.md) | `resolve-dataapi-001-empty-results`, `investigate-db-001-table-row-counts`, `investigate-logs-001-top-error-function`, `resolve-reliability-001-unhealthy-project-recovery` |

Use the scenario set that matches the workflow under evaluation, and prefer scenarios that exercise the delivery boundary the skill requires (real authorization paths, migration replay, live stack services) over scenarios that can be gamed with unverified claims.

## Relationship to this skill's evals

- The harness is an external benchmark: it measures agent task competence on scored scenarios and is owned by Supabase.
- `supabase/evals/evals.json` in this catalog is this repository's schema-versioned output-quality contract for the skill's own cases.
- They are complementary, not duplicates. Run the harness when the question is "how well can an agent use Supabase?"; keep the catalog manifest as the regression contract for this skill's documented behaviors.

## When not to use

- Do not use this reference to design evaluation methodology, datasets, or graders — that is [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md).
- Do not confuse supabase/evals with this skill's own `evals/evals.json`: the former runs agents against scored scenarios, the latter is a static output-quality contract validated by this repository.

## Attribution

Concepts, runtime descriptions, and commands in this reference are derived from the [supabase/evals README](https://github.com/supabase/evals), Copyright Supabase, licensed under [Apache-2.0](https://github.com/supabase/evals/blob/main/LICENSE). Definitions are paraphrased or quoted for documentation; the harness and its skills submodule remain external to this repository.
