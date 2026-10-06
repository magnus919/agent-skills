#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARGS=(restore "$@")
if [[ "${HEADSCALE_SKIP_SERVICE_CONTROL:-}" == "1" ]]; then
  ARGS+=(--skip-service-control)
fi
exec python3 "${SCRIPT_DIR}/hs-archive.py" "${ARGS[@]}"
