#!/usr/bin/env bash
set -euo pipefail

# hs-approve-nodes.sh — Approve pending node registrations in Headscale
#
# Usage:
#   hs-approve-nodes.sh [--all] [--auth-id <id>] [--dry-run] [--json] [--help]
#
# Options:
#   --all         Approve all pending registrations
#   --auth-id <id> Approve a specific pending auth by its ID
#   --dry-run     Show pending registrations without approving
#   --json        Output raw JSON
#   --help        Show this help message

usage() {
  sed -n '/^# Usage:/,/^$/{ s/^#//p; }' "$0"
  echo ""
  echo "Examples:"
  echo "  hs-approve-nodes.sh --dry-run              # Show pending registrations"
  echo "  hs-approve-nodes.sh --all                   # Approve all pending"
  echo "  hs-approve-nodes.sh --auth-id 42            # Approve a specific node"
  echo "  hs-approve-nodes.sh --all --json"
  exit "${1:-0}"
}

APPROVE_ALL=false
AUTH_ID=""
DRY_RUN=false
JSON_MODE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)      APPROVE_ALL=true; shift ;;
    --auth-id)  shift; AUTH_ID="$1"; shift ;;
    --dry-run)  DRY_RUN=true; shift ;;
    --json)     JSON_MODE=true; shift ;;
    --help)     usage 0 ;;
    *)          echo "ERROR: Unknown option: $1" >&2; usage 1 ;;
  esac
done

if ! $APPROVE_ALL && [[ -z "$AUTH_ID" ]]; then
  echo "ERROR: Specify --all or --auth-id <id>" >&2
  usage 1
fi

# ---------------------------------------------------------------------------
# Try headscale CLI first
# ---------------------------------------------------------------------------
if command -v headscale &>/dev/null; then
  HEADSCALE_CMD=(headscale)
  if [[ -n "${HEADSCALE_URL:-}" ]]; then
    HEADSCALE_CMD+=(--url "$HEADSCALE_URL")
  fi

  if $DRY_RUN; then
    if $JSON_MODE; then
      "${HEADSCALE_CMD[@]}" nodes list --output json 2>/dev/null | jq 'map(select(.approvalRequired == true or .approved == false))'
    else
      echo "=== Pending Node Registrations ==="
      "${HEADSCALE_CMD[@]}" nodes list --output json 2>/dev/null | \
        jq -r 'map(select(.approvalRequired == true or .approved == false)) | .[] | "ID: \(.id) | Name: \(.givenName // .name // "?") | IP: \(.ipAddresses // [] | join(",")) | User: \(.user.name // .user // "?")"'
    fi
    exit 0
  fi

  if [[ -n "$AUTH_ID" ]]; then
    # Register/approve a specific node by ID via the route node approve command
    "${HEADSCALE_CMD[@]}" nodes approve -i "$AUTH_ID"
  elif $APPROVE_ALL; then
    PENDING=$("${HEADSCALE_CMD[@]}" nodes list --output json 2>/dev/null | \
      jq -r 'map(select(.approvalRequired == true or .approved == false)) | .[].id' 2>/dev/null || true)
    if [[ -z "$PENDING" ]]; then
      echo "No pending nodes to approve."
      exit 0
    fi
    COUNT=0
    while IFS= read -r NODE_ID; do
      if [[ -n "$NODE_ID" ]]; then
        echo "Approving node $NODE_ID..."
        "${HEADSCALE_CMD[@]}" nodes approve -i "$NODE_ID"
        COUNT=$((COUNT + 1))
      fi
    done <<< "$PENDING"
    echo "Approved $COUNT node(s)."
  fi

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

if $DRY_RUN; then
  # List all nodes and filter for pending/unapproved
  RESPONSE=$(curl -s -X GET "${API}/node" \
    -H "Authorization: Bearer $HEADSCALE_API_KEY" \
    -H "Accept: application/json")

  PENDING=$(echo "$RESPONSE" | jq 'map(select(.approvalRequired == true or .approved == false))' 2>/dev/null)

  if $JSON_MODE; then
    echo "$PENDING"
  else
    COUNT=$(echo "$PENDING" | jq 'length')
    echo "=== Pending Node Registrations ($COUNT pending) ==="
    echo "$PENDING" | jq -r '.[] | "ID: \(.id) | Name: \(.givenName // .name // "?") | IP: \(.ipAddresses // [] | join(",")) | User: \(.user.name // .user // "?")"'
  fi
  exit 0
fi

if [[ -n "$AUTH_ID" ]]; then
  RESPONSE=$(curl -s -X POST "${API}/node/${AUTH_ID}/approve" \
    -H "Authorization: Bearer $HEADSCALE_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{}')

  if $JSON_MODE; then
    echo "$RESPONSE"
  else
    STATUS=$(echo "$RESPONSE" | jq -r '.status // "ok"')
    echo "Node $AUTH_ID approval status: $STATUS"
  fi
elif $APPROVE_ALL; then
  RESPONSE=$(curl -s -X GET "${API}/node" \
    -H "Authorization: Bearer $HEADSCALE_API_KEY" \
    -H "Accept: application/json")

  echo "$RESPONSE" | jq -c '.[] | select(.approvalRequired == true or .approved == false) | .id' 2>/dev/null | while read -r NODE_ID; do
    NODE_ID=$(echo "$NODE_ID" | tr -d '"')
    echo "Approving node $NODE_ID..."
    curl -s -X POST "${API}/node/${NODE_ID}/approve" \
      -H "Authorization: Bearer $HEADSCALE_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{}' > /dev/null
  done
  echo "All pending nodes approved."
fi
