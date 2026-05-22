---
name: cli-builder
description: >-
  Build or refactor CLI tools designed for AI agent consumption: non-interactive,
  flag-driven, idempotent, with --json output and --dry-run preview. Use when
  creating a new script the agent will call, adding agent-friendly flags to an
  existing tool, or debugging why an agent keeps failing to use your CLI.
license: MIT
compatibility: Requires bash, Python 3.8+, jq, and standard Unix CLI environment.
metadata:
  tags: [cli, agent-tooling, design-patterns, automation]
  sources:
    - https://x.com/ericzakariasson/status/2036762680401223946
    - https://www.scalekit.com/blog/mcp-vs-cli-use
    - https://github.com/ComposioHQ/awesome-agent-clis
    - https://ronnierocha.dev/blog/dont-build-mcps-build-cli-tools
---

# CLI Builder — Agent-Friendly Tool Design

## Overview

A CLI tool is a **contract** between your code and the agent that calls it. Every design decision is part of that contract:

| CLI Element | Contract Purpose |
|---|---|
| `--help` output | Schema — what the tool offers, what flags it accepts |
| Subcommand structure | API surface — the operations the agent can perform |
| `--json` output fields | Data contract — guaranteed keys and their types |
| Exit codes | Status signals — success, usage error, runtime failure |
| Stderr messages | Error contract — what went wrong and how to fix it |
| `--dry-run` output | Preview contract — what would happen |

An agent discovers this contract by calling `--help`. The tool needs to be **predictable, structured, and complete** — no interactive surprises, no missing examples, no silent failures.

## When to Use

- Building a new script the agent will call
- Refactoring an existing tool that causes agent friction (interactive prompts, unclear errors, non-idempotent operations)
- Adding `--json`, `--dry-run`, or `--yes` flags to an existing script
- Designing a CLI subcommand for an agent framework

**Don't use for:** One-off terminal commands the human runs interactively. The principles here optimize for machine consumption, which can make human-facing CLIs feel overly verbose.

## Build Workflow

A CLI tool is built in three phases:

```
Phase 1: Discover    →  Phase 2: Build     →  Phase 3: Verify
curl the live server →  Implement          →  Run test suite
Confirm auth        →  Wire client auth   →  Test against live
Inventory endpoints →  Write help text    →  Verify dry-run paths
Capture data shapes →  Run tests as-you-go →  Fix failures
```

## Phase 1: Plan — Before Writing Code

### Architecture: One CLI Per Service

Each API or data source gets its own CLI. Do not combine disparate services into one tool.

**Correct:** `tmdb-cli` (TMDb only), `ghost-cli` (Ghost CMS only)
**Wrong:** `media-cli` (combines TMDb + Trakt + Radarr)

Exception: services from the same vendor sharing auth (e.g. Radarr + Sonarr).

### Live-Server Discovery

Before writing any code, verify against the actual server:

```bash
# 1. Test auth against a NON-WHITELISTED endpoint
curl -s -w "\nHTTP: %{http_code}" \
  -H "X-API-Key: $KEY" \
  https://server.example.com/api/items

# 2. Try alternate auth mechanisms if that 401s
curl -s -w "\nHTTP: %{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  https://server.example.com/api/items

# 3. Capture response shapes for a read endpoint
curl -s -H "X-API-Key: $KEY" \
  https://server.example.com/api/items?limit=1 | head -c 2000
```

**Why this matters:** The health endpoint is often whitelisted and won't catch a wrong auth header. Test against a real data endpoint. Field names in the live response are the only truth — docs are often for a different version.

### Bash vs Python Decision

| Concern | Bash | Python |
|---------|------|--------|
| HTTP requests | Pipe to curl, parse with jq | `requests` library, proper error handling |
| JSON handling | jq, fragile escaping | Native `json` module |
| Auth tokens | Write/read files | Class with `_token` state |
| Multipart uploads | curl -F, painful | requests `files=` param |
| Subcommands | Case statements | argparse subparsers |
| Testing | bats, shunit2 | pytest |

**Use Python** when: the tool sends HTTP requests, manages auth state, parses JSON responses, or has 3+ subcommand levels.

**Use Bash** when: the tool wraps local binaries, does filesystem operations, or pipes commands together. Bash must have `set -euo pipefail` at the top.

## Phase 2: Build — Design Patterns

### Pattern 1: Non-Interactive by Default

No prompts mid-execution. Everything passable as a flag or environment variable.

```bash
# BAD — agent blocks forever
read -p "Are you sure? (y/n) " confirm

# GOOD — flag-driven
FORCE=${FORCE:-false}
if [[ "$1" == "--force" || "$FORCE" == "true" ]]; then
  : # proceed
fi
```

### Pattern 2: Progressive Help Discovery

Every subcommand's `--help` includes concrete examples. Agents pattern-match off examples faster than prose.

