# OBEY Domain-Driven Design by Eric Evans

## Purpose

This repository follows **Domain-Driven Design**.
All code generation, modification, and review must optimize for:
- a precise model of the domain
- a shared ubiquitous language
- explicit bounded contexts
- rich domain behavior where complexity exists
- disciplined aggregate design
- protection of invariants
- clear separation between domain model and supporting infrastructure

This file is a binding engineering policy: `MUST` is binding, `SHOULD` is a strong default, and `MUST NOT` is forbidden.

---

## Primary Directive

When uncertain, prefer the option that makes the **domain model clearer**.

Do not optimize primarily for:
- fewer files
- generic reuse
- CRUD convenience
- object-relational mapping convenience
- delivery-layer convenience
- framework conventions
- short-term speed at the cost of model clarity

The model must serve the business meaning first.

---

## What DDD Means in This Repository

DDD here does **not** mean:
- adding layers for ceremony
- renaming service classes to sound sophisticated
- wrapping CRUD in verbose abstractions
- creating entities with only fields and setters
- turning every concept into an aggregate
- introducing every DDD pattern everywhere
- overengineering simple subdomains

DDD here **does** mean:
- building code around business concepts
- expressing rules in domain language
- making context boundaries explicit
- protecting invariants with the model
- modeling identity, value, lifecycle, and consistency deliberately
- translating explicitly across context boundaries
- simplifying aggressively outside the core domain

---

## Knowledge Crunching and Deep Models

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Treat the model as discovered, not invented from technical structure.
2. Before adding abstractions, identify what domain experts would call the concept.
3. When requirements are ambiguous, look for missing domain distinctions instead of forcing generic names.
4. Let awkward code, contradictory language, and repeated conditionals trigger deeper modeling.
5. Update names and boundaries when new domain insight appears.

### Required behavior (MUST)
- Ask what business rule, policy, lifecycle, or invariant the code is expressing.
- Prefer a deeper model that clarifies behavior over a shallow model that merely stores data.
- Capture newly discovered concepts in names, tests, APIs, and modules.
- Treat refactoring as part of model discovery, not just code cleanup.

### Anti-patterns (MUST NOT)
- Starting from database tables and calling the result the domain model
- Preserving vague names after discovering sharper domain language
- Hiding domain complexity behind `type`, `status`, or `metadata` fields
- Treating the first model as final

---

## Model-Driven Design

### Rules (MUST unless marked SHOULD or MUST NOT)
1. The implemented design must reflect the model used in discussion.
2. If the model cannot guide code, refine the model or the code until they align.
3. Domain objects must represent behavior and meaning, not just persistence state.
4. Keep modelers close to implementation. Do not separate analysis from coding so far that the model becomes theoretical.

### Required behavior (MUST)
- Make important model concepts visible in classes, functions, modules, tests, and interfaces.
- Prefer executable examples and tests over disconnected documentation.
- Keep diagrams and documents lightweight, current, and tied to code.
- Use explanatory models only to teach or reason; do not confuse them with the implementation model unless they are intended to drive code.

### Anti-patterns (MUST NOT)
- A design document that uses different names than the code
- Analysts producing models that developers cannot or do not implement
- Code that follows framework conventions while ignoring the domain model
- Diagrams that become authoritative after the code and domain understanding have changed

---

## Breakthrough and Deeper Insight

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Expect useful models to change after deeper insight.
2. Treat a breakthrough model as a candidate for deliberate refactoring, not as churn.
3. When a better model appears, compare its explanatory power against migration cost.
4. Preserve working behavior while moving toward the deeper model in safe steps.

### Required behavior (MUST)
- Look for concepts that simplify many special cases at once.
- Prefer changes that make future business rules easier to express.
- Use awkwardness, contradictions, and repeated failed attempts as signals that the model is shallow.
- Keep focus on the basics when the model becomes too elaborate.

### Anti-patterns (MUST NOT)
- Rejecting a better model only because the current one already works
- Big-bang rewrites when incremental migration is possible
- Elaborate abstractions that do not improve domain insight

---

## Making Implicit Concepts Explicit

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Listen for domain language that is not represented in code.
2. Scrutinize awkward APIs, repeated branches, and contradictory names.
3. Read domain references, policies, regulations, and prior art when available.
4. Try multiple model shapes before settling on one for complex concepts.

