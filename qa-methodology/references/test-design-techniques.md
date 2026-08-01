# Test Design Techniques

Systematic methods for deriving test cases from specifications. Load when designing test cases for a specific feature, choosing which technique fits a scenario, or reviewing test coverage gaps. Not for test strategy allocation (that's [test-strategy.md](./test-strategy.md)) or exploratory discovery (that's [exploratory-testing.md](./exploratory-testing.md)).

## Technique Overview

| Technique | Input Model | Strength | Weakness |
|-----------|------------|----------|----------|
| Equivalence Partitioning (EP) | Input domains | Reduces test count with representative coverage | Misses boundary defects |
| Boundary Value Analysis (BVA) | Numeric/ordered ranges | Catches off-by-one, overflow, edge behavior | Only useful at boundaries |
| Decision Tables | Business rules with conditions | Complete combinatorial logic coverage | Explosion with many conditions |
| State Transition | Stateful workflows | Catches invalid transitions, dead states | Requires accurate state model |
| Pairwise / Combinatorial | Multi-parameter configurations | Covers all 2-way interactions with O(n log n) tests | Misses 3+ way interactions |
| Error Guessing | Experience, defect history | Finds "obvious" bugs fast | Unsystematic; depends on tester skill |

## Equivalence Partitioning (EP)

Divide the input domain into classes where behavior should be identical. Test one representative from each class.

### Worked Example: Age Field (0–120, integer)

| Partition | Range | Representative | Expected |
|-----------|-------|---------------|----------|
| Invalid (below) | < 0 | -1 | Reject |
| Valid (child) | 0–12 | 6 | Accept, category=child |
| Valid (adult) | 13–64 | 30 | Accept, category=adult |
| Valid (senior) | 65–120 | 70 | Accept, category=senior |
| Invalid (above) | > 120 | 121 | Reject |
| Invalid (type) | non-integer | "abc", 3.5 | Reject |

5 tests instead of 121 exhaustive values. Each partition's representative exercises the same code path as all other members.

## Boundary Value Analysis (BVA)

Defects cluster at boundaries. Test the values adjacent to partition edges.

### 2-Value vs 3-Value BVA

| Approach | Values Tested | When to Use |
|----------|--------------|-------------|
| **2-value** (edge) | min, max | Quick coverage; most defects are at the boundary itself |
| **3-value** (edge + just outside) | min-1, min, max, max+1 | When off-by-one is likely; stronger assurance |

### Worked Example: Order Quantity (1–999)

| Value | Type | Expected |
|-------|------|----------|
| 0 | Below minimum (3-value) | Reject |
| 1 | Minimum boundary | Accept |
| 999 | Maximum boundary | Accept |
| 1000 | Above maximum (3-value) | Reject |

Add EP representatives for interior partitions (e.g., 500) if behavior differs within the range.

## Decision Tables

When business logic depends on combinations of conditions, a decision table ensures every combination is tested.

### Worked Example: Discount Rules

| Condition | Rule 1 | Rule 2 | Rule 3 | Rule 4 |
|-----------|--------|--------|--------|--------|
| Premium member? | Y | Y | N | N |
| Order > $100? | Y | N | Y | N |
| **Action** | 20% off | 10% off | 5% off | 0% |

4 rules from 2 binary conditions (2² = 4). Each rule becomes at least one test case.

### Managing Complexity

| Conditions | Rules | Strategy |
|-----------|-------|----------|
| ≤ 4 | ≤ 16 | Full decision table |
| 5–8 | 32–256 | Collapse don't-care combinations; use pairwise for remaining |
| > 8 | 256+ | Pairwise testing (below) + risk-based selection |

## State Transition Testing

Model the system as states + transitions. Test every valid transition and verify that invalid transitions are rejected.

### Worked Example: Order Lifecycle

```
[Created] --pay--> [Paid] --ship--> [Shipped] --deliver--> [Delivered]
    |                 |                                    |
    +--cancel--> [Cancelled] <--cancel-- [Paid]           +--return--> [Returned]
```

| Test | Path | Expected |
|------|------|----------|
| Happy path | Created → Paid → Shipped → Delivered | Success at each step |
| Cancel from Created | Created → Cancelled | Order voided, no charge |
| Cancel from Paid | Paid → Cancelled | Refund issued |
| Invalid: ship unpaid | Created → Shipped (attempt) | Reject; state unchanged |
| Invalid: pay cancelled | Cancelled → Paid (attempt) | Reject; state unchanged |
| Return path | Delivered → Returned | Return processed |

**Coverage criteria:** at minimum, cover every state (0-switch) and every transition (1-switch). For critical workflows, cover 2-switch (pairs of consecutive transitions).

## Pairwise (Combinatorial) Testing

When parameters interact, full combinatorial testing explodes (e.g., 5 params × 4 values = 1024 tests). Pairwise covers every pair of parameter values in far fewer tests.

### Tool: PICT

PICT (Microsoft) generates pairwise test sets from a model file:

```
# model.txt — PICT format
OS:      Windows, macOS, Linux
Browser: Chrome, Firefox, Safari
Network: WiFi, Cellular, Offline
Locale:  en-US, de-DE, ja-JP
```

