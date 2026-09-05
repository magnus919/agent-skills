# Hybrid delivery and dependency coordination

Use when teams, vendors, procurement, hardware, or governance work on different
cadences. Basis: S01/S06 support tailoring; C03 supplies a real coordination
example. The interface procedure below is this skill's synthesis.

## Define a hybrid precisely

Name which work follows which approach, why, and who owns each interface. A
monthly sponsor decision can coexist with continuous software delivery; it must
not secretly require every team to wait for a monthly release. Conversely, a
sprint review cannot override a required external certification.

Maintain one authoritative milestone/decision view. Team backlogs can differ;
project commitments cannot contradict each other without a visible unresolved
issue. Do not impose a shared sprint length merely to simplify reporting.

## Dependency agreement

For each material dependency record: provider, receiver, deliverable and version,
acceptance evidence, needed-by date, provider forecast, accepted commitment,
confidence basis, review date, escalation owner, and fallback. A provider saying
"we'll try" is a forecast or aspiration, not a commitment.

1. Ask the receiver what usable input is needed, not just which team is blocking.
2. Validate whether it is a hard dependency. A mock may permit development but not
   production acceptance; document both boundaries.
3. Confirm the provider's scope and capacity. Include procurement lead time,
   reviews, security, test environments, and customer participation.
4. Schedule an integration checkpoint before the final milestone. Agree how a
   failed handoff changes the forecast and who decides the response.
5. Track interface changes and receiver acknowledgement. A delivered artifact is
   not an accepted handoff until the receiving party can use it as agreed.

## Vendor and distributed-team cases

| Problem | Response |
|---|---|
| Fixed-price vendor with evolving software needs | Identify contractual acceptance/change process; assess options with procurement/legal rather than interpreting rights yourself |
| Vendor dates lag the project need | Record date gap and latest decision point for contingency; escalate before the fallback becomes impossible |
| Shared environment unavailable | Treat environment capacity as a dependency, with a specific reservation owner |
| Time-zone handoffs add a day per question | Use an async decision brief, clear response window, and backup decision-maker |
| Two teams claim contract ownership | Separate authoring, approval, and acceptance responsibilities; route unresolved authority to the sponsor |
| Several projects compete for one team | Surface program/portfolio arbitration; do not allocate another project's capacity unilaterally |

## Worked boundary (hypothetical)

A vendor provides a certified device in week 8; software teams iterate fortnightly.
The project has interface test evidence due in week 5 and integrated acceptance in
week 9. If certification moves to week 10, successful software sprints do not keep
the project green. Present a revised integration forecast, impact on commitments,
and an authorized fallback decision. A simulator retires interface uncertainty but
does not replace device certification.

Complete when critical handoffs have accepted owners, evidence, dates, and escalation
paths, or their absence is explicitly blocking the affected commitment.
