# Multi-Tenant Isolation

## Make The Decision Now

Define the isolation promise: which tenants may share compute, storage, keys, queues, caches, search indexes, logs, and support paths, and which may not. Derive tenant context on the server from a verified identity or trusted workload binding, then enforce it at every data and resource boundary.

## Choose Layered Controls

- Scope queries, object stores, caches, queues, search, exports, background jobs, and analytics by server-derived tenant context.
- Use one or more fitting mechanisms: separate accounts or databases, schema or namespace boundaries, application-enforced predicates, row-level security, encryption-key separation, or workload isolation. RLS is one option and still needs correct policy, connection, and privileged-job handling.
- Bind job payloads and callbacks to tenant context; authorize workers and support tools independently rather than trusting a queue field.
- Partition caches and rate limits; avoid keys, reuse, or resource quotas that let one tenant read, influence, or exhaust another tenant's resources.
- Make safe defaults automatic: a new tenant should receive restrictive permissions, isolation, logging, and limits without manual hardening. This aligns with CISA Secure by Design joint guidance.
- Constrain AI retrieval and tools to the authorized tenant and user context. A prompt must not broaden a corpus or tool capability.

## Evidence And Verification

Test cross-tenant reads, writes, cache hits, search results, exports, jobs, audit events, and resource exhaustion using distinct tenants. Inspect privileged paths, migrations, support tools, and batch workers for policy bypass. Prove provisioning produces safe defaults.

## Misuse To Avoid

- Filtering tenant IDs only in the UI or trusting a client-provided tenant header.
- Treating database isolation as sufficient while cache keys, logs, or asynchronous workers remain shared.
- Granting an AI agent a tenant-wide capability when the user needs a document-scoped one.
