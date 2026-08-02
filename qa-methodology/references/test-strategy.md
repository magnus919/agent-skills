# Test Strategy Design

## The Pyramid as Heuristic, Not Dogma

The test pyramid (unit → integration → E2E) is a **starting point** for test investment allocation. Adapt the shape to your system's risk profile, feedback-loop requirements, and team capabilities.

> **Gotcha — Pyramid dogmatism:** Treating the pyramid as a rule ("always more unit than E2E") leads to over-testing trivial logic while under-testing the integration boundaries where real defects cluster. Measure where your bugs actually escape and invest there.

### Alternative Models

| Model | Origin | Core Idea | When It Fits |
|-------|--------|-----------|--------------|
| **Testing Trophy** | Kent C. Dodds | Integration tests give the highest confidence-per-effort; unit tests support them | UI-heavy apps, React/Vue ecosystems |
| **Testing Quadrants** | Lisa Crispin & Janet Gregory | Classify tests by purpose (technology-facing vs business-facing, supporting vs critiquing) | Teams needing balanced coverage across quality dimensions |
| **Context-Driven Shape** | "Pyramid or Crab?" (Hillel Wayne, James Bach) | The optimal distribution depends on architecture, risk, and feedback cost | Microservices, event-driven systems, any non-trivial topology |

### Default Allocation by Project Type

| Project Type | Unit | Integration | E2E |
|-------------|------|-------------|-----|
| Library / SDK | 80% | 15% | 5% |
| Web API | 40% | 40% | 20% |
| Web application (UI-heavy) | 20% | 40% | 40% |
| CLI tool | 60% | 30% | 10% |
| Data pipeline | 50% | 40% | 10% |

These are defaults. Re-evaluate quarterly against escaped-defect data.

## Shift-Left AND Shift-Right

Effective strategy moves quality activities in **both** directions:

| Direction | Activities | Goal |
|-----------|-----------|------|
| **Shift-left** | Static analysis in IDE, unit tests on PR, contract tests before integration, spec testability review | Catch defects at lowest cost |
| **Shift-right** | Canary releases, feature-flag monitoring, production error budgets, chaos experiments | Validate assumptions under real conditions |

Shift-left reduces defect volume; shift-right validates that what survives left-side filtering actually works in production. Neither alone is sufficient.

## Cost-of-Failure Reasoning

Defects found later cost exponentially more to fix. Use this to justify test investment:

| Phase Found | Relative Cost | Example Activity |
|-------------|--------------|-----------------|
| Requirements / Design | 1× | Spec review, testability analysis |
| Implementation (PR) | 5–10× | Unit test failure, code review catch |
| Integration / Staging | 20–50× | Contract test failure, QA cycle |
| Production | 100×+ | Hotfix, rollback, customer impact, reputation |

**Decision rule:** Invest in testing up to the point where the marginal cost of one more test exceeds the expected cost of the defect it would catch earlier.

## Coverage as Diagnostic, Not Target

> **Gotcha — Coverage gaming:** Chasing a coverage percentage (e.g., "reach 90%") incentivizes writing tests that execute lines without asserting behavior. A suite at 95% line coverage with 40% mutation score is weaker than a suite at 75% coverage with 85% mutation score.

Use coverage as a **diagnostic signal**:
- Identify untested high-risk code (coverage gaps in payment/auth modules)
- Detect coverage regressions (a PR that drops branch coverage on changed files)
- Guide test design (what paths remain unverified?)

Do **not** use coverage as a pass/fail gate without mutation testing or escaped-defect correlation to validate test quality. See [test-automation.md](./test-automation.md) for mutation testing as a complement.

## Risk-Based Prioritization

| Priority | Coverage Required | Examples |
|----------|------------------|----------|
| Critical (P0) | Every path, every edge case | Payment processing, auth, data integrity |
| High (P1) | All happy paths + known failure modes | Core business logic, API contracts |
| Medium (P2) | Happy paths + common failure modes | Secondary features, non-critical APIs |
| Low (P3) | Smoke test only | UI polish, debug tooling |

