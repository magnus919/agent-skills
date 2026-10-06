#!/usr/bin/env bash
set -euo pipefail
SCRIPT_NAME="$(basename "$0")"
BACKUP_FILE=""
CONFIG_DIR="${HEADSCALE_CONFIG_DIR:-/etc/headscale}"
DATA_DIR="${HEADSCALE_DATA_DIR:-/var/lib/headscale}"
CERTS_DIR="${HEADSCALE_CERTS_DIR:-/etc/headscale}"
FORCE=false
DRY_RUN=false
JSON_OUTPUT=false
usage() {
  cat <<EOF
Usage: $SCRIPT_NAME --backup FILE [OPTIONS]

Restore verified Headscale assets to their manifest destinations. The service is stopped during restore.

Options:
  --backup FILE      Recovery archive (required)
  --config-dir DIR   Restore config-rooted paths here
  --data-dir DIR     Restore data-rooted paths here
  --certs-dir DIR    Restore certificate-rooted paths here
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
ARGS=(restore --backup "$BACKUP_FILE" --config-dir "$CONFIG_DIR" --data-dir "$DATA_DIR" --certs-dir "$CERTS_DIR" --service "${HEADSCALE_SERVICE:-headscale}")
[[ "$FORCE" == true ]] && ARGS+=(--force)
[[ "$DRY_RUN" == true ]] && ARGS+=(--dry-run)
[[ "$JSON_OUTPUT" == true ]] && ARGS+=(--json)
[[ "${HEADSCALE_SKIP_SERVICE_CONTROL:-}" == "1" ]] && ARGS+=(--skip-service-control)
exec python3 "${SCRIPT_DIR}/hs-archive.py" "${ARGS[@]}"
