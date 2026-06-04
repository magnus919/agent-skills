#!/usr/bin/env bash
# test-arr-cli.sh — Dry-run smoke tests for arr-cli
# No API keys or live servers needed. All tests use --dry-run.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

ok()   { PASS=$((PASS+1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL+1)); echo "  ✗ $1"; }
check() {
    local desc="$1" cmd="$2" pattern="$3"
    output=$(eval "$cmd" 2>&1) && echo "$output" | grep -q "$pattern" && ok "$desc" || fail "$desc (expected '$pattern' in output)"
}

echo "=== arr-cli smoke tests ==="
echo ""

echo "--- radarr-cli ---"
check "help shows add subcommand" \
    "python3 $DIR/radarr-cli --help" \
    "  add"

check "help shows search subcommand" \
    "python3 $DIR/radarr-cli --help" \
    "  search"

check "help shows quality-profile" \
    "python3 $DIR/radarr-cli --help" \
    "quality-profile"

check "dry-run status" \
    "python3 $DIR/radarr-cli --dry-run status" \
    "dry-run"

check "dry-run movies" \
    "python3 $DIR/radarr-cli --dry-run movies" \
    "dry-run"

check "dry-run lookup" \
    "python3 $DIR/radarr-cli --dry-run lookup --term Dune" \
    "dry-run"

check "dry-run add" \
    "python3 $DIR/radarr-cli --dry-run add --tmdb-id 550 --root /movies" \
    "dry-run.*550"

check "dry-run quality-profile (all)" \
    "python3 $DIR/radarr-cli --dry-run quality-profile" \
    "dry-run"

check "dry-run quality-profile (by id)" \
    "python3 $DIR/radarr-cli --dry-run quality-profile 4" \
    "dry-run"

check "dry-run search" \
    "python3 $DIR/radarr-cli --dry-run search --movie-id 5" \
    "dry-run.*movie id=5"

check "dry-run queue" \
    "python3 $DIR/radarr-cli --dry-run queue" \
    "dry-run"

check "dry-run history" \
    "python3 $DIR/radarr-cli --dry-run history" \
    "dry-run"

check "dry-run root-folder" \
    "python3 $DIR/radarr-cli --dry-run root-folder" \
    "dry-run"

check "dry-run calendar" \
    "python3 $DIR/radarr-cli --dry-run calendar" \
    "dry-run"

check "dry-run collections" \
    "python3 $DIR/radarr-cli --dry-run collections" \
    "dry-run"

echo ""
echo "--- sonarr-cli ---"
check "help shows add subcommand" \
    "python3 $DIR/sonarr-cli --help" \
    "  add"

check "help shows quality-profile" \
    "python3 $DIR/sonarr-cli --help" \
    "quality-profile"

check "help shows episode-file" \
    "python3 $DIR/sonarr-cli --help" \
    "episode-file"

check "dry-run status" \
    "python3 $DIR/sonarr-cli --dry-run status" \
    "dry-run"

check "dry-run series" \
    "python3 $DIR/sonarr-cli --dry-run series" \
    "dry-run"

check "dry-run lookup" \
    "python3 $DIR/sonarr-cli --dry-run lookup --term Severance" \
    "dry-run"

check "dry-run add" \
    "python3 $DIR/sonarr-cli --dry-run add --tvdb-id 77526 --root /tv --series-type Standard" \
    "dry-run.*77526"

check "dry-run add with anime flags" \
    "python3 $DIR/sonarr-cli --dry-run add --tvdb-id 12345 --root /tv --series-type Anime --no-season-folder" \
    "dry-run"

check "dry-run quality-profile (all)" \
    "python3 $DIR/sonarr-cli --dry-run quality-profile" \
    "dry-run"

check "dry-run quality-profile (by id)" \
    "python3 $DIR/sonarr-cli --dry-run quality-profile 4" \
    "dry-run"

check "dry-run episode-file" \
    "python3 $DIR/sonarr-cli --dry-run episode-file --series-id 1" \
    "dry-run"

check "dry-run search" \
    "python3 $DIR/sonarr-cli --dry-run search --series-id 5" \
    "dry-run.*series id=5"

check "dry-run queue" \
    "python3 $DIR/sonarr-cli --dry-run queue" \
    "dry-run"

check "dry-run history" \
    "python3 $DIR/sonarr-cli --dry-run history" \
    "dry-run"

check "dry-run root-folder" \
    "python3 $DIR/sonarr-cli --dry-run root-folder" \
    "dry-run"

check "dry-run calendar" \
    "python3 $DIR/sonarr-cli --dry-run calendar" \
    "dry-run"

check "dry-run wanted" \
    "python3 $DIR/sonarr-cli --dry-run wanted --limit 5" \
    "dry-run"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
