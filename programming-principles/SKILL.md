---
name: programming-principles
description: Distilled coding principles from 14 classic software books.
version: 0.2.0
author: Hermes
license: MIT
compatibility: Platform-agnostic. Works with any agent that supports the Agent Skills
  directory format. No external dependencies.
source: https://github.com/mattpocock/agent-rules-books
---

# Programming Principles (14 Books)

Principles distilled from the `mattpocock/agent-rules-books` repo — 14 pre-made
AGENTS.md rule sets derived from classic software engineering books. Use this
skill directly during code review, refactoring, design, and implementation.
For deeper per-book coverage, load the relevant reference file.

## Task-to-Book Mapping

When the task involves...                    Load / apply principles from
────────────────────────────────────────────────────────────────────────
Everyday implementation & code review        Clean Code, Code Complete
Refactoring existing code                    Refactoring, WELC
Architecture / dependency management         Clean Architecture, APoSD
Domain modeling / business rules             DDD, DDD Distilled, IDDD
Enterprise app patterns / layering           PoEAA
Production reliability / stability           Release It!
Data consistency / scalability / events      DDIA
Engineering craft / automation               Pragmatic Programmer
Designing APIs / module boundaries           APoSD
Legacy code / risky changes                  WELC, Refactoring

## How to Perform a Code Assessment

For a structured, reproducible workflow that combines book principles with
actual repo exploration, see `references/code-assessment-workflow.md`. It
covers: loading the evaluation framework, reading the repo and GitHub context,
deduplicating against existing issues/PRs, classifying findings by book +
priority, and deciding whether each merits an issue.

## Cross-Cutting Principles

Principles synthesized from multiple books, organized by concern.

### Naming & Communication

- One term per concept across the codebase. RENAMING is design work.
- Names reveal abstraction, not mechanism. Prefer domain vocabulary over
  technical implementation detail.
- Functions are verbs, classes/types are nouns, booleans are predicates.
- A name needing a comment to explain it is the wrong name.
- Comments exist for rationale, contracts, warnings, and non-obvious constraints
  — never to narrate code or compensate for bad names.

### Functions & Routines

- ONE level of abstraction per function. Tell the story top-down.
- Keep parameters few. Boolean flags mean split the function.
- Separate commands (mutate) from queries (answer). Never both.
- When a module exceeds ~400 lines or requires scrolling to understand its
  full scope, it's a candidate for decomposition. Split by stable
  responsibility boundary, not by execution order or framework convention.
- The happy path must be readable. Isolate error handling, edge cases, and
  cleanup from the main flow.
- A function too long to name precisely is too long. Extract.

### Architecture & Boundaries

- Source dependencies point INWARD toward higher-level policy. Domain and use
  cases never import frameworks, databases, UI, or vendor SDKs.
- Every external dependency — HTTP clients, filesystems, databases, vendor
  SDKs — must sit behind a trait or interface owned by inner layers. Direct
  instantiation of infrastructure code inside application or domain logic is
  a structural violation (Dependency Inversion Principle).
- Frameworks, databases, delivery mechanisms, and devices are outer-layer
  details. Keep them behind ports, gateways, and adapters.
- Organize by business capability / use case first, NOT by technical layer
  (controllers/, services/, repositories/).
- The dependency rule: inner layers OWN the interfaces they need; outer layers
  IMPLEMENT them.
- Choose boundaries by volatility and policy importance, not by size or habit.
- A wrapper, layer, or abstraction must HIDE more complexity than it adds.
  Pass-through layers are debt.

### Data & State

- Prefer types that make invalid states unrepresentable. Use enums for closed
  sets, Value Objects for meaningful primitives, and booleans only for binary
  meanings.
- Make data ownership explicit: distinguish source of truth from derived,
  cached, or ephemeral data.
- Treat shared mutable state, globals, and ambient context as costs that must
  earn themselves.
- Keep identity, lifecycle, mutation, and loading behavior visible.
- One authoritative representation per piece of system knowledge. Derive or
  generate everything else.

### Testing

- Tests are production code: readable, deterministic, aligned with behavior.
- Keep tests focused on externally visible behavior, not internal
  implementation details.
