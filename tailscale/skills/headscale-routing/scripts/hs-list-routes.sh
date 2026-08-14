#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# hs-list-routes.sh — List all routes with detailed status in Headscale
#
# Query the Headscale server for all routes with detailed status information.
# Supports filtering by node and status.
#
# Usage:
#   hs-list-routes.sh
#   hs-list-routes.sh --json
#   hs-list-routes.sh --node myserver
#   hs-list-routes.sh --pending-only
#   hs-list-routes.sh --node myserver --json
#   hs-list-routes.sh --pending-only --json
#
# Options:
#   --node <id>          Filter by node ID or name
#   --pending-only       Show only unapproved/pending routes
#   --json               Output raw JSON
#   --help               Show this help message
#
# Environment:
#   HEADSCALE_URL       Headscale server URL (e.g., https://headscale.example.com)
#   HEADSCALE_API_KEY   API key from `headscale apikeys create`
#
# Columns: ID, Node, Prefix, Status, Last Seen
# Status values: pending, advertised, enabled, disabled
# =============================================================================

SCRIPT_NAME="$(basename "$0")"

usage() {
    sed -n '/^# Usage:/,/^$/p' "$0" | sed '1d' | sed 's/^# //; s/^#$//'
    exit 0
}

# ── Parse arguments ──────────────────────────────────────────────────────────
NODE=""
PENDING_ONLY=false
JSON=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --node)          NODE="$2"; shift 2 ;;
        --pending-only)  PENDING_ONLY=true; shift ;;
        --json)          JSON=true; shift ;;
        --help)          usage ;;
        *)               echo "Error: Unknown argument '$1'" >&2; usage ;;
    esac
done

# ── Helper: fetch routes ─────────────────────────────────────────────────────
fetch_routes() {
    if [[ -n "$HEADSCALE_URL" && -n "$HEADSCALE_API_KEY" ]]; then
        curl -sf -X GET \
            -H "Authorization: Bearer ${HEADSCALE_API_KEY}" \
            -H "Content-Type: application/json" \
            "${HEADSCALE_URL%/}/api/v1/routes" 2>/dev/null \
        || echo '{"routes":[]}'
    elif command -v headscale &>/dev/null; then
        headscale routes list --output json 2>/dev/null \
        || echo '{"routes":[]}'
    elif [[ -f /usr/local/bin/headscale ]]; then
        /usr/local/bin/headscale routes list --output json 2>/dev/null \
        || echo '{"routes":[]}'
    else
        echo "Error: HEADSCALE_URL/HEADSCALE_API_KEY not set and 'headscale' CLI not found" >&2
        echo "Set HEADSCALE_URL and HEADSCALE_API_KEY, or run on the Headscale server." >&2
        exit 1
    fi
}

# ── Format output ────────────────────────────────────────────────────────────
format_table() {
    python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    data = {'routes': []}

routes = data if isinstance(data, list) else data.get('routes', [])

# Filters
filter_node = '$NODE'
pending_only = '${PENDING_ONLY}'

if filter_node:
    fn = filter_node.lower()
    routes = [r for r in routes
              if str(r.get('node', {}).get('id', '')).lower() == fn
              or str(r.get('node', {}).get('name', '')).lower() == fn]

if pending_only == 'true':
    routes = [r for r in routes if r.get('status', '').lower() in ('pending', 'advertised')]

if not routes:
    print('No routes found.')
    sys.exit(0)

# Header
print(f'{\"ID\":<10} {\"Node\":<20} {\"Prefix\":<25} {\"Status\":<15} {\"Last Seen\":<22}')
print('-' * 92)

for r in routes:
    rid = str(r.get('id', ''))
    node_name = r.get('node', {}).get('name', r.get('node', {}).get('id', '?'))
    node_id = str(r.get('node', {}).get('id', ''))
    # Show prefix(es)
    prefixes = r.get('prefixes', [])
    if not prefixes and r.get('prefix'):
        prefixes = [r.get('prefix')]
    prefix_str = ', '.join(prefixes) if prefixes else '-'

    # Determine status: enabled > disabled > advertised > pending
    raw_status = r.get('status', 'unknown')
    enabled = r.get('enabled', False)
    is_primary = r.get('isPrimary', r.get('is_primary', False))
    
    if enabled and is_primary:
        status = 'enabled'
    elif enabled:
        status = 'enabled'
    elif raw_status.lower() in ('disabled', 'rejected'):
        status = 'disabled'
    elif raw_status.lower() == 'advertised':
        status = 'pending'
    else:
        status = raw_status.lower()

    last_seen = r.get('lastSeen', r.get('last_seen', ''))
    if last_seen and len(last_seen) > 19:
        last_seen = last_seen[:19]
    if not last_seen:
        last_seen = '-'

    print(f'{rid:<10} {str(node_name):<20} {str(prefix_str):<25} {str(status):<15} {str(last_seen):<22}')
" <<< "$1"
}

# ── Main ─────────────────────────────────────────────────────────────────────
RAW="$(fetch_routes)"

if [[ "$JSON" == true ]]; then
    # Apply filters but output as raw JSON
    python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    data = {'routes': []}

routes = data if isinstance(data, list) else data.get('routes', [])

filter_node = '$NODE'
pending_only = '${PENDING_ONLY}'

if filter_node:
    fn = filter_node.lower()
    routes = [r for r in routes
              if str(r.get('node', {}).get('id', '')).lower() == fn
              or str(r.get('node', {}).get('name', '')).lower() == fn]

if pending_only == 'true':
    routes = [r for r in routes if r.get('status', '').lower() in ('pending', 'advertised')]

output = {'routes': routes, 'count': len(routes)}
print(json.dumps(output, indent=2))
" <<< "$RAW"
else
    format_table "$RAW"
fi
