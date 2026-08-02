# Product Outcome Review Template

A recurring review that ties product measurements back to decisions. Run monthly (recommended) or at whatever cadence matches the product's decision rhythm. This is not a status update — it is a deliberate inspection of whether the metrics are telling the truth and whether the team is acting on what they say.

## Review Header

| Field | Value |
|-------|-------|
| **Product** | _[fill: product name]_ |
| **Review date** | _[fill: date]_ |
| **Review period** | _[fill: e.g. January 2026]_ |
| **Participants** | _[fill: names and roles]_ |
| **Facilitator** | _[fill: name]_ |

## 1. North Star Health

_[fill: Current North Star value and trend. Is it moving in the intended direction? At what rate?]_

| Metric | Current value | Previous period | Change | Trend | Context label |
|--------|--------------|----------------|--------|-------|---------------|
| _[North Star]_ | _[fill]_ | _[fill]_ | _[fill: absolute and %]_ | _[up/down/flat]_ | _[Product/Market/Stage/Model]_ |

**Assessment:** _[fill: Is the North Star healthy? Is it still the right North Star?]_

## 2. Metric Tree Health

_[fill: For each node in the metric tree, record current value, target, and trend.]_

| Metric | Current | Target | Trend | Owner | Action status |
|--------|---------|--------|-------|-------|--------------|
| _[Driver 1]_ | _[fill]_ | _[fill]_ | _[up/down/flat]_ | _[team]_ | _[on-track / needs-attention / critical]_ |
| _[Sub-driver 1a]_ | _[fill]_ | _[fill]_ | _[up/down/flat]_ | _[team]_ | _[on-track / needs-attention / critical]_ |
| ... | ... | ... | ... | ... | ... |

**Largest positive mover:** _[fill: which metric improved most, and why?]_

**Largest negative mover:** _[fill: which metric declined most, and why?]_

## 3. Countermetric Audit

_[fill: For each primary metric that drives a decision, verify that its countermetric has not crossed the guardrail threshold.]_

| Primary metric | Countermetric | Countermetric value | Threshold | Status |
|---------------|---------------|-------------------|-----------|--------|
| _[metric]_ | _[counter]_ | _[value]_ | _[threshold]_ | _[ok / warning / breached]_ |

**Breached guardrails:** _[fill: Any countermetric that crossed its threshold. What action is taken?]_

## 4. Decision Log

_[fill: What decisions were made in this review period based on metric signals? What was the outcome of decisions made in the previous review period?]_

| Decision | Date | Trigger metric(s) | Expected outcome | Actual outcome | Learning |
|----------|------|-------------------|-----------------|----------------|---------|
| _[decision]_ | _[date]_ | _[metrics that informed it]_ | _[expected]_ | _[actual]_ | _[what we learned]_ |

## 5. Instrumentation Health

_[fill: Summary of instrumentation QA status. Any events with data quality issues? Any new events added? Any events deprecated?]_

| Check | Status |
|-------|--------|
| New events QA'd and approved this period | _[fill: count and list]_ |
| Events with data quality alerts this period | _[fill: count and list]_ |
| Deprecated events pending removal | _[fill: count and list]_ |
| Tracking plan version | _[fill: current version]_ |

## 6. Metric Deprecation and Retirement

_[fill: Any metrics that are no longer used for decisions? Any dashboards that should be retired?]_

| Metric / Dashboard | Reason for deprecation | Retirement date | Consumer notification |
|--------------------|-----------------------|-----------------|----------------------|
| _[name]_ | _[why]_ | _[date]_ | _[teams notified]_ |

## 7. Measurement Gaps and Requests

_[fill: What would the team like to measure but cannot currently? What instrumentation constraints need investment to resolve?]_

| Gap | Constraint | Estimated effort | Priority |
|-----|-----------|-----------------|---------|
| _[desired measurement]_ | _[missing instrumentation, data source, or identity resolution]_ | _[effort]_ | _[P0-P3]_ |

## 8. Next Period Actions

_[fill: Concrete actions for the next review period, with owners.]_

| Action | Owner | Due |
|--------|-------|-----|
| _[action]_ | _[person/team]_ | _[date]_ |

## Review Sign-Off

| Role | Name | Date |
|------|------|------|
| Product owner | _[name]_ | _[date]_ |
| Engineering lead | _[name]_ | _[date]_ |
| Data / analytics lead | _[name]_ | _[date]_ |
