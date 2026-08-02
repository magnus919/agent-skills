# Privacy and Human Judgment Boundaries

This reference defines the non-negotiable privacy and human-judgment
boundaries that govern every customer-success artifact and practice. These
boundaries apply regardless of product model, account tier, or CS team
structure.

## 1. Customer Feedback Must Not Become Surveillance

### Consent Framework

- Feedback is collected with explicit consent and a stated purpose.
- Consent is granular: a customer consenting to health-review data sharing
  has not consented to behavior tracking for other purposes.
- Consent is revocable. When revoked, existing aggregate data may be retained
  (cannot be un-aggregated), but new individual-level collection stops.
- Consent records are maintained alongside feedback records.

### Usage Limitation

- Data is used only for the purpose stated at collection.
- Repurposing customer feedback for unrelated product decisions (e.g., using
  support-call sentiment to score adoption without the customer's knowledge)
  is prohibited.
- Aggregate pattern detection is permitted; individual-level behavior tracking
  beyond the stated purpose is not.

### Data Minimization

- Only the data necessary for the stated purpose is collected.
- Customer-identifiable data is never embedded in templates shared outside the
  CS team (handoff records use anonymized or aggregated signals).
- Cross-team sharing is scoped to the minimum necessary for the receiving
  team's purpose.

### Surveillance-Risk Guidance

If a proposed health signal or feedback mechanism could reasonably be
perceived as surveillance by the customer, it must pass three checks before
proceeding:

1. **Consent check**: Has the customer explicitly consented to this specific
   data collection for this specific purpose?
2. **Proportionality check**: Is the data collected proportional to the
   benefit the customer receives?
3. **Alternative check**: Is there a less invasive way to achieve the same
   evidence?

If any check fails, the mechanism must not proceed.

## 2. Health Scores Are Decision-Support, Not Automated Decisions

### Evidence, Not Scores

- Every health dimension records a **signal** (observable evidence), not a
  score.
- Signals include: source, trend direction, recency, and confidence.
- Multiple signals per dimension are expected. Conflicting signals are
  surfaced, not averaged into a single score.

### No Automated Actions

- A health signal never triggers an automated action (no auto-churn, no
  auto-escalation, no auto-renewal, no auto-expansion).
- Every action requires a human decision, informed by the health evidence.
- Automated alerts ("review needed") are permitted; automated decisions
  ("account downgraded") are not.

### Conflicting Signals Must Be Surfaced

- When one signal indicates healthy and another indicates at-risk for the
  same dimension, both are recorded.
- The health record includes a "conflict note" explaining the disagreement
  and proposing a resolution path (e.g., "adoption signals are strong but
  support-ticket volume has doubled — investigate whether growth is causing
  onboarding gaps").
- The resolution path requires a human decision, not an algorithmic
  tiebreaker.

### Confidence and Provenance

- Every signal includes a confidence assessment: high (directly observed,
  recent, multiple sources agree), medium (indirect proxy, moderate recency),
  or low (stale, single source, or proxy with known limitations).
- Every signal includes provenance: where the data came from, when it was
  collected, and who collected it.

## 3. Human Judgment Is Required for Escalation Decisions

### Escalation Gate Requirements

Every escalation path must define:

1. **Trigger signal and threshold**: What evidence triggers the escalation.
2. **Named decision-maker**: A role (not a system) responsible for the
   decision.
3. **Decision options**: What the decision-maker can decide (with minimum
   viable options defined — never a single forced path).
4. **Evidence package**: What evidence accompanies the escalation.
5. **Decision deadline**: When the decision must be made by.
6. **Fallback**: What happens if no decision is made by the deadline (escalate
   further, never auto-act).

### No-Devision Fallback

A "no decision" state has a defined fallback: escalate further to the next
level of authority. The fallback must never be "auto-act" or "do nothing
silently."

### Escalation Records

Every escalation decision is recorded:
- What was escalated, by whom, on what evidence.
- What decision was made, by whom, on what date.
- What action followed.

Escalation records are reviewable by the CS team and, in redacted form, by
the customer.

## 4. Privacy Boundaries Around Customer Data

### Data Classification

Customer data handled by CS practice falls into three tiers:

| Tier | Examples | Sharing Rule |
|---|---|---|
| **Account-identifiable** | Customer name, company, contract terms | CS team only; never in cross-team templates |
| **Anonymized signal** | "Account in healthcare sector, adoption rate 62%, trend declining" | Shareable with product/support/engineering |
| **Aggregate pattern** | "3 of 12 healthcare accounts show declining adoption" | Shareable broadly |

### Cross-Team Sharing Rules

- Product team receives: anonymized or aggregate health evidence,
  feature-request patterns, adoption signals. Never receives: individual
  customer identities, contract details, or commercial terms.
- Support team receives: escalation records with account context necessary
  for resolution. Receives account identity only when required and only for
  the specific support interaction.
- Engineering team receives: defect records with anonymized account-impact
  assessment. Never receives customer identity unless the defect requires
  account-specific reproduction and the customer has consented.

### Data Retention

- Customer-success records follow the product's data-retention policy.
- When a customer relationship ends, health/risk records are archived.
- Archived records are retained for the period defined by the retention
  policy (for pattern analysis) and then deleted.
- Success plans and QBR records are retained for the customer relationship
  duration plus the retention period.

### Access Control

- CS team members have access to the full customer record.
- Cross-team access is granted on a need-to-know basis, scoped to the
  specific purpose and duration.
- Access is logged and auditable.

## 5. Boundary Enforcement

### Pre-Flight Checklist

Before any customer-success artifact is created or shared, verify:

- [ ] Consent: Has the customer consented to this data collection and use?
- [ ] Purpose: Is the data used only for the stated purpose?
- [ ] Minimization: Is only the minimum necessary data collected/shared?
- [ ] Human gate: Does every action require a human decision?
- [ ] No surveillance: Would the customer reasonably perceive this as
  surveillance? If uncertain, apply the three-check test.
- [ ] Privacy tier: Is the data classified at the correct tier for the
  intended recipient?

### Violation Response

If a boundary is violated:

1. Stop the violating practice immediately.
2. Record what happened, what data was affected, and who was impacted.
3. Notify the CS team lead and, if customer data was exposed, the customer.
4. Update the boundary or process to prevent recurrence.
5. Do not resume the practice until the fix is verified.

This is not a punitive framework — it is a recovery framework. The goal is
to restore the boundary, not to assign blame.
