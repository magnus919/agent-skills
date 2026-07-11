#!/usr/bin/env bash
set -euo pipefail
OUT=${1:-k8s-gather-$(date -u +%Y%m%dT%H%M%SZ)}
mkdir -p "$OUT"
run() { name=$1; shift; "$@" >"$OUT/$name.txt" 2>&1 || printf 'command failed: %s\n' "$*" >>"$OUT/$name.txt"; }
run context kubectl config current-context
run version kubectl version -o json
run readiness kubectl get --raw='/readyz?verbose'
run api-resources kubectl api-resources -o wide
run api-versions kubectl api-versions
run nodes kubectl get nodes -o wide
run system-pods kubectl get pods -A -o wide
run events kubectl events -A --types=Warning --sort-by=.lastTimestamp
run crds kubectl get crd
run storage kubectl get pvc,pv,storageclass -A
run webhooks kubectl get mutatingwebhookconfigurations,validatingwebhookconfigurations
printf 'Collected bounded diagnostics in %s\n' "$OUT"
printf 'Secrets and raw kubeconfig were intentionally omitted.\n'
