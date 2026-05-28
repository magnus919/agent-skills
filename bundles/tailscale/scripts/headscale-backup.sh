#!/usr/bin/env bash
set -euo pipefail

# headscale-backup.sh — Full backup of Headscale
SCRIPT_NAME="$(basename "$0")"
JSON_OUTPUT=false
DRY_RUN=false
OUTPUT_DIR="${HOME}/backups/headscale"
CONFIG_DIR="/etc/headscale"
DATA_DIR="/var/lib/headscale"

usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Backup Headscale configuration and database.

Options:
  --output-dir DIR  Backup destination (default: ~/backups/headscale)
  --config-dir DIR  Headscale config directory (default: /etc/headscale)
  --data-dir DIR    Headscale data directory (default: /var/lib/headscale)
  --dry-run         Preview what would be backed up
  --json            Output as JSON
  --help            Show this help

Examples:
  $SCRIPT_NAME
  $SCRIPT_NAME --output-dir /mnt/backups
  $SCRIPT_NAME --dry-run --json
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --config-dir) CONFIG_DIR="$2"; shift 2 ;;
    --data-dir) DATA_DIR="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --json) JSON_OUTPUT=true; shift ;;
    --help) usage ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="${OUTPUT_DIR}/headscale-${TIMESTAMP}.tar.gz"

if [[ "$DRY_RUN" == true ]]; then
  echo "=== Headscale Backup (DRY RUN) ==="
  echo "Would create: $BACKUP_FILE"
  echo "Would include:"
  echo "  - ${CONFIG_DIR}/config.yaml"
  echo "  - ${CONFIG_DIR}/policy.json (if exists)"
  echo "  - ${DATA_DIR}/db.sqlite"
  echo "  - ${DATA_DIR}/private.key"
  echo "  - ${DATA_DIR}/derp_server_key (if exists)"
  echo "  - TLS certs (if found)"
  if [[ "$JSON_OUTPUT" == true ]]; then
    echo '{"dry_run": true, "backup_file": "'"$BACKUP_FILE"'", "sources": ["'"$CONFIG_DIR"/config.yaml"'", "'"$DATA_DIR"/db.sqlite"'"]}'
  fi
  exit 0
fi

mkdir -p "$OUTPUT_DIR"

# Build list of files to backup
FILES_TO_BACKUP=()
[[ -f "$CONFIG_DIR/config.yaml" ]] && FILES_TO_BACKUP+=("$CONFIG_DIR/config.yaml")
[[ -f "$CONFIG_DIR/policy.json" ]] && FILES_TO_BACKUP+=("$CONFIG_DIR/policy.json")
[[ -f "$DATA_DIR/db.sqlite" ]] && FILES_TO_BACKUP+=("$DATA_DIR/db.sqlite")
[[ -f "$DATA_DIR/private.key" ]] && FILES_TO_BACKUP+=("$DATA_DIR/private.key")
[[ -f "$DATA_DIR/derp_server_key" ]] && FILES_TO_BACKUP+=("$DATA_DIR/derp_server_key")

# Check for TLS certs
for cert_path in /etc/letsencrypt/live/*/fullchain.pem /etc/ssl/certs/*.crt; do
  [[ -f "$cert_path" ]] && FILES_TO_BACKUP+=("$cert_path")
done 2>/dev/null || true

if [[ ${#FILES_TO_BACKUP[@]} -eq 0 ]]; then
  echo "Error: no headscale files found to backup" >&2
  exit 1
fi

# Create backup
tar czf "$BACKUP_FILE" "${FILES_TO_BACKUP[@]}" 2>/dev/null
CHECKSUM=$(sha256sum "$BACKUP_FILE" | cut -d' ' -f1)

if [[ "$JSON_OUTPUT" == true ]]; then
  echo '{"backup_file": "'"$BACKUP_FILE"'", "checksum": "'"$CHECKSUM"'", "file_count": '"${#FILES_TO_BACKUP[@]}"', "timestamp": "'"$TIMESTAMP"'"}'
else
  echo "Backup created: $BACKUP_FILE"
  echo "Checksum (SHA256): $CHECKSUM"
  echo "Files backed up: ${#FILES_TO_BACKUP[@]}"
fi