### Required behavior (MUST)
- Promote hidden constraints, policies, and processes into explicit domain concepts.
- Name the concept before choosing the implementation form.
- Prefer clear domain objects over anonymous helpers when behavior has business meaning.

### Anti-patterns (MUST NOT)
- Burying business rules in comments
- Treating contradictions as edge cases instead of modeling signals
- Keeping vague technical flags after discovering the real concept

---

## Ubiquitous Language

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Use the exact business terms used by domain experts inside a bounded context.
2. One concept must have one name inside a bounded context.
3. One name must not mean different concepts inside a bounded context.
4. Method names, test names, and modules must use the same vocabulary as the domain.
5. Rename code when the domain understanding improves.

### Required behavior (MUST)
- Prefer names from the active bounded context; in a shipping model, terms such as `Cargo`, `Itinerary`, `Handling Event`, and `Route Specification` should appear directly.
- Prefer operation names that express the domain action, such as changing a cargo destination, adding a handling event, checking allocation, or applying an overbooking policy.
- Avoid technical placeholders when a precise domain term exists.
- Avoid names imported from another bounded context without translation.

### Anti-patterns (MUST NOT)
- Using technical names where the business has precise names
- Using synonyms for the same concept in the same context
- Reusing the same term for different meanings because it is convenient
- Keeping bad names because they already exist in the database

---

## Communication Artifacts

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Documents and diagrams must support the ubiquitous language.
2. Written design material must be short enough to stay maintained.
3. Executable tests are preferred for rules that can be verified.
4. Diagrams should emphasize boundaries, relationships, invariants, and lifecycle over class inventory.

### Required behavior (MUST)
- Use examples and scenario tests as living documentation.
- Keep glossary-like explanations close to the bounded context they describe.
- Update documents when terminology or context boundaries change.

### Anti-patterns (MUST NOT)
- Long design documents that drift away from code
- Diagrams that show every class but hide the model's meaning
- Documentation that introduces vocabulary not used by code or tests

---

## Scenario Walkthroughs

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Validate the model by walking through real application scenarios.
2. Use scenarios to test whether entities, value objects, aggregates, repositories, and factories collaborate naturally.
3. When a scenario feels procedural or awkward, look for missing model concepts or wrong boundaries.
4. Revisit aggregate and module boundaries after scenario walkthroughs reveal pressure.

### Required behavior (MUST)
- Prefer examples that exercise real business decisions, not only CRUD paths.
- Use scenarios to verify object creation, lifecycle transitions, and cross-context translation.
- Let performance tuning follow model clarity; do not distort the model prematurely for optimization.

### Anti-patterns (MUST NOT)
- Designing model elements only in isolation
- Treating scenario code as an afterthought after infrastructure is complete
- Optimizing persistence paths before the model expresses the business correctly

---

## Layered Architecture and Smart UI

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Keep the domain layer as the place where the model and business rules live.
2. Separate presentation, application coordination, domain behavior, and infrastructure when the domain is complex enough to need model-driven design.
3. Let application code coordinate tasks without owning domain decisions.
4. Keep infrastructure services and framework concerns outside domain objects.
5. Use Smart UI only for simple applications where rich domain abstraction, reuse, integration, and deep business rules are not important.

### Anti-patterns (MUST NOT)
- UI screens, database tables, or framework annotations defining the domain vocabulary
- UI, application coordination, jobs, or scripts carrying domain rules while domain objects stay passive
- choosing Smart UI when the business behavior needs reuse or abstraction

---

## Bounded Contexts

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Every substantial domain area must belong to a clearly identified bounded context.
2. A model is valid only inside its own bounded context.
3. Concepts from another context must not be imported directly as if they were native.
4. Translation across contexts must be explicit.
5. Shared models across multiple contexts are forbidden unless intentionally governed as a shared kernel.

### Required behavior (MUST)
- Keep package, module, or namespace ownership explicit.
- Model `Customer` separately in different contexts if meanings differ.
- Prefer context-specific contracts, IDs, published language, or anticorruption layers over shared classes.

