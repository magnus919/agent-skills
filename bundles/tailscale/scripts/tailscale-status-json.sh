#!/usr/bin/env bash
set -euo pipefail

# tailscale-status-json.sh
# Structured wrapper around `tailscale status --json` with peer diagnostics

SCRIPT_NAME="$(basename "$0")"
JSON_OUTPUT=false
VERBOSE=false
PEER=""
WATCH=false

usage() {
  echo "Usage: $SCRIPT_NAME [OPTIONS]"
  echo ""
  echo "Display structured Tailscale status in JSON"
  echo ""
  echo "Options:"
  echo "  --json         Output raw JSON (no summary)"
  echo "  --peer <IP>    Show status for specific peer"
  echo "  --watch        Watch for changes"
  echo "  --verbose      Show all peers including long-idle"
  echo "  --help         Show this help"
  echo ""
  echo "Examples:"
  echo "  $SCRIPT_NAME"
  echo "  $SCRIPT_NAME --json | jq '.Self.Routes'"
  echo "  $SCRIPT_NAME --peer 100.64.0.1"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON_OUTPUT=true; shift ;;
    --verbose) VERBOSE=true; shift ;;
    --peer) PEER="$2"; shift 2 ;;
    --watch) WATCH=true; shift ;;
    --help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

# Check if tailscale is available
if ! command -v tailscale &>/dev/null; then
  echo "Error: 'tailscale' CLI not found. Is Tailscale installed?" >&2
  exit 2
fi

# Build tailscale status command
TAILSCALE_CMD=("tailscale" "status" "--json")
if [[ "$WATCH" == true ]]; then
  TAILSCALE_CMD+=("--watch")
fi

# Get status JSON
STATUS_JSON="$("${TAILSCALE_CMD[@]}" 2>/dev/null)" || {
  echo "Error: failed to get tailscale status. Is tailscaled running?" >&2
  exit 2
}

# If --peer specified, filter to that peer
if [[ -n "$PEER" ]]; then
  FILTERED=$(echo "$STATUS_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
target = '$PEER'
result = {'Self': data.get('Self'), 'Peer': []}
for peer in data.get('Peer', []):
    if target in str(peer.get('TailscaleIPs', [])) or target in peer.get('DNSName', ''):
        result['Peer'].append(peer)
if not result['Peer']:
    print(json.dumps({'error': f'No peer found matching {target}'}))
else:
    print(json.dumps(result, indent=2))
" 2>/dev/null || echo "{\"error\": \"failed to parse\"}")
  STATUS_JSON="$FILTERED"
fi

if [[ "$JSON_OUTPUT" == true ]]; then
  echo "$STATUS_JSON"
  exit 0
fi

# Human-readable summary
python3 -c "
import json, sys

data = json.load(sys.stdin)

if 'error' in data:
    print(f'Error: {data[\"error\"]}')
    sys.exit(0)

self_info = data.get('Self', {})
peers = data.get('Peer', [])

print('=== Tailscale Status ===')
print(f'Self: {self_info.get(\"DNSName\", \"unknown\")} ({self_info.get(\"OS\", \"?\")})')
print(f'Online: {self_info.get(\"Online\", False)}')
ips = self_info.get('TailscaleIPs', [])
if ips:
    print(f'IPs: {\", \".join(ips)}')

# Count peer status
online = sum(1 for p in peers if p.get('Online'))
via_derp = sum(1 for p in peers if p.get('Relay'))
direct = sum(1 for p in peers if not p.get('Relay'))

print(f'')
print(f'Peers: {len(peers)} total, {online} online')
print(f'Direct connections: {direct}')
print(f'Via DERP relay: {via_derp}')

if peers:
    print(f'')
    print('Peer Summary:')
    for p in peers:
        name = p.get('DNSName', '?').rstrip('.')
        peer_ips = p.get('TailscaleIPs', [])
        status = 'online' if p.get('Online') else 'offline'
        relay = p.get('Relay', 'direct')
        last_seen = p.get('LastSeen', '')
        print(f'  {name} ({peer_ips[0] if peer_ips else \"?\"}) — {status}, relay: {relay}')
"
