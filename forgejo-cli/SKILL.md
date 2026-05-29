---
name: forgejo-cli
description: "CLI for Forgejo API — issues, PRs, repos, labels, webhooks, Actions runners. Dual auth (AGENT/USER)."
version: 1.1.0
tags: [forgejo, git, api, code-review]
---

# forgejo-cli

Python CLI at `~/.hermes/scripts/forgejo-cli` wrapping the Forgejo API v1.

## Auth

Two tokens stored in `~/.hermes/.env`:
- `FORGEJO_AGENT_TOKEN` — jasper bot (default)
- `FORGEJO_USER_TOKEN` — magnus user (use `--user` flag)

## Usage

```
forgejo-cli <command> [<subcommand>] [OPTIONS]

Commands:
  issue       Manage issues (list, show, create, comment, label, assign)
  pr          Manage pull requests (list, show, create, diff, review, comment, merge)
  repo        Manage repositories (list, show, create, search)
  label       Manage labels (list, create)
  hook        Manage webhooks (list, create, delete)
  user        User info and settings
  comment     Manage comments (list, create, delete)

Global flags:
  --json      Machine-readable JSON output
  --dry-run   Preview without making changes
  --agent     Use AGENT token (default)
  --user      Use USER token
  --force     Skip confirmations
  --quiet     Suppress non-essential output
```

## Common Operations

```bash
# List issues
forgejo-cli issue list --owner magnus --repo test

# Show issue
forgejo-cli issue show --owner magnus --repo test --index 3

# Add comment
forgejo-cli issue comment --owner magnus --repo test --index 3 --body "Fixed"

# Get PR diff for review
forgejo-cli pr diff --owner magnus --repo myrepo --index 1

# Submit PR review (as jasper)
forgejo-cli pr review --owner magnus --repo myrepo --index 1 --body "LGTM" --event approve

# Merge a PR
forgejo-cli pr merge --owner magnus --repo myrepo --index 3 --dry-run   # Preview first
forgejo-cli pr merge --owner magnus --repo myrepo --index 3 --force      # Execute merge

# Merge via API (when CLI returns 405 or PR has conflicts to resolve first)
# See references/pr-merge-via-api.md for full workflow

# Create a PR
forgejo-cli pr create --owner magnus --repo myrepo --title "feat: add auth" --head feat/add-auth --base main --body "Closes #42"
forgejo-cli pr create --owner magnus --repo myrepo --title "draft: WIP" --head feat/wip --base main --draft

# List repos
forgejo-cli repo list --json

# Create a repo (NOT YET IMPLEMENTED in CLI — use API directly, see references/repo-creation-via-api.md)
# Documentation says `repo create` but the method isn't coded yet

# List labels
forgejo-cli label list --owner magnus --repo test

# Get current user info
forgejo-cli user show
forgejo-cli --user user show
```

## Server Setup

The Forgejo instance runs via Docker on `phatalbert`. See `references/server-setup.md` for the docker-compose.yml, SSH port mapping details (rootless gotcha), volume strategy, and admin accounts.

## Test Suite

Test script at `~/.hermes/scripts/forgejo-cli-test.sh`. Run with:
```bash
bash ~/.hermes/scripts/forgejo-cli-test.sh
```

## Forgejo Docker Deployment

See `references/fj-deployment.md` for Forgejo-specific Docker patterns: rootless image quirks, SSH port config, entrypoint config generation, `INSTALL_LOCK` requirements, database setup, and the `***` secrets masking pitfall.

## Forgejo Actions (CI/CD)

Forgejo Actions is a CI/CD system similar to GitHub Actions. Requires both server-side config and a runner. The `forgejo-actions` skill covers runner lifecycle, step container behavior, workflow patterns, and debugging in detail.

### Enabling Actions on Forgejo

Add to `/data/gitea/conf/app.ini` inside the forgejo container:
```bash
docker exec forgejo sh -c 'printf "\n[actions]\nENABLED=true\n" >> /data/gitea/conf/app.ini'
docker restart forgejo
```

### Registering a runner

```bash
# Get registration token
curl -s "https://git.brandyapple.com/api/v1/admin/runners/registration-token" \
  -H "Authorization: token $FORGEJO_USER_TOKEN"

# Register and start on the target host
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v runner-data:/data \
  data.forgejo.org/forgejo/runner:4.0.0 \
  forgejo-runner register \
  --instance https://git.brandyapple.com \
  --token <token> --name <host>-runner \
  --labels docker:docker://node:20-bookworm --no-interactive

# Run daemon
docker run -d --name forgejo-runner --user root \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v runner-data:/data --restart unless-stopped \
  data.forgejo.org/forgejo/runner:4.0.0 \
  forgejo-runner daemon
```

### Critical runner config

After registration, edit `/data/config.yaml` in the runner volume. See the `forgejo-actions` skill for full config reference — key settings:
- `container.docker_host: automount` — required to mount host Docker socket (runner > 5.0.3). Default is `"-"` which skips mounting.
- `container.valid_volumes: ['**']` — allows volume mounts from host

### Debugging

Step output is only visible in the Forgejo web UI, not in `docker logs forgejo-runner`. See `forgejo-actions` skill for Docker events debugging patterns.

Full runner/deploy workflow details in the `forgejo-gitea` skill's "Forgejo Actions (CI/CD)" section.

## Release Workflow

The forgejo-cli does not implement `release create`. Use the Forgejo API directly for the full release lifecycle:

