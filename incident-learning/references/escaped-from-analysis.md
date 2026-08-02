# Escaped-From Analysis

Every incident escaped from something — a gap in the system that allowed the failure to reach production or users. The "escaped from" analysis maps the originating gap to one or more of five categories. This mapping drives the domain of follow-up work: a monitoring gap produces an observability follow-up, not a code patch.

## The five escaped-from categories

### 1. Escaped requirement

**Definition:** A needed requirement was absent, incomplete, or incorrectly specified — and that gap allowed the incident. The system behaved as specified, but the specification was wrong or missing.

**Indicators:**
- The incident occurred because the system lacked a capability that, had it existed, would have prevented or mitigated the incident.
- The specification, PRD, or design document did not address the failure condition.
- A stakeholder says "we never thought of that scenario" or "the requirement didn't cover this."

**Follow-up domain:** Product (requirements update, design review, specification amendment).

**Examples:**
- An API rate-limiting requirement was missing from the specification. A legitimate-but-unexpected traffic pattern overwhelmed the service.
- The authentication flow did not require MFA for a privileged operation because the requirement only specified MFA for login.
- A data-retention policy was not specified, leading to unbounded storage growth and eventual disk exhaustion.

### 2. Missing monitoring or observability

**Definition:** No signal existed to detect the condition before or during the incident — no alert, no dashboard, no log, no metric. The condition occurred in a blind spot.

**Indicators:**
- The incident was discovered by users, not by an alert.
- An alert existed but fired too late, was tuned incorrectly, or was ignored (alert fatigue).
- The relevant metric, log, or trace was not instrumented.
- The condition was detectable in principle but not in practice because the data was not collected, retained, or surfaced.

**Follow-up domain:** Operations (monitoring, alerting, observability instrumentation).

**Examples:**
- A database connection-pool exhaustion had no alert. The pool metric existed but was not wired to an alert rule.
- A third-party API latency degradation was invisible because outbound call latency was not instrumented.
- Disk space on a critical volume was not monitored; the volume filled without warning.

### 3. Unsafe authority or access

**Definition:** Insufficient guardrails on who could act, what actions were permitted, or what approvals were required. The incident occurred because someone (human or agent) had authority they should not have had, or could act without sufficient validation.

**Indicators:**
- A human operator performed an action that should have required approval, confirmation, or a second pair of eyes.
- An automated system or AI agent made a decision that should have had a human-in-the-loop gate.
- A permission was broader than necessary (e.g., a service account with write access to a database it only needed to read).
- A deployment was possible without a required check or gate.

**Follow-up domain:** Governance (access control, policy, approval workflows, agent authority boundaries).

**Examples:**
- A developer ran a database migration directly in production without a change request because they had direct production access.
- An AI agent executed a destructive action because its authority boundary did not require confirmation for that action class.
- A service account with full cluster admin was used by a deployment pipeline, and a misconfigured deployment deleted namespaces outside its scope.

### 4. Migration gap

**Definition:** A transition — deployment, data migration, infrastructure change, dependency upgrade — introduced or exposed the condition that led to the incident.

**Indicators:**
- The incident began within a window following a change: deployment, migration, configuration update, dependency version bump.
- The change was tested in pre-production but the production environment differed in a relevant way.
- A migration was not fully completed, leaving the system in an intermediate state.
- A rollback was attempted but failed, or a rollback path was not planned.

**Follow-up domain:** Code or operations, depending on whether the gap is in the change itself (code) or in the migration procedure (operations).

**Examples:**
- A database schema migration added a column without a default value, and the application code did not handle the null case.
- A dependency upgrade changed the default timeout behavior, and the application did not configure an explicit timeout.
- A cross-region migration left stale DNS records that routed traffic to decommissioned endpoints.

### 5. Adoption consequence

**Definition:** User or operator behavior — intended or unintended — contributed to the incident. The system was used in a way that was not anticipated, or a documented procedure was not followed.

**Indicators:**
- A user action triggered a code path that was not tested or designed for that input.
- An operator followed a runbook that was outdated or incorrect.
- A feature was used at a scale or in a pattern that was not anticipated.
- A documented procedure existed but was not followed (process adherence gap).

**Follow-up domain:** Product (if the usage pattern reveals a missing requirement or design gap), Governance (if a process or procedure needs to change), or Code (if the system should handle the usage pattern safely).

**Examples:**
- Users discovered that uploading a file with a specific character in the filename caused a parsing error in the pipeline.
- The on-call runbook instructed the operator to restart a service, but the correct procedure had changed to restarting a dependent service first.
- A feature designed for 100 items was used with 10,000 items, exposing an O(n^2) algorithm.

## Multi-category mapping

An incident can escape from multiple gaps. Each gap is recorded separately, with its own follow-up work. For example:

- An incident where a deployment (migration gap) exposed a missing alert (monitoring gap) maps to both categories. The deployment procedure fix and the alert creation are separate follow-up items.
- An incident where users triggered an unforeseen code path (adoption consequence) that revealed a missing requirement (escaped requirement) maps to both categories. The code fix and the requirement update are separate follow-up items.

## Using escaped-from analysis

1. For each incident, ask: "What gap allowed this incident to reach production or users?"
2. Classify each gap into one or more of the five categories.
3. For each gap, create at least one follow-up work item in the corresponding domain.
4. Record the escaped-from category in the incident learning record.
5. When no gap can be identified, record "no escaped-from gap identified" as a finding — this may indicate that the incident was genuinely unavoidable, or that the analysis is incomplete.
