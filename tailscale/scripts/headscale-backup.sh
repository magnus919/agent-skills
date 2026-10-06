#!/usr/bin/env bash
set -euo pipefail
SCRIPT_NAME="$(basename "$0")"
OUTPUT_DIR="${HOME}/backups/headscale"
CONFIG_DIR="/etc/headscale"
DATA_DIR="/var/lib/headscale"
CERTS_DIR="/etc/headscale"
DRY_RUN=false
JSON_OUTPUT=false
usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Create a consistent Headscale backup using the database and recovery paths in config.yaml.

Options:
  --output-dir DIR  Backup destination (default: ~/backups/headscale)
  --config-dir DIR  Headscale configuration directory (default: /etc/headscale)
  --data-dir DIR    Headscale data directory (default: /var/lib/headscale)
  --certs-dir DIR   TLS recovery directory (default: /etc/headscale)
  --dry-run         Preview required assets without creating an archive
  --json            Output as JSON
  --help            Show this help
EOF
}
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --config-dir) CONFIG_DIR="$2"; shift 2 ;;
    --data-dir) DATA_DIR="$2"; shift 2 ;;
    --certs-dir) CERTS_DIR="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --json) JSON_OUTPUT=true; shift ;;
    --help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../skills/headscale-backup/scripts" && pwd)"
ARGS=(backup --config "${CONFIG_DIR}/config.yaml" --data-dir "$DATA_DIR" --certs-dir "$CERTS_DIR" --output-dir "$OUTPUT_DIR" --auto)
[[ "$DRY_RUN" == true ]] && ARGS+=(--dry-run)
[[ "$JSON_OUTPUT" == true ]] && ARGS+=(--json)
exec python3 "${SCRIPT_DIR}/hs-archive.py" "${ARGS[@]}"