- Add a characterization test before changing behavior in untested code.
- When fixing a bug, add a regression test that would have caught it.
- Treat ignored, flaky, or skipped tests as unresolved questions.
- The Boy Scout Rule for tests: leave the test suite cleaner than you found it.

### Error & Failure Handling

- Distinguish: programmer errors (assert), contract violations (panic/fail),
  expected domain failures (return/result type), retryable failures, and
  permanent failures.
- Treat every dependency, timeout, retry, queue, and degraded state as capable
  of failing in slow, partial, or prolonged ways.
- Timeouts on ALL outbound calls. No infinite waits. Finite retries with
  exponential backoff and jitter. Never retry validation errors or permanent
  failures — distinguish retryable from non-retryable outcomes.
- Validate external input at trust boundaries. Never trust shape, size, or
  semantics of things from outside the process.
- Fail fast when continuing hides unrecoverable trouble. Let-it-crash only with
  supervision and isolation.

### Refactoring & Change

- Refactoring is behavior-preserving structural improvement. Never disguise a
  feature or redesign as cleanup.
- Work in small, reversible, buildable steps. Split patches too large for
  local reasoning.
- Identify the structural friction blocking a change. Refactor BEFORE the
  feature only when it makes the feature safer or simpler.
- Target the current blocking smell, not every smell in sight. Stop when the
  next cleanup would be speculative.
- Remove duplication when the SAME edit appears a third time.
- Decompose when a module exceeds ~400 lines or handles 3+ distinct
  responsibilities. A module you can't name in a single sentence is
  doing too much — extract the cohesive sub-concepts.
- Prefer the simplest named move: rename, extract, inline, move, split, or
  substitute.

## Per-Book Compressed Rules

### Clean Code (Martin)
Readability, local reasoning, maintainability. Corrects: "working code = clean."
- Functions: one thing, one level of abstraction, top-down narrative
- Names: intention-revealing, pronounceable, one concept per term
- No boolean flags, no output parameters, no hidden side effects
- Comments only for rationale/constraints, never to narrate
- Tests as production code: readable, deterministic, fast
- Boy Scout Rule: leave touched code cleaner

### A Philosophy of Software Design (Ousterhout)
Deep modules, information hiding, complexity reduction. Corrects: "familiar patterns = simple."
- Deep modules: small interface, meaningful hidden complexity. Reject thin wrappers.
- Pull complexity downward into the module that owns the detail
- Design interfaces around what callers need to know, not how impl works
- Reduce exception surface via stronger invariants. Define away invalid states.
- Comments document design decisions and hidden complexity
- Names, consistency, and obviousness ARE design information

### Clean Architecture (Martin)
Business rules independent of frameworks/databases/UI. Corrects: "details = architecture."
- Dependencies point inward. Domain never imports frameworks, DB, UI, vendors.
- Entities guard enterprise invariants; Use Cases orchestrate one action
- Frameworks, DB, delivery = outer-layer details behind Ports/Adapters
- Inner layers OWn interfaces; outer layers IMPLEMENT
- Use cases are not merged by sharing; duplication from different actors stays
- Core tests run without real DB, network, framework, or hardware

### Code Complete (McConnell)
Construction discipline, defect reduction, verifiable code. Corrects: "typing = construction."
- Sketch pseudocode at consistent abstraction before complex routines
- Input validation at every trust boundary. Assertions for programmer assumptions.
- Handle errors at the right abstraction. Never silently continue from corruption.
- Rising complexity IS defect risk. Split tangled routines.
- Build in small, verifiable increments. Integrate often.
- Comments explain intent, constraints, contracts — not mechanics.

### Domain-Driven Design (Evans) + DDD Distilled (Vernon)
Ubiquitous language, bounded contexts, tactical patterns. Corrects: "model = data schema."
- Name the Bounded Context before interpreting any term or module
- One term per concept within the context. Code speaks Ubiquitous Language.
- Aggregates: small, one root, invariant-protected, one per transaction default
- Value Objects: immutable, validated at construction, compare by value
- Repositories return domain objects, not tables or ORM rows
- Domain Events: past-tense business facts, not property-change notifications
- Anti-corruption layer at every context boundary
- Core Domain gets richer modeling; supporting subdomains stay simpler

