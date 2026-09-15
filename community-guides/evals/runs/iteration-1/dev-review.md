# Independent review: `multilingual-renters-outage` and `rural-offline`

Review date: 2026-09-15

## Scope and method

Reviewed only:

- `community-guides/evals/evals.json` assertions for the two `dev` cases;
- `community-guides/evals/files/multilingual-renters-outage.json`;
- `community-guides/evals/files/rural-offline.json`;
- `/private/tmp/community-guides-evidence/multilingual-renters-outage/with-skill/guide.md`;
- `/private/tmp/community-guides-evidence/rural-offline/guide.md`.

I did not read the `community-guides` skill or author notes. Line references below are to the rendered outputs unless a fixture is explicitly named. Language parity is an LLM content-parity assessment only; this is not competent Spanish or Vietnamese community-language review, and the outputs correctly identify that limitation.

## Summary

| Case | Assertion result | Independent usability result |
|---|---:|---|
| `multilingual-renters-outage` | 9/9 PASS | Strong package structure and safety boundaries. Not actually publication-ready: competent Spanish/Vietnamese review and a resident pilot remain required. Phone/large-print usability is specified but not demonstrated by rendered artifacts. |
| `rural-offline` | 9/9 PASS | Strong offline and consent boundaries, with a runnable 75-minute module. Not a proven operating plan: channel reach, stock, access, roles, and household usability remain unverified. |

No assertion failed. The pass results do not mean the guides are locally validated or ready for external publication.

## `multilingual-renters-outage`

Output reviewed: `/private/tmp/community-guides-evidence/multilingual-renters-outage/with-skill/guide.md`.

### Assertion grades

1. **PASS — materially equivalent actions and warnings in all three languages.**

   English gives the seven core actions at lines 59–67. Spanish gives the corresponding seven actions at lines 159–167, including `No use el ascensor` and the unresolved-contact/restoration warning. Vietnamese gives the corresponding seven at lines 261–269, including `Không dùng thang máy` and the same unresolved-contact/restoration warning. Each language also has its own activity, blank worksheet, and worked example (English lines 69–150; Spanish 169–251; Vietnamese 271–353). This is substantive parity, not title-only translation.

   LLM-only parity check: the safety boundary, affected-service note, building-desk contact, accessibility check-in, and no-invention warning are all present in the three quick cards. The fixture-approved terms are retained, as shown at lines 253 and 355. A competent human reviewer still needs to validate naturalness, register, and safety meaning.

2. **PASS — renter/landlord boundary is preserved.**

   The English copy says, “Do not alter wiring, plumbing, meters, elevators, or building equipment” and separately prohibits elevator use during a power outage (lines 61–63). Spanish and Vietnamese carry the same prohibition at lines 162–163 and 264–265. The host fallback also says a repair proposal is only a question for an authorized building decision-maker (lines 400–403). No participant step asks renters to inspect, reset, repair, or operate equipment.

3. **PASS — practical action, contact/escalation path, and accessibility options without unsupported local claims.**

   The practical path is to move away from hazards, record unit/service, contact the building desk during posted hours, and request an accessibility check-in from a neighbor or the desk when needed (lines 59–67). The worksheet makes the unresolved alternatives explicit: “Desk not reached; no other contact is confirmed,” with restoration time, utility provider, after-hours contact, and emergency procedure listed as unknowns (lines 123–132). Accessibility is handled without requiring stairs, voice calls, or disclosure of a reason (lines 117–121 and 404–405). The document explicitly supplies no emergency number, utility provider, after-hours contact, or restoration time (lines 20–24 and 496–503).

4. **PASS — fixture facts, assumptions, and unresolved local details are labeled.**

   The opening labels Maple Court and the example people/units as fictional and says the package is not legal, emergency, utility, or restoration guidance (lines 8–12). The “Known brief” separates fixture-bounded answers from missing local facts and an unconfirmed owner (lines 30–42). The source record identifies the two fictional source IDs and their status (lines 540–545), while explicit unresolved facts are listed at lines 547–555. This prevents the synthetic packet from being presented as authoritative local information.

5. **PASS — runnable timed participant activity with follow-through purpose.**

   The “Make an Outage Ready Note” activity has a stated purpose and approximately 15-minute duration (lines 69–74), six executable steps (lines 75–82), a fictional scenario, and a retained note. The host run plan gives a concrete 45-minute session with worksheet completion, scenario practice, next-action check, and close (lines 373–384). The activity is therefore an intervention that produces an artifact, not merely outage explanation.

6. **PASS — blank worksheet and completed fictional example.**

   English has a completed example at lines 84–96 and a blank worksheet at lines 98–150. The same pair exists in Spanish at lines 184–251 and Vietnamese at lines 286–353. The examples are explicitly labeled fictional, and the worksheets include safety, privacy, unresolved facts, next action, and check fields.

