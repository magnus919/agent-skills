# OBEY Patterns of Enterprise Application Architecture by Martin Fowler

## Purpose

This repository follows the practical style of **Patterns of Enterprise Application Architecture**:
structure enterprise software around clear responsibilities for domain logic, persistence, transaction boundaries, integration, and presentation.

All code generation, edits, and reviews must optimize for:
- explicit separation of concerns
- predictable business logic placement
- appropriate enterprise patterns instead of accidental coupling
- manageable persistence and transaction boundaries
- clear mapping between in-memory objects and external systems
- code that is maintainable under real enterprise constraints

This file is a binding engineering policy: `MUST` is binding, `SHOULD` is a strong default, and `MUST NOT` is forbidden.

---

## Primary Directive

Enterprise software is not improved by inventing architecture from scratch for every feature.
Prefer a small number of well-understood structural patterns, applied deliberately.

When uncertain, choose the design that makes these responsibilities explicit:
- presentation and transport
- application workflow
- domain logic
- data source interaction
- transaction management
- concurrency control
- integration boundaries

Do not let one class or layer own all of them.

---

## Architectural Baseline

### Layering
Use layering as a default organizing principle:
1. presentation and delivery
2. application coordination
3. domain logic
4. data source and integration access

Rules (MUST unless marked SHOULD or MUST NOT):
- upper layers may depend on lower ones
- lower layers must not reach into presentation concerns
- each layer must earn its existence by reducing coupling or clarifying responsibility

Anti-patterns (MUST NOT):
- controllers reaching directly into SQL and transaction details
- domain logic embedded in views or handlers
- repositories returning HTTP-shaped DTOs
- fake layers that only pass calls through

---

## Choosing the Business Logic Pattern

### Transaction Script
Use when:
- logic is simple
- each request or use case is mostly independent
- rich domain modeling is unnecessary

Rules (MUST unless marked SHOULD or MUST NOT):
- scripts must remain short and use-case focused
- do not let transaction scripts become dumping grounds for all business logic
- if duplication, lifecycle, or invariant complexity grows, escalate to a stronger pattern

### Table Module
Use when:
- logic is naturally organized around tabular data sets
- calculations are set-oriented
- object identity is not the key organizing force

Rules (MUST unless marked SHOULD or MUST NOT):
- keep behavior centered on the table abstraction
- do not fake entities if the real model is fundamentally tabular
- isolate tabular logic from presentation and transport

### Domain Model
Use when:
- domain complexity is significant
- business rules, invariants, and lifecycles matter
- identity, collaboration, and behavior belong in the model

Rules (MUST unless marked SHOULD or MUST NOT):
- rich domain logic belongs in model objects
- keep application coordination separate from domain decisions
- avoid anemic models in behavior-rich domains

---

## Application Workflow Rules

### Service Layer
Use a service layer to define application operations.

Rules (MUST unless marked SHOULD or MUST NOT):
1. Application services coordinate use cases.
2. They define transaction boundaries and orchestration.
3. They must not absorb all domain logic by default.
4. They should expose an application-oriented API, not UI mechanics.

### Remote Facade
Use when:
- the boundary is remote
- coarse-grained APIs reduce chatty calls
- transport shape differs from internal design

Rules (MUST unless marked SHOULD or MUST NOT):
- expose coarse remote operations
- translate between remote contracts and internal model
- keep remote transport concerns at the boundary

### Data Transfer Object
Use when:
- data crosses process or layer boundaries
- batching values reduces remote or serialization cost
- translation protects the internal model

Rules (MUST unless marked SHOULD or MUST NOT):
- DTOs are transport structures, not domain models
- keep mapping explicit
- do not move business behavior into DTOs

---

## Persistence Pattern Rules

### Repository
Use repositories to present a collection-like interface over domain object access.

Rules (MUST unless marked SHOULD or MUST NOT):
1. Repositories must speak in domain terms.
2. Repository interfaces should reflect domain access needs rather than table shape.
3. Repository implementations hide query, mapping, and storage details.
4. Repositories must not become generic “everything” gateways.

### Data Mapper
Use when:
- the domain model should remain decoupled from the database structure
- object-relational mismatch is real
- persistence logic deserves isolation

Rules (MUST unless marked SHOULD or MUST NOT):
- mapping code belongs outside the domain objects
- do not force domain objects to know SQL, record formats, or mapping mechanics
- keep mapping explicit and testable

