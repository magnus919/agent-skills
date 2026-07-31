# CLI Command Reference

Complete reference for the `binary` CLI — every command, its flags, output
format, and exit codes. Load this when you need exact flag syntax, want to
understand what a command returns, or need to look up an exit code.

## Global Flags

These flags apply to every command and are registered on the root parser:

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--json` | flag | off | Emit machine-readable JSON output with the standard envelope |
| `--quiet` | flag | off | Suppress progress messages and non-error diagnostics on stderr |
| `--limit` | int | 100 | Maximum number of results (positive integer, max 1000) |
| `--timeout` | int | 300 | Operation timeout in seconds (positive integer) |
| `--max-output-size` | int | 67108864 | Maximum output size in bytes (default 64MB, max 256MB) |
| `--max-memory` | int | 0 | Maximum memory in bytes (0 = no explicit limit) |

### Global Flag Behavior

- `--json` produces a standard envelope on stdout: `schema_version`, `command`,
  `generated_at`, `duration_ms`, `success`, `partial`, `warnings`,
  `diagnostics`, `provenance`, `data`. Without `--json`, output is
  human-readable text.
- `--quiet` suppresses stderr diagnostics. Only fatal errors appear on stderr.
  Exit codes are unchanged.
- `--limit` clamps to the range [1, 1000]. Values outside this range produce a
  diagnostic but use the clamped value.
- `--timeout` clamps to the range [1, 3600]. Values <= 0 are rejected with exit
  code 2.
- `--max-output-size` triggers truncation with a diagnostic when output exceeds
  the limit.

## JSON Envelope

Every `--json` response follows this structure:

```json
{
  "schema_version": "1.0.0",
  "command": "functions",
  "generated_at": "2026-07-30T12:00:00Z",
  "duration_ms": 183,
  "success": true,
  "partial": false,
  "warnings": [],
  "diagnostics": [],
  "provenance": {
    "cli_version": "0.1.0",
    "schema_version": "1.0.0",
    "adapter": "fake",
    "adapter_version": "0.1.0",
    "backend": "FakeAdapter",
    "backend_version": "0.1.0",
    "project_id": "<uuid>",
    "binary_id": "<uuid>",
    "binary_sha256": "<hex>",
    "analysis_profile": "standard",
    "platform": "arm64",
    "architecture": "x86:LE:64:default"
  },
  "data": {}
}
```

### Envelope Field Semantics

- `success: true, partial: false` — Complete success.
- `success: true, partial: true` — Bounded success; some analyzers failed or
  timed out. Results are valid but incomplete. Review `diagnostics`.
- `success: false, partial: true` — Timeout or partial failure. Some results
  may be present.
- `success: false, partial: false` — Hard failure. No usable results.

### Structured Addresses

All addresses use a canonical structured object:

```json
{
  "space": "ram",
  "offset": "0x4018d0",
  "display": "0x4018d0",
  "file_offset": 6352
}
```

## Exit Codes

| Code | Name | When |
|------|------|------|
| 0 | SUCCESS | Success or explicit valid partial result |
| 1 | GENERIC_ERROR | Generic failure |
| 2 | INVALID_ARGS | Invalid arguments, missing required args, invalid flag values |
| 3 | DEPENDENCY_MISSING | Missing or incompatible dependency (Java, Ghidra, PyGhidra) |
| 4 | INVALID_CONFIG | Invalid configuration (corrupted manifest, bad settings) |
| 5 | UNSUPPORTED_FORMAT | Unsupported binary format or architecture |
| 6 | PROJECT_NOT_FOUND | Project name or UUID not found |
| 7 | BINARY_NOT_FOUND | No binary imported into the project |
| 8 | AMBIGUOUS_SELECTOR | Selector resolved to multiple entities |
| 9 | ENTITY_NOT_FOUND | Specific entity (function, address) not found |
| 10 | IMPORT_FAILED | Import operation failed |
| 11 | ANALYSIS_FAILED | Analysis operation failed (hard failure) |
| 12 | OPERATION_TIMEOUT | Timeout or cancellation |
| 13 | BACKEND_FAILURE | Backend or internal failure (unexpected) |

## Command Reference

### Environment & Setup

#### `binary doctor`

Check dependency health. Reports Java, Ghidra, and PyGhidra status.

```
binary doctor [--json] [--quiet] [--require-ready]
```

| Flag | Description |
|------|-------------|
| `--require-ready` | Exit code 3 if any component is missing (for scripting) |

**Exit codes:** 0 (all healthy), 3 (dependency missing)

**Output:** `data.components[]` with `name`, `status`, `message`, `remediation`
for each component. Each `diagnostics[]` entry has `severity`, `component`,
`message`, `remediation`.

#### `binary bootstrap`

Discover and install dependencies (PyGhidra only — Java and Ghidra must be
installed manually).

```
binary bootstrap [--json] [--quiet] (--plan | --apply)
```

| Flag | Description |
|------|-------------|
| `--plan` | Show install targets without making changes |
| `--apply` | Download and install missing dependencies |

**Exit codes (--plan):** 0 (all present), 3 (some missing)
**Exit codes (--apply):** 0 (all installed), 1 (partial failure)

**`--plan` output:** `data.components[]` with `name`, `status` (`missing` or
`present`), `action` (`install` or `skip`), `source`.

**`--apply` output:** `data.components[]` with `name`, `status` (`installed` or
`failed`). On failure, `success: false`, `partial: true`, and failed components
have a `reason` field.

#### `binary version`

Report all component versions.

```
binary version [--json] [--quiet]
```

**Exit code:** 0

**Output:** `data` containing `cli_version`, `schema_version`,
`workspace_version`, `adapter` (`name`, `version`), `backend` (`name`,
`version`), `platform`.

### Project Management

#### `binary project create`

Create a new analysis workspace.

```
binary project create <name> [--json] [--quiet] [--dry-run]
```

| Flag | Description |
|------|-------------|
| `--dry-run` | Report planned creation without creating files |

**Exit codes:** 0 (created), 1 (duplicate name)

**Output:** `data` with `id` (UUID), `name`, `state` (`CREATED`), `created_at`,
`directory`.

#### `binary project list`

List projects with pagination.

```
binary project list [--json] [--quiet] [--limit N] [--cursor <cursor>]
```

**Exit code:** 0

**Output:** `data.items[]` with each project's `id`, `name`, `state`,
`created_at`, `binary_count`. `data.total`, `data.next_cursor`, `data.has_more`.

#### `binary project status`

Show full project state and metadata.

```
binary project status <project> [--json] [--quiet]
```

**Exit codes:** 0 (found), 6 (not found)

**Output:** `data` with `state` (ProjectState enum), `binary_count`,
`created_at`, `updated_at`, `is_stale`, `lock` (holder string or null).

#### `binary project clean`

Reset a FAILED project to CREATED.

```
binary project clean <project> [--json] [--quiet] [--yes] [--force]
```

| Flag | Description |
|------|-------------|
| `--yes` | Skip confirmation prompt |
| `--force` | Same as `--yes` |

**Exit codes:** 0 (cleaned), non-zero (denied, or project not in FAILED state)

**Note:** Only works on FAILED projects. Other states are rejected.

#### `binary project remove`

Delete an entire project workspace.

```
binary project remove <project> [--json] [--quiet] [--yes] [--force] [--dry-run]
```

| Flag | Description |
|------|-------------|
| `--yes` | Skip confirmation prompt |
| `--force` | Same as `--yes` |
| `--dry-run` | Report deletion plan without deleting |

**Exit codes:** 0 (removed), non-zero (denied or not found)

#### `binary project migrate`

Upgrade project workspace format.

```
binary project migrate <project> [--json] [--quiet] (--plan | --apply) [--dry-run]
```

| Flag | Description |
|------|-------------|
| `--plan` | Show migration path without changes |
| `--apply` | Perform the migration |
| `--dry-run` | Preview migration (alias for `--plan`) |

**Exit codes:** 0 (migrated or plan shown), non-zero (locked or incompatible)

### Import & Analysis

#### `binary import`

Import a binary into a project.

```
binary import <path> --project <project> [--json] [--quiet] [--reference]
```

| Flag | Description |
|------|-------------|
| `--project` | Project name or UUID (required) |
| `--reference` | Use reference mode (track source path, do not copy) |

**Exit codes:** 0 (imported), 5 (unsupported format), 6 (project not found), 10
(import failed)

**Output:** `data` with `binary_id` (UUID), `binary_sha256` (hex),
`binary_path`, `format`, `import_mode` ("copy" or "reference"), `size_bytes`.

Copy mode (default) copies the binary into the project's `samples/` directory.
Reference mode records the source path — faster but the project becomes STALE
if the source changes.

#### `binary analyze`

Run analysis on an imported binary.

```
binary analyze --project <project> [--json] [--quiet] [--profile PROFILE] [--timeout N]
```

| Flag | Description |
|------|-------------|
| `--project` | Project name or UUID (required) |
| `--profile` | Analysis profile: `standard` (default), `quick`, or `deep` |

**Exit codes:** 0 (analyzed), 7 (no binary), 11 (analysis failed), 12 (timeout)

**Output:** `provenance.project_state` reflecting the state transition.
`diagnostics` includes lock acquisition/release records.

### Structural Queries

All structural queries support `--limit` and `--cursor` for pagination.

#### `binary metadata`

Show canonical metadata for the imported binary.

```
binary metadata --project <project> [--json] [--quiet]
```

**Exit codes:** 0, 6 (project not found), 7 (no binary)

**Output:** `data` with `format`, `architecture`, `endianness`, `size_bytes`,
`entry_point` (address object or null). No backend-specific keys at root of
`data`.

#### `binary sections`

List sections in the binary.

```
binary sections --project <project> [--json] [--quiet] [--limit N] [--cursor C]
```

**Output:** `data.items[]` with `name`, `address`, `virtual_size`, `raw_size`,
`flags` (array of "r"/"w"/"x"), `entropy` (float or null).

#### `binary entrypoints`

List entry points with confidence scoring.

```
binary entrypoints --project <project> [--json] [--quiet] [--limit N] [--cursor C]
```

**Output:** `data.items[]` with `address`, `kind` ("program"/"library"/"boot"/
"firmware"/"unknown"), `confidence` ("HIGH"/"MEDIUM"/"LOW"/"UNKNOWN"), `name`.

#### `binary imports`

List imported symbols with resolution status.

```
binary imports --project <project> [--json] [--quiet] [--limit N] [--cursor C]
```

**Output:** `data.items[]` with `module`, `symbol`, `address` (or null),
`resolution` ("RESOLVED"/"PARTIAL"/"UNRESOLVED"), `ordinal` (or null).

#### `binary exports`

List exported symbols.

```
binary exports --project <project> [--json] [--quiet] [--limit N] [--cursor C]
```

**Output:** `data.items[]` with `name`, `address`, `ordinal` (or null),
`forwarder` (or null), `kind` ("function" or "data").

#### `binary symbols`

List symbols with source and scope.

```
binary symbols --project <project> [--json] [--quiet] [--limit N] [--cursor C]
```

**Output:** `data.items[]` with `name`, `address`, `source` (FunctionNameSource
enum), `scope` ("global"/"local"/"unknown").

#### `binary strings`

List decoded strings.

```
binary strings --project <project> [--json] [--quiet] [--limit N] [--cursor C]
               [--min-length N] [--contains PATTERN]
