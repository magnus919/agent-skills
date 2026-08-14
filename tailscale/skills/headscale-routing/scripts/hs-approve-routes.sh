#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# hs-approve-routes.sh -- List and approve/reject routes in Headscale
#
# Manage subnet route and exit node approval on a Headscale server.
# Supports Headscale REST API or direct CLI access.
#
# Usage:
#   hs-approve-routes.sh --list
#   hs-approve-routes.sh --list --pending-only
#   hs-approve-routes.sh --list --node myserver
#   hs-approve-routes.sh --approve <route-id>
#   hs-approve-routes.sh --approve-all
#   hs-approve-routes.sh --reject <route-id>
#   hs-approve-routes.sh --list --json
#   hs-approve-routes.sh --approve-all --dry-run
#
# Options:
#   --list               List all routes (or filter with --node/--pending-only)
#   --approve <id>       Approve a specific route by ID
#   --approve-all        Approve all pending routes
#   --reject <id>        Reject a specific route by ID
#   --node <id>          Filter by node ID (used with --list)
#   --pending-only       Show only unapproved/pending routes
#   --dry-run            Print what would be done without making changes
#   --json               Output results as JSON
#   --help               Show this help message
#
# Environment:
#   HEADSCALE_URL       Headscale server URL (e.g., https://headscale.example.com)
#   HEADSCALE_API_KEY   API key from `headscale apikeys create`
# =============================================================================

SCRIPT_NAME="$(basename "$0")"

usage() {
    sed -n '/^# Usage:/,/^$/p' "$0" | sed '1d' | sed 's/^# //; s/^#$//'
    exit 0
}

# -- Config ------------------------------------------------------------------
HEADSCALE_URL="${HEADSCALE_URL:-}"
HEADSCALE_API_KEY="${HEADSCALE_API_KEY:-}"

# -- Parse arguments ---------------------------------------------------------
ACTION=""
ACTION_ARG=""
NODE=""
PENDING_ONLY=false
DRY_RUN=false
JSON=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --list)          ACTION="list"; shift ;;
        --approve)       ACTION="approve"; ACTION_ARG="$2"; shift 2 ;;
        --approve-all)   ACTION="approve-all"; shift ;;
        --reject)        ACTION="reject"; ACTION_ARG="$2"; shift 2 ;;
        --node)          NODE="$2"; shift 2 ;;
        --pending-only)  PENDING_ONLY=true; shift ;;
        --dry-run)       DRY_RUN=true; shift ;;
        --json)          JSON=true; shift ;;
        --help)          usage ;;
        *)               echo "Error: Unknown argument '$1'" >&2; usage ;;
    esac
done

# -- Validate -----------------------------------------------------------------
if [[ -z "$ACTION" ]]; then
    echo "Error: One of --list, --approve, --approve-all, or --reject is required" >&2
    usage
fi

if [[ "$ACTION" == "approve" && -z "$ACTION_ARG" ]]; then
    echo "Error: --approve requires a route ID argument" >&2
    exit 1
fi

if [[ "$ACTION" == "reject" && -z "$ACTION_ARG" ]]; then
    echo "Error: --reject requires a route ID argument" >&2
    exit 1
fi

# -- Helper: route list to JSON/table ----------------------------------------
format_routes() {
    local raw_json="$1"
    if [[ "$JSON" == true ]]; then
        echo "$raw_json"
        return
    fi

    python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f'Error: Invalid JSON input: {e}', file=sys.stderr)
    sys.exit(1)

routes = data if isinstance(data, list) else data.get('routes', [])

if not routes:
    print('No routes found.')
    sys.exit(0)

print(f'{\"ID\":<10} {\"Node\":<20} {\"Prefix\":<22} {\"Status\":<15} {\"Last Seen\":<20}')
print('-' * 87)

