# Follow-Up Work Map

Map every incident finding to follow-up work across six domains: product, code, tests, evals, operations, and governance. Every item must have an owner, a domain, a verification method, and a status. No item may remain unowned.

## Work map

| ID | Finding reference | Domain | Description | Escaped-from category | Owner | Target date | Verification method | Routing target | Status | Closure record |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |
| | | | | | | | | | | |

## Field definitions

| Field | Description | Required |
|---|---|---|
| **ID** | Unique follow-up item identifier | Yes |
| **Finding reference** | Link to the finding in the incident learning record | Yes |
| **Domain** | One of: product, code, tests, evals, operations, governance | Yes |
| **Description** | What needs to be done — concrete and verifiable | Yes |
| **Escaped-from category** | The originating gap: escaped requirement, missing monitoring, unsafe authority, migration gap, adoption consequence | Yes |
| **Owner** | Named individual or role accountable for completion | Yes — "the team" or "TBD" is not acceptable |
| **Target date** | When the follow-up work should be completed | Yes |
| **Verification method** | How completion and effect will be verified | Yes |
| **Routing target** | Specialist skill or team that owns implementation | Recommended |
| **Status** | One of the status values below | Yes |
| **Closure record** | Link to the verification and closure record when closed | Required for verified-closed or rejected items |

## Status values

| Status | Meaning |
|---|---|
| **Proposed** | Follow-up item has been identified but not yet accepted by the owner |
| **Accepted** | Owner has accepted the follow-up item; work is planned |
| **In progress** | Implementation is underway |
| **Implemented** | Implementation is complete; verification is pending |
| **Verified** | Implementation verified; effect evidence is pending or complete |
| **Rejected** | Follow-up item was evaluated and intentionally not pursued (requires rejection reason in closure record) |
| **Superseded** | Follow-up item was replaced by a different item (link to superseding ID) |

## Domain-specific verification methods

| Domain | Verification method examples |
|---|---|
| **Product** | Requirement document updated and approved; specification accepted; design decision recorded |
| **Code** | Code change merged; tests pass; failure mode reproduced and confirmed fixed |
| **Tests** | Test added; test passes; test fails when original failure condition is reintroduced (mutation verification) |
| **Evals** | Eval case added; eval fails against pre-fix system, passes against post-fix system |
| **Operations** | Monitor/alert deployed; alert fires under incident condition (fault injection); runbook exercised |
| **Governance** | Policy/access change enacted; restricted action attempted and blocked; approval gate exercised |

## Ownership rules

1. Every item must have a named owner. "The team," "TBD," "engineering," or any group designation is not acceptable.
2. If the appropriate owner cannot be identified, the item status remains "Proposed" and the item is escalated to the incident owner or engineering manager for owner assignment.
3. An owner may delegate implementation but remains accountable for verification and closure.
4. When an owner leaves or changes role, the item must be reassigned — it does not become unowned.

## Cross-domain items

A finding that maps to multiple domains should be split into separate follow-up items — one per domain. For example, a monitoring gap (operations) that also reveals a missing requirement (product) produces two items with different owners and verification methods.

## Closure gate

An item transitions to "Verified" only when the verification and closure record is complete with implementation evidence, verification evidence, and effect evidence (or a re-evaluation date for effect-pending items). See the verification and closure record template for the evidence standard.
