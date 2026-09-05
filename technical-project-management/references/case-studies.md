# Real-world cases and transfer limits

Use when testing a proposed practice against experience. Source IDs resolve in the
source index. Findings are paraphrased narrowly; proposed controls are our
interpretation. These are illustrative cases, not a controlled comparison of methods.

## Healthcare.gov: visible progress without reliable control

**Context and evidence:** The 2013 marketplace launch involved multiple systems and
contractors. GAO's 2014 audit (C01) connected changing requirements and oversight
gaps with increased costs and schedule slippage. Its 2015 review (C02) identified
incomplete testing, weak requirements management, and an unreliable schedule; later
recommendation updates document corrective actions.

**Our inference:** A dashboard cannot compensate for uncertain scope and missing
integration evidence. **Proposed control:** reconcile current scope, remaining work,
and acceptance evidence before assigning project health. Require a specific decision
when an external deadline and demonstrated readiness conflict.

**Transfer limit:** This does not establish that a particular framework caused the
failure or that a startup needs federal acquisition governance. **Test question:**
what evidence could make you withdraw today's green status?

## GitHub's MySQL upgrade: coordination before cutover

**Evidence (C03):** GitHub reports upgrading more than 1,200 hosts, with preparation
and execution taking over a year across teams and without impact to its SLOs. Its
account describes compatibility testing, a rolling calendar and issue checklists
for app/database coordination, gradual upgrades, and rollback preparation.

**Our inference:** Prerequisite readiness and handoff agreements belong in the
project plan. **Proposed control:** track receiver acceptance and rollback evidence
alongside each scheduled migration wave, with a decision owner for conflicts.

**Transfer limit:** This is self-reported success in a specific architecture. Do
not copy its database topology, rollback assumptions, or duration to another system.
**Test question:** can each team identify the evidence needed before its next handoff?

## Mars Climate Orbiter: interfaces and escalation

**Evidence (C04):** NASA's retrospective briefing identifies a units mismatch plus
inadequate interface verification, missing end-to-end testing evidence, incomplete
communication of navigation concerns, and readiness weaknesses around the 1999 loss.

**Our inference:** Naming an interface is insufficient unless someone verifies it
and unresolved concerns reach an accountable decision-maker. **Proposed control:**
include contract version, receiving-team verification, escalation trigger, and
fallback readiness in dependency agreements.

**Transfer limit:** A spacecraft's irreversibility differs from a reversible web
release. The lesson is proportional verification and escalation, not treating every
software update as a mission launch. **Test question:** who must act if the receiving
team sees an unexplained mismatch?

## GOV.UK: the end of migration is a new operating context

**Evidence (C05):** GDS's 2015 account reports completing the single-domain transition
and shifting priorities away from organizations' migration timetables toward
supporting and improving the service, with team and goal changes.

**Our inference:** A successful migration milestone does not settle ongoing
ownership or service priorities. **Proposed control:** obtain accepted operational
ownership and a benefits-review handoff as part of project closure.

**Transfer limit:** A leadership account does not independently verify all benefits
or prove its organization design fits another team. **Test question:** what changes
in ownership and decision cadence after the project team disbands?

## Using cases responsibly

Compare uncertainty, scale, reversibility, incentives, authority, and dependency
structure before transferring a lesson. Seek a counterexample or local evidence
that would invalidate the analogy. Do not manufacture a small-team case by shrinking
one of these organizations. Hypothetical worked examples in other references are
labeled explicitly and are not part of the field evidence.
