# Metric Tree Reference

A metric tree decomposes a product's primary outcome (often called the North Star) into a hierarchy of measurable, actionable, and owned sub-metrics. It is the single source of truth for "how we measure success."

## Structure

```
North Star (primary outcome)
├── Driver 1 (leading indicator)
│   ├── Sub-driver 1a
│   │   ├── Metric (owned by team X)
│   │   └── Countermetric (guardrail)
│   └── Sub-driver 1b
├── Driver 2 (lagging indicator)
│   └── ...
└── Driver 3 (leading indicator)
    └── ...
```

## Node Properties

Every node in the metric tree must satisfy four properties:

### 1. Observable

The metric can be measured from instrumentation or a defined data source. If no data source exists and none can be feasibly created, the metric is **not currently observable** — and must be rejected or marked as aspirational with a named constraint.

**Observability test:**
- Can you name the specific event(s) or data source that produces this metric?
- Can you write the SQL or analytics query that computes it?
- Can you trace the metric value on a dashboard back to raw events?

### 2. Actionable

A change in the metric suggests a specific product or operational response. If the metric moves and nobody knows what to do, it is not actionable.

**Actionability test:**
- If this metric drops 20%, what specific action does the team take?
- If this metric rises 20%, what does it tell you to do more of?

### 3. Owned

Exactly one team or role is accountable for the metric's definition, collection, interpretation, and accuracy. Shared ownership is no ownership.

**Ownership fields:**
- **Definition owner** — who decides what this metric means and when to change the definition.
- **Instrumentation owner** — who ensures the event fires correctly.
- **Consumer** — who uses this metric to make decisions.
- **On-call** — who gets paged when the data looks wrong.

### 4. Contextual

The metric's target, threshold, and interpretation depend on product type, market, stage, and business model. No universal benchmark applies.

**Context label format:** `[Product: <type> | Market: <type> | Stage: <stage> | Model: <model>]`

Example: `[Product: B2B SaaS | Market: mid-market | Stage: growth | Model: subscription]`

## Leading vs Lagging Indicators

| Property | Leading indicator | Lagging indicator |
|----------|------------------|-------------------|
| Timing | Changes before the outcome moves | Changes after the outcome moves |
| Sensitivity | High — responds quickly to product changes | Low — takes time to reflect changes |
| Use | Day-to-day decision making, experiment readouts | Strategic review, board reporting |
| Example | Feature adoption rate, activation completion | Quarterly revenue, annual retention |
| Risk | Noisy, may false-signal | Slow, may confirm a problem too late |

A healthy metric tree has both: leading indicators for fast feedback and lagging indicators for confirmation.

## Countermetrics (Guardrails)

Every metric that drives a decision must be paired with at least one countermetric — a metric that would reveal an adverse side effect of optimizing for the primary metric.

**Countermetric selection rules:**
1. The countermetric must detect a real, plausible harm — not a theoretical edge case.
2. The countermetric must have a defined threshold at which the primary metric optimization is paused or re-evaluated.
3. The countermetric must be owned by a different team than the primary metric when the primary metric's optimization creates a conflict of interest.

**Example pairs:**

| Primary metric | Countermetric | What it guards against |
|---------------|---------------|----------------------|
| New user signups | 30-day retention | Growth hacking that attracts users who churn |
| Feature adoption rate | Support ticket volume | Pushing adoption before the feature is stable |
| Time-to-value (decrease) | Activation quality score | Rushing onboarding at the expense of comprehension |
| Revenue per user (increase) | NPS or satisfaction | Monetization that degrades experience |
| Messages sent (increase) | Unsubscribe rate | Engagement maximization that drives users away |

## Measurability Gate

Before committing a metric to the tree, it must pass a measurability gate. A metric that fails is either rejected (with a named constraint) or marked as aspirational (tracked separately from operational metrics).

### Measurability assessment

