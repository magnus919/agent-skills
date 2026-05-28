#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# hs-backup.sh  —  Full headscale backup
#
# Creates a timestamped tarball containing:
#   - SQLite DB (via sqlite3 .backup for safe live backup)
#   - config.yaml
#   - policy.json (if present)
#   - TLS certs and keys
#   - DERP map (if customized)
# ============================================================

SCRIPT_NAME="$(basename "$0")"

# --- Defaults ---
DEFAULT_OUTPUT_DIR="${HOME}/backups/headscale"
HEADSCALE_CONFIG="${HEADSCALE_CONFIG:-/etc/headscale/config.yaml}"
HEADSCALE_DATA_DIR="${HEADSCALE_DATA_DIR:-/var/lib/headscale}"
HEADSCALE_CERTS_DIR="${HEADSCALE_CERTS_DIR:-/etc/headscale}"

# --- Parse arguments ---
OUTPUT_DIR=""
DRY_RUN=false
JSON_OUTPUT=false
AUTO=false

usage() {
    cat <<EOF
Usage: ${SCRIPT_NAME} [options]

Backup a Headscale installation — SQLite database, config, policy, certs, and DERP map.

Options:
  --output-dir <path>    Output directory for backup tarball (default: ~/backups/headscale/)
  --dry-run              Show what would be backed up without creating the tarball
  --json                 Output results as JSON
  --auto                 Non-interactive mode (for cron); skips confirmation prompts
  --help                 Show this help message and exit

Examples:
  ${SCRIPT_NAME}
  ${SCRIPT_NAME} --output-dir /mnt/backups/headscale --auto
  ${SCRIPT_NAME} --dry-run --json
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        --dry-run)    DRY_RUN=true; shift ;;
        --json)       JSON_OUTPUT=true; shift ;;
        --auto)       AUTO=true; shift ;;
        --help)       usage; exit 0 ;;
        *)            echo "ERROR: Unknown option: $1" >&2; usage >&2; exit 1 ;;
    esac
done

OUTPUT_DIR="${OUTPUT_DIR:-$DEFAULT_OUTPUT_DIR}"

# --- Helper functions ---
log() {
    if [[ "$JSON_OUTPUT" != "true" ]]; then
        echo "[${SCRIPT_NAME}] $*"
    fi
}

die() {
    echo "ERROR: $*" >&2
    exit 1
}

json_echo() {
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        echo "$1"
    fi
}

# --- Validate config file ---
if [[ ! -f "$HEADSCALE_CONFIG" ]]; then
    die "Headscale config not found at ${HEADSCALE_CONFIG}. Set HEADSCALE_CONFIG or ensure the file exists."
fi

