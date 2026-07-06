# Methodology Selection Matrix

Different specification methodologies serve different purposes. This guide helps select the right methodology (or combination) for your AI code generation context.

## Methodology Spectrum

```
Human-oriented (conversational) ─────────────────────────── Machine-oriented (formal)
        |              |                |                      |               |
    User Stories    BDD/Gherkin    OpenAPI-first          DbC/Contracts   Formal Methods
    (Agile)         (Cucumber)     (Swagger/OpenAPI)       (Eiffel)        (TLA+, Alloy)
        |              |                |                      |               |
    Too vague       Executable      Machine-readable       Machine-        Provably
    for AI          & human-        API contracts           verifiable      correct
```

## Methodology Descriptions

### User Stories (Agile)

**Format:** "As a [role], I want [capability] so that [benefit]"

**AI-readiness:** LOW. User stories express intent but lack the precision AI agents need. They work as conversation starters with humans but fail as executable specs for AI.

**When to use:** As the starting point for spec authoring (Phase 0), but they must be refined into structured acceptance criteria before entering the SDD pipeline.

### Behavior-Driven Development (BDD) — Gherkin / Cucumber

**Format:**
```gherkin
Feature: Title
  Scenario: Description
    Given <precondition>
    When <action>
    Then <expected outcome>
```

**AI-readiness:** HIGH. Gherkin is the most AI-friendly spec format for behavioral requirements.

**Why:**
- Fixed syntax with defined keywords — agents parse it deterministically
- Scenarios map directly to test cases — spec IS the test
- Each scenario produces a binary PASS/FAIL verdict
- Language-agnostic — works with any tech stack
- Tools exist to execute scenarios directly (Cucumber, SpecFlow, Behave)

**When to use:** Any behavioral requirement where the user can describe preconditions, actions, and expected outcomes.

**Limitations:** Does not cover non-functional requirements well. Step definitions require maintenance. Complex state setup can make scenarios brittle.

### OpenAPI-First

**Format:** YAML/JSON specification following the OpenAPI 3.x standard

**AI-readiness:** VERY HIGH for API definitions. Directly machine-parseable.

**Why:**
- Declarative YAML/JSON — agents parse without interpretation
- Can generate server stubs, client libraries, and test harnesses
- GitHub Copilot, Cursor, Claude Code all consume OpenAPI natively
- Enables mock-server testing before implementation exists

**When to use:** Any system with REST APIs, microservices, or client-server interfaces.

**Limitations:** REST-only. Does not cover internal logic, async events, or architectural decisions.

### AsyncAPI

**Format:** YAML/JSON for event-driven and message-based APIs

**AI-readiness:** HIGH. Same YAML/JSON structure as OpenAPI but for async channels.

**When to use:** Event-driven architectures, message queues (Kafka, RabbitMQ), WebSocket APIs.

### Design by Contract (DbC)

**Format:** Preconditions, postconditions, and invariants expressed as assertions

**AI-readiness:** VERY HIGH. Contracts:
- Are machine-verifiable
- Translate directly to assertions in generated code
- Define clear success/failure boundaries
- Enable fuzz testing and property-based verification

**When to use:** Interface boundaries between components, library/API contracts, systems where correctness guarantees matter. Works alongside any other methodology — contracts complement rather than replace behavioral specs.

### Formal Methods — TLA+, Alloy

**Format:** Mathematical models of system behavior, verified by model checkers

**AI-readiness:** VERY HIGH for specific use cases (distributed systems, protocols, safety-critical components). The model checker provides provable guarantees.

**When to use:**
- Distributed/concurrent systems (race conditions, deadlocks, consensus)
- Critical infrastructure where correctness is paramount
- Protocol design (network, consensus, replication)
- Systems where a bug costs >$1M

**Tradeoff:** The "formal methods tax" — requires specialized expertise, is slow to write, and covers only specific properties (safety/liveness), not full system behavior. Use only for critical subsystems, not the entire codebase.

### Architecture Decision Records (ADRs)

**Format:** Structured markdown with Context → Decision → Consequences

**AI-readiness:** MEDIUM. ADRs are narrative documents, not executable. They provide context that informs AI code generation but do not directly drive it.

**When to use:** Alongside behavioral specs. ADRs provide architectural context (why a decision was made, what alternatives were considered) that helps AI agents make consistent implementation choices.

### C4 Model

**Format:** Hierarchical diagrams at 4 levels (Context → Container → Component → Code)

**AI-readiness:** MEDIUM-HIGH for architecture. The structured hierarchy maps well to AI consumption when expressed as structured markdown or PlantUML, but the diagrams themselves require human interpretation.

**When to use:** Defining system boundaries and component decomposition before AI agents implement individual containers/components.

### arc42

**Format:** Structured template for software architecture documentation

**AI-readiness:** MEDIUM. arc42 provides a comprehensive template (constraints, building block view, runtime view, deployment, cross-cutting concepts) that can feed into AI agents as architectural constraints, but it's prose-heavy.

**When to use:** As the architectural companion to a behavioral SPEC.md, especially for complex systems with multiple quality concerns.

## Selecting a Methodology

The AI software factory typically needs a **composite** approach — not a single methodology:

| Concern | Best Methodology | AI-Readiness |
|---------|-----------------|--------------|
| What the system does (behavior) | BDD / Gherkin | HIGH |
| How components communicate | OpenAPI / AsyncAPI | VERY HIGH |
| Interface contracts | Design by Contract | VERY HIGH |
| Architecture decisions | ADRs | MEDIUM |
| System structure | C4 / arc42 | MEDIUM |
| Critical correctness | TLA+ / Alloy | VERY HIGH (narrow scope) |
| Business intent | User Stories | LOW (needs refinement) |

The SPEC.md template in this skill's templates/ directory combines multiple approaches: structured Gherkin-like ACs for behavior, OpenAPI/YAML for interfaces, and prose sections for architecture context.
