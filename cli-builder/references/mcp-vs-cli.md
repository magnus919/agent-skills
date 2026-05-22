# MCP vs CLI — Discourse Summary & Decision Framework

## The Core Argument

CLI-first design for agent tools vs MCP servers — what the debate is actually about, not the noise.

### Key Sources

| Source | Key Claim |
|--------|-----------|
| **Eric Zakariasson** — "Building CLIs for Agents" ([X thread](https://x.com/ericzakariasson/status/2036762680401223946)) | CLIs designed for agents need `--json`, `--dry-run`, examples in help, and non-interactive mode. Most CLIs assume a human. |
| **ScaleKit Benchmarks** ([scalekit.com/blog/mcp-vs-cli-use](https://www.scalekit.com/blog/mcp-vs-cli-use)) | 9-32× token savings for CLI over MCP on GitHub automation. 100% reliability (CLI) vs 72% (MCP). The gap is schema injection — 43 tool definitions per turn, agent uses 1-2. |
| **Ronnie Rocha** — "Don't Build MCPs, Build CLI Tools" ([ronnierocha.dev](https://ronnierocha.dev/blog/dont-build-mcps-build-cli-tools/)) | MCP was designed for sandboxed agents (IDE plugins, web assistants). Terminal-native agents already have access — they don't need a bridge. MCP tax: context bloat, no composability, no pipes, serialized overhead. |
| **Garry Tan** ([X](https://x.com/garrytan/status/2031910564344262988)) | "MCP sucks honestly. It eats too much context window… I vibe coded a CLI wrapper for Playwright tonight in 30 minutes… worked 100x better." |
| **Peter Steinberger (steipete)** — MCPorter ([github.com/steipete/mcporter](https://github.com/steipete/mcporter)) | Converts MCP tools to CLI commands. Describes MCP as "a crutch" for environments without terminal access. |

## Token Cost Breakdown

The ScaleKit benchmark reveals why CLI wins for agent consumption:

| Metric | CLI | MCP |
|--------|-----|-----|
| Schema overhead per turn | 0 tokens (agent calls `--help` on demand) | 500-2000 tokens (full tool definitions injected every turn) |
| Output shape | Agent requests exactly what it needs via flags | Full JSON-RPC response, unfiltered |
| Composition | Piped through `jq`, `grep`, `mlr` | Atomic calls only |
| Failure mode | Exit code + stderr message | ConnectTimeout to MCP endpoint (36% of MCP failures) |

The gap grows with tool count. A CLI aggregate (one binary with subcommands) costs ~100 tokens in `--help` output. An MCP aggregate costs ~43 tool schemas × ~500 tokens each = ~21,500 tokens per turn.

## Decision Framework

| Situation | Default | Rationale |
|-----------|---------|-----------|
| Agent already has a terminal | **CLI** | No bridge needed. Agent pipes output directly. |
| Single-user, personal/homelab | **CLI** | Simpler to build and debug. No server to maintain. |
| Multi-tenant, end-user OAuth | **MCP** | Auth delegation and credential management handled by the protocol. |
| Token-sensitive at scale | **CLI** | 9-32× cheaper per operation. |
| Need composability (pipes) | **CLI** | `cmd | grep | jq` is zero-cost composition. |
| Need dynamic resource discovery | **MCP** | MCP's `list_resources` + `subscribe` provides real-time schema discovery. |
| Enterprise audit/traceability | **MCP** | JSON-RPC has structured request/response logging at the protocol level. |
| Internal bespoke API | **Either** — CLI with `--json` is simpler; MCP if governed access is required |

**Bottom line:** CLI is the default for most agent-facing tools. MCP wins for governed multi-tenant deployments where credential management and audit trails are the primary value. In practice, many deployments end up hybrid: CLI for high-frequency known tools, MCP for sandboxed or governed integrations.
