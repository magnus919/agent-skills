#!/usr/bin/env bash
# test-lidarr-cli.sh — Dry-run smoke tests for lidarr-cli
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

echo "=== lidarr-cli smoke tests ==="
echo ""

echo "--- help ---"
check "help shows status" "python3 $DIR/lidarr-cli --help" "status"
check "help shows artists" "python3 $DIR/lidarr-cli --help" "artists"
check "help shows lookup" "python3 $DIR/lidarr-cli --help" "lookup"
check "help shows lookup-album" "python3 $DIR/lidarr-cli --help" "lookup-album"
check "help shows add" "python3 $DIR/lidarr-cli --help" "add"
check "help shows albums" "python3 $DIR/lidarr-cli --help" "albums"
check "help shows tracks" "python3 $DIR/lidarr-cli --help" "tracks"
check "help shows track-files" "python3 $DIR/lidarr-cli --help" "track-files"
check "help shows quality-profile" "python3 $DIR/lidarr-cli --help" "quality-profile"
check "help shows metadata-profile" "python3 $DIR/lidarr-cli --help" "metadata-profile"
check "help shows root-folder" "python3 $DIR/lidarr-cli --help" "root-folder"
check "help shows calendar" "python3 $DIR/lidarr-cli --help" "calendar"
check "help shows queue" "python3 $DIR/lidarr-cli --help" "queue"
check "help shows history" "python3 $DIR/lidarr-cli --help" "history"
check "help shows wanted" "python3 $DIR/lidarr-cli --help" "wanted"
check "help shows search" "python3 $DIR/lidarr-cli --help" "search"
check "help shows disk-space" "python3 $DIR/lidarr-cli --help" "disk-space"
check "help shows health" "python3 $DIR/lidarr-cli --help" "health"

echo ""
echo "--- dry-run commands ---"
check "dry-run status" "python3 $DIR/lidarr-cli --dry-run status" "dry-run"
check "dry-run artists" "python3 $DIR/lidarr-cli --dry-run artists" "dry-run"
check "dry-run lookup" "python3 $DIR/lidarr-cli --dry-run lookup --term Radiohead" "dry-run"
check "dry-run lookup-album" "python3 $DIR/lidarr-cli --dry-run lookup-album --term OK" "dry-run"
check "dry-run add" "python3 $DIR/lidarr-cli --dry-run add --mb-id a74b1b7f --root /music" "dry-run.*a74b1b7f"
check "dry-run albums" "python3 $DIR/lidarr-cli --dry-run albums --artist-id 1" "dry-run"
check "dry-run tracks" "python3 $DIR/lidarr-cli --dry-run tracks --album-id 1" "dry-run"
check "dry-run track-files" "python3 $DIR/lidarr-cli --dry-run track-files --album-id 1" "dry-run"
check "dry-run quality-profile (all)" "python3 $DIR/lidarr-cli --dry-run quality-profile" "dry-run"
check "dry-run quality-profile (by id)" "python3 $DIR/lidarr-cli --dry-run quality-profile 4" "dry-run"
check "dry-run metadata-profile" "python3 $DIR/lidarr-cli --dry-run metadata-profile" "dry-run"
check "dry-run root-folder" "python3 $DIR/lidarr-cli --dry-run root-folder" "dry-run"
check "dry-run calendar" "python3 $DIR/lidarr-cli --dry-run calendar" "dry-run"
check "dry-run queue" "python3 $DIR/lidarr-cli --dry-run queue" "dry-run"
check "dry-run history" "python3 $DIR/lidarr-cli --dry-run history" "dry-run"
check "dry-run wanted" "python3 $DIR/lidarr-cli --dry-run wanted" "dry-run"
check "dry-run search" "python3 $DIR/lidarr-cli --dry-run search --artist-id 5" "dry-run.*artist id=5"
check "dry-run disk-space" "python3 $DIR/lidarr-cli --dry-run disk-space" "dry-run"
check "dry-run health" "python3 $DIR/lidarr-cli --dry-run health" "dry-run"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