```bash
pict model.txt > pairwise-tests.txt
# Produces ~12–15 tests covering all pairs (vs 81 exhaustive)
```

### When Pairwise Is Sufficient

| Interaction Depth | Technique | Test Count |
|-------------------|-----------|-----------|
| 1-way (each value) | EP representatives | N |
| 2-way (all pairs) | Pairwise / all-pairs | O(N log N) |
| 3-way (all triples) | t-wise (t=3) | O(N² log N) |
| N-way (exhaustive) | Full combinatorial | Product of all values |

Most defects are triggered by 1- or 2-way interactions (empirical evidence from NIST studies). Pairwise is the default; escalate to t=3 only for high-risk configuration surfaces.

## Error Guessing

Systematic intuition: use defect history, code complexity, and experience to target likely failure points.

### Structured Error-Guessing Checklist

| Category | Examples to Try |
|----------|----------------|
| Empty / null inputs | `""`, `null`, `undefined`, `[]`, `{}` |
| Extreme values | MAX_INT, empty string, 10MB upload, 0-length list |
| Special characters | Unicode, emoji, SQL metacharacters, path separators |
| Concurrency | Double-submit, back-button during save, parallel edits |
| Timing | Midnight boundary, DST transition, leap second, month-end |
| State corruption | Kill process mid-write, network drop during transaction |
| Permission edges | Read-only filesystem, expired token, revoked role |

**Error guessing complements systematic techniques** — run it after EP/BVA/decision tables to catch what structured methods miss.

## When to Use Which Technique

| Scenario | Primary Technique | Secondary | Rationale |
|----------|-------------------|-----------|-----------|
| Numeric input field with ranges | BVA (3-value) | EP | Boundaries are the highest-yield targets |
| Form with many optional fields | Pairwise (PICT) | EP for each field | Interactions between fields cause most form bugs |
| Business rules with 2–4 conditions | Decision table | EP for each condition value | Complete logic coverage with manageable size |
| Stateful workflow (order, ticket, session) | State transition | Error guessing (invalid transitions) | Invalid transitions are the #1 stateful bug class |
| API with enum parameters | EP | Pairwise if multiple enums | Each enum value is a partition |
| Legacy code with defect history | Error guessing | BVA on known-problem fields | History predicts future defect locations |
| Configuration matrix (OS × browser × env) | Pairwise | — | Exhaustive is infeasible; pairs catch most bugs |

### Technique Selection Flowchart

```
Is the input numeric or ordered?
  YES → BVA + EP
  NO  → Does behavior depend on condition combinations?
          YES → ≤ 4 conditions? → Decision table
                 > 4 conditions? → Pairwise
          NO  → Is the system stateful?
                  YES → State transition
                  NO  → EP + error guessing
```

## Level-Mapping Guidance

These techniques apply at any test level (unit, integration, E2E). The following mapping is a **typical starting point** — adapt to your context:

| Technique | Typical Level | Adaptation Note |
|-----------|--------------|-----------------|
| EP / BVA | Unit (input validation) | Also applies at integration (API contracts) and E2E (form validation) |
| Decision tables | Unit / integration | Business rules often span services; test at integration level |
| State transition | Integration / E2E | Workflow state is usually service-level, not function-level |
| Pairwise | E2E / system | Configuration surfaces are system-wide |
| Error guessing | Any level | Most valuable at integration and E2E where interactions emerge |

> **Note:** This is a heuristic default, not a prescription. A state machine inside a single function is best tested at unit level; a simple input boundary may be best caught by an integration test. Context determines placement, not technique identity. See [test-strategy.md](./test-strategy.md) for the pyramid-as-heuristic framing.

## Gotchas

> **Gotcha — EP without boundary testing:** Equivalence partitioning alone misses off-by-one errors at partition edges. Always pair EP with BVA on numeric or ordered inputs.

> **Gotcha — Decision table explosion:** Adding a 5th binary condition doubles the table. Before adding conditions, ask: does this condition independently affect the outcome? If not, collapse it.

> **Gotcha — Pairwise as a substitute for understanding:** Pairwise generates combinations but doesn't tell you what's wrong. You still need oracles (expected results) for every generated test. A pairwise suite without assertions is just coverage theater.

## Exit Condition

You are done applying this reference when: (1) each testable input or behavior is assigned a primary technique, (2) boundary values are tested for all numeric/ordered inputs, (3) stateful workflows have transition coverage (at least 1-switch), and (4) configuration matrices use pairwise reduction rather than exhaustive enumeration.

## Composition Links

- Test strategy and allocation by risk tier: [test-strategy.md](./test-strategy.md)
- Exploratory testing for areas where techniques don't yet apply: [exploratory-testing.md](./exploratory-testing.md)
- Risk-based prioritization of which areas get exhaustive design: [risk-based-testing.md](./risk-based-testing.md)
- Test automation of designed cases: [test-automation.md](./test-automation.md)

---

*Sources: ISTQB Foundation Level Syllabus 2023 (test design techniques), PICT (Microsoft, github.com/microsoft/pict), NIST pairwise studies (Kuhn et al., 2004), Cem Kaner et al. "Lessons Learned in Software Testing" (Wiley, 2002), Rex Black "Managing the Testing Process" (Wiley, 2009).*
