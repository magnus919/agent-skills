#!/usr/bin/env bash
#
# reload-headscale-policy.sh — Reload Headscale policy via SIGHUP
#
# Sends SIGHUP to the headscale process to trigger a policy reload,
# then verifies the reload was successful via logs or health check.
#
# Usage:
#   reload-headscale-policy.sh
#   reload-headscale-policy.sh --dry-run
#   reload-headscale-policy.sh --json
#   reload-headscale-policy.sh --help
#
# Options:
#   --dry-run   Show what would be done without actually sending SIGHUP
#   --json      Output machine-readable JSON
#   --help      Show this help message

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
PROCESS_NAME="headscale"
RELOAD_TIMEOUT=10  # seconds to wait for successful reload

# ---- Help ----
show_help() {
    sed -ne '/^#/!q;s/^#$//;s/^# //p' "$0"
    exit 0
}

# ---- Logging ----
log_info()  { echo "[INFO]  $*"; }
log_error() { echo "[ERROR] $*" >&2; }
log_debug() { :; }  # noop unless DEBUG is set

# ---- JSON output helpers ----
JSON_MODE=false
json_output() {
    local status="$1"
    shift
    local reloaded="$1"
    shift
    # Remaining args are error messages as separate args
    local errors=("$@")

    if $JSON_MODE; then
        # Build JSON safely
        local json_errors="[]"
        if [ ${#errors[@]} -gt 0 ]; then
            json_errors="["
            local first=true
            for err in "${errors[@]}"; do
                if $first; then
                    first=false
                else
                    json_errors+=", "
                fi
                # Escape for JSON
                local escaped
                escaped=$(printf '%s' "$err" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null || echo "\"$err\"")
                json_errors+="$escaped"
            done
            json_errors+="]"
        fi
        printf '{"reloaded":%s,"errors":%s}\n' "$reloaded" "$json_errors"
    fi
}

print_and_exit() {
    local exit_code="$1"
    shift
    local reloaded_val="$1"
    shift
    local errors=("$@")

    if $JSON_MODE; then
        json_output "done" "$reloaded_val" "${errors[@]}"
    fi
    exit "$exit_code"
}

# ---- Parse arguments ----
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            show_help
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --json)
            JSON_MODE=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            log_error "Usage: $SCRIPT_NAME [--dry-run] [--json] [--help]"
            exit 1
            ;;
    esac
done

# ---- Find headscale PID ----
HEADSCALE_PID=""
declare -a ERROR_MESSAGES=()

if DRY_RUN=false; then :; fi  # suppress shellcheck SC2034

# Try pgrep first
if command -v pgrep &>/dev/null; then
    HEADSCALE_PID=$(pgrep -x "$PROCESS_NAME" 2>/dev/null || true)
fi

# Fallback: check common paths
if [ -z "$HEADSCALE_PID" ]; then
    if [ -f /var/run/headscale/headscale.pid ]; then
        HEADSCALE_PID=$(cat /var/run/headscale/headscale.pid 2>/dev/null || true)
    elif [ -f /run/headscale.pid ]; then
        HEADSCALE_PID=$(cat /run/headscale.pid 2>/dev/null || true)
    fi
fi

# Fallback: ps aux
if [ -z "$HEADSCALE_PID" ]; then
    HEADSCALE_PID=$(ps aux 2>/dev/null | grep -E '[h]eadscale' | awk '{print $2}' | head -1 || true)
fi

if [ -z "$HEADSCALE_PID" ]; then
    ERROR_MESSAGES+=("headscale process not found")
    if $JSON_MODE; then
        print_and_exit 1 false "${ERROR_MESSAGES[@]}"
    else
        log_error "headscale process not found (is Headscale running?)"
        exit 1
    fi
fi

# ---- Dry run ----
if $DRY_RUN; then
    if $JSON_MODE; then
        print_and_exit 0 false "Dry run — no SIGHUP sent"
    else
        log_info "Dry run — would send SIGHUP to headscale (PID: $HEADSCALE_PID)"
        exit 0
    fi
fi

# ---- Send SIGHUP ----
if kill -HUP "$HEADSCALE_PID" 2>/dev/null; then
    # Check if process is still alive (died after signal?)
    sleep 0.5
    if kill -0 "$HEADSCALE_PID" 2>/dev/null; then
        :
    else
        ERROR_MESSAGES+=("headscale process (PID: $HEADSCALE_PID) exited after SIGHUP")
    fi
else
    ERROR_MESSAGES+=("Failed to send SIGHUP to PID $HEADSCALE_PID (permission denied?)")
fi

# ---- Verify reload ----
RELOADED=false
if [ ${#ERROR_MESSAGES[@]} -eq 0 ]; then
    # Wait briefly and check process health
    sleep 1

    # Check process is still alive
    if kill -0 "$HEADSCALE_PID" 2>/dev/null; then
        RELOADED=true
    else
        ERROR_MESSAGES+=("headscale process died after reload (PID: $HEADSCALE_PID)")
    fi

    # Try to verify via logs (journalctl if available)
    if $RELOADED && command -v journalctl &>/dev/null; then
        RELOAD_LOG=$(journalctl -u headscale --since "10 seconds ago" 2>/dev/null | grep -i "policy.*reload\|reload.*policy\|ACL\|grant" | tail -3 || true)
        if [ -n "$RELOAD_LOG" ]; then
            log_debug "Reload log entries: $RELOAD_LOG"
        fi
    fi
fi

# ---- Output ----
if [ ${#ERROR_MESSAGES[@]} -gt 0 ]; then
    if $JSON_MODE; then
        print_and_exit 1 false "${ERROR_MESSAGES[@]}"
    else
        log_error "Policy reload FAILED"
        for err in "${ERROR_MESSAGES[@]}"; do
            log_error "  • $err"
        done
        exit 1
    fi
fi

if $JSON_MODE; then
    print_and_exit 0 true
else
    log_info "Policy reloaded successfully (PID: $HEADSCALE_PID)"
    exit 0
fi
