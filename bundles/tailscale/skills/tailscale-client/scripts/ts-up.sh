#!/usr/bin/env bash
# =============================================================================
# ts-up.sh — Wrapper for `tailscale up` with Headscale
# =============================================================================
# Description:
#   Wrapper around `tailscale up` configured for Headscale. Applies env-var
#   defaults and exposes common flags in a consistent interface.
#
# Usage:
#   ./ts-up.sh [options]
#
# Options:
#   --login-server <URL>     Headscale control server URL (default: $HEADSCALE_URL)
#   --authkey <key>          Pre-authentication key (default: $TAILSCALE_AUTHKEY)
#   --advertise-tags <tags>  Comma-separated tags (e.g. tag:ci-runner,tag:monitoring)
#   --advertise-routes <cidr> CIDR ranges to advertise (e.g. 10.0.0.0/16)
#   --accept-routes          Accept routes from other nodes
#   --accept-dns             Accept MagicDNS configuration
#   --exit-node <IP>         Use a specific exit node
#   --ssh                    Enable Tailscale SSH
#   --dry-run                Preview the tailscale up command without running it
#   --json                   Output results in JSON format
#   --help                   Show this help message and exit
#
# Environment:
#   HEADSCALE_URL            Default --login-server value
#   TAILSCALE_AUTHKEY        Default --authkey value
#
# Examples:
#   ./ts-up.sh --login-server https://headscale.example.com --authkey tskey-auth-xxxxx
#   ./ts-up.sh --accept-routes --accept-dns
#   HEADSCALE_URL=https://headscale.example.com ./ts-up.sh --dry-run --json
#   ./ts-up.sh --advertise-tags tag:ci-runner --ssh
# =============================================================================

set -euo pipefail

# ---- Colors ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

usage() {
    grep "^# " "$0" | sed 's/^# //' | sed 's/^#//'
    exit 0
}

# ---- Defaults ----
LOGIN_SERVER=""
AUTHKEY=""
ADVERTISE_TAGS=""
ADVERTISE_ROUTES=""
ACCEPT_ROUTES=false
ACCEPT_DNS=false
EXIT_NODE=""
SSH=false
DRY_RUN=false
JSON_OUTPUT=false

# ---- Parse Arguments ----
while [[ $# -gt 0 ]]; do
    case "$1" in
        --login-server) LOGIN_SERVER="$2"; shift 2 ;;
        --authkey)      AUTHKEY="$2"; shift 2 ;;
        --advertise-tags) ADVERTISE_TAGS="$2"; shift 2 ;;
        --advertise-routes) ADVERTISE_ROUTES="$2"; shift 2 ;;
        --accept-routes) ACCEPT_ROUTES=true; shift ;;
        --accept-dns)    ACCEPT_DNS=true; shift ;;
        --exit-node)     EXIT_NODE="$2"; shift 2 ;;
        --ssh)           SSH=true; shift ;;
        --dry-run)       DRY_RUN=true; shift ;;
        --json)          JSON_OUTPUT=true; shift ;;
        --help)          usage ;;
        *)               error "Unknown option: $1"; usage ;;
    esac
done

# Apply env var defaults
LOGIN_SERVER="${LOGIN_SERVER:-${HEADSCALE_URL:-}}"
AUTHKEY="${AUTHKEY:-${TAILSCALE_AUTHKEY:-}}"

# ---- Verify prerequisites ----
if ! command -v tailscale &>/dev/null; then
    error "tailscale command not found. Install tailscale first (see ts-install.sh)."
    exit 1
fi

# ---- Build the tailscale up flags ----
TAILSCALE_UP_FLAGS=()

if [[ -n "$LOGIN_SERVER" ]]; then
    TAILSCALE_UP_FLAGS+=(--login-server="$LOGIN_SERVER")
fi

if [[ -n "$AUTHKEY" ]]; then
    TAILSCALE_UP_FLAGS+=(--authkey="$AUTHKEY")
fi