```bash
# 1. Tag and push
git tag -a vX.Y.Z -m "vX.Y.Z — Title"
git push origin vX.Y.Z

# 2. Write release notes and POST data to a JSON file
# (Use the JSON-file approach to avoid shell escaping issues)
cat > /tmp/release-data.json << 'ENDJSON'
{
  "tag_name": "vX.Y.Z",
  "name": "vX.Y.Z — Release Title",
  "body": "## What's New\n\nRelease notes here.\n",
  "draft": false,
  "prerelease": false
}
ENDJSON

# 3. Create the release
curl -s -X POST "https://git.brandyapple.com/api/v1/repos/{owner}/{repo}/releases" \
  -H "Authorization: token $FORGEJO_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/release-data.json

# 4. Get the release ID for any subsequent edits
curl -s "https://git.brandyapple.com/api/v1/repos/{owner}/{repo}/releases" \
  -H "Authorization: token $FORGEJO_AGENT_TOKEN" | \
  python3 -c "import sys,json; [print(f'ID: {r[\"id\"]}  Tag: {r[\"tag_name\"]}') for r in json.load(sys.stdin)]"
```

### Gotcha: `name` not `title`

Forgejo's release API uses **`name`** as the release display title, **not** `title`. If you send `"title": "vX.Y.Z — Release"`, the field is silently ignored and the tag name is used as a fallback. The correct field:

```json
{"tag_name": "vX.Y.Z", "name": "vX.Y.Z — Release Title", "body": "..."}
```

To fix a release that was created with the wrong name, PATCH by release ID:

```bash
curl -s -X PATCH "https://git.brandyapple.com/api/v1/repos/{owner}/{repo}/releases/{id}" \
  -H "Authorization: token $FORGEJO_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "vX.Y.Z — Corrected Title"}'
```

PATCH by tag (`/releases/tag/{tag}`) returns 404 — you must use the numeric release ID.

📄 **`references/release-workflow.md`** — Full worked example with rollback instructions, the complete API sequence, and recovery steps for release mistakes.

## PR Review Workflow

The `references/pr-review-workflow.md` file covers the end-to-end automated code review workflow triggered by forgejo-prs webhooks: fetching diffs, composing review bodies with complex JSON, submitting reviews via API, and handling inline comments vs summary reviews.

## Pitfalls

### Shell metacharacters in `--body` break `issue create`

The `--body` value is passed through the shell, so text containing `$`, backticks, parentheses, `&`, `|`, `;`, or unbalanced quotes causes parsing errors or silent truncation.

**Symptoms:** `Error: Unknown option: working`, `syntax error near unexpected token`, or the body gets truncated at the first special character.

**Fix:** Use the Forgejo API directly with a JSON file for complex bodies:

```bash
# Write body to file
cat > /tmp/body.json << 'ENDOFBODY'
{"title": "Issue title", "body": "Complex body with (parens) and $dollar signs"}
ENDOFBODY

# POST via API
. ~/.hermes/.env 2>/dev/null
curl -s -X POST "https://git.brandyapple.com/api/v1/repos/{owner}/{repo}/issues" \
  -H "Authorization: Bearer $FORGEJO_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/body.json
```

Or pipe from Python to avoid any shell escaping:
```bash
. ~/.hermes/.env 2>/dev/null
python3 -c "import json; body = open('/tmp/body.md').read(); print(json.dumps({'title': '...', 'body': body}))" \
  | curl -s -X POST "https://git.brandyapple.com/api/v1/repos/{owner}/{repo}/issues" \
    -H "Authorization: Bearer $FORGE...EN" \
    -H "Content-Type: application/json" \
    -d @-
```

**Best option for complex bodies: Use `execute_code` with `urllib.request`.**

This eliminates ALL shell interaction — no quoting, no temp files, no token expansion:
```python
import json, urllib.request, os

env_path = os.path.expanduser("~/.hermes/.env")
token = None
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if "FORGEJO_AGENT_TOKEN" in line and "=" in line:
            token = line.split("=", 1)[1].strip().strip('"').strip("'")

body = open("/tmp/body.md").read()
payload = json.dumps({"title": "Issue title", "body": body})

req = urllib.request.Request(
    "https://git.brandyapple.com/api/v1/repos/{owner}/{repo}/issues",
    data=payload.encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as resp:
    r = json.loads(resp.read())
    print(f"Created #{r['number']}: {r['title']}")
```

The same pattern works for PR creation — POST to `/pulls` instead of `/issues` with `head` and `base` fields. See `references/pr-creation-via-api.md`.

## Known Gaps ⚠️

| Claimed Feature | Actual Status | Workaround |
|---|---|---|
| `repo create` | Not implemented (only `list`, `show`, `search` exist) | Use raw API — see `references/repo-creation-via-api.md` |
| `repo show` | Accepts `--owner --repo` | `repo get` in code; `repo show` alias may not exist — try `--json` on `repo list` filtered by name |
| `pr merge` | Requires `--force` or `--dry-run` flag (not obvious from help output). Returns 405 when PR isn't mergeable (branch divergence, conflicts) | API-based merge — see `references/pr-merge-via-api.md` |
| `release create` | Not implemented (no release commands exist at all) | Use raw API — see `references/release-workflow.md` |
| Standalone PR comment (merged PR) | No subcommand for commenting on already-merged PRs | Use `POST /issues/{id}/comments` — see `references/pr-review-workflow.md` |

When a CLI subcommand is missing, the Forgejo REST API at `git.brandyapple.com/api/v1` is the backup. The `references/repo-creation-via-api.md` file has the exact curl incantation for repo creation, and `references/pr-creation-via-api.md` covers PR creation.
