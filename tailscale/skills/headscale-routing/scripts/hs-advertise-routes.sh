#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# hs-advertise-routes.sh — Advertise subnet routes on a Tailscale node
#
# Wrapper around `tailscale up --advertise-routes=<cidr>` with overlap
# detection and dry-run support.
#
# Usage:
#   hs-advertise-routes.sh --routes 192.168.1.0/24,10.0.0.0/16
#   hs-advertise-routes.sh --routes 192.168.1.0/24 --node myserver
#   hs-advertise-routes.sh --routes 10.0.0.0/8 --dry-run
#   hs-advertise-routes.sh --routes 172.16.0.0/12 --json
#
# Options:
#   --routes <cidr1,cidr2>   Comma-separated subnet CIDRs to advertise
#   --node <name>            Node to configure (auto-detects current host if omitted)
#   --dry-run                Print what would be done without making changes
#   --json                   Output results as JSON
#   --help                   Show this help message
# =============================================================================

SCRIPT_NAME="$(basename "$0")"

usage() {
    sed -n '/^# Usage:/,/^$/p' "$0" | sed '1d' | sed 's/^# //; s/^#$//'
    exit 0
}

# ── Parse arguments ──────────────────────────────────────────────────────────
ROUTES=""
NODE=""
DRY_RUN=false
JSON=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --routes)     ROUTES="$2"; shift 2 ;;
        --node)       NODE="$2"; shift 2 ;;
        --dry-run)    DRY_RUN=true; shift ;;
        --json)       JSON=true; shift ;;
        --help)       usage ;;
        *)            echo "Error: Unknown argument '$1'" >&2; usage ;;
    esac
done

# ── Validate inputs ──────────────────────────────────────────────────────────
if [[ -z "$ROUTES" ]]; then
    echo "Error: --routes is required (comma-separated CIDRs)" >&2
    exit 1
fi

# Validate CIDR format (basic check)
IFS=',' read -ra CIDR_LIST <<< "$ROUTES"
for cidr in "${CIDR_LIST[@]}"; do
    if ! [[ "$cidr" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+$ ]]; then
        echo "Error: Invalid CIDR format: '$cidr'" >&2
        exit 1
    fi
done

# ── Auto-detect node ─────────────────────────────────────────────────────────
if [[ -z "$NODE" ]]; then
    if command -v tailscale &>/dev/null && tailscale status --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('Self',{}).get('DNSName','').rstrip('.'))" 2>/dev/null; then
        NODE="$(tailscale status --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('Self',{}).get('DNSName','').rstrip('.'))")"
    else
        NODE="$(hostname -s)"
    fi
fi

# ── Check for subnet overlap with existing routes ────────────────────────────
check_overlap() {
    local new_cidr="$1"
    if ! command -v tailscale &>/dev/null; then
        return 0  # can't check, skip
    fi
    local status_json
    status_json="$(tailscale status --json 2>/dev/null || echo '{}')"

    # Extract advertised routes from self
    local self_routes
    self_routes="$(echo "$status_json" | python3 -c "
import sys, json, ipaddress
try:
    data = json.load(sys.stdin)
    self = data.get('Self', {})
    routes = self.get('AdvertisedRoutes', [])
    new = ipaddress.ip_network('$new_cidr')
    for r in routes:
        try:
            existing = ipaddress.ip_network(r)
            if new.overlaps(existing) and new != existing:
                print(f'OVERLAP:{r}')
        except:
            pass
except:
    pass
" 2>/dev/null || true)"

    if [[ -n "$self_routes" ]]; then
        echo "$self_routes" | while IFS=: read -r tag cidr; do
            echo "Warning: New route $new_cidr overlaps with existing advertised route $cidr" >&2
        done
        return 1
    fi
    return 0
}

# ── Execute ──────────────────────────────────────────────────────────────────
ADVERTISE_ROUTES="$ROUTES"

if [[ "$DRY_RUN" == true ]]; then
    if [[ "$JSON" == true ]]; then
        echo '{"dry_run":true,"node":"'"$NODE"'","routes":["'"$(echo "$ROUTES" | sed 's/,/","/g')"'"],"command":"tailscale up --advertise-routes='"$ADVERTISE_ROUTES"'"}'
    else
        echo "[DRY-RUN] Node: $NODE"
        echo "[DRY-RUN] Routes: $ROUTES"
        echo "[DRY-RUN] Command: tailscale up --advertise-routes=$ADVERTISE_ROUTES"
        echo ""
        echo "Hint: Client nodes need --accept-routes to use these routes."
        echo "      tailscale up --accept-routes"
    fi
    exit 0
fi

# Check for overlaps before applying
OVERLAP_FOUND=false
for cidr in "${CIDR_LIST[@]}"; do
    if ! check_overlap "$cidr"; then
        OVERLAP_FOUND=true
    fi
done

if [[ "$OVERLAP_FOUND" == true ]]; then
    echo "Warning: Overlapping routes detected. Proceeding anyway..." >&2
fi

# Execute tailscale up
echo "Advertising routes '$ADVERTISE_ROUTES' on node '$NODE'..."
if command -v tailscale &>/dev/null; then
    tailscale up --advertise-routes="$ADVERTISE_ROUTES"
    EXIT_CODE=$?
else
    echo "Error: 'tailscale' command not found on this node" >&2
    EXIT_CODE=1
fi

# ── Output ───────────────────────────────────────────────────────────────────
if [[ "$JSON" == true ]]; then
    if [[ $EXIT_CODE -eq 0 ]]; then
        echo '{"status":"ok","node":"'"$NODE"'","routes":["'"$(echo "$ROUTES" | sed 's/,/","/g')"'"],"message":"Routes advertised. Approve them on the Headscale server."}'
    else
        echo '{"status":"error","node":"'"$NODE"'","routes":["'"$(echo "$ROUTES" | sed 's/,/","/g')"'"],"exit_code":'"$EXIT_CODE"'}'
    fi
else
    if [[ $EXIT_CODE -eq 0 ]]; then
        echo "✓ Routes advertised successfully on '$NODE'"
        echo ""
        echo "Next steps:"
        echo "  1. Approve the routes on Headscale:"
        echo "     hs-approve-routes.sh --list --pending-only"
        echo "     hs-approve-routes.sh --approve <route-id>"
        echo "  2. Ensure clients have --accept-routes enabled:"
        echo "     tailscale up --accept-routes"
    else
        echo "✗ Failed to advertise routes (exit code: $EXIT_CODE)" >&2
    fi
fi

exit $EXIT_CODE
