# Project control and communication

Use for recurring reviews, executive updates, disputed status, or escalation.
Basis: C02 documents weak oversight and stale planning evidence; S06 places
reporting, issues, and decision-making within project control. This cadence is a
suggested lightweight adaptation, not a prescribed standard.

## A minimum viable review

Use an existing team cadence; default to an async weekly project review with live
discussion only for decisions or unresolved conflict. High-risk work may need more
frequent review. Never delay material bad news until the next meeting.

1. Read accepted milestones and new evidence since the last review.
2. Compare baseline, current forecast, and deadline. Ask what remaining work changed.
3. Inspect blocked/aging dependencies, current issues, and leading risk signals.
4. Review capacity and cost exposure, including unplanned work displacing commitments.
5. Identify decisions due before the next review, available options, and consequences
   of waiting. Ask the authorized owner rather than assembling consensus by default.
6. Issue a concise update and record the next evidence checkpoint.

## Status semantics

Agree thresholds for this project. A useful starting vocabulary is:

- **On track:** current evidence supports the approved commitment within tolerance.
- **At risk:** a credible threat needs mitigation or decision; commitment not yet lost.
- **Off track:** forecast breaches tolerance or acceptance cannot be met as agreed.
- **Unknown:** evidence is missing, contradictory, or stale enough to affect judgment.

Report by dimension when necessary: schedule green, quality unknown is not an
unqualified green project. Do not average away a failed critical dependency. Keep
the assessment's as-of date and evidence. A ticket marked done without acceptance
is a discrepancy to resolve, not an excuse to claim delivery.

## Risks, issues, assumptions, decisions

A risk is an uncertain event; an issue has occurred or requires resolution now.
When a risk materializes, link it to the issue and activate the response. Each risk
needs an impact, owner, signal, mitigation, contingency, and review trigger. A
probability-impact score helps sorting but does not replace judgment about severe
outcomes. Record assumptions with an expiry or invalidation event. Decisions need
options, authority, rationale, and affected commitments.

## Communicate at the audience's pace

For an expert TPM or sponsor: lead with what changed, impact, recommendation,
decision required, and latest useful decision date. Link detail. For a team new
to project management: pair each request with the reason it helps their work.
Neither audience needs a glossary appended to every update.

For conflict, separate facts from differing objectives. Show at least two feasible
options with who benefits, who bears cost, and what becomes impossible. Escalate
when the relevant decision rights are absent or contested. Do not manufacture
agreement or silently reassign ownership.

## Worked example: read-only dependency review

A migration sponsor wants earlier warning of slipping dependencies. The project
tracker says a test environment is ready. An approved meeting record says the
network prerequisite is still open, and neither source identifies who accepted
ownership. Give the agent read access to those sources and a weekly draft
destination visible to the sponsor. Use [the status and decision template](../templates/status-and-decision.md)
for the draft. Report the status as disputed, cite both dated records, mark the
owner unconfirmed, and ask the sponsor to decide who can confirm readiness by
the latest useful date. Escalate time-sensitive decisions using the sponsor's
existing route. The sponsor decides and authorizes any follow-up.

Compare with the existing review across comparable work windows. Count decisions
made in time to act, confirmed and missed blockers, reviewer and interruption
minutes, and cost per accepted brief. A brief counts as accepted when the sponsor
confirms that it is actionable and its evidence and uncertainty are correct. Stop
on a material data-access or authority violation, or when the agreed review
window shows sustained extra burden without decision benefit.

Route cross-project capacity or benefit decisions to
[technical program management](../../technical-program-management/SKILL.md).
Route executive attention and briefing to
[chief of staff methodology](../../chief-of-staff-methodology/SKILL.md).
[November 24 interview, 29:09 and 43:48 onward](https://softwareengineeringdaily.com/wp-content/uploads/2026/11/SED1980-Steve-Yegge-2026.txt)

## Edge conditions and exit

A request to "make the report green" does not change evidence. Prepare a truthful
report with recovery options. A user asking to send it is a separate external action;
apply authorization before posting. Avoid individual productivity rankings from
commits, tickets, or time online. These measures do not establish performance.

Complete when the user has the update or decision brief, each material uncertainty
is visible, and next actions have accepted owners or explicit ownership gaps.
