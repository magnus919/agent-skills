#!/usr/bin/env bash
set -euo pipefail

# hs-tag-node.sh — Update tags on a Headscale node
#
# Usage:
#   hs-tag-node.sh --node <id/name> --tags <tag1,tag2> [--replace | --add] [--dry-run] [--json] [--help]
#
# Options:
#   --node <id/name>  Node ID or name to update
#   --tags <tags>     Comma-separated list of tags (without tag: prefix)
#   --replace         Replace all existing tags with the specified ones (default)
#   --add             Add specified tags to existing tags
#   --dry-run         Show what would be changed without modifying
#   --json            Output raw JSON response
#   --help            Show this help message

usage() {
  sed -n '/^# Usage:/,/^$/{ s/^#//p; }' "$0"
  echo ""
  echo "Examples:"
  echo "  hs-tag-node.sh --node myserver --tags webserver,production"
  echo "  hs-tag-node.sh --node 42 --tags monitoring --add"
  echo "  hs-tag-node.sh --node myserver --tags webserver --dry-run --json"
  exit "${1:-0}"
}

NODE=""
TAGS=""
REPLACE=true
DRY_RUN=false
JSON_MODE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --node)     shift; NODE="$1"; shift ;;
    --tags)     shift; TAGS="$1"; shift ;;
    --replace)  REPLACE=true; shift ;;
    --add)      REPLACE=false; shift ;;
    --dry-run)  DRY_RUN=true; shift ;;
    --json)     JSON_MODE=true; shift ;;
    --help)     usage 0 ;;
    *)          echo "ERROR: Unknown option: $1" >&2; usage 1 ;;
  esac
done

if [[ -z "$NODE" || -z "$TAGS" ]]; then
  echo "ERROR: --node and --tags are required" >&2
  usage 1
fi

# Normalize tags
IFS=',' read -ra TAG_ARRAY <<< "$TAGS"
NORMALIZED_TAGS=()
for t in "${TAG_ARRAY[@]}"; do
  t=$(echo "$t" | xargs)  # trim whitespace
  if [[ "$t" != tag:* ]]; then
    t="tag:$t"
  fi
  NORMALIZED_TAGS+=("$t")
done

# ---------------------------------------------------------------------------
# Try headscale CLI first
# ---------------------------------------------------------------------------
if command -v headscale &>/dev/null; then
  HEADSCALE_CMD=(headscale)
  if [[ -n "${HEADSCALE_URL:-}" ]]; then
    HEADSCALE_CMD+=(--url "$HEADSCALE_URL")
  fi

  # Resolve node ID from name if needed
  NODE_ID="$NODE"
  if ! [[ "$NODE_ID" =~ ^[0-9]+$ ]]; then
    RESOLVED=$("${HEADSCALE_CMD[@]}" nodes list --output json 2>/dev/null | \
      jq -r ".[] | select(.givenName == \"$NODE\" or .name == \"$NODE\") | .id" 2>/dev/null | head -1)
    if [[ -z "$RESOLVED" ]]; then
      echo "ERROR: Could not find node with name: $NODE" >&2
      exit 1
    fi
    NODE_ID="$RESOLVED"
  fi

  if $DRY_RUN; then
    # Show current and proposed tags
    CURRENT=$("${HEADSCALE_CMD[@]}" nodes list --output json 2>/dev/null | \
      jq -r ".[] | select(.id == $NODE_ID)" 2>/dev/null)

    CURRENT_TAGS=$(echo "$CURRENT" | jq -r '.tags // [] | join(", ")')
    NODE_NAME=$(echo "$CURRENT" | jq -r '.givenName // .name // "?"')

    if $JSON_MODE; then
      cat <<EOF
{
  "dry_run": true,
  "node_id": $NODE_ID,
  "node_name": "$NODE_NAME",
  "current_tags": [$(echo "$CURRENT_TAGS" | sed 's/, /","/g' | sed 's/^/"/' | sed 's/$/"/')],
  "new_tags": [$(printf '"%s",' "${NORMALIZED_TAGS[@]}" | sed 's/,$//')],
  "mode": "$( $REPLACE && echo 'replace' || echo 'add' )"
}
EOF
    else
      echo "Node: $NODE_NAME (ID: $NODE_ID)"
      echo "Current tags: $CURRENT_TAGS"
      echo "Proposed tags: ${NORMALIZED_TAGS[*]}"
      echo "Mode: $($REPLACE && echo 'replace' || echo 'add')"
      echo "(dry-run — no changes made)"
    fi
    exit 0
  fi

  TAG_ARGS=()
  for t in "${NORMALIZED_TAGS[@]}"; do
    TAG_ARGS+=(--tag "$t")
  done

  if $REPLACE; then
    "${HEADSCALE_CMD[@]}" nodes tag -i "$NODE_ID" "${TAG_ARGS[@]}"
  else
    # For --add, we need to get existing tags first, then add to them
    CURRENT=$("${HEADSCALE_CMD[@]}" nodes list --output json 2>/dev/null | \
      jq -r ".[] | select(.id == $NODE_ID) | .tags // [] | .[]" 2>/dev/null || true)

    ADDED=()
    # Build combined list
    while IFS= read -r tag; do
      if [[ -n "$tag" ]]; then
        ADDED+=("$tag")
      fi
    done <<< "$CURRENT"
    for t in "${NORMALIZED_TAGS[@]}"; do
      # Check if already present
      found=false
      for existing in "${ADDED[@]:-}"; do
        if [[ "$existing" == "$t" ]]; then
          found=true
          break
        fi
      done
      if ! $found; then
        ADDED+=("$t")
      fi
    done

    TAG_ARGS2=()
    for t in "${ADDED[@]}"; do
      TAG_ARGS2+=(--tag "$t")
    done
    "${HEADSCALE_CMD[@]}" nodes tag -i "$NODE_ID" "${TAG_ARGS2[@]}"
  fi

  if $JSON_MODE; then
    "${HEADSCALE_CMD[@]}" nodes list --output json 2>/dev/null | \
      jq ".[] | select(.id == $NODE_ID)"
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

