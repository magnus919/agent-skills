#!/usr/bin/env bash
set -euo pipefail

# headscale-health-check.sh — Probe Headscale server health
SCRIPT_NAME="$(basename "$0")"
JSON_OUTPUT=false
WATCH=false
INTERVAL=5
URL="${HEADSCALE_URL:-}"
API_KEY="${HEADSCALE_API_KEY:-}"

usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Probe Headscale server health and return diagnostics.

Options:
  --json          Output as JSON
  --watch         Continuous monitoring every --interval seconds
  --interval N    Polling interval in seconds (default: 5)
  --url URL       Headscale server URL (default: \$HEADSCALE_URL)
  --api-key KEY   Headscale API key (default: \$HEADSCALE_API_KEY)
  --help          Show this help

Examples:
  $SCRIPT_NAME
  $SCRIPT_NAME --json
  $SCRIPT_NAME --watch --interval 10
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON_OUTPUT=true; shift ;;
    --watch) WATCH=true; shift ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    --url) URL="$2"; shift 2 ;;
    --api-key) API_KEY="$2"; shift 2 ;;
    --help) usage ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$URL" ]]; then
  echo "Error: HEADSCALE_URL not set. Pass --url or set HEADSCALE_URL env var." >&2
  exit 1
fi

do_health_check() {
  local result
  local version=""
  local healthy=false
  local api_ok=false

  # Check /version endpoint
  version_info=$(curl -s -f "${URL}/version" 2>/dev/null) && version="$version_info" || true

  # Check API
  if [[ -n "$API_KEY" ]]; then
    api_result=$(curl -s -w "%{http_code}" -H "Authorization: Bearer $API_KEY" "${URL}/api/v1/user" 2>/dev/null) || true
    http_code="${api_result: -3}"
    if [[ "$http_code" == "200" ]]; then
      api_ok=true
    fi
  fi

  # Overall health
  if [[ -n "$version" ]]; then
    healthy=true
  fi

  if [[ "$JSON_OUTPUT" == true ]]; then
    cat <<JSONEOF
{
  "url": "$URL",
  "healthy": $healthy,
  "version": "${version:-unknown}",
  "api_ok": $api_ok,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSONEOF
  else
    echo "=== Headscale Health Check ==="
    echo "URL:     $URL"
    echo "Healthy: $healthy"
    echo "Version: ${version:-unknown}"
    echo "API:     $([ "$api_ok" == true ] && echo 'OK' || echo 'UNKNOWN (no API key)')"
  fi
}

if [[ "$WATCH" == true ]]; then
  while true; do
    do_health_check
    echo "---"
    sleep "$INTERVAL"
  done
else
  do_health_check
fi