# --- Parse config for database path, cert paths, etc. ---
# Headscale typically uses /var/lib/headscale/db.sqlite
CONFIG_DB_PATH=$(grep -E '^\s*database_path:' "$HEADSCALE_CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"'"'" || true)
CONFIG_TLS_CERT=$(grep -E '^\s*tls_cert_path:' "$HEADSCALE_CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"'"'" || true)
CONFIG_TLS_KEY=$(grep -E '^\s*tls_key_path:' "$HEADSCALE_CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"'"'" || true)
CONFIG_POLICY=$(grep -E '^\s*policy_path:' "$HEADSCALE_CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"'"'" || true)

DB_PATH="${CONFIG_DB_PATH:-${HEADSCALE_DATA_DIR}/db.sqlite}"
CERT_PATH="${CONFIG_TLS_CERT:-${HEADSCALE_CERTS_DIR}/server.crt}"
KEY_PATH="${CONFIG_TLS_KEY:-${HEADSCALE_CERTS_DIR}/server.key}"
POLICY_PATH="${CONFIG_POLICY:-}"
NODE_KEY_PATH="${HEADSCALE_DATA_DIR}/private.key"
DERP_MAP_PATH="/etc/headscale/derp.yaml"

# --- Determine backup items ---
declare -a BACKUP_ITEMS=()
BACKUP_ITEMS+=("$HEADSCALE_CONFIG")
BACKUP_ITEMS+=("$DB_PATH")

if [[ -n "$POLICY_PATH" && -f "$POLICY_PATH" ]]; then
    BACKUP_ITEMS+=("$POLICY_PATH")
fi

for f in "$CERT_PATH" "$KEY_PATH" "$NODE_KEY_PATH"; do
    if [[ -f "$f" ]]; then
        BACKUP_ITEMS+=("$f")
    fi
done

if [[ -f "$DERP_MAP_PATH" ]]; then
    BACKUP_ITEMS+=("$DERP_MAP_PATH")
fi

# --- Dry-run: just list what would be backed up ---
if [[ "$DRY_RUN" == "true" ]]; then
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        ITEMS_JSON="["
        FIRST=true
        for item in "${BACKUP_ITEMS[@]}"; do
            $FIRST || ITEMS_JSON+=","
            FIRST=false
            SIZE=""
            if [[ -f "$item" ]]; then
                SIZE=$(stat -f%z "$item" 2>/dev/null || stat -c%s "$item" 2>/dev/null || echo "0")
            fi
            ITEMS_JSON+="{\"path\":\"${item}\",\"exists\":$([[ -f "$item" ]] && echo "true" || echo "false"),\"size\":${SIZE:-0}}"
        done
        ITEMS_JSON+="]"
        cat <<EOF
{
  "action": "backup",
  "dry_run": true,
  "output_dir": "${OUTPUT_DIR}",
  "items": ${ITEMS_JSON}
}
EOF
    else
        echo "=== Dry-run: would backup the following files ==="
        for item in "${BACKUP_ITEMS[@]}"; do
            if [[ -f "$item" ]]; then
                echo "  [EXISTS]   ${item}"
            else
                echo "  [MISSING]  ${item}"
            fi
        done
        echo "Output directory: ${OUTPUT_DIR}"
    fi
    exit 0
fi

# --- Create output directory ---
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="headscale-${TIMESTAMP}"
TARBALL_PATH="${OUTPUT_DIR}/${BACKUP_NAME}.tar.gz"

# --- Confirm unless --auto ---
if [[ "$AUTO" != "true" ]]; then
    echo "This will create a backup of Headscale state at: ${TARBALL_PATH}"
    echo "Items to back up:"
    for item in "${BACKUP_ITEMS[@]}"; do
        if [[ -f "$item" ]]; then
            echo "  [OK]   ${item}"
        else
            echo "  [WARN] ${item} (not found, skipping)"
        fi
    done
    read -r -p "Proceed? [y/N] " CONFIRM
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# --- Create a temporary working directory ---
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

BACKUP_DIR="${WORK_DIR}/${BACKUP_NAME}"
mkdir -p "$BACKUP_DIR"

# --- Backup SQLite database using .backup (safe for live DB) ---
log "Backing up SQLite database..."
SQLITE_BACKUP_PATH="${BACKUP_DIR}/db.sqlite"
if command -v sqlite3 &>/dev/null; then
    sqlite3 "$DB_PATH" ".backup '${SQLITE_BACKUP_PATH}'" || die "sqlite3 .backup failed"
else
    die "sqlite3 not found. Install it: brew install sqlite3 (macOS) or apt install sqlite3"
fi

# --- Copy config files ---
log "Backing up configuration..."
cp "$HEADSCALE_CONFIG" "${BACKUP_DIR}/config.yaml"

if [[ -n "$POLICY_PATH" && -f "$POLICY_PATH" ]]; then
    cp "$POLICY_PATH" "${BACKUP_DIR}/policy.json"
fi

# --- Copy TLS certs and keys ---
log "Backing up TLS assets..."
mkdir -p "${BACKUP_DIR}/certs"
for f in "$CERT_PATH" "$KEY_PATH" "$NODE_KEY_PATH"; do
    if [[ -f "$f" ]]; then
        cp "$f" "${BACKUP_DIR}/certs/"
    fi
done

# --- Copy DERP map if present ---
if [[ -f "$DERP_MAP_PATH" ]]; then
    log "Backing up DERP map..."
    cp "$DERP_MAP_PATH" "${BACKUP_DIR}/derp.yaml"
fi

# --- Create tarball ---
log "Creating tarball..."
tar -czf "$TARBALL_PATH" -C "$WORK_DIR" "$BACKUP_NAME"

# --- Compute checksum ---
CHECKSUM=""
if command -v sha256sum &>/dev/null; then
    CHECKSUM=$(sha256sum "$TARBALL_PATH" | awk '{print $1}')
elif command -v shasum &>/dev/null; then
    CHECKSUM=$(shasum -a 256 "$TARBALL_PATH" | awk '{print $1}')
elif command -v openssl &>/dev/null; then
    CHECKSUM=$(openssl dgst -sha256 "$TARBALL_PATH" | awk '{print $NF}')
fi

TARBALL_SIZE=$(stat -f%z "$TARBALL_PATH" 2>/dev/null || stat -c%s "$TARBALL_PATH" 2>/dev/null || echo "0")

# --- Output ---
log "Backup complete: ${TARBALL_PATH}"
log "Size: ${TARBALL_SIZE} bytes"

if [[ "$JSON_OUTPUT" == "true" ]]; then
    cat <<EOF
{
  "action": "backup",
  "dry_run": false,
  "output_dir": "${OUTPUT_DIR}",
  "backup_path": "${TARBALL_PATH}",
  "timestamp": "${TIMESTAMP}",
  "size_bytes": ${TARBALL_SIZE},
  "checksum_sha256": "${CHECKSUM}",
  "items_count": ${#BACKUP_ITEMS[@]}
}
EOF
fi

exit 0
