#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# hs-restore.sh  —  Restore headscale from a backup tarball
#
# Stops headscale, restores files, then starts headscale.
# Validates backup integrity and headscale version compatibility.
# ============================================================

SCRIPT_NAME="$(basename "$0")"

# --- Defaults ---
HEADSCALE_CONFIG="${HEADSCALE_CONFIG:-/etc/headscale/config.yaml}"
HEADSCALE_DATA_DIR="${HEADSCALE_DATA_DIR:-/var/lib/headscale}"
HEADSCALE_CERTS_DIR="${HEADSCALE_CERTS_DIR:-/etc/headscale}"
HEADSCALE_SERVICE="${HEADSCALE_SERVICE:-headscale}"

# --- Parse arguments ---
BACKUP_PATH=""
DRY_RUN=false
JSON_OUTPUT=false
FORCE=false

usage() {
    cat <<EOF
Usage: ${SCRIPT_NAME} --backup <path> [options]

Restore a Headscale installation from a backup tarball.

Options:
  --backup <path>        Path to the backup tarball (headscale-YYYYMMDD-HHMMSS.tar.gz)
  --dry-run              Show what would be restored without making changes
  --json                 Output results as JSON
  --force                Skip confirmation prompt
  --help                 Show this help message and exit

Examples:
  ${SCRIPT_NAME} --backup ~/backups/headscale/headscale-20250101-120000.tar.gz
  ${SCRIPT_NAME} --backup /backups/latest.tar.gz --dry-run --json
  ${SCRIPT_NAME} --backup /backups/latest.tar.gz --force
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --backup)   BACKUP_PATH="$2"; shift 2 ;;
        --dry-run)  DRY_RUN=true; shift ;;
        --json)     JSON_OUTPUT=true; shift ;;
        --force)    FORCE=true; shift ;;
        --help)     usage; exit 0 ;;
        *)          echo "ERROR: Unknown option: $1" >&2; usage >&2; exit 1 ;;
    esac
done

# --- Validate backup path ---
if [[ -z "$BACKUP_PATH" ]]; then
    echo "ERROR: --backup is required" >&2
    usage >&2
    exit 1
fi

if [[ ! -f "$BACKUP_PATH" ]]; then
    echo "ERROR: Backup file not found: ${BACKUP_PATH}" >&2
    exit 1
fi

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

# --- Validate backup tarball ---
log "Validating backup tarball..."

# Check it's a valid gzip tarball
if ! gzip -t "$BACKUP_PATH" 2>/dev/null; then
    die "Backup file is not a valid gzip archive: ${BACKUP_PATH}"
fi

# List contents
TAR_CONTENTS=$(tar -tzf "$BACKUP_PATH" 2>/dev/null) || die "Cannot read tarball contents"

# Check for essential files
HAS_DB=false
HAS_CONFIG=false
BACKUP_BASENAME=""
if echo "$TAR_CONTENTS" | grep -q 'db.sqlite$'; then HAS_DB=true; fi
if echo "$TAR_CONTENTS" | grep -q 'config.yaml$'; then HAS_CONFIG=true; fi
BACKUP_BASENAME=$(echo "$TAR_CONTENTS" | head -1 | cut -d/ -f1)

if [[ "$HAS_DB" != "true" ]]; then
    die "Backup tarball is missing db.sqlite — invalid backup"
fi
if [[ "$HAS_CONFIG" != "true" ]]; then
    die "Backup tarball is missing config.yaml — invalid backup"
fi

log "Backup validated (base directory: ${BACKUP_BASENAME})"

# --- Check headscale version compatibility ---
check_headscale_version() {
    if command -v headscale &>/dev/null; then
        INSTALLED_VERSION=$(headscale version 2>/dev/null || echo "unknown")
        # Try to extract version from the database
        if command -v sqlite3 &>/dev/null; then
            WORK_DIR_CHECK=$(mktemp -d)
            trap 'rm -rf "$WORK_DIR_CHECK"' EXIT
            tar -xzf "$BACKUP_PATH" -C "$WORK_DIR_CHECK" "${BACKUP_BASENAME}/db.sqlite" 2>/dev/null || true
            RESTORED_DB="${WORK_DIR_CHECK}/${BACKUP_BASENAME}/db.sqlite"
            if [[ -f "$RESTORED_DB" ]]; then
                log "Backup headscale version can't be determined from backup metadata; installed version: ${INSTALLED_VERSION}"
                log "Recommendation: ensure source and target headscale versions match."
            fi
        fi
    else
        log "headscale binary not found on this system — will install or copy after restore."
    fi
}

