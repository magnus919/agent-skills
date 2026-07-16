# Deployment and self-hosting

## Deployment modes

| Concern | Vercel deployment | Self-hosted Node deployment |
|---|---|---|
| HTTP host | Vercel Functions / Build Output | Nitro `.output/` served by `eve start` |
| Durable execution | Vercel Workflows | Local Workflow world by default, or compatible custom world |
| Session state | Managed Workflow storage | `.eve/.workflow-data` unless an external compatible world is selected |
| Sandbox | Vercel Sandbox by default | `defaultBackend()`, Docker, microsandbox, or custom backend |
| Model credential | Gateway via Vercel OIDC | Gateway API key or direct AI SDK provider key |
| Dashboard | Agent Runs | External OpenTelemetry backend |
| Schedules | Vercel Cron wiring | Nitro schedule runner or the operator’s scheduler |

Eve can self-host. The portability comes from separate HTTP, workflow, and sandbox adapters, not from removing those responsibilities.

## Build and start

```sh
eve build
PORT=3000 eve start --host 0.0.0.0
```

On Vercel, `eve build` emits `.vercel/output`. On a standard Node host, it emits the normal Nitro `.output/` plus Eve’s `.eve/` compilation artifacts.

## Mandatory self-hosting checklist

1. **Workflow persistence:** Put `.eve/.workflow-data` on durable storage, or select a compatible Workflow world package. Ephemeral container filesystems do not provide durable sessions.
2. **Reverse proxy:** Forward both `/eve/` and `/.well-known/workflow/`. The latter carries workflow callbacks; omitting it can start a session and then silently stall execution.
3. **Sandbox:** Leave `defaultBackend()` in place for the local default, select Docker or microsandbox explicitly, or provide a custom adapter. Do not pin `vercel()` for a host that should not create Vercel Sandboxes.
4. **Model route:** Use `AI_GATEWAY_API_KEY` for Gateway routing, or use a direct provider object plus its provider credential to remove Gateway dependency.
5. **Authentication:** Replace placeholder authentication. Do not use `vercelOidc()` as the only production authenticator outside Vercel; use Basic auth, JWT/OIDC validation for the host’s identity provider, or a custom verifier.
6. **Schedules:** Ensure the normal Nitro schedule runner is active, or trigger the equivalent work from an external scheduler.
7. **Observability:** Export OpenTelemetry to a reachable backend and redact sensitive capture when needed.
8. **Verification:** Test health, a real authenticated session, its stream, and a durable callback/resume path.

## Common failures

| Symptom | Likely cause | Check |
|---|---|---|
| Session starts but never progresses | Workflow callback route missing at the proxy | `/.well-known/workflow/` forwarding and upstream logs |
| Sessions disappear after restart | Workflow data on ephemeral disk | Volume mount or external Workflow world |
| Production endpoint rejects all requests | Placeholder auth still installed | Channel auth configuration and runtime secrets |
| Self-hosted deployment calls Vercel unexpectedly | Gateway string model or `vercel()` sandbox backend remains configured | `agent.ts` model shape and sandbox definition |
| Health is green but a real task fails | Only HTTP server checked | Authenticated session, stream, tool, callback, and trace evidence |

## Verify

```sh
curl https://example.test/eve/v1/health
curl -X POST https://example.test/eve/v1/session \
  -H 'content-type: application/json' \
  -d '{"message":"Hello from production"}'
curl https://example.test/eve/v1/session/<sessionId>/stream
```

Use a real authentication mechanism when testing production. Confirm the trace shows the expected model, tool, workflow, and redaction behavior.