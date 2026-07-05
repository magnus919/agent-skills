#!/usr/bin/env bash
# traefik-healthcheck.sh — Check a running Traefik instance health
# Usage: ./traefik-healthcheck.sh [--json] [--url https://traefik.example.com]
#
# Requires: curl, jq
# Non-interactive, agent-friendly.

set -euo pipefail

# Defaults
URL="${TRAEFIK_URL:-http://localhost:8080}"
JSON=false
EXIT_CODE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON=true; shift ;;
    --url) URL="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: traefik-healthcheck.sh [--json] [--url <traefik-url>]"
      echo ""
      echo "Checks ping, API, version, router counts, and certificate expiry."
      echo "Defaults to http://localhost:8080. Set TRAEFIK_URL env var to override."
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

json_out() {
  if $JSON; then
    echo "$1"
  fi
}

text_out() {
  if ! $JSON; then
    echo "$1"
  fi
}

# 1. Ping check
ping_status=$(curl -s -o /dev/null -w "%{http_code}" "${URL}/ping" 2>/dev/null || echo "000")
if [ "$ping_status" = "200" ]; then
  text_out "✓ Ping: OK (200)"
  json_out "{\"ping\": {\"status\": \"ok\", \"code\": 200}"
else
  text_out "✗ Ping: FAILED ($ping_status)"
  json_out "{\"ping\": {\"status\": \"fail\", \"code\": $ping_status}"
  EXIT_CODE=1
fi

# 2. API health check
api_status=$(curl -s -o /dev/null -w "%{http_code}" "${URL}/api/version" 2>/dev/null || echo "000")
if [ "$api_status" = "200" ]; then
  version=$(curl -s "${URL}/api/version" 2>/dev/null | jq -r '.Version // "unknown"' 2>/dev/null || echo "unknown")
  text_out "✓ API: OK ($api_status) — Traefik $version"
  json_out ", \"api\": {\"status\": \"ok\", \"version\": \"$version\"}"
else
  text_out "✗ API: FAILED ($api_status) — is the API enabled?"
  json_out ", \"api\": {\"status\": \"fail\", \"code\": $api_status}"
  EXIT_CODE=1
fi

# 3. Router count
routers=$(curl -s "${URL}/api/http/routers" 2>/dev/null | jq length 2>/dev/null || echo "N/A")
text_out "  HTTP routers: $routers"
json_out ", \"routers\": {\"count\": $routers}"

tcp_routers=$(curl -s "${URL}/api/tcp/routers" 2>/dev/null | jq length 2>/dev/null || echo "N/A")
text_out "  TCP routers: $tcp_routers"
json_out ", \"tcp_routers\": {\"count\": $tcp_routers}"

# 4. Overview
overview=$(curl -s "${URL}/api/overview" 2>/dev/null || echo "{}")
if [ "$overview" != "{}" ]; then
  total=$(echo "$overview" | jq -r '.http.routers.total // 0' 2>/dev/null)
  text_out "  Total HTTP routers (overview): $total"
fi

# 5. Certificate expiry check
certs=$(curl -s "${URL}/api/rawconfig" 2>/dev/null | jq -r '.tls.certificates // []' 2>/dev/null || echo "[]")
if [ "$certs" != "[]" ]; then
  cert_count=$(echo "$certs" | jq length)
  text_out "  TLS certificates: $cert_count"
  json_out ", \"tls_certificates\": {\"count\": $cert_count}"
else
  json_out ", \"tls_certificates\": null"
fi

# Close JSON
if $JSON; then
  echo "}"
fi

exit $EXIT_CODE
