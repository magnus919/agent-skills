#!/usr/bin/env bash
#
# configure-derp.sh — Configure embedded DERP server in Headscale
#
# Usage:
#   configure-derp.sh [--enable|--disable] [--region-id <id>] [--region-name <name>]
#                     [--relay-port <port>] [--config-path <path>] [--test-connectivity]
#                     [--dry-run] [--json]
#
# Options:
#   --enable              Enable embedded DERP relay in config
#   --disable             Disable embedded DERP relay
#   --region-id <id>      Numeric region ID (default: 999)
#   --region-name <name>  Human-readable region name (default: "my-headscale")
#   --relay-port <port>   STUN/Relay UDP port (default: 3478)
#   --config-path <path>  Path to headscale config.yaml (default: /etc/headscale/config.yaml)
#   --test-connectivity   Run connectivity test after configuration change
#   --dry-run             Preview changes without applying
#   --json                Output structured JSON
#   --help                Show this help and exit
#
# Examples:
#   configure-derp.sh --enable --region-id 1 --region-name "us-east"      # enable DERP
#   configure-derp.sh --disable --dry-run                                 # preview disable
#   configure-derp.sh --enable --test-connectivity --json                  # enable + test + JSON
#   configure-derp.sh --region-id 2 --region-name "eu-west" --dry-run     # preview region change

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
CONFIG_PATH="/etc/headscale/config.yaml"
ENABLE=""
DISABLE=""
REGION_ID="999"
REGION_NAME="my-headscale"
RELAY_PORT="3478"
TEST_CONNECTIVITY=false
DRY_RUN=false
JSON=false

# ── Argument parsing ──────────────────────────────────────────────────────────

usage() {
  sed -n '2,31p' "$0" | sed 's/^# //; s/^#$//'
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --enable)             ENABLE=true; shift ;;
    --disable)            DISABLE=true; shift ;;
    --region-id)          REGION_ID="$2"; shift 2 ;;
    --region-name)        REGION_NAME="$2"; shift 2 ;;
    --relay-port)         RELAY_PORT="$2"; shift 2 ;;
    --config-path)        CONFIG_PATH="$2"; shift 2 ;;
    --test-connectivity)  TEST_CONNECTIVITY=true; shift ;;
    --dry-run)            DRY_RUN=true; shift ;;
    --json)               JSON=true; shift ;;
    --help)               usage ;;
    *)                    echo "Unknown option: $1" >&2; usage ;;
  esac
done

# ── Helpers ───────────────────────────────────────────────────────────────────

log()   { if ! $JSON; then echo "[${SCRIPT_NAME}] $*"; fi }
err()   { echo "[${SCRIPT_NAME}] ERROR: $*" >&2; }
info()  { if ! $JSON; then echo "  $*"; fi }

json_out() {
  if $JSON; then echo "$1"; fi
}

validate_config_exists() {
  if [[ ! -f "$CONFIG_PATH" ]]; then
    err "Config file not found: $CONFIG_PATH"
    json_out '{"error":"config_not_found","config_path":"'"$CONFIG_PATH"'"}'
    exit 1
  fi
}

# ── YAML manipulation (basic, using python3) ─────────────────────────────────

