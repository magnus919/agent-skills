# Test Strategy

> Fill in each section for the target project or feature. Replace `<...>` placeholders with concrete values. Delete guidance notes once populated.

## Context

| Field | Value |
|-------|-------|
| Project / Feature | <name> |
| Version / Release | <version or release identifier> |
| Author | <author> |
| Date | <YYYY-MM-DD> |
| Status | Draft / In Review / Approved |

### Scope

<What is in scope for this strategy? List the components, features, or services under test.>

### Out of Scope

<What is explicitly excluded and why?>

## Risk Tiers

Assign each area a risk tier (P0–P3) using probability × impact scoring. See [risk-based-testing.md](../references/risk-based-testing.md) and [assets/risk-matrix-grid.md](../assets/risk-matrix-grid.md) for the scoring grid.

| Area / Component | Probability (1–5) | Impact (1–5) | Score | Tier |
|------------------|--------------------:|-------------:|------:|------|
| <area 1> | | | | P0 / P1 / P2 / P3 |
| <area 2> | | | | P0 / P1 / P2 / P3 |
| <area 3> | | | | P0 / P1 / P2 / P3 |

### Tier Definitions

| Tier | Score Range | Coverage Approach |
|------|-------------|-------------------|
| P0 — Critical | 20–25 | Exhaustive: every path, every edge case |
| P1 — High | 12–19 | All happy paths + known failure modes |
| P2 — Medium | 6–11 | Happy paths + common failure modes |
| P3 — Low | 1–5 | Smoke test only; defer detailed testing |

## Test Levels

| Level | What It Covers | Framework / Tool | Target Coverage by Tier |
|-------|---------------|-----------------|------------------------|
| Unit | <e.g., business logic, validators> | <framework> | P0: ___% / P1: ___% / P2: ___% / P3: ___% |
| Integration | <e.g., API contracts, service boundaries> | <framework> | P0: ___% / P1: ___% / P2: ___% / P3: ___% |
| End-to-End | <e.g., critical user journeys> | <framework> | P0: ___% / P1: ___% / P2: ___% / P3: ___% |
| Exploratory | <e.g., new features, unknown-risk areas> | SBTM charter | Sessions per sprint: ___ |

> The pyramid shape is a heuristic, not dogma. Adjust level allocation to match your system's risk profile. See [test-strategy.md](../references/test-strategy.md).

## Coverage Approach

| Dimension | How It Is Measured | Diagnostic Target | Notes |
|-----------|--------------------|-------------------|-------|
| Code coverage | <tool> | <e.g., 80% line on P0 modules> | Coverage is diagnostic, not a goal |
| Requirement coverage | <traceability matrix / RTM> | Every AC has ≥ 1 test | |
| Risk coverage | <risk register mapping> | Every P0/P1 risk has tests | |
| Mutation score | <tool, e.g., PIT/Stryker/mutmut> | <target % on critical paths> | Optional; measures test effectiveness |

## Environment

| Environment | Purpose | Data Strategy | Access |
|-------------|---------|---------------|--------|
| <e.g., local / CI> | <unit + integration> | <fixtures / factories> | <who> |
| <e.g., staging> | <integration + E2E> | <masked subset / synthetic> | <who> |
| <e.g., perf> | <load / soak> | <generated at scale> | <who> |

> Never use production PII in test environments. See [test-data-management.md](../references/test-data-management.md).

## Execution Plan

| Phase | What Runs | Trigger | Cadence |
|-------|-----------|---------|---------|
| Pre-merge | <unit + lint + fast integration> | PR opened / updated | Every PR |
| Post-merge | <full integration + E2E> | Merge to main | Every merge |
| Nightly | <full regression + perf smoke> | Scheduled | Daily |
| Release | <full suite + exploratory + security scan> | Release candidate | Per release |

## Automation Targets

| Area | Current State | Target State | Priority |
|------|--------------|--------------|----------|
| <area 1> | <manual / partial / automated> | <target> | P0 / P1 / P2 / P3 |
| <area 2> | <manual / partial / automated> | <target> | P0 / P1 / P2 / P3 |

## Exit Criteria

The test strategy is complete when:

- [ ] Every in-scope area has a risk tier assigned (P0–P3)
- [ ] Test level allocation is defined per tier
- [ ] Coverage dimensions and diagnostic targets are set
- [ ] Environment and data strategy are specified
- [ ] Execution cadence is agreed with the team
- [ ] Automation targets have owners and timelines
- [ ] Exit criteria for each tier are defined below

### Per-Tier Exit Criteria

| Tier | Exit Criteria |
|------|--------------|
| P0 | <e.g., 100% path coverage, zero open critical defects, mutation score ≥ ___%> |
| P1 | <e.g., all happy paths + failure modes pass, zero open high defects> |
| P2 | <e.g., happy paths pass, known issues documented> |
| P3 | <e.g., smoke suite green> |