For the full risk-scoring methodology (P×I matrix, workshops, register), see [risk-based testing](./risk-based-testing.md). For verification planning and evidence standards, see [verification-methodology](../../verification-methodology/SKILL.md).

## Test Estimation

Estimation is inherently uncertain; use heuristics to bound the range, then refine with historical data.

| Heuristic | Method | Typical Range |
|-----------|--------|---------------|
| **Test-to-dev effort ratio** | Test effort = dev effort × ratio | 0.25× (well-tested greenfield) to 0.5× (legacy, high-risk) |
| **Risk-weighted estimation** | Sum(P × I × test-design-hours) per risk item | Varies; prioritize P0/P1 items first |
| **Historical velocity** | Story points tested per sprint (trailing 3 sprints) | Use as capacity input, not commitment |
| **Percentage-of-development-time** | Allocate 20–40% of sprint capacity to test design + execution | Adjust based on automation maturity |

**Practical approach:** Start with ratio-based estimate, decompose by priority tier (P0 items get 3× the per-item budget of P3), then sanity-check against velocity history.

## Requirements-to-Test Traceability (RTM)

### Coverage Rule

Every requirement (user story, acceptance criterion, non-functional requirement) must map to **at least one** test case. Orphan tests (tests with no requirement mapping) must be flagged for review — they may test removed functionality.

### Traceability Matrix Structure

| Requirement ID | Description | Test Cases | Status | Owner |
|---------------|-------------|-----------|--------|-------|
| REQ-001 | User can reset password | TC-012, TC-013 | Pass | QA-1 |
| REQ-002 | Session expires after 30min idle | TC-045 | Pass | QA-2 |
| REQ-003 | Export CSV respects locale | — | **GAP** | — |

### Gap Detection and Action

- **Pre-release audit:** Run a traceability gap report before every release. Any requirement with zero mapped tests blocks release sign-off.
- **Continuous detection:** When requirements change (new AC added in sprint planning), flag unmapped requirements within 24 hours.
- **Orphan review:** Quarterly review of tests with no requirement link; retire tests for removed features, reassign tests whose requirements were restructured.

## Accessibility as a Quality Dimension

Accessibility testing is a quality dimension alongside functional, performance, and security testing — not an afterthought.

| Aspect | QA Responsibility | Delegated To |
|--------|------------------|-------------|
| When to test a11y | Strategy: include in P0/P1 coverage, gate on critical violations | — |
| WCAG 2.2 conformance level | Define target (AA for public-facing, A minimum) | [web-accessibility](../../web-accessibility/SKILL.md) |
| Automated scanning | Integrate axe-core or pa11y in CI as advisory gate | [web-accessibility](../../web-accessibility/SKILL.md) |
| Manual screen-reader testing | Schedule per release for P0 flows | [web-accessibility](../../web-accessibility/SKILL.md) |

**Integration point:** Add automated a11y scans to CI (advisory initially, blocking once baseline is clean). Track violation count as a quality metric alongside escaped defects.

## Composition Links

- Risk scoring methodology: [risk-based-testing.md](./risk-based-testing.md)
- Verification planning and evidence: [verification-methodology](../../verification-methodology/SKILL.md)
- Accessibility mechanics (WCAG conformance, ARIA, screen readers): [web-accessibility](../../web-accessibility/SKILL.md)
- Spec testability review (for AI-generated code): [spec-driven-development](../../spec-driven-development/SKILL.md)

---

*Sources: Kent C. Dodds (Testing Trophy, 2017), Lisa Crispin & Janet Gregory (Agile Testing Quadrants), Hillel Wayne / James Bach (context-driven testing), DORA State of DevOps Reports, WCAG 2.2 (W3C Recommendation 2023).*
