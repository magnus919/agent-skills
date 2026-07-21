# OBEY Implementing Domain-Driven Design by Vaughn Vernon

## Purpose

This repository follows **Implementing Domain-Driven Design** in the practical style of Vaughn Vernon:
apply DDD operationally, with explicit bounded contexts, disciplined aggregates, and implementation patterns that survive real systems.

All code generation, edits, and reviews must optimize for:
- explicit bounded contexts
- local ubiquitous language
- small aggregate boundaries
- identities over object graph coupling
- eventual consistency where appropriate
- context mapping instead of shared muddled models
- practical DDD implementation instead of theory theater

This file is a binding engineering policy: `MUST` is binding, `SHOULD` is a strong default, and `MUST NOT` is forbidden.

---

## Primary Directive

Model the domain in a way that can actually be implemented and evolved.

When uncertain:
1. identify the bounded context
2. use the local ubiquitous language
3. define the aggregate consistency boundary conservatively
4. reference other aggregates by identity
5. keep infrastructure outside the model
6. integrate across contexts through explicit translation

Reject designs that sound like DDD but behave like generic CRUD plus renamed classes.

---

## Strategic Design Rules

### Bounded Context Is Mandatory
1. Every substantial domain area must belong to a named bounded context.
2. A model is valid only inside its bounded context.
3. Terms may change meaning across contexts; that is normal and must be respected.
4. Do not share model classes across contexts by default.

### Context Mapping Is a Design Artifact
1. Every context interaction must have an explicit relationship.
2. Translation responsibility must be visible.
3. Upstream/downstream influence matters.
4. External models, partner systems, and legacy systems must not define the local model.

### Core Domain Protection
1. Protect the core domain from generic abstractions and vendor terms.
2. Spend the richest modeling effort where competitive or operational complexity truly lives.
3. Keep supporting subdomains simpler.

Anti-patterns (MUST NOT):
- one global company model
- shared domain package crossing all contexts
- context boundaries existing only in diagrams but not in code
- context integration via direct imports of each other's domain classes

---

## Ubiquitous Language Rules

1. Use business terms exactly as they are understood in the current bounded context.
2. One concept gets one term inside the context.
3. One term must not carry multiple meanings inside the same context.
4. Rename code when understanding improves.
5. Tests, events, commands, repositories, and application services must all speak the same language.

Required behavior:
- use local domain terms in class, method, event, and package names
- remove technical placeholders when a real domain term exists

---

## Aggregate Rules of Thumb

### Aggregates Are Consistency Boundaries
1. Design aggregates around invariants that must hold immediately.
2. Keep aggregates as small as possible.
3. Small aggregates scale better in both understanding and throughput.
4. Large object graphs are not evidence of good modeling.

### Aggregate Root Discipline
1. Only the aggregate root may be referenced directly from outside.
2. All invariant-changing operations must go through the root.
3. Internal members must not be mutated directly by external code.
4. Expose intention-revealing behavior, not arbitrary setters.

### Reference Other Aggregates by Identity
1. Prefer IDs over direct object references across aggregate boundaries.
2. Avoid loading large connected graphs by default.
3. Cross-aggregate coordination should usually be eventual, not transactional.

### One Aggregate per Transaction by Default
1. Modify one aggregate in one transaction unless there is a compelling reason not to.
2. Do not stretch transactions across many aggregates out of convenience.
3. Use events, policies, or process coordination when consistency can be eventual.

Anti-patterns (MUST NOT):
- aggregates sized to fit ORM navigation
- transactions updating many aggregates by default
- aggregate roots exposing mutable child collections
- direct cross-aggregate navigation baked into the model

---

## Entity and Value Object Rules

### Entities
1. Use entities where identity and lifecycle matter.
2. Entities must protect meaningful state transitions.
3. Entity methods must express domain behavior, not generic state changes.
4. Entities must not be passive ORM containers in behavior-rich domains.

### Value Objects
1. Use value objects aggressively where primitives hide meaning.
2. Value objects must be immutable by default.
3. Validation belongs in value object construction.
4. Equality is by value, not identity.

Required behavior:
- model local value concepts explicitly instead of passing raw primitives for meaningful identifiers, quantities, ranges, names, or descriptive whole values
- keep invariant enforcement near the concept itself

---

## Domain and Transformation Service Rules

1. Use a domain service for a domain-significant operation that requires multiple domain objects and fits no single entity or value object.
2. Name domain services in the ubiquitous language.
3. Use transformation services when domain information must be transformed without assigning behavior to the wrong object.
4. Keep technical transformation, serialization, transport, and persistence mapping outside the domain model.

Anti-patterns (MUST NOT):
- moving behavior into services to avoid modeling entities or value objects
- hiding technical mapping behind a domain-sounding service name

---

## Repository Rules

1. Repositories exist for aggregate roots.
2. Repository interfaces must be defined by the domain or application code that needs them.
3. Repositories reconstitute and persist aggregates.
4. Repository APIs should reflect aggregate access needs, not generic table CRUD.
5. Repositories must return domain objects or domain-oriented results, not ORM rows.

Anti-patterns (MUST NOT):
- giant generic repository abstractions
- repository per table without aggregate thinking
- business rules inside repository implementations
- repositories returning persistence-layer entities into the domain

---

## Domain Event Rules