```bash
usage() {
  case "${1:-}" in
    create)
      echo "Usage: $0 create --name <name> [OPTIONS]"
      echo ""
      echo "Examples:"
      echo "  $0 create --name my-resource"
      echo "  $0 create --name my-resource --dry-run"
      echo "  $0 create --name my-resource --force"
      ;;
    *)
      echo "Commands:"
      echo "  list     List resources"
      echo "  create   Create a resource"
      echo "Run '$0 <command> --help' for command-specific options."
      ;;
  esac
}
```

### Pattern 3: `--json` for Machine-Readable Output

Support `--json` flag. Humans get text; agents get parseable data.

```bash
if [[ "$JSON_OUTPUT" == "true" ]]; then
  cat <<EOF
{"status": "deployed", "tag": "$TAG", "env": "$ENV"}
EOF
else
  echo "Deployed $TAG to $ENV"
fi
```

**Critical:** `--json` mode must suppress all non-JSON output from stdout. No "Processing..." lines, no status messages, no library banners — only the JSON payload. Use `warnings.simplefilter("ignore")` in Python or redirect library stdout to stderr.

### Pattern 4: `--dry-run` for Destructive Operations

Let the agent preview what would happen.

```bash
if [[ "$DRY_RUN" == "true" ]]; then
  echo "[dry-run] Would deploy $TAG to $ENV"
  echo "[dry-run] Would restart 3 instances"
  exit 0
fi
```

**Watch out for chained-API commands:** If your handler fetches data (e.g. station IDs) before the dry-run check, the dry-run will fail because the first API call returns empty data. Short-circuit BEFORE any data-fetching calls:

```python
def cmd_current(client, args):
    if client.dry_run:
        emit("Would query observations from station", {"dry_run": True})
        return  # ALL API calls below never execute
    stations = client.get_stations()  # real work
```

### Pattern 5: Idempotent — Guard Before Act

Running the same command twice should return success with "no-op", not an error or duplicate state.

```bash
if resource_exists "$NAME"; then
  echo "Resource '$NAME' already exists — no-op"
  exit 0
fi
create_resource "$NAME"
```

### Pattern 6: `emit()` — Single Dual-Output Helper

Abstract the JSON-vs-human branching into one function. Every command calls `emit` once.

```bash
emit() {
  if [[ "$JSON_OUTPUT" == "true" ]]; then echo "$1"
  else echo "$2"; fi
}

# Usage — one call per command, cannot forget
emit '{"status":"deployed"}' "Deployed $TAG to $ENV"
```

**Why:** Inline `if [[ "$JSON_OUTPUT" ]]` blocks are easy to forget. `emit()` is a single point of truth.

### Pattern 7: Structured Logging with Levels

```bash
log()   { [[ "$QUIET" != "true" ]] && echo "$@" || true; }
warn()  { echo "Warning: $*" >&2; }
die()   { echo "Error: $*" >&2; exit 1; }
info()  { [[ "$VERBOSE" == "true" ]] && echo "[info] $*" >&2 || true; }
```

**Critical:** `log()` must be suppressed in `--json` mode. A stray "Processing..." line before the JSON payload breaks all consumers. `emit()` handles this correctly; the danger is auxiliary `log()`/`print()` calls that don't go through `emit()`.

### Pattern 8: `--force` / `--yes` to Skip Confirmations

Safe default, bypassable for automation.

```bash
for arg in "$@"; do
  case "$arg" in
    --force|--yes|-y) FORCE=true ;;
    --dry-run|-n)     DRY_RUN=true ;;
    --json)           JSON_OUTPUT=true ;;
  esac
done
```

### Pattern 9: Consistent Subcommand Structure

Pick `resource verb` or `verb resource` and stick to it everywhere.

```
tool service list      ✓
tool service create    ✓
tool service delete    ✓
tool config list       ✓  (agent can guess this pattern)

tool list services     ✗  (verb resource — inconsistent)
tool create-service    ✗  (hyphenated verb-resource)
```

### Pattern 10: Lazy Auth — Help Works Without Credentials

Credentials checked at request time, not client creation time. `--help` and `--dry-run` work without any key.

```python
class MyClient:
    def __init__(self, api_key=""):
        self.api_key = api_key  # Accept empty key — don't check yet

    def _request(self, method, path, ...):
        if not self.api_key and not DRY_RUN:
            die("API key not found. Set MYTOOL_API_KEY in your environment.")
        if DRY_RUN:
            return {"dry_run": True}  # Safe empty response
        # Real HTTP call follows
```

This way `tool cmd --help` and `tool cmd --dry-run` never need credentials.

## Phase 3: QA — Agent Compatibility Testing

### Essential Test Suite

