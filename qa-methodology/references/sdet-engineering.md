# SDET Engineering

## Definition and Distinction

An SDET (Software Development Engineer in Test) is an engineer whose **product is test infrastructure** — frameworks, tooling, pipelines, and platforms that enable the entire organization to verify software quality efficiently.

What an SDET is NOT:
- **Not "a tester who codes":** A manual tester who learned Selenium is not an SDET. Writing scripts that automate existing manual steps produces brittle, low-value automation.
- **Not "a developer who tests":** A developer who writes unit tests for their own code is practicing good development hygiene, not building test infrastructure for others.

The SDET's customers are other engineers. Success is measured by how effectively the organization can detect defects, not by how many tests the SDET personally writes.

## Competency Model: 7 Habits (Angie Jones)

| # | Habit | Core Practice |
|---|-------|--------------|
| 1 | **Be intentional** | Automate selectively aligned to goals, not "all the things" |
| 2 | **Enhance development skills** | OOP, design patterns, clean code — not just API syntax |
| 3 | **Enhance testing skills** | Balance developer and tester mindsets; verify behavior, not just execution |
| 4 | **Explore new tools** | Match tools to contexts; never force one tool on every problem |
| 5 | **Automate throughout the tech stack** | Use seams at unit/service/API layers; UI automation sparingly |
| 6 | **Collaborate** | Strategy requires input from exploratory testers, developers, and product |
| 7 | **Automate beyond the tests** | Data generation, environment setup, log parsing — remove repetitive toil |

Source: Angie Jones, "7 Habits of Highly Effective SDETs" (angiejones.tech, 2018).

## gTAA / TAF Layered Architecture

The generic Test Automation Architecture (gTAA) organizes test infrastructure as layers with clear responsibilities:

```
┌─────────────────────────────────────────┐
│  Layer 5: Test Reporting & Analytics    │  Dashboards, trend analysis, flake metrics
├─────────────────────────────────────────┤
│  Layer 4: Test Execution & Orchestration│  CI runners, parallelism, sharding, retry policy
├─────────────────────────────────────────┤
│  Layer 3: Test Scripts / Scenarios      │  Business-readable test cases, data-driven flows
├─────────────────────────────────────────┤
│  Layer 2: Test Services / Utilities     │  API clients, page objects, data factories, auth helpers
├─────────────────────────────────────────┤
│  Layer 1: Core Framework / Adapters     │  Driver management, config, logging, plugin system
└─────────────────────────────────────────┘
```

**Key principle:** Higher layers depend on lower layers, never the reverse. Test scripts (L3) never import driver internals (L1) directly.

## Design Patterns for Test Code

### Page Object Model (POM)

Encapsulates UI structure behind a semantic interface. Tests interact with page meaning, not selectors.

```python
class CheckoutPage:
    def __init__(self, page):
        self._page = page
        self._submit = page.locator('[data-testid="checkout-submit"]')

    def complete_order(self, card: str) -> OrderConfirmation:
        self._page.fill('[name="card"]', card)
        self._submit.click()
        return OrderConfirmation(self._page)
```

### Flow Model

Models multi-page user journeys as composable transitions. Each step returns the next page state, enabling type-safe navigation chains.

```python
confirmation = (
    HomePage(page)
    .search("widget")
    .select_result(0)
    .add_to_cart()
    .checkout(card="4111...")
)
assert confirmation.is_successful()
```

Flow Model complements POM: POM encapsulates single pages; Flow Model composes them into end-to-end journeys.

### SOLID Applied to Test Code

| Principle | Test Code Application |
|-----------|----------------------|
| **S**ingle Responsibility | One test class per feature area; one assertion concept per test |
| **O**pen/Closed | Extend test data via fixtures, not by modifying shared helpers |
| **L**iskov Substitution | Any test-double must be swappable for the real dependency without test changes |
| **I**nterface Segregation | Page objects expose only methods relevant to their page (no god-objects) |
| **D**ependency Inversion | Tests depend on abstractions (interfaces), not concrete driver implementations |

## Build vs. Buy Decision Framework

### Decision Criteria