7. **PASS — activity → next action → observable check/review trigger.**

   The outcome map makes the chain explicit: the completed note is kept and used at the building desk, with a check that it contains unit, service, time/unknown, and no invented contact/restoration time (lines 44–51). The worksheet asks for “My next action and when” and “How will I check?” (lines 134–149). After the session, the host records accepted shared tasks or an unfilled role and provides a catch-up route (lines 383–410); the pilot also tests whether the next action is feasible (lines 517–526).

8. **PASS — participant and host instructions agree.**

   The participant activity requires the quick card, private worksheet, safety choice, desk plan, and retained note (lines 75–82). The English host agenda repeats those same steps, safety limits, 15-minute worksheet block, scenario, next-action check, and resulting artifact (lines 373–384). Spanish and Vietnamese facilitator agendas preserve the same seven time blocks and checks at lines 420–435 and 445–460. The language-specific facilitator notes are shorter than the English host package, but they do not contradict it; a facilitator relying only on a non-English section would still need the English “if stuck” and records/privacy detail.

9. **PASS — agent preflight is separated from community-pilot learning.**

   Agent checks are explicitly scoped to source/safety parity, package completeness, timing, and document structure (lines 464–503). The pilot section says the guide is not participant-tested and asks residents about comprehension, accessibility, language equivalence, timing, feasible next action, and real building facts (lines 507–535). The document does not treat its own checks as community evidence.

### New-facilitator usability

The package is runnable from the document: it has preparation steps (lines 363–371), a 45-minute run plan (373–384), host words in all three languages (386–394), stuck-session fallbacks (396–405), privacy/record handling (406–410), and absent-participant catch-up. A new English-speaking facilitator can identify materials, timings, completion checks, and what not to promise without consulting the author.

The main usability risks are real but do not fail the assertions:

- The output is a 568-line Markdown document, not actual phone and large-print deliverables. It instructs the host to offer 16-point text and a phone-readable version (lines 363–366), but it does not demonstrate a rendered layout. The worksheets are wide Markdown tables, so phone overflow and print pagination remain untested.
- The Spanish and Vietnamese participant packages are substantial, but the language-specific facilitator sections are abbreviated. A facilitator who cannot use English would not get the full English “if the session gets stuck” and records/privacy guidance in their language.
- Translation quality is explicitly unverified. The output says machine translation alone is insufficient and requires competent reviewers (line 367), and the pilot asks whether Spanish/Vietnamese are natural and equivalent (lines 522–523). That is the correct boundary, but it means actual language accessibility is not yet established.
- The accessibility path is privacy-preserving and offers writing, drawing, passing, phone/print choices, and a chosen helper (lines 77–82 and 398–405). Whether residents can understand and use those options is correctly left to the pilot, not claimed from document inspection.

### Invented-claim and safety check

I found no unsupported utility, legal, emergency, restoration, or after-hours claim. The fictional worked example is clearly labeled (lines 84–96), and proposed design choices such as 15/45-minute timing, 16-point text, and a pilot group are presented as package design or verification steps rather than local facts. The one potentially easy-to-misread item—“posted hours”—is repeatedly left unconfirmed (lines 369 and 498), consistent with the fixture.

## `rural-offline`

Output reviewed: `/private/tmp/community-guides-evidence/rural-offline/guide.md`.

### Assertion grades

1. **PASS — designs for loss of internet and cellular service with redundant channels.**

   The package states the 48-hour no-internet/no-cellular condition and no-device/no-power constraints (lines 8–21). Its channel card covers printed card, FM radio, phone tree, and in-person check, with a visible limit for each (lines 68–78). The offline fallback ladder distinguishes paper, consented paper location, battery radio, accessible in-person exchange, and the later network-dependent phone tree (lines 80–100).

2. **PASS — no smartphone, car, generator, or reliable-power assumption, with alternatives.**

   Design choices explicitly say instructions and worksheets are printable, no car/ridge/grange travel is required, no powered meeting place is assumed, and roles remain unfilled until accepted (lines 56–66). The activity requires only paper, a pencil, and an optional battery radio; it explicitly lists no address, phone, radio, vehicle, internet, or electricity as required (lines 102–117). The host preparation repeats that no phone, internet account, car, battery radio, or payment is required (lines 255–267). This is a concrete alternative, not just a disclaimer.

3. **PASS — channel limits, coverage gaps, privacy/consent, and unknowns are visible.**

   Limits are attached to every channel: weekly rather than continuous paper-stock checking, possible radio non-reach, network dependence of the phone tree, and inaccessible/non-required grange travel (lines 73–78). The guide warns that silence or a missed mark does not prove household safety (lines 16–21), requires consent for a paper status location (lines 42–44 and 88–90), and keeps private information out of shared worksheets (lines 23–27 and 173–181). Unverified schedule, reception, stock, access, consent, and roles are enumerated with evidence needed at lines 351–371.

