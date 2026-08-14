#!/usr/bin/env bash
# =============================================================================
# ts-install.sh — Tailscale Client Installation Script
# =============================================================================
# Description:
#   Auto-detect the operating system and install the official Tailscale client.
#   Supports Debian/Ubuntu (apt), macOS (brew), Windows (choco),
#   Fedora/RHEL (yum/dnf), and Alpine (apk).
#
# Usage:
#   ./ts-install.sh [options]
#
# Options:
#   --login-server <URL>    Headscale server URL to configure after install
#   --authkey <key>         Pre-authentication key for non-interactive auth
#   --dry-run               Preview actions without executing them
#   --json                  Output results in JSON format
#   --help                  Show this help message and exit
#
# Environment:
#   HEADSCALE_URL           Default --login-server value
#   TAILSCALE_AUTHKEY       Default --authkey value
#
# Examples:
#   ./ts-install.sh --login-server https://headscale.example.com
#   ./ts-install.sh --login-server https://headscale.example.com --authkey tskey-auth-xxxxx
#   ./ts-install.sh --dry-run --json
#   HEADSCALE_URL=https://headscale.example.com ./ts-install.sh
# =============================================================================

set -euo pipefail

# ---- Colors / Formatting ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ---- Defaults ----
LOGIN_SERVER=""
AUTHKEY=""
DRY_RUN=false
JSON_OUTPUT=false

# ---- Functions ----
info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

usage() {
    grep "^# " "$0" | sed 's/^# //' | sed 's/^#//'
    exit 0
}

json_escape() {
    echo "$1" | sed 's/"/\\"/g'
}

json_output() {
    local status="$1"
    local message="$2"
    local platform="$3"
    local version="$4"
    cat <<EOF
{
  "status": "$(json_escape "$status")",
  "message": "$(json_escape "$message")",
  "platform": "$(json_escape "$platform")",
  "version": "$(json_escape "$version")",
  "login_server": "$(json_escape "${LOGIN_SERVER:-not-configured}")"
}
EOF
}

# ---- Parse Arguments ----
while [[ $# -gt 0 ]]; do
    case "$1" in
        --login-server)
            LOGIN_SERVER="$2"
            shift 2
            ;;
        --authkey)
            AUTHKEY="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            error "Unknown option: $1"
            usage
            ;;
    esac
done

# Apply env var defaults
LOGIN_SERVER="${LOGIN_SERVER:-${HEADSCALE_URL:-}}"
AUTHKEY="${AUTHKEY:-${TAILSCALE_AUTHKEY:-}}"

# ---- Detect Platform ----
detect_platform() {
    if command -v apt-get &>/dev/null || [[ -f /etc/debian_version ]]; then
        echo "debian"
    elif command -v brew &>/dev/null && [[ "$(uname)" == "Darwin" ]]; then
        echo "macos"
    elif command -v choco &>/dev/null && [[ "$(uname -s)" == MINGW* || "$(uname -s)" == CYGWIN* ]]; then
        echo "windows"
    elif command -v dnf &>/dev/null; then
        echo "fedora"
    elif command -v yum &>/dev/null; then
        echo "rhel"
    elif command -v apk &>/dev/null; then
        echo "alpine"
    elif command -v brew &>/dev/null && [[ "$(uname)" == "Linux" ]]; then
        echo "linuxbrew"
    else
        echo "unknown"
    fi
}

PLATFORM=$(detect_platform)

# ---- Check if already installed ----
check_installed_version() {
    if command -v tailscale &>/dev/null; then
        tailscale version 2>/dev/null | head -1
    else
        echo ""
    fi
}

EXISTING_VERSION=$(check_installed_version)

# ---- Dry-Run Mode ----
if [[ "$DRY_RUN" == "true" ]]; then
    INSTALL_CMD=""
    case "$PLATFORM" in
        debian)  INSTALL_CMD="curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null && curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list && sudo apt-get update && sudo apt-get install -y tailscale" ;;
        macos)   INSTALL_CMD="brew install tailscale" ;;
        windows) INSTALL_CMD="choco install tailscale" ;;
        fedora)  INSTALL_CMD="sudo dnf install -y tailscale" ;;
        rhel)    INSTALL_CMD="sudo yum install -y tailscale" ;;
        alpine)  INSTALL_CMD="apk add tailscale" ;;
        *)       INSTALL_CMD="UNKNOWN_PLATFORM" ;;
    esac

    if [[ "$JSON_OUTPUT" == "true" ]]; then
        json_output "dry-run" "Platform detected: ${PLATFORM}. Would install tailscale. Existing version: ${EXISTING_VERSION:-none}" "${PLATFORM}" "${EXISTING_VERSION:-}"
    else
        info "Dry-run mode — no changes will be made"
        info "Detected platform: ${PLATFORM}"
        info "Tailscale already installed: ${EXISTING_VERSION:-no}"
        info "Install command: ${INSTALL_CMD}"
        if [[ -n "$LOGIN_SERVER" ]]; then
            info "Would configure --login-server: ${LOGIN_SERVER}"
        fi
        if [[ -n "$AUTHKEY" ]]; then
            info "Would authenticate with --authkey: ${AUTHKEY:0:16}..."
        fi
    fi
    exit 0
