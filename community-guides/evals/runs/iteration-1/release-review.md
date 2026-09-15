# Independent release review

## Scope and method

Reviewed only the requested assertion blocks in
`community-guides/evals/evals.json`, the two raw JSON fixtures, and these
generated outputs:

- `/private/tmp/community-guides-evidence/revision-from-participant-feedback/with-skill/guide.md`
- `/private/tmp/community-guides-evidence/absent-residents-responsibilities/with-skill/guide.md`

The second output was absent at first, appeared during a bounded wait, and was
byte-stable across a five-second check before review. I did not read the skill
or any author conclusions, and I used no internet or external source.

Grades are against the literal assertions, with line references to the
assertions, fixtures, and outputs. A pass means the output provides the
asserted behavior; it does not mean every proposed operational detail is
already locally verified.

## Grade summary

| Case | Result |
|---|---:|
| `revision-from-participant-feedback` | 5/5 pass |
| `absent-residents-responsibilities` | 3/5 pass, 2/5 fail |

## `revision-from-participant-feedback`

Fixture evidence: the comments are from three residents and are not a
representative vote (fixture lines 2-3); the supported issues are plain
wording, a closed-desk workflow gap, and an unsafe elevator sentence with an
accessibility need (lines 14-16). The repair guarantee and neon-green request
are explicitly unsupported/preference feedback (line 17). The fixture also
requires preserved history and re-testing (lines 19-22).

### Assertion 1 — PASS

The revision replaces the jargon with “power or water outage” (output lines
10, 62-66), adds a closed-desk workflow while refusing to invent an unconfirmed
contact (lines 18-28), and removes the duration-based elevator instruction in
favor of an accessibility/check-in plan (lines 30-51). The change record maps
these three supported concerns directly at lines 117-119.

### Assertion 2 — PASS

The original 0.1 wording is reproduced as an unchanged provenance record at
output lines 91-102. The participant comments remain distinct at lines
104-111, and the concise change record identifies the decision, edit/reason,
and open item for each comment at lines 113-123. This is traceability rather
than a silent rewrite.

### Assertion 3 — PASS

The output explicitly says the comments are not a representative vote and
preserves them as distinct observations (lines 104-111). It defers the visual
preference rather than making it universal (line 120), rejects the unsupported
repair guarantee (line 121), and labels the result pilot-ready rather than
validated (lines 3-6, 123).

### Assertion 4 — PASS

The output separates document/cold-walkthrough checks from claims that require
real-world evidence (lines 125-143). It separately lists pilot tests for
night-shift reporting, route reachability, accessible check-in, bilingual
comprehension, and real print conditions (lines 145-159). It also identifies
the Spanish review as not evidenced by the fixture (lines 62-66, 80), rather
than pretending translation validation occurred.

### Assertion 5 — PASS

The release boundary is bounded: verify the route, then run the first bounded
pilot before distribution/reliance (output lines 70-89 and 145-159). The
maintenance record repeats concrete triggers—before distribution, after route
verification, and after the first bounded pilot—at lines 161-172. No arbitrary
seven-session process is required.

### Practical usability and supported-commitment review

The card is usable as a resident-facing template, but it is not operational
for overnight use until the blank after-hours method, contact/location,
verifier/date, and fallback are filled and verified (output lines 18-28,
70-76). This is an appropriate release block given that the fixture says the
after-hours contact is not confirmed (fixture line 9). The proposed fallback
of reporting when the desk opens is clearly presented as what to do when no
dependable overnight route exists, not as an emergency response commitment
(output lines 20-23, 82-84).

The output does not promise a repair time or invent a number, volunteer, or
local service commitment (lines 53-58, 120-122, 127-134). The owner/manager
is a proposed party to verify the card, not a fact established by the fixture;
the output appropriately leaves ownership unconfirmed at lines 163-171.

### Safety-related source fidelity

The fixture supports identifying the old elevator sentence as unsafe and
adding an accessible check-in need, but it does not provide authoritative
elevator, emergency-response, or local emergency-number guidance. The new
advice—do not use an unconfirmed elevator, use its alarm/emergency
communication method if stopped, and use the area's emergency service number
in immediate danger (output lines 30-40)—is prudent general guidance, but it
is not traceable to this offline fixture. It should therefore be treated as
proposed safety copy requiring local/qualified review before release, not as a
fixture-verified commitment. The output avoids inventing a specific number and
does not claim that this advice was externally validated.

## `absent-residents-responsibilities`