4. **PASS — runnable timed offline communication practice.**

   Module `WC-OFF-01` has a 75-minute duration, materials, prerequisites, and an observable completion condition (lines 102–117). The participant steps write a neutral paper message, relay it without a device, remove one channel, record what remains possible, and choose a follow-through action (lines 144–171). It deliberately practices communication rather than falsely claiming a real household check.

5. **PASS — usable blank worksheet and completed fictional example.**

   W1 is a concrete blank worksheet with private preference, two-channel decision, paper relay, and follow-through/limits sections (lines 173–222). The Birch example fills those same fields and explicitly leaves consent, helpers, coverage, and the fallback unconfirmed (lines 224–247). The example is usable as a model without pretending to establish a real household plan.

6. **PASS — activity → next action → check/review, including channel failure.**

   The remove-one-channel step requires participants to mark what still works, what cannot be claimed, and what needs verification (lines 162–165). W1 records an individual action, a community fact to verify, accepted versus proposed action, and a check date/trigger (lines 211–222). Host follow-through records accepted/unfilled roles, the no-role fallback, catch-up, and evidence for the next check (lines 322–335); maintenance adds review triggers after failed rehearsal, channel change, or withdrawn role (lines 373–392).

7. **PASS — participant and host instructions agree.**

   The host notes explicitly say they match `WC-OFF-01` and W1 (lines 249–253). The 75-minute agenda covers the same access boundaries, channel limits, W1 inventory, paper relay, remove-one-channel test, follow-through, and close described for participants (lines 276–286). Fallbacks for no partner, no paper, missing interpretation/access support, and time pressure preserve the participant activity's stated limits (lines 303–320).

8. **PASS — agent checks and household pilot are separate.**

   The agent section identifies document-only checks such as tracing capability through W1, cold walkthrough, field consistency, and absence of device/car/power assumptions (lines 394–407). It explicitly says those checks do not verify reception, stock, physical access, consent, role acceptance, language support, or household usability (lines 409–411). The household pilot is separately scoped to representative willing households and asks whether they can complete W1 and the relay, what barriers occurred, and whether the next action fits (lines 413–423).

9. **PASS — no fabricated emergency guarantee or internet-dependent promise.**

   The opening says the package is not a live response plan, medical service, welfare-check system, emergency coverage, shelter, evacuation route, or functioning-network promise (lines 16–21). The host is instructed to refuse professional-care or urgent-response requests without inventing local emergency instructions (lines 318–320). The final handoff repeats that this is not a promise of emergency coverage (lines 425–427), and the phone tree is explicitly marked as network-dependent rather than offline (lines 76–78 and 98–100).

### New-facilitator usability

This is unusually usable as a cold-start facilitator document. It names the module and worksheet IDs, materials, prerequisites, duration, completion checks, host words, stuck-session branches, catch-up steps, follow-through record, maintenance triggers, and pilot questions. The agenda arithmetic is correct: 10 + 10 + 12 + 20 + 13 + 5 + 5 = 75 minutes (lines 276–286).

The main usability risks are actual-validation risks rather than missing instructions:

- The guide supplies an offline-capable paper process, but it does not make a paper plan into coverage. It correctly says paper-in-hand is an individual fallback and that no shared channel or roster is implied when no role is accepted (lines 329–334 and 390–392).
- The workshop can be run without electricity, but physical venue access, large-print supply, interpretation, radio reception, library stock, and a host are not established. Preparation tells the facilitator to verify these before advertising (lines 255–272), and the open-items table identifies the evidence needed (lines 357–367).
- The W1 tables are dense and wide. The document recommends large print, private writing, proxy writing, and paper timing, but there is no rendered print sample or accessibility test in the supplied output. Actual legibility and completion burden remain pilot questions (lines 415–423).
- The default paper option is safe but intentionally limited: it cannot establish that anyone received a message. The guide makes that limitation explicit rather than hiding it (lines 82–100 and 128–142).

### Invented-claim and safety check

I found no fabricated emergency-service guarantee, current official instruction, phone number, or internet-dependent resource presented as available offline. The only concrete local channels and capacities are repeatedly marked fictional/supplied and unverified (lines 68–78 and 255–269). Design proposals—75-minute timing, Birch, sample messages, paper-only timing, and pilot composition—are clearly framed as exercise choices or fictional examples, not Willow County facts.

## Overall disposition

Both outputs pass every listed assertion on the evidence reviewed. They are strong drafts for controlled pilot use, not validated resident-facing operating plans. Before publication or live use, the highest-value gates are:

1. render and inspect the phone and large-print artifacts rather than relying on Markdown instructions;
2. obtain competent Spanish/Vietnamese language review for the multilingual package;
3. verify local channels, access arrangements, contacts, supplies, and role acceptance;
4. run the bounded resident/household pilots and record comprehension and practical barriers without collecting unnecessary private data.
