#!/usr/bin/env bash
# test-prowlarr-cli.sh — Dry-run smoke tests for prowlarr-cli
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

ok()   { PASS=$((PASS+1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL+1)); echo "  ✗ $1"; }
check() {
    local desc="$1" cmd="$2" pattern="$3"
    output=$(eval "$cmd" 2>&1) && echo "$output" | grep -q "$pattern" && ok "$desc" || fail "$desc (expected '$pattern')"
}

echo "=== prowlarr-cli smoke tests ==="
echo ""

echo "--- help ---"
for cmd in status indexers indexer indexer-stats indexer-status applications download-clients history health tags test-all; do
    check "help shows $cmd" "python3 $DIR/prowlarr-cli --help" "$cmd"
done

echo ""
echo "--- dry-run commands ---"
check "dry-run status" "python3 $DIR/prowlarr-cli --dry-run status" "dry-run"
check "dry-run indexers" "python3 $DIR/prowlarr-cli --dry-run indexers" "dry-run"
check "dry-run indexer (by id)" "python3 $DIR/prowlarr-cli --dry-run indexer 5" "dry-run"
check "dry-run indexer-stats" "python3 $DIR/prowlarr-cli --dry-run indexer-stats" "dry-run"
check "dry-run indexer-status" "python3 $DIR/prowlarr-cli --dry-run indexer-status" "dry-run"
check "dry-run applications" "python3 $DIR/prowlarr-cli --dry-run applications" "dry-run"
check "dry-run download-clients" "python3 $DIR/prowlarr-cli --dry-run download-clients" "dry-run"
check "dry-run history" "python3 $DIR/prowlarr-cli --dry-run history" "dry-run"
check "dry-run health" "python3 $DIR/prowlarr-cli --dry-run health" "dry-run"
check "dry-run tags" "python3 $DIR/prowlarr-cli --dry-run tags" "dry-run"
check "dry-run test-all" "python3 $DIR/prowlarr-cli --dry-run test-all" "dry-run.*Test all"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
