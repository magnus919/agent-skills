# multi-tenant-saas-architecture
Design a coherent architecture for subscription products serving many customer tenants.

## Why Install This Skill

Multi-tenant SaaS decisions cross product semantics, identity, provisioning, data placement, usage, billing, and operations. Without one architecture view, teams often choose an isolation model before defining the customer promise, or let billing, support, and deletion paths become afterthoughts.

This skill helps an agent turn those seams into explicit decisions and handoffs. It compares tenancy shapes per resource, distinguishes control-plane policy from application serving, and makes tenant lifecycle and noisy-neighbor behavior reviewable without replacing security, finance, capacity, platform, API, or implementation specialists.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Triggerable workflow, output contract, and ownership boundaries |
| `references/` | Five focused decision guides plus public-source and transformation index |
| `templates/` | SaaS brief, tenancy decision record, and lifecycle checklist |
| `evals/evals.json` | Eight output-quality cases for architecture and routing behavior |

## Quick Start

No credentials or runtime dependencies are required. Start with a service promise and tenant vocabulary, then use the brief template:

```text
Define the tenant model and compare pooled, bridge, and silo choices for this SaaS product.
```

## Triggers

- Designing or reviewing a multi-tenant SaaS architecture
- Choosing pooled, bridge, silo, or hybrid tenancy
- Defining control-plane and application-plane boundaries
- Connecting onboarding, entitlements, metering, billing, and tenant lifecycle
- Planning tenant-aware restore, deletion, quotas, or noisy-neighbor behavior

## Requirements

- An agent client that supports Agent Skills-format directories
- Repository access to the linked specialist skills when handoffs are needed
- Organization-specific customer, contract, scale, privacy, and recovery facts supplied by the user
