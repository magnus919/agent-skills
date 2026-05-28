#!/usr/bin/env bash
#
# headscale-health-check.sh — Comprehensive health probe for Headscale
#
# Usage:
#   headscale-health-check.sh [--json] [--watch] [--interval <sec>] [--api-key <key>]
#                             [--url <url>] [--config-path <path>] [--help]
#
# Options:
#   --json              Output structured JSON (default: human-readable)
#   --watch             Continuous monitoring mode (repeats every --interval)
#   --interval <sec>    Polling interval in seconds for --watch (default: 30)
#   --api-key <key>     Headscale API key (lazy auth: reads HEADSCALE_API_KEY env)
#   --url <url>         Headscale server URL (lazy auth: reads HEADSCALE_URL env)
#   --config-path <path> Path to headscale config.yaml (default: /etc/headscale/config.yaml)
#   --help              Show this help and exit
#
# Examples:
#   headscale-health-check.sh                                         # human-readable
#   HEADSCALE_URL=https://hs.example.com headscale-health-check.sh    # via env var
#   headscale-health-check.sh --json                                  # structured output
#   headscale-health-check.sh --watch --interval 60                   # monitor every 60s
#   headscale-health-check.sh --url https://hs.example.com --api-key k-xxx  # explicit

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
JSON=false
WATCH=false
INTERVAL=30
API_KEY=""
SERVER_URL=""
CONFIG_PATH="/etc/headscale/config.yaml"

# ── Argument parsing ──────────────────────────────────────────────────────────

usage() {
  sed -n '2,27p' "$0" | sed 's/^# //; s/^#$//'
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)             JSON=true; shift ;;
    --watch)            WATCH=true; shift ;;
    --interval)         INTERVAL="$2"; shift 2 ;;
    --api-key)          API_KEY="$2"; shift 2 ;;
    --url)              SERVER_URL="$2"; shift 2 ;;
    --config-path)      CONFIG_PATH="$2"; shift 2 ;;
    --help)             usage ;;
    *)                  echo "Unknown option: $1" >&2; usage ;;
  esac
done

# ── Helpers ───────────────────────────────────────────────────────────────────

log()     { if ! $JSON; then echo "[${SCRIPT_NAME}] $*"; fi }
err()     { echo "[${SCRIPT_NAME}] ERROR: $*" >&2; }
out()     { if ! $JSON; then echo "$*"; fi }

json_out() {
  if $JSON; then echo "$1"; fi
}

derive_url_and_key() {
  # Lazy auth: env vars, then config file, then explicit params
  if [[ -z "$SERVER_URL" ]]; then
    SERVER_URL="${HEADSCALE_URL:-}"
  fi
  if [[ -z "$API_KEY" ]]; then
    API_KEY="${HEADSCALE_API_KEY:-}"
  fi

  # Try reading from config file if still empty
  if [[ -z "$SERVER_URL" && -f "$CONFIG_PATH" ]]; then
    SERVER_URL="$(python3 -c "
import yaml
with open('$CONFIG_PATH') as f:
    d = yaml.safe_load(f)
print(d.get('server_url', ''))
" 2>/dev/null || true)"
  fi

  # Try running headscale binary for URL if available
  if [[ -z "$SERVER_URL" ]] && command -v headscale &>/dev/null; then
    SERVER_URL="$(headscale config 2>/dev/null | grep 'server_url' | awk '{print $2}' || true)"
  fi

  if [[ -z "$SERVER_URL" ]]; then
    err "Cannot determine Headscale server URL. Set HEADSCALE_URL, pass --url, or ensure config at $CONFIG_PATH"
    return 1
  fi

  return 0
}

# ── Health checks ─────────────────────────────────────────────────────────────

check_health_endpoint() {
  local url="${SERVER_URL}/health"
  local result
  result="$(curl -sSf --connect-timeout 5 --max-time 10 "$url" 2>&1 || true)"
  if echo "$result" | grep -qi "ok\|healthy\|200" 2>/dev/null; then
    echo "true"
  else
    echo "false"
  fi
}

check_version_endpoint() {
  local url="${SERVER_URL}/version"
  local result
  result="$(curl -sSf --connect-timeout 5 --max-time 10 "$url" 2>&1 || true)"
  if [[ -n "$result" ]] && ! echo "$result" | grep -qi "error\|not found\|404"; then
    echo "$result" | head -1
  else
    echo "unknown"
  fi
}

