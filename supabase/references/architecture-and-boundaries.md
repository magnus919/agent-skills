# Architecture and boundaries

Read this before system design, security review, feature-parity claims, or debugging across services.

## Three environments

| Environment | Intended use | Operator boundary |
|---|---|---|
| Supabase Platform | Managed development and production | Supabase operates infrastructure, backups, upgrades, and platform-only services according to the selected plan |
| CLI local stack | Local development and CI | The developer's CLI chooses images/config; defaults favor convenience, not exposure or production hardening |
| Official self-hosted Docker | Single-project deployment on operator infrastructure | The operator owns capacity, network, TLS, SMTP, secrets, backups, upgrades, observability, abuse controls, and recovery |

Do not promote behavior from one environment into a claim about another without checking. The local Dashboard does not expose every platform setting; self-hosted Studio is single-project; platform features and support are not implied by an open-source component.

## Service map

- **Postgres** is the system of record. Supabase adds roles, schemas, extensions, migrations, and service-specific metadata.
- **PostgREST** exposes selected Postgres schemas as REST and GraphQL routes through the gateway.
- **Auth (GoTrue)** stores users and sessions in the `auth` schema and issues user JWTs.
- **Realtime** listens to database changes and serves WebSocket clients; replication/publication configuration is part of its data path.
- **Storage** stores object metadata and authorization policy in Postgres while object bytes use the configured file or S3-compatible backend.
- **Edge Runtime** runs Functions from mounted Deno/TypeScript source in self-hosted deployments.
- **Studio** is an administrative UI. It is not the source of truth for schema history or deployment configuration.
- **postgres-meta** supplies schema/admin operations used by Studio.
- **Kong** is the default self-hosted API gateway. Envoy is an optional override. The gateway routes APIs, checks API keys, and protects Studio with basic auth.
- **Supavisor** pools database connections and exposes session and transaction modes.
- **Logflare + Vector** are optional in the current self-hosted Compose release to reduce the default footprint.
- **imgproxy** transforms Storage images.

A `healthy` gateway can still front an unhealthy service. A `healthy` service can still have wrong policy, data, URL, or client behavior. Verify the full path.

## Keys and authorization

Current deployments may support both legacy and new keys:

| Credential | Intended placement | Effect |
|---|---|---|
| Publishable key / legacy anon key | Public clients | Selects the anonymous API role; database access still depends on grants and RLS |
| Secret key / legacy service-role key | Trusted server only | Selects service role and bypasses RLS; compromise is a high-impact incident |
| User access token | User session | Carries authenticated identity/claims evaluated by Auth and RLS |
| JWT signing keys | Auth service/operator | Sign or verify sessions; rotation can invalidate sessions depending on which key changes |
| Database password | Trusted operator/server | Direct/pooler database access; not an application API key |

The self-hosted new-key setup accepts one publishable and one secret opaque key per deployment, alongside legacy keys for migration. When `JWT_KEYS` is configured, Auth signs new sessions with ES256; every verifier must receive compatible JWKS configuration before cutover.

Do not use a service-role request to validate an RLS policy. It bypasses the policy by design. Test with anonymous and authenticated users, including attempts that must return no rows or fail.

## Database exposure boundary

PostgREST exposes schemas listed in `PGRST_DB_SCHEMAS`, currently `public,graphql_public` in the official Docker defaults. Tables in exposed schemas need deliberate grants and RLS. Tables created through Studio may enable RLS automatically; raw SQL does not.

Prefer private schemas for server-only data and functions. Expose the smallest surface, grant only required operations, enable RLS, and write policies for both visibility (`USING`) and proposed rows (`WITH CHECK`) where applicable.

## URL boundary

- `SUPABASE_PUBLIC_URL`: externally reachable base for Studio and APIs.
- `API_EXTERNAL_URL`: externally reachable Auth base and current issuer/callback root; current self-hosted form includes `/auth/v1`.
- `SITE_URL`: the application destination used by Auth redirects, often a different hostname.
- `ADDITIONAL_REDIRECT_URLS`: explicit allowed application redirects.

Behind TLS termination, all externally generated URLs must use the public HTTPS origin. The proxy must forward WebSocket upgrades and `X-Forwarded-*` headers. Recreate affected containers after environment changes; a simple restart does not reload container environment.

## Connection modes

The official self-hosted stack publishes Supavisor session mode on `5432` and transaction mode on `6543`. The username includes the tenant ID, such as `postgres.<tenant-id>`. Transaction pooling is unsuitable for session-dependent behavior such as prepared statements or connection-local state unless the client is configured accordingly.

Do not expose Postgres broadly just because the API gateway is protected. Bind to a trusted interface, use a firewall/private network, require TLS where traffic crosses trust boundaries, and reserve direct connections for migrations or operations that need session semantics.
