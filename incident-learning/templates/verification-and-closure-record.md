# Verification and Closure Record

Complete this record for each follow-up item to close it. Closure requires evidence that the intended change was implemented, verified, and had the intended effect. Ticket creation alone is not sufficient.

## Record

| Field | Value |
|---|---|
| **Closure record ID** | |
| **Follow-up item ID** | (link to follow-up work map item) |
| **Finding reference** | (link to incident learning record finding) |
| **Domain** | (product / code / tests / evals / operations / governance) |

## Implementation evidence

*What was implemented? Provide a concrete reference — commit SHA, config change ID, document URL, policy reference.*

| Field | Value |
|---|---|
| **Description of change** | |
| **Reference** | (commit SHA, PR URL, config change ID, document URL) |
| **Implementation date** | |

## Verification evidence

*How was the implementation verified against the intended change? Provide a concrete reference — test run, monitor fire log, eval result, audit record.*

| Field | Value |
|---|---|
| **Verification method** | (from follow-up work map) |
| **Verification result** | |
| **Verification reference** | (test run URL, monitor fire log, eval result, audit record) |
| **Verification date** | |

## Effect evidence

*Did the intended change have the intended effect? If the effect is not yet observable, state when it will be observable and set a re-evaluation date.*

| Field | Value |
|---|---|
| **Intended effect** | |
| **Observed effect** | |
| **Effect evidence reference** | |
| **Re-evaluation date** | (if effect not yet observable) |

## Closure decision

| Field | Value |
|---|---|
| **Closure state** | (Verified closed / Verified closed — effect pending / Rejected / Superseded) |
| **Closure authority** | (who approved the closure) |
| **Closure date** | |

## Rejection record (if rejected)

| Field | Value |
|---|---|
| **Rejection reason** | |
| **Residual risk acceptance** | (explicit acknowledgment that the gap remains) |
| **Rejection authority** | |
| **Rejection date** | |

## Supersedure record (if superseded)

| Field | Value |
|---|---|
| **Superseding follow-up ID** | |
| **Reason for replacement** | |

## Revised hypothesis (if effect was not as expected)

| Field | Value |
|---|---|
| **What was expected** | |
| **What was observed** | |
| **Revised hypothesis** | |
| **Replacement follow-up ID** | (if a new follow-up item is created) |

## Closure rules

1. **Tickets alone are not sufficient.** A ticket ID may be referenced as supplementary context, but it does not satisfy any of the three evidence requirements (implementation, verification, effect).
2. **All three evidence fields must be complete for "Verified closed."** If effect evidence is not yet available, use "Verified closed — effect pending" with a re-evaluation date.
3. **"Rejected" is a terminal state.** A rejected follow-up does not remain open. The rejection is a conscious decision with documented rationale and residual risk acceptance.
4. **"Superseded" requires a link to the replacement.** The superseding item carries the finding forward; this record is closed.
5. **A closure record with missing evidence is not a closure — it is a status update.** If evidence is missing, the follow-up remains open.
