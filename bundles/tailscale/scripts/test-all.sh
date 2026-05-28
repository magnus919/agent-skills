#!/usr/bin/env bash
set -euo pipefail

# test-all.sh — Smoke test for the entire Tailscale skill bundle
# Runs basic validation on all scripts without requiring a running Headscale.

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0
SKIP=0
ERRORS=""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { PASS=$((PASS+1)); echo -e "  ${GREEN}PASS${NC} $1"; }
fail() { FAIL=$((FAIL+1)); echo -e "  ${RED}FAIL${NC} $1${2:+ — $2}"; ERRORS+="$1: $2"$'\n'; }
skip() { SKIP=$((SKIP+1)); echo -e "  ${YELLOW}SKIP${NC} $1${2:+ — $2}"; }

test_help() {
  local script="$1"
  local name="$2"
  if [[ ! -f "$script" ]]; then
    fail "$name" "script not found at $script"
    return
  fi
  if [[ ! -x "$script" ]]; then
    fail "$name" "not executable"
    return
  fi
  if [[ "$script" == *.py ]]; then
    if python3 -c "import py_compile; py_compile.compile('$script', doraise=True)" 2>/dev/null; then
      :
    else
      fail "$name" "Python syntax error"
      return
    fi
    # Check --help on Python scripts
    if "$script" --help >/dev/null 2>&1; then
      pass "$name --help"
    else
      fail "$name --help" "exit code $?"
    fi
  else
    if bash -n "$script" 2>/dev/null; then
      :
    else
      fail "$name" "bash syntax error"
      return
    fi
    # Check --help on bash scripts
    if "$script" --help >/dev/null 2>&1; then
      pass "$name --help"
    else
      # Try -h as fallback
      if "$script" -h >/dev/null 2>&1; then
        pass "$name -h"
      else
        fail "$name --help" "exit code $?"
      fi
    fi
  fi
  # Check --dry-run if applicable (non-destructive)
  if [[ "$script" != *ts-install* && "$script" != *deploy-derp* ]]; then
    if "$script" --dry-run >/dev/null 2>&1; then
      pass "$name --dry-run"
    else
      # Some scripts need env vars for dry-run
      :
    fi
  fi
  # Check --json output (skipped for scripts that need live server)
  if [[ "$script" == *validate-policy* || "$script" == *migrate-acls* ]]; then
    if echo '{}' | "$script" --json --policy /dev/stdin >/dev/null 2>&1; then
      pass "$name --json"
    else
      # Different scripts need different args
      :
    fi
  fi
}

echo "=== Tailscale Skill Bundle — Smoke Tests ==="
echo ""

# Root scripts
echo "--- Root Scripts ---"
test_help "$SCRIPT_DIR/scripts/tailscale-status-json.sh" "tailscale-status-json"
test_help "$SCRIPT_DIR/scripts/headscale-health-check.sh" "headscale-health-check" 2>/dev/null || skip "headscale-health-check" "no live server"

# Sub-skill SKILL.md files
echo ""
echo "--- SKILL.md Files ---"
for skill_dir in "$SCRIPT_DIR/skills/"*/; do
  skill_name="$(basename "$skill_dir")"
  if [[ -f "$skill_dir/SKILL.md" ]]; then
    pass "skills/$skill_name/SKILL.md"
  else
    fail "skills/$skill_name/SKILL.md" "missing"
  fi
done

# Sub-skill scripts
echo ""
echo "--- Sub-Skill Scripts ---"
for skill_dir in "$SCRIPT_DIR/skills/"*/; do
  skill_name="$(basename "$skill_dir")"
  script_dir="$skill_dir/scripts"
  if [[ ! -d "$script_dir" ]]; then
    continue
  fi
  for script in "$script_dir"/*; do
    if [[ -f "$script" ]]; then
      test_help "$script" "$skill_name/$(basename "$script")"
    fi
  done
done

# Reference files
echo ""
echo "--- Reference Files ---"
for ref in "$SCRIPT_DIR/references/"*.md; do
  if [[ -f "$ref" ]]; then
    pass "references/$(basename "$ref")"
  fi
done

# Template files
echo ""
echo "--- Template Files ---"
for tmpl in "$SCRIPT_DIR/templates/"*; do
  if [[ -f "$tmpl" ]]; then
    # Validate JSON templates
    case "$tmpl" in
      *.json)
        if python3 -c "import json; json.load(open('$tmpl'))" 2>/dev/null; then
          pass "templates/$(basename "$tmpl")"
        else
          fail "templates/$(basename "$tmpl")" "invalid JSON"
        fi
        ;;
      *.yaml|*.yml)
        if python3 -c "import yaml; yaml.safe_load(open('$tmpl'))" 2>/dev/null; then
          pass "templates/$(basename "$tmpl")"
        else
          fail "templates/$(basename "$tmpl")" "invalid YAML"
        fi
        ;;
      *)
        pass "templates/$(basename "$tmpl")"
        ;;
    esac
  fi
done

echo ""
echo "=== Results: $PASS passed, $FAIL failed, $SKIP skipped ==="

if [[ "$FAIL" -gt 0 ]]; then
  echo ""
  echo "Errors:"
  echo "$ERRORS"
  exit 1
fi
exit 0