| Question | Pass condition |
|----------|---------------|
| Is the data source identified? | A specific event, database table, or API is named. |
| Is the data source currently instrumented? | The data exists in production, or a feasible instrumentation plan exists. |
| Are identity and session semantics defined? | For user-level metrics: how users are identified across sessions, devices, and auth states is specified. |
| Can the metric be computed end-to-end? | The full pipeline from raw event to dashboard is traceable. |
| Is the metric stable under reasonable data quality issues? | Late-arriving data, duplicates, and nulls have defined handling. |

### Unmeasurable Metric Handling

When a metric fails the measurability gate:

1. **Name the constraint** — what specifically is missing (e.g., "no event fires when a user completes onboarding step 3," "identity resolution fails for users who sign in with SSO after starting anonymously").
2. **Do not fabricate a proxy** — do not substitute a different metric that "seems close." Record the gap honestly.
3. **If a proxy is explicitly requested**, define it with: (a) the exact formula, (b) the data source, (c) the known biases and gaps compared to the ideal metric, and (d) a plan to close the gap.

## Metric Tree Maintenance

The metric tree is a living artifact, not a one-time exercise:

- **Quarterly review** — is the North Star still the right primary outcome? Are all metrics still observable and actionable?
- **Metric deprecation** — when a metric is no longer used for decisions, retire it. Remove it from dashboards and stop instrumenting it.
- **Ownership refresh** — when teams reorganize, reassign metric ownership. An unowned metric is untrustworthy.
- **Countermetric audit** — verify that every decision-driving metric still has a valid countermetric and that countermetric thresholds have not been silently ignored.

## Examples (Contextual)

### Example 1: B2B SaaS Collaboration Tool
**Context:** `[Product: B2B SaaS | Market: mid-market | Stage: growth | Model: subscription]`

```
North Star: Weekly Active Teams
├── Team Activation (leading)
│   ├── % teams with ≥3 members completing core action within 7 days
│   ├── Time-to-first-collaboration (days)
│   └── Countermetric: Support tickets per activated team
├── Team Engagement Depth (leading)
│   ├── Avg collaborative actions per team per week
│   ├── % teams using ≥2 features
│   └── Countermetric: Feature confusion rate (clicks-to-undo ratio)
└── Team Retention (lagging)
    ├── 90-day team retention rate
    ├── Expansion revenue per retained team
    └── Countermetric: Contraction rate (% teams downgrading)
```

### Example 2: Internal Developer Platform
**Context:** `[Product: Internal tool | Market: enterprise-internal | Stage: adoption | Model: productivity]`

```
North Star: Developer Time Saved
├── Onboarding Speed (leading)
│   ├── Time-to-first-deploy for new service (minutes)
│   ├── % services using platform defaults vs custom config
│   └── Countermetric: Deployment failure rate
├── Daily Workflow Efficiency (leading)
│   ├── Median CI pipeline duration (minutes)
│   ├── % builds that pass on first attempt
│   └── Countermetric: Build queue wait time
└── Platform Satisfaction (lagging)
    ├── Developer NPS (quarterly survey)
    ├── % teams voluntarily on platform (not mandated)
    └── Countermetric: Shadow IT incidents (services deployed outside platform)
```

### Example 3: Public Digital Service
**Context:** `[Product: Public service | Market: government-citizen | Stage: mature | Model: service-delivery]`

```
North Star: Successful Outcome Rate
├── Access (leading)
│   ├── % applications started that are completed
│   ├── Completion rate by device type (mobile vs desktop)
│   └── Countermetric: Support call volume (calls indicate access failure)
├── Timeliness (leading)
│   ├── Median time-to-decision (days)
│   ├── % decisions within service standard
│   └── Countermetric: Error rate on expedited applications
└── Equity (lagging)
    ├── Outcome rate by demographic segment
    ├── % eligible population using the service
    └── Countermetric: Appeals rate (indicates incorrect decisions)
```
