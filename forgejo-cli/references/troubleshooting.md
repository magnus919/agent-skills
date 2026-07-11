# Troubleshooting Forgejo API calls

| Symptom | Check | Safe next action |
| --- | --- | --- |
| `No API token available` | Required environment variable is absent | Export the intended token or provide a deliberate `Authorization` header for the one request |
| 401 | Token type, expiry, server URL, or authentication scheme | Run a read-only `user show`; do not retry mutations blindly |
| 403 | Token scope, repository access, or server policy | Inspect the target endpoint's required scope and permissions; use a narrower correctly scoped token rather than escalating indiscriminately |
| 404 | Owner/repo/path or server-version mismatch | Check `/api/v1/version` and the server's Swagger document before changing the path |
| 422 | Valid route but invalid payload | Compare the complete JSON body against the live Swagger schema; dry-run first-class calls to inspect generated fields |
| Missing list results | Pagination | Add `--page`, `--limit`, and `--include-response`; follow the `link` header |
| Connection error | DNS, TLS, proxy, or server availability | Verify the exact `--server` URL with a harmless version request; do not expose tokens in diagnostic output |

Use `--verbose` only to inspect method and URL. It deliberately does not print tokens or request bodies. For mutation failures, retain the dry-run JSON plan and the status/message, but redact credentials before sharing either.