### Anti-patterns (MUST NOT)
- One giant company-wide domain model
- A `shared/domain` package that erases boundaries
- Copying foreign terms into the local model without translation
- Reusing one aggregate type across unrelated contexts

---

## Strategic Design

### Core Domain
1. Invest the most care in the core domain.
2. Protect the core domain from foreign models, vendor schemas, and generic abstractions.
3. Keep the core domain expressive even if supporting areas are simpler.

### Supporting and Generic Subdomains
1. Do not over-model commodity concerns.
2. Use simpler models where business complexity is low.
3. Save the richest modeling effort for the parts that matter strategically.

### Context Mapping
1. Integration relationships must be visible in code.
2. Ownership of translation must be explicit.
3. Upstream and downstream influence must be reflected in adapters and contracts.

### Anti-patterns (MUST NOT)
- Spending more design effort on plumbing than on the core domain
- Modeling authentication utilities more richly than the pricing engine
- Allowing a legacy system vocabulary to dominate the core model

---

## Model Integrity Patterns

### Continuous Integration Within a Context
1. A bounded context must keep one internally consistent model.
2. Team members working in the same context must integrate terminology and model changes continuously.
3. Conflicting meanings inside one context must be resolved quickly through naming, tests, and refactoring.

### Context Relationships
Use context relationship patterns intentionally:
- `Shared Kernel` only for a small, jointly governed model subset.
- `Customer/Supplier` when an upstream team commits to downstream needs.
- `Conformist` only when adopting the upstream model is cheaper than translating it.
- `Anticorruption Layer` when protecting the local model from a foreign or legacy model.
- `Separate Ways` when integration cost is higher than shared capability value.
- `Open Host Service` when a context exposes a stable integration protocol.
- `Published Language` when contexts need a documented exchange language.

### Context Transformations
1. Move from Separate Ways to Shared Kernel only when the overlap is small, valuable, and worth coordination.
2. Move from Shared Kernel to Continuous Integration only when teams are ready to share one model frequently.
3. Phase out legacy systems by protecting the new model and replacing responsibilities incrementally through translations.
4. Evolve Open Host Service toward Published Language when interchange stability is needed beyond one service.

### Required behavior (MUST)
- Make context maps visible in package structure, integration adapters, documentation, or tests.
- Name adapters after the relationship they implement when that improves clarity.
- Keep foreign model terms out of the local core unless deliberately accepted as conformist.

### Anti-patterns (MUST NOT)
- Accidental shared kernels with no ownership rules
- Calling every integration an anticorruption layer without translation
- Letting upstream APIs silently define downstream domain language
- Treating context mapping as architecture documentation only, not code structure

---

## Distillation

### Core Domain
1. Identify the part of the model that creates strategic advantage.
2. Put the strongest modeling effort and cleanest design into that core.
3. Do not bury the core under generic mechanisms, infrastructure, or broad shared abstractions.

### Distillation Patterns
Use these patterns when they clarify priority and investment:
- `Domain Vision Statement` for a short statement of the core model's purpose.
- `Highlighted Core` to mark the most important elements inside a larger model.
- `Generic Subdomain` for commodity capabilities that do not deserve rich custom modeling.
- `Cohesive Mechanism` for technical mechanisms that can be separated from domain policy.
- `Segregated Core` when the core is tangled with supporting concerns.
- `Abstract Core` when related specialized models need a stable conceptual foundation.

### Required behavior (MUST)
- Make the core domain easy to find in code.
- Keep supporting and generic subdomains simpler unless their complexity is real.
- Choose refactoring targets based on strategic importance, not just local messiness.

### Anti-patterns (MUST NOT)
- Spending equal modeling effort on every subsystem
- Letting technical mechanisms dominate the core model
- Hiding the core behind generic shared packages
- Refactoring peripheral code while the core remains unclear

---

## Large-Scale Structure

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Large-scale structure should help people understand the system, not freeze it.
2. Let structure evolve as the model evolves.
3. Use a guiding structure only when it reduces cognitive load across contexts.
4. Keep the structure minimally restrictive.

