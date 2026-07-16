# Database development and testing

Read this for schema design, migrations, data changes, seeds, Row Level Security, pgTAP, generated types, or migration-history repair.

## Pick one schema authority

### Declarative schemas

Use `supabase/schemas/*.sql` as desired state. Order files deliberately when objects depend on one another. Edit the schema files first, then:

```sh
supabase db diff -f descriptive-name
supabase db reset
```

Commit schema files and generated migration together. `db diff` does not read ad hoc local database changes when declarative schemas are configured.

### Imperative migrations

Create timestamped forward migrations directly:

```sh
supabase migration new descriptive-name
supabase db reset
```

If using local Studio as a schema editor, capture changes with `supabase db diff -f descriptive-name`, inspect the result, then reset from migrations to prove reproducibility.

Do not maintain both an imported baseline migration and a duplicate declarative representation without an explicit transition plan. Two sources of truth drift.

## Migration review

Generated diffs are drafts. Review for:

- Destructive `DROP`, truncation, type conversion, and constraint operations.
- Redundant or over-broad grants and revoke/re-grant churn.
- Extensions added or removed because local and remote defaults differ.
- View/function ownership and `security definer` search paths.
- RLS policy drops/recreates or renames that the diff engine cannot express safely.
- DML omitted entirely: inserts, updates, deletes, backfills, and data transformations must be authored deliberately.
- Lock duration, table rewrites, index creation, and compatibility with rolling application deployments.

Prefer roll-forward corrections after production deployment. Down migrations are often destructive and should not be generated or run mechanically.

## Seeds

Seeds run after migrations on first local start and on `db reset`. Keep schema changes in migrations and data inserts in seed files.

Default: `supabase/seed.sql`. Multiple ordered files can be configured in `config.toml`:

```toml
[db.seed]
enabled = true
sql_paths = ['./seeds/00-reference.sql', './seeds/10-scenarios.sql']
```

Glob matches are lexically sorted. Hand-written deterministic seeds are the default. Never commit production PII, real tokens, password hashes, customer objects, or other sensitive dumps as development fixtures.

## RLS design

For every table in an exposed schema:

```sql
alter table public.todos enable row level security;
```

Then grant only intended operations to API roles and define policies for each operation. Key distinctions:

- `USING` controls which existing rows are visible/targetable.
- `WITH CHECK` controls which new or changed rows are allowed.
- `auth.uid()` can be `null` for anonymous requests; write policies with explicit identity assumptions.
- A `service_role` request bypasses RLS and cannot validate policy behavior.
- Views, functions, storage metadata, and custom JWT claims introduce separate privilege/ownership paths.

Use private schemas for data that should never be reachable through the Data API. Qualify object names and secure `search_path` in privileged functions.

## Database tests with pgTAP

Create tests with the CLI and run them transactionally:

```sh
supabase test new todos_rls.test
supabase test db
```

RLS suites should cover:

1. Anonymous access allowed and denied.
2. Authenticated user can read/write their own rows.
3. A different authenticated user cannot read/write those rows.
4. Insert/update `WITH CHECK` prevents changing ownership or restricted fields.
5. Deletes and RPC/functions follow the intended policy path.
6. Privileged functions do not expose a bypass through ownership or mutable `search_path`.

Use `begin`/`rollback`, set the local role, and set request JWT claims deliberately. Require negative assertions, not only happy paths.

### Executable negative-test pattern

Adapt table and column names to the migration under test, but preserve the privilege and assertion semantics:

```sql
begin;
select plan(5);

grant usage on schema public to authenticated;
grant select, insert, update, delete on public.documents to authenticated;

set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa","role":"authenticated"}', true);

select throws_ok(
  $$insert into public.documents (id, owner_id, body)
    values ('10000000-0000-0000-0000-000000000001',
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'foreign')$$,
  '42501'
);

select is(
  (with changed as (
     update public.documents set owner_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
      where id = '20000000-0000-0000-0000-000000000002' returning 1
   ) select count(*) from changed),
  0::bigint, 'USING hides cross-owner update'
);

select set_config('request.jwt.claims', '{"sub":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb","role":"authenticated"}', true);
select is(
  (select owner_id from public.documents
    where id = '20000000-0000-0000-0000-000000000002'),
  'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid,
  'owner re-read proves ownership unchanged'
);

select set_config('request.jwt.claims', '{"sub":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa","role":"authenticated"}', true);
select is(
  (with deleted as (
     delete from public.documents
      where id = '20000000-0000-0000-0000-000000000002' returning 1
   ) select count(*) from deleted),
  0::bigint, 'USING hides cross-owner delete'
);

select set_config('request.jwt.claims', '{"sub":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb","role":"authenticated"}', true);
select is(
  (select count(*) from public.documents
    where id = '20000000-0000-0000-0000-000000000002'),
  1::bigint, 'owner re-read proves row remains'
);

select * from finish();
rollback;
```

The direct SQL passed to `throws_ok` proves a `WITH CHECK` exception only after the ordinary grants exist. The data-modifying CTEs prove the zero-row behavior of `USING`; owner re-reads prove the invariant. Lock the expected SQLSTATE or error text to the supported Postgres/Supabase release rather than guessing across versions.

## Application-level tests

Test the client/gateway path in addition to pgTAP. Use unique users and object names so tests can run independently; clean up what they create. Test the publishable key plus user sessions. Keep the secret key in server-only setup/cleanup code and do not use it for behavior under test.

An update blocked by RLS may affect zero rows without returning a dramatic error. Query again as the owning user to prove no unauthorized change occurred.

## Generated types

Generate from the same target whose schema the application will use:

```sh
supabase gen types --lang typescript --local > database.types.ts
supabase gen types --lang typescript --linked > database.types.ts
supabase gen types typescript --db-url "$DATABASE_URL" --schema public > database.types.ts
```

Do not put password-bearing URLs in shell history or CI logs. Regenerate after schema changes and fail CI when committed types drift from the replayed schema.

## Remote rollout

Before push:

```sh
supabase migration list
supabase db push --dry-run
```

Review order and target, take a recovery-capable backup for consequential changes, apply with `db push`, then verify migration history, schema, representative reads/writes, and application compatibility.

If remote schema changed outside migrations, use `db pull` to capture drift and replay locally. If only migration history is wrong, inspect `supabase migration list` and current CLI guidance before `migration repair`; history repair changes bookkeeping and must not be used to hide unapplied SQL.
