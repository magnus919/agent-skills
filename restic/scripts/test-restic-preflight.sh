#!/usr/bin/env bash
# Deterministic test for restic-preflight.sh. No repository or installed restic needed.
set -euo pipefail

skill_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/bin"
cat > "$tmp/bin/restic" <<'EOF'
#!/usr/bin/env sh
[ "$1" = version ] || exit 64
printf 'restic 0.test\n'
EOF
chmod +x "$tmp/bin/restic"

output=$(PATH="$tmp/bin:$PATH" RESTIC_REPOSITORY=/backup RESTIC_PASSWORD_FILE=/secure/password \
  "$skill_root/scripts/restic-preflight.sh")
printf '%s\n' "$output" | grep -F 'restic: restic 0.test' >/dev/null
printf '%s\n' "$output" | grep -F 'repository configuration: RESTIC_REPOSITORY' >/dev/null
printf '%s\n' "$output" | grep -F 'password configuration: RESTIC_PASSWORD_FILE' >/dev/null
if printf '%s\n' "$output" | grep -F '/secure/password' >/dev/null; then
  printf 'FAIL: preflight exposed a password path\n' >&2
  exit 1
fi
printf 'PASS: restic-preflight.sh reports configuration presence without secret values.\n'
