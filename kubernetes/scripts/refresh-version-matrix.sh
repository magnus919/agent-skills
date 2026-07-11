#!/usr/bin/env bash
# Refresh release observations for human review. This script intentionally does
# not edit references automatically: version claims need source reconciliation.
set -euo pipefail
command -v gh >/dev/null || { echo 'gh is required' >&2; exit 127; }
printf 'Research date: '; date -u +%Y-%m-%d
printf '\nKubernetes docs:\nhttps://kubernetes.io/releases/\n'
for repo in k3s-io/k3s rancher/rke2 k0sproject/k0s siderolabs/talos kubernetes-sigs/kind kubernetes/minikube; do
  gh release view --repo "$repo" --json name,publishedAt,url
 done
cat <<'EOF'

Review output against references/distributions.md and references/operations.md before editing.
EOF
