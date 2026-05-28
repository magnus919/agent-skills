#!/usr/bin/env bash
#
# install-headscale.sh — Install or upgrade the Headscale binary
#
# Usage:
#   install-headscale.sh [--version <tag>] [--config-path <path>] [--dry-run] [--json] [--docker]
#
# Options:
#   --version <tag>       Headscale version to install (default: latest stable)
#   --config-path <path>  Path for config.yaml (default: /etc/headscale/config.yaml)
#   --docker              Deploy using Docker Compose instead of bare binary
#   --dry-run             Preview actions without making changes
#   --json                Output structured JSON
#   --help                Show this help and exit
#
# Examples:
#   install-headscale.sh                                          # install latest
#   install-headscale.sh --version v0.23.0                        # specific version
#   install-headscale.sh --docker --dry-run                       # preview Docker deploy
#   install-headscale.sh --json                                   # structured output
#   install-headscale.sh --version v0.23.0 --config-path /custom  # custom config path

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
VERSION=""
CONFIG_PATH="/etc/headscale/config.yaml"
DRY_RUN=false
JSON=false
DOCKER=false
RELEASE_API="https://api.github.com/repos/juanfont/headscale/releases"
GITHUB_DL="https://github.com/juanfont/headscale/releases/download"

# ── Argument parsing ──────────────────────────────────────────────────────────

usage() {
  sed -n '2,31p' "$0" | sed 's/^# //; s/^#$//'
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)     VERSION="$2"; shift 2 ;;
    --config-path) CONFIG_PATH="$2"; shift 2 ;;
    --dry-run)     DRY_RUN=true; shift ;;
    --json)        JSON=true; shift ;;
    --docker)      DOCKER=true; shift ;;
    --help)        usage ;;
    *)             echo "Unknown option: $1" >&2; usage ;;
  esac
done

# ── Helpers ───────────────────────────────────────────────────────────────────

log()     { if ! $JSON; then echo "[${SCRIPT_NAME}] $*"; fi }
err()     { echo "[${SCRIPT_NAME}] ERROR: $*" >&2; }
json_out() {
  if $JSON; then
    echo "$1"
  fi
}

detect_arch() {
  local arch
  arch="$(uname -m)"
  case "$arch" in
    x86_64)  echo "amd64" ;;
    aarch64) echo "arm64" ;;
    armv7l)  echo "armv7" ;;
    *)       err "Unsupported architecture: $arch"; exit 1 ;;
  esac
}

detect_os() {
  local os
  os="$(uname -s)"
  case "$os" in
    Linux)  echo "linux" ;;
    Darwin) echo "darwin" ;;
    *)      err "Unsupported OS: $os"; exit 1 ;;
  esac
}

get_latest_version() {
  local tag
  tag="$(curl -sSfL "$RELEASE_API/latest" 2>/dev/null | grep '"tag_name"' | cut -d'"' -f4 || true)"
  if [[ -z "$tag" ]]; then
    # Fallback: list releases and pick first non-prerelease
    tag="$(curl -sSfL "$RELEASE_API?per_page=10" 2>/dev/null \
      | python3 -c "
import json,sys
releases=json.load(sys.stdin)
for r in releases:
    if not r.get('prerelease') and r.get('tag_name'):
        print(r['tag_name'])
        break
" 2>/dev/null || true)"
  fi
  echo "${tag:-v0.23.0}"
}

check_current_version() {
  if command -v headscale &>/dev/null; then
    headscale version 2>/dev/null | head -1 | tr -d '[:space:]' || echo ""
  else
    echo ""
  fi
}

# ── Docker Compose deployment ────────────────────────────────────────────────