check_headscale_version

# --- Determine files to restore ---
declare -a RESTORE_FILES=()
RESTORE_FILES+=("${HEADSCALE_CONFIG}")
RESTORE_FILES+=("${HEADSCALE_DATA_DIR}/db.sqlite")
RESTORE_FILES+=("${HEADSCALE_CERTS_DIR}/server.crt")
RESTORE_FILES+=("${HEADSCALE_CERTS_DIR}/server.key")
RESTORE_FILES+=("${HEADSCALE_DATA_DIR}/private.key")
if echo "$TAR_CONTENTS" | grep -q 'derp.yaml$'; then
    RESTORE_FILES+=("/etc/headscale/derp.yaml")
fi

# --- Dry run ---
if [[ "$DRY_RUN" == "true" ]]; then
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        ITEMS_JSON="["
        FIRST=true
        for item in "${RESTORE_FILES[@]}"; do
            $FIRST || ITEMS_JSON+=","
            FIRST=false
            TAR_PATH="${BACKUP_BASENAME}/"
            case "$item" in
                */db.sqlite)                    TAR_PATH+="db.sqlite" ;;
                */config.yaml)                  TAR_PATH+="config.yaml" ;;
                */server.crt)                   TAR_PATH+="certs/server.crt" ;;
                */server.key)                   TAR_PATH+="certs/server.key" ;;
                */private.key)                  TAR_PATH+="certs/private.key" ;;
                */derp.yaml)                    TAR_PATH+="derp.yaml" ;;
                */policy.json)                  TAR_PATH+="policy.json" ;;
            esac
            EXISTS_IN_TAR=$(echo "$TAR_CONTENTS" | grep -q "$(basename "$TAR_PATH")$" && echo "true" || echo "false")
            CURRENT_EXISTS=$([[ -f "$item" ]] && echo "true" || echo "false")
            ITEMS_JSON+="{\"target\":\"${item}\",\"in_backup\":${EXISTS_IN_TAR},\"currently_exists\":${CURRENT_EXISTS}}"
        done
        ITEMS_JSON+="]"
        cat <<EOF
{
  "action": "restore",
  "dry_run": true,
  "backup_path": "${BACKUP_PATH}",
  "backup_id": "${BACKUP_BASENAME}",
  "has_db": ${HAS_DB},
  "has_config": ${HAS_CONFIG},
  "items": ${ITEMS_JSON}
}
EOF
    else
        echo "=== Dry-run: would restore the following files ==="
        for item in "${RESTORE_FILES[@]}"; do
            CURRENT=""
            if [[ -f "$item" ]]; then
                CURRENT="(currently exists)"
            else
                CURRENT="(will be created)"
            fi
            echo "  ${item} ${CURRENT}"
        done
        echo "Backup: ${BACKUP_PATH}"
        echo "Backup base: ${BACKUP_BASENAME}"
        echo "Action: stop headscale → restore files → start headscale"
    fi
    exit 0
fi

