#!/usr/bin/env bash
# Run the lifecycle evaluation corpus end-to-end with the fake adapter.
#
# Loops every corpus manifest (14 per-skill + 3 bundle umbrellas = 17) through
# eval_runner with --adapter fake and aggregates the exit status. A trial that
# reports a failure (non-"completed" status) or a runner error counts as a
# corpus failure. The script exits 0 only when every trial in every manifest
# completed with zero failures.
#
# No API keys, model credentials, or network access are required: the fake
# adapter is fully deterministic (see eval_runner/fake_adapter.py).
#
# Usage (from the repository root):
#   bash lifecycle-evals/scripts/run-corpus.sh
#
# Output artifacts are written under ${CORPUS_OUT_DIR} (default: /tmp/lifecycle-evals-runs),
# one subdirectory per skill, with per-trial manifests under
# <out>/<skill>/manifests/*.manifest.json. The committed one-snapshot artifact
# copy lives in lifecycle-evals/run-artifacts/manifests/ and is refreshed only
# at merge time (VAL-CRP-021 churn policy: do NOT gate CI on artifact freshness).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="$ROOT/.venv/bin/python"
OUT_DIR="${CORPUS_OUT_DIR:-/tmp/lifecycle-evals-runs}"

if [[ ! -x "$PYTHON" ]]; then
  echo "error: $PYTHON not found (is the repository .venv set up?)" >&2
  exit 2
fi

MANIFESTS=(
  "implementation-planning/evals/evals.json"
  "product-analytics-and-measurement/evals/evals.json"
  "product-roadmapping-and-portfolio/evals/evals.json"
  "product-experimentation/evals/evals.json"
  "product-adoption/evals/evals.json"
  "conditional-customer-success/evals/evals.json"
  "product-operations-and-governance/evals/evals.json"
  "product-lifecycle-learning/evals/evals.json"
  "production-readiness/evals/evals.json"
  "migration-engineering/evals/evals.json"
  "resilience-and-recovery/evals/evals.json"
  "capacity-and-cost-engineering/evals/evals.json"
  "incident-learning/evals/evals.json"
  "privacy-engineering/evals/evals.json"
  "product-lifecycle/evals/evals.json"
  "production-excellence/evals/evals.json"
  "agent-production-operations/evals/evals.json"
)

total_failures=0
for manifest in "${MANIFESTS[@]}"; do
  skill_dir="$(dirname "$(dirname "$manifest")")"
  echo "==> $manifest"
  if ! "$PYTHON" -m eval_runner "$ROOT/$manifest" --adapter fake \
    --output-dir "$OUT_DIR/$skill_dir"; then
    echo "FAIL: $manifest" >&2
    total_failures=$((total_failures + 1))
  fi
done

if [[ "$total_failures" -gt 0 ]]; then
  echo "corpus run FAILED: $total_failures manifest(s) reported failures" >&2
  exit 1
fi

echo "corpus run OK: ${#MANIFESTS[@]} manifests, 0 failures (fake adapter, no credentials)"
exit 0