for r in routes:
    rid = str(r.get('id', \'\'))
    node = r.get('node', {}).get('name', r.get('node', {}).get('id', '?'))
    prefix = r.get('prefix', r.get('prefixes', '')) if isinstance(r.get('prefix'), str) else ', '.join(r.get('prefixes', []))
    status = r.get('status', 'unknown')
    last_seen = r.get('lastSeen', r.get('last_seen', ''))[:19]
    print(f'{rid:<10} {str(node):<20} {str(prefix):<22} {str(status):<15} {str(last_seen):<20}')
" <<< "$raw_json"
}

# -- API call wrapper --------------------------------------------------------
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"

    if [[ -z "$HEADSCALE_URL" || -z "$HEADSCALE_API_KEY" ]]; then
        local headscale_cmd=""
        if command -v headscale &>/dev/null; then
            headscale_cmd="headscale"
        elif [[ -f /usr/local/bin/headscale ]]; then
            headscale_cmd="/usr/local/bin/headscale"
        else
            echo "Error: HEADSCALE_URL/HEADSCALE_API_KEY not set and 'headscale' CLI not found" >&2
            echo "Set HEADSCALE_URL and HEADSCALE_API_KEY, or run on the Headscale server." >&2
            return 1
        fi

        case "$endpoint" in
            *routes)
                if [[ "$method" == "GET" ]]; then
                    $headscale_cmd routes list --output json 2>/dev/null || $headscale_cmd routes list 2>/dev/null
                elif [[ "$method" == "POST" ]]; then
                    local route_id
                    route_id="$(echo "$data" | python3 -c "import sys,json; print(json.load(sys.stdin).get('route_id',''))" 2>/dev/null || echo "")"
                    if [[ -n "$route_id" ]]; then
                        $headscale_cmd routes approve -r "$route_id" 2>/dev/null
                    fi
                elif [[ "$method" == "DELETE" ]]; then
                    local route_id
                    route_id="$(echo "$data" | python3 -c "import sys,json; print(json.load(sys.stdin).get('route_id',''))" 2>/dev/null || echo "")"
                    if [[ -n "$route_id" ]]; then
                        $headscale_cmd routes reject -r "$route_id" 2>/dev/null
                    fi
                fi
                ;;
            *) return 1 ;;
        esac
        return $?
    fi

    local api_url="${HEADSCALE_URL%/}/api/v1${endpoint}"
    local curl_args=(-s -X "$method" -H "Authorization: Bearer ${HEADSCALE_API_KEY}" -H "Content-Type: application/json")

    if [[ -n "$data" ]]; then
        curl_args+=(-d "$data")
    fi

    curl "${curl_args[@]}" "$api_url"
}

# -- List routes -------------------------------------------------------------
list_routes() {
    local filter_node="$1"
    local pending_only="$2"

    local raw
    raw="$(api_call "GET" "/routes" || echo '{"routes":[]}')"

    python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    data = {'routes': []}

routes = data if isinstance(data, list) else data.get('routes', [])

filter_node = '$filter_node'
if filter_node:
    routes = [r for r in routes if str(r.get('node', {}).get('id', '')).lower() == filter_node.lower() or str(r.get('node', {}).get('name', '')).lower() == filter_node.lower()]

pending_only = '${pending_only}'
if pending_only == 'true':
    routes = [r for r in routes if r.get('status', '').lower() in ('pending', 'advertised')]

output = {'routes': routes}
print(json.dumps(output, indent=2))
" <<< "$raw"
}

# -- Approve route -----------------------------------------------------------
approve_route() {
    local route_id="$1"
    local data='{"route_id": "'"$route_id"'"}'

    if [[ "$DRY_RUN" == true ]]; then
        if [[ "$JSON" == true ]]; then
            echo '{"dry_run":true,"action":"approve","route_id":"'"$route_id"'"}'
        else
            echo "[DRY-RUN] Would approve route ID: $route_id"
        fi
        return 0
    fi

    api_call "POST" "/routes/$route_id/approve"
}

# -- Approve all -------------------------------------------------------------
approve_all() {
    local raw
    raw="$(list_routes "" "true")"

    local pending_ids
    pending_ids="$(echo "$raw" | python3 -c "
import sys, json
data = json.load(sys.stdin)
routes = data.get('routes', [])
ids = [str(r.get('id')) for r in routes if r.get('id')]
print(' '.join(ids))
" 2>/dev/null || true)"

    if [[ -z "$pending_ids" ]]; then
        if [[ "$JSON" == true ]]; then
            echo '{"status":"ok","approved":0,"message":"No pending routes to approve"}'
        else
            echo "No pending routes to approve."
        fi
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        if [[ "$JSON" == true ]]; then
            echo '{"dry_run":true,"action":"approve-all","route_ids":["'"$(echo "$pending_ids" | sed 's/ /","/g')"'"]}'
        else
            echo "[DRY-RUN] Would approve routes: $pending_ids"
        fi
        return 0
    fi

    local count=0
    for rid in $pending_ids; do
        approve_route "$rid" >/dev/null 2>&1 || true
        count=$((count + 1))
    done

    if [[ "$JSON" == true ]]; then
        echo '{"status":"ok","approved":'"$count"'}'
    else
        echo "Approved $count route(s)"
    fi
}

# -- Reject route ------------------------------------------------------------
reject_route() {
    local route_id="$1"

    if [[ "$DRY_RUN" == true ]]; then
        if [[ "$JSON" == true ]]; then
            echo '{"dry_run":true,"action":"reject","route_id":"'"$route_id"'"}'
        else
            echo "[DRY-RUN] Would reject route ID: $route_id"
        fi
        return 0
    fi

    local data='{"route_id": "'"$route_id"'"}'
    api_call "POST" "/routes/$route_id/reject"
}

# -- Main --------------------------------------------------------------------
case "$ACTION" in
    list)
        RAW="$(list_routes "$NODE" "$(echo "$PENDING_ONLY" | tr '[:upper:]' '[:lower:]')")"
        format_routes "$RAW"
        ;;
    approve)
        approve_route "$ACTION_ARG"
        ;;
    approve-all)
        approve_all
        ;;
    reject)
        reject_route "$ACTION_ARG"
        ;;
esac
