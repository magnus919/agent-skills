# OBEY Patterns of Enterprise Application Architecture by Martin Fowler

## When to use

Use when designing or reviewing enterprise application code that crosses presentation, application workflow, domain logic, persistence, transactions, concurrency, integration, session state, or remote boundaries.

## Primary bias to correct

Enterprise applications are not improved by inventing architecture for every feature. Use a small set of well-understood patterns to make responsibilities and boundaries explicit.

## Decision rules

- Make responsibility ownership explicit: presentation, workflow, domain logic, data source, transaction management, and concurrency control must not collapse into one class.
- Use layering as the default, but every layer must earn its cost. Reject pass-through layering theater.
- Choose business logic pattern by force: Transaction Script for simple flows, Table Module for table-centered set logic, Domain Model for significant rules and invariants.
- Use a Service Layer to define application operations and coordinate use cases. Do not absorb all domain logic into services.
- At remote boundaries, use Remote Facade and DTOs. DTOs are transport structures, not domain models.
- Choose persistence deliberately: Repositories speak domain terms, Data Mappers keep SQL out of domain objects, Active Record only for simple domains.
- Use Identity Map for one object per identity per scope, Unit of Work for one logical commit, Lazy Load only where hidden database calls won't surprise readers.
- Design concurrency in the application workflow: optimistic locks detect conflicts, pessimistic locks require justified contention, transactions stay short.
- Keep presentation focused on input/rendering/routing. Business rules stay out of controllers, views, and templates.
- Access external systems through boundaries. Translate partner formats. Do not let vendor payloads shape internal design.
- Choose session state deliberately: client, server, or database storage accounts for integrity, scaling, cleanup.

## Trigger rules

- If domain behavior appears in controllers, views, handlers, SQL, DTOs, or framework glue, move it to the owning layer.
- If a class coordinates rendering, validation, SQL, transactions, domain rules, and external calls, split it.
- If a Transaction Script accumulates duplicated decisions, revisit Domain Model.
- If a layer only forwards calls, treat it as a forbidden-pattern review blocker.

## Final checklist

- Presentation, workflow, domain, persistence separated intentionally?
- Business logic pattern matches actual complexity?
- Transaction ownership explicit and short?
- Remote boundaries coarse, translated, failure-aware?
