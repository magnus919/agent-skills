#!/usr/bin/env bash
# ===========================================================================
# headscale-derp: test-derp-latency.sh — Measure latency to DERP regions
# ===========================================================================
# Runs `tailscale netcheck` and parses results to report DERP region latency.
#
# Usage:
#   test-derp-latency.sh [--region-id <ID>] [--json] [--help]
#
# Options:
#   --region-id   Test only a specific DERP region by ID (e.g., 900).
#   --json        Output structured JSON with per-region latency data.
#   --help        Show this help message and exit.
#
# Examples:
#   test-derp-latency.sh
#   test-derp-latency.sh --region-id 900
#   test-derp-latency.sh --region-id 900 --json
#   test-derp-latency.sh --json
# ===========================================================================

set -euo pipefail

# --- Constants ---
SCRIPT_NAME="$(basename "$0")"

# --- Colors ---
if [[ -t 2 ]]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; CYAN=''; NC=''
fi

log_info()  { echo -e "${GREEN}[INFO]${NC} $*" >&2; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# --- Help ---
usage() {
    cat <<EOF
Usage: ${SCRIPT_NAME} [OPTIONS]

Run tailscale netcheck and report DERP region latency.

Options:
  --region-id <ID>  Test only a specific DERP region by numeric ID.
  --json            Output structured JSON with per-region latency data.
  --help            Show this help message and exit.

Examples:
  ${SCRIPT_NAME}
  ${SCRIPT_NAME} --region-id 900
  ${SCRIPT_NAME} --region-id 900 --json
  ${SCRIPT_NAME} --json
EOF
    exit 0
}

# --- Parse arguments ---
REGION_ID=""
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --region-id)   REGION_ID="$2"; shift 2 ;;
        --json)        JSON_OUTPUT=true; shift ;;
        --help|-h)     usage ;;
        *) log_error "Unknown argument: $1"; usage ;;
    esac
done

# --- Check prerequisites ---
if ! command -v tailscale &>/dev/null; then
    log_error "tailscale command not found. Is Tailscale installed?"
    exit 1
fi

# --- Run netcheck ---
log_info "Running tailscale netcheck..."
NETCHECK_OUTPUT=$(tailscale netcheck 2>&1) || {
    log_error "tailscale netcheck failed (exit code $?)"
    log_error "Output: ${NETCHECK_OUTPUT}"
    exit 1
}

# --- Parse netcheck output ---
# Expected format (example):
#   Report:
#       * UDP: true
#       * IPv4: yes
#       * ...
#       * DERP latency:
#           - dallas: 18ms (dallas)
#           - us-west: 35ms (us-west)
#           - new-york-city: 5ms (new-york-city)

