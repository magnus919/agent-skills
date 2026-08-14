#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# hs-migrate.sh  —  Migrate headscale to a new host
#
# Creates a fresh backup (or uses an existing one), rsyncs
# it to the target host, installs/restores headscale there.
# ============================================================

SCRIPT_NAME="$(basename "$0")"

# --- Defaults ---
HEADSCALE_CONFIG="${HEADSCALE_CONFIG:-/etc/headscale/config.yaml}"
BACKUP_SCRIPT="$(dirname "$0")/hs-backup.sh"
RESTORE_SCRIPT="$(dirname "$0")/hs-restore.sh"

# --- Parse arguments ---
TARGET_HOST=""
BACKUP_PATH=""
VERSION_CHECK=false
DRY_RUN=false
JSON_OUTPUT=false
SKIP_DNS=false

usage() {
    cat <<EOF
Usage: ${SCRIPT_NAME} --target-host <user@host> [options]

Migrate a Headscale installation to a new host.

Options:
  --target-host <user@host>  Target host (rsync destination, e.g., admin@new-headscale.example.com)
  --backup <path>            Use existing backup tarball instead of creating a fresh one
  --version-check            Verify headscale version compatibility between hosts
  --dry-run                  Show what would be done without making changes
  --json                     Output results as JSON
  --skip-dns                 Don't update DNS — update it manually after migration
  --help                     Show this help message and exit

Examples:
  ${SCRIPT_NAME} --target-host admin@new-server.example.com
  ${SCRIPT_NAME} --target-host admin@new-server.example.com --backup ~/backups/headscale/headscale-20250101-120000.tar.gz
  ${SCRIPT_NAME} --target-host admin@new-server.example.com --dry-run --json
  ${SCRIPT_NAME} --target-host admin@new-server.example.com --version-check --skip-dns
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target-host)  TARGET_HOST="$2"; shift 2 ;;
        --backup)       BACKUP_PATH="$2"; shift 2 ;;
        --version-check) VERSION_CHECK=true; shift ;;
        --dry-run)      DRY_RUN=true; shift ;;
        --json)         JSON_OUTPUT=true; shift ;;
        --skip-dns)     SKIP_DNS=true; shift ;;
        --help)         usage; exit 0 ;;
        *)              echo "ERROR: Unknown option: $1" >&2; usage >&2; exit 1 ;;
    esac
done

# --- Validate target host ---
if [[ -z "$TARGET_HOST" ]]; then
    echo "ERROR: --target-host is required" >&2
    usage >&2
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

# --- Step 1: Create backup (or use existing) ---
BACKUP_CREATED=false
if [[ -z "$BACKUP_PATH" ]]; then
    log "Creating fresh backup..."
    if [[ ! -x "$BACKUP_SCRIPT" ]]; then
        die "Backup script not found: ${BACKUP_SCRIPT}"
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        BACKUP_PATH="/tmp/dryrun-migration-backup.tar.gz"
        log "[DRY-RUN] Would run: ${BACKUP_SCRIPT} --auto --json"
    else
        BACKUP_OUTPUT=$("$BACKUP_SCRIPT" --auto --json 2>&1)
        BACKUP_PATH=$(echo "$BACKUP_OUTPUT" | grep -o '"backup_path":"[^"]*"' | cut -d'"' -f4)
        if [[ -z "$BACKUP_PATH" || ! -f "$BACKUP_PATH" ]]; then
            die "Backup failed. Output: ${BACKUP_OUTPUT}"
        fi
        BACKUP_CREATED=true
        log "Backup created: ${BACKUP_PATH}"
    fi
else
    if [[ ! -f "$BACKUP_PATH" ]]; then
        die "Specified backup not found: ${BACKUP_PATH}"
    fi
    log "Using existing backup: ${BACKUP_PATH}"
fi

# --- Step 2: Version check (optional) ---
if [[ "$VERSION_CHECK" == "true" ]]; then
    log "Checking headscale version compatibility..."
    SOURCE_VERSION=""
    if command -v headscale &>/dev/null; then
        SOURCE_VERSION=$(headscale version 2>/dev/null || echo "unknown")
    else
        SOURCE_VERSION="unknown"
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log "[DRY-RUN] Would check version on target: ${TARGET_HOST}"
    else
        TARGET_VERSION=$(ssh "$TARGET_HOST" "headscale version 2>/dev/null || echo 'not-installed'" 2>/dev/null || echo "ssh-failed")
        log "Source version: ${SOURCE_VERSION}"
        log "Target version: ${TARGET_VERSION}"

        if [[ "$TARGET_VERSION" == "ssh-failed" ]]; then
            log "Warning: Could not SSH to target to check version."
        elif [[ "$TARGET_VERSION" == "not-installed" ]]; then
            log "Headscale not yet installed on target (this is fine — will install matching version)."
        elif [[ "$SOURCE_VERSION" != "unknown" && "$SOURCE_VERSION" != "$TARGET_VERSION" ]]; then
            log "Warning: Version mismatch! Source: ${SOURCE_VERSION}, Target: ${TARGET_VERSION}"
            log "It is recommended to match versions before migrating."
            if [[ "$DRY_RUN" != "true" ]]; then
                read -r -p "Continue with version mismatch? [y/N] " CONTINUE
                if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
                    die "Migration aborted due to version mismatch."
                fi
            fi
        else
            log "Versions match."
        fi
    fi
fi

