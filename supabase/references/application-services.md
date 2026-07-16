# Application services

Read this when building or debugging Auth, Data API, Realtime, Storage, or Edge Functions behavior.

## Client configuration

A normal client needs:

- The public Supabase URL.
- A publishable key (or legacy anon key).
- A user session when acting as an authenticated user.

A trusted backend may use a secret/service-role key for administrative work. Keep separate client instances and configuration paths so the privileged key cannot enter browser/mobile bundles, generated static assets, telemetry, or error reports.

## Auth

Configure and verify:

- `SITE_URL` and allowed redirects.
- External Auth URL/issuer and OAuth callback path.
- SMTP sender, host, port, credentials, and production deliverability.
- Email confirmation/autoconfirm behavior appropriate to the environment.
- OAuth/SAML/SMS/MFA provider settings and provider-console callbacks.
- Token lifetime, signing/JWKS configuration, and rotation plan.

Local CLI Auth settings live in `supabase/config.toml`; use `env(NAME)` for secrets and restart the local stack after changes. Self-hosted settings are environment variables passed to the Auth container and require container recreation to pick up changed environment.

Test the lifecycle through the gateway: create/invite or sign up, confirm as configured, sign in, refresh, inspect user, sign out/revoke, and reject invalid redirects. Do not infer email delivery from a successful Auth API response.

## REST and GraphQL

PostgREST maps exposed schemas to HTTP APIs. Verify:

- Schema is intentionally in `PGRST_DB_SCHEMAS`.
- Grants match each API role.
- RLS is enabled and policies cover each operation.
- Expected maximum-row behavior and query filters.
- RPC functions use safe ownership and `search_path`.

The OpenAPI root `/rest/v1/` currently requires an administrative key in the self-hosted release; a public key returning `403` there is not proof that table routes are broken. Test a real table route with the intended role.

GraphQL depends on `pg_graphql`. It is disabled by default on fresh Postgres 17 self-hosted deployments. An endpoint may return HTTP 200 with an error explaining that the extension is disabled, so inspect the JSON body as well as status.

## Realtime

Realtime readiness requires more than an HTTP route. Verify:

1. The target table is included in the relevant publication/configuration.
2. The client connects through the gateway's WebSocket route with a valid API key.
3. RLS permits the subscribing user to observe the relevant rows.
4. A committed database change produces the expected event.
5. Reconnect and token refresh behavior work through the reverse proxy.

Reverse proxies must forward `Upgrade`/`Connection` behavior and `X-Forwarded-*` headers. Avoid exposing Realtime tenant-management routes; current official gateway configuration blocks sensitive paths.

## Storage

Storage authorization is database-backed. Define buckets and object policies explicitly. For local reproducibility, bucket definitions and seed objects can be declared in `supabase/config.toml` and loaded with `supabase seed buckets`.

Test a complete object lifecycle with the intended role:

- Create or access the bucket.
- Upload within size/MIME constraints.
- Download and verify bytes or checksum.
- Generate/fetch a signed URL when required.
- Deny cross-user object access.
- Delete object and bucket/test fixture.

Self-hosted default file storage persists under the deployment's storage volume/bind path. S3-compatible backends require a separate override and backend-specific backup/availability controls. Database backup alone does not contain object bytes.

## Edge Functions

### CLI local/platform

Create and serve through the CLI local project before platform deployment:

```sh
supabase functions new FUNCTION_NAME
supabase functions serve
supabase functions deploy FUNCTION_NAME
```

Test the function's authorization, CORS, error path, and dependency behavior through the local gateway. Keep function secrets in the supported secrets mechanism, not source or `config.toml` literals. Platform deployment and secret/config updates target the linked managed project; verify the project reference first.

### Self-hosted Docker

Functions live under `volumes/functions/<name>/index.ts`. The official stack's main worker loads functions from the mounted directory. Restart Functions after code changes; recreate it after changing environment/secrets:

```sh
sh run.sh restart functions
sh run.sh recreate functions
```

Invoke through the gateway:

```sh
curl http://localhost:8000/functions/v1/hello
```

The current self-hosted `FUNCTIONS_VERIFY_JWT` setting applies globally to Functions, not per function. Design explicit authorization inside functions that need different policies; do not assume platform deployment options map one-for-one to the self-hosted runtime.

## Cross-service verification

A representative end-to-end flow should sign in a user, perform an RLS-protected REST operation, receive a Realtime event, upload/download a Storage object under policy, and invoke a Function through the gateway. Administrative setup/cleanup may use the secret key, but each user-facing assertion must use the same credentials and route as the application.
