#!/usr/bin/env bash
# ===========================================================================
# headscale-derp: deploy-derp.sh — Deploy standalone DERP server (Docker)
# ===========================================================================
# Deploys a standalone Tailscale DERP relay server using the official
# tailscale/derper Docker image.
#
# Usage:
#   deploy-derp.sh --region-id <ID> --region-name <NAME> --hostname <HOST>
#     [--cert <PATH> --key <PATH>] [--dry-run] [--json] [--output-dir <DIR>]
#     [--compose] [--stun-port <PORT>] [--relay-port <PORT>]
#
# Options:
#   --region-id      Numeric region ID (e.g., 900). Required.
#   --region-name    Human-readable region name (e.g., "New York"). Required.
#   --region-code    Short region code (e.g., "us-nyc"). Default: from hostname.
#   --hostname       FQDN for the DERP server. Required.
#   --cert           Path to TLS cert PEM file (mutually exclusive with --acme).
#   --key            Path to TLS key PEM file (requires --cert).
#   --acme           Use Let's Encrypt auto-cert instead of manual certs.
#   --stun-port      STUN UDP port. Default: 3478.
#   --relay-port     DERP TCP/TLS port. Default: 443.
#   --verify-domain  Domain to verify TLS against (default: --hostname).
#   --output-dir     Directory for generated DERP map JSON. Default: ./derp-maps
#   --compose        Generate a docker-compose.yml alongside the DERP map.
#   --dry-run        Print configuration without deploying.
#   --json           Output structured JSON instead of human-readable text.
#   --help           Show this help message and exit.
#
# Examples:
#   deploy-derp.sh --region-id 900 --region-name "New York" \
#     --hostname derp-nyc.example.com --acme
#
#   deploy-derp.sh --region-id 901 --region-name "Frankfurt" \
#     --hostname derp-fra.example.com \
#     --cert /etc/certs/fullchain.pem --key /etc/certs/privkey.pem
#
#   deploy-derp.sh --region-id 902 --region-name "Tokyo" \
#     --hostname derp-tokyo.example.com --acme --compose --dry-run
# ===========================================================================

set -euo pipefail

# --- Constants ---
SCRIPT_NAME="$(basename "$0")"
DEFAULT_STUN_PORT=3478
DEFAULT_RELAY_PORT=443
DEFAULT_OUTPUT_DIR="./derp-maps"
HEADSCALE_DIR="${HEADSCALE_DIR:-}"
DERPER_IMAGE="tailscale/derper:latest"

# --- Colors (disabled if not a terminal) ---
if [[ -t 2 ]]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
    CYAN='\033[0;36m'; NC='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; CYAN=''; NC=''
fi

log_info()  { echo -e "${GREEN}[INFO]${NC} $*" >&2; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# --- Help ---
usage() {
    sed -n '/^# Usage:/,/^$/{s/^# //;s/^#//;p;}' "$0" | sed '$d'
    exit 0
}

# --- Parse arguments ---
REGION_ID=""
REGION_NAME=""
REGION_CODE=""
HOSTNAME=""
CERT_PATH=""
KEY_PATH=""
ACME=false
STUN_PORT="$DEFAULT_STUN_PORT"
RELAY_PORT="$DEFAULT_RELAY_PORT"
VERIFY_DOMAIN=""
OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"
COMPOSE=false
DRY_RUN=false
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --region-id)     REGION_ID="$2";  shift 2 ;;
        --region-name)   REGION_NAME="$2"; shift 2 ;;
        --region-code)   REGION_CODE="$2"; shift 2 ;;
        --hostname)      HOSTNAME="$2";   shift 2 ;;
        --cert)          CERT_PATH="$2";   shift 2 ;;
        --key)           KEY_PATH="$2";    shift 2 ;;
        --acme)          ACME=true;        shift   ;;
        --stun-port)     STUN_PORT="$2";   shift 2 ;;
        --relay-port)    RELAY_PORT="$2";  shift 2 ;;
        --verify-domain) VERIFY_DOMAIN="$2"; shift 2 ;;
        --output-dir)    OUTPUT_DIR="$2";  shift 2 ;;
        --compose)       COMPOSE=true;     shift   ;;
        --dry-run)       DRY_RUN=true;     shift   ;;
        --json)          JSON_OUTPUT=true; shift   ;;
        --help|-h)       usage ;;
        *) log_error "Unknown argument: $1"; exit 1 ;;
    esac
done

