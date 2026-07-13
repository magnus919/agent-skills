# API Design And Evolution

Design APIs that consumers can integrate with, operate, and migrate without relying on unwritten assumptions.

## Why Install This Skill

An API is a long-lived agreement: mobile apps, partners, generated SDKs, jobs, and
event consumers can all depend on details that are easy to overlook. This skill helps
your agent begin with the consumer's job and the domain's meaning before naming a
route or selecting a protocol.

It produces practical design artifacts for HTTP, GraphQL, RPC, events, webhooks, and
streams. Your agent can document retries, errors, authorization boundaries, delivery
semantics, compatibility risks, and a migration path instead of treating an OpenAPI
file as the whole design.

## What You Get

| Contents | Provides |
|---|---|
| `SKILL.md` | A workflow from discovery through rollout and verification |
| `references/` | Protocol, schema, failure, event, evolution, testing, and source guidance |
| `templates/` | Fillable briefs, contracts, taxonomies, assessments, plans, and reviews |

## Quick Start

Ask your agent: `Design an API contract for creating and listing invoices, including retry and migration behavior.`

It should begin an API design brief, select an interface style from the workload, and
produce a contract reviewable by consumers and implementers.

## Triggers

- Design or review a REST/HTTP, GraphQL, RPC, event, webhook, or streaming API
- Write or improve OpenAPI or AsyncAPI contracts
- Define pagination, errors, idempotency, concurrency, or rate/resource behavior
- Assess a consumer-breaking API change, version an interface, or plan deprecation
- Build a migration and rollback plan for an external interface

## Requirements

No runtime dependencies or API keys. The skill links to public standards; validate
tooling support before relying on a specific OpenAPI or AsyncAPI feature for code
generation or documentation.
