# Benefits dependency and tranche control

**Applicability:** Load when a program's value depends on several components, changed behavior, staged releases, or benefits that mature after delivery.

## Benefits dependency map

A benefit is not a feature and a component output is not a benefit. Map the causal chain:

`program capability -> required operational change -> changed behavior -> benefit or disbenefit -> measure`

For each link record its owner, evidence, assumption, dependency, timing, and failure consequence. Mark links as observed, inferred, asserted, or committed. A benefit with no accountable owner, baseline, data source, or review trigger is an unvalidated hypothesis.

Check whether the components are jointly necessary, whether another dependency is required, and whether one component creates a disbenefit for another stakeholder. Do not count activity, adoption, or delivery percentages as benefits without a causal and measurement argument.

## Tranche and release decisions

Use tranches when the program can deliver a useful capability or learn enough to change the next investment decision before every component is complete. Each tranche needs:

- a bounded capability and intended benefit;
- entry evidence and a named decision owner;
- integration, operational, adoption, and safety evidence;
- a benefit hypothesis and early signal;
- exit choices: continue, reshape, pause, stop, or transfer;
- dependencies and conditions for the next tranche.

A tranche is not permission to weaken mandatory approval, security, safety, or release gates. Coordinate tranche timing with component projects, but do not force every component into the same cadence.

## Benefit drift and disbenefits

Review expected versus observed outcomes at the program level. If an output ships but the benefit does not move, test the missing link: adoption, process, incentive, data, capability, operating ownership, or the original causal assumption. Track negative consequences such as workload, cost, service degradation, control burden, or displacement of other outcomes. Give the accountable owner options to mitigate, accept, compensate, reshape, or stop.

## Boundaries

Route roadmap sequencing and investment choices to [product-roadmapping-and-portfolio](../product-roadmapping-and-portfolio/SKILL.md); route measurement design to [product-analytics-and-measurement](../product-analytics-and-measurement/SKILL.md); route adoption intervention to [product-adoption](../product-adoption/SKILL.md); route organizational structure to [org-design](../org-design/SKILL.md). This skill owns the cross-component causal map, tranche decision, and handoffs among those specialists.
