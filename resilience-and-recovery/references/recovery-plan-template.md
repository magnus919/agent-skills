# Recovery Plan Template

## Purpose

A structured template for a system resilience and recovery plan. Every field is required; an empty field is a gap.

## Template

### System boundary
- **System name:**
- **System owner (team/individual):**
- **In scope:** Components, services, data stores, and dependencies covered by this plan.
- **Out of scope:** Adjacent systems or components explicitly not covered.

### Failure modes
| Failure mode | Category | Likelihood | Impact | Detection method | Mitigation |
|---|---|---|---|---|---|
| | component / dependency / resource / region / data / operator / security / cascading | low / medium / high / critical | low / medium / high / critical | | |

### Dependency map
| Dependency | Direction | Failure behavior | Consumer contract |
|---|---|---|---|
| | upstream (we depend on it) / downstream (it depends on us) | What happens when it fails, is slow, or returns incorrect data | What we promise our consumers when this dependency fails |

### Degradation choices
| Failure scenario | Tier 3 shed | Tier 2 shed | Tier 1 preserved | User experience |
|---|---|---|---|---|
| | Features shed first | Features shed if necessary | Core function preserved | What the user sees |

### RTO/RPO decision record
| System / scenario | RTO | RPO | Rationale | Tradeoffs considered | Last verified |
|---|---|---|---|---|---|
| | (context-specific, not a universal value) | (context-specific, not a universal value) | Why this target | Cost, complexity, user impact of alternatives | Date of last exercise |

### Data integrity
- **Post-restore validation procedure:** Step-by-step verification of data correctness after recovery.
- **Checksum method:** How data integrity is cryptographically verified.
- **Row counts and consistency checks:** Expected counts and cross-table consistency.
- **Reconciliation protocol:** How discrepancies are investigated and resolved.
- **Validation owner:** Who runs the validation and signs off.

### Recovery procedure
- **Scenario:**
- **Pre-conditions:** What must be true before recovery can begin.
- **Step-by-step procedure:** Numbered, executable steps.
- **Success criteria:** Observable conditions that confirm recovery is complete.
- **Owner:** Who executes the procedure.
- **Last exercise date:** When this procedure was last tested end-to-end.

### Communication plan
| Scenario | Who to notify | Channel | When | Template |
|---|---|---|---|---|
| | Stakeholder role or name | Email, Slack, PagerDuty, status page | At detection, at start of recovery, at resolution | Link to communication template |

### Exercise schedule
| Scenario | Last exercised | Result | Findings | Next exercise |
|---|---|---|---|---|
| | Date | pass / fail / pass-with-gaps | Summary of findings | Date |

### Follow-up work ledger
| Finding ID | Source exercise | Finding | Owner | Target date | Verification method | Status |
|---|---|---|---|---|---|---|
| | | What was found | Named individual | | How closure will be verified | open / in-progress / verified / escalated |

## Usage notes

- This template is a starting point. Tailor fields to the system's risk class — higher-risk systems require more detail and more frequent exercise.
- Every field must be populated. A field left empty is a documented gap and must appear in the follow-up work ledger.
- The exercise schedule must show evidence of recent exercises. A plan with no exercise evidence in the last 12 months is a finding, not a passing state.
