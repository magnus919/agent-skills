# Exercise Design and Evidence

## Purpose

Design and execute resilience exercises — game days, restore tests, and failover drills — and record the evidence they produce. Exercises are the standard of proof for resilience claims. A recovery plan without exercise evidence is a design document, not a capability.

## Exercise types

| Type | What it tests | Frequency guidance |
|---|---|---|
| **Game day** | System behavior under a specific failure scenario — dependency loss, region failure, resource exhaustion | Per scenario, per release cycle or quarterly |
| **Restore test** | End-to-end restore from backup, including data integrity verification | Monthly for critical systems; quarterly for others |
| **Failover drill** | Failover to a standby or DR region, including application-level validation | Quarterly for systems with DR capability |
| **Chaos experiment** | Continuous or semi-continuous injection of failure in production (or staging) | Ongoing for mature systems; start with game days |

## Exercise design

### Pre-exercise

1. **Define the scenario.** What specific failure is being tested? Be precise: "Primary database region becomes unavailable" not "database failure."
2. **Define success criteria.** Observable, measurable conditions that confirm the system behaved as expected. "Application continues serving reads from replica within 30 seconds" not "system handles failure."
3. **Define the rollback/safety plan.** How to abort the exercise if it goes wrong. Every exercise needs a stop condition and a rollback path.
4. **Notify stakeholders.** Who needs to know the exercise is happening? Use the communication plan from the recovery plan template.
5. **Record the pre-exercise state.** System metrics, data state, configuration — the baseline to compare against.

### During exercise

1. **Execute the failure injection.** Follow the scenario precisely. Do not deviate unless the safety plan triggers.
2. **Observe system behavior.** Record: detection time, mitigation activation time, degradation onset, user-visible impact, automated vs. manual responses.
3. **Record anomalies.** Anything unexpected — slower-than-expected recovery, unexpected cascading failures, alerts that did not fire or fired incorrectly.
4. **Abort if safety threshold is crossed.** The exercise is not a martyrdom. If degradation exceeds the pre-defined safety boundary, stop and investigate.

### Post-exercise

1. **Restore to pre-exercise state.** Verify the system is back to normal operation.
2. **Compare against success criteria.** Did the system meet every criterion?
3. **Classify findings:**
   - **Pass:** All success criteria met.
   - **Pass with gaps:** Success criteria met but unexpected behavior observed (e.g., recovery worked but alerts were delayed).
   - **Fail:** One or more success criteria not met.
4. **Record evidence.** Date, scenario, participants, observed behavior, metrics, findings, and classification.
5. **Convert findings to follow-up work.** Every gap or failure becomes an entry in the follow-up work ledger with an owner, a target date, and a verification method.

## Exercise evidence standard

Exercise evidence is NOT sufficient when it consists only of:

- Design documentation or architecture diagrams.
- "The plan was reviewed and approved."
- A checklist that was filled out without actual system observation.
- A backup verification report without a restore test.
- A claim that "the system is designed to handle this."

Exercise evidence IS sufficient when it includes:

- A timestamped exercise log with observed system behavior.
- Metrics showing the system's actual response (detection time, recovery time, error rates).
- Comparison against pre-defined success criteria with a pass/fail/gaps verdict.
- Findings classified and converted to owned follow-up work.
- The exercise was performed against the actual system (or a faithful replica), not a diagram.

## Game day scenario examples

| Scenario | Injection | Expected behavior | Success criteria |
|---|---|---|---|
| Primary database failure | Simulate primary DB unavailability | Application fails over to replica; read-only mode or full service depending on architecture | Failover completes within RTO; no data loss beyond RPO |
| Upstream API timeout | Introduce 30s latency on dependency | Circuit breaker opens; fallback activates; consumers see degraded but acceptable response | Fallback activates within 5s; no error returned to consumers |
| Region loss | Simulate complete AZ/region unavailability | Traffic shifts to secondary region; DR plan activates | Traffic shift completes within RTO; data consistency verified post-failover |
| Disk full | Fill disk on a node to 100% | Monitoring alerts; node drains; service continues on remaining nodes | Alert fires within 2 min; node drains without dropped requests |
| Bad deployment | Deploy a version with a known memory leak | Canary detects degradation; rollback triggers before full rollout | Canary catches degradation within monitoring window; rollback completes without manual intervention |
