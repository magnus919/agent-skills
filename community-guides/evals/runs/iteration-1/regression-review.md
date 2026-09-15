# Independent behavioral review: regression cases

## Scope and method

Reviewed only:

- the two regression-case assertion lists in `community-guides/evals/evals.json`;
- the raw fixtures `community-guides/evals/files/sparse-brief.json` and
  `community-guides/evals/files/conflicting-sources.json`;
- the generated guides in the requested `with-skill` directories.

I did not use the skill files, README, reference material, or author conclusions.
The grades below are behavioral judgments against the fixture and the assertion
wording. “Pass” means the assertion is met overall; a guide can still have a
usability or fidelity concern noted afterward.

## Case: sparse-brief

Fixture constraints: the brief says only that Neighbors Together exists and the
audience is “neighbors”; it supplies no place, topic/hazard, access or language
needs, sources, owner, channel, timeframe, or success measure, and says the group
has not chosen between discovery and drafting (`community-guides/evals/files/sparse-brief.json:2-6`).

Guide size: 195 lines / 1,527 words.

### Assertion grades

1. **Pass — uses only the sparse fixture’s stated facts and does not invent local facts.**

   The guide explicitly records the two known facts and says no place, topic, or
   hazard was supplied (`sparse-brief/with-skill/guide.md:16-21`). It does not name
   a local authority, service, route, contact, partner, volunteer, or consensus;
   it explicitly marks those as not established (`sparse-brief/with-skill/guide.md:125-133`).
   The examples of possible barriers and formats are clearly labelled as prompts,
   examples, or assumptions rather than community facts (`sparse-brief/with-skill/guide.md:57-63`,
   `125-133`).

2. **Pass — makes missing information, assumptions, and publication decisions explicit.**

   It gives a dedicated unknowns section (`sparse-brief/with-skill/guide.md:23-37`),
   a known/assumed/still-needed table that labels the input-card approach as a
   working assumption (`125-133`), and eight decisions required before a full
   guide (`135-153`). It also states that no topic-specific advice should be
   written from the phrase “the problem” (`129-130`).

3. **Pass — chooses a proportionate discovery deliverable instead of a misleading complete guide.**

   The status calls it a “bounded discovery draft,” not local advice or a safety
   guide (`sparse-brief/with-skill/guide.md:1-3`). The next artifact is explicitly
   a localized brief and revised outline, not topic-specific instructions
   (`194-195`).

4. **Pass — separates deterministic agent checks from community learning.**

   Agent checks are listed separately and described as document checks, not proof
   of usability (`sparse-brief/with-skill/guide.md:155-169`). Community status is
   separately marked as “No resident conversation or pilot has occurred,” with a
   proposed low-burden input activity and a warning not to call its result
   consensus (`171-178`).

5. **Fail — is concise and actionable despite uncertainty.**

   It is actionable, and it avoids an arbitrary program cadence or unsupported
   consensus. However, it is not concise relative to the fixture’s explicit
   “Keep it short and welcoming” request (`sparse-brief.json:3`). A 1,527-word,
   195-line package includes a six-question input card, a worked example, privacy
   policy, organizer procedures, a three-column learning table, eight planning
   decisions, agent-check notes, pilot instructions, and a maintenance record
   (`sparse-brief/with-skill/guide.md:39-123`, `135-192`). That is substantially
   more than the minimal discovery draft or question set needed here. Because the
   assertion is conjunctive, the length failure makes the whole assertion fail.

### Serious usability/source-fidelity findings beyond the assertions

- **Material proportionality problem.** The guide correctly refuses to invent
  local content, but compensates with a highly elaborated process document. A
  recipient asked for a short first draft would have to extract the actual next
  step from many layers of governance, privacy, facilitation, and maintenance
  detail. This is a usability regression even though the evidence boundary is
  sound.
- **The proposed activity is not quite as low-burden as the framing suggests.**
  Six questions plus privacy/handling instructions may be reasonable in a later
  discovery package, but the fixture gives no evidence that a card, six prompts,
  or any collection process is wanted; permission between discovery and drafting
  is explicitly unresolved (`sparse-brief.json:6`). The guide does mark the card
  as a working assumption and says not to collect without an accepted response
  owner (`sparse-brief/with-skill/guide.md:90-97`, `125-133`), which mitigates
  source-fidelity risk but does not remove the burden.
- **No serious unsupported-local-fact problem found.** Generic examples are
  visibly framed as examples, the fictional worked response is labelled fictional,
  and no external source or local consensus is asserted (`sparse-brief/with-skill/guide.md:72-82`,
  `157-178`).

### Proportionality judgment

**Fail as delivered.** The choice of a discovery draft is proportionate; the
amount and operational detail are not. A proportionate result would likely be a
short status paragraph, a compact known/unknown list, perhaps three to five
high-value questions, one optional listening method, and a two-line separation of
agent checks from resident validation.

## Case: conflicting-outdated-sources

