# API usage, compatibility, and pagination

## Establish the server contract

1. Pass the target with `--server https://forge.example`; do not treat the placeholder default as a usable service.
2. Request `GET /api/v1/version` with the generic command and record the Forgejo major version.
3. Open `https://forge.example/swagger.v1.json` (or `/api/swagger`) and use that server's schema for request fields. Forgejo guarantees API compatibility within a major version; do not assume a current server has the same endpoints or fields as an older Gitea-compatible installation. The upstream usage guide is https://forgejo.org/docs/latest/user/api-usage/.

## Authenticate safely

Use `FORGEJO_AGENT_TOKEN` for automation and `FORGEJO_USER_TOKEN` for user-authorized work. Give tokens the narrowest Forgejo scope that can complete the request. The client sends these as `Authorization: token …`.

The generic `--header Authorization=…` path supports Basic or Bearer authentication when an endpoint requires it. Prefer an environment-backed wrapper or a token for routine use: command-line credentials may be recorded in shell history and process listings. Never put tokens in `--data`, dry-run output, issue text, or logs.

## Paginate intentionally

All list/search commands accept `--page N --limit N`, including generic API calls. Use `--include-response --json` on a live request to retain Forgejo's `link` and `x-total-count` headers:

```bash
python3 scripts/forgejo-cli --server https://forge.example --page 1 --limit 50 \
  --include-response --json issue list --owner acme --repo app
```

Follow the `rel="next"` URL until absent. Do not assume a fixed page size: server administrators configure defaults and maximum response items.

## Scope boundaries

The generic `api` command intentionally accepts only `/api/v1/` paths. Package registries and other non-v1 endpoints require their native client or a separately reviewed HTTP workflow. First-class commands provide guardrails; the generic command provides coverage, not schema validation.
