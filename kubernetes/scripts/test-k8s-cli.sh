#!/usr/bin/env bash
set -euo pipefail
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
CLI="$ROOT/scripts/k8s-cli"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/kubectl" <<'FAKE'
#!/usr/bin/env bash
set -u
printf '{"argv":['
first=1
for arg in "$@"; do [ "$first" = 1 ] || printf ','; first=0; printf '%s' "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$arg")"; done
printf '],"kind":"List","items":[]}'
FAKE
chmod +x "$TMP/kubectl"
run() { KUBECTL="$TMP/kubectl" "$CLI" --json "$@"; }

out=$(run get pods --namespace test)
python3 -c 'import json,sys; d=json.loads(sys.argv[1]); assert d["ok"] and d["result"]["kind"] == "List"' "$out"

if run delete pod/example --namespace test >/dev/null 2>&1; then
  echo 'delete must require --yes' >&2; exit 1
fi
run delete pod/example --namespace test --dry-run >/dev/null
run delete pod/example --namespace test --yes >/dev/null

if run raw /api/../secrets >/dev/null 2>&1; then
  echo 'raw traversal must be rejected' >&2; exit 1
fi

echo 'k8s-cli tests: PASS'