```

| Flag | Description |
|------|-------------|
| `--min-length` | Minimum string length (default: 4) |
| `--contains` | Substring filter (case-sensitive) |

**Output:** `data.items[]` with `text`, `encoding` ("ASCII"/"UTF-8"/"UTF-16"),
`address`, `length`. `data.applied_filters` lists active filters.

#### `binary functions`

List functions.

```
binary functions --project <project> [--json] [--quiet] [--limit N] [--cursor C]
                 [--no-exclude-external] [--no-exclude-thunks]
```

| Flag | Description |
|------|-------------|
| `--no-exclude-external` | Include external (imported) functions |
| `--no-exclude-thunks` | Include thunk functions |

**Output:** `data.items[]` with `name`, `address`, `size_bytes`, `confidence`
("HIGH"/"MEDIUM"/"LOW"/"UNKNOWN"), `name_source` (FunctionNameSource enum).
External and thunk functions are excluded by default; use the flags to include
them. `data.applied_filters` documents active exclusions.

### Focused Analysis

#### `binary decompile`

Decompile a function to reconstructed pseudocode.

```
binary decompile --project <project> <function-selector> [--json] [--quiet] [--timeout N]
```

**Selector format:** `function:<name>` or `function:<address>`

**Exit codes:** 0 (decompiled), 8 (ambiguous selector), 9 (function not found),
12 (timeout)

**Output:** `data.pseudocode` (string), `data.address_map` (line-to-address
mapping), `data.diagnostics[]`. The output is labeled as reconstructed
pseudocode, not original source.

#### `binary disassemble`

Disassemble instructions in a function or address range.

```
binary disassemble --project <project> <target> [--json] [--quiet] [--limit N]
```

**Target formats:**
- `function:<name>` or `function:<address>` — a function
- `<start>..<end>` — an explicit address range

**Exit codes:** 0, 2 (no target specified), 9 (unmapped range)

**Output:** `data.instructions[]` with `mnemonic`, `operands`, `bytes` (hex
string), `address`. Partially mapped ranges return `partial: true` with a
diagnostic about the unmapped gap.

#### `binary bytes`

Read raw bytes at an address.

```
binary bytes --project <project> <address> <length> [--json] [--quiet]
```

**Exit codes:** 0, 2 (non-positive length), 9 (unmapped address)

**Output:** `data.hex`, `data.base64`, `data.address`, `data.length`. Requests
extending past segment boundaries return truncated results with `partial: true`.

#### `binary xrefs`

List cross-references to/from an entity.

```
binary xrefs --project <project> <entity-selector> [--json] [--quiet] [--limit N] [--cursor C]
```

**Selector format:** `function:<name>`, `function:<address>`, or raw address.

**Exit codes:** 0, 9 (entity not found)

**Output:** `data.references[]` with `from`, `to` (address objects), `kind`
(ReferenceKind enum: CALL/JUMP/READ/WRITE/DATA/IMPORT/EXPORT/INDIRECT/UNKNOWN),
`confidence`.

#### `binary callers`

List functions that call the target.

```
binary callers --project <project> <function-selector> [--json] [--quiet] [--limit N] [--cursor C]
```

**Exit codes:** 0, 8 (ambiguous), 9 (not found)

**Output:** `data.callers[]` — each a function object with name and address.

#### `binary callees`

List functions called by the target.

```
binary callees --project <project> <function-selector> [--json] [--quiet] [--limit N] [--cursor C]
```

**Exit codes:** 0, 8 (ambiguous), 9 (not found)

**Output:** `data.callees[]` — each a function object with name and address.

#### `binary callgraph`

Build a bounded call graph.

```
binary callgraph --project <project> <function-selector> [--json] [--quiet] [--depth N]
```

| Flag | Description |
|------|-------------|
| `--depth` | Maximum depth (default: 3, max: 10) |

**Exit codes:** 0, 2 (invalid depth), 8 (ambiguous selector), 9 (not found)

**Output:** `data.graph` with `nodes[]` (functions) and `edges[]` (call
relationships). Root node is the target function. Depth limit is disclosed.

#### `binary search`

Search for entities by name or pattern.

```
binary search --project <project> <query> [--json] [--quiet] [--limit N] [--cursor C]
```

**Exit codes:** 0

**Output:** `data.results[]` — matching entities. `data.next_page_token` for
cursor-based pagination.

#### `binary trace`

Find call paths between two entities.

```
binary trace --project <project> --from <source> --to <target> [--json] [--quiet] [--depth N]
```

| Flag | Description |
|------|-------------|
| `--from` | Source entity selector (required) |
| `--to` | Target entity selector (required) |
| `--depth` | Maximum path depth (default: 5) |

**Exit codes:** 0

**Output:** `data.paths[]` — each path is an ordered sequence of entities. Empty
array if no path found.

### Security Analysis

#### `binary triage`

Run automated triage analysis.

```
binary triage --project <project> [--json] [--quiet] [--profile PROFILE] [--limit N]
```

**Exit codes:** 0 (complete or partial), 11 (analysis failed)

**Output:** Three separate categories:
- `data.observations[]` — deterministic facts (no `confidence` field)
- `data.heuristics[]` — rule-derived interpretations with `confidence`
- `data.unknowns[]` — unresolved questions with `address` and `question`

No free-form narrative or agent conclusions. Complete `provenance` block.

#### `binary diagnostics`

List all persistent diagnostics from the project lifecycle.

```
binary diagnostics --project <project> [--json] [--quiet] [--limit N] [--cursor C]
```

**Exit codes:** 0, 6 (project not found)

**Output:** `data.items[]` with `severity` (INFO/WARNING/ERROR), `category`,
`message`, `recoverable` (boolean), `timestamp`.

#### `binary suspicious-apis`

Detect suspicious API usage.

```
binary suspicious-apis --project <project> [--json] [--quiet] [--limit N]
```

**Exit codes:** 0, 6 (project not found), 7 (no binary)

**Output:** `data.matches[]` with `api_name`, `risk_score` (numeric),
`confidence`, `rule_id`. `data.rules_applied[]` lists evaluated rule IDs.

#### `binary capability-map`

Suggest functional capabilities.

```
binary capability-map --project <project> [--json] [--quiet] [--limit N]
```

**Exit codes:** 0, 6 (project not found), 7 (no binary)

**Output:** `data.capabilities[]` with `name` (e.g., "cryptography",
"networking"), `confidence`, `evidence[]` — each evidence item references a
concrete source (import API, string, section pattern).

### Reporting

#### `binary export-report`

Export an analysis report.

```
binary export-report --project <project> [--json] [--quiet]
                     [--type {triage,focused,project}]
                     [--format {markdown,json,html,pdf}]
                     [--selector SELECTOR] [--profile PROFILE] [--output PATH]
