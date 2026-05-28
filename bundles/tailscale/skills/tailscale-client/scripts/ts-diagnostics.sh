#!/usr/bin/env bash
# =============================================================================
# ts-diagnostics.sh — Comprehensive Tailscale Connectivity Diagnostics
# =============================================================================
# Description:
#   Runs a comprehensive diagnostic bundle: tailscale status, ping, netcheck,
#   and version. Produces structured JSON or human-readable output with path
#   analysis (direct vs. DERP relay).
#
# Usage:
#   ./ts-diagnostics.sh [options]
#
# Options:
#   --peer <IP|hostname>    Specific peer to test (ping target)
#   --json                  Output results in JSON format
#   --help                  Show this help message and exit
#
# Examples:
#   ./ts-diagnostics.sh
#   ./ts-diagnostics.sh --peer 100.64.0.2
#   ./ts-diagnostics.sh --peer my-server --json > diagnostics.json
# =============================================================================

set -euo pipefail

# ---- Colors ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

usage() {
    grep "^# " "$0" | sed 's/^# //' | sed 's/^#//'
    exit 0
}

# ---- Defaults ----
PEER=""
JSON_OUTPUT=false

# ---- Parse Arguments ----
while [[ $# -gt 0 ]]; do
    case "$1" in
        --peer) PEER="$2"; shift 2 ;;
        --json) JSON_OUTPUT=true; shift ;;
        --help) usage ;;
        *) error "Unknown option: $1"; usage ;;
    esac
done

# ---- Verify prerequisites ----
if ! command -v tailscale &>/dev/null; then
    error "tailscale command not found"
    exit 1
fi

# ---- Collect Diagnostics ----
info "Collecting Tailscale diagnostics..."

