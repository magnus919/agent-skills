# Retention/Deletion Verification Plan

Template for designing a retention and deletion verification plan with measurable success conditions. A retention policy without a verification plan is a policy document, not an engineering artifact. This template produces an exercise-ready plan that can be executed to prove deletion actually works.

## Context

| Field | Value |
|---|---|
| **System / feature** | |
| **Data categories in scope** | |
| **Regulatory / policy drivers** | |
| **Retention policy reference** | |
| **Owner** | |
| **Last updated** | |

## Retention schedule

| Data category | Retention period | Clock start | Clock stop | Stated in privacy policy? | Policy reference |
|---|---|---|---|---|---|
| | | | | | |

## Deletion SLA

| Store | Deletion trigger | SLA target | SLA measurement start | SLA measurement end | Verification method |
|---|---|---|---|---|---|
| Primary database | Account closure | 72 hours | Account closure timestamp | Last PII row removed | Row-count audit + sampling |
| Read replica | Account closure | 72 hours | Account closure timestamp | Last PII row removed | Row-count audit |
| Cache | Account closure | 1 hour | Account closure timestamp | Cache key expired/evicted | Cache inspection |
| Object storage | Account closure | 7 days | Account closure timestamp | All objects deleted | Bucket listing |
| Backups | Account closure | 30 days | Account closure timestamp | Backup rotation aged out | Backup manifest inspection |
| Logs | Account closure | 90 days | Account closure timestamp | Log partition dropped | Log-store query |
| Analytics warehouse | Account closure | 7 days | Account closure timestamp | Derived rows removed | dbt model inspection + query |
| Search index | Account closure | 72 hours | Account closure timestamp | Documents removed | Search query for user ID |
| Third-party / subprocessor | Account closure | 30 days | Deletion request sent | Deletion confirmation received | Subprocessor attestation |

## Deletion triggers

| Trigger | Description | Data categories affected | Cascade order |
|---|---|---|---|
| Account closure | User closes account | All PII | Per deletion SLA above |
| Retention expiry | Data exceeds retention period | Category-specific | Per retention schedule |
| Consent revocation | User withdraws consent | Consent-scoped data | Stop collection → delete existing |
| DSAR deletion request | User requests deletion under applicable regulation | Per legal guidance | Per legal-strategy input |
| Data purge request | Internal data-cleanup request | Specified categories | Per change ticket |

## Verification procedure

### Pre-verification baseline

| Step | Action | Expected result |
|---|---|---|
| 1 | Identify test user(s) scheduled for deletion | User ID(s) recorded |
| 2 | Record baseline row counts for each store | Count per store per data category |
| 3 | Record baseline data samples for audit comparison | Sample rows, checksums, or hashes recorded |
| 4 | Record deletion trigger timestamp | Clock-start timestamp recorded |

### Deletion execution

| Step | Action | Expected result |
|---|---|---|
| 1 | Trigger deletion (account closure, DSAR, etc.) | Deletion job queued |
| 2 | Monitor deletion job completion | Job completes within SLA target |
| 3 | Wait for all cascading deletions to propagate | Cascade complete within SLA |

### Post-verification audit

| Store | Verification method | Pass condition | Actual result | Pass/Fail |
|---|---|---|---|---|
| Primary database | `SELECT COUNT(*) WHERE user_id = ?` | 0 rows | | |
| Read replica | Same query on replica | 0 rows | | |
| Cache | Cache key inspection | Key absent | | |
| Object storage | Bucket listing for user prefix | 0 objects | | |
| Backups | Latest backup manifest inspection | User data absent from manifest | | |
| Logs | Log-store query for user ID | 0 records within retention window | | |
| Analytics warehouse | Derived-table row count for user | 0 rows | | |
| Search index | Search query for user ID | 0 documents | | |
| Third-party | Subprocessor deletion confirmation | Confirmation received | | |

## Verification exercise schedule

| Exercise type | Frequency | Last exercise date | Next exercise date | Owner |
|---|---|---|---|---|
| Full deletion verification | | | | |
| Spot-check (sample user) | | | | |
| DSAR simulation | | | | |
| Consent-revocation test | | | | |

## Measurable success conditions

| Condition ID | Description | Measurement | Target | Pass/Fail criteria |
|---|---|---|---|---|
| DEL-SLA-01 | PII deleted from primary store within SLA | Time from trigger to zero rows | ≤ 72 hours | PASS: actual ≤ SLA. FAIL: actual > SLA |
| DEL-COMP-01 | All stores verified deletion-complete | Stores with zero PII rows / total stores | 100% (all stores) | PASS: all stores zero. FAIL: any store has PII |
| DEL-BACKUP-01 | Backup aged out within backup SLA | Time from trigger to backup rotation | ≤ 30 days | PASS: backup rotated. FAIL: backup still contains PII |
| DEL-THIRD-01 | Third-party deletion confirmed | Confirmation received within SLA | ≤ 30 days | PASS: confirmation received. FAIL: no confirmation |

## Gaps and findings

| Finding | Severity | Store affected | Owner | Due date | Re-verification required? |
|---|---|---|---|---|---|
| | | | | | |

## Exercise evidence record

| Field | Value |
|---|---|
| **Exercise date** | |
| **Exercise type** | |
| **Test user ID(s)** | |
| **Deletion trigger timestamp** | |
| **Verification timestamp** | |
| **SLA met?** | |
| **Stores verified** | |
| **Stores with gaps** | |
| **Overall verdict** | Pass / Fail / Pass with gaps |
| **Findings escalated to incident-learning?** | |
| **Follow-up work ledger reference** | |