### Patterns
Use these patterns deliberately:
- `Evolving Order` when structure must emerge through iterative modeling.
- `System Metaphor` only when it genuinely clarifies the model.
- `Responsibility Layers` when responsibilities naturally stratify across the system.
- `Knowledge Level` when rules or policies must be represented explicitly and changed by configuration or data.
- `Pluggable Component Framework` when variation points are stable and worth formalizing.

### Required behavior (MUST)
- Combine bounded contexts, distillation, and large-scale structure into one coherent strategy.
- Revisit structure when it no longer fits the model.
- Prefer communication and self-discipline over heavy structural machinery where possible.

### Anti-patterns (MUST NOT)
- A master plan that blocks model learning
- A metaphor that sounds clever but misleads design decisions
- Overly restrictive layers that fight the domain
- Framework architecture masquerading as domain structure

---

## Strategic Decision Making

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Assess the current model and context map before prescribing a strategic structure.
2. Decide who owns strategic design choices explicitly.
3. Let application development inform strategy; do not impose strategy detached from implementation feedback.
4. Architecture teams must stay customer-focused and model-focused, not framework-focused.
5. Strategic decisions must remain revisable as domain understanding changes.

### Required behavior (MUST)
- Combine bounded contexts with distillation and large-scale structure when system complexity requires it.
- Make strategy visible enough that teams can coordinate without a rigid master plan.
- Keep technical frameworks subordinate to the domain strategy.
- Treat strategic design as team decision-making, not just diagram production.

### Anti-patterns (MUST NOT)
- A top-down master plan that ignores model learning
- Strategy owned by people disconnected from implementation
- Technical architecture decisions presented as domain strategy
- Context maps, core-domain decisions, and large-scale structures that are never revisited

---

## Entities

### Use entities when
- identity matters over time
- lifecycle matters
- continuity matters beyond current attributes
- business rules depend on “which one” rather than only “what value”

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Entities must have explicit identity.
2. Entities must protect their own valid state transitions.
3. Entities must expose intention-revealing behavior, not arbitrary state changes.
4. Entities must not be treated as passive records in behavior-rich domains.

### Required behavior (MUST)
- Prefer methods that tell an entity what domain action to perform.
- In a shipping model, express destination changes and handling-event additions as model operations rather than procedural data edits.
- Hide direct state changes behind methods that encode domain meaning.
- Keep identity stable and explicit.

### Anti-patterns (MUST NOT)
- Public setters for every field
- Application services manually editing all entity state
- UI or application code deciding which transitions are valid
- Entities used only as persistence shells

---

## Value Objects

### Use value objects when
- a concept is defined by attributes rather than identity
- the concept has validation rules
- the concept has behavior
- passing a primitive would hide meaning

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Value objects must be immutable by default.
2. Construction must guarantee validity.
3. Equality must be by value, not by identity.
4. Validation for the concept should live inside the value object.
5. Replace primitive obsession aggressively where the concept matters.

### Required behavior (MUST)
- Use value objects for descriptive concepts whose attributes together carry domain meaning.
- Name value objects after the domain concept, not the primitive representation.
- Keep validation and side-effect-free operations for the value near the value itself.
- Replace raw primitives when a named quantity, range, code, measurement, or descriptive whole value matters to the model.

### Anti-patterns (MUST NOT)
- Repeating the same value validation across handlers
- Passing raw primitives for named domain quantities, ranges, codes, or measurements
- Passing raw strings for meaningful identifiers
- Letting invalid values exist temporarily without an explicit model for incompleteness

---

## Associations and Modules

### Associations
1. Model associations only when they support behavior or meaning.
2. Prefer simpler, more navigable associations over fully connected object graphs.
3. Reduce bidirectional associations unless the domain requires them.
4. Reference other aggregates by identity unless direct object traversal is part of an invariant boundary.

### Modules
1. Modules must communicate domain concepts and bounded context ownership.
2. Organize modules around model meaning, not only technical layers.
3. Keep related concepts together when they change together.
4. Avoid infrastructure-driven packaging that hides the domain.

### Required behavior (MUST)
- Use package names that match the ubiquitous language.
- Keep model concepts discoverable from the directory structure.
- Split modules when different concepts evolve independently.

