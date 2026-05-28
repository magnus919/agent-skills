#!/usr/bin/env bash
set -euo pipefail

# hs-list-nodes.sh — List all nodes in the Headscale tailnet
#
# Usage:
#   hs-list-nodes.sh [--json] [--user <user>] [--tag <tag>] [--online-only] [--help]
#
# Options:
#   --json         Output raw JSON from the API
#   --user <user>  Filter by user (personal or tagged-devices)
#   --tag <tag>    Filter by tag (e.g. webserver)
#   --online-only  Show only online nodes
#   --help         Show this help message

usage() {
  sed -n '/^# Usage:/,/^$/{ s/^#//p; }' "$0"
  echo ""
  echo "Examples:"
  echo "  hs-list-nodes.sh"
  echo "  hs-list-nodes.sh --online-only"
  echo "  hs-list-nodes.sh --user tagged-devices"
  echo "  hs-list-nodes.sh --tag webserver --json"
  echo "  hs-list-nodes.sh --online-only --json"
  exit "${1:-0}"
}

JSON_MODE=false
USER_FILTER=""
TAG_FILTER=""
ONLINE_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)       JSON_MODE=true; shift ;;
    --user)       shift; USER_FILTER="$1"; shift ;;
    --tag)        shift; TAG_FILTER="$1"; shift ;;
    --online-only) ONLINE_ONLY=true; shift ;;
    --help)       usage 0 ;;
    *)            echo "ERROR: Unknown option: $1" >&2; usage 1 ;;
  esac
done

# ---------------------------------------------------------------------------
# Try headscale CLI first
# ---------------------------------------------------------------------------
if command -v headscale &>/dev/null; then
  HEADSCALE_CMD=(headscale)
  if [[ -n "${HEADSCALE_URL:-}" ]]; then
    HEADSCALE_CMD+=(--url "$HEADSCALE_URL")
  fi

  # List nodes with user info
  HEADSCALE_CMD+=(nodes list --output json)

  NODES=$("${HEADSCALE_CMD[@]}" 2>/dev/null || true)

  if [[ -z "$NODES" ]]; then
    echo "No nodes found." >&2
    exit 0
  fi

  # Apply filters using jq
  FILTER="."
  if [[ -n "$USER_FILTER" ]]; then
    FILTER="$FILTER | map(select(.user.name == \"$USER_FILTER\" or .user == \"$USER_FILTER\"))"
  fi
  if [[ -n "$TAG_FILTER" ]]; then
    FILTER="$FILTER | map(select(.tags // [] | index(\"tag:$TAG_FILTER\") != null))"
  fi
  if $ONLINE_ONLY; then
    FILTER="$FILTER | map(select(.online == true))"
  fi

  FILTERED=$(echo "$NODES" | jq "$FILTER" 2>/dev/null || echo "$NODES")

  if $JSON_MODE; then
    echo "$FILTERED"
    exit 0
  fi

  # Pretty-print tabular output
  echo "$FILTERED" | jq -r '
    (["ID", "NAME", "IP", "USER", "TAGS", "ONLINE", "LAST_SEEN", "OS", "VERSION"]
    | join(" | ")),
    (.[] | [
      (.id // "?" | tostring),
      (.givenName // .name // "?"),
      (.ipAddresses // [] | join(",") // "?"),
      (.user.name // .user // "?"),
      ((.tags // []) | join(",") // "-"),
      (if .online then "✓" else "✗" end),
      (.lastSeen // "?"),
      (.hostInfo.os // "?"),
      (.clientVersion // "?")
    ] | join(" | "))
  ' | column -s '|' -t

  exit 0
fi

# ---------------------------------------------------------------------------
# Fallback: REST API via curl
# ---------------------------------------------------------------------------
if [[ -z "${HEADSCALE_URL:-}" || -z "${HEADSCALE_API_KEY:-}" ]]; then
  echo "ERROR: headscale CLI not found. Set HEADSCALE_URL and HEADSCALE_API_KEY env vars for API fallback." >&2
  exit 1
fi

API="${HEADSCALE_URL}/api/v1"

# Build query params
QUERY_PARAMS=()
if [[ -n "$USER_FILTER" ]]; then
  QUERY_PARAMS+=("user=$USER_FILTER")
fi

QUERY=""
if [[ ${#QUERY_PARAMS[@]} -gt 0 ]]; then
  QUERY="?$(IFS='&'; echo "${QUERY_PARAMS[*]}")"
fi

RESPONSE=$(curl -s -X GET "${API}/node${QUERY}" \
  -H "Authorization: Bearer $HEADSCALE_API_KEY" \
  -H "Accept: application/json")

# Apply client-side filters for tag and online-only (API may not support these natively)
if [[ -n "$TAG_FILTER" ]]; then
  RESPONSE=$(echo "$RESPONSE" | jq "map(select(.tags // [] | index(\"tag:$TAG_FILTER\") != null))")
fi
if $ONLINE_ONLY; then
  RESPONSE=$(echo "$RESPONSE" | jq "map(select(.online == true))")
fi

if $JSON_MODE; then
  echo "$RESPONSE"
  exit 0
fi

# Pretty-print table
echo "$RESPONSE" | jq -r '
  if type == "array" then .
  elif .nodes then .nodes
  else [] end
  | (["ID", "NAME", "IP", "USER", "TAGS", "ONLINE", "LAST_SEEN", "OS", "VERSION"]
  | join(" | ")),
  (.[] | [
    (.id // "?" | tostring),
    (.givenName // .name // "?"),
    (.ipAddresses // [] | join(",") // "?"),
    (.user.name // .user // "?"),
    ((.tags // []) | join(",") // "-"),
    (if .online then "✓" else "✗" end),
    (.lastSeen // "?"),
    (.hostInfo.os // "?"),
    (.clientVersion // "?")
  ] | join(" | "))
' 2>/dev/null | column -s '|' -t