| Criterion | Favors BUILD | Favors BUY/ADOPT |
|-----------|-------------|-----------------|
| Team size | > 5 SDETs maintaining infra | < 3 engineers |
| Longevity | Custom needs persist 2+ years | Needs may shift within 12 months |
| Integration surface | Deep internal system hooks (custom protocols) | Standard web/API/mobile |
| Maintenance cost tolerance | Org can fund ongoing maintenance | Prefer vendor/community maintenance |
| TCO (3-year) | Custom amortizes below commercial | Commercial license < build + maintain |

### Decision Table

| Scenario | Recommendation |
|----------|---------------|
| Standard web E2E, < 5 engineers | Adopt Playwright/Cypress |
| Custom protocol (IoT, proprietary binary) | Build adapter layer atop open framework |
| High-scale parallelism + custom reporting at > 20 teams | Build orchestration; adopt execution engines |
| Mobile-only, small team | Adopt Appium/Detox |
| Uncertain requirements, < 12 months horizon | Adopt; revisit when needs stabilize |

> **Gotcha — NIH syndrome:** Building a custom framework "because none fit perfectly" when an existing tool covers 90% of needs wastes months. Extend, don't replace.

## Testability Engineering

### Designing Systems for Testability

| Technique | Mechanism | Example |
|-----------|-----------|---------|
| **Dependency Injection** | Inject collaborators via constructor/parameter | `OrderService(repo: Repository, clock: Clock)` |
| **Architectural seams** | Boundaries where behavior can be altered without editing | Interface between service and external gateway |
| **Observability hooks** | Expose internal state for verification | Health endpoints, debug headers, structured logs |

### Test-Double Selection Criteria

| Double Type | Use When | Avoid When |
|------------|----------|-----------|
| **Stub** | You need canned return values; no interaction verification | You need to verify call sequences |
| **Mock** | Verifying interactions (was X called N times?) | Over-mocking creates brittle coupling to implementation |
| **Fake** | You need working behavior without external cost (in-memory DB, local SMTP) | Behavior diverges from production over time |

**Selection rule:** Default to stubs for data, fakes for stateful collaborators, mocks only for interaction-critical boundaries. Never mock value objects.

## CI/CD Integration

### Multi-Level Pipeline Architecture

| Level | Trigger | Contents | Time Budget |
|-------|---------|----------|-------------|
| **L1: Pre-merge** | Every PR | Unit + fast integration + lint + type-check | < 5 min |
| **L2: Post-merge** | Merge to main | Full integration + contract tests + E2E smoke | < 15 min |
| **L3: Scheduled** | Nightly / weekly | Full E2E + performance + soak + mutation | < 60 min |

### Configuration Management

Test configuration (URLs, credentials, feature flags) lives in environment-specific config, never hardcoded. Use layered config: defaults → environment overrides → CI secrets.

### Contract Testing

Consumer-driven contracts (e.g., Pact) verify service boundaries independently of full integration:
- Consumer defines expectations → publishes contract
- Provider verifies against contract in its own CI
- Breaks are caught before deployment, not during integration testing

## Test Data and Environment Self-Service

| Capability | Implementation Pattern |
|-----------|----------------------|
| **Data on demand** | Factory/builder functions generating valid entities per test |
| **Environment provisioning** | Ephemeral environments via containers (Docker Compose, k8s namespaces) |
| **State isolation** | Each test owns its data; no shared mutable database state |
| **Self-service portal** | Engineers spin up test environments without SRE ticket |

## Observability and Shift-Right

| Technique | QA Application |
|-----------|---------------|
| **Correlation IDs** | Trace a user journey across microservices; reproduce failures from production traces |
| **Canary releases** | Deploy to 1–5% traffic; monitor error rates before full rollout; auto-rollback on SLO breach |
| **Feature flags** | Gate risky features; enable targeted regression testing in production; kill-switch without deploy |

Shift-right does not replace shift-left. It validates that pre-merge testing caught what matters, and feeds escaped-defect data back into suite evolution.

## Flakiness and Reliability Engineering

**Core principle: Test code is production code.** It deserves the same review, ownership, and SLA expectations as application code.

### Flakiness Triage (Flakinator-Style)

| Step | Action |
|------|--------|
| 1. Detect | Statistical flake scoring: Bayesian analysis of pass/fail patterns over N runs |
| 2. Classify | Root cause category: timing/race, resource contention, test-order dependency, external service |
| 3. Quarantine | Remove from blocking path; track in dashboard with owner and SLA |
| 4. Fix or delete | Owner resolves within 5 business days or deletes the test |
| 5. Burn-in | 20+ consecutive green runs before re-enabling as blocking |

