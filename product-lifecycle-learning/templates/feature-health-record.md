# Feature Health Record

Assess feature health across multiple dimensions. Do not reduce to a single score or traffic-light
color. Each dimension has its own evidence, confidence, and trend.

## Feature Identity

| Field | Value |
|---|---|
| Feature / capability name | |
| Assessment date | |
| Assessor | |
| Prior health record date | |

## Health Dimensions

### 1. Adoption Health

| Metric | Value | Confidence | Trend (over 3 cycles) | Threshold for concern |
|---|---|---|---|---|
| Activation rate | | | Improving / Stable / Declining | |
| Time-to-value (median) | | | | |
| Feature discovery rate | | | | |
| Sustained use (DAU/WAU/MAU as appropriate) | | | | |
| Cohort retention (30/60/90-day) | | | | |

**Adoption health summary:** (narrative, with evidence)

### 2. Technical Health

| Metric | Value | Confidence | Trend | Threshold for concern |
|---|---|---|---|---|
| Error rate | | | | |
| P95/P99 latency | | | | |
| Availability (uptime %) | | | | |
| Known bugs (open, by severity) | | | | |
| Dependency freshness (outdated deps) | | | | |

**Technical health summary:** (narrative, with evidence)

### 3. Operational Health

| Metric | Value | Confidence | Trend | Threshold for concern |
|---|---|---|---|---|
| Support ticket volume | | | | |
| Time-to-resolution (median) | | | | |
| Alert frequency (false positives, actionable) | | | | |
| On-call burden (pages per week) | | | | |
| Documentation freshness | | | | |

**Operational health summary:** (narrative, with evidence)

### 4. Strategic Health

| Factor | Assessment | Evidence |
|---|---|---|
| Alignment with current strategy | Strong / Moderate / Weak | |
| User need confirmed | Yes / Partial / No | |
| Competitive differentiation | Strong / Moderate / Weak / None | |
| Revenue or value contribution | | |
| Replacement or alternative exists | Yes / Partial / No | |

**Strategic health summary:** (narrative, with evidence)

## Cross-Dimension Patterns

Are there correlations or conflicts across dimensions? (e.g., "High adoption but declining
technical health — investment in reliability needed" or "Strong strategic alignment but no
adoption — discovery or positioning problem")

## Overall Assessment

- **Strongest dimension:**
- **Weakest dimension:**
- **Most concerning trend:**
- **Most improved since last assessment:**
- **Recommended lifecycle decision direction:** (continue / improve / harvest / pivot / pause / retire — preliminary, to be confirmed by the formal decision record)