### Implementing DDD (Vernon)
Practical DDD: aggregates, events, services, persistence. Corrects: "renamed CRUD = DDD."
- Reference other Aggregates by identity, not by object graph
- Domain Services for operations that fit no Entity or Value Object
- Application Services coordinate use cases — they don't own domain decisions
- CQRS when consistency or representation needs justify separate models
- Event Sourcing only when the event sequence IS the right persistence model
- Test invariants, valid/invalid state transitions, and events directly

### Patterns of Enterprise Application Architecture (Fowler)
Layering, patterns for enterprise apps. Corrects: "more patterns = better design."
- Choose business logic pattern by force: Transaction Script → Table Module → Domain Model
- Service Layer for use-case coordination and transaction boundaries
- Repository speaks domain terms; Data Mapper keeps SQL out of domain objects
- Unit of Work for one logical commit; Identity Map for one identity per scope
- Remote Facade + DTOs at cross-layer boundaries — never leak domain internals
- Session state chosen deliberately: client, server, or DB with scaling accounted for

### Refactoring (Fowler)
Behavior-preserving structural improvement. Corrects: "cleanup = rewrite."
- Preserve observable behavior. Isolate behavior change from structural change.
- Small, reversible, testable steps. Safety net before risky work.
- Preparatory refactoring: reshape blocking structure BEFORE the feature
- Targeted at the current blocking smell, not every smell in sight
- Simplest named move: rename, extract, inline, move, encapsulate, substitute
- Stop when the requested change is easy and the blocking smell is gone

### Working Effectively with Legacy Code (Feathers)
Safe change in untested code. Corrects: "rewrite = first move."
- Legacy = code without trustworthy tests. Characterize before redesign.
- Find or create a seam: place to change behavior without editing surrounding code
- Break the ONE blocking dependency before making the change
- Sprout Method, Sprout Class, Wrap Method, Wrap Class for insertion
- Leave the area more testable than found
- Reject: hidden dependency expansion, cosmetic-only refactoring, big rewrites

### Designing Data-Intensive Applications (Kleppmann)
Distributed data, consistency, events, replication. Corrects: "everything is local/ordered/exactly-once."
- Source of truth, derived representations, and consistency expectations must be EXPLICIT
- Treat crashes, partial writes, duplicates, and timeouts as normal input
- Write semantics: durable when? visible when? conflicts how? stale reads allowed?
- Events describe facts. Consumers tolerate lag, duplicates, replay, versioned payloads.
- Schemas, APIs, and events evolve across old/new readers/writers
- Partition by workload-relevant locality; make hot-key and cross-partition costs explicit
- Transactions and isolation matched to actual invariants, not blanket defaults

### Release It! (Nygard)
Production reliability, stability patterns. Corrects: "happy path = production readiness."
- Timeouts on every outbound call. No infinite waits. Bounded retries with backoff.
- Circuit breakers, bulkheads, fast failure to isolate dependency failures
- Design overload behavior: finite queues, load shedding, capacity for critical traffic
- Startup, health checks, migrations, and operational controls: restartable, observable
- Validate external responses for shape, plausibility, and semantics before trusting
- Observability at every boundary: latency, saturation, errors, queue depth, breaker state

### The Pragmatic Programmer (Hunt & Thomas)
Engineering craft, accountability, automation. Corrects: "local edit = done."
- One authoritative source per fact. Everything else derives or traces.
- Preserve orthogonality: independent components, narrow interfaces, separated concerns
- Tracer bullets over piles of isolated pieces. Validate architecture end-to-end early.
- Automate repetitive, error-prone, easy-to-forget work
- Shorten feedback loops: relevant tests, automated checks, cheap early signals
- Broken windows: fix or visibly contain small quality decay before it normalizes
- Debug from reproduced facts: observe, isolate, explain, fix, verify

### Refactoring.Guru
Smell catalog and technique catalog. Corrects: "pattern = always the answer."
- Diagnose the smell before choosing the technique
- Prefer the simplest treatment: rename before extract, extract before redesign
- Each smell has a specific root cause and treatment path
- See `references/refactoring-guru-smells.md` for the full catalog

## Compatibility Guide

