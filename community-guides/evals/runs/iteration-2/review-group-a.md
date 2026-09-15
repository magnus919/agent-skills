# Independent final-suite review — group A

Scope was limited to the current assertions in `community-guides/evals/evals.json`, the three named raw fixtures, and the actual generated guides under `/private/tmp/community-guides-final`. No skill text, earlier output, or review was used. Evidence below cites the generated guide path and line numbers; fixture citations are included where source fidelity is material.

## Score summary

| Case | Assertions passed | Failed | Result |
|---|---:|---:|---|
| `forty-five-minute-workshop` | 5/5 | 0 | Pass |
| `garden-seasonal-care` | 9/9 | 0 | Pass |
| `absent-residents-responsibilities` | 5/5 | 0 | Pass |
| **Total** | **19/19** | **0** | **Pass** |

## `forty-five-minute-workshop` — 5/5

Guide: `/private/tmp/community-guides-final/forty-five-minute-workshop/guide.md`. In this section, a shorthand citation such as `:39-45` refers to that guide path.

1. **Pass — exact 45-minute timing and usable artifact.** The run of show has nine blocks from 0:00 through 0:45, with durations 4+4+5+7+9+7+4+3+2 = 45; the guide explicitly says the blocks include transitions and interpretation pauses (`/private/tmp/community-guides-final/forty-five-minute-workshop/guide.md:31-45`). It supplies both a fictional worked card and a blank participant copy with primary, backup, accessibility, failure, review, and open-question fields (`:47-71`).
2. **Pass — participatory dissent and missing-voice handling.** Participants contribute privately before discussion, map routes and barriers, test the card, and record dissent without a forced vote; the absent-resident route provides a duplicate card/feedback slip and does not appoint an absent resident (`:39-45`, `:83-93`).
3. **Pass — supported accessibility, language, facilitation, materials, and roles.** Materials and the facilitator/note-taker setup are concrete (`:17-29`); the guide provides seated, written, paired, dictated, pass, quiet-seat, limited-English, and night-shift options (`:27`, `:75-81`). The supplied translated phrase card is used but its quality is not overstated (`:23`, `:77`).
4. **Pass — agent checks are separated from pilot evidence.** Mechanical preflight checks are listed separately (`:95-108`), while comprehension, real reachability, language review, night-shift use, local legitimacy, and real-outage usability are explicitly left to pilot/follow-up (`:110-123`).
5. **Pass — bounded intervention.** The guide states that this is one bounded intervention and not a seven-session program (`:3-7`), and closes with a pilot of this single workshop plus optional follow-up rather than a mandatory curriculum (`:123`).

### Secondary checks

- **Actual usability:** A facilitator can prepare from the named materials, run each timed block, and hand participants a blank/marked card. Completion checks are embedded in every block (`:35-45`), and the blank artifact is usable without invented contacts (`:62-73`).
- **Timing:** The displayed start/end times are contiguous and total exactly 45 minutes (`:31-45`).
- **Numbered worksheet references:** No numbered worksheet identifier is used. The named artifact is consistently the one-page outage contact/accessibility card; its worked example and blank copy both exist (`:47-71`).
- **Safety/source fidelity:** The raw fixture identifies a fictional setting and forbids diagnosis/personal-safety disclosure (`community-guides/evals/files/workshop-45-minute.json:2-9`); the guide preserves that boundary and labels the short primary/backup route as a hypothesis rather than fact (`:5-15`, `:37-45`). It does not invent local contacts (`:29`, `:55-60`).
- **Accepted versus unconfirmed roles:** Accepted actions are requested explicitly and otherwise marked unfilled; card routes remain placeholders until confirmed (`:29`, `:44`, `:49-60`, `:93`, `:127-133`).

## `garden-seasonal-care` — 9/9

Guide: `/private/tmp/community-guides-final/garden-seasonal-care/guide.md`. In this section, a shorthand citation such as `:76-83` refers to that guide path.