```bash
# 1. Syntax check
python3 -c "import py_compile; py_compile.compile('./tool.py', doraise=True)"

# 2. --help on every subcommand has examples
./tool.sh create --help | grep -qi "example" && echo "PASS"

# 3. --json output is valid parseable JSON
./tool.sh list --json 2>/dev/null | jq . >/dev/null && echo "PASS"

# 4. Missing required args → immediate error with corrective usage
result=$(./tool.sh create 2>&1 || true)
echo "$result" | grep -qi "\-\-name" && echo "PASS"

# 5. --dry-run returns meaningful preview
result=$(./tool.sh delete --name x --dry-run 2>&1 || true)
echo "$result" | grep -qi "dry-run\|would" && echo "PASS"

# 6. Errors to stderr, data to stdout
result=$(./tool.sh create 2>&1 1>/dev/null || true)
echo "$result" | grep -qi "Error" && echo "PASS: errors to stderr"

# 7. Idempotent — second call succeeds
result=$(./tool.sh create --name test 2>&1 || true)
result=$(./tool.sh create --name test 2>&1 || true)
echo "$result" | grep -qi "no-op\|already\|exists" && echo "PASS"

# 8. --dry-run on chained commands doesn't crash
result=$(./tool.sh list --dry-run 2>&1 || true)
echo "$result" | grep -qi "dry-run\|would\|preview" && echo "PASS"
```

### Live-Server Verification

The syntax tests above catch coding errors. They don't catch API mismatches. Run every read command against a real server:

```bash
# Auth verification (non-whitelisted endpoint)
curl -s -H "X-API-Key: $KEY" https://api.example.com/items?limit=1

# Read command smoke test
./tool.sh list --json > /dev/null && echo "PASS"

# Dry-run every mutating command to verify payload structure
./tool.sh create --name test --dry-run --json 2>/dev/null
```

Common bugs only found this way:
- **Wrong auth header** — health endpoint was whitelisted, you never tested a real endpoint
- **Wrong field names** — API returns `items[].id` but you wrote `entity_name`
- **Wrong content-type** — login needs form data, not JSON
- **Wrong nesting** — Swagger shows `daily` at top level, real API nests it under `forecast`

## Gotchas — The Eight Most Common Agent-CLI Bugs

These are the failures observed across every agent-built CLI:

1. **Errors on stdout** — `echo "Error"` (no `>&2`) breaks pipeline consumers. Always use `die()` which writes to stderr.

2. **No examples in `--help`** — Agents can't guess argument order from a field description. Every subcommand needs at least two concrete examples.

3. **`--json` output has auxiliary text** — A "Processing..." line before the JSON payload makes `json.load()` fail. Gate ALL output through `emit()`.

4. **No `--dry-run` for chained commands** — Handler fetches data first (e.g. station ID lookup), dry-run crashes before reaching the preview. Short-circuit BEFORE data-fetching logic.

5. **Auth header format guessed wrong** — Some APIs use `X-API-Key`, others use `Authorization: Bearer`, some use both for different auth mechanisms. Always curl a non-whitelisted endpoint first.

6. **Content-type mismatch on login** — Login/oauth endpoints usually use `application/x-www-form-urlencoded`, not JSON. Build `_form_post()` separately.

7. **Idempotency not checked** — `create` called twice creates duplicate state. Always guard creation/deletion with an existence check.

8. **Hyphenated positional arguments** — Python argparse converts `--flag-name` to `args.flag_name` for flags, but `parser.add_argument("resource-id")` stays as `getattr(args, "resource-id")`, not `args.resource_id`.

## Phase 4: Skillify — Wrap Your CLI for Agent Discovery

A CLI tool that an agent doesn't know exists is useless. The final phase creates a [compliant Agent Skill](https://agentskills.io) wrapper — a `SKILL.md` that acts as the trigger surface, letting the agent discover and reach for your CLI at the right moment.

### The Two-Layer Architecture

```
SKILL.md (this file)        CLI binary (your tool)
─────────────────────────   ─────────────────────────
Tells the agent:             Provides the agent:
• When to use this tool      • --help as schema
• What data to pass          • --json as data contract
• What the output means      • --dry-run as preview
• Known gotchas & limits     • --force as automation bypass
```

The skill **triggers** the tool. The tool **executes** the contract. Neither is complete without the other.

### Frontmatter Conventions

The `description` field is your skill's only trigger mechanism. Craft it to match the agent's vocabulary:

```yaml
---
name: tool-name              # matches the CLI binary name
description: >-
  Interact with ServiceX: search, create, and manage resources via
  the ServiceX API. Use when the user mentions ServiceX, their service
  status, or asks to look up records, create resources, or check
  service health.
license: MIT
compatibility: Requires <tool-name> CLI on PATH, API key in
  SERVICEX_API_KEY env var (or ~/.servicex.env)
metadata:
  tags: [servicex, api-client, automation]
---
```