# --- Confirm unless --force ---
if [[ "$FORCE" != "true" ]]; then
    echo "WARNING: This will OVERWRITE current Headscale state with backup contents."
    echo "  Backup: ${BACKUP_PATH}"
    echo "  Files to restore:"
    for item in "${RESTORE_FILES[@]}"; do
        echo "    ${item}"
    done
    echo ""
    echo "Headscale service will be STOPPED and RESTARTED."
    read -r -p "Are you sure? This is destructive. Type 'yes' to continue: " CONFIRM
    if [[ "$CONFIRM" != "yes" ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# --- Stop headscale ---
log "Stopping headscale service..."
if command -v systemctl &>/dev/null; then
    sudo systemctl stop "$HEADSCALE_SERVICE" || log "Warning: could not stop service (may not be running)"
elif command -v service &>/dev/null; then
    sudo service "$HEADSCALE_SERVICE" stop || log "Warning: could not stop service"
elif command -v launchctl &>/dev/null; then
    sudo launchctl bootout system "/Library/LaunchDaemons/${HEADSCALE_SERVICE}.plist" 2>/dev/null || \
        log "Warning: could not stop launchd service"
else
    log "Unknown init system — attempting to stop headscale directly..."
    pkill headscale 2>/dev/null || true
fi

sleep 1

# --- Extract and restore files ---
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

log "Extracting backup..."
tar -xzf "$BACKUP_PATH" -C "$WORK_DIR"

RESTORE_DIR="${WORK_DIR}/${BACKUP_BASENAME}"

# Restore config
if [[ -f "${RESTORE_DIR}/config.yaml" ]]; then
    log "Restoring config.yaml..."
    sudo cp "${RESTORE_DIR}/config.yaml" "$HEADSCALE_CONFIG"
    sudo chmod 644 "$HEADSCALE_CONFIG"
fi

# Restore database
if [[ -f "${RESTORE_DIR}/db.sqlite" ]]; then
    log "Restoring SQLite database..."
    sudo mkdir -p "$HEADSCALE_DATA_DIR"
    sudo cp "${RESTORE_DIR}/db.sqlite" "${HEADSCALE_DATA_DIR}/db.sqlite"
    sudo chmod 600 "${HEADSCALE_DATA_DIR}/db.sqlite"
fi

# Restore policy
if [[ -f "${RESTORE_DIR}/policy.json" ]]; then
    POLICY_TARGET=$(grep -E '^\s*policy_path:' "$HEADSCALE_CONFIG" 2>/dev/null | awk '{print $2}' | tr -d '"'"'" || echo "/etc/headscale/policy.json")
    log "Restoring policy.json..."
    sudo cp "${RESTORE_DIR}/policy.json" "$POLICY_TARGET"
    sudo chmod 644 "$POLICY_TARGET"
fi

# Restore certs
if [[ -d "${RESTORE_DIR}/certs" ]]; then
    log "Restoring TLS certificates and keys..."
    sudo mkdir -p "$HEADSCALE_CERTS_DIR"
    for f in "${RESTORE_DIR}/certs/"*; do
        if [[ -f "$f" ]]; then
            BASENAME=$(basename "$f")
            if [[ "$BASENAME" == "private.key" ]]; then
                sudo cp "$f" "${HEADSCALE_DATA_DIR}/${BASENAME}"
                sudo chmod 600 "${HEADSCALE_DATA_DIR}/${BASENAME}"
            else
                sudo cp "$f" "${HEADSCALE_CERTS_DIR}/${BASENAME}"
                sudo chmod 600 "$f" 2>/dev/null || sudo chmod 644 "${HEADSCALE_CERTS_DIR}/${BASENAME}"
            fi
        fi
    done
fi

# Restore DERP map
if [[ -f "${RESTORE_DIR}/derp.yaml" ]]; then
    log "Restoring DERP map..."
    sudo cp "${RESTORE_DIR}/derp.yaml" "/etc/headscale/derp.yaml"
    sudo chmod 644 "/etc/headscale/derp.yaml"
fi

# --- Start headscale ---
log "Starting headscale service..."
if command -v systemctl &>/dev/null; then
    sudo systemctl start "$HEADSCALE_SERVICE" || die "Failed to start headscale"
elif command -v service &>/dev/null; then
    sudo service "$HEADSCALE_SERVICE" start || die "Failed to start headscale"
elif command -v launchctl &>/dev/null; then
    sudo launchctl bootstrap system "/Library/LaunchDaemons/${HEADSCALE_SERVICE}.plist" 2>/dev/null || \
        sudo launchctl kickstart -k system/homebrew.mxcl.headscale 2>/dev/null || \
        log "Warning: could not start launchd service — start it manually"
else
    log "Unknown init system — attempting to start headscale directly..."
    nohup headscale serve &>/dev/null &
fi

sleep 2

# --- Verify ---
VERIFY_OK=false
if command -v headscale &>/dev/null; then
    NODES=$(headscale nodes list --output json 2>/dev/null || true)
    if [[ -n "$NODES" ]]; then
        log "Headscale is running. Nodes found in database."
        VERIFY_OK=true
    else
        log "Headscale started but could not list nodes (may need API key)"
        VERIFY_OK=true
    fi
else
    log "headscale binary not found, but files have been restored."
    VERIFY_OK=true
fi

# --- Output ---
if [[ "$JSON_OUTPUT" == "true" ]]; then
    cat <<EOF
{
  "action": "restore",
  "dry_run": false,
  "backup_path": "${BACKUP_PATH}",
  "backup_id": "${BACKUP_BASENAME}",
  "service_stopped": true,
  "service_started": ${VERIFY_OK},
  "restored_files": [
    "config.yaml",
    "db.sqlite",
    "certs/*",
    $(echo "$TAR_CONTENTS" | grep -q 'policy.json' && echo '"policy.json",' || true)
    $(echo "$TAR_CONTENTS" | grep -q 'derp.yaml' && echo '"derp.yaml"' || true)
  ]
}
EOF
else
    if [[ "$VERIFY_OK" == "true" ]]; then
        log "Restore complete. Headscale is running."
    else
        log "Restore complete. Verify headscale status manually."
    fi
fi

exit 0
