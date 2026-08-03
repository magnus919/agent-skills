# Backend Engineering

Backend engineering methodology — API implementation patterns (REST, gRPC, GraphQL), service architecture (clean/hexagonal/layered), database access patterns, integration and middleware design, error handling, and service-level testing. Language and framework agnostic.

## Why Install This Skill

Your agent gains structured patterns for API design, service architecture, database access, error handling, and integration — instead of improvising each time. Fillable templates turn service designs and error contracts into reviewable records, and the bundled N+1 query spotter catches a whole class of database performance bugs during review.

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Core methodology, trigger conditions, reference index |
| `references/` | Deep-dive reference files loaded on demand |
| `templates/` | Fillable records: service design record, error-handling taxonomy |
| `scripts/` | `n1-query-spotter.py` — scans Python source for potential N+1 query patterns |
| `evals/` | Output-quality eval manifest for the skill's methodology cases |

## Triggers

Building or reviewing APIs, designing service layers, implementing database access patterns, adding error handling, or integrating external services.

## Requirements

Platform-agnostic. Applicable to any language/framework stack. The bundled script needs only Python 3 (standard library).

## Quick Start

Scan a service for potential N+1 query patterns before a performance review:

```bash
python3 backend-engineering/scripts/n1-query-spotter.py services/orders.py
```

Each finding points at the query call, the enclosing loop, and whether the loop variable is used in the query (high confidence vs possible). Add `--json` for machine-readable output, and run it from CI — the script exits 1 when findings exist.

Load SKILL.md for the methodology overview and reference table, then load specific references as needed for the task at hand.
