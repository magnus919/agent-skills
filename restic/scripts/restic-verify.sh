#!/usr/bin/env bash
# Bounded read-only repository verification. Does not alter retention or delete data.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/restic-verify.sh [--repo REPOSITORY] [--password-file PATH]
                                [--read-data-subset PERCENT] [--full-data]

Runs `restic check` against an existing repository. By default it checks metadata.
--read-data-subset accepts restic syntax such as 5% or 500M. --full-data reads all
repository data and can be expensive. Repository/password environment variables are
used when corresponding flags are omitted. Secret values are never printed.
EOF
}

repo="${RESTIC_REPOSITORY:-}"
password_file="${RESTIC_PASSWORD_FILE:-}"
read_subset=""
full_data=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) repo=${2:?ERROR: --repo needs a value}; shift 2 ;;
    --password-file) password_file=${2:?ERROR: --password-file needs a value}; shift 2 ;;
    --read-data-subset) read_subset=${2:?ERROR: --read-data-subset needs a value}; shift 2 ;;
    --full-data) full_data=true; shift ;;
    --help) usage; exit 0 ;;
    *) printf 'ERROR: unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if ! command -v restic >/dev/null 2>&1; then
  printf 'ERROR: restic is not on PATH.\n' >&2
  exit 127
fi
if [[ -z $repo ]]; then
  printf 'ERROR: repository missing. Use --repo or RESTIC_REPOSITORY.\n' >&2
  exit 2
fi
if [[ -n $read_subset && $full_data == true ]]; then
  printf 'ERROR: choose either --read-data-subset or --full-data.\n' >&2
  exit 2
fi

args=(--repo "$repo")
if [[ -n $password_file ]]; then
  args+=(--password-file "$password_file")
fi
args+=(check)
if [[ $full_data == true ]]; then
  args+=(--read-data)
elif [[ -n $read_subset ]]; then
  args+=(--read-data-subset "$read_subset")
fi

printf 'Running read-only restic check (%s).\n' \
  "$([[ $full_data == true ]] && printf 'full data' || [[ -n $read_subset ]] && printf 'sample %s' "$read_subset" || printf 'metadata')"
restic "${args[@]}"
printf 'PASS: restic check completed. Run a separate restore drill for recovery evidence.\n'
