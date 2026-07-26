# Grafana Skill

Design and operate trustworthy Grafana dashboards, alerting, provisioning, access, and troubleshooting across OSS, Enterprise, and Cloud.

## Why Install This Skill

Grafana can look healthy while dashboards fail to reconcile, queries tell the wrong story, or alerts never reach the intended responder. Versions, editions, organizations, API generations, and provisioning methods also change which operation is safe. A plausible dashboard or copied API example is not enough.

This skill gives your agent a discovery-first workflow for Grafana itself. It identifies version and ownership, validates dashboard and alert semantics, follows notifications from rule to resolution, prevents competing as-code writers, protects credentials and access boundaries, and verifies each affected plane instead of treating `/api/health` as proof that everything works.

## What You Get

| Resource | Purpose |
|---|---|
| `SKILL.md` | Core operating contract, task routing, approval boundaries, and completion criteria |
| `references/api-and-version-discovery.md` | Version, edition, organization, authentication, permissions, and `/api` versus `/apis` selection |
| `references/dashboard-engineering.md` | Decision-oriented dashboards, query semantics, variables, panels, links, JSON, accessibility, and review |
| `references/alerting-and-routing.md` | Rules, instances, labels, policies, grouping, silences, contact points, firing, and resolved delivery |
| `references/provisioning-and-gitops.md` | File provisioning, Terraform, Git Sync, APIs/SDKs, Operator ownership, drift, migration, and rollback |
| `references/troubleshooting.md` | Structured diagnosis for panels, data sources, provisioning, alerts, proxies, plugins, and migrations |
| `references/security-and-change-control.md` | Tokens, secure fields, RBAC, sharing, plugins, destructive actions, backups, and production gates |
| `references/source-index.md` | Dated official sources, coverage, live Grafana evidence, exclusions, and refresh rules |
| `evals/evals.json` | Portable output-quality cases covering the required capability areas, version/API selection, and unsafe boundaries |
| `EVIDENCE-LEDGER.md` | Implementation evidence, verification boundaries, and known gaps |

## Quick Start

Start with read-only version and health discovery:

```sh
grafana server -v
curl --fail --silent --show-error https://grafana.example.com/api/health
```

Then identify the edition, deployment owner, organization, resource provenance, and authorized API scope before planning changes. Never place tokens directly in commands retained by shell history or reports.

## Triggers

Use this skill for Grafana dashboards, folders, variables, panels, data sources, annotations, library panels, dashboard JSON, service accounts, RBAC, alert rules, contact points, notification policies, silences, mute timings, provisioning, Terraform/Git Sync ownership, Grafana APIs, plugins, security, upgrades, or Grafana-specific troubleshooting.

Do not use it for general observability strategy, SLO or paging-policy design, operating telemetry backends, generic container/orchestrator/proxy work, plugin development, or an authorized security assessment. Load the corresponding specialist skill instead.

## Requirements

Reference-only planning needs access to current Grafana documentation. Live work requires authorized access to the target Grafana instance and its owning deployment control plane. API discovery requires an HTTP client and a least-privilege Grafana service-account token; data-source and notification verification require separately authorized test paths.