fi

# ---- Proceed with Installation ----
INSTALL_NEEDED=false

if [[ -n "$EXISTING_VERSION" ]]; then
    success "Tailscale already installed: ${EXISTING_VERSION}"
else
    INSTALL_NEEDED=true
    info "Installing tailscale on ${PLATFORM}..."
fi

if [[ "$INSTALL_NEEDED" == "true" ]]; then
    case "$PLATFORM" in
        debian)
            info "Detected Debian/Ubuntu — installing via apt"
            curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
            curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list >/dev/null
            sudo apt-get update
            sudo apt-get install -y tailscale
            ;;
        macos)
            info "Detected macOS — installing via Homebrew"
            brew install tailscale
            ;;
        windows)
            info "Detected Windows — installing via Chocolatey"
            choco install tailscale -y
            ;;
        fedora)
            info "Detected Fedora — installing via dnf"
            sudo dnf install -y dnf-plugins-core
            sudo dnf config-manager --add-repo https://pkgs.tailscale.com/stable/fedora/tailscale.repo
            sudo dnf install -y tailscale
            ;;
        rhel)
            info "Detected RHEL/CentOS — installing via yum"
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://pkgs.tailscale.com/stable/rhel/tailscale.repo
            sudo yum install -y tailscale
            ;;
        alpine)
            info "Detected Alpine — installing via apk"
            apk add tailscale
            ;;
        linuxbrew)
            info "Detected Linux + Homebrew — installing via brew"
            brew install tailscale
            ;;
        *)
            error "Unknown platform. Please install tailscale manually from https://tailscale.com/download"
            if [[ "$JSON_OUTPUT" == "true" ]]; then
                json_output "error" "Unknown platform. Manual installation required." "unknown" ""
            fi
            exit 1
            ;;
    esac

    # Verify installation
    NEW_VERSION=$(check_installed_version)
    if [[ -n "$NEW_VERSION" ]]; then
        success "Tailscale ${NEW_VERSION} installed successfully"
    else
        error "Installation completed but tailscale command not found"
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            json_output "error" "Installation completed but command not found" "${PLATFORM}" ""
        fi
        exit 1
    fi
fi

# ---- Start the daemon (if applicable) ----
if [[ "$PLATFORM" != "macos" && "$PLATFORM" != "windows" ]]; then
    # Check if tailscaled is running
    if systemctl is-active tailscaled &>/dev/null 2>&1; then
        success "tailscaled already running"
    else
        info "Starting tailscaled..."
        sudo systemctl enable --now tailscaled 2>/dev/null || {
            warn "Could not start tailscaled via systemd. Try: sudo systemctl start tailscaled"
        }
    fi
fi

# ---- Configure login server / authenticate ----
if [[ -n "$LOGIN_SERVER" ]]; then
    if [[ -n "$AUTHKEY" ]]; then
        info "Authenticating with Headserver: ${LOGIN_SERVER}"
        sudo tailscale up --login-server="${LOGIN_SERVER}" --authkey="${AUTHKEY}" 2>&1 || {
            error "Failed to authenticate with Headscale"
            if [[ "$JSON_OUTPUT" == "true" ]]; then
                json_output "error" "Authentication failed" "${PLATFORM}" "$(check_installed_version)"
            fi
            exit 1
        }
        success "Authenticated with ${LOGIN_SERVER}"
    else
        warn "No --authkey provided. Run the following to authenticate interactively:"
        echo "  sudo tailscale up --login-server=${LOGIN_SERVER}"
    fi
fi

# ---- Final Result ----
FINAL_VERSION=$(check_installed_version)

if [[ "$JSON_OUTPUT" == "true" ]]; then
    json_output "success" "Tailscale installed and configured" "${PLATFORM}" "${FINAL_VERSION}"
else
    success "Tailscale ${FINAL_VERSION} ready on ${PLATFORM}"
fi
