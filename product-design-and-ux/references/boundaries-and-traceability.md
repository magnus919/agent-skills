# Boundaries and Traceability

## Pipeline Boundary

| Concern | Owner | This skill receives or produces |
|---|---|---|
| Obtain and validate human evidence | `product-discovery` | Validated needs, evidence links, limitations, unresolved assumptions. |
| Decide scope, priority, and rationale | `product-methodology` | Chosen outcome, scope boundary, decisions, and success measures. |
| Define user-facing behavior | This skill | IA, task/state models, interface contracts, usability evidence, and handoff. |
| Accessibility conformance depth | `web-accessibility` | Routed requirements and its implementation/testing evidence. |
| Formal software specification and gates | `spec-driven-development` | Approved interaction contracts and observable acceptance criteria. |

Do not replace discovery with invented research, reopen an approved scope through prioritization, issue a WCAG conformance claim, or prescribe visual implementation.

## Traceability Method

Assign stable identifiers to evidence (`E-01`), outcomes (`O-01`), decisions (`D-01`), tasks (`T-01`), contracts (`IC-01`), and acceptance criteria (`AC-01`). For each decision, record the source, confidence or limitation, affected role, and what would change it. A claim without evidence is an assumption; name its owner and resolution gate.

Read `templates/outcomes-to-design.md` when creating the trace. The trace is complete when a reviewer can move both directions: outcome to interface behavior, and interface behavior to evidence or an explicit open decision.

## Accessibility Routing

Carry requirements such as keyboard reachability, focus outcome, accessible name/role/state expectations, text alternatives, reflow, and error recovery into contracts. For exact criterion applicability, semantics selection, ARIA, browser/AT evidence, or conformance claims, link the work to [web-accessibility](../../web-accessibility/SKILL.md) rather than summarizing standards here.