**Rules:**
- `name` matches the CLI binary name — the agent may need to call it
- `description` lists concrete trigger keywords the user might say
- `compatibility` documents what the agent needs to have set up
- `metadata.tags` adds secondary retrieval surface

### Body Structure

The skill body does NOT duplicate the CLI's `--help`. Instead, it teaches the agent *what to use the tool FOR* and *how to interpret the results*:

```markdown
# ToolName CLI

## When to Use

- User asks "what's the status of X" or "check on Y"
- User asks to create, update, or delete resources
- User asks about unusual behavior from the service

## Setup

Credentials are read from the `SERVICEX_API_KEY` env var or
`~/.servicex.env`. If the agent gets a 401, guide the user to
set up credentials before retrying.

## Essential Commands

### list — List resources

```bash
tool-name list                        # human-readable table
tool-name list --json | jq '.[].id'   # machine-readable
```

### create — Create a resource

```bash
tool-name create --name "My Resource" --type standard
tool-name create --name "My Resource" --type standard --dry-run
```

### get — Get details by id

```bash
tool-name get --id abc123 --json
```

## Known Gotchas

- Rate limit: 100 req/min. On 429, back off and retry.
- The `status` field uses the API's raw labels (`provisioning`, `active`, `error`).
- Names are case-sensitive. `My Resource` ≠ `my resource`.
```

### What NOT to Put in the Skill Body

| Don't | Why |
|-------|-----|
| Full flag reference | That's what `--help` is for. Reference it, don't duplicate it. |
| Installation instructions | The CLI is deployed separately — the skill assumes it exists on PATH |
| API architecture details | The skill teaches *usage*, not *architecture*. Gotchas are the exception. |
| Every possible subcommand | Cover the 3-5 most common. Agents discover the rest via `--help`. |

### The Completed Architecture

```
servicex-cli/
├── servicex-cli            # The CLI binary (built with Phases 1-3)
└── SKILL.md                # The skill wrapper (built in Phase 4)

Agent opens session:
  ├── Loads all SKILL.md descriptions at startup
  ├── User says "check my servicex resources"
  ├── skill-triggered: "servicex" in user message matches description
  │     └── Agent loads skill body
  │           ├── Reads "use servicex-cli list --json"
  │           ├── Calls servicex-cli list --json
  │           └── Reads output, tells user
  │
  Deeper questions → agent reads CLI --help for specifics
```

### Skill Wrapper Template

See [references/skill-wrapper-example.md](references/skill-wrapper-example.md) for a complete worked example wrapping a hypothetical API CLI, including frontmatter, essential commands, gotchas, and auth wiring documentation.

## Agent-Readiness Checklist

- [ ] No interactive prompts (`read`, `select`, `dialog`)
- [ ] All inputs via flags or env vars
- [ ] `--help` on every subcommand with examples
- [ ] `--json` output is valid parseable JSON
- [ ] `--dry-run` on every destructive command
- [ ] `--force` / `--yes` to skip confirmations
- [ ] Idempotent: second call returns no-op, not error
- [ ] Consistent `resource verb` structure
- [ ] Errors go to stderr (`>&2` or `die()`)
- [ ] `--json` mode suppresses all non-JSON stdout
- [ ] Lazy auth: `--help` and `--dry-run` work without credentials
- [ ] Exit codes: 0=success, 1=usage error, 2=runtime failure
- [ ] Live-server verified for every read endpoint
- [ ] Dry-run verified for every chained-API path

## References

- [templates/bash-cli-scaffold.sh](templates/bash-cli-scaffold.sh) — Full bash project template with pre-wired global flags, logging helpers, and subcommand dispatch. Use as a starting point for any bash CLI.
- [references/python-api-client.md](references/python-api-client.md) — Complete Python API client pattern with lazy auth, centralized error handling, form-login support, and argparse dispatch with pre-parsed global flags. Read when building a Python CLI that wraps an HTTP API.
- [references/advanced-patterns.md](references/advanced-patterns.md) — Edge case patterns: morphological text matching, version-dependent imports, robust JSON consumption from third-party tools, dry-run short-circuit for chained APIs. Read when a specific edge case from the gotchas section bites you.
- [references/skill-wrapper-example.md](references/skill-wrapper-example.md) — Complete worked example of a skill wrapper around a hypothetical `weather-cli`, including frontmatter, essential commands, gotchas, and auth wiring. Read in Phase 4 as a template for wrapping your own CLI.
- [references/mcp-vs-cli.md](references/mcp-vs-cli.md) — Summary of the MCP-vs-CLI discourse with a decision framework. Read when debating whether to build a CLI or an MCP server for a new integration.
- [references/improvement-cycle.md](references/improvement-cycle.md) — Structured feedback schema and HALO-style prioritization for improving CLIs over time. Read after shipping your first version and collecting usage traces.