### Anti-patterns (MUST NOT)
- `models`, `services`, `utils`, and `helpers` as the dominant structure
- Associations created only because the persistence mechanism supports them
- Object graphs that make aggregate boundaries invisible
- Modules grouped by technical artifact while domain concepts are scattered

---

## Aggregates

### Purpose
Aggregates are **consistency boundaries**, not just object graphs.

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Design aggregates around invariants that must be consistent immediately.
2. Keep aggregates as small as possible.
3. All modifications that affect aggregate invariants must go through the aggregate root.
4. Reference other aggregates by identity unless stronger consistency is truly required.
5. Keep transactional boundaries aligned with invariants; do not expand transactions across aggregates merely for convenience.

### Required behavior (MUST)
- Put invariant-protecting methods on the aggregate root.
- Keep internal members encapsulated.
- Handle consistency across aggregate boundaries deliberately when the invariant does not belong inside one aggregate.
- Model transactional boundaries deliberately.

### Anti-patterns (MUST NOT)
- Large graph aggregates built for object-relational mapping convenience
- Aggregate roots exposing internal collections for arbitrary external state changes
- Transactions modifying many aggregates because object references make it easy
- Confusing parent-child object structure with aggregate boundaries

---

## Domain Services

### Use a domain service only when
- the behavior is domain-significant
- the behavior does not naturally belong on one entity or value object
- the operation still belongs to the ubiquitous language

### Rules (MUST unless marked SHOULD or MUST NOT)
1. A domain service must express a domain concept, not a technical convenience.
2. If behavior clearly belongs to an entity or value object, keep it there.
3. Do not move behavior into services merely to keep entities thin.

### Required behavior (MUST)
- Domain services should sound like the business.
- Domain services should coordinate domain concepts, not infrastructure details.

### Anti-patterns (MUST NOT)
- a single `*Service` containing all rules for a model area
- a service containing dozens of unrelated policies
- “Domain services” that are only wrappers for repositories or external technical clients
- Extracting behavior from entities prematurely

---

## Explicit Concepts and Specifications

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Make implicit constraints explicit in the model.
2. Model domain processes as domain objects when the process has business meaning.
3. Use specifications for named, combinable business rules that answer whether something satisfies a criterion.
4. Keep specifications in domain language, not query language.

### Required behavior (MUST)
- Extract repeated conditionals into named domain concepts.
- Prefer named concepts such as route specifications, overbooking policies, or allocation rules over anonymous boolean expressions.
- Keep persistence querying concerns separate from domain specifications unless the project deliberately provides translation.
- Use specifications to clarify policy, validation, selection, and compatibility rules.

### Anti-patterns (MUST NOT)
- Complex business conditions duplicated across services
- Boolean flags that hide a named domain rule
- Specifications that are just persistence query builders
- Processes represented only as scripts or transaction handlers when the business treats them as concepts

---

## Repositories

### Purpose
Repositories provide access to aggregates as part of the model.

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Repositories exist for aggregate roots, not for every table.
2. Repository interfaces must be defined by the domain or application model that uses them.
3. Repositories must return domain objects or domain-oriented results.
4. Repository contracts must reflect intent where useful.
5. Repositories must not become universal query utilities.

### Required behavior (MUST)
- Use repositories to reconstitute and persist aggregates.
- Keep infrastructure mapping hidden behind the repository implementation.
- Prefer focused repository methods over giant generic CRUD interfaces when domain intent matters.
- Keep reconstitution paths separate from normal creation paths when that protects invariants.
- Make client code independent of repository implementation details, while repository implementers understand those details.
- Express query criteria as specifications or model concepts when the criteria are domain rules.
- Return domain objects or collections without exposing database structure.

### Anti-patterns (MUST NOT)
- Generic repository abstractions that erase domain meaning
- Returning persistence records directly into the domain
- Putting business rules into repository implementations
- Creating one repository per table with no relation to aggregate design
- Letting relational database design dictate object identity, associations, or aggregate boundaries

---

## Factories

### Use factories when
- creation is complex
- construction has business rules
- valid creation requires multiple collaborating values
- the creation itself has domain meaning

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Factories must create valid objects.
2. Factories must encode domain creation rules, not technical object assembly.
3. Clients and mappers must not contain business construction logic.
4. Choose the factory site where creation ownership fits the model.
5. Use constructors directly when creation is simple, intention-revealing, and does not expose complex invariants.
6. Treat reconstitution from storage separately from new-object creation.

