# Privacy Change Review

Template for reviewing a feature, schema, integration, or AI pipeline change for privacy impact. Every change that touches data collection, storage, processing, sharing, or deletion should produce a privacy change review before implementation proceeds.

## Change context

| Field | Value |
|---|---|
| **Change ID / ticket** | |
| **Change description** | |
| **System / feature affected** | |
| **Change type** | New feature / Schema change / Integration / AI pipeline / Infrastructure / Deprecation / Other |
| **Requestor** | |
| **Reviewer** | |
| **Review date** | |

## Privacy impact summary

- [ ] **No privacy impact** — change does not touch PII, change data collection, modify data flows, or affect retention/deletion behavior.
- [ ] **Privacy impact identified** — complete the sections below.

## Data impact assessment

| Dimension | Current state | Proposed state | Impact |
|---|---|---|---|
| **Data collected** | | | |
| **Purpose** | | | |
| **Classification** | | | |
| **Retention** | | | |
| **Access** | | | |
| **Deletion** | | | |
| **Residency** | | | |
| **Consent** | | | |
| **Tenant isolation** | | | |

## New data elements

| Data element | Purpose | Classification | Justification for collection | Minimization considered? |
|---|---|---|---|---|
| | | | | |

## Changed data flows

| Flow | Current path | Proposed path | Crosses new trust boundary? | Crosses new region? |
|---|---|---|---|---|
| | | | | |

## Agent trace and telemetry impact

| Concern | Assessment |
|---|---|
| Does this change introduce new agent traces (LLM logs, tool calls)? | |
| Does this change introduce new product analytics events? | |
| Are prompts, tool arguments, or intermediate reasoning logged? | |
| Is redaction applied before traces leave the execution boundary? | |
| Is consent required for new telemetry? | |

## Privacy acceptance criteria (new or updated)

| Criterion ID | Description | Verification method | Pass/fail condition |
|---|---|---|---|
| | | | |

## Retention and deletion impact

| Concern | Assessment |
|---|---|
| Does this change introduce data that needs a retention period? | |
| Are existing retention periods still appropriate? | |
| Does deletion cascade to the new data? | |
| Is the deletion SLA achievable for the new data volume or store? | |

## Third-party and subprocessor impact

| Third party | New data shared? | DPA updated? | Deletion commitment confirmed? |
|---|---|---|---|
| | | | |

## Risk assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| | | | |

## Review decision

- [ ] **Approved** — no privacy concerns, or concerns are adequately mitigated.
- [ ] **Approved with conditions** — proceed, with the following conditions:
  - Condition 1:
  - Condition 2:
- [ ] **Blocked** — do not proceed until the following are resolved:
  - Blocker 1:
  - Blocker 2:
- [ ] **Escalated to legal** — jurisdiction-specific interpretation required for:
  - Question:

## Conditions tracking

| Condition | Owner | Due date | Status | Closure evidence |
|---|---|---|---|---|
| | | | | |

## Sign-off

| Role | Name | Date |
|---|---|---|
| Privacy reviewer | | |
| Engineering owner | | |
| Legal (if escalated) | | |