Books that CONFLICT (do not load as equal guidance):
- DDD ❌ PoEAA — different data ownership paradigms
- IDDD ❌ PoEAA — same conflict at implementation level

Books that OVERLAP (choose one, they push similar pressure):
- Clean Code 🔁 Pragmatic Programmer, Code Complete, APoSD — code quality
- DDD 🔁 DDD Distilled, IDDD — DDD at different depths; pick the level you need
- Clean Architecture 🔁 IDDD, PoEAA — architecture/layering overlap
- Refactoring 🔁 Refactoring.Guru — code improvement; choose Refactoring for strategy, Guru for catalog

All other pairs are complementary. Default: one primary always-on book, others
loaded on-demand per task.

## Local Reference Files

Each book's mini rule set is available as a local reference file under
`references/`. Load any with:

```
skill_view(name='programming-principles', file_path='references/{book-dir}.mini.md')
```

| File | Book |
|------|------|
| `references/a-philosophy-of-software-design.mini.md` | A Philosophy of Software Design |
| `references/clean-architecture.mini.md` | Clean Architecture |
| `references/clean-code.mini.md` | Clean Code |
| `references/code-complete.mini.md` | Code Complete |
| `references/designing-data-intensive-apps.mini.md` | Designing Data-Intensive Applications |
| `references/domain-driven-design.mini.md` | Domain-Driven Design |
| `references/domain-driven-design-distilled.mini.md` | DDD Distilled |
| `references/implementing-domain-driven-design.mini.md` | Implementing DDD |
| `references/patterns-of-eaa.mini.md` | Patterns of Enterprise App Architecture |
| `references/refactoring.mini.md` | Refactoring |
| `references/refactoring-guru.mini.md` | Refactoring.Guru |
| `references/release-it.mini.md` | Release It! |
| `references/the-pragmatic-programmer.mini.md` | The Pragmatic Programmer |
| `references/working-effectively-with-legacy-code.mini.md` | Working Effectively with Legacy Code |
| `references/code-assessment-workflow.md` | Assessment methodology — not a book, but the workflow for combining all books against a real repo |

Each book also has a **full** version (11-63 KB) for deep reference when you need
the complete rule catalog. Load on demand:

```
skill_view(name='programming-principles', file_path='references/{name}.full.md')
```

| Full File | Book | Size |
|-----------|------|------|
| `references/a-philosophy-of-software-design.full.md` | A Philosophy of Software Design | 13 KB |
| `references/clean-architecture.full.md` | Clean Architecture | 17 KB |
| `references/clean-code.full.md` | Clean Code | 13 KB |
| `references/code-complete.full.md` | Code Complete | 12 KB |
| `references/designing-data-intensive-apps.full.md` | Designing Data-Intensive Applications | 16 KB |
| `references/domain-driven-design.full.md` | Domain-Driven Design | 42 KB |
| `references/domain-driven-design-distilled.full.md` | DDD Distilled | 11 KB |
| `references/implementing-domain-driven-design.full.md` | Implementing DDD | 12 KB |
| `references/patterns-of-eaa.full.md` | Patterns of Enterprise App Architecture | 15 KB |
| `references/refactoring.full.md` | Refactoring | 17 KB |
| `references/refactoring-guru.full.md` | Refactoring.Guru | 62 KB |
| `references/release-it.full.md` | Release It! | 13 KB |
| `references/the-pragmatic-programmer.full.md` | The Pragmatic Programmer | 13 KB |
| `references/working-effectively-with-legacy-code.full.md` | Working Effectively with Legacy Code | 13 KB |

Progressive disclosure pattern: load the **mini** file for daily guidance (triggers,
decision rules, final checklist). Load the **full** file only for deep sessions,
audits, or when you need the complete rule catalog with code-smell indexes and
technique references.

## Known Weaknesses (from repo criticism)

- No empirical measurement of improvement — these are principle-based, not
  benchmarked. Apply judgment about whether rules improve actual outcomes.
- Loading too many rule sets at once causes context saturation. Use at most one
  primary always-on set + one task-specific on-demand set.
- Rules are book-derived, not incident-derived. The highest-value agent rules
  come from real failures, not theory.
- Risk of pseudo-compliance: agent follows the letter of rules while missing
  the actual task. Test outputs against real requirements, not rule conformity.
