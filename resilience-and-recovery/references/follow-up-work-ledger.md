# Follow-Up Work Ledger

## Purpose

Convert every exercise finding into owned, tracked, and verified follow-up work. An exercise that produces findings but no follow-up work is an incomplete exercise. The follow-up work ledger is the bridge between "we found a gap" and "we closed the gap."

## Ledger template

| Field | Description |
|---|---|
| **Finding ID** | Unique identifier for this finding |
| **Source exercise** | Which exercise (game day, restore test, failover drill) produced this finding, and when |
| **Finding** | What was observed — be specific: "Restore took 47 minutes against a 30-minute RTO target" not "Restore was slow" |
| **Severity** | blocker (system cannot meet its recovery objective) / gap (system meets objective but with unexpected behavior) / improvement (system meets objective; opportunity to do better) / observation (noted for tracking; no immediate action) |
| **Owner** | Named individual accountable for resolution. Cannot be "the team" or "TBD" |
| **Target date** | When resolution is expected. Must be a specific date, not "next quarter" |
| **Work type** | implementation (code/config change) / test (new or updated test/exercise) / operational (process/procedure change) / documentation (plan/runbook update) |
| **Verification method** | How closure will be verified — re-exercise, automated test, code review, audit |
| **Status** | open / in-progress / verified / escalated / wont-fix (with rationale) |
| **Verification date** | When closure was verified |
| **Verification evidence** | Pointer to evidence — test result, exercise log, commit SHA, audit record |

## Finding classification

### Blocker
The finding demonstrates that the system cannot meet a defined recovery objective (RTO, RPO, data integrity). The recovery plan is not valid until this is resolved.

**Example:** "Restore from backup took 47 minutes. Target RTO is 30 minutes. Gap: 17 minutes."

### Gap
The system meets its recovery objective but with unexpected behavior — a surprise that did not prevent success but indicates an unknown or unmanaged risk.

**Example:** "Failover completed within RTO, but alerts for the failover event were delayed by 8 minutes. Operations team was unaware of the failover during that window."

### Improvement
The system meets its recovery objective. The finding identifies an opportunity to improve beyond the objective.

**Example:** "Restore completed in 22 minutes against a 30-minute RTO. Parallelizing the restore of two independent data stores could reduce this to under 15 minutes."

### Observation
Noted for tracking; no immediate action required but worth revisiting.

**Example:** "During the game day, the team noted that the runbook references a deprecated internal tool name. The procedure works but the documentation is stale."

## Escalation rules

Findings that cannot be resolved within the normal follow-up workflow must be escalated:

| Condition | Escalation |
|---|---|
| No owner can be identified for a blocker finding | Escalate to system owner or engineering manager. The finding cannot remain ownerless. |
| Owner declines ownership without a transfer | Escalate to the owner's manager. Ownership gaps are themselves a finding. |
| Target date passes without resolution | Escalate to the system owner with a revised date or a decision to accept the risk. |
| Blocker finding has no feasible resolution | Escalate to leadership for a risk-acceptance decision. Document the accepted risk. |
| Exercise exposes a gap in another team's ownership (unowned gap) | Escalate to the system owner with the gap documented. The gap must be assigned an owner before the exercise is closed. Do not close the exercise with an unowned gap. |

## Closure criteria

A finding is closed (status: verified) only when:

1. The resolution has been implemented (code change, test addition, process update, documentation fix).
2. The verification method has been executed and passed.
3. Verification evidence is recorded.
4. The owner confirms closure.

A finding is NOT closed when:

- A ticket was filed. (Ticket creation is tracking, not verification.)
- "We'll fix it next cycle." (Deferral without a specific date and owner is not closure.)
- "The plan says we handle this." (Design documentation is not verification evidence.)

## Example entries

| Finding ID | Source exercise | Finding | Severity | Owner | Target date | Work type | Verification method | Status |
|---|---|---|---|---|---|---|---|---|
| EX-2026-001 | Restore test 2026-03-15 | Restore took 47 min vs 30 min RTO | blocker | jane.chen@example.com | 2026-04-15 | implementation | Re-exercise restore; measure time | open |
| EX-2026-002 | Game day 2026-03-22 | Failover alerts delayed 8 min; ops unaware | gap | marcus.kim@example.com | 2026-04-01 | operational | Monitor alert latency during next game day | in-progress |
| EX-2026-003 | Failover drill 2026-03-29 | Runbook references deprecated tool "backupctl" | observation | priya.patel@example.com | 2026-04-30 | documentation | Review runbook diff | open |
