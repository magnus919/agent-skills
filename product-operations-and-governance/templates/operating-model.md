# Product Operating Model

> Fill this template to configure a complete product operating model. Replace every `[fill: ...]` marker. This is a governance configuration artifact — it describes how decisions are made, not what decisions are made.

## Operating Mode

- **Mode:** [fill: lightweight / high-assurance]
- **Rationale:** [fill: why this mode fits this product — cite regulatory obligations, team size, risk profile, or compliance requirements]

## Governance Pattern

- **Selected pattern:** [fill: single-accountable-owner / product-council / tiered-review / delegated-authority-with-escalation]
- **Adaptations from the base pattern:** [fill: any customizations — e.g., "product council with tie-breaking vote from CPO" or "tiered review where Tier 1 (low-risk) skips synchronous review"]

## Scope

- **Product or portfolio covered:** [fill: name and brief description]
- **Teams / groups included:** [fill: which teams fall under this operating model]
- **Teams / groups explicitly excluded:** [fill: adjacent teams not governed by this model — e.g., "platform infrastructure team (has separate operating model)"]

## Decision Rights Summary

> Detailed map in `decision-rights-map.md`. Summarize key assignments here.

| Decision type | Accountable owner (role) | Consulted | Informed |
|---------------|--------------------------|-----------|----------|
| Intake accept/reject | [fill] | [fill] | [fill] |
| Portfolio prioritization | [fill] | [fill] | [fill] |
| Roadmap commitment | [fill] | [fill] | [fill] |
| Experiment proceed/stop | [fill] | [fill] | [fill] |
| Launch go/no-go | [fill] | [fill] | [fill] |
| Lifecycle continue/invest/harvest/retire | [fill] | [fill] | [fill] |

## Review Cadences

> Detailed configuration in `review-cadence.md`. Summarize frequency here.

| Review | Frequency | Mode-specific notes |
|--------|-----------|---------------------|
| Intake / Opportunity | [fill] | [fill] |
| Portfolio | [fill] | [fill] |
| Roadmap | [fill] | [fill] |
| Experiment | [fill] | [fill] |
| Launch | [fill] | [fill] |
| Lifecycle / Health | [fill] | [fill] |

## Evidence Standards

- **Default evidence classification:** All artifacts distinguish observed, inferred, asserted, and committed.
- **Lightweight minimums (if applicable):** [fill: e.g., "problem statement + one qualitative or quantitative signal for intake"]
- **High-assurance minimums (if applicable):** [fill: e.g., "statistical evidence + risk analysis + compliance sign-off for launch"]

## Escalation Path

- **Tier 1 (product-level resolution):** [fill: who resolves contested decisions within the product team]
- **Tier 2 (cross-product or portfolio-level):** [fill: who resolves when Tier 1 cannot — e.g., product council, CPO]
- **Tier 3 (executive):** [fill: who resolves when the decision exceeds product authority — e.g., CEO, board]

## Exception and Escalation Records

- **Exception records stored at:** [fill: path, wiki link, or registry location]
- **Escalation records stored at:** [fill: path, wiki link, or registry location]
- **Review cadence for open exceptions:** [fill: how often outstanding exceptions are revisited]

## Version

- **Version:** [fill: date or semver]
- **Last reviewed:** [fill: date]
- **Next review:** [fill: date or trigger]
