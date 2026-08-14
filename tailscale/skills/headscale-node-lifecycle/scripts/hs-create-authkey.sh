#!/usr/bin/env bash
set -euo pipefail

# hs-create-authkey.sh — Create pre-authenticated keys in Headscale
# Supports both headscale CLI and REST API fallback.
#
# Usage:
#   hs-create-authkey.sh --user <user> [options]
#   hs-create-authkey.sh --tags <tag> [options]
#
# Options:
#   --user <user>      Create auth key for a personal user
#   --tags <tag>       Create auth key for tagged nodes (comma-separated)
#   --expiration <dur> Key lifetime (default: 1h, use 0 for no expiry)
#   --reusable         Allow key to be used multiple times
#   --ephemeral        Remove node from tailnet on disconnection
#   --json             Output raw JSON response
#   --dry-run          Print what would be done without executing
#   --help             Show this help message and exit

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  sed -n '/^# Usage:/,/^$/{ s/^#//p; }' "$0"
  echo ""
  echo "Examples:"
  echo "  hs-create-authkey.sh --user alice"
  echo "  hs-create-authkey.sh --user alice --expiration 24h --reusable --json"
  echo "  hs-create-authkey.sh --tags webserver,monitoring --ephemeral"
  echo "  hs-create-authkey.sh --tags ci-runner --expiration 0 --reusable --dry-run"
  exit "${1:-0}"
}

# Defaults
USER=""
TAGS=""
EXPIRATION="1h"
REUSABLE=false
EPHEMERAL=false
JSON_MODE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)       shift; USER="$1"; shift ;;
    --tags)       shift; TAGS="$1"; shift ;;
    --expiration) shift; EXPIRATION="$1"; shift ;;
    --reusable)   REUSABLE=true; shift ;;
    --ephemeral)  EPHEMERAL=true; shift ;;
    --json)       JSON_MODE=true; shift ;;
    --dry-run)    DRY_RUN=true; shift ;;
    --help)       usage 0 ;;
    *)            echo "ERROR: Unknown option: $1" >&2; usage 1 ;;
  esac
done

# Validate: one of --user or --tags is required
if [[ -z "$USER" && -z "$TAGS" ]]; then
  echo "ERROR: Specify --user or --tags (or both)" >&2
  usage 1
fi

# --json implies JSON_MODE
# --dry-run implies JSON_MODE for structured output
if $DRY_RUN; then
  cat <<EOF
{
  "dry_run": true,
  "user": "${USER:-tagged}",
  "tags": ${TAGS:-null},
  "expiration": "$EXPIRATION",
  "reusable": $REUSABLE,
  "ephemeral": $EPHEMERAL
}
EOF
  exit 0
fi

# ---------------------------------------------------------------------------
# Try headscale CLI first
# ---------------------------------------------------------------------------
if command -v headscale &>/dev/null; then
  HEADSCALE_CMD=(headscale)
  if [[ -n "${HEADSCALE_URL:-}" ]]; then
    HEADSCALE_CMD+=(--url "$HEADSCALE_URL")
  fi

  # Build CLI args
  PREAUTH_ARGS=(preauthkeys create)

  if [[ -n "$USER" ]]; then
    PREAUTH_ARGS+=(--user "$USER")
  fi
  if [[ -n "$TAGS" ]]; then
    # Convert comma-separated tags to individual --tag flags
    IFS=',' read -ra TAG_LIST <<< "$TAGS"
    for t in "${TAG_LIST[@]}"; do
      PREAUTH_ARGS+=(--tag "tag:$t")
    done
  fi
  if [[ "$EXPIRATION" != "1h" ]]; then
    PREAUTH_ARGS+=(--expiration "$EXPIRATION")
  fi
  if $REUSABLE; then
    PREAUTH_ARGS+=(--reusable)
  fi
  if $EPHEMERAL; then
    PREAUTH_ARGS+=(--ephemeral)
  fi

  if $JSON_MODE; then
    PREAUTH_ARGS+=(--output json)
  fi

  exec "${HEADSCALE_CMD[@]}" "${PREAUTH_ARGS[@]}"
fi

# ---------------------------------------------------------------------------
# Fallback: REST API via curl
# ---------------------------------------------------------------------------
if [[ -z "${HEADSCALE_URL:-}" || -z "${HEADSCALE_API_KEY:-}" ]]; then
  echo "ERROR: headscale CLI not found. Set HEADSCALE_URL and HEADSCALE_API_KEY env vars for API fallback." >&2
  exit 1
fi

API="${HEADSCALE_URL}/api/v1"

# Determine user for tagged vs personal
API_USER="${USER:-tagged-devices}"

# Build JSON payload
PAYLOAD=$(jq -n \
  --arg user "$API_USER" \
  --arg exp "$EXPIRATION" \
  --arg reusable "$REUSABLE" \
  --arg ephemeral "$EPHEMERAL" \
  --arg tags "$TAGS" \
  '{
    user: $user,
    expiration: $exp,
    reusable: ($reusable == "true"),
    ephemeral: ($ephemeral == "true")
  } | if $tags != "" then .tags = ($tags | split(",") | map("tag:" + .)) else . end')

RESPONSE=$(curl -s -X POST "$API/preauthkey" \
  -H "Authorization: Bearer $HEADSCALE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

if $JSON_MODE; then
  echo "$RESPONSE"
else
  KEY=$(echo "$RESPONSE" | jq -r '.key // empty')
  if [[ -n "$KEY" ]]; then
    echo "Pre-authenticated key created: $KEY"
    echo "  User:       $API_USER"
    echo "  Tags:       ${TAGS:-none}"
    echo "  Expiration: $EXPIRATION"
    echo "  Reusable:   $REUSABLE"
    echo "  Ephemeral:  $EPHEMERAL"
  else
    echo "ERROR: Failed to create auth key" >&2
    echo "$RESPONSE" >&2
    exit 1
  fi
fi
