# Risk-Based Testing

Prioritize test effort by risk. Load when deciding where to invest limited testing time, building a risk register, or running a risk assessment workshop. For the broader strategy context (pyramid shape, shift-left/right), see [test-strategy.md](./test-strategy.md).

## Risk = Probability × Impact

Every test decision is a risk decision made implicitly. Make it explicit:

```
Risk Score = Probability (1–5) × Impact (1–5)
```

| Score Range | Zone | Action |
|-------------|------|--------|
| 20–25 | **Critical** (P0) | Test exhaustively; every path, every edge case |
| 12–19 | **High** (P1) | Test all happy paths + known failure modes |
| 6–11 | **Medium** (P2) | Test happy paths + common failure modes |
| 1–5 | **Low** (P3) | Smoke test only; defer detailed testing |

These priority tiers (P0–P3) align with the coverage tiers in [test-strategy.md](./test-strategy.md). A P0 risk item demands P0-level coverage; a P3 risk item justifies smoke-only testing.

## 5×5 Risk Matrix

| P \ I | 1 — Negligible | 2 — Minor | 3 — Moderate | 4 — Major | 5 — Catastrophic |
|-------|----------------|-----------|--------------|-----------|-------------------|
| **5 — Almost Certain** | 5 (P3) | 10 (P2) | 15 (P1) | 20 (P0) | 25 (P0) |
| **4 — Likely** | 4 (P3) | 8 (P2) | 12 (P1) | 16 (P0) | 20 (P0) |
| **3 — Possible** | 3 (P3) | 6 (P2) | 9 (P2) | 12 (P1) | 15 (P1) |
| **2 — Unlikely** | 2 (P3) | 4 (P3) | 6 (P2) | 8 (P2) | 10 (P2) |
| **1 — Rare** | 1 (P3) | 2 (P3) | 3 (P3) | 4 (P3) | 5 (P3) |

### Scoring Guidance

| Rating | Probability Anchor | Impact Anchor |
|--------|--------------------|---------------|
| 5 | Will fail in production within a quarter (or has already) | Data loss, security breach, revenue stoppage |
| 4 | Expected to fail within a year | Major feature outage, SLA breach |
| 3 | Could fail; uncertain | Degraded experience, workaround exists |
| 2 | Unlikely given current controls | Cosmetic, minor inconvenience |
| 1 | Extremely unlikely; well-understood code | No user-visible impact |

## Risk Assessment Workshop

Run a structured workshop to score risks collaboratively. Solo scoring introduces individual bias; group calibration produces defensible priorities.

### Participants

- QA lead (facilitator)
- Engineering leads for affected areas
- Product manager (impact calibration)
- Operations / SRE representative (production context)

### Agenda (90 minutes)

| Time | Activity |
|------|----------|
| 0–15 min | Identify risk items: what could go wrong? (brainstorm from change log, incident history, architecture) |
| 15–50 min | Score each item: probability (group vote, median), impact (product calibrates) |
| 50–65 min | Rank and assign priority tiers (P0–P3) from the matrix |
| 65–80 min | Define mitigations: what tests, who owns them, by when |
| 80–90 min | Agree reassessment triggers and next review date |

### Calibration Rule

If probability votes span > 2 points, the facilitator asks the highest and lowest voter to state their evidence. Re-vote once. Record dissent in the register.

## Risk Register Structure

| Column | Description | Example |
|--------|-------------|---------|
| ID | Unique identifier | RISK-012 |
| Risk Description | What could go wrong | Payment gateway timeout during peak |
| Component | Affected system area | Checkout service |
| Probability (1–5) | Likelihood of occurrence | 4 |
| Impact (1–5) | Severity if it occurs | 5 |
| Score | P × I | 20 |
| Priority Tier | P0–P3 (from matrix) | P0 |
| Mitigation / Test Plan | What testing addresses this | Load test at 2× peak; chaos inject timeout |
| Owner | Who implements the mitigation | QA-2 |
| Status | Open / Mitigating / Closed | Mitigating |
| Last Reviewed | Date of last reassessment | 2025-07-15 |
| Reassessment Trigger | What event re-opens this | Payment provider API change |