check_api_key() {
  if [[ -z "$API_KEY" ]]; then
    echo "no_key"
    return
  fi

  local url="${SERVER_URL}/api/v1/apikey"
  local result
  result="$(curl -sSf --connect-timeout 5 --max-time 10 \
    -H "Authorization: Bearer ${API_KEY}" \
    "${url}" 2>&1 || true)"

  if echo "$result" | grep -qi "valid\|ok\|200" 2>/dev/null; then
    echo "valid"
  elif echo "$result" | grep -qi "unauthorized\|invalid\|401\|403" 2>/dev/null; then
    echo "invalid"
  else
    echo "unknown"
  fi
}

get_node_count() {
  if [[ -z "$API_KEY" ]]; then
    echo "-1"
    return
  fi

  local url="${SERVER_URL}/api/v1/node"
  local result
  result="$(curl -sSf --connect-timeout 5 --max-time 10 \
    -H "Authorization: Bearer ${API_KEY}" \
    "${url}" 2>&1 || true)"

  echo "$result" | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
    print(len(d.get('nodes',[])))
except:
    print('-1')
" 2>/dev/null || echo "-1"
}

check_db_integrity() {
  if command -v headscale &>/dev/null; then
    local result
    result="$(headscale db stats 2>&1 || true)"
    if echo "$result" | grep -qi "error\|failed\|corrupt" 2>/dev/null; then
      echo "false"
    elif [[ -n "$result" ]]; then
      echo "true"
    else
      echo "unknown"
    fi
  else
    echo "unknown"
  fi
}

check_derp_endpoint() {
  local url="${SERVER_URL}/derp"
  local result
  result="$(curl -sSf --connect-timeout 5 --max-time 10 "$url" 2>&1 || true)"
  if [[ -n "$result" ]] && ! echo "$result" | grep -qi "error\|not found\|404\|refused"; then
    echo "true"
  else
    echo "false"
  fi
}

get_uptime() {
  if command -v headscale &>/dev/null; then
    headscale debug stats 2>/dev/null | grep -i "uptime" | awk '{print $NF}' || echo "unknown"
  else
    echo "unknown"
  fi
}

# ── Run check ─────────────────────────────────────────────────────────────────

run_health_check() {
  if ! derive_url_and_key; then
    if $JSON; then
      json_out '{"healthy":false,"error":"cannot_determine_url"}'
    else
      err "Cannot determine Headscale server URL."
      err "Set HEADSCALE_URL environment variable or pass --url."
    fi
    return 1
  fi

  local healthy=true
  local health_ok version_str api_status db_ok derp_ok node_count uptime

  health_ok="$(check_health_endpoint)"
  version_str="$(check_version_endpoint)"
  api_status="$(check_api_key)"
  node_count="$(get_node_count)"
  db_ok="$(check_db_integrity)"
  derp_ok="$(check_derp_endpoint)"
  uptime="$(get_uptime)"

  if [[ "$health_ok" != "true" ]]; then
    healthy=false
  fi

  if $JSON; then
    json_out '{"version":"'"${version_str}"'","healthy":'"${healthy}"',"nodes":'"${node_count}"',"db_ok":'"${db_ok}"',"api_ok":"'"${api_status}"'","derp_ok":'"${derp_ok}"',"health_endpoint":'"${health_ok}"',"uptime":"'"${uptime}"'"}'
  else
    out "========================================"
    out "       Headscale Health Report          "
    out "========================================"
    out "  Server URL:       ${SERVER_URL}"
    out "  Version:          ${version_str}"
    out "  Health Endpoint:  ${health_ok}"
    out "  API Key:          ${api_status}"
    out "  Nodes:            ${node_count}"
    out "  DB Integrity:     ${db_ok}"
    out "  DERP Relay:       ${derp_ok}"
    out "  Uptime:           ${uptime}"
    out "----------------------------------------"
    if $healthy; then
      out "  STATUS: HEALTHY"
    else
      out "  STATUS: CHECK FAILURES DETECTED"
    fi
    out "========================================"
  fi
}

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
  if $WATCH; then
    log "Watching Headscale health every ${INTERVAL}s (Ctrl+C to stop)..."
    while true; do
      run_health_check || true
      sleep "$INTERVAL"
    done
  else
    run_health_check
  fi
}

main