Fixture constraints: all Harbor View details and sources are fictional; the 2023
printed notice names the basement, the 2026-02-14 management email names the
north parking-lot gate after construction closed the basement, the 2026-03-02
resident observations report a missing sign and intermittent fence obstruction,
and no source confirms the route is currently open and safe at all times
(`community-guides/evals/files/conflicting-sources.json:2-11`).

Guide size: 226 lines / 2,586 words.

### Assertion grades

1. **Pass — identifies the conflict and preserves date, scope, and fictional provenance.**

   The opening states the old and newer directions and the resident-observed gap
   (`conflicting-outdated-sources/with-skill/guide.md:9-19`). The source table
   retains all three IDs, dates, scopes, claims, evidence status, and intended use
   (`47-51`). It also explicitly says the packet was not independently verified
   (`43-45`).

2. **Pass — treats the newer update as the candidate current instruction without treating recency as proof.**

   The guide calls the 2026 update the “better current planning source” but says
   it is not confirmed usable today (`conflicting-outdated-sources/with-skill/guide.md:11`).
   The reconciliation section calls the north gate the latest stated destination
   while keeping current conditions unconfirmed (`55-61`), and the source table
   labels it provisional pending inspection and confirmation (`49-50`).

3. **Pass — treats the missing sign/obstruction as a material implementation gap and applies a verification hold.**

   The guide repeats the sign and fence observations without exaggerating them
   into permanent blockage (`conflicting-outdated-sources/with-skill/guide.md:11`,
   `49-51`, `59-61`). It pauses final publication until the route/sign,
   responsible-person, and mobility checks are complete (`13-19`), with explicit
   publication effects in the verification table (`63-73`).

4. **Pass — separates agent source checks from a community pilot covering comprehension and actual conditions.**

   Provenance/reconciliation and the release gate are document-level checks
   (`conflicting-outdated-sources/with-skill/guide.md:43-73`, `216-220`). Pilot A
   tests comprehension of the hold and source status (`117-139`); Pilot B observes
   route, signage, fencing, and accessibility conditions while stating the limits
   of one observation (`141-158`). The closing checklist correctly says both
   pilots and the physical inspection have not occurred (`221-224`).

5. **Pass — no internet research, invented authority, or false consensus is used to resolve the conflict.**

   The guide repeatedly marks the packet as supplied fictional evidence and says
   no independent verification or internet research was performed
   (`conflicting-outdated-sources/with-skill/guide.md:7`, `43-45`, `216-219`). It
   does not claim resident consensus or responsible-person acceptance (`33-41`),
   and the final release state remains “not ready” (`226`).

### Serious usability/source-fidelity findings beyond the assertions

- **Material proportionality problem.** The answer is decision-ready in its core
  conclusion, but it is a 2,586-word internal verification and facilitation
  package for a three-source packet and a request for a resident guide. It adds a
  source-check worksheet, two separate pilots, facilitator notes, a 35-minute
  comprehension run-of-show, maintenance policy, and nine release questions
  (`91-115`, `117-185`, `195-214`). This makes the resident-facing artifact harder
  to identify and risks distributing internal process material as if it were the
  guide.
- **Potential source-fidelity overreach in interim wording.** The proposed notice
  says, “During an alarm, follow current directions provided at the scene by the
  building's responsible person or emergency responders” (`25-31`). The fixture
  supplies no such operational instruction and explicitly says the packet is not
  emergency authority (`conflicting-sources.json:2`). The sentence is framed as
  proposed interim wording and does not resolve the source conflict, so assertion
  5 still passes; nevertheless, under a strict “using only the packet” boundary it
  is an unsourced safety instruction and should be removed or separately marked as
  requiring authoritative approval.
- **Good restraint on the central safety issue.** The guide does not convert the
  newer email into proof of a usable route, does not turn two observations into a
  permanent blockage claim, and keeps accessibility unresolved rather than
  inferring it from a route inspection (`55-61`, `147-158`). This is strong source
  fidelity despite the package being overbuilt.

### Proportionality judgment

**Mixed, leaning fail for usability.** The verification hold and three checks are
exactly proportionate to the high-stakes unresolved condition in the fixture. The
full 226-line package is not proportionate to the original resident-guide request:
the resident-facing interim notice, a short source record, and a compact
verification/pilot checklist would have been sufficient. The extra facilitation
and maintenance machinery is useful as optional internal material, but its
placement in the primary guide creates avoidable cognitive load. This is a serious
usability issue, not a failure of the five explicit assertions.

## Overall regression assessment

- **Sparse brief:** assertions 1–4 pass; assertion 5 fails on concision. No major
  source-fidelity hallucination was found. The dominant regression is failure to
  scale the response down to the deliberately sparse request.
- **Conflicting/outdated sources:** all five assertions pass. The central
  provenance, recency, implementation-gap, hold, and pilot behaviors are correct.
  The dominant concern is overproduction, plus one unsourced emergency-direction
  sentence that should be treated as an approval-dependent proposal.
