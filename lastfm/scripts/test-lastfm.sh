#!/usr/bin/env bash
# lastfm-cli test suite
set -euo pipefail
PASS=0
FAIL=0

test() {
    local desc="$1"
    shift
    if "$@" 2>&1; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc"
        FAIL=$((FAIL + 1))
    fi
}

check_output() {
    local desc="$1" expected="$2"
    shift 2
    local output
    output="$("$@" 2>&1 || true)"
    if echo "$output" | grep -qi "$expected"; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc (expected to contain '$expected')"
        echo "       Got: $output"
        FAIL=$((FAIL + 1))
    fi
}

# CLI path — adjust if not on PATH
CLI=lastfm-cli

echo "=== lastfm-cli Test Suite ===
"

# 1. Syntax check
test "Python syntax check" python3 -c "import py_compile; py_compile.compile('$CLI', doraise=True)"
echo ""

# 2. --help on main
check_output "--help shows usage" "Examples" $CLI --help
echo ""

# 3. --help on subcommands
check_output "user --help" "username" $CLI user info --help
check_output "artist --help" "similar" $CLI artist --help
check_output "track --help" "scrobble" $CLI track --help
check_output "chart --help" "top-artists" $CLI chart --help
check_output "geo --help" "country" $CLI geo top-artists --help
check_output "tag --help" "top-albums" $CLI tag --help
echo ""

# 4. Missing required args → error with corrective info
check_output "user info missing username → error" "required" $CLI user info
check_output "artist info missing artist → error" "required" $CLI artist info
echo ""

# 5. --dry-run works on read commands
check_output "user recent-tracks --dry-run" "dry" $CLI user recent-tracks testuser --dry-run
echo ""

# 6. --json output with no api key → graceful error
check_output "Missing API key → graceful error" "LASTFM_API_KEY" $CLI user info testuser
echo ""

echo "=== Results: $PASS passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] || exit 1