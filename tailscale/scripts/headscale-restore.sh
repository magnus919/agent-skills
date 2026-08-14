#!/usr/bin/env bash
set -euo pipefail

# headscale-restore.sh — Restore Headscale from backup
SCRIPT_NAME="$(basename "$0")"
JSON_OUTPUT=false
DRY_RUN=false
FORCE=false
BACKUP_FILE=""
CONFIG_DIR="${HEADSCALE_CONFIG_DIR:-/etc/headscale}"
DATA_DIR="${HEADSCALE_DATA_DIR:-/var/lib/headscale}"

usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] --backup <file>

Restore Headscale from a backup archive.

Options:
  --backup FILE   Path to backup tarball (required)
  --config-dir DIR  Config restore target (default: /etc/headscale)
  --data-dir DIR    Data restore target (default: /var/lib/headscale)
  --force         Skip confirmation prompt
  --dry-run       Preview what would be restored
  --json          Output as JSON
  --help          Show this help

Examples:
  $SCRIPT_NAME --backup ~/backups/headscale-20260101-120000.tar.gz
  $SCRIPT_NAME --backup backup.tar.gz --dry-run --json
  $SCRIPT_NAME --backup backup.tar.gz --force
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --backup) BACKUP_FILE="$2"; shift 2 ;;
    --config-dir) CONFIG_DIR="$2"; shift 2 ;;
    --data-dir) DATA_DIR="$2"; shift 2 ;;
    --force) FORCE=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --json) JSON_OUTPUT=true; shift ;;
    --help) usage ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$BACKUP_FILE" ]]; then
  echo "Error: --backup <file> is required" >&2
  usage >&2
  exit 1
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "Error: backup file not found: $BACKUP_FILE" >&2
  exit 1
fi

# List contents for preview
if [[ "$DRY_RUN" == true ]]; then
  echo "=== Headscale Restore (DRY RUN) ==="
  echo "Backup: $BACKUP_FILE"
  echo "Contents:"
  tar tzf "$BACKUP_FILE" 2>/dev/null | while read -r line; do
    echo "  $line"
  done
  echo ""
  echo "Target config dir: $CONFIG_DIR"
  echo "Target data dir: $DATA_DIR"
  if [[ "$JSON_OUTPUT" == true ]]; then
    FILES=$(tar tzf "$BACKUP_FILE" 2>/dev/null | paste -sd, -)
    echo '{"dry_run": true, "backup_file": "'"$BACKUP_FILE"'", "contents": ["'"$FILES"'"], "config_dir": "'"$CONFIG_DIR"'", "data_dir": "'"$DATA_DIR"'"}'
  fi
  exit 0
fi

# Confirm unless --force
if [[ "$FORCE" != true ]]; then
  echo "WARNING: This will overwrite Headscale configuration and database."
  echo "Backup: $BACKUP_FILE"
  echo "Target: $CONFIG_DIR + $DATA_DIR"
  echo ""
  read -r -p "Continue? [y/N] " response
  case "$response" in
    [yY]|[yY][eE][sS]) ;;
    *) echo "Aborted."; exit 0 ;;
  esac
fi

# Stop headscale before restore
if command -v systemctl &>/dev/null && systemctl is-active headscale &>/dev/null; then
  echo "Stopping headscale service..."
  systemctl stop headscale
fi

# Restore
TMP_DIR=$(mktemp -d)
tar xzf "$BACKUP_FILE" -C "$TMP_DIR"

# Copy files to correct locations
for f in config.yaml policy.json private.key derp_server_key; do
  found=$(find "$TMP_DIR" -name "$f" -type f 2>/dev/null | head -1)
  if [[ -n "$found" ]]; then
    if [[ "$f" == "config.yaml" || "$f" == "policy.json" ]]; then
      cp "$found" "$CONFIG_DIR/$f" 2>/dev/null || true
    else
      cp "$found" "$DATA_DIR/$f" 2>/dev/null || true
    fi
  fi
done

# Restore database
db_found=$(find "$TMP_DIR" -name "db.sqlite" -type f 2>/dev/null | head -1)
if [[ -n "$db_found" ]]; then
  cp "$db_found" "$DATA_DIR/db.sqlite"
fi

rm -rf "$TMP_DIR"

# Start headscale
if command -v systemctl &>/dev/null; then
  systemctl start headscale
  sleep 2
  if systemctl is-active headscale &>/dev/null; then
    echo "Headscale service started successfully."
  else
    echo "Warning: headscale service may not have started. Check 'systemctl status headscale'." >&2
  fi
fi

if [[ "$JSON_OUTPUT" == true ]]; then
  echo '{"restored": true, "backup": "'"$BACKUP_FILE"'", "config_dir": "'"$CONFIG_DIR"'", "data_dir": "'"$DATA_DIR"'"}'
else
  echo "Restore complete from: $BACKUP_FILE"
fi
