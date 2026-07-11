#!/usr/bin/env bash
set -euo pipefail

# Portable diagnostics. Never removes containers, networks, or volumes.
project_dir="${1:-.}"
json=false
if [[ "${1:-}" == "--json" ]]; then project_dir="."; json=true; fi
if [[ "${2:-}" == "--json" ]]; then json=true; fi
if [[ ! -d "$project_dir" ]]; then printf 'error: project directory not found: %s\n' "$project_dir" >&2; exit 2; fi
if ! command -v docker >/dev/null 2>&1; then printf 'error: docker CLI not found\n' >&2; exit 127; fi
if ! docker compose version >/dev/null 2>&1; then printf 'error: docker compose plugin unavailable\n' >&2; exit 127; fi
cd "$project_dir"
status=0
docker compose config --quiet >/dev/null 2>&1 || status=$?
services="$(docker compose config --services 2>/dev/null || true)"
if $json; then
  python3 - "$status" "$services" <<'PY'
import json, sys
print(json.dumps({"config_valid": int(sys.argv[1]) == 0,
                  "services": [x for x in sys.argv[2].splitlines() if x]}))
PY
else
  printf 'Compose project: %s\n' "$PWD"
  if (( status == 0 )); then printf 'Config: valid\n'; else printf 'Config: INVALID (run docker compose config for details)\n'; fi
  printf 'Services:\n%s\n' "${services:-<unavailable>}"
  docker compose ps --all || true
fi
exit "$status"
