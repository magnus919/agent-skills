# OBEY Domain-Driven Design by Eric Evans

## When to use

Use when designing or reviewing software for complex domains where business rules, invariants, lifecycle, and domain language must drive the model rather than database tables, frameworks, or generic CRUD habits.

## Primary bias to correct

The most critical business behavior does not live in a schema, service, controller, or DTO. It needs a model that speaks the domain language and guards its invariants.

## Decision rules

- Model the domain, not the data schema. The model expresses the business language, rules, and invariants before storage, UI, or transport constraints shape it.
- Use the Ubiquitous Language in code: one concept, one term, shared across developers and domain experts. Refactor the model when language drifts.
- Place each model in a Bounded Context. Define context boundaries explicitly; do not force one company-wide model. Translate between contexts.
- Use Entities for objects with identity and lifecycle continuity. Their responsibilities protect state transitions that domain rules require.
- Use Value Objects for objects whose identity is based on their attributes — immutable, self-validating, replaceable. Replace primitive obsession with meaningful domain types.
- Use Services only for operations that fit naturally in no Entity or Value Object. Keep services thin — they orchestrate, the model decides.
- Make Aggregates small. Each transaction modifies one Aggregate. Reference other Aggregates by identity, not by object graph.
- Use Repositories to retrieve Aggregates. Keep fact-finding queries in a separate mechanism when the domain does not need them.
- Use Domain Events for significant business occurrences when other parts of the model or other contexts must react.
- Use Factories for complex creation logic when object construction should not be in the client. Keep creation atomic with valid initial state.
- Keep infrastructure, framework, and technical cross-cutting concerns outside the domain model. Use dependency injection to provide domain-layer services when needed.
- Let strategic design drive tactical design: first find the Core Domain, then apply Entity, Value Object, Aggregate, Service, Repository, and Event where the complexity lives.
- Protect the Core Domain from the Generic and Supporting subdomains. Invest the best modeling effort in the core.

## Trigger rules

- If a name is ambiguous or means different things to different team members, start a Bounded Context discussion before modeling further.
- If terms live only in database column names, API contracts, UI labels, or conversation but not in code, bring them into the model.
- If business rules or validation exist in controllers, views, services, or SQL rather than in domain objects, move them inward.
- If a model has no invariants or behavior beyond getters/setters, question whether you need a rich Domain Model or can use a simpler pattern.
- If one transaction touches multiple aggregates, re-evaluate the aggregate boundaries or use eventual consistency with domain events.
- If a primitive is used for an important concept (money, currency, email, range, quantity) and validation or behavior is duplicated, replace it with a Value Object.
- If services accumulate logic that belongs in entities or value objects, push it down.

## Final checklist

- Does the code speak the Ubiquitous Language?
- Are Bounded Contexts explicit?
- Do Aggregates protect invariants and remain small?
- Are Value Objects used for meaningful domain concepts?
- Does infrastructure stay outside the domain model?
