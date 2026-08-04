# CRM — Operate HubSpot from the Terminal

Look up contacts, search records, and view deal pipeline stages from your terminal or agent — and apply confirmed stage changes — all against HubSpot's CRM API.

## Why Install This Skill

CRM data is where the answers to "who is this person?" and "what is in the pipeline?" live, and agents have had no bounded way to reach it. This skill gives your agent a real read path into HubSpot (contact records, contact search, deal pipeline views, pipeline stage maps) and a safe write path: moving a deal between stages is a guarded mutation that requires a preview and an explicit confirmation, so the agent can answer sales questions without ever silently changing the pipeline.

It ships `crm-cli`, a small Python script that speaks the HubSpot CRM v3 API with no third-party dependencies. Reads are capped (`--limit`), output is clean JSON for the agent or readable text for you, and `--help` works with no token and no network. Records are summarized as the fields people actually ask about — name, email, company, amount, stage — instead of raw property maps.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating contract, mutation gates, and verification boundaries |
| `references/` | Dated source index and a HubSpot CRM operations reference (endpoints, object model, pagination, stage updates, errors) |
| `scripts/crm-cli` | Bounded, stdlib-only CLI: contacts list/get/search, deals list/update-stage, pipelines list; `--json`, `--limit`, stage changes gated by `--dry-run`/`--yes` |
| `tests/` | 13 deterministic tests against a stub HubSpot API, covering the mutation gate and read-only contract |
| `evals/evals.json` | Six output-quality evaluation cases for agent runs |

## Quick Start

```bash
# Help works with no token and no network
crm/scripts/crm-cli --help

# List contacts (capped)
HUBSPOT_TOKEN=pat_... crm/scripts/crm-cli --json --limit 20 contacts list

# Find a contact by name
HUBSPOT_TOKEN=pat_... crm/scripts/crm-cli --json contacts search --query "ada"

# View the deal pipeline (optionally filtered)
HUBSPOT_TOKEN=pat_... crm/scripts/crm-cli --json --limit 20 deals list
HUBSPOT_TOKEN=pat_... crm/scripts/crm-cli --json deals list --pipeline default --stage appointmentscheduled

# Resolve stage labels to IDs
HUBSPOT_TOKEN=pat_... crm/scripts/crm-cli --json pipelines list

# Move a deal only with a preview first, then explicit confirmation
HUBSPOT_TOKEN=pat_... crm/scripts/crm-cli deals update-stage --id 901 --stage closedwon --dry-run
HUBSPOT_TOKEN=pat_... crm/scripts/crm-cli deals update-stage --id 901 --stage closedwon --yes
```

## Triggers

Load this skill for `hubspot` / `crm` operations: "who is this contact", searching contacts, what deals are in the pipeline, listing deals by stage, resolving pipeline stages, or moving a deal to a new stage with confirmation. Do not load it for building HubSpot apps or workflow automations, marketing automation, or other CRMs like Salesforce.

## Requirements

- Python 3.9+ for `crm-cli` (stdlib only; `--help` needs nothing else).
- A HubSpot private app access token (`HUBSPOT_TOKEN`) with object scopes: `crm.objects.contacts.read` and `crm.objects.deals.read` for reads, plus `crm.objects.deals.write` for stage updates.
- Network access to `api.hubapi.com` for live reads and updates.