parse_regions() {
    local in_derp_section=false
    local regions_json="["
    local first=true

    while IFS= read -r line; do
        # Detect start of DERP latency section
        if [[ "$line" =~ DERP\ latency: ]]; then
            in_derp_section=true
            continue
        fi

        if [[ "$in_derp_section" == "true" ]]; then
            # Break on next top-level line that doesn't start with whitespace/dash
            if [[ ! "$line" =~ ^[[:space:]]*-[[:space:]] ]]; then
                break
            fi

            # Parse: "- region_code: XXms (region_code)"
            if [[ "$line" =~ ^[[:space:]]*-\ ([^:]+):[[:space:]]*([0-9]+)ms ]]; then
                local region_name="${BASH_REMATCH[1]}"
                local latency_ms="${BASH_REMATCH[2]}"

                # Map display name to region code
                local region_code="$region_name"
                # Clean up common display names
                region_code=$(echo "$region_code" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')

                if [[ -z "$REGION_ID" ]]; then
                    if [[ "$first" == true ]]; then first=false; else regions_json+=","; fi
                    regions_json+=$(cat <<JSON
                    {
                        "region_code": "${region_code}",
                        "region_name": "${region_name}",
                        "latency_ms": ${latency_ms}
                    }
JSON
)
                fi
            fi
        fi
    done <<< "$NETCHECK_OUTPUT"

    regions_json+="]"
    echo "$regions_json"
}

# --- Parse netcheck JSON if available (preferred) ---
parse_netcheck_json_if_available() {
    # tailscale netcheck supports --json in newer versions
    local json
    json=$(tailscale netcheck --json 2>/dev/null) || return 1
    echo "$json"
    return 0
}

# --- Extract UDP/IPv4 info ---
extract_field() {
    local field="$1"
    local value
    value=$(echo "$NETCHECK_OUTPUT" | grep -i "\* ${field}:" | head -1 | sed "s/.*:\s*//")
    echo "$value"
}

# --- Main ---
UDP_STATUS=$(extract_field "UDP")
IPV4_STATUS=$(extract_field "IPv4")
IPV6_STATUS=$(extract_field "IPv6")
NEAREST_DERP=$(echo "$NETCHECK_OUTPUT" | grep -i "Nearest DERP" | head -1 | sed "s/.*Nearest DERP: //")

# Try to get structured JSON via --json flag
PARSED_JSON=""
if PARSED_JSON=$(parse_netcheck_json_if_available); then
    # If we have structured data from netcheck --json, use it
    if [[ -n "$REGION_ID" ]]; then
        log_info "Filtering for region ID: ${REGION_ID}"
        # Filter regions by ID if netcheck --json was used (returns node IDs)
        PARSED_JSON=$(echo "$PARSED_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
regions = {k: v for k, v in data.get('Region', data.get('Regions', {})).items()}
filter_id = '${REGION_ID}'
target = {k: v for k, v in regions.items() if str(k) == str(filter_id)}
if not target:
    print(json.dumps({'filtered': True, 'region_id': int(filter_id), 'regions': {}, 'found': False}))
else:
    print(json.dumps({'filtered': True, 'region_id': int(filter_id), 'regions': target, 'found': True}))
" 2>/dev/null)
    fi

    if [[ "$JSON_OUTPUT" == true ]]; then
        echo "$PARSED_JSON"
    else
        echo "=== DERP Latency Report ==="
        echo "UDP:        ${UDP_STATUS:-unknown}"
        echo "IPv4:       ${IPV4_STATUS:-unknown}"
        echo "IPv6:       ${IPV6_STATUS:-unknown}"
        echo "Nearest:    ${NEAREST_DERP:-unknown}"
        echo ""
        echo "--- DERP Regions (by latency) ---"
        python3 -c "
import json, sys
data = json.load(sys.stdin)
regions = data.get('Region', data.get('Regions', {}))
sorted_regions = sorted(regions.items(), key=lambda x: x[1].get('Latency', 99999))
for rid, rdata in sorted_regions:
    code = rdata.get('RegionCode', '?')
    name = rdata.get('RegionName', '?')
    lat = rdata.get('Latency', 'N/A')
    if lat != 'N/A':
        print(f\"  {rid:>4}  {code:<15}  {name:<20}  {lat:.0f}ms\")
    else:
        print(f\"  {rid:>4}  {code:<15}  {name:<20}  unreachable\")
" 2>/dev/null <<< "$PARSED_JSON"
    fi
else
    # Fallback: manually parse text output
    if [[ "$JSON_OUTPUT" == true ]]; then
        # Build JSON from text parsing
        REGIONS_JSON=$(parse_regions)
        cat <<JSONEOF
{
  "status": "ok",
  "script": "${SCRIPT_NAME}",
  "region_filter": $( [[ -n "$REGION_ID" ]] && echo "$REGION_ID" || echo null ),
  "connectivity": {
    "udp": $( [[ "${UDP_STATUS,,}" == "true" ]] && echo true || echo false ),
    "ipv4": $( [[ "${IPV4_STATUS,,}" == "true" || "${IPV4_STATUS,,}" == "yes" ]] && echo true || echo false ),
    "ipv6": $( [[ "${IPV6_STATUS,,}" == "true" || "${IPV6_STATUS,,}" == "yes" ]] && echo true || echo false )
  },
  "nearest_derp": "${NEAREST_DERP:-unknown}",
  "regions": ${REGIONS_JSON}
}
JSONEOF
    else
        echo "=== DERP Latency Report ==="
        echo "UDP:        ${UDP_STATUS:-unknown}"
        echo "IPv4:       ${IPV4_STATUS:-unknown}"
        echo "IPv6:       ${IPV6_STATUS:-unknown}"
        echo "Nearest:    ${NEAREST_DERP:-unknown}"
        echo ""
        echo "--- DERP Regions (ranked by latency) ---"

        # Parse and sort regions
        echo "$NETCHECK_OUTPUT" | while IFS= read -r line; do
            if [[ "$line" =~ ^[[:space:]]*-\ ([^:]+):[[:space:]]*([0-9]+)ms ]]; then
                local name="${BASH_REMATCH[1]}"
                local lat="${BASH_REMATCH[2]}"
                printf "  %4sms  %s\n" "$lat" "$name"
            fi
        done | sort -n
    fi
fi
