#!/usr/bin/env bash
set -euo pipefail
fail=0
kubectl get --raw='/readyz' >/dev/null || fail=1
if kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}' | grep -qv $'\tTrue$'; then
  echo 'one or more nodes are not Ready' >&2; fail=1
fi
if kubectl get pods -n kube-system -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\n"}{end}' | grep -qv $'\tRunning$'; then
  echo 'one or more kube-system pods are not Running' >&2; fail=1
fi
if [ "$fail" -eq 0 ]; then echo 'cluster health: PASS'; else echo 'cluster health: FAIL'; fi
exit "$fail"