# Resolve node ID from name if needed
NODE_ID="$NODE"
if ! [[ "$NODE_ID" =~ ^[0-9]+$ ]]; then
  RESOLVED=$(curl -s -X GET "${API}/node" \
    -H "Authorization: Bearer $HEADSCALE_API_KEY" \
    -H "Accept: application/json" | \
    jq -r ".[] | select(.givenName == \"$NODE\" or .name == \"$NODE\") | .id" 2>/dev/null | head -1)
  if [[ -z "$RESOLVED" ]]; then
    echo "ERROR: Could not find node with name: $NODE" >&2
    exit 1
  fi
  NODE_ID="$RESOLVED"
fi

if $DRY_RUN; then
  CURRENT_NODE=$(curl -s -X GET "${API}/node/${NODE_ID}" \
    -H "Authorization: Bearer $HEADSCALE_API_KEY" \
    -H "Accept: application/json")

  if $JSON_MODE; then
    echo "$CURRENT_NODE" | jq --argjson new_tags "$(printf '%s\n' "${NORMALIZED_TAGS[@]}" | jq -R . | jq -s .)" \
      '. + {dry_run: true, proposed_tags: $new_tags}'
  else
    CURRENT_TAGS=$(echo "$CURRENT_NODE" | jq -r '.tags // [] | join(", ")')
    NODE_NAME=$(echo "$CURRENT_NODE" | jq -r '.givenName // .name // "?"')
    echo "Node: $NODE_NAME (ID: $NODE_ID)"
    echo "Current tags: $CURRENT_TAGS"
    echo "Proposed tags: ${NORMALIZED_TAGS[*]}"
    echo "Mode: $($REPLACE && echo 'replace' || echo 'add')"
    echo "(dry-run — no changes made)"
  fi
  exit 0
fi

if $REPLACE; then
  PAYLOAD=$(jq -n --argjson tags "$(printf '%s\n' "${NORMALIZED_TAGS[@]}" | jq -R . | jq -s .)" \
    '{tags: $tags}')
else
  # Get existing tags and merge
  CURRENT_NODE=$(curl -s -X GET "${API}/node/${NODE_ID}" \
    -H "Authorization: Bearer $HEADSCALE_API_KEY" \
    -H "Accept: application/json")
  EXISTING_TAGS=$(echo "$CURRENT_NODE" | jq -r '.tags // [] | .[]' 2>/dev/null)
  COMBINED=()
  while IFS= read -r tag; do
    if [[ -n "$tag" ]]; then
      COMBINED+=("$tag")
    fi
  done <<< "$EXISTING_TAGS"
  for t in "${NORMALIZED_TAGS[@]}"; do
    found=false
    for existing in "${COMBINED[@]:-}"; do
      if [[ "$existing" == "$t" ]]; then
        found=true
        break
      fi
    done
    if ! $found; then
      COMBINED+=("$t")
    fi
  done
  PAYLOAD=$(jq -n --argjson tags "$(printf '%s\n' "${COMBINED[@]}" | jq -R . | jq -s .)" \
    '{tags: $tags}')
fi

RESPONSE=$(curl -s -X PUT "${API}/node/${NODE_ID}/tags" \
  -H "Authorization: Bearer $HEADSCALE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

if $JSON_MODE; then
  echo "$RESPONSE"
else
  echo "Tags updated on node $NODE_ID: ${NORMALIZED_TAGS[*]}"
fi
