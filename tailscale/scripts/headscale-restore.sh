#!/usr/bin/env bash
set -euo pipefail
SCRIPT_NAME="$(basename "$0")"
BACKUP_FILE=""
CONFIG_DIR="${HEADSCALE_CONFIG_DIR:-}"
DATA_DIR="${HEADSCALE_DATA_DIR:-}"
CERTS_DIR="${HEADSCALE_CERTS_DIR:-}"
FORCE=false
DRY_RUN=false
JSON_OUTPUT=false
usage() {
  cat <<EOF
Usage: $SCRIPT_NAME --backup FILE [OPTIONS]

Restore verified Headscale assets to their manifest destinations. The service is stopped during restore.

Options:
  --backup FILE      Recovery archive (required)
  --config-dir DIR   Request a config-root override (rejected if it moves files)
  --data-dir DIR     Request a data-root override (rejected if it moves files)
  --certs-dir DIR    Request a certs-root override (rejected if it moves files)
  --force            Skip confirmation prompt
  --dry-run          Validate and preview without changes
  --json             Output as JSON
  --help             Show this help
EOF
}
while [[ $# -gt 0 ]]; do
  case "$1" in
    --backup) BACKUP_FILE="$2"; shift 2 ;;
    --config-dir) CONFIG_DIR="$2"; shift 2 ;;
    --data-dir) DATA_DIR="$2"; shift 2 ;;
    --certs-dir) CERTS_DIR="$2"; shift 2 ;;
    --force) FORCE=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --json) JSON_OUTPUT=true; shift ;;
    --help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done
[[ -n "$BACKUP_FILE" ]] || { echo "Error: --backup FILE is required" >&2; exit 1; }
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../skills/headscale-backup/scripts" && pwd)"
ARGS=(restore --backup "$BACKUP_FILE" --service "${HEADSCALE_SERVICE:-headscale}")
[[ -n "$CONFIG_DIR" ]] && ARGS+=(--config-dir "$CONFIG_DIR")
[[ -n "$DATA_DIR" ]] && ARGS+=(--data-dir "$DATA_DIR")
[[ -n "$CERTS_DIR" ]] && ARGS+=(--certs-dir "$CERTS_DIR")
[[ "$FORCE" == true ]] && ARGS+=(--force)
[[ "$DRY_RUN" == true ]] && ARGS+=(--dry-run)
[[ "$JSON_OUTPUT" == true ]] && ARGS+=(--json)
[[ "${HEADSCALE_SKIP_SERVICE_CONTROL:-}" == "1" ]] && ARGS+=(--skip-service-control)
exec python3 "${SCRIPT_DIR}/hs-archive.py" "${ARGS[@]}"
