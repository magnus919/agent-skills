---
name: forgejo-cli
description: >-
  Interact with a Forgejo or Gitea self-hosted Git forge from the terminal:
  list repositories, search repos, manage issues, view pull requests, and
  get user info. Use when the user mentions Forgejo, Gitea, a self-hosted
  Git server, or asks about repos, issues, PRs, or code review.
license: MIT
compatibility: Requires FORGEJO_TOKEN env var (generate from Settings →
  Applications → Personal Access Tokens), FORGEJO_SERVER, Python 3.8+,
  and the `requests` library.
metadata:
  tags: [forgejo, gitea, git, self-hosted, code-review, api-client]
  sources:
    - https://forgejo.org/docs/next/user/oauth2/
    - https://codeberg.org/forgejo/forgejo
---

# forgejo-cli — Forgejo/Gitea Git Forge from the Terminal

Interact with a self-hosted Forgejo or Gitea server via the REST API v1. List repositories, search, manage issues, and view pull requests.

## Setup

1. Generate a personal access token: Settings → Applications → Create Personal Access Token
2. Set environment variables:

```bash
export FORGEJO_SERVER="https://git.your-domain.com"
export FORGEJO_TOKEN="your-personal-access-token"
```

`--help` and `--dry-run` work without credentials.

## Essential Commands

### me — Current user profile

```bash
forgejo-cli me                           # your account info
forgejo-cli me --json                    # machine-readable
```

### repos — List your repositories

```bash
forgejo-cli repos                        # all your repos
forgejo-cli repos --limit 100            # more results
forgejo-cli repos --json                 # machine-readable
```

### search — Search repositories

```bash
forgejo-cli search --query "cli"                  # by name/description
forgejo-cli search --query "infra" --limit 5      # top 5
forgejo-cli search --query "docs" --json          # machine-readable
```

### issues — List issues in a repo

```bash
forgejo-cli issues --repo owner/repo              # open issues
forgejo-cli issues --repo owner/repo --state closed
forgejo-cli issues --repo owner/repo --state all --limit 50
forgejo-cli issues --repo owner/repo --json
```

Forgejo's issues endpoint also returns pull requests — the CLI filters them out automatically.

### view — View an issue or PR

```bash
forgejo-cli view --repo owner/repo --issue 42       # full details
forgejo-cli view --repo owner/repo --issue 42 --json
```

Shows: number, title, state, author, body, labels, milestone, assignee, timestamps, and whether it's a pull request.

### prs — List pull requests

```bash
forgejo-cli prs --repo owner/repo                  # open PRs
forgejo-cli prs --repo owner/repo --state merged   # merged PRs
forgejo-cli prs --repo owner/repo --state all       # all PRs
forgejo-cli prs --repo owner/repo --json
```

Shows: number, title, state, author, head and base branches, and merge status.

## Global Flags

All flags work in any position:

```bash
forgejo-cli --json issues --repo owner/repo          # flag before subcommand
forgejo-cli issues --repo owner/repo --json          # flag after subcommand
forgejo-cli --dry-run issues --repo owner/repo       # preview
forgejo-cli --quiet repos                            # suppress non-essential output
```

## Known Gotchas

- **Repo format** must be `owner/repo` (e.g. `--repo myorg/my-project`). Forgejo does not accept bare repo names.
- **Issues and PRs share an endpoint** — The Forgejo API returns pull requests mixed into the issues list. The CLI filters PRs out when listing issues. To view PRs, use `prs`.
- **Pagination** — The Forgejo API paginates with `page` and `limit` params. The CLI sets reasonable defaults but doesn't auto-page. Use `--limit` to control results.
- **Token permissions** — Personal access tokens are scoped per-repo or globally. A 403 on a specific repo usually means the token doesn't have access to it.
- **Authorization header format** — Forgejo/Gitea uses `Authorization: token YOUR_TOKEN`, not `Bearer`. The CLI handles this automatically.

## References

- [scripts/forgejo-cli](scripts/forgejo-cli) — The CLI binary. Built following the cli-builder patterns: non-interactive, `--json`, `--dry-run`, `--quiet`, `--verbose`, dual-output via `emit()`, lazy auth, structured logging.
- [Forgejo REST API docs](https://forgejo.org/docs/next/user/api-usage/) — Official API reference.
