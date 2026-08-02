# RTO/RPO Decision Record

## Purpose

Define Recovery Time Objective (RTO) and Recovery Point Objective (RPO) on a per-system, per-scenario basis using a structured decision record. RTO and RPO are context-dependent; they must never be prescribed as universal values.

## Why context matters

RTO and RPO depend on:

- **System criticality:** A payment processing system has different recovery requirements than an internal wiki.
- **Data classification:** Personally identifiable information, financial records, and audit logs have different RPO constraints than cached or derived data.
- **User impact:** How long can users tolerate unavailability or stale data before the business impact becomes unacceptable?
- **Regulatory requirements:** Some industries mandate specific RTO/RPO ranges (e.g., financial services, healthcare).
- **Cost:** Faster recovery and less data loss cost more. The RTO/RPO decision is a tradeoff between recovery capability and infrastructure cost.
- **Dependency chain:** The system's RTO is bounded by the RTO of its dependencies. You cannot recover faster than the systems you depend on.

## Examples of context-specific RTO/RPO

These are examples, not prescriptions. Each system's values must be determined through its own decision record.

| System type | Example RTO context | Example RPO context | Rationale |
|---|---|---|---|
| Payment processing | May be minutes (financial loss per minute of downtime) | Near-zero (every transaction is a financial record) | Revenue impact per minute; regulatory requirements for transaction records |
| Customer-facing SaaS | May be 1-4 hours (user tolerance for unavailability) | May be 1 hour (acceptable data loss for non-financial data) | User experience impact; no regulatory data-loss constraint |
| Internal wiki | May be 1 business day (non-critical internal tool) | May be 24 hours (document edits are recoverable) | Low user impact; cost of rapid recovery outweighs benefit |
| Batch analytics pipeline | May be 1-2 days (pipeline can be re-run) | May be 24 hours (source data is re-ingestible) | Data is derived; source of truth is elsewhere; re-run is acceptable |
| Healthcare records system | May be minutes (patient safety impact) | Near-zero (clinical data integrity is non-negotiable) | Patient safety; regulatory requirements for data integrity |

## Decision record template

### RTO/RPO decision record

- **System name:**
- **Scenario:** (e.g., primary region loss, data corruption, ransomware)
- **Date of decision:**
- **Decision owner:**

#### RTO

- **Target RTO:** (context-specific value with unit — seconds, minutes, hours)
- **Rationale:** Why this target? What is the user/business impact of exceeding it?
- **Tradeoffs considered:** What would it cost (infrastructure, complexity, operational overhead) to achieve a faster RTO? What would a slower RTO cost in user/business impact?
- **Constraints:** Dependencies that bound this RTO (upstream system RTOs, platform capabilities, regulatory minimums).
- **Measurement method:** How is RTO measured in an exercise? Start of outage to verification of recovery.

#### RPO

- **Target RPO:** (context-specific value with unit — seconds, minutes, hours)
- **Rationale:** Why this target? What data would be lost if this RPO is exceeded? Is that data loss acceptable?
- **Tradeoffs considered:** What would it cost to achieve a tighter RPO? What data loss would a looser RPO represent?
- **Constraints:** Data classification, regulatory requirements, backup technology limitations.
- **Measurement method:** How is RPO measured in an exercise? Time of last verified backup to time of failure.

#### Verification

- **Last exercise date:**
- **Exercise result:** pass / fail / pass-with-gaps
- **Measured RTO:** (actual observed recovery time)
- **Measured RPO:** (actual observed data loss)
- **Gap from target:** (if any — difference between measured and target)
- **Follow-up work:** (if gap exists, reference to follow-up work ledger entry)

## Anti-patterns

- **"RTO should be < 1 hour"** — Universal prescription without context. RTO depends on the system.
- **"RPO = 0" without verification** — Claiming zero data loss without an exercise that proves it.
- **Copying RTO/RPO from another system** — Different systems have different failure modes, user impacts, and data classifications.
- **Setting RTO/RPO once and never revisiting** — Systems evolve; recovery objectives must be re-validated as dependencies, data volumes, and user expectations change.
