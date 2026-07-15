#!/usr/bin/env bash
# Read-only local readiness check. It never opens a repository or prints secrets.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/restic-preflight.sh

Checks that restic is installed and reports only the presence/type of configured
repository and password settings. It never runs a command against the repository
and never prints secret values.
EOF
}

if [[ ${1:-} == "--help" ]]; then
  usage
  exit 0
fi
if [[ $# -ne 0 ]]; then
  usage >&2
  exit 2
fi

if ! command -v restic >/dev/null 2>&1; then
  printf 'ERROR: restic is not on PATH. Install it, then rerun this check.\n' >&2
  exit 127
fi

version=$(restic version 2>&1) || {
  printf 'ERROR: restic was found but `restic version` failed.\n' >&2
  exit 1
}

repository_source=unset
if [[ -n ${RESTIC_REPOSITORY:-} ]]; then
  repository_source=RESTIC_REPOSITORY
elif [[ -n ${RESTIC_REPOSITORY_FILE:-} ]]; then
  repository_source=RESTIC_REPOSITORY_FILE
fi

password_source=unset
if [[ -n ${RESTIC_PASSWORD_FILE:-} ]]; then
  password_source=RESTIC_PASSWORD_FILE
elif [[ -n ${RESTIC_PASSWORD_COMMAND:-} ]]; then
  password_source=RESTIC_PASSWORD_COMMAND
elif [[ -n ${RESTIC_PASSWORD:-} ]]; then
  password_source=RESTIC_PASSWORD
fi

printf 'restic: %s\n' "$version"
printf 'repository configuration: %s\n' "$repository_source"
printf 'password configuration: %s\n' "$password_source"

if [[ $password_source == RESTIC_PASSWORD ]]; then
  printf 'WARNING: RESTIC_PASSWORD is set. Prefer RESTIC_PASSWORD_FILE or RESTIC_PASSWORD_COMMAND for unattended jobs.\n' >&2
fi
if [[ $repository_source == unset || $password_source == unset ]]; then
  printf 'STATUS: incomplete configuration; set a repository location and protected password source before live operations.\n'
  exit 3
fi

printf 'STATUS: local prerequisites present; run `restic snapshots` next to verify repository access.\n'