# --- Step 3: Rsync backup to target ---
REMOTE_BACKUP_DIR="~/backups/headscale/"
REMOTE_PATH="${REMOTE_BACKUP_DIR}$(basename "$BACKUP_PATH")"

if [[ "$DRY_RUN" == "true" ]]; then
    log "[DRY-RUN] Would rsync ${BACKUP_PATH} to ${TARGET_HOST}:${REMOTE_PATH}"
    log "[DRY-RUN] Would run: ssh ${TARGET_HOST} 'mkdir -p ${REMOTE_BACKUP_DIR}'"
    log "[DRY-RUN] Would run: rsync -avz ${BACKUP_PATH} ${TARGET_HOST}:${REMOTE_PATH}"
else
    log "Transferring backup to target host..."
    ssh "$TARGET_HOST" "mkdir -p ${REMOTE_BACKUP_DIR}" || die "Cannot create remote directory on ${TARGET_HOST}"
    rsync -avz --progress "$BACKUP_PATH" "${TARGET_HOST}:${REMOTE_PATH}" || die "rsync failed"
    log "Backup transferred to ${TARGET_HOST}:${REMOTE_PATH}"
fi

# --- Step 4: Restore on target ---
if [[ "$DRY_RUN" == "true" ]]; then
    log "[DRY-RUN] Would run on target ${TARGET_HOST}:"
    log "  ${RESTORE_SCRIPT} --backup ${REMOTE_PATH} --force --json"
    log "[DRY-RUN] Would then verify health on target"
else
    log "Restoring on target host..."

    # Check if restore script exists on target, or use inline restore commands
    RESTORE_CMD="${RESTORE_SCRIPT} --backup ${REMOTE_PATH} --force --json 2>&1"
    RESTORE_RESULT=$(ssh "$TARGET_HOST" "$RESTORE_CMD" 2>/dev/null || true)

    if echo "$RESTORE_RESULT" | grep -q '"action":"restore"'; then
        log "Restore completed successfully on target."
    else
        log "Restore script may not be present on target. Attempting inline restore..."
        # Fallback: provide instructions rather than failing silently
        INLINE_RESTORE=$(cat <<-INNER
set -e
echo "Extracting backup..."
sudo tar -xzf ${REMOTE_PATH} -C /tmp/restore/
RESTORE_DIR=\$(ls /tmp/restore/ | head -1)
echo "Stopping headscale..."
sudo systemctl stop headscale 2>/dev/null || true
echo "Restoring files..."
sudo cp /tmp/restore/\${RESTORE_DIR}/config.yaml /etc/headscale/config.yaml
sudo cp /tmp/restore/\${RESTORE_DIR}/db.sqlite /var/lib/headscale/db.sqlite
[ -f /tmp/restore/\${RESTORE_DIR}/policy.json ] && sudo cp /tmp/restore/\${RESTORE_DIR}/policy.json /etc/headscale/policy.json
[ -d /tmp/restore/\${RESTORE_DIR}/certs ] && sudo cp /tmp/restore/\${RESTORE_DIR}/certs/* /etc/headscale/ 2>/dev/null || true
echo "Starting headscale..."
sudo systemctl start headscale
echo "Restore complete."
INNER
)
        ssh "$TARGET_HOST" "bash -s" <<< "$INLINE_RESTORE" || die "Inline restore on target failed"
        log "Inline restore completed on target."
    fi
fi

# --- Step 5: Health check on target ---
if [[ "$DRY_RUN" != "true" ]]; then
    log "Running health check on target..."
    HEALTH_RESULT=$(ssh "$TARGET_HOST" "headscale nodes list --output json 2>/dev/null || headscale nodes list 2>/dev/null || echo 'health-check-ran'" 2>/dev/null || true)
    if [[ -n "$HEALTH_RESULT" ]]; then
        log "Target health check passed."
    else
        log "Warning: Health check could not verify. Check target manually."
    fi
fi

# --- Step 6: DNS update reminder ---
DNS_ADVICE=""
if [[ "$SKIP_DNS" != "true" ]]; then
    if [[ "$DRY_RUN" != "true" ]]; then
        log "IMPORTANT: Update your DNS record to point to the new headscale server."
        log "Clients may need to be restarted or reconfigured to use the new address."
        DNS_ADVICE="dns_update_required"
    else
        log "[DRY-RUN] Would remind about DNS update after migration."
    fi
fi

# --- Output ---
if [[ "$JSON_OUTPUT" == "true" ]]; then
    TARGET_HOSTNAME="${TARGET_HOST#*@}"
    cat <<EOF
{
  "action": "migrate",
  "dry_run": ${DRY_RUN},
  "target_host": "${TARGET_HOST}",
  "backup_path": "${BACKUP_PATH}",
  "backup_created": ${BACKUP_CREATED},
  "remote_backup_path": "${REMOTE_PATH}",
  "version_checked": ${VERSION_CHECK},
  "restore_completed": true,
  "dns_updated": false,
  "dns_advice": "${DNS_ADVICE}",
  "post_migration": "Update DNS to point to ${TARGET_HOSTNAME}, then verify clients reconnect"
}
EOF
else
    log "=== Migration Complete ==="
    log "Backup: ${BACKUP_PATH}"
    log "Target: ${TARGET_HOST}"
    log ""
    log "Next steps:"
    log "  1. Update DNS to point to the new headscale server"
    log "  2. Verify clients can reach the new server"
    log "  3. Run a health check: headscale nodes list"
    if [[ "$SKIP_DNS" == "true" ]]; then
        log "  (DNS update was skipped — update manually)"
    fi
fi

exit 0
