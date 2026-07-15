#!/usr/bin/env bash
# Deterministic test for restic-verify.sh. No repository or installed restic needed.
set -euo pipefail

skill_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/bin"
cat > "$tmp/bin/restic" <<'EOF'
#!/usr/bin/env sh
printf '%s\n' "$*"
EOF
chmod +x "$tmp/bin/restic"

output=$(PATH="$tmp/bin:$PATH" "$skill_root/scripts/restic-verify.sh" \
  --repo /backup --password-file /secure/password --read-data-subset 5%)
printf '%s\n' "$output" | grep -F 'Running read-only restic check (sample 5%).' >/dev/null
printf '%s\n' "$output" | grep -F -- '--repo /backup --password-file /secure/password check --read-data-subset 5%' >/dev/null
printf '%s\n' "$output" | grep -F 'PASS: restic check completed.' >/dev/null
printf 'PASS: restic-verify.sh constructs a bounded check command.\n'