# 1. tailscale status --json
STATUS_JSON=""
STATUS_TEXT=""
if STATUS_RAW=$(tailscale status --json 2>/dev/null); then
    STATUS_JSON="$STATUS_RAW"
    STATUS_TEXT=$(echo "$STATUS_RAW" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RAW")
else
    STATUS_JSON='{"error":"tailscale status failed"}'
    STATUS_TEXT="tailscale status: FAILED"
fi
info "  ✓ Status collected"

# 2. tailscale version
VERSION_RAW=$(tailscale version 2>/dev/null || echo "unknown")
VERSION_CLIENT=$(echo "$VERSION_RAW" | sed -n '1p')
VERSION_DAEMON=$(echo "$VERSION_RAW" | sed -n '2p')
VERSION_COMMIT=$(echo "$VERSION_RAW" | sed -n '3p')
info "  ✓ Version collected"

# 3. tailscale netcheck
NETCHECK_JSON=""
if NETCHECK_RAW=$(tailscale netcheck 2>/dev/null); then
    NETCHECK_JSON=$(echo "$NETCHECK_RAW" | head -50)
else
    NETCHECK_JSON='{"error":"tailscale netcheck failed"}'
fi
info "  ✓ Netcheck collected"

# 4. tailscale ping to peer(s)
PING_RESULTS="[]"
if [[ -n "$PEER" ]]; then
    if PING_RAW=$(tailscale ping --verbose -c 3 "$PEER" 2>&1); then
        PING_PARSED=$(echo "$PING_RAW" | python3 -c "
import sys, json
lines = sys.stdin.read().strip().split('\n')
results = []
for line in lines:
    parts = line.split()
    entry = {'raw': line}
    if 'via' in line:
        entry['type'] = 'relay' if 'DERP' in line else 'direct'
    if 'pong' in line:
        entry['type'] = 'pong'
        for i, p in enumerate(parts):
            if 'from' in p and i+1 < len(parts):
                entry['target'] = parts[i+1]
            if 'latency' in line:
                import re
                m = re.search(r'[\\d.]+ms', line)
                if m:
                    entry['latency_ms'] = m.group()
    results.append(entry)
print(json.dumps(results))
        " 2>/dev/null || echo "[{\"raw\": \"${PING_RAW}\"}]")
        PING_RESULTS=$(echo "$PING_RAW" | python3 -c "
import sys, json
lines = sys.stdin.read().strip().split('\n')
results = []
for line in lines:
    parts = line.split()
    entry = {'raw': line}
    # Detect path type
    if 'via' in line.lower() or 'relay' in line.lower() or 'derp' in line.lower():
        entry['path_type'] = 'relay'
        for i, p in enumerate(parts):
            if p.lower() == 'via' and i+1 < len(parts):
                entry['via'] = parts[i+1]
            if p.lower() == 'derp' and i+1 < len(parts):
                entry['derp_server'] = parts[i+1]
    elif 'pong' in line.lower():
        entry['path_type'] = 'direct'
    if 'pong' in line.lower():
        entry['type'] = 'pong'
        for i, p in enumerate(parts):
            if p == 'from' and i+1 < len(parts):
                entry['target'] = parts[i+1].rstrip(':')
        import re
        m = re.search(r'([\\d.]+)ms', line)
        if m:
            entry['latency_ms'] = float(m.group(1))
    results.append(entry)
print(json.dumps(results, indent=2))
        " 2>/dev/null || echo "[{\"raw\": \"ping command failed\"}]")
    fi
    info \"  ✓ Ping to ${PEER} collected\"
fi

# ---- Analyze peers for direct vs DERP relay ----
PEER_ANALYSIS="[]"
if [[ -n "$STATUS_JSON" ]]; then
    PEER_ANALYSIS=$(echo "$STATUS_JSON" | python3 -c "
import sys, json

data = json.load(sys.stdin)
peers = data.get('Peer', {})
status_map = data.get('Status', '').lower()

results = []
for node_id, node_info in peers.items():
    entry = {
        'id': node_id,
        'hostname': node_info.get('HostName', ''),
        'dns_name': node_info.get('DNSName', ''),
        'tailscale_ips': node_info.get('TailscaleIPs', []),
        'os': node_info.get('OS', ''),
        'online': node_info.get('Online', False),
        'relay': node_info.get('Relay', ''),
        'tx_bytes': node_info.get('TxBytes', 0),
        'rx_bytes': node_info.get('RxBytes', 0),
        'cur_connection': node_info.get('CurConnection', ''),
        'keep_alive': node_info.get('KeepAlive', False)
    }

    # Determine primary path
    if node_info.get('Relay'):
        entry['primary_path'] = 'relay'
        entry['relay_server'] = node_info['Relay']
    elif node_info.get('CurConnection') == 'direct':
        entry['primary_path'] = 'direct'
    elif node_info.get('TxBytes', 0) > 0 or node_info.get('RxBytes', 0) > 0:
        # Has traffic but no relay — likely direct
        entry['primary_path'] = 'direct'
    else:
        entry['primary_path'] = 'unknown'

    results.append(entry)

print(json.dumps(results, indent=2))
    " 2>/dev/null || echo "$PEER_ANALYSIS")
fi

# ---- Self info ----
SELF_INFO="{}"
if [[ -n "$STATUS_JSON" ]]; then
    SELF_INFO=$(echo "$STATUS_JSON" | python3 -c "
import sys, json
data = json.load(sys.stdin)
self_info = data.get('Self', {})
self_info = {
    'hostname': self_info.get('HostName', ''),
    'dns_name': self_info.get('DNSName', ''),
    'tailscale_ips': self_info.get('TailscaleIPs', []),
    'online': self_info.get('Online', False),
    'os': self_info.get('OS', ''),
    'relay': self_info.get('Relay', ''),
    'cur_connection': self_info.get('CurConnection', ''),
    'id': list(data.get('Self', {}).keys())[0] if len(data.get('Self', {})) <= 1 else None
}
if 'Self' in data:
    s = data['Self']
    if isinstance(s, dict) and 'ID' in s:
        self_info['id'] = s['ID']
print(json.dumps(self_info, indent=2))
    " 2>/dev/null || echo '{}')
fi

# ---- Output ----
if [[ "$JSON_OUTPUT" == "true" ]]; then
    cat <<EOF
{
  "version": {
    "client": "$(echo "$VERSION_CLIENT" | sed 's/"/\\"/g')",
    "daemon": "$(echo "$VERSION_DAEMON" | sed 's/"/\\"/g')",
    "commit": "$(echo "$VERSION_COMMIT" | sed 's/"/\\"/g')"
  },
  "self": $SELF_INFO,
  "status": $STATUS_JSON,
  "peer_analysis": $PEER_ANALYSIS,
  "ping_results": $PING_RESULTS,
  "netcheck": $(echo "$NETCHECK_JSON" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read().strip() if sys.stdin.read().strip() else '{}')
except:
    d = {'raw_output': sys.stdin.read().strip() if sys.stdin.read().strip() else 'unavailable'}
print(json.dumps(d, indent=2))
" 2>/dev/null || echo '"unavailable"')
}
EOF
else
    echo ""
    echo "============================================"
    echo "  Tailscale Diagnostics Report"
    echo "============================================"
    echo ""
    echo "--- Version ---"
    echo "  Client: ${VERSION_CLIENT:-unknown}"
    echo "  Daemon: ${VERSION_DAEMON:-unknown}"
    if [[ -n "$VERSION_COMMIT" ]]; then
        echo "  Commit: ${VERSION_COMMIT}"
    fi
    echo ""

    echo "--- Self ---"
    echo "$SELF_INFO" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for k, v in d.items():
    if isinstance(v, list):
        print(f'  {k}: {', '.join(str(x) for x in v)}')
    else:
        print(f'  {k}: {v}')
" 2>/dev/null || echo "  (unavailable)"
    echo ""

    echo "--- Peer Analysis ---"
    echo "$PEER_ANALYSIS" | python3 -c "
import sys, json
peers = json.load(sys.stdin)
for p in peers:
    path_str = 'DIRECT' if p.get('primary_path') == 'direct' else ('RELAY (' + p.get('relay_server', '?') + ')' if p.get('primary_path') == 'relay' else 'UNKNOWN')
    online_str = 'ONLINE' if p.get('online') else 'OFFLINE'
    ips = ', '.join(p.get('tailscale_ips', []))
    print(f'  {p[\"hostname\"] + \".\" + p.get(\"dns_name\", \"\"):30} {ips:20} {online_str:8} Path: {path_str}')
" 2>/dev/null || echo "  (no peers or unavailable)"
    echo ""

    if [[ -n "$PEER" ]]; then
        echo "--- Ping: ${PEER} ---"
        echo "$PING_RESULTS" | python3 -c "
import sys, json
results = json.load(sys.stdin)
for r in results:
    path = r.get('path_type', 'unknown')
    lat = r.get('latency_ms', '?')
    via = r.get('via', '')
    if path == 'direct':
        print(f'  DIRECT  latency={lat}ms')
    elif path == 'relay':
        print(f'  RELAY   via={via} latency={lat}ms')
    else:
        print(f'  {r.get(\"raw\", \"?\")}')
" 2>/dev/null || echo "  (ping output unavailable)"
        echo ""
    fi

    echo "--- Netcheck ---"
    echo "$NETCHECK_JSON" | head -15
    echo ""

    echo "--- Status (summary) ---"
    tailscale status 2>/dev/null | head -30 || echo "  (unavailable)"
    echo ""
    echo "============================================"
fi
