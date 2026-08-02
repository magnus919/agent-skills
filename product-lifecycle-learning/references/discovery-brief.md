# Discovery Brief — Product Lifecycle Learning

Bounded discovery for issue #194. Maps existing skill landscape relevant to
post-launch outcome review, feature health, assumption updates, retirement,
and retained learning.

## Existing Material Survey

| Skill | Relationship |
|---|---|
| `product-strategy` | Upstream. Defines lifecycle stages and decision-log concepts. Lifecycle-learning operationalizes the closure phase. |
| `product-roadmapping-and-portfolio` | Sibling. Sets strategic bets and roadmap priorities. Lifecycle-learning feeds evidence back into roadmap re-evaluation. |
| `product-analytics-and-measurement` | Sibling. Owns instrumentation and metric definitions. Lifecycle-learning consumes analytics outputs as input. |
| `product-adoption` | Sibling. Owns adoption diagnostics, activation, and sustained-use review. Lifecycle-learning consumes adoption evidence and feeds pattern changes back. |
| `product-experimentation` | Sibling. Owns experiment design and readout. Lifecycle-learning consumes experiment results and feeds new hypotheses. |
| `spec-driven-development` | Sibling. Owns specifications and acceptance criteria. Lifecycle-learning compares expected (from spec) against observed. |
| `site-reliability-engineering` | Sibling. Owns operational reliability and incident response. Lifecycle-learning consumes incident signals as input. |
| `product-methodology` | Sibling. Provides prioritization frameworks. Lifecycle-learning does not re-derive these. |

## Gaps This Skill Fills

| Gap | Response |
|---|---|
| No skill closes the launch-to-learning loop systematically | Full loop defined in SKILL.md: observe → compare → gap analysis → assumption update → health assessment → decide → retain learning → feed back |
| No systematic comparison of expected vs. observed outcomes | Epistemic discipline taxonomy in [epistemic-discipline.md](epistemic-discipline.md); outcome review template |
| No assumption ledger update methodology | Assumption ledger update template with confidence shifts |
| No feature health assessment that avoids single-score reduction | Multi-dimensional feature health record template |
| No structured retirement lifecycle covering deprecation, migration, customer treatment, and internal cleanup | Retirement lifecycle reference + sunset plan template |
| No skill produces a durable retained learning record rather than a transient meeting summary | Retained learning record template |
| No skill routes lifecycle evidence back to roadmap, analytics, adoption, experimentation, and specifications | Feedback destinations reference with explicit routing per decision type |

## Ownership Boundaries

**OWNS:** Post-launch outcome review, expected-vs-observed comparison with epistemic categories,
assumption ledger updates, feature health assessment, lifecycle decisions
(continue/improve/harvest/pivot/pause/retire), retirement lifecycle execution (deprecation
communication, migration paths, customer treatment during sunset, internal cleanup), durable
retained learning artifacts, feedback routing to downstream skills.

**Does NOT own:** Incident postmortems or root-cause analysis (routes to incident-learning
and site-reliability-engineering), analytics instrumentation or metric pipeline design (routes
to product-analytics-and-measurement), customer-success account management or health scoring
(routes to conditional-customer-success), roadmap prioritization or portfolio allocation (routes
to product-roadmapping-and-portfolio), experiment design or statistical analysis (routes to
product-experimentation and data-scientist), specification authoring (routes to
spec-driven-development).

## Retirement Decision Discipline

Retirement decisions require human judgment and named accountability. This skill never applies
automated thresholds like "retire if DAU < 100" or "kill if NPS < 30." Every retirement
decision must include: the accountable human decision-maker, the evidence considered, the
context (product, market, alternatives, user base), and the rationale. The retirement-decision
template enforces this contract.

## Routing Design

Five mandatory feedback destinations: roadmap, analytics, adoption, experimentation, and
specifications. Two conditional destinations: customer-success (for retirement communication
and migration coordination) and incident-learning (for incident-driven signals). See
[feedback-destinations.md](feedback-destinations.md).

Prose references to skills not yet landed: `conditional-customer-success` (same-wave issue
#192, dir not yet on main) and `incident-learning` (later milestone-2 issue, not yet landed).
Real relative links to existing directories: product-analytics-and-measurement,
product-roadmapping-and-portfolio, product-adoption, product-experimentation,
spec-driven-development.
