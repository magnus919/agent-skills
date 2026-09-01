# Go-to-Market Decision Workflow

Use this workflow when a launch, channel, or segment choice must be made rather than when operating a CRM pipeline.

## Repeatable Method

1. **Frame inputs:** target segment, job/pain, alternatives, price and margin, capacity, cash horizon, channel hypotheses, and confidence for each assumption.
2. **Generate options:** compare segment/channel pairs using pain fit, reachable demand, proof access, expected payback, and operational readiness. Record unknowns instead of inventing them.
3. **Decide with gates:** choose a primary motion only when a named ICP, message, acquisition signal, owner, budget cap, and 30/60/90-day success thresholds exist. Otherwise run a bounded discovery test.
4. **Validate:** instrument activation, qualified demand, conversion, gross-margin payback, retention, and qualitative objections. Review weekly; stop or revise when a guardrail is breached.
5. **Package evidence:** write `00-index.md`, assumptions, decision log, channel model, experiment results, and next review date. Use `artifact-pyramids` for durable evidence structure.

## Worked Example

A compliance automation startup compares fintech, healthcare, and manufacturing. Fintech wins the first beachhead because existing references and integrations support a 90-day launch, while healthcare requires unvalidated privacy integrations. The decision is: spend $30k on two fintech reference accounts and partner-led demand for one quarter; do not enter healthcare until two paid pilots, security review time under 30 days, and 40% gross-margin payback evidence exist. A weekly dashboard records qualified opportunities, activation, CAC estimate, and retention assumptions.

## Reusable Artifact

```text
GTМ decision memo
Decision / owner / date / review date
ICP and painful job:
Alternatives and differentiator:
Options considered and evidence:
Assumptions (confidence + test):
Budget and payback guardrail:
90-day milestones and stop rules:
Evidence links and unresolved questions:
```

## Routing Matrix

| Need | Route to | Handoff in / out |
|---|---|---|
| Corporate strategy or market portfolio | [strategy-frameworks](../../strategy-frameworks/SKILL.md) | GTM hypothesis in; strategic choice out |
| CAC, LTV, margin, or cash model | [financial-modeling](../../financial-modeling/SKILL.md) | Channel inputs in; economics and sensitivity out |
| Technology feasibility | [technology-radar](../../technology-radar/SKILL.md) | Integration hypothesis in; evaluated options out |
| Launch delivery plan | [implementation-planning](../../implementation-planning/SKILL.md) | Chosen motion in; sequenced work out |
| Evidence packaging | [artifact-pyramids](../../artifact-pyramids/SKILL.md) | Decision log in; durable index out |
| Pipeline records or stage changes | [crm](../../crm/SKILL.md) | Qualified signal in; confirmed CRM state out |

Do not create a new market or growth sibling: route an uncovered concern to the closest owner and record the boundary.