1. Publish domain events for meaningful business facts.
2. Event names must be in the past tense.
3. Domain events are part of the model, not transport mechanics.
4. Use events to coordinate across aggregates or contexts when immediate consistency is not required.
5. Keep event payloads meaningful and local to the model.

### Event Sourcing
1. Use event sourcing only when storing the sequence of domain events is the right persistence model for the aggregate.
2. Keep event streams consistent with aggregate identity and versioning.
3. Rebuild state from events deterministically.
4. Version events and upcasters or translators when event meaning evolves.
5. Do not choose event sourcing just because domain events exist.

Anti-patterns (MUST NOT):
- using events for every property change
- event names that describe commands instead of facts
- domain events carrying framework request objects or persistence artifacts
- using events to compensate for missing aggregate design

---

## Application Service Rules

1. Application services coordinate use cases.
2. They load aggregates, invoke domain behavior, persist results, and publish resulting events.
3. Application services must not contain the domain model's core decision logic.
4. Application services must be thin enough that the model still matters.
5. Application services may own transaction boundaries and integration coordination.

Anti-patterns (MUST NOT):
- application services containing all branching business rules
- controllers duplicating application service orchestration
- repositories and application services both implementing the same invariants

---

## Module and Package Rules

1. Packages/modules must reflect bounded contexts first.
2. Within a context, organize around domain and use-case ownership, not only technical layers.
3. Avoid a giant `shared` or `common` package for domain concepts.
4. Keep the model visible in the structure.

Preferred structure examples:
- `identity/domain`
- `identity/application`
- `identity/infrastructure`
- `identity/interfaces`

---

## Context Integration Rules

### Anticorruption Layer
Use when integrating with legacy systems or foreign models.

Rules (MUST unless marked SHOULD or MUST NOT):
1. Translate foreign language into the local context's language.
2. Keep foreign schemas and statuses out of local domain objects.
3. Own the translation explicitly.

### Identity Across Contexts
1. Use explicit identifiers and integration messages.
2. Do not pass local aggregates directly across context boundaries.
3. Keep contract models separate from local models.

Anti-patterns (MUST NOT):
- importing another context's domain package
- shared enums across contexts with different semantics
- direct DB coupling between contexts

---

## Client Representation and Scope Discipline

1. Use DTOs, projections, use-case queries, rendition adapters, or mediators when client needs differ from aggregate shape.
2. Expose REST resources as application-facing representations rather than aggregate internals.
3. Tailor representations for different clients without changing the domain model for each client.
4. Compose multiple bounded contexts at the application or integration layer, not by merging their models.
5. Keep command behavior separate from query models when consistency, performance, or representation needs justify the split.
6. Keep scope identifiers explicit where context or ownership affects invariants or access.

---

## Practical Simplicity Rule

1. Not every subdomain needs full-blown DDD ceremony.
2. Use richer modeling where complexity is real.
3. Use simpler patterns in supporting areas.
4. However, once invariants and lifecycle complexity appear, model them honestly.

Anti-patterns (MUST NOT):
- using DDD vocabulary without changing design
- over-modeling trivial CRUD subdomains
- refusing to model real complexity because “simple services are enough”

---

## Code Generation Rules

When generating code, follow this order:
1. identify the bounded context
2. state the ubiquitous language term(s)
3. determine whether the concept is entity, value object, aggregate root, domain event, repository, or application service
4. define aggregate boundary conservatively
5. reference other aggregates by ID
6. place invariants on the aggregate root or local model
7. define repositories around aggregate access
8. define application services around use cases
9. define translation layers for context or infrastructure boundaries

Avoid by default:
- direct cross-context model reuse
- ORM-shaped aggregates
- all-powerful application services
- generic repositories
- one transaction touching many aggregates
- shared domain packages across contexts

---

## Review Rules

When reviewing or modifying code, actively look for:
- missing bounded context ownership
- context bleeding
- shared models across different contexts
- foreign vocabularies polluting the local context
- oversized aggregates
- aggregate roots not protecting invariants
- external code mutating aggregate internals
- cross-aggregate references by object instead of identity
- events that are really commands
- repository contracts shaped like table CRUD

---

## Testing Rules

1. Test aggregate invariants directly.
2. Test valid and invalid state transitions.
3. Test value object validation and behavior.
4. Test domain events as outcomes of domain behavior.
5. Test repositories as infrastructure separately from aggregate rules.
6. Test anticorruption and translation layers explicitly.
7. Test application services for orchestration, not for all domain decisions.

---

## Review Checklist

Before finalizing any change, verify:
- Is the bounded context explicit?
- Is the local ubiquitous language used consistently?
- Are aggregates small and centered on immediate invariants?
- Are cross-aggregate references by identity?
- Does one transaction usually modify one aggregate?
- Are repository interfaces aggregate-oriented?
- Are domain events facts rather than commands?
- Are application services orchestrating rather than owning the model?
- Are foreign models translated explicitly?
- Did we avoid shared-model shortcuts across contexts?

If any answer is no, revise before shipping.

---

## Final Instruction

When uncertain, choose the option that:
1. protects the bounded context
2. keeps aggregates small
3. keeps identities explicit
4. preserves local language
5. moves cross-boundary coordination toward events and translation rather than shared object graphs

Reject DDD theater and model the real operational domain.