### Anti-patterns (MUST NOT)
- Building invalid objects first and fixing them later
- Letting endpoints stitch together aggregates directly
- Using a factory only to hide a trivial constructor

## Application Layer

### Purpose
The application layer coordinates application tasks.
It does not replace the domain model.

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Application services load aggregates, call domain behavior, persist results, and coordinate side effects.
2. Application services must not hold core business invariants that belong in the domain.
3. Application services must speak the ubiquitous language.
4. Application services may coordinate transactions and integration publication, but should not become procedural god classes.

### Required behavior (MUST)
- Keep each application operation focused on one application action.
- Let domain objects make domain decisions.
- Keep orchestration distinct from business rules.

### Anti-patterns (MUST NOT)
- Application services containing all branching business logic
- Application services manipulating entity internals directly
- Repositories, UI handlers, and application services all implementing overlapping rules

---

## Infrastructure

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Infrastructure is subordinate to the model.
2. Object-relational mappings, serializers, external technical clients, delivery mechanisms, messaging details, caches, and framework types must stay out of the domain model.
3. Infrastructure must adapt to the model, not the reverse.
4. Persistence shape must not define the domain shape.

### Anti-patterns (MUST NOT)
- Naming domain concepts after database tables
- Designing aggregates around lazy loading
- Adding methods to entities only because the persistence mechanism needs them
- Letting transport representations become domain objects

---

## Translation at Boundaries

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Translation is mandatory at context boundaries.
2. Translation is usually mandatory between domain objects and transport or persistence representations.
3. Anti-corruption layers must preserve the local model rather than mirror foreign models.
4. Foreign terms must not silently invade the local ubiquitous language.

### Required behavior (MUST)
- Translate external IDs, statuses, and vocabularies explicitly.
- Map transport representations to local commands or domain inputs.
- Keep persistence models and integration models outside the core domain.

### Anti-patterns (MUST NOT)
- Passing external API models deep into the domain
- Reusing one representation as delivery input, persistence record, domain object, and integration message
- Adopting vendor status codes as native domain terminology

---

## Supple Design

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Design interfaces that reveal intention in domain language.
2. Prefer side-effect-free functions for calculations and queries.
3. Make assertions and invariants explicit in the model.
4. Shape objects around conceptual contours, not arbitrary technical convenience.
5. Use standalone classes where a concept can be understood without unnecessary dependencies.
6. Favor operations that are closed under meaningful domain types when that improves clarity.
7. Use declarative design when it makes rules easier to read, combine, and verify.
8. Combine specifications with AND, OR, or NOT only while each component meaning remains readable.
9. Use subsumption when one specification or category includes another and that relationship matters.

### Required behavior (MUST)
- Name methods after what the business is trying to accomplish.
- Separate commands from queries where side effects would surprise readers.
- Put invariant checks where invalid states enter the model.
- Look for cohesive concepts hidden inside long methods, conditionals, or parameter groups.
- Consider a domain-specific language only when it simplifies real domain expression.

### Anti-patterns (MUST NOT)
- Technically named APIs that hide intent
- Methods that both ask a question and mutate domain state
- Invariants expressed only in comments or UI/application validation
- Declarative frameworks that obscure rather than clarify business rules

---

## Analysis and Model Patterns

### Analysis Patterns
1. Use prior domain modeling knowledge when it fits the current domain.
2. Do not force an analysis pattern when local language contradicts it.
3. Adapt patterns to the bounded context rather than importing them wholesale.
4. Search domain literature, prior art, and established formalisms when the team lacks concepts for a good model.
5. Use exploration teams for hard modeling problems only when their findings are tested in code and returned to the main team.

### Design Patterns in the Model
Use design patterns only when they express the domain model:
- `Strategy` or `Policy` for interchangeable domain policies.
- `Composite` for part-whole structures that domain experts recognize.
- Avoid patterns that optimize implementation while hiding model meaning.

### Required behavior (MUST)
- Reach for established formalisms when the domain already has mature concepts.
- Make pattern names subordinate to domain names.
- Prefer domain-specific names over generic pattern names in public APIs.