1. **Pass — routine care remains distinct from disaster response.** The guide explicitly describes routine horticulture/stewardship and excludes disaster response, emergency, medical, and pesticide guidance (`/private/tmp/community-guides-final/garden-seasonal-care/guide.md:8-20`, `:237-243`).
2. **Pass — fixture tasks, water limits, and observation triggers are preserved safely.** West-bed dryness, the shared rain barrel, the accessible raised bed, unknown-pest photography/discussion, conditional compost turning, and the prior tomato-staking observation are carried through (`:35-52`, `:59-66`). The guide avoids treatment, diagnosis, water guarantees, and unsupported procedures (`:116-128`, `:252-264`, `:331-345`).
3. **Pass — inclusive participation and handoffs.** Seated, observation-only, paired, short, and longer options are explicit; lifting compost and tool use are not required, and each handoff requires explicit acceptance or remains unfilled (`:85-100`, `:125-132`, `:287-300`).
4. **Pass — runnable timed activity.** The participant activity has a stated 35–45-minute normal duration and a 20–25-minute short version (`:76-83`); the matching host run is explicitly timed 0–45 minutes with completion checks (`:233-243`). It turns observation into a bounded decision and handoff (`:102-132`).
5. **Pass — blank worksheet and worked example.** The fictional example fills observation, uncertainty, decision, task, acceptance, fallback, and next-check fields (`:134-155`); the blank `SCW-1` worksheet provides those fields and decision choices (`:157-212`).
6. **Pass — next action and review trigger.** The activity closes the loop through an accepted task or unfilled fallback and a next check (`:125-132`); the follow-through record captures decisions, accepted/unfilled work, barriers, and the next review trigger (`:271-285`).
7. **Pass — participant/host agreement.** Both sections use the same observe → decide → handoff workflow, the same access choices, explicit acceptance gate, worksheet, and shared output (`:76-132`, `:213-250`).
8. **Pass — agent checks versus community pilot.** Pilot observations test actual comprehension, access choice, accepted/unfilled status, handoff information, and host explanation needs (`:302-329`); agent checks separately cover source boundaries, capability trace, worksheet walkthrough, access, safety, and cold-run consistency (`:331-351`).
9. **Pass — flexible cadence.** Seasonal windows are care windows rather than a fixed program, and the guide supports one activity, repeated ordinary care windows, or worksheet-only use (`:17-20`, `:54-57`). The pilot is explicitly one ordinary care window, not seven sessions (`:302-308`).

### Secondary checks

- **Actual usability:** `SCW-1` is identified before use, has writable fields and checkboxes, has a worked example, and is directly referenced by host preparation and the timed run (`:32-33`, `:76-83`, `:134-212`, `:217-243`). Every `SCW-1` reference resolves to that same worksheet (`:32`, `:83`, `:157`, `:219`, `:240`, `:337`).
- **Timing:** The normal host run is 5+5+5+13+8+5+4 = 45 minutes (`:233-243`); the short version is 3+3+9+6+4 = 25 minutes (`:245-250`).
- **Safety/source fidelity:** The raw fixture says the garden is fictional, avoids synthetic pesticides, requires photograph/discussion before unknown-pest action, makes compost conditional, and supplies no medical/pesticide/emergency procedure (`community-guides/evals/files/garden-seasonal-care.json:1-19`). The guide labels all supplied sources fictional/unverified and keeps those limits visible (`:17-20`, `:35-52`, `:353-370`).
- **Accepted versus unconfirmed roles:** A host must accept the role before first use; shared tasks require explicit yes/no/later or are marked unfilled; compost requires two accepted people (`:217-231`, `:241`, `:297-300`). Pilot status remains pending an accepted host (`:349-351`).

## `absent-residents-responsibilities` — 5/5

Guide: `/private/tmp/community-guides-final/absent-residents-responsibilities/guide.md`. In this section, a shorthand citation such as `:37-43` refers to that guide path.

