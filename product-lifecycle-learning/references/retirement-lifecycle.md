# Retirement Lifecycle

When the lifecycle decision is Retire, a structured retirement lifecycle covers the full path
from deprecation announcement through internal cleanup and learning closure. This reference
defines each phase, its required outputs, and its routing.

## Phase Overview

```
DEPRECATION ANNOUNCEMENT → MIGRATION PATH → CUSTOMER TREATMENT → INTERNAL CLEANUP → LEARNING CLOSURE
```

## Phase 1: Deprecation Communication

**Goal:** Inform affected users that the feature will be retired, with clear timeline, rationale,
and alternatives.

**Required outputs:**
- Deprecation announcement with target retirement date
- Rationale: why the feature is being retired (evidence-backed, not opinion)
- Affected-user segmentation: which users or cohorts are impacted, and how
- Alternative or replacement path: what users should use instead
- Timeline: announcement date, end-of-life date, end-of-support date, removal date
- Communication channels: in-product notice, email, documentation, support portal

**Template:** Use [../templates/sunset-plan.md](../templates/sunset-plan.md).

**Routing:** Coordinate communication plans with `conditional-customer-success` for
customer-facing execution, especially for enterprise and B2B products where customer
relationships are managed.

## Phase 2: Migration Path

**Goal:** Provide existing users with a clear, supported path to an alternative.

**Required outputs:**
- Migration guide: step-by-step instructions for moving to the replacement
- Data export: format, instructions, timeline, support contact
- Compatibility window: how long the old feature remains usable during migration
- Migration tooling: automated migration scripts, import tools, API compatibility shims
- Migration support: dedicated support channel, FAQs, office hours for enterprise accounts

**Template:** Use [../templates/sunset-plan.md](../templates/sunset-plan.md).

**Principles:**
- The migration path must be documented before the deprecation announcement, not after.
- Data export must be complete, lossless, and in an open or documented format.
- The compatibility window must be long enough for users to migrate — context-dependent,
  never a one-size-fits-all deadline.
- Enterprise and B2B users may need extended migration windows and dedicated support.

## Phase 3: Customer Treatment During Sunset

**Goal:** Treat affected users with respect and transparency during the transition.

**Required outputs:**
- Support commitment: what support is available during the sunset window, and at what SLA
- Grace period: how long users have before the feature is removed, with clear milestones
- Data export guarantee: users can export their data until the removal date
- Refund or credit policy: if applicable, how paid users are compensated
- Escalation path: how users can request extensions or exceptions

**Template:** Use [../templates/sunset-plan.md](../templates/sunset-plan.md).

**Routing:** Customer-treatment strategy routes to `conditional-customer-success` for account-level
execution, especially for products with named accounts, renewal cycles, or customer-success teams.
For products without customer-success teams (internal tools, public services, transactional
products), the sunset plan itself serves as the execution document.

**Principles:**
- Never remove access without notice. The deprecation announcement must precede removal by a
  documented interval.
- Never delete user data without offering export. Data belongs to the user.
- Never degrade support during the sunset window. Support commitments hold until the removal date.
- Respect the user's investment in the feature. Acknowledge the disruption and make the transition
  as smooth as possible.

## Phase 4: Internal Cleanup

**Goal:** Remove the feature completely from the system and update all internal artifacts.

**Required outputs:**
- Feature flag removal: remove all feature flags, kill switches, and toggles
- Code archival: archive the feature's code (do not leave dead code in the active codebase)
- Documentation update: remove or archive feature documentation; update references in other docs
- Monitoring and alerting retirement: remove dashboards, alerts, runbooks, and SLOs for the feature
- Infrastructure reclamation: decommission dedicated infrastructure, reclaim resources
- Dependency cleanup: remove third-party dependencies used only by the retired feature

**Template:** Use [../templates/sunset-plan.md](../templates/sunset-plan.md).

## Phase 5: Learning Closure

**Goal:** Capture what the feature's lifecycle taught before the evidence disappears.

**Required outputs:**
- Retained learning record: what was learned, why, and how it should inform future work
- Assumption ledger finalization: close out assumptions with final evidence
- Feedback routing: route learning to roadmap, analytics, adoption, experimentation, specifications

**Template:** Use [../templates/retained-learning-record.md](../templates/retained-learning-record.md).

**Principle:** The learning from a retired feature is as valuable as the learning from a successful
one. A feature that failed taught you something about your users, your market, or your assumptions.
Capture it before the evidence is gone.

## Decision Record Requirement

Every retirement decision must record:
- The accountable human decision-maker (name and role)
- The evidence considered (expected vs. observed, assumption ledger, feature health assessment)
- The context (product, market, user base, alternatives, business priorities)
- The rationale (why retire, not harvest or pivot)
- The date of decision
- The sunset timeline with phase milestones

No retirement decision may be made by an automated threshold. Rules like "retire if DAU < 100" or
"kill if NPS < 30" are prohibited in this skill. Retirement is a human judgment informed by
evidence, not a formula.

## Cross-Cutting: Incident Learning Distinction

Retiring a feature because it is unhealthy or misaligned with strategy is a lifecycle decision.
Retiring a feature because it caused an incident and a postmortem recommended removal is an
incident-driven decision. The latter routes through `incident-learning` (not yet landed) and
[../../site-reliability-engineering/SKILL.md](../../site-reliability-engineering/SKILL.md).
Lifecycle-learning consumes the incident signal as input but does not produce the postmortem.
