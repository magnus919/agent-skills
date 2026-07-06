# Format Translation

Specifications in an AI software factory come in multiple formats. This reference covers how to translate between formats, when to use each, and the conversion loss risks.

## Translation Map

```
                    ┌─────────────────┐
                    │   Human PRD     │ (natural language)
                    └────────┬────────┘
                             │ (lossy — interpretation required)
                             ▼
                    ┌─────────────────┐
                    │   SPEC.md       │ (structured markdown)
                    └───┬──────┬──────┘
                        │      │
               ┌────────┘      └────────┐
               ▼                         ▼
     ┌──────────────────┐     ┌──────────────────┐
     │  Gherkin .feature│     │  OpenAPI YAML     │
     │  (behavior)      │     │  (API contracts)  │
     └────────┬─────────┘     └────────┬─────────┘
              │                        │
              ▼                        ▼
     ┌──────────────────┐     ┌──────────────────┐
     │  Step definitions│     │  Server stubs    │
     │  + test cases    │     │  + client SDKs   │
     └──────────────────┘     └──────────────────┘
```

## Directional Conversions

### Human PRD → SPEC.md

**Loss:** HIGH. A PRD is narrative, opinionated, and assumes shared context. Converting to structured SPEC.md requires:

1. Extract explicit requirements from narrative prose
2. Identify implicit assumptions and make them explicit
3. Decompose vague statements into testable ACs
4. Add edge cases the PRD author didn't consider
5. Define measurable NFR thresholds from qualitative descriptions

**Risk:** Interpretation loss. The PRD author's intent may not survive the translation. **Solution:** Send the SPEC.md to the PRD author for Gate 1 review.

### SPEC.md → Gherkin Feature Files

**Loss:** LOW (for behavioral sections). Gherkin maps directly to the user stories and ACs in SPEC.md.

**Mapping:**
```
SPEC.md user story → Gherkin Feature (with narrative)
SPEC.md acceptance criteria → Gherkin Scenario (Given/When/Then)
SPEC.md edge cases → Additional Scenarios or Scenario Outline
```

**Translation example:**

| SPEC.md | Gherkin |
|---------|---------|
| "US-001: As a user, I want to reset my password" | `Feature: Password Reset` |
| "AC-001.1: Given I'm on the login page, When I click 'Forgot Password', Then I see an email input field" | `Scenario: Initiate password reset` with Given/When/Then |
| "Edge case: email not found" | `Scenario: Reset with unregistered email` |

### SPEC.md → OpenAPI YAML

**Loss:** LOW-MEDIUM. The Data Contracts & Interfaces section of SPEC.md maps directly to OpenAPI paths, schemas, and responses.

**Mapping:**
```
SPEC.md "Data Contracts" API spec → OpenAPI paths
SPEC.md request/response schemas → OpenAPI components/schemas
SPEC.md auth requirements → OpenAPI securitySchemes
SPEC.md error formats → OpenAPI responses with examples
```

**Translation example:**
```markdown
## Data Contracts

### POST /api/users
- Request: { name: string, email: string }
- Response 201: { id: uuid, name: string, email: string, created_at: datetime }
- Error 409: { error: "email_taken", message: "..." }
```

→ OpenAPI YAML with the path, requestBody schema, and response schemas for 201 and 409.

### Gherkin ↔ OpenAPI (cross-format verification)

Gherkin scenarios can validate OpenAPI contracts and vice versa:

- An OpenAPI `400` response definition implies a Gherkin scenario: "When I send an invalid request, Then I receive 400"
- A Gherkin scenario about successful creation implies an OpenAPI `201` response with a specific schema

**Trick:** Generate Gherkin scenarios directly from OpenAPI response codes and schemas. Every documented error code should have a corresponding negative test scenario.

### SPEC.md → TASK-PLAN.md tasks

**Loss:** MINIMAL (intentional). Each AC in SPEC.md becomes one or more tasks in TASK-PLAN.md. This is not a lossy conversion — it's a decomposition.

**Rule:** Every AC must appear in at least one task. The `spec-to-tasks.sh` script validates this coverage.

### SPEC.md → JSON Schema (data contracts)

**Loss:** NONE for structural types. JSON Schema losslessly represents the type constraints in SPEC.md data contracts.

**Mapping:**
```
SPEC.md field type constraints → JSON Schema type/format/enum
SPEC.md required fields → JSON Schema required array
SPEC.md validation rules → JSON Schema pattern/minLength/maxLength
```

## Conversion Ordering

For a new feature, the recommended conversion sequence:

```
1. Human conversation → SPEC.md (structured markdown)
2. SPEC.md behavioral ACs → Gherkin .feature files (spec-as-tests)
3. SPEC.md data contracts → OpenAPI YAML + JSON Schema (for code gen)
4. SPEC.md → TASK-PLAN.md (for implementation sequencing)
```

Steps 2 and 3 can happen in parallel since they target different concerns.

## Format Selection Guide

| Format | Best For | Worst For |
|--------|----------|-----------|
| SPEC.md (markdown) | Complete spec with all concerns | Machine automation without human review |
| Gherkin | Behavioral requirements, executable tests | Architecture, NFRs, data contracts |
| OpenAPI | REST API contracts, client/server code gen | Internal business logic, UI, async events |
| AsyncAPI | Event-driven systems, message queues | Request/response APIs |
| JSON Schema | Data validation, type safety | Behavior, orchestration, side effects |
| Protocol Buffers | High-performance RPC, cross-language schemas | Human readability, quick iteration |
| TLA+ | Distributed systems, protocol verification | Full-system specification, non-critical code |

## Translation Risks

| Conversion | Risk | Mitigation |
|------------|------|-----------|
| Human prose → structured spec | Intent loss | Review Gate 1 with domain expert |
| SPEC.md → Gherkin | ACs that don't map to scenarios | Cover every AC in at least one scenario |
| SPEC.md → OpenAPI | Missing error paths | Derive error responses from edge cases, not just happy path |
| Gherkin → step definitions | Brittle UI-coupled steps | Implement at the API/domain layer, not UI layer |
| OpenAPI → client stubs | Stale SDKs when API changes | Regenerate stubs from spec, keep generation in CI |

## Brownfield: Reverse-Engineering Specs from Code

When working with existing codebases that have no specs, the conversion direction reverses:

```
Code → API surface (OpenAPI from routes/swagger/middleware)
Code → Behavioral spec (Gherkin from tests or observed behavior)
Code → Architecture decisions (ADRs from code review & commit history)
```

This is never lossless. The resulting spec captures **what the code does**, not **what it should do**. Treat reverse-engineered specs as starting points for refinement, not ground truth. See `ai-factory-pipeline.md` for brownfield feature additions.