1. **Pass — absence is not consent and status distinctions are operational.** The guide says absence, nonresponse, or reachability does not mean agreement or refusal (`/private/tmp/community-guides-final/absent-residents-responsibilities/guide.md:7-18`), defines proposed/confirmed/unfilled/declined/unknown (`:20-31`), leaves resident-a proposed rather than assigned, and does not assign absent residents (`:37-53`). It allows decline, later response, or no reason (`:13-18`, `:80-99`).
2. **Pass — primary/backup, scope, opt-in, escalation, and safe updates.** Each role has a small scope, status, confirmation gate, backup/fallback, and uncovered-work path (`:33-43`). The primary/independent-backup/escalation/recheck sequence is explicit (`:115-127`), and map/public-board update rules are defined (`:55-72`, `:222-231`).
3. **Pass — privacy and accessibility protections.** Public-board exclusions cover absence reasons, diagnoses, care arrangements, work schedules, nonresponse lists, and unapproved routes (`:55-70`). Paper/text/other approved routes, private follow-up, and practical access adjustments without diagnoses are offered (`:13-18`, `:74-99`, `:105-113`). Fixture resident states and consent limits are preserved (`community-guides/evals/files/absent-residents.json:5-23`; guide `:45-53`).
4. **Pass — agent checks versus resident pilot.** The one-round pilot tests route reachability, review-versus-acceptance comprehension, primary/backup rehearsal, and private receipt/access handling (`:129-189`); draft-only agent checks separately cover role scope/status, privacy, receipt semantics, accessibility, unresolved council route, bounded pilot, and cold walkthrough (`:206-220`).
5. **Pass — unresolved gaps and bounded review.** All five roles remain explicitly unfilled or proposed until acceptance; the council route is not invented (`:37-43`, `:168-175`). The pilot is one bounded round with optional catch-up, and review triggers are concrete (`:129-131`, `:191-204`, `:222-229`).

### Secondary checks

- **Actual usability:** The private responsibility map, resident opt-in card, fictional worked example, private receipt-check wording, pilot sequence, and pilot record are all present (`:33-43`, `:74-113`, `:155-189`). The guide is actionable without treating the public board as a census.
- **Timing:** The pilot sequence is 5+7+8+5+5 = 30 minutes, plus explicitly optional private follow-up (`:155-164`).
- **Numbered worksheet references:** No numbered worksheet identifier is used. The unnumbered opt-in card and its worked fictional example are both present and tied to the private coordination map (`:74-103`).
- **Safety/source fidelity:** The raw fixture forbids publishing sensitive absence reasons and requires confirmed/proposed/unfilled/declined distinctions and a reachability/willingness pilot (`community-guides/evals/files/absent-residents.json:1-23`). The guide does not invent a council route or service commitment (`:41-43`, `:168-175`, `:206-220`).
- **Accepted versus unconfirmed roles:** No role is operational in the draft; resident-a is only proposed, resident-d is willing to review but not assigned, absent/unknown residents are not appointed, and each role has an explicit acceptance gate (`:37-53`, `:168-175`, `:224-229`).

## Actionable findings

There are no assertion failures. The following are release/pilot actions rather than grading defects:

1. **Before the Riverside workshop, confirm real ownership and routes.** The guide correctly leaves the primary/backup/accessibility channels, translation review, and later-comment owner/deadline unresolved; the council should fill those dependencies before relying on the card (`/private/tmp/community-guides-final/forty-five-minute-workshop/guide.md:110-133`).
2. **Before the South Fork activity, accept a host and verify current ordinary conditions.** Check the actual observation route, current barrel status, available shared practice, and whether the conditional compost pair exists; otherwise retain the unfilled fallback (`/private/tmp/community-guides-final/garden-seasonal-care/guide.md:217-231`, `:349-370`).
3. **Before Oak Terrace treats any role as operational, obtain explicit acceptance and confirm approved contact/council routes.** The current guide intentionally has no accepted resident role and no verified council route (`/private/tmp/community-guides-final/absent-residents-responsibilities/guide.md:37-43`, `:168-175`, `:224-229`).
4. **Perform a print/large-print legibility check during each pilot.** Content usability is supported by the blank artifacts and instructions, but legibility in the actual paper/board format remains an empirical pilot check rather than something this Markdown artifact can prove (`/private/tmp/community-guides-final/forty-five-minute-workshop/guide.md:17-27`, `:62-73`; `/private/tmp/community-guides-final/garden-seasonal-care/guide.md:157-212`; `/private/tmp/community-guides-final/absent-residents-responsibilities/guide.md:74-99`).
