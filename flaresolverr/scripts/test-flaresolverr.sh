#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 scripts/flaresolverr --help >/dev/null
python3 -m py_compile scripts/flaresolverr
printf '%s\n' 'FlareSolverr CLI smoke checks passed.'
