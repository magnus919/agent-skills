# OBEY Implementing Domain-Driven Design by Vaughn Vernon

## When to use

Use when DDD implementation choices affect bounded contexts, language, aggregates, repositories, events, application services, package structure, or cross-context integration.

## Primary bias to correct

Practical DDD is not renamed CRUD. Model the operational domain inside an explicit Bounded Context, with local language, small invariant boundaries, identity references across Aggregates, and explicit translation across context and infrastructure boundaries.

## Decision rules

- Name the Bounded Context before interpreting terms, modules, services, repositories, events, APIs, persistence, or integrations; never force one global company model.
- Use the local Ubiquitous Language consistently: one concept gets one term inside the context, one term must not carry multiple meanings, and code, tests, events, commands, repositories, services, and packages must speak that language.
- Protect the Core Domain from generic abstractions and vendor terms; spend richer modeling where competitive or operational complexity lives, keep supporting subdomains simpler, and avoid DDD ceremony for trivial CRUD.
- Make every context interaction explicit: show the relationship, translation responsibility, and upstream/downstream influence before sharing data, terms, models, or integration code.
- Translate foreign, legacy, partner, external, and infrastructure models into the local language; keep foreign schemas, statuses, contract models, and aggregates out of local domain objects.
- Treat Aggregates as immediate consistency boundaries: keep them small, expose one root, route invariant-changing behavior through the root, hide mutable internals, and expose intention-revealing behavior instead of arbitrary setters.
- Reference other Aggregates by identity, avoid large connected object graphs, and default to one Aggregate per transaction; use events, policies, or process coordination when consistency can be eventual.
- Use Entities when identity and lifecycle matter, and make their methods protect meaningful state transitions rather than generic state changes.
- Use immutable Value Objects for meaningful descriptive concepts; validate at construction, compare by value, and replace raw primitives for meaningful identifiers, quantities, ranges, names, and whole values.
- Use Domain Services only for domain-significant operations that require multiple domain objects and fit no Entity or Value Object; keep technical transformation, serialization, transport, and persistence mapping outside the domain model.
- Provide Repositories for Aggregate Roots, not tables; define interfaces by domain or application needs, return domain objects or domain-oriented results, and keep business rules out of repository implementations.
- Publish Domain Events only for meaningful completed business facts; name them in the past tense, keep payloads local to the model, and do not use events for every property change or to hide poor Aggregate design.
- Use Event Sourcing only when the event sequence is the right persistence model; streams must match Aggregate identity and versioning, replay must be deterministic, and event meaning changes need versioning, upcasters, or translators.
- Keep Application Services as use-case coordinators: load Aggregates, invoke domain behavior, persist results, publish resulting events, own transaction or integration coordination, and keep core decisions in the domain model.
- Organize modules by Bounded Context first and by domain or use-case ownership within the context; avoid giant `shared` or `common` packages for domain concepts.
- Keep command behavior separate from query models when consistency, performance, or representation needs justify it.
- Test domain behavior and boundaries directly: Aggregate invariants, valid and invalid state transitions, Value Object validation, Domain Events as outcomes.

## Trigger rules

- When a term is ambiguous, reused across contexts, or drifting into a technical placeholder, qualify, split, or rename it before coding further.
- When code wants to import another context's domain package, share enums across contexts, or couple through another context's database, add explicit translation instead.
- When legacy, vendor, partner, API, transport, persistence, or UI shape appears in local domain code, add an Anticorruption Layer.
- When an Aggregate boundary changes or one transaction wants multiple Aggregates, list the immediate invariants that require it.
- When a Repository becomes generic CRUD, reshape it around Aggregate access.

## Final checklist

- Bounded Context explicit before interpreting terms?
- One local term per concept across all code?
- Aggregates small, root-protected, one per transaction?
- Entities behavior-bearing? Value Objects immutable, validated?
- Repositories Aggregate-root access points, not ORM leaks?
- Application Services coordinate, domain model decides?