if [[ -n "$ADVERTISE_TAGS" ]]; then
    IFS=',' read -ra TAGS <<< "$ADVERTISE_TAGS"
    for tag in "${TAGS[@]}"; do
        TAILSCALE_UP_FLAGS+=(--advertise-tags="$tag")
    done
fi

if [[ -n "$ADVERTISE_ROUTES" ]]; then
    TAILSCALE_UP_FLAGS+=(--advertise-routes="$ADVERTISE_ROUTES")
fi

if [[ "$ACCEPT_ROUTES" == "true" ]]; then
    TAILSCALE_UP_FLAGS+=(--accept-routes)
fi

if [[ "$ACCEPT_DNS" == "true" ]]; then
    TAILSCALE_UP_FLAGS+=(--accept-dns)
fi

if [[ -n "$EXIT_NODE" ]]; then
    TAILSCALE_UP_FLAGS+=(--exit-node="$EXIT_NODE")
fi

if [[ "$SSH" == "true" ]]; then
    TAILSCALE_UP_FLAGS+=(--ssh)
fi

# ---- Dry-Run / Execute ----
if [[ "$DRY_RUN" == "true" ]]; then
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        cat <<EOF
{
  "status": "dry-run",
  "command": "sudo tailscale up ${TAILSCALE_UP_FLAGS[*]}",
  "login_server": "${LOGIN_SERVER:-not-set}",
  "authkey": "$(if [[ -n "$AUTHKEY" ]]; then echo "provided (${#AUTHKEY} chars)"; else echo "not-set"; fi)",
  "advertise_tags": "${ADVERTISE_TAGS:-none}",
  "advertise_routes": "${ADVERTISE_ROUTES:-none}",
  "accept_routes": ${ACCEPT_ROUTES},
  "accept_dns": ${ACCEPT_DNS},
  "exit_node": "${EXIT_NODE:-none}",
  "ssh": ${SSH}
}
EOF
    else
        info "Dry-run mode — would execute:"
        echo ""
        echo "  sudo tailscale up ${TAILSCALE_UP_FLAGS[*]}"
        echo ""
        info "Current tailscale status:"
        tailscale status --json 2>/dev/null | python3 -m json.tool 2>/dev/null || tailscale status 2>/dev/null || echo "  (not connected)"
    fi
    exit 0
fi

# ---- Execute tailscale up ----
info "Running: sudo tailscale up ${TAILSCALE_UP_FLAGS[*]}"
echo ""

UP_OUTPUT=$(sudo tailscale up "${TAILSCALE_UP_FLAGS[@]}" 2>&1) || {
    EXIT_CODE=$?
    error "tailscale up failed (exit code ${EXIT_CODE})"
    error "${UP_OUTPUT}"
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        cat <<EOF
{
  "status": "error",
  "exit_code": ${EXIT_CODE},
  "error": "$(echo "${UP_OUTPUT}" | head -5 | sed 's/"/\\"/g')"
}
EOF
    fi
    exit ${EXIT_CODE}
}

if [[ -n "$UP_OUTPUT" ]]; then
    echo "${UP_OUTPUT}"
fi

# ---- Verify connectivity ----
echo ""
info "Verifying connectivity..."
CONNECTIVITY=""
if tailscale status --json 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
self = d.get('Self', {})
online = self.get('Online', False)
print('online' if online else 'offline')
" 2>/dev/null; then
    CONNECTIVITY=$(tailscale status --json 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
self = d.get('Self', {})
print('connected' if self.get('Online', False) else 'online-false')
")
fi

if [[ "$JSON_OUTPUT" == "true" ]]; then
    # Get full status for JSON output
    STATUS_JSON=$(tailscale status --json 2>/dev/null || echo '{}')
    cat <<EOF
{
  "status": "success",
  "login_server": "${LOGIN_SERVER:-}",
  "authkey_provided": $(if [[ -n "$AUTHKEY" ]]; then echo "true"; else echo "false"; fi),
  "connectivity": $(echo "$STATUS_JSON")
}
EOF
else
    success "tailscale up completed successfully"
    tailscale status 2>/dev/null | head -20
fi
