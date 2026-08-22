# Service Patterns

## Architecture Styles

| Style | Separation axis | Best for | Tradeoff |
|-------|----------------|----------|----------|
| Layered | Technical layer (controller → service → repository) | Simple CRUD services, convention-based frameworks | Business logic leaks across layers |
| Clean Architecture | Dependency direction (outer → inner) | Complex business logic, long-lived projects | Boilerplate for interfaces |
| Hexagonal (Ports & Adapters) | External vs internal (ports as boundaries) | Services with multiple I/O sources | More interfaces upfront |
| Pipeline | Request flow through stages | Data processing, middleware-heavy services | Composable but hard to trace |

## Request Lifecycle

```
Request → Middleware 1 → Middleware N → Router → Controller → Service → Repository → Database
                                             ↓
                                        Response ← Middleware N ← Middleware 1 ←
```

Each layer has a distinct responsibility:

| Layer | Responsibility | Doesn't do |
|-------|---------------|------------|
| Middleware | Auth, logging, rate limiting, CORS, tracing | Business logic, data access |
| Controller | Request parsing, validation, response formatting | Business decisions, database queries |
| Service | Business rules, workflow orchestration, state mgmt | HTTP concerns, direct database access |
| Repository | Data access, query construction, result mapping | Business rules, request parsing |

## Domain, Application, And Infrastructure

Use the boundary that makes policy independent from delivery and storage details:

| Boundary | Responsibility | Dependency rule |
|---|---|---|
| Domain | Invariants, state transitions, value semantics, and meaningful business facts | No framework, database, broker, or vendor imports |
| Application | Use-case coordination, ports, unit-of-work scope, authorization handoff, and transaction intent | Depends on domain and interfaces it owns; does not construct infrastructure |
| Infrastructure | ORM/data mapping, transaction implementation, broker relay, HTTP clients, and framework wiring | Implements application ports; does not decide domain policy |

Organize by business capability or use case within the bounded context before falling
back to technical layers. Keep one logical commit boundary visible in the application
service. For state changes that publish facts, use the focused
[`event-driven-service-implementation.md`](event-driven-service-implementation.md)
reference for outbox/inbox coordination, replay, and failure behavior. The existing
DDD catalog in [`programming-principles`](../../programming-principles/SKILL.md)
owns bounded-context, aggregate, repository, and domain-modeling decisions; do not
duplicate it here.

## Background Job Processing

| Pattern | When to use | Concerns |
|---------|-------------|----------|
| In-process worker | Lightweight, no external deps | Memory, process lifecycle, scaling |
| Message queue | Reliable async processing | Queue management, retry, DLQ |
| Scheduled cron | Periodic batch work | Timing guarantees, overlap |
| Event-driven streaming | Real-time event processing | State management, ordering |

Every background job should be: idempotent, retryable, and have a defined failure path (dead letter or alert).
