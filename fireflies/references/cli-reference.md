# CLI Reference

Run `scripts/fireflies --help` for the authoritative interface. Global flags work before or after
subcommands: `--json`, `--api-key`, `--endpoint`, `--timeout`, `--dry-run`, `--quiet`, and `--verbose`.
`--json` writes one JSON document to stdout; diagnostics are stderr-only.

## Commands

| Command | Purpose |
|---|---|
| `query --document DOC [--variables JSON|--variables-file PATH]` | Generic read-only GraphQL |
| `mutation --document DOC ... --confirm` | Generic mutation |
| `transcripts list|get|delete` | Search, inspect, or delete meetings |
| `users`, `contacts`, `channels`, `groups`, `bites`, `apps` | Workspace/content reads; `users set-role --user-id ID --role admin|user` assigns roles |
| `analytics`, `meetings active`, `live-action-items` | Analytics and live data |
| `meetings rename|privacy|state|share|revoke-share|update-channel` | Meeting mutations; `share` accepts `--expiry-days` |
| `bites create`, `live add|add-to|soundbite`, `audio upload|create-upload|confirm-upload` | Creation/upload mutations; `live add` creates a live action item, `add-to` joins a live meeting by link, `soundbite` clips one; `audio create-upload`/`confirm-upload` are the two-phase file upload |
| `askfred threads|get|create|continue|delete` | AskFred workflow |
| `audit-events`, `rule-executions` | Enterprise/admin queries |
| `webhook verify` | Local signature check, no network |
| `schema introspect` | Explicit GraphQL introspection |

## Examples

```bash
scripts/fireflies query --document 'query { user { name } }' --json
scripts/fireflies transcripts list --from-date 2026-01-01 --to-date 2026-01-31 --limit 50 --json
scripts/fireflies mutation --document 'mutation X { ... }' --confirm --dry-run --json
scripts/fireflies webhook verify --secret "$WEBHOOK_SECRET" --signature sha256=... --body payload.json --json
```

Variables must be a JSON object, inline or from a file. `--dry-run` returns the exact endpoint and
payload and does not need an API key. Exit codes: 2 usage/input, 3 configuration, 4 transport/HTTP,
5 GraphQL errors, 6 confirmation refused.
