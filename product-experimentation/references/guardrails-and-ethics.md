# Guardrails and Ethics

Every experiment must define guardrails, ethical boundaries, stopping rules, and decision ownership before it starts. A statistically significant result with a failing guardrail is a no-ship.

## Guardrail Metrics

Guardrails are mandatory safety metrics that can stop the experiment regardless of the primary outcome. Every experiment must name at least one guardrail metric.

### Minimum Required Guardrails

| Guardrail | What it catches | Example threshold |
|-----------|----------------|-------------------|
| **Error rate** | The variant introduces bugs or regressions | Error rate must not increase by more than X% relative to control |
| **Latency / performance** | The variant degrades user experience through slowness | p95 latency must not increase by more than Y ms |
| **Domain-specific harm** | The variant causes harm specific to the domain (e.g., unhealthy engagement, financial loss, privacy violation) | Defined per experiment |

Additional guardrails may be required depending on the domain: revenue/cost impact, support-ticket volume, churn rate, accessibility regression, or security-signal changes.

### Guardrail Design Principles

1. **Guardrails are not the primary metric.** They are safety checks, not success measures.
2. **Guardrails are monitored continuously, not checked at the end.** If a guardrail breaches at any point, the experiment stops.
3. **Guardrails are directional.** You must specify the direction of concern (increase, decrease, or both) and the threshold.
4. **A missing guardrail is a design defect.** If you cannot name at least one guardrail, the experiment is not ready to run.

### Harmful Guardrail Omission Example

An experiment tests a new recommendation algorithm with the primary metric "engagement time." No error-rate guardrail is defined. The algorithm increases engagement by 15% (p < 0.01) but also increases server errors by 400% because it triggers an untested code path. Without the error-rate guardrail, the ship decision proceeds on statistical evidence alone. **This is a no-ship** — the guardrail omission invalidates the decision. The correct action: withhold the ship decision, define the missing guardrail, and re-run with proper safety monitoring.

## Ethical Boundaries

### User Consent

- Is the experiment transparent to users? If not, is the deception justified and minimal?
- Does the experiment comply with the product's terms of service and privacy policy?
- For medical, financial, or vulnerable-population contexts: is institutional review (IRB or equivalent) required?

### Data Minimization

- Is the experiment collecting only the data needed to answer the hypothesis?
- Are identifiers minimized or pseudonymized?
- Is there a data retention and deletion plan?

### Vulnerable Populations

- Does the experiment population include children, elderly users, or other groups requiring special protection?
- Are there power dynamics (employer/employee, provider/patient) that make consent problematic?

### Institutional Alignment

- Does the experiment design align with the organization's stated values and commitments?
- Would a reasonable user feel misled or exploited if they understood the experiment?

## Stopping Rules

Define when the experiment stops — for any reason, not just completion.

### Types of Stopping Rules

| Rule | Trigger | Action |
|------|---------|--------|
| **Guardrail breach** | Any guardrail metric exceeds its threshold | Stop immediately; investigate; no ship decision until resolved |
| **Sufficiency** | The evidence is strong enough to decide (e.g., Bayesian posterior probability exceeds threshold, or sequential test boundary is crossed) | Stop and decide; do not continue collecting data "just to be sure" |
| **Futility** | It is extremely unlikely the experiment will reach a decision with the remaining budget | Stop and record as inconclusive; do not waste sample |
| **Time cap** | A calendar deadline is reached regardless of evidence | Stop and decide with available evidence; record the uncertainty |
| **External event** | A product change, incident, or business decision makes the experiment irrelevant | Stop and record the reason |

## Decision Ownership

Every experiment must name who decides and what inputs they consider.

### Decision Authority

- **Owner:** a named individual (not a team or committee) who makes the final ship/no-ship call.
- **Informed by:** the experiment readout, but not bound by it. The owner may override the statistical recommendation with documented reasoning.

### Decision Inputs (Multiple Criteria)

Statistical significance is one input among several. The decision owner must consider:

1. **Statistical evidence** — effect size, confidence/credible interval, and whether the experiment was adequately powered. Route to data-scientist.
2. **Practical significance** — is the effect large enough to matter for the business or user?
3. **Guardrail evidence** — all guardrails must pass. A guardrail failure blocks the ship decision regardless of statistical evidence.
4. **Qualitative evidence** — user feedback, support tickets, usability observations that contextualize the numbers.
5. **Reversibility** — if we are wrong, how hard is it to undo? A reversible change can tolerate more uncertainty.
6. **Opportunity cost** — what else could we build with the same effort?

A statistically significant result that exceeds authority boundaries (safety, compliance, ethics, or domain authority) is a no-ship regardless of other criteria.