yaml_set() {
  local key="$1" value="$2"
  python3 -c "
import yaml, sys

with open('$CONFIG_PATH') as f:
    data = yaml.safe_load(f)

# Navigate dotted keys like 'derp.server.enabled'
parts = '$key'.split('.')
d = data
for p in parts[:-1]:
    if p not in d or d[p] is None:
        d[p] = {}
    d = d[p]
d[parts[-1]] = $value

with open('$CONFIG_PATH', 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
" 2>/dev/null
}

yaml_get() {
  local key="$1"
  python3 -c "
import yaml, sys

with open('$CONFIG_PATH') as f:
    data = yaml.safe_load(f)

parts = '$key'.split('.')
d = data
for p in parts:
    if isinstance(d, dict):
        d = d.get(p)
    else:
        d = None
        break

if d is None:
    sys.exit(1)
elif isinstance(d, bool):
    print(str(d).lower())
else:
    print(d)
" 2>/dev/null || echo "null"
}

# ── Connectivity test ────────────────────────────────────────────────────────

test_connectivity() {
  log "Testing DERP connectivity..."
  local server_url
  server_url="$(yaml_get server_url)"

  if [[ "$server_url" == "null" || -z "$server_url" ]]; then
    err "Cannot test connectivity: server_url not found in config"
    return 1
  fi

  local health_result derp_result
  health_result="$(curl -sSf --connect-timeout 5 "$server_url/health" 2>&1 || true)"
  derp_result="$(curl -sSf --connect-timeout 5 "$server_url/derp" 2>&1 || true)"

  if echo "$health_result" | grep -qi "ok\|healthy" 2>/dev/null; then
    info "Health endpoint: OK"
  else
    info "Health endpoint: UNREACHABLE ($health_result)"
  fi

  if [[ -n "$derp_result" ]]; then
    info "DERP endpoint: RESPONDED"
  else
    info "DERP endpoint: NO RESPONSE"
  fi

  # Return combined status
  if echo "$health_result" | grep -qi "ok\|healthy" 2>/dev/null; then
    echo "healthy"
  else
    echo "unhealthy"
  fi
}

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
  validate_config_exists

  # Determine action
  local action="preview"
  if [[ "$ENABLE" == "true" ]]; then
    action="enable"
  elif [[ "$DISABLE" == "true" ]]; then
    action="disable"
  fi

  # Read current values
  local current_enabled current_region_id current_region_name current_stun_addr
  current_enabled="$(yaml_get derp.server.enabled)"
  current_region_id="$(yaml_get derp.server.region_id)"
  current_region_name="$(yaml_get derp.server.region_name)"
  current_stun_addr="$(yaml_get derp.server.stun_listen_addr)"

  if $JSON; then
    log ""
  fi

  log "Current DERP config:"
  info "  enabled:      ${current_enabled:-null}"
  info "  region_id:    ${current_region_id:-null}"
  info "  region_name:  ${current_region_name:-null}"
  info "  stun_addr:    ${current_stun_addr:-null}"

  if $DRY_RUN; then
    log "[DRY-RUN] Would apply the following changes:"
    if [[ "$action" == "enable" ]]; then
      info "  derp.server.enabled = true"
      info "  derp.server.region_id = $REGION_ID"
      info "  derp.server.region_name = $REGION_NAME"
      info "  derp.server.stun_listen_addr = 0.0.0.0:$RELAY_PORT"
    elif [[ "$action" == "disable" ]]; then
      info "  derp.server.enabled = false"
    else
      info "  No change requested (use --enable or --disable)"
    fi

    json_out '{"action":"'"$action"'","dry_run":true,"config_path":"'"$CONFIG_PATH"'","current":{"enabled":'"${current_enabled:-false}"',"region_id":'"${current_region_id:-0}"',"region_name":"'"${current_region_name:-}"'"},"proposed":{"enabled":'"${ENABLE:-false}"',"region_id":'"$REGION_ID"',"region_name":"'"$REGION_NAME"'","relay_port":'"$RELAY_PORT"'}}'
    return 0
  fi

  # Apply changes
  if [[ "$action" == "enable" ]]; then
    log "Enabling embedded DERP server..."
    yaml_set derp.server.enabled true
    yaml_set derp.server.region_id "$REGION_ID"
    yaml_set derp.server.region_name "\"$REGION_NAME\""
    yaml_set derp.server.stun_listen_addr "\"0.0.0.0:$RELAY_PORT\""
    log "DERP server configured: region $REGION_ID ($REGION_NAME), port $RELAY_PORT/udp"
    log "Note: Restart headscale to apply changes"

  elif [[ "$action" == "disable" ]]; then
    log "Disabling embedded DERP server..."
    yaml_set derp.server.enabled false
    log "DERP server disabled. Restart headscale to apply changes"

  else
    err "No action specified. Use --enable or --disable."
    usage
  fi

  # Connectivity test
  local connectivity_status="not_tested"
  if $TEST_CONNECTIVITY; then
    connectivity_status="$(test_connectivity || echo 'failed')"
  fi

  # Read back final values
  local final_enabled final_region_id final_region_name
  final_enabled="$(yaml_get derp.server.enabled)"
  final_region_id="$(yaml_get derp.server.region_id)"
  final_region_name="$(yaml_get derp.server.region_name)"

  json_out '{"action":"'"$action"'","dry_run":false,"config_path":"'"$CONFIG_PATH"'","applied":{"enabled":'"${final_enabled:-false}"',"region_id":'"${final_region_id:-0}"',"region_name":"'"${final_region_name:-}"'"},"connectivity":"'"$connectivity_status"'"}'
}

main