```

| Flag | Description |
|------|-------------|
| `--type` | Report type: `triage` (default), `focused`, or `project` |
| `--format` | Output format: `markdown` (default), `json`, `html`, or `pdf` |
| `--selector` | Entity selector for `focused` reports (required for that type) |
| `--profile` | Analysis profile to reference in methodology |
| `--output` | Custom output path (must be within project directory) |

**Exit codes:** 0, 6 (project not found)

Markdown and JSON are authoritative formats. HTML and PDF are optional
renderings — if a rendering dependency is unavailable, the command exits 0 with
a warning and the canonical Markdown path.

#### `binary audit`

List append-only audit events.

```
binary audit --project <project> [--json] [--quiet] [--limit N] [--cursor C]
```

**Exit codes:** 0, 6 (project not found)

**Output:** `data.items[]` with `command`, `args`, `result` (SUCCESS/PARTIAL/
FAILED/CANCELLED/REFUSED), `duration_ms`, `timestamp`.

### Worker

#### `binary worker`

Manage the optional local worker daemon.

```
binary worker {start,stop,status} [--json] [--quiet]
```

| Subcommand | Description |
|------------|-------------|
| `start` | Start the worker (idempotent — reports "already running" if running) |
| `stop` | Stop the worker (idempotent — reports "not running" if stopped) |
| `status` | Report `running` (with PID and uptime) or `stopped` |

The worker is optional. All commands function without it (one-shot mode).

## Pagination

Cursor-based pagination is the standard for list commands. The pattern:

1. First call: `binary <command> --project <proj> --limit 50 --json`
2. Read `data.next_cursor` and `data.has_more` from the response
3. Next page: `binary <command> --project <proj> --limit 50 --cursor <next_cursor> --json`
4. Final page: `data.next_cursor: null`, `data.has_more: false`

**Cursor scoping:** Cursors are scoped to the combination of command, project,
filters, and sort order. Using a cursor from a different filter set returns an
error or empty result.

## Selector Syntax

Entity selectors identify specific entities for focused analysis commands.

| Format | Example | Resolves To |
|--------|---------|-------------|
| `function:<name>` | `function:main` | Function by name |
| `function:<address>` | `function:0x401000` | Function by entry address |
| `<address>` | `0x402080` | Address (for xrefs, bytes) |
| `<start>..<end>` | `0x401000..0x401200` | Address range (for disassemble) |

**Disambiguation:** If a function selector matches multiple functions (e.g.,
common names or substring matches), the CLI returns exit code 8
(AMBIGUOUS_SELECTOR) with a list of candidates. Use a more specific selector
(full name or address) to disambiguate.
