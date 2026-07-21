# OBEY Domain-Driven Design Distilled by Vaughn Vernon

## Purpose

This repository follows **Domain-Driven Design Distilled**:
use the smallest effective set of DDD practices to model the business meaning clearly and deliver results quickly.

All code generation, edits, and reviews must optimize for:
- clear business language
- explicit bounded contexts
- focus on core domain complexity
- selective use of tactical DDD patterns
- practical implementation over ceremony
- collaboration between model and software design

This file is a binding engineering policy: `MUST` is binding, `SHOULD` is a strong default, and `MUST NOT` is forbidden.

---

## Primary Directive

Use DDD where it clarifies complex business software.
Do not turn DDD into ritual.

When uncertain:
1. identify the business capability or subdomain
2. decide whether it is core, supporting, or generic
3. define the bounded context
4. use the local ubiquitous language
5. apply only the tactical patterns that actually earn their cost

Reject both extremes:
- no modeling when the domain is complex
- full-blown DDD ceremony when the problem is simple

---

## Adoption Fit and Modeling Investment

1. Use DDD when domain complexity, language ambiguity, business differentiation, or integration risk justify the modeling effort.
2. Do not apply full tactical DDD to simple CRUD, generic subdomains, or problems whose complexity is mainly technical.
3. Let business drivers decide where modeling effort goes.
4. Reassess the model when the core business concern drifts, terms stop matching code, or supporting complexity hides the core.
5. Use scenarios and acceptance tests to validate that the model expresses real business behavior.

---

## Strategic Rules

### Start with Subdomains
Classify major areas as:
- core domain
- supporting subdomain
- generic subdomain

Rules (MUST unless marked SHOULD or MUST NOT):
1. Invest the most design effort in the core domain.
2. Keep supporting and generic subdomains simpler unless complexity proves otherwise.
3. Do not waste the best modeling effort on commodity concerns.

### Define Bounded Contexts Early
1. Every meaningful model lives inside a bounded context.
2. A bounded context owns its language, rules, and model semantics.
3. The same term may mean different things in different contexts.
4. Code structure must reflect context boundaries.

### Use Context Mapping
1. Make context relationships explicit.
2. Translate where meanings differ.
3. Own integration contracts deliberately.
4. Protect the local model from foreign language.

Anti-patterns (MUST NOT):
- one model reused across billing, identity, catalog, fulfillment, and support
- shared domain classes with subtly different meanings
- context boundaries documented but ignored in code

---

## Context Relationship Rules

Choose context relationships deliberately:

- USE Partnership only when teams can coordinate closely and share planning burden.
- USE Shared Kernel only for a small stable overlap with joint ownership and tests.
- USE Customer/Supplier when the upstream team can plan for downstream needs.
- USE Conformist when adopting the upstream model is cheaper and safer than translation.
- USE Anticorruption Layer when a foreign model would corrupt the local language.
- USE Open Host Service when many clients need a stable protocol into one context.
- USE Published Language when multiple systems need a documented interchange model.
- USE Separate Ways when integration cost is higher than shared capability value.
- TREAT Big Ball of Mud as a context to contain and translate around, not as a model to spread.

Anti-patterns (MUST NOT):
- claiming independent modeling while conforming silently
- using Shared Kernel without governance
- calling integration an anticorruption layer when no translation exists

---

## Integration Style Rules

1. Use RPC only when request/response coupling, latency, versioning, and failure semantics are acceptable.
2. Use REST resources as application-facing representations, not as leaked aggregate internals.
3. Use messaging when asynchronous coordination fits the business process and consumers can handle lag, duplicates, and ordering limits.
4. Decide whether domain events should carry enough information for consumers or require query-back.
5. Keep integration contracts separate from internal models.
6. Test translations at context boundaries.

---

## Ubiquitous Language Rules

1. Use domain terms from the current bounded context in code, tests, commands, events, and conversations.
2. One concept gets one term.
3. One term must not carry multiple meanings inside one context.
4. Rename code when understanding improves.
5. Prefer domain names over technical placeholders.

Avoid:
- technical placeholders that conceal a business concept
- names imported from another bounded context without translation
- generic helper or utility names that end up carrying domain decisions

---

## Tactical Pattern Rules

### Entities
Use entities when identity and lifecycle matter.

Rules (MUST unless marked SHOULD or MUST NOT):
1. Entities must have explicit identity.
2. Entities must protect meaningful state transitions.
3. Do not expose unrestricted state changes by default.

### Value Objects
Use value objects aggressively when a primitive hides meaning.

Rules (MUST unless marked SHOULD or MUST NOT):
1. Value objects are immutable by default.
2. They validate themselves.
3. They make code read in domain language.

### Aggregates
Use aggregates only where invariants require a consistency boundary.

