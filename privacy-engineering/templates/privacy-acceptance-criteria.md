# Privacy Acceptance Criteria

Template for defining verifiable, testable privacy acceptance criteria. Every criterion must include a description, verification method, and pass/fail condition. "Data is handled securely" is not a verifiable criterion — use this template to make every requirement testable.

## Context

| Field | Value |
|---|---|
| **System / feature** | |
| **Data categories in scope** | |
| **Privacy dimensions addressed** | |
| **Regulatory / policy drivers** | |
| **Owner** | |
| **Last updated** | |

## Acceptance criteria

For each privacy requirement, define at least one criterion with all three fields. A criterion without a verification method is a policy statement, not an engineering artifact.

| ID | Criterion description | Verification method | Pass/fail condition |
|---|---|---|---|
| **PUR-01** | | | |
| **RET-01** | | | |
| **ACC-01** | | | |
| **DEL-01** | | | |
| **TEN-01** | | | |
| **RES-01** | | | |
| **CON-01** | | | |

### Example criteria (illustrative)

| ID | Criterion description | Verification method | Pass/fail condition |
|---|---|---|---|
| **PUR-01** | Email address collected only for account recovery; not used for marketing | Schema inspection of marketing pipeline: confirm email field is not present in marketing events table | PASS: email field absent from marketing events schema. FAIL: email field present |
| **RET-01** | User session logs retained for 90 days from session end, then deleted | Automated audit: query session_logs for records with session_end > 90 days ago; expect zero rows | PASS: zero rows returned. FAIL: any rows returned |
| **ACC-01** | Customer support staff can view user PII only while a support ticket is open | Access-log review: sample 100 access events; confirm each access corresponds to an open ticket for that user | PASS: 100/100 accesses tied to open tickets. FAIL: any access without open ticket |
| **DEL-01** | User PII deleted from primary store within 72 hours of verified account closure | End-to-end test: close test account, wait 72h, query all tables for test user PII; expect zero PII rows | PASS: no PII rows found for test user. FAIL: any PII rows remain |
| **TEN-01** | Tenant-A data never returned in a query authenticated as Tenant-B | Integration test: execute cross-tenant queries with Tenant-B credentials; verify zero Tenant-A rows in result set | PASS: zero cross-tenant rows. FAIL: any Tenant-A data in Tenant-B response |
| **RES-01** | EU user PII never stored in non-EU region | Infrastructure audit: inspect storage bucket regions, database instance regions, CDN edge locations; confirm all in EU | PASS: all stores in EU regions. FAIL: any store outside EU |
| **CON-01** | Analytics events fire only after consent is granted; no events fire post-revocation | Event-stream audit: for a post-revocation user, confirm zero events emitted after revocation timestamp | PASS: zero events post-revocation. FAIL: any event emitted after revocation |

## Verification schedule

| Criterion ID | Verification frequency | Last verified | Next verification | Verified by |
|---|---|---|---|---|
| | | | | |

## Gaps and exceptions

| Criterion ID | Gap description | Exception approved by | Expiry | Mitigation |
|---|---|---|---|---|
| | | | | |