## Reassessment Triggers

Risk is not static. Re-score the register when any trigger fires:

| Trigger | Rationale |
|---------|-----------|
| Production incident in the area | Actual failure updates probability upward |
| Architecture change (new dependency, refactor) | Changes both probability and impact landscape |
| New regulatory requirement | May raise impact (compliance penalty) |
| Major release or migration | New failure modes introduced |
| Quarterly calendar review | Prevents register staleness (default cadence) |
| Team change (key engineer leaves) | Knowledge gaps raise probability |
| Customer escalation | Business impact may have changed |

## Cost-of-Failure Reasoning

Risk-based testing investment is justified by the cost differential between catching a defect early vs late:

| Detection Phase | Relative Fix Cost | Risk-Based Justification |
|----------------|-------------------|--------------------------|
| Design / Spec review | 1× | Highest-leverage test: risk workshop catches design flaws |
| Unit / PR testing | 5–10× | P0/P1 items justify exhaustive unit coverage |
| Integration / Staging | 20–50× | Contract and integration tests for cross-boundary risks |
| Production | 100×+ | Shift-right monitoring for residual P0 risk |

**Decision rule:** Allocate test effort proportional to risk score. A P0 item (score 20–25) receives 3–5× the per-item test design budget of a P3 item (score 1–5).

## Test Estimation Heuristic

Estimate test effort from the risk register:

```
total_test_hours = Σ (risk_items_in_tier × hours_per_tier)

Hours per tier (default):
  P0: 8–16 hours per risk item (exhaustive design + automation)
  P1: 4–8 hours per risk item
  P2: 2–4 hours per risk item
  P3: 0.5–1 hour per risk item (smoke only)
```

**Adjustment factors:** multiply by 1.5× for legacy/unfamiliar code, 0.7× for well-automated areas with existing coverage.

### Worked Example

A release has 3 P0 risks, 5 P1 risks, 8 P2 risks, and 12 P3 risks:

| Tier | Items | Hours/Item | Subtotal |
|------|-------|-----------|----------|
| P0 | 3 | 12 | 36 |
| P1 | 5 | 6 | 30 |
| P2 | 8 | 3 | 24 |
| P3 | 12 | 0.75 | 9 |
| **Total** | **28** | — | **99 hours** |

With a 2-person QA team (80 hours/sprint), this release requires ~1.25 sprints of test design effort. Negotiate scope or add capacity for P0 items; P3 items can be deferred.

## Gotchas

> **Gotcha — Static register:** A risk register written once at project start and never updated is fiction. Reassess on triggers (above) and at minimum quarterly. A stale register misallocates effort toward risks that no longer exist.

> **Gotcha — Consensus theater:** If the workshop rubber-stamps the loudest voice's scores without evidence, the register is political, not analytical. Require evidence anchors for every score. Record dissent.

> **Gotcha — Full suite on every PR regardless of risk:** Running everything on every change wastes CI minutes and trains teams to ignore results. Use risk tiers to gate test selection (P0 always runs; P3 runs nightly).

## Exit Condition

You are done applying this reference when: (1) a risk register exists with scored items mapped to P0–P3 tiers, (2) test allocation is proportional to risk scores, (3) reassessment triggers are defined with a calendar backstop, and (4) the estimation heuristic produces a capacity-checked plan.

## Composition Links

- Broader test strategy and pyramid shape: [test-strategy.md](./test-strategy.md)
- Regression suite tiering by risk: [regression-testing.md](./regression-testing.md)
- Quality gate design (blocking vs advisory per tier): [quality-gates-and-metrics.md](./quality-gates-and-metrics.md)
- Verification planning and evidence standards: [verification-methodology](../../verification-methodology/SKILL.md)

---

*Sources: ISO/IEC 25010 (systems and software quality requirements), ISTQB Foundation Level Syllabus 2023 (risk-based testing chapter), James Bach (context-driven testing, risk heuristics), Kaner/Bach/Pettichord "Lessons Learned in Software Testing" (Wiley, 2002), DORA State of DevOps Reports (cost-of-failure data).*
