# OBEY Domain-Driven Design Distilled by Vaughn Vernon

## When to use

Use as a lightweight introduction to DDD when you need the benefits of strategic and tactical DDD without excessive ceremony or when onboarding a team to DDD concepts quickly.

## Primary bias to correct

DDD is not all or nothing. Start with strategic design — bounded contexts, ubiquitous language, subdomains — and apply tactical patterns only where the complexity lives.

## Decision rules

- Start with strategic design before tactical patterns. Name the Bounded Context, establish the Ubiquitous Language, and identify Core, Supporting, and Generic subdomains.
- A Bounded Context owns its model; no other context shares it. Translate between contexts with explicit mapping.
- Use Context Mapping to document relationships between contexts: Partnership, Shared Kernel, Customer-Supplier, Conformist, Anticorruption Layer, Open Host Service, Published Language, Separate Ways, Big Ball of Mud.
- Keep Aggregates small. One Aggregate per transaction. Reference by identity. Design around consistency boundaries, not data relationships.
- Use Domain Events for integration across aggregates or contexts. Keep them past-tense and meaningful to the business.
- Apply tactical patterns (Entity, Value Object, Aggregate, Repository, Domain Service, Domain Event) only where the complexity warrants them. Simple CRUD does not need DDD.
- Use Application Services to coordinate use cases; keep them thin. Domain decisions stay in the domain model.
- Repositories are for Aggregate persistence; they return domain objects. Do not expose table structures or ORM queries.
- Value Objects are immutable, self-validating, and compare by value. Replace primitives for meaningful domain concepts.
- Use Core Domain to focus the richest modeling. Spend less on Generic and Supporting subdomains.

## Trigger rules

- When a term means different things in different parts of the system, define a Bounded Context boundary.
- When two contexts exchange data, define the context mapping relationship and translation mechanism.
- When a transaction spans multiple aggregates, challenge the aggregate boundaries or use eventual consistency.
- When business logic appears in services or controllers, push it into the domain model.

## Final checklist

- Bounded Context named and documented?
- Ubiquitous Language established and used in code?
- Aggregates small, one per transaction, referenced by identity?
- Core Domain identified and getting richer modeling?