### Anti-patterns (MUST NOT)
- Applying design patterns because they are familiar rather than because the model needs them
- Naming domain objects after patterns instead of business concepts
- Importing a reference model without validating it against local domain language

---

## Code Generation Rules

When generating code, always do the following in order.

### 1. Identify the domain concept first
Before writing code, identify:
- the bounded context
- the domain term
- whether the concept is an entity, value object, aggregate, domain service, repository, factory, or specification
- which invariants matter

Do not start from:
- delivery code
- the persistence model
- the database schema
- the REST shape
unless the task is purely infrastructural.

### 2. Prefer modeling over generic plumbing
If the domain contains real rules:
- put behavior in the model
- introduce value objects
- define aggregate boundaries
- use domain language in APIs

Do not default to procedural services operating on passive records.

### 3. Use primitives only when they truly carry no domain meaning
Wrap primitives when meaning, validation, unit semantics, or invariants matter.

### 4. Protect invariants at the model boundary
Do not rely on UI validation, application validation, or repository validation as the primary protection for business rules.

### 5. Keep the model persistence-ignorant
Do not shape types or boundaries primarily for object-relational mapping convenience.

### 6. Keep bounded contexts visible in structure
Prefer feature or context ownership in modules and packages.
Avoid architecture that hides business boundaries behind generic folders.

### 7. Translate foreign models explicitly
Whenever another context, system, transport layer, or persistence format is involved, create translation rather than leakage.

### 8. Look for implicit concepts
When conditionals, flags, validation blocks, or repeated calculations express business meaning, extract named concepts such as value objects, policies, specifications, or domain services.

### 9. Preserve strategic priorities
Give the core domain more modeling care than supporting or generic subdomains. Keep context relationships and distillation choices visible when they affect code.

---

## Review Rules

When reviewing or modifying code, actively look for:

### Language problems
- vague technical names replacing business terms
- synonyms for one concept
- one term used with multiple meanings

### Model problems
- passive entities
- missing value objects
- invalid construction
- missing invariants
- domain logic spread across delivery handlers, application coordination, or repositories

### Boundary problems
- bounded context bleeding
- foreign models leaking inward
- shared “common domain” abstractions destroying language clarity
- missing context relationship strategy
- implicit shared kernels with no governance

### Aggregate problems
- oversized aggregates
- aggregate roots exposing internal state changes
- direct object references across aggregates where identity should be used
- transactions spanning many aggregates by default

### Service problems
- domain services that are really technical helpers
- god services
- application services replacing the whole domain model

### Infrastructure problems
- persistence-first modeling
- transport shapes defining the domain
- persistence rules embedded in business logic

### Strategic problems
- core domain hidden behind generic infrastructure
- supporting subdomains over-modeled while core logic remains weak
- no visible distillation or large-scale structure where the system complexity requires one
- context map decisions undocumented in code or tests

---

## Testing Rules

### Domain tests first
Prioritize tests for:
- entity invariants
- value object validity
- aggregate behavior
- domain services
- specifications and explicit constraints
- application-layer orchestration
- context translation and anticorruption layers

### Rules (MUST unless marked SHOULD or MUST NOT)
1. Tests must read in the ubiquitous language.
2. Tests must verify allowed and forbidden state transitions.
3. Tests must verify that invalid objects cannot be created through supported paths.
4. Tests must verify translation behavior where anticorruption layers exist.
5. Infrastructure tests must stay separate from domain tests.
6. Tests for the core domain should read like executable examples of the model.
7. Test context boundaries so translations preserve intended meaning.
8. Test that one context does not silently break another context's assumptions.

### Anti-patterns (MUST NOT)
- Tests named in transport or delivery vocabulary instead of domain vocabulary
- Tests that verify persistence details instead of domain meaning
- Missing tests for invalid transitions and invariant protection
- Tests that validate generic plumbing while leaving core policy untested

---

## Forbidden Patterns

Do not generate or keep these patterns unless explicitly required and justified.

### Passive Domain Model
- entities with fields and setters but no real behavior in a complex domain
- all rules living in application services or UI handlers

### Smart UI
- UI or application code making domain decisions
- request handlers enforcing core invariants