# --- Validation ---
ERRORS=()
[[ -z "$REGION_ID" ]]       && ERRORS+=("--region-id is required")
[[ -z "$REGION_NAME" ]]     && ERRORS+=("--region-name is required")
[[ -z "$HOSTNAME" ]]        && ERRORS+=("--hostname is required")

if [[ -n "$CERT_PATH" && -z "$KEY_PATH" ]]; then
    ERRORS+=("--cert requires --key")
fi
if [[ -z "$CERT_PATH" && "$ACME" == false ]]; then
    ERRORS+=("Either --cert/--key or --acme is required")
fi
if [[ -n "$CERT_PATH" && "$ACME" == true ]]; then
    ERRORS+=("--cert/--key and --acme are mutually exclusive")
fi

# Validate region ID is numeric
if [[ -n "$REGION_ID" && ! "$REGION_ID" =~ ^[0-9]+$ ]]; then
    ERRORS+=("--region-id must be a number, got: $REGION_ID")
fi

if [[ ${#ERRORS[@]} -gt 0 ]]; then
    for e in "${ERRORS[@]}"; do log_error "$e"; done
    echo "" >&2
    usage
fi

# --- Defaults ---
[[ -z "$REGION_CODE" ]] && REGION_CODE="${HOSTNAME%%.*}"
[[ -z "$VERIFY_DOMAIN" ]] && VERIFY_DOMAIN="$HOSTNAME"

# --- Build DERP map JSON ---
build_derp_map() {
    cat <<JSON
{
  "Regions": {
    "${REGION_ID}": {
      "RegionID": ${REGION_ID},
      "RegionCode": "${REGION_CODE}",
      "RegionName": "${REGION_NAME}",
      "Nodes": [
        {
          "Name": "${REGION_ID}a",
          "RegionID": ${REGION_ID},
          "HostName": "${HOSTNAME}",
          "DERPPort": ${RELAY_PORT},
          "STUNPort": ${STUN_PORT},
          "STUNOnly": false
        }
      ]
    }
  }
}
JSON
}

# --- Build docker-compose.yml ---
build_compose() {
    local vol_certs vol_data cmd_extra
    vol_certs=""
    vol_data="/var/lib/derper:/var/lib/derper"
    cmd_extra=""

    if [[ "$ACME" == true ]]; then
        vol_certs="/etc/letsencrypt:/certs"
        cmd_extra=""
    else
        vol_certs="${CERT_PATH}:${CERT_PATH}:ro"
        # Derper requires cert+key as mounted files; the --cert and --key flags
        # point to the container-side paths.
        cmd_extra="--cert=${CERT_PATH} --key=${KEY_PATH}"
    fi

    cat <<YAML
version: "3.8"

services:
  derper:
    image: ${DERPER_IMAGE}
    container_name: derper-${REGION_CODE}
    restart: always
    ports:
      - "${STUN_PORT}:${STUN_PORT}/udp"
      - "${RELAY_PORT}:${RELAY_PORT}"
    volumes:
      - ${vol_certs}
      - ${vol_data}
    environment:
      - DERP_HOST=${HOSTNAME}
      - DERP_ADDR=:${RELAY_PORT}
      - DERP_STUN_ADDR=:${STUN_PORT}
      - DERP_CERT_MODE=${ACME}
      - DERP_VERIFY_CLIENTS=false
    command:
      - "--hostname=${HOSTNAME}"
      - "--addr=:${RELAY_PORT}"
      - "--stun-port=${STUN_PORT}"
      ${cmd_extra:+${cmd_extra}}
YAML
}

# --- Generate output ---
DERP_MAP_JSON=$(build_derp_map)

if [[ "$JSON_OUTPUT" == true ]]; then
    # Structured JSON output
    OUTPUT=$(cat <<EOF
{
  "status": "ok",
  "script": "${SCRIPT_NAME}",
  "dry_run": ${DRY_RUN},
  "region": {
    "id": ${REGION_ID},
    "name": "${REGION_NAME}",
    "code": "${REGION_CODE}",
    "hostname": "${HOSTNAME}"
  },
  "ports": {
    "stun": ${STUN_PORT},
    "relay": ${RELAY_PORT}
  },
  "tls": $(if [[ "$ACME" == true ]]; then echo '"lets-encrypt"'; else echo '{"cert":"'"${CERT_PATH}"'","key":"'"${KEY_PATH}"'"}'; fi),
  "derp_map": ${DERP_MAP_JSON}
}
EOF
)
    echo "$OUTPUT"
    exit 0
fi

# --- Dry-run / deploy ---
if [[ "$DRY_RUN" == true ]]; then
    log_info "=== DERP Deployment Configuration (DRY RUN) ==="
    echo ""
    echo "Region ID:       ${REGION_ID}"
    echo "Region Name:     ${REGION_NAME}"
    echo "Region Code:     ${REGION_CODE}"
    echo "Hostname:        ${HOSTNAME}"
    echo "STUN Port:       ${STUN_PORT}"
    echo "Relay Port:      ${RELAY_PORT}"
    if [[ "$ACME" == true ]]; then
        echo "TLS:             Let's Encrypt (auto)"
    else
        echo "TLS Cert:        ${CERT_PATH}"
        echo "TLS Key:         ${KEY_PATH}"
    fi
    echo ""
    echo "--- DERP Map (${OUTPUT_DIR}/derp-region-${REGION_ID}.json) ---"
    echo "${DERP_MAP_JSON}" | python3 -m json.tool 2>/dev/null || echo "${DERP_MAP_JSON}"
    if [[ "$COMPOSE" == true ]]; then
        echo ""
        echo "--- Docker Compose (${OUTPUT_DIR}/docker-compose-${REGION_CODE}.yml) ---"
        build_compose
    fi
    echo ""
    log_info "Dry-run complete. No changes made."
    exit 0
fi

# --- Deploy ---
log_info "Creating output directory: ${OUTPUT_DIR}"
mkdir -p "$OUTPUT_DIR"

# Write DERP map
MAP_FILE="${OUTPUT_DIR}/derp-region-${REGION_ID}.json"
echo "${DERP_MAP_JSON}" > "$MAP_FILE"
log_info "DERP map written to: ${MAP_FILE}"

if [[ "$COMPOSE" == true ]]; then
    COMPOSE_FILE="${OUTPUT_DIR}/docker-compose-${REGION_CODE}.yml"
    build_compose > "$COMPOSE_FILE"
    log_info "Docker Compose file written to: ${COMPOSE_FILE}"
fi

# Check if Docker is available
if ! command -v docker &>/dev/null; then
    log_error "Docker is not installed. Install Docker and run again."
    exit 1
fi

# Pull the image
log_info "Pulling DERP image: ${DERPER_IMAGE}"
docker pull "$DERPER_IMAGE" >&2

# Run container
CONTAINER_NAME="derper-${REGION_CODE}"

# Remove existing container if present
if docker inspect "$CONTAINER_NAME" &>/dev/null; then
    log_warn "Container '${CONTAINER_NAME}' exists. Removing..."
    docker rm -f "$CONTAINER_NAME" >&2
fi

log_info "Starting DERP container: ${CONTAINER_NAME}"

DOCKER_ARGS=(
    --name "$CONTAINER_NAME"
    --restart always
    -p "${STUN_PORT}:${STUN_PORT}/udp"
    -p "${RELAY_PORT}:${RELAY_PORT}"
)

if [[ "$ACME" == true ]]; then
    DOCKER_ARGS+=(
        -v "/etc/letsencrypt:/certs"
    )
else
    # Mount the containing directories for cert files
    DOCKER_ARGS+=(
        -v "$(dirname "$CERT_PATH"):$(dirname "$CERT_PATH"):ro"
        -v "$(dirname "$KEY_PATH"):$(dirname "$KEY_PATH"):ro"
    )
fi

DOCKER_ARGS+=(
    -v "/var/lib/derper:/var/lib/derper"
    "$DERPER_IMAGE"
    --hostname="$HOSTNAME"
    --addr=":${RELAY_PORT}"
    --stun-port="${STUN_PORT}"
)

if [[ "$ACME" == false ]]; then
    DOCKER_ARGS+=(--cert="$CERT_PATH" --key="$KEY_PATH")
fi

docker run -d "${DOCKER_ARGS[@]}" >&2

log_info "DERP server deployed successfully!"
log_info "Container:  ${CONTAINER_NAME}"
log_info "Hostname:   ${HOSTNAME}"
log_info "STUN:       ${HOSTNAME}:${STUN_PORT} (UDP)"
log_info "Relay:      ${HOSTNAME}:${RELAY_PORT} (TLS)"
log_info ""
log_info "Add this DERP map URL to your Headscale config under 'derp.urls':"
log_info "  file://$(realpath "$MAP_FILE" 2>/dev/null || echo "$MAP_FILE")"
log_info ""
log_info "Or copy the JSON contents into the Headscale 'derp.paths' JSON file."
