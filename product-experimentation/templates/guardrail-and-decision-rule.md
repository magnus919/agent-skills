# Guardrail and Decision Rule Record

Record the guardrails, stopping rules, and decision authority for an experiment. This document must be completed and reviewed before the experiment starts.

## Experiment Reference

- **Experiment name:**
- **Experiment brief:** (link)
- **Date:**

## Guardrail Metrics

Every experiment must define at least one guardrail metric. Record the metric, threshold, direction, and the action taken if the threshold is breached.

| # | Guardrail metric | Direction | Threshold | Action on breach | Monitoring frequency |
|---|-----------------|-----------|-----------|-----------------|---------------------|
| 1 | Error rate | Increase | +X% over control | Stop experiment, investigate | Continuous |
| 2 | p95 latency | Increase | +Y ms over control | Stop experiment, investigate | Continuous |
| 3 | (domain-specific) | | | | |

**Guardrail omission check:** If any row above is empty and no domain-specific guardrail is defined, the experiment is not ready. At minimum, error rate must be monitored.

## Stopping Rules

| Rule | Condition | Action |
|------|-----------|--------|
| Guardrail breach | Any guardrail exceeds threshold | Stop immediately; no ship until resolved |
| Sufficiency | Evidence strong enough to decide (e.g., posterior > 0.95) | Stop and decide |
| Futility | Unlikely to reach decision with remaining budget | Stop and record inconclusive |
| Time cap | Calendar deadline reached | Stop and decide with available evidence |
| External event | Product change or incident makes experiment irrelevant | Stop and record reason |

## Decision Authority

- **Decision owner:** (name of individual, not team)
- **Backup decision owner:** (if primary is unavailable)
- **Decision inputs required:**
  - [ ] Statistical evidence (from data-scientist)
  - [ ] Guardrail evidence (all guardrails must pass)
  - [ ] Practical significance assessment
  - [ ] Qualitative evidence (if applicable)
  - [ ] Reversibility assessment
- **Escalation path:** (who to escalate to if decision owner cannot decide)

## Ethical Review

- [ ] User consent model documented
- [ ] Data minimization confirmed
- [ ] Vulnerable population check completed
- [ ] Institutional alignment confirmed
- [ ] Ethical concerns documented (if any):

## Sign-Off

- **Experiment owner:** _____ Date: _____
- **Decision owner:** _____ Date: _____
- **Data/science review (if applicable):** _____ Date: _____
