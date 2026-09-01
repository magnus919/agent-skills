---
name: cli-builder
description: >-
  Build or refactor agent-facing CLI tools with non-interactive commands, stable
  --help and --json contracts, idempotent operations, and --dry-run previews.
  Use for CLI design, agent-friction refactors, output/exit-code debugging, or
  automation safety. Do not use for GUI/TUI design, conversational tools, MCP
  server design, or general API architecture; use api-design-and-evolution for
  the latter.
license: MIT
compatibility: Requires bash, Python 3.8+, jq, and standard Unix CLI environment.
metadata:
  tags: cli, agent-tooling, design-patterns, automation
  sources: https://x.com/ericzakariasson/status/2036762680401223946, https://www.scalekit.com/blog/mcp-vs-cli-use,
    https://github.com/ComposioHQ/awesome-agent-clis, https://ronnierocha.dev/blog/dont-build-mcps-build-cli-tools
---

# CLI Builder

Treat a CLI as a contract between the tool and the agent. The contract includes
command names, `--help`, flags, output schemas, exit codes, stderr, and previews.
Keep this file as the workflow; load the linked references only when their
specialized guidance is needed.

## When to Use

- Build a new CLI that an agent will discover and call.
- Refactor prompts, ambiguous commands, parser-hostile output, or false success codes.
- Add or review `--json`, `--dry-run`, `--yes`, idempotency, or lazy authentication.

## One Workflow

### 1. Discover the real contract

Define one CLI per service (except services sharing vendor authentication). Inspect
real non-health read endpoints before coding, verify the actual authentication
header and response shape, and capture the command tree and failure cases. Do not
invent flags from API documentation alone. For HTTP clients, read
[the Python API client pattern](references/python-api-client.md).

Choose Bash for local wrappers and filesystem pipelines. Choose Python for HTTP,
JSON, authentication state, or three-level command trees.

### 2. Build a predictable surface

Use one consistent verb/resource convention. Every command should be non-interactive
and flag-driven, reject unknown flags, and provide useful subcommand help with
concrete examples. Make normal output human-readable, but support `--json` with a
stable curated schema, normalized types, deterministic ordering, and no other stdout.
Send diagnostics to stderr with truthful non-zero exit codes.

For any state change, implement `--dry-run` before data-fetching or mutation, and
require an explicit `--yes`/`--force` gate for destructive work. Guard creation,
updates, and deletion so reruns are safe. Authentication must be lazy: `--help` and
safe dry-runs work without credentials.

Use the [advanced patterns](references/advanced-patterns.md) for chained dry-runs,
third-party JSON, version-dependent behavior, and text matching. Use the
[Bash scaffold](templates/bash-cli-scaffold.sh) when a local shell wrapper is the
right fit.

### 3. Verify the contract

Run syntax checks, every command's `--help`, parse every `--json` response, check
missing arguments and unknown flags, confirm errors are on stderr, exercise dry-run
without credentials, and prove a second identical run is a no-op. Against a live
service, test a real authenticated read and dry-run each mutation. Use the
[agent-readiness checklist](references/agent-readiness-checklist.md) for the final
review.

### 4. Wrap and maintain

Keep the entry-point skill concise and put conditional detail in references. A
wrapper should explain what the CLI is for, setup, common commands, output meaning,
and gotchas, not duplicate every flag. See the
[skill-wrapper example](references/skill-wrapper-example.md). After real usage,
record failures and prioritize fixes with the [improvement cycle](references/improvement-cycle.md).

## Core Contracts

- `--help` is the discoverable schema and includes examples.
- `--json` is parseable on stdout alone; errors have stable machine-readable codes.
- `--dry-run` describes exact intended changes and performs no writes or prerequisite lookups.
- Mutations are explicitly authorized, idempotent, and report meaningful status.
- Exit status distinguishes success, usage failure, and runtime failure.

## When Not to Use

Do not use this skill for one-off interactive human commands, GUI/TUI or web UI
design, conversational agent tools, or MCP servers. Read
[the MCP-vs-CLI decision guide](references/mcp-vs-cli.md) for tool-boundary choices,
and route general API contract design to
[api-design-and-evolution](../api-design-and-evolution/SKILL.md).

## References

- [Python API client](references/python-api-client.md)
- [Advanced patterns](references/advanced-patterns.md)
- [Agent-readiness checklist](references/agent-readiness-checklist.md)
- [Skill wrapper example](references/skill-wrapper-example.md)
- [MCP vs CLI](references/mcp-vs-cli.md)
- [Improvement cycle](references/improvement-cycle.md)
- [Bash scaffold](templates/bash-cli-scaffold.sh)
