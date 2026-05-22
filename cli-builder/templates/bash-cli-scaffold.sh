#!/usr/bin/env bash
# tool.sh — <description>
# Usage: ./tool.sh <command> [OPTIONS]
#
# Agent-friendly CLI scaffold following the cli-builder skill patterns.
# Replace <placeholders> and implement cmd_* functions for your use case.
#
# Pre-wired patterns:
#   --json       Machine-readable JSON output
#   --dry-run    Preview destructive operations
#   --force      Skip confirmations
#   --quiet/-q   Suppress non-essential output
#   --verbose/-v Additional diagnostic output to stderr
#
# Available helpers:
#   log()    stdout, suppressed in --json and --quiet modes
#   warn()   stderr, always visible
#   die()    stderr + exit 1
#   info()   stderr, visible only with --verbose
#   emit()   dual output: machine string vs human string

set -euo pipefail

# === Configuration (override via env vars) ===
TOOL_DB="${TOOL_DB:-/path/to/default.db}"
TOOL_SERVER="${TOOL_SERVER:-http://localhost:8080}"

# === State (modified by parse_args) ===
COMMAND=""
FORCE=false
DRY_RUN=false
JSON_OUTPUT=false
QUIET=false
VERBOSE=false

# === Argument Parsing (indexed approach) ===
# Uses while+shift inside the loop, NOT for arg in "$@" — shifts inside
# for-each loops don't affect the iteration variable and cause consumed
# flag values to appear as positional arguments.
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --force|--yes|-y) FORCE=true; shift ;;
      --dry-run|-n)     DRY_RUN=true; shift ;;
      --json)           JSON_OUTPUT=true; shift ;;
      --quiet|-q)       QUIET=true; shift ;;
      --verbose|-v)     VERBOSE=true; shift ;;
      --help|-h)        usage "${COMMAND:-}"; exit 0 ;;
      --)               shift; break ;;
      -*)               die "Unknown flag '$1'. Run '$0 --help' for usage." ;;
      *)
        if [[ -z "$COMMAND" ]]; then
          COMMAND="$1"
        else
          die "Unexpected argument '$1'. Run '$0 $COMMAND --help' for usage."
        fi
        shift
        ;;
    esac
  done

  [[ -z "$COMMAND" ]] && { usage; exit 1; }
}

# === Logging Helpers ===
log() {
  if [[ "$QUIET" != "true" && "$JSON_OUTPUT" != "true" ]]; then
    echo "$@"
  fi
}
warn()  { echo "Warning: $*" >&2; }
die()   { echo "Error: $*" >&2; exit 1; }
info()  { [[ "$VERBOSE" == "true" ]] && echo "[info] $*" >&2 || true; }

# === Dual Output Helper ===
# Every command calls emit() exactly once. This is the only path to stdout.
emit() {
  if [[ "$JSON_OUTPUT" == "true" ]]; then
    echo "$1"  # machine-readable JSON string
  else
    echo "$2"  # human-readable text
  fi
}

# === Usage / Help ===
usage() {
  local cmd="${1:-}"
  case "$cmd" in
    list)
      cat <<'HELP'
Usage: tool.sh list [OPTIONS]

List resources.

Options:
  --json    Output as JSON
  --quiet   Suppress non-essential output

Examples:
  tool.sh list
  tool.sh list --json | jq '.[].name'
HELP
      ;;
    create)
      cat <<'HELP'
Usage: tool.sh create --name <name> [OPTIONS]

Create a resource.

Options:
  --name    Resource name (required)
  --dry-run Preview without creating
  --force   Overwrite if exists

Examples:
  tool.sh create --name my-resource
  tool.sh create --name my-resource --dry-run
HELP
      ;;
    *)
      cat <<'HELP'
Usage: tool.sh <command> [OPTIONS]

Commands:
  list      List resources
  create    Create a resource
  delete    Delete a resource

Global flags (work in any position):
  --force, -y    Skip confirmations
  --dry-run, -n  Preview changes
  --json         Machine-readable output
  --quiet, -q    Minimal output
  --verbose, -v  Detailed output to stderr

Run 'tool.sh <command> --help' for command-specific options.
HELP
      ;;
  esac
}

# === Commands ===

cmd_list() {
  info "Listing resources..."

  if [[ "$DRY_RUN" == "true" ]]; then
    emit '{"dry_run":true,"command":"list"}' "[dry-run] Would list resources"
    return 0
  fi

  # TODO: implement list logic
  # Use log() for progress, emit() for output
  # Use $JSON_OUTPUT to decide format

  emit '{"items":[]}' "No resources found"
}

cmd_create() {
  local NAME=""

  # Parse command-specific flags
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name)  NAME="$2"; shift 2 ;;
      --name=*) NAME="${1#--name=}"; shift ;;
      --)      shift; break ;;
      *)       die "Unknown flag '$1'. Run 'tool.sh create --help' for usage." ;;
    esac
  done

  # Validate required flags
  [[ -z "$NAME" ]] && die "--name is required"

  # Sanitize input
  NAME=$(printf '%s' "$NAME" | sed -e "s/'//g" -e 's/;//g')

  # Idempotency check
  if resource_exists "$NAME"; then
    if [[ "$FORCE" != "true" ]]; then
      emit "{\"status\":\"exists\",\"name\":\"$NAME\"}" "Resource '$NAME' already exists — no-op"
      return 0
    fi
    info "Overwriting existing resource '$NAME'"
  fi

  # Dry-run
  if [[ "$DRY_RUN" == "true" ]]; then
    emit "{\"dry_run\":true,\"name\":\"$NAME\"}" "[dry-run] Would create '$NAME'"
    return 0
  fi

  # TODO: implement create logic
  create_resource "$NAME"

  emit "{\"status\":\"created\",\"name\":\"$NAME\"}" "Created '$NAME'"
}

cmd_delete() {
  local NAME=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name)  NAME="$2"; shift 2 ;;
      --name=*) NAME="${1#--name=}"; shift ;;
      --)      shift; break ;;
      *)       die "Unknown flag '$1'. Run 'tool.sh delete --help' for usage." ;;
    esac
  done

  [[ -z "$NAME" ]] && die "--name is required"

  if ! resource_exists "$NAME"; then
    emit "{\"status\":\"not_found\",\"name\":\"$NAME\"}" "Resource '$NAME' not found"
    return 1
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    emit "{\"dry_run\":true,\"name\":\"$NAME\"}" "[dry-run] Would delete '$NAME'"
    return 0
  fi

  # TODO: implement delete logic
  delete_resource "$NAME"

  emit "{\"status\":\"deleted\",\"name\":\"$NAME\"}" "Deleted '$NAME'"
}

# === Stub Functions (implement for your use case) ===
resource_exists() { return 1; }
create_resource()  { :; }
delete_resource()  { :; }

# === Main Dispatch ===
parse_args "$@"

case "$COMMAND" in
  list)   cmd_list   "$@" ;;
  create) cmd_create "$@" ;;
  delete) cmd_delete "$@" ;;
  *)      die "Unknown command '$COMMAND'" ;;
esac