deploy_docker() {
  local ver="${VERSION:-latest}"
  local cfg_dir
  cfg_dir="$(dirname "$CONFIG_PATH")"

  log "Preparing Docker Compose deployment (version: $ver)"
  log "Config directory: $cfg_dir"

  if $DRY_RUN; then
    log "[DRY-RUN] Would create $cfg_dir/docker-compose.yml"
    log "[DRY-RUN] Would create $cfg_dir/config.yaml"
    log "[DRY-RUN] Would run: docker compose up -d"
    json_out '{"version":"'"$ver"'","method":"docker","dry_run":true,"config_dir":"'"$cfg_dir"'","status":"preview"}'
    return 0
  fi

  mkdir -p "$cfg_dir"

  # Write docker-compose.yml
  cat > "$cfg_dir/docker-compose.yml" <<COMPOSE
version: "3.9"
services:
  headscale:
    image: headscale/headscale:${ver#v}
    container_name: headscale
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "3478:3478/udp"
    volumes:
      - ${cfg_dir}/data:/var/lib/headscale
      - ${cfg_dir}:/etc/headscale
    command: headscale serve
COMPOSE
  log "Created $cfg_dir/docker-compose.yml"

  # Write default config if it doesn't exist
  if [[ ! -f "$CONFIG_PATH" ]]; then
    write_default_config "$CONFIG_PATH" "$cfg_dir"
    log "Created default config at $CONFIG_PATH"
  fi

  log "Starting Headscale with Docker Compose..."
  (cd "$cfg_dir" && docker compose up -d)

  json_out '{"version":"'"$ver"'","method":"docker","dry_run":false,"config_dir":"'"$cfg_dir"'","status":"deployed"}'
}

# ── Binary deployment ────────────────────────────────────────────────────────

deploy_binary() {
  local arch os url ver installed_ver
  arch="$(detect_arch)"
  os="$(detect_os)"

  if [[ -z "$VERSION" ]]; then
    ver="$(get_latest_version)"
  else
    ver="${VERSION#v}"
    ver="v${ver}"
  fi

  installed_ver="$(check_current_version)"
  if [[ "$installed_ver" == "$ver" ]]; then
    log "Headscale $ver is already installed. Skipping."
    json_out '{"version":"'"$ver"'","action":"skipped","reason":"already_installed","installed":true}'
    return 0
  fi

  local tarball="headscale_${ver#v}_${os}_${arch}.tar.gz"
  url="${GITHUB_DL}/${ver}/${tarball}"

  log "Version: $ver"
  log "Platform: ${os}/${arch}"
  log "Download: $url"
  log "Config:   $CONFIG_PATH"

  if $DRY_RUN; then
    log "[DRY-RUN] Would download: $url"
    log "[DRY-RUN] Would install to: /usr/local/bin/headscale"
    log "[DRY-RUN] Would create user: headscale"
    log "[DRY-RUN] Would create systemd unit"
    log "[DRY-RUN] Would write config: $CONFIG_PATH"
    json_out '{"version":"'"$ver"'","method":"binary","dry_run":true,"arch":"'"$arch"'","os":"'"$os"'","config_path":"'"$CONFIG_PATH"'","status":"preview"}'
    return 0
  fi

  # Download
  log "Downloading Headscale $ver..."
  local tmpdir
  tmpdir="$(mktemp -d)"
  curl -sSfL "$url" -o "$tmpdir/$tarball"
  tar -xzf "$tmpdir/$tarball" -C "$tmpdir"

  # Install binary
  install -o root -g root -m 0755 "$tmpdir/headscale" /usr/local/bin/headscale
  log "Installed binary to /usr/local/bin/headscale"

  # Create system user
  if ! id -u headscale &>/dev/null; then
    useradd --system --no-create-home --shell /usr/sbin/nologin headscale
    log "Created system user: headscale"
  fi

  # Create config directory
  local cfg_dir
  cfg_dir="$(dirname "$CONFIG_PATH")"
  mkdir -p "$cfg_dir"

  # Write config if it doesn't exist
  if [[ ! -f "$CONFIG_PATH" ]]; then
    write_default_config "$CONFIG_PATH" "$cfg_dir"
    log "Created default config at $CONFIG_PATH"
  fi

  # Set permissions
  chown -R headscale:headscale "$cfg_dir"

  # Create systemd unit
  local unit_file="/etc/systemd/system/headscale.service"
  if [[ ! -f "$unit_file" ]]; then
    cat > "$unit_file" <<UNIT
[Unit]
Description=headscale control server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=headscale
Group=headscale
ExecStart=/usr/local/bin/headscale serve
Restart=on-failure
RestartSec=5
WorkingDirectory=${cfg_dir}
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
UNIT
    log "Created systemd unit: $unit_file"
    systemctl daemon-reload
  fi

  # Enable and start
  systemctl enable headscale.service
  systemctl start headscale.service
  log "Headscale service started and enabled"

  # Cleanup
  rm -rf "$tmpdir"

  json_out '{"version":"'"$ver"'","method":"binary","dry_run":false,"arch":"'"$arch"'","os":"'"$os"'","config_path":"'"$CONFIG_PATH"'","status":"deployed","service":"headscale.service"}'
}

# ── Default config writer ────────────────────────────────────────────────────

write_default_config() {
  local path="$1"
  local data_dir="$2/data"

  cat > "$path" <<CONFIG
# headscale configuration
server_url: https://localhost:443
listen_addr: 0.0.0.0:8080
metrics_listen_addr: 127.0.0.1:9090
grpc_listen_addr: 127.0.0.1:50443
grpc_allow_insecure: false

database:
  type: sqlite3
  path: ${data_dir}/db.sqlite3

tls_letsencrypt_hostname: ""
tls_letsencrypt_cache_dir: ${data_dir}/cache
tls_letsencrypt_challenge_type: HTTP-01
tls_cert_path: ""
tls_key_path: ""

log:
  level: info
  format: text

acl_policy_path: ""

dns_config:
  nameservers:
    - 1.1.1.1
    - 8.8.8.8
  domains: []
  magic_dns: true
  base_domain: example.com

unix_socket: /var/run/headscale/headscale.sock
unix_socket_permission: "0770"

derp:
  server:
    enabled: false
    region_id: 999
    region_name: "my-headscale"
    stun_listen_addr: "0.0.0.0:3478"
  urls: []
  paths: []
  auto_update_enabled: true
  update_frequency: 24h

ephemeral_node_inactivity_timeout: 30m
node_update_check_interval: 10s
CONFIG
}

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
  if $DOCKER; then
    deploy_docker
  else
    deploy_binary
  fi
}

main