Fixture evidence: resident-a is confirmed only for board-update opt-in;
resident-b and resident-c are absent with unconfirmed consent; resident-d is
reachable by text and willing to review but has no chosen role; resident-e is
unknown (fixture lines 5-10). The available roles and the privacy, opt-in,
rotatable-workload, and pilot constraints are at lines 12-23.

### Assertion 1 — FAIL

The output correctly refuses to assign absent residents and distinguishes
confirmed, proposed, unfilled, and declined in its status key (output lines
23-34). It also says that “not available” is an acceptable response (lines
98-100). However, it never defines or uses **unavailable** as a distinct map
status. The responsibility map statuses at lines 38-44 use proposed and
unfilled; the status key substitutes declined for unavailable. “Not available”
as a resident phrase is not the same as distinguishing an unavailable
responsibility state. This misses the assertion’s explicit confirmed/proposed/
unavailable/unfilled distinction.

### Assertion 2 — PASS

Every listed role has primary/backup treatment, a bounded role scope, an
acceptance step, and a fallback in the map at output lines 38-44. The rules
require explicit opt-in, a defined period, and a review point (lines 50-64).
Uncovered work remains visibly unfilled, and the escalation owner is not
claimed until someone opts in (lines 41, 44, 60-61). The map can be updated
after withdrawal and role changes (lines 62-64, 200-214).

### Assertion 3 — PASS

The output keeps absence reasons, diagnoses, household-level receipt status,
and private numbers off the public board (output lines 13-21, 115-116). It
offers text-only contact, alternative formats/routes, private requests, and
no-reason-needed participation at lines 42-43, 74-80, and 96-100. It records
“not reached” without inferring a reason (lines 46-48, 108-116). The fixture’s
work/caregiving categories are not published, and the guide provides a safe
generic path for anyone needing accommodation.

### Assertion 4 — FAIL

The output clearly separates agent checks from the resident pilot (output
lines 180-198) and covers coverage, privacy, and confirmation/status. It does
not, however, state or demonstrate a distinct **contradiction check**. The
one-person/two-role rule at lines 147-150 is a pilot operating rule, not an
agent regression check, and the agent-check list at lines 182-194 contains no
check for contradictory assignments, statuses, or role claims. The assertion
therefore fails on the explicit contradiction-check requirement, although the
reachability, willingness, and workload-feasibility pilot design itself is
present at lines 118-170.

### Assertion 5 — PASS

The guide identifies unresolved roles and contact/ownership gaps throughout the
map (output lines 38-48, 166-170), treats no accepted role as a valid
unfilled result (lines 166-170), and defines review triggers after the pilot,
when roles change, or when the guide/contact route changes (lines 200-214).
It explicitly uses one bounded cycle and says it is not a seven-session
program (lines 118-121).

### Practical usability and supported-commitment review

The guide is operationally cautious and usable as a pilot packet: it gives
residents scripts for volunteering, declining, requesting another format, and
withdrawing; it gives coordinators a private receipt-check procedure; and it
specifies what evidence to retain and what to publish (output lines 66-116,
154-170). It correctly does not provide actual phone numbers, a council
contact, or an already-approved public route because none exists in the
fixture. “Use the resident-approved route shown on the board” is therefore a
placeholder dependency, not a currently supported operational commitment
(lines 82-100, 172-178).

The role invitations to resident-a and resident-d are proposals, not
assignments, and the output repeatedly preserves that boundary (lines 31-34,
40-44, 127-135). The proposed one-reminder limit, removal of names after
withdrawal, and aggregate-only pilot notes are sensible safeguards, but they
are additions to the fixture rather than facts supplied by it; they should be
kept as proposed process rules subject to resident approval.

### Safety-related source fidelity

There is no physical safety instruction in the absent-residents fixture or
output that needs external factual validation. The safety/privacy posture is
largely faithful to the supplied constraints: no coercion, no disclosure of
absence reasons, no diagnosis collection, explicit consent, and safe
escalation boundaries (fixture lines 19-23; output lines 13-21, 44, 98-100).
The output should still avoid presenting the unconfirmed board route or
council contact as available until residents approve and verify it.

## Release disposition

Do not treat either guide as fully operational yet. The revision guide is
ready for the stated agent checks and a bounded pilot, subject to local review
of the new safety wording and completion/verification of the after-hours
route. The Oak Terrace guide is suitable as a privacy-preserving pilot draft,
but the release artifact should add an explicit **unavailable** status and an
agent-level contradiction check before claiming full assertion compliance.
