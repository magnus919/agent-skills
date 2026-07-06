# SDD Overview & Philosophy

## What Is Spec-Driven Development?

Spec-Driven Development (SDD) is a methodology for building software where **the specification is the executable input** to a code generation pipeline. It synthesizes practices from Behavior-Driven Development (BDD), Design by Contract (DbC), Formal Methods (TLA+/Alloy), OpenAPI-first design, and lean phase-gate project management — organized around a central insight relevant to AI code generation.

## The Core Distinction

Traditional requirements engineering produces documents that **describe** what the system should do. SDD produces specifications that **drive** what the system does.

| Aspect | Traditional Requirements | SDD Spec |
|--------|------------------------|----------|
| Primary consumer | Humans | AI agents (also readable by humans) |
| Purpose | Communication and alignment | Executable input to code generation |
| Ambiguity tolerance | High — humans can ask questions | Zero — agents implement one interpretation |
| Verification | Manual review | Automated acceptance criteria |
| Format | Prose-heavy documents | Structured markdown + machine-readable formats |

## The Software Factory Metaphor

SDD adopts the factory model for software development:

| Factory Element | SDD Equivalent |
|----------------|----------------|
| Blueprints | Specification (SPEC.md) |
| Routing plan | Work decomposition (TASK-PLAN.md) |
| Work orders | Individual tasks with acceptance criteria |
| Assembly line | AI code generation agents |
| Quality control | Verification against spec |
| Rework loop | Failed AC → spec review → regenerate |

The metaphor is precise: a factory doesn't design products on the assembly line. The design (spec) is completed, reviewed, and approved before any fabrication (code generation) begins. Changes to the design go back through the design process, not through ad-hoc patches on the factory floor.

## The Feedback Loop

When verification fails, the root cause can be in two places:

| Failure Type | Root Cause | Response |
|-------------|-----------|----------|
| Implementation bug | Code doesn't meet spec | Regenerate code for affected task |
| Spec ambiguity | Spec is unclear | Revise spec, regenerate code |
| Missing edge case | Spec didn't enumerate | Add edge case to spec, regenerate |
| NFR failure | Implementation choices | Revise task plan with NFR constraints |
| Contract violation | Interface mismatch | Fix contract alignment across tasks |

The feedback loop routes failures to their correct root cause. A spec defect should not be fixed by patching code — it should be fixed in the spec, and the code regenerated.

## Key Principles

1. **Precision over clarity.** The AI cannot ask for clarification. A precise-but-dense spec is better than a readable-but-ambiguous one.

2. **Completeness over brevity.** Every missing acceptance criterion is a missing feature. The cost of specifying an edge case up front is minutes; discovering it in production is hours or days.

3. **Testability over descriptiveness.** An AC that cannot produce a CLEAR PASS or CLEAR FAIL is not an AC — it's a hope.

4. **Gates catch defects early.** A defect caught at Gate 1 (spec review) costs minutes to fix. The same defect caught at Gate 4 (acceptance review) costs hours — the entire implementation may need to be discarded.

5. **Spec is the single source of truth.** Every downstream artifact — task plan, architecture, implementation, tests — derives from and traces back to the spec. Deviations are defects unless explicitly documented.

6. **Spec IS the test (when possible).** Acceptance criteria expressed in Gherkin (Given/When/Then) serve double duty as test cases. No separate test writing required.

## When to Use SDD

SDD excels when:
- AI agents are generating the code and cannot ask clarifying questions
- The system has defined interfaces, contracts, or behavioral boundaries
- Multiple AI agents work in parallel and need consistent guidance
- Quality requirements justify spec investment (not throwaway prototypes)
- The team can maintain spec discipline (spec + code are both versioned)

SDD is overkill when:
- The implementation is a throwaway prototype or spike
- Requirements are genuinely unknown and emerge through exploration
- The team lacks the discipline to maintain specs alongside code
- The cost of writing a spec exceeds the cost of fixing bugs in production