### Row Data Gateway
Use when behavior is simple and record-oriented.

### Table Data Gateway
Use when operations are naturally table-oriented and one table interface can clearly centralize access.

### Active Record
Use only when domain logic is simple and persistence coupling is acceptable.
Do not default to Active Record for complex domains.

---

## Identity, Caching, and Unit-of-Work Rules

### Identity Map
- preserve one in-memory representation per identity per scope where needed
- avoid duplicate object instances fighting each other inside one logical unit of work

### Unit of Work
- make transactional write coordination explicit
- commit work as one logical unit
- keep unit-of-work scope understandable

### Lazy Load
- use deliberately, not everywhere
- know where lazy loading may trigger remote/database chatter
- avoid lazy loading surprises in loops and serialization paths

Anti-patterns (MUST NOT):
- invisible N+1 behavior everywhere
- hidden auto-persistence with surprising write timing
- saving each object ad hoc from random callers

---

## Object-Relational Mapping Pattern Index

- USE Identity Field when in-memory objects need stable database identity; keep identity mapping explicit.
- USE Foreign Key Mapping when object references map to relational keys; avoid hiding expensive joins behind innocent traversal.
- USE Association Table Mapping when many-to-many relationships need a separate relational table.
- USE Dependent Mapping when child objects have no independent database identity outside their owner.
- USE Embedded Value when a small value object can live inside the owning row without independent lifecycle.
- USE Serialized LOB only when querying inside the value is not required and serialization versioning is controlled.
- USE Single Table Inheritance when one table with nullable columns is simpler than multiple joins.
- USE Class Table Inheritance when normalized subtype data is worth join complexity.
- USE Concrete Table Inheritance when each concrete type can own its table without excessive duplication.
- USE Inheritance Mappers to isolate inheritance persistence decisions from domain logic.
- USE Metadata Mapping when mapping rules are regular enough to centralize safely; avoid it when metadata obscures exceptional behavior.
- USE Query Object when query construction needs a composable object model instead of scattered SQL strings.

---

## Concurrency and Transaction Rules

### Optimistic Offline Lock
Use when conflicts are possible but uncommon.

Rules (MUST unless marked SHOULD or MUST NOT):
- detect conflicting concurrent updates
- fail safely and explicitly
- surface conflict resolution or merge semantics intentionally

### Pessimistic Locking
Use only when contention is expected and the cost is justified.

### Transaction Boundaries
1. Transaction boundaries must be explicit in application workflow.
2. Avoid transactions that span remote calls when possible.
3. Keep transactions short.
4. Do not bury transaction ownership deep in helper classes.

### Additional Offline Concurrency Patterns
- USE Coarse-Grained Lock when related objects must be locked together to preserve a user-level edit.
- USE Implicit Lock only when lock acquisition is reliably hidden without making concurrency invisible to maintainers.
- Do not let implicit locking make transaction ownership or contention impossible to diagnose.

---

## Presentation Layer Rules

1. Presentation code handles input, rendering, and transport concerns.
2. Business rules must not live in controllers or views.
3. Presentation models may differ from domain models.
4. Formatting, pagination, and UI interaction state belong outside domain logic.

Choose Page Controller vs Front Controller pragmatically, but keep routing concerns out of business logic.

### Presentation Pattern Index
- USE Model View Controller to separate domain model, view, and controller responsibilities.
- USE Page Controller when each page/action can be handled independently.
- USE Front Controller when centralized request handling, authentication, routing, or dispatch is valuable.
- USE Template View when server-side templates clearly express the response.
- USE Transform View when transforming data into output is clearer than embedding logic in templates.
- USE Two Step View when shared presentation structure should be separated from page-specific content.
- USE Application Controller when flow and navigation decisions need a dedicated coordinator.

---

## Offline and Integration Rules

1. External systems must be accessed through clear boundaries.
2. Translate partner formats into internal concepts.
3. Integration events/messages are not domain objects.
4. Do not allow integration convenience to dominate internal design.

Anti-patterns (MUST NOT):
- internal code shaped around partner API payloads
- direct vendor DTOs used across the application
- business logic embedded in serialization code

---

## Session State and Base Pattern Index