Rules (MUST unless marked SHOULD or MUST NOT):
1. Keep aggregates small.
2. Protect invariants through the aggregate root.
3. Reference other aggregates by identity.
4. Avoid loading large object graphs.

### Domain Events
Use domain events for meaningful facts.

Rules (MUST unless marked SHOULD or MUST NOT):
1. Name events in the past tense.
2. Use events when they clarify collaboration or integration.
3. Do not publish trivial noise for every field change.

## Aggregate Minimalism Rules

1. Do not create large aggregates to make navigation convenient.
2. Default to smaller boundaries.
3. Default to eventual consistency across aggregates.
4. Use IDs for references across aggregate boundaries.
5. One transaction should usually change one aggregate.

Anti-patterns (MUST NOT):
- aggregate designed around a screen
- one request loading and mutating a whole graph
- aggregate roots exposing mutable children directly

---

## Application Service Rules

1. Application services coordinate use cases.
2. They load aggregates, call domain behavior, save results, and trigger integration work.
3. They must not become the real domain model.
4. They should stay thin enough that the model still carries meaning.

Anti-patterns (MUST NOT):
- all business decisions in application services
- controllers duplicating application orchestration
- application services shaped only by transport

---

## Architecture and Infrastructure Rules

1. Infrastructure is a detail.
2. Keep frameworks, persistence mechanics, REST resources, transport formats, and other technology concerns out of the domain model.
3. Persist aggregates without letting persistence define the model.
4. Translate transport and integration data at the boundary.

Anti-patterns (MUST NOT):
- persistence-first modeling
- reusing transport objects as domain objects
- domain methods depending on framework types

---

## Collaboration Rules

1. Keep names close to real business terms.
2. Prefer code that teaches the model to a reader.
3. Make domain assumptions explicit in names, tests, and events.
4. Where a concept is fuzzy, do not hide the ambiguity behind technical abstractions.

Anti-patterns (MUST NOT):
- generic code that could belong to any business
- unexplained status codes and flags with domain meaning
- enums and booleans where a richer concept is needed

---

## Practicality Rules

1. Use the least expensive pattern that honestly models the problem.
2. Simple domains may use simple services and data structures.
3. Once invariants, lifecycle, and language complexity rise, strengthen the model.
4. Prefer incremental improvement over massive design overhauls.

Anti-patterns (MUST NOT):
- dismissing DDD because not every module needs it
- over-modeling a generic subsystem
- introducing aggregates and events before knowing why

---

## Accelerated Modeling and Project Rules

1. Use event storming or similar collaborative modeling when workflow, events, commands, policies, or team language are unclear.
2. Timebox modeling work so it improves implementation instead of becoming detached analysis.
3. Use modeling spikes to reduce uncertainty before committing to a model shape.
4. Track modeling debt when code and language are known to be imperfect but intentionally deferred.
5. Involve domain experts in scenario walkthroughs, terminology decisions, and acceptance criteria.
6. Estimate DDD work by modeling uncertainty, integration risk, and implementation cost, not only by feature count.
7. Treat team skill and access to domain experts as constraints on how much DDD ceremony the project can sustain.

---

## Code Generation Rules

When generating code, use this default order:
1. identify the subdomain
2. identify the bounded context
3. write names in the local ubiquitous language
4. decide whether a concept is entity, value object, aggregate, service, repository, or event
5. choose the smallest tactical pattern that fits
6. isolate infrastructure at boundaries
7. keep context translation explicit

Default avoidance:
- giant shared domain packages
- service-centric fake DDD
- technical names replacing domain language
- full tactical DDD in trivial modules

---

## Review Rules

When reviewing code, actively look for:
- missing subdomain classification
- missing bounded context ownership
- context bleeding
- no context translation where meanings differ
- primitive obsession
- anemic entities
- no value objects where concepts repeat
- aggregates too large
- services containing all behavior
- excessive ceremony in simple modules
- no modeling at all in complex modules

---

## Testing Rules

1. Domain tests must read in the ubiquitous language.
2. Test value objects for validation and behavior.
3. Test entities and aggregates for valid and invalid transitions.
4. Test application services for orchestration, not for all domain rules.
5. Test context translation where external or foreign models exist.

---

## Review Checklist

Before finalizing any change, verify:
- Is the subdomain/core importance understood?
- Is the bounded context explicit?
- Is the ubiquitous language visible in the code?
- Did we use only the tactical patterns that genuinely help?
- Are aggregates small and focused on invariants?
- Are value objects used where they clarify meaning?
- Are application services coordinating rather than owning all domain logic?
- Did we keep infrastructure out of the model?
- Did we avoid DDD theater and over-modeling?

If any answer is no, revise before shipping.

---

## Final Instruction

When uncertain, choose the option that:
1. sharpens the business language
2. clarifies the bounded context
3. models real complexity honestly
4. avoids unnecessary ceremony
5. keeps the design practical enough to deliver

Use DDD selectively, but seriously.
