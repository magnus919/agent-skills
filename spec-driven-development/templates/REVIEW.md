# Gate Decision: <Project / Phase>

## Verdict

**APPROVED** / **CONDITIONS** / **REJECTED**

**Gate:** Gate 1 (Spec Review) / Gate 2 (Plan Review) / Gate 3 (Implementation Review) / Gate 4 (Acceptance Review)

**Artifact under review:** <path to artifact>
**Candidate:** <commit SHA; include a content/tree hash for dirty or non-Git artifacts>
**Acceptance contract:** <ID, version, and immutable hash/reference>
**Review scope:** <tasks, criteria, artifacts, and relevant dependencies>
**Validity:** Current / Superseded / Withdrawn — <reason and replacement record>

Approval applies only to this candidate, contract, and evidence scope. Before a
phase transition or delivery, compare them to the actual artifacts. A relevant
change to code, dirty content, contract, dependencies, configuration, fixtures,
or relevant environment invalidates the affected approval and evidence; retain the old record as
history and obtain a new verdict. A candidate change cannot inherit an old PASS
from the same branch, PR, filename, or task label.

**Reviewer:** <name>
**Independence and limitations:** <separate evaluator or disclosed self-review; scope limits>
**Date:** <date>

## Summary

<One-paragraph summary: what was evaluated, the key finding, and why the verdict was reached.>

## Executed checks and evidence

| Criterion / task | Check or observation | Candidate / contract binding | Environment and fixtures | Executed at | Result | Evidence reference / hash |
|---|---|---|---|---|---|---|
| <AC-ID / T-ID> | <command or reproducible procedure> | <same candidate and contract above> | <runtime/configuration/fixture versions> | <timestamp> | PASS / FAIL / HOLD / UNRUN | <report or observed output> |

Record actual execution and relevant coverage, including skipped or unavailable
checks. A check name, proposed command, or exit zero from an empty/stub run is not
evidence that the criterion passed. Explain any justified reuse of unaffected
checks; rerun affected checks on the new candidate and issue a current verdict.

## Findings

### Finding 1: <Title>

- **Finding ID:** <stable ID, retained across review rounds>
- **Severity:** BLOCKING / CRITICAL / MINOR / INFO
- **Location:** <artifact> — <section>
- **Description:** <what was found>
- **Recommendation:** <what should change>

### Finding 2: <Title>

...

## Finding handoffs and closure

| Finding ID | Disposition | Decision owner and rationale | Follow-up task / duplicate-of | Dependencies and blocking boundary | Closure evidence |
|---|---|---|---|---|---|
| <F-ID> | proposed / accepted / deferred / declined / duplicate / resolved | <authorized orchestrator decision and record> | <existing or newly accepted task when warranted> | <affected tasks and latest safe gate; or none> | <fix candidate + verifying evidence; or rationale/canonical link> |

A recommendation is not backlog authority. The orchestrator may accept, defer,
decline, or deduplicate it; do not create a ticket for every suggestion. An
accepted follow-up needs an owner, acceptance checks, and a receiving-task link.
Deferral or ticket creation is a handoff, not resolution. Close an accepted
finding only after its receiving task supplies verified closure evidence; a
declined/duplicate disposition closes triage with rationale/canonical linkage,
not a claim of repair. Block dependent effects while a governing finding remains
unresolved; unrelated work may continue under its existing authority.

## Conditions (if verdict is CONDITIONS)

| # | Condition | Owner | Due By |
|---|-----------|-------|--------|
| 1 | <remediation required> | <name> | <date/gate> |

## Revision History

| Version | Date | Verdict | Author |
|---------|------|---------|--------|
| 1.0 | <date> | <verdict> | <name> |
