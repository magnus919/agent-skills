# LiteLLM Keys, Teams, Budgets, Rate Limits, and Spend

> **Last Updated:** 2026-08-22
> Sources: https://docs.litellm.ai/docs/proxy/virtual_keys ,
> https://docs.litellm.ai/docs/proxy/users ,
> https://docs.litellm.ai/docs/enterprise

This reference covers the credential model (master key vs virtual keys), teams and
users, budget and rate-limit knobs with their enforcement semantics — including the
fail-open-without-DB trap — and spend tracking. Scope: governing who spends what;
routing mechanics live in [02-config-and-routing.md](02-config-and-routing.md).

## Master key vs virtual keys

- `general_settings.master_key` (or env `LITELLM_MASTER_KEY`) must start with `sk-`.
  It is the admin API credential **and** the Admin UI password. If both config and
  env are set, the config value wins.
- Virtual keys are minted with `POST /key/generate` under a master-key bearer and
  returned once. They authorize and meter requests; they never contain provider
  credentials, which stay in `model_list[].litellm_params` (`os.environ/...`) or,
  with `STORE_MODEL_IN_DB=True`, encrypted in Postgres via `LITELLM_SALT_KEY`.
- Key lifecycle: `POST /key/generate`, `GET /key/info?key=...` (spend, expiry,
  models), `POST /key/update`, `POST /key/block` / `/key/unblock` for instant
  revocation, `/key/delete`. Regeneration with grace periods and scheduled
  auto-rotation are Enterprise features.
- What a key inherits: model/MCP access is evaluated against the key row itself;
  management-route power comes from the owner's role — an admin-owned key can hit
  admin endpoints. Admin-created keys without an explicit `user_id` have no owner
  and inherit nothing.
- Self-service guardrails: `litellm_settings.upperbound_key_generate_params` caps
  what any caller can grant itself; `default_key_generate_params` fills omissions;
  `key_generation_settings` restricts who may mint keys. Policy hooks:
  `custom_key_generate` runs on generation only — pair it with `custom_key_update`
  or edits bypass policy.

```bash
curl -X POST 'http://localhost:4000/key/generate' \
  -H 'Authorization: Bearer sk-master' -H 'Content-Type: application/json' \
  -d '{"models": ["gpt-4o"], "max_budget": 50, "budget_duration": "30d",
       "tpm_limit": 80000, "rpm_limit": 60, "duration": "90d"}'
```

## The database requirement — budgets fail open

Keys, teams, budgets, spend logs, and UI state live in Postgres
(`DATABASE_URL`). Without a connected DB:

- `max_budget` is **not enforced** — global spend cannot be loaded, one startup
  warning is logged, requests keep serving past budget.
- `/key/*` endpoints fail with `No connected db.`.

Never run a budget-sensitive deployment DB-less; bound spend upstream instead if you
must run DB-less.

## Budgets

Where things live:

| Scope | Setting | Notes |
|---|---|---|
| Global proxy | `litellm_settings.max_budget` + `budget_duration` | Under litellm_settings, NOT general_settings |
| Team | `/team/new` fields `max_budget`, `budget_duration` | |
| Team member | `/team/member_add` with `max_budget_in_team` | |
| Internal user default | `litellm_settings.max_internal_user_budget` + duration | |
| Virtual key | `/key/generate` fields `max_budget`, `budget_duration` | Multi-window via `budget_limits: [{budget_duration, max_budget}, ...]` |
| End users/customers | `/budget/new` then `litellm_settings.max_end_user_budget_id` | Float `max_end_user_budget` is no longer enforced |

Semantics that matter:

- Crossing a hard budget fails requests (`ExceededBudget` / `ExceededTokenBudget`
  errors); `soft_budget` warns without blocking. Resets are checked by a scheduler
  roughly every 10 minutes (`proxy_budget_rescheduler_min_time/max_time`).
- **Team-key rule:** a key belonging to a team enforces only team (+ member)
  budgets; the owner's personal budget does not apply.
- Cost reservation is ON by default: estimated max cost is reserved before the
  provider call to prevent concurrency overspend. For hard ceilings across replicas
  set `general_settings.fail_closed_budget_enforcement: true` (rejects with 503 when
  Redis+DB cannot verify spend).
- Per-model budgets on keys/users are Enterprise.

## Rate limits

- Knobs on keys/teams/users: `tpm_limit`, `rpm_limit`, `max_parallel_requests`;
  per-model dicts (`model_rpm_limit`, `model_tpm_limit`) supported. Proxy-wide
  concurrency cap: `general_settings.global_max_parallel_requests`.
- Deployment-level `rpm`/`tpm` in `litellm_params` inform weighted routing by
  default; to enforce them as hard limits add
  `router_settings.optional_pre_call_checks: [enforce_model_rate_limits]`
  (RPM exact; TPM best-effort). Needs Redis when multi-instance.
- TPM counting type: `general_settings.token_rate_limit_type: input|output|total`.
- Rate limits do **not** apply to proxy admins — test with an internal-user role.
- Remaining-quota headers: `x-litellm-key-remaining-requests[-<model>]`,
  `x-litellm-key-remaining-tokens[-<model>]`.

## Teams and users

`POST /team/new` (with `members_with_roles`, limits), `/team/info`,
`/team/member_add`, `/team/update`; `POST /user/new`, `GET /user/info`. Roles:
PROXY_ADMIN, PROXY_ADMIN_VIEW_ONLY, ORG_ADMIN (EE), INTERNAL_USER,
INTERNAL_USER_VIEW_ONLY, TEAM, CUSTOMER. Model access groups
(`model_info.access_groups`) let keys/teams be granted a group name instead of
enumerated models.

## Spend tracking

- Every request writes a spend log row (tokens, cost, model, key hash, end user);
  rollups land on key/user/team tables via LiteLLM's cost map. Query surfaces:
  `GET /spend/logs`, `GET /global/spend`, plus the UI.
- `general_settings.disable_spend_logs` turns off per-transaction rows;
  `store_prompts_in_spend_logs` (default **false**) opts into storing full
  prompt/response content per row — a privacy decision, see
  [07-security-and-public-hosting.md](07-security-and-public-hosting.md).
- Retention: `maximum_spend_logs_retention_period` (e.g. `30d`) plus a cleanup
  interval. Batched writes via `proxy_batch_write_at`; high-RPS deployments should
  enable the Redis transaction buffer.

## Verification at the delivery boundary

- Readiness 200 confirms DB connectivity; `/key/info` returns live spend for the key.
- A key restricted to one model gets a clean rejection requesting another model.
- Set a tiny test budget, exceed it, observe the documented error, then restore —
  proving enforcement rather than assuming it (and confirming budgets are not
  silently failing open).