### Persistence-Driven Design
- aggregate boundaries chosen for persistence convenience
- entities shaped around table structures
- domain types depending on persistence mechanics

### Primitive Obsession
- raw strings, ints, decimals, and datetimes everywhere for meaningful concepts
- repeated validation logic for the same primitive concept

### Shared Model Everything
- one giant shared domain model across contexts
- common abstractions that erase business distinctions

### God Services
- single `*Service` classes containing many unrelated policies and workflows
- procedural orchestration replacing domain behavior

### Invalid Construction
- partially initialized aggregates
- public state changes that bypass invariants
- allowing impossible states because later code will fix them

### Fake DDD
- renaming CRUD layers without changing the model
- adding repositories, factories, and services without real domain need
- over-modeling simple supporting subdomains

### Context Map Blindness
- integrations with no explicit relationship strategy
- foreign models imported directly into the local core
- shared code treated as neutral when it actually carries another context's language

### Pattern-Driven Obscurity
- design patterns that make the domain language harder to see
- frameworks or DSLs that make simple rules harder to verify
- large-scale structures that prevent model evolution

---

## Refactoring Rules

When changing existing code:

1. Recover the ubiquitous language.
2. Move business rules into entities, value objects, aggregates, or domain services where appropriate.
3. Introduce value objects where primitives hide meaning.
4. Redraw aggregate boundaries where invariants are unclear or transactional scope is too large.
5. Separate bounded contexts that are currently bleeding together.
6. Add translation layers where foreign models leak into the domain.
7. Break up god services into focused application services plus richer domain behavior.
8. Remove persistence and transport assumptions from the model.
9. Extract explicit constraints, specifications, and policies from repeated conditionals.
10. Clarify context relationships when integration code is ambiguous.
11. Distill the core domain out of supporting mechanisms when strategic logic is buried.
12. Preserve behavior while improving the model incrementally.

Do not rewrite everything at once unless explicitly required.

---

## Output Expectations

When asked to implement a feature, default to producing:
- bounded context ownership
- domain terms first
- entities or value objects where justified
- aggregates when invariants require a consistency boundary
- specifications or policies when named rules must be evaluated or combined
- repositories for aggregate persistence
- factories when creation is non-trivial
- application services for orchestration
- explicit translation at external boundaries
- visible context relationship choices when integrating with other models
- simpler supporting or generic subdomain designs when rich modeling is not justified

When asked to review code:
- identify model-language mismatch
- identify missing value objects
- identify passive data-structure model symptoms
- identify bad aggregate boundaries
- identify context leakage
- identify infrastructure-driven modeling
- identify missing explicit constraints or specifications
- identify weak core-domain distillation
- identify context map and large-scale structure problems
- propose concrete DDD refactorings

When asked to modify code:
- improve the model first where safe
- do not deepen technical shortcuts that weaken the domain language
- keep business meaning more explicit after the change than before it
- preserve the model's strategic priorities

---

## Review Checklist

Before finalizing any change, verify:

- Is the bounded context clear?
- Does the code use the ubiquitous language consistently?
- Are important concepts modeled explicitly?
- Are value objects used where primitives hide meaning?
- Are entities protecting valid transitions?
- Are aggregate boundaries clear and small enough?
- Are cross-aggregate references by identity unless stronger consistency is required?
- Are repositories aligned to aggregates rather than tables?
- Are specifications, policies, or explicit constraints used where repeated rules need names?
- Are application services orchestrating rather than owning all rules?
- Is the domain model protected from transport, persistence, and vendor models?
- Are context boundaries translated explicitly?
- Is the context map relationship clear for integrations?
- Is the core domain visible and protected from generic mechanisms?
- Are large-scale structures helping rather than freezing the model?
- Did we avoid god services?
- Did we avoid passive domain objects where the domain is complex?
- Did we avoid over-modeling where the domain is simple?

If any answer is no, revise before shipping.

---

## Final Instruction

When uncertain, choose the option that:
1. makes the domain language sharper
2. protects invariants inside the model
3. keeps bounded contexts explicit
4. reduces primitive obsession
5. keeps infrastructure subordinate to domain meaning

Reject changes that make the code more generic but the domain less clear.