- USE Client Session State only when client storage is acceptable and integrity/security implications are handled.
- USE Server Session State when server-managed session data is needed and scaling/cleanup costs are explicit.
- USE Database Session State when session durability or server-farm sharing outweighs database load.
- USE Gateway to isolate access to an external resource or subsystem.
- USE Mapper to move data between objects or layers while keeping both sides independent.
- USE Layer Supertype only when shared layer behavior is real and stable.
- USE Separated Interface when clients should depend on an interface in a different package from implementation details.
- USE Registry sparingly for well-known objects; avoid turning it into global hidden dependency.
- USE Value Object for small values where equality by value and immutability simplify code.
- USE Money for currency amounts so rounding, currency, and arithmetic rules stay explicit.
- USE Special Case to replace repeated null or exceptional handling with a named object.
- USE Plugin when implementations must be selected or extended without changing core code.
- USE Service Stub to test or run without a real remote service.
- USE Record Set when tabular data is the natural interchange shape and object behavior is not needed.

---

## Distribution Rules

1. Do not distribute objects or services remotely by default.
2. Remote boundaries must be coarse-grained.
3. Separate local object design from remote contract design.
4. Budget explicitly for latency, serialization, versioning, and partial failure.

Anti-patterns (MUST NOT):
- chatty remote object interfaces
- assuming local method-call semantics over a network
- leaking domain internals through remote endpoints

---

## Code Generation Rules

When generating code, apply this order:
1. identify the business logic pattern that actually fits the complexity
2. place use-case coordination in an application/service layer
3. place domain decisions in the domain model when the domain is rich
4. place persistence behind repositories, mappers, or gateways
5. define transaction boundaries explicitly
6. define DTOs or remote facades only at boundaries
7. keep presentation and transport concerns at the edge

Default choices:
- simple CRUD -> transaction script or simple service layer
- rich invariants -> domain model + repository + mapper
- table-oriented calculations -> table module or table gateway
- remote boundary -> remote facade + DTO

Avoid by default:
- using domain model everywhere regardless of complexity
- generic repository for everything
- exposing persistence models directly to callers
- placing transactions, validation, rendering, and SQL in one class

---

## Review Rules

When reviewing code, actively look for:
- domain logic in controllers or views
- repositories returning transport shapes
- lower layers knowing presentation details
- trivial CRUD wrapped in excessive modeling
- complex rules trapped in transaction scripts
- SQL spread through business code
- missing transaction boundaries
- hidden unit-of-work behavior
- accidental N+1 loading
- chatty remote APIs
- no translation between internal and remote models

---

## Forbidden Patterns

### Layering Theater
- five layers that only forward method calls

### Generic Repository Everywhere
- one CRUD abstraction for all domain and data access
- repository APIs shaped by tables instead of use cases

### ORM-Driven Everything
- all design decisions dictated by ORM convenience
- aggregates, services, and DTOs collapsed into one persistence model

### Controller-Centric Enterprise App
- request handlers coordinating transactions, SQL, domain rules, and external calls

### Distributed Object Fantasy
- pretending network calls are normal method calls

### Unclear Transaction Ownership
- random save calls across layers
- no clear transaction owner
- long-running workflows treated as one immediate transaction

---

## Testing Rules

1. Test domain logic independently from presentation and persistence when possible.
2. Test repositories, mappers, and gateways separately as data-access infrastructure.
3. Test service/application workflows for transaction and orchestration behavior.
4. Test concurrency behaviors where optimistic or pessimistic locking matters.
5. Test DTO and remote facade mapping at the boundaries.

---

## Review Checklist

Before finalizing any change, verify:
- Did we choose the right business logic pattern for the actual complexity?
- Are presentation, workflow, domain logic, and persistence responsibilities distinct?
- Is transaction ownership explicit?
- Are repositories or gateways shaped by use cases or aggregates rather than raw tables?
- Is mapping isolated from domain logic?
- Are remote boundaries coarse-grained and translated explicitly?
- Did we avoid generic repository overreach?
- Did we avoid controller-centric design?
- Did we avoid layering theater?
- Did we keep concurrency and loading assumptions visible?

If any answer is no, revise before shipping.

---

## Final Instruction

When uncertain, choose the smallest set of enterprise patterns that makes:
1. business logic placement obvious
2. persistence and mapping explicit
3. transaction boundaries clear
4. remote boundaries coarse and safe
5. the application easier to evolve under real enterprise constraints

Reject fashionable complexity and accidental coupling alike.