### The ~18-Month Decay Rule

Test suites without active maintenance decay: flake rates climb, false confidence accumulates, and developer trust erodes. Budget ~20% of test infrastructure capacity for ongoing maintenance. If an organization cannot sustain this, adopt fewer, higher-value tests rather than a large neglected suite.

Source: Google Testing Blog, "Flaky Tests at Google and How We Mitigate Them" (2016); Atlassian Engineering, "Taming Test Flakiness with Flakinator" (2025).

## Career Progression

| Stage | Focus | Scope |
|-------|-------|-------|
| Junior SDET | Learn framework, write tests under guidance | Task |
| Senior SDET | Own a product area's test infrastructure | Project |
| Staff SDET | Set test architecture standards across teams | Product |
| Principal SDET | Multi-year QE vision; industry contribution | Org |

For detailed leveling mechanics, promotion packets, and archetypes, see [qa-career-levels.md](./qa-career-levels.md).

## Emerging AI Dimensions

| Dimension | Current State (2025–2026) | QA Implication |
|-----------|--------------------------|----------------|
| **Self-healing tests** | Tools auto-update selectors on UI changes (Healenium, Applitools) | Reduces maintenance burden but masks real UI regressions if unchecked |
| **AI log analysis** | LLM-assisted root-cause analysis of CI failures | Accelerates triage; requires validation against deterministic signals |
| **Agentic testing pyramids** | AI agents generate and execute test scenarios autonomously | QA role shifts to strategy, oracle design, and verifying agent-generated test quality |

> **Gotcha — AI-generated tests without oracle verification:** An agent that generates 500 tests asserting nothing is worse than 50 well-designed tests. Always verify that AI-generated tests have meaningful assertions and kill mutants.

## Decision Table: SDET Scope Choices

| Question | If YES | If NO |
|----------|--------|-------|
| Is the team > 5 engineers maintaining test infra? | Invest in layered gTAA | Adopt existing framework directly |
| Does the system have custom protocols? | Build adapter layer | Use standard tool |
| Are flake rates > 5%? | Prioritize reliability engineering over new tests | Continue balanced investment |
| Is AI-generated code > 50% of PRs? | Add mutation testing + independent verification gates | Standard review sufficient |

**Exit condition:** You are done applying this reference when you can identify the appropriate gTAA layers for your system, make a build-vs-buy recommendation with documented criteria, and establish a flake-management SLA for your team's test suite.

## Worked Example: Build vs. Buy for an API-First Startup

**Context:** 8-person startup, 3 backend services, REST + gRPC, no dedicated QA. Team needs E2E confidence.

| Criterion | Assessment |
|-----------|-----------|
| Team size | 3 engineers touching tests → favors BUY |
| Integration surface | Standard REST + gRPC → no custom protocol |
| Longevity | Product-market fit uncertain; needs may pivot in 12 months |
| TCO | Playwright + pytest adoption: 2 weeks. Custom framework: 3 months + ongoing |

**Recommendation:** Adopt Playwright (API testing) + pytest (unit/integration). Add contract testing (Pact) at service boundaries when team reaches 12+ engineers. Revisit build-vs-buy at 2-year mark if custom orchestration needs emerge.

## Composition Links

- Career levels, promotion packets, archetypes: [qa-career-levels.md](./qa-career-levels.md)
- Test automation patterns (parallelism, ML selection): [test-automation.md](./test-automation.md)
- Flaky quarantine workflow details: [test-automation.md](./test-automation.md)
- Quality metrics and gate design: [quality-gates-and-metrics.md](./quality-gates-and-metrics.md)

---

*Sources: Angie Jones, "7 Habits of Highly Effective SDETs" (angiejones.tech, 2018); Google Testing Blog, "Flaky Tests at Google" (testing.googleblog.com, 2016); Atlassian Engineering, "Taming Test Flakiness with Flakinator" (2025); Lisa Crispin & Janet Gregory, Agile Testing (2009); Gerard Meszaros, xUnit Test Patterns (2007); Pact Foundation (docs.pact.io); Will Larson, Staff Engineer (2020).*
