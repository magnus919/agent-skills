# Forgejo CLI v2 — safe repository automation

Manage a Forgejo server from the terminal without hand-written `curl` or accidental mutations. It covers daily repository work—issues, pull requests, repositories, contents, metadata, webhooks, and settings—and has a guarded API escape hatch for the rest.

## Why Install This Skill

The CLI gives agents one predictable safety contract: JSON is machine-readable, diagnostics stay off stdout, mutations require confirmation, and dry runs never need a token or network access. For version-specific features such as Actions runners and variables, packages, organizations, teams, admin APIs, notifications, and permissions, use the generic API command with your server's Swagger schema.

It deliberately does not try to duplicate every API endpoint. Instead, it offers guarded first-class commands for common repository work and a generic client for the rest. The references explain when to use each, how to select a compatible schema, and how to handle pagination and token scopes.

## What You Get

| Contents | Purpose |
| --- | --- |
| `scripts/forgejo-cli` | Argparse Forgejo API v1 client |
| `references/command-reference.md` | Endpoint and payload guide |
| `references/api-usage.md` | Authentication, pagination, versioning, and schema-discovery procedure |
| `references/endpoint-routing.md` | Decision guide for first-class commands versus generic API calls |
| `references/troubleshooting.md` | Safe diagnosis of API and transport failures |
| `V2-SPEC.md` | v2 acceptance criteria |
| `tests/` | Offline stdlib contract tests |

## Quick Start

Set `FORGEJO_AGENT_TOKEN` (default) or `FORGEJO_USER_TOKEN`, then run:

```bash
python3 scripts/forgejo-cli --dry-run --json repo create --name demo --private
python3 scripts/forgejo-cli --server https://forge.example api --method GET --path /api/v1/user --json
python3 scripts/forgejo-cli --server https://forge.example --page 1 --limit 50 --include-response issue list --owner acme --repo app --json
```

## Triggers

- Managing Forgejo/Gitea issues, PRs, repos, file contents, releases, or hooks.
- Calling a version-specific `/api/v1/` endpoint safely.
- Previewing a Forgejo mutation.

## Requirements

Python 3.8+ and `requests` for live API calls. `--help` and `--dry-run` need no token or dependency. Set `FORGEJO_AGENT_TOKEN` or `FORGEJO_USER_TOKEN` for token authentication. A deliberate `Authorization` header supports other documented schemes, but avoid putting secrets directly in shell history. Consult your Forgejo server's `/api/swagger` or `/swagger.v1.json` for exact schemas.
