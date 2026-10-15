# Specification: <Project / Feature Name>

## Status

- **Author:** <name>
- **Version:** 0.1.0 (draft)
- **Status:** Draft / Under Review / Approved
- **Reviewed by:** <reviewer>
- **Gate verdict:** Pending / Approved / Conditions / Rejected

## Problem Statement

<One to three sentences describing the problem this specification addresses. What gap exists in the current system? What user need is unmet? Why is this worth building?>

## Success Criteria

<Measurable outcomes that define success. These are NOT acceptance criteria for individual features — they are the overall outcomes justifying the investment. Example: "Reduce account creation time from 90s to under 30s.">

## Scope

### In Scope

- <Capability or behavior included>
- <Capability or behavior included>

### Out of Scope (Explicit)

- <Capability explicitly excluded — prevents scope creep>
- <Capability explicitly excluded>

## User Stories

### US-001: <Story Title>

**Priority:** P0 / P1 / P2 / P3
**Description:** As a <role>, I want <capability> so that <benefit>.

**Acceptance Criteria:**

1. [AC-001.1] Given/When/Then or pass/fail condition
2. [AC-001.2] Given/When/Then or pass/fail condition

**Edge Cases:**

- <Edge case description — what happens when>
- <Edge case description>

### US-002: <Story Title>

...

## Non-Functional Requirements

| ID | Requirement | Threshold | Verification Method |
|----|-------------|-----------|-------------------|
| NFR-001 | Response time | < 200ms at P95 | Load test |
| NFR-002 | Availability | 99.9% uptime | Monitoring |
| NFR-003 | Security | <describe requirement> | <describe how verified> |

## Data Contracts & Interfaces

<Schemas, API signatures, event definitions. Stubs are acceptable at this phase — identify what contracts exist even if refined later.>

### <Interface Name>

```
<Schema or signature>
```

## Assumptions & Open Questions

| ID | Assumption / question and impact if wrong | Affected tasks / criteria | Decision owner | Risk and reversibility | Status | Decision deadline / latest safe point | Resolution / approval evidence |
|---|---|---|---|---|---|---|---|
| A-001 | <choice; what breaks if wrong> | <T-IDs / AC-IDs; pending decomposition if not yet known> | <accountable decision owner> | <consequence; rollback cost/boundary> | provisional | <date or milestone, before dependent effect> | <decision, authority, timestamp, contract version, source reference; unresolved until supplied> |
| A-002 | <open question; what blocks> | <dependent tasks / criteria> | <owner> | <risk / reversibility> | unresolved | <latest point before dependency may proceed> | <needed evidence> |

Use stable IDs and retain status history: unresolved → provisional → accepted,
rejected, or superseded. Provisional records a choice within already authorized
bounded work; the status is not owner acceptance or authority for new effects.
Batch low-risk, reversible choices at a milestone when the existing contract
allows them, with an owner and rollback boundary. Decide consequential unresolved
assumptions before dependent merge/release or other effects, even if milestone
review is later. Silence or a passed deadline is not approval.

If an assumption is rejected, changed, or overdue at its safe boundary, identify
affected tasks and their dependent tasks. Mark their acceptance and derived
review/test evidence stale, block dependent effects, revise the contract/plan,
and reverify the affected candidate before restoring approval. Retain historical
evidence without presenting it as current. Unaffected tasks need not be reset.

## Revision History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 0.1.0 | <date> | <name> | Initial draft |
