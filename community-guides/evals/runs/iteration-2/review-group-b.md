# Independent grading — review group B

Scope: current `community-guides/evals/evals.json` assertions, the two named raw
fixtures, and the actual final outputs at `/private/tmp/community-guides-final/`.
I did not read the skill or earlier outputs/reviews. Language equivalence below is
a textual/package check only; it does not claim qualified human language review.

## Totals

| Case | Pass | Fail | Total |
|---|---:|---:|---:|
| `multilingual-renters-outage` | 9 | 0 | 9/9 |
| `rural-offline` | 9 | 0 | 9/9 |

## `multilingual-renters-outage` — 9/9 pass

1. **Pass — materially equivalent English, Spanish, and Vietnamese actions.**
   The English sequence and ACT-1 are at `guide.md:L50-L90`, Spanish at
   `guide.md:L192-L236`, and Vietnamese at `guide.md:L338-L376`; each language
   carries the outage steps, three scenarios, six worksheet prompts, privacy
   option, and follow-through. The matching worksheet/example sections are also
   present at `guide.md:L92-L166`, `L238-L312`, and `L381-L456`. This is a
   content-parity finding, not a claim that a qualified speaker approved the
   translations: the guide explicitly makes that review outstanding at
   `guide.md:L627-L630` and `L653`, `L727-L728`.

2. **Pass — renter/landlord boundary preserved.** `guide.md:L17-L23` forbids
   altering wiring, plumbing, meters, elevators, or building equipment and gives
   the posted-hours/after-18:00 boundary. The same prohibition is repeated in
   Spanish at `L194-L208` and Vietnamese at `L340-L352`; the activity also
   reinforces it at `L563-L567`.

3. **Pass — practical actions, escalation path, and accessibility options without
   invented authority.** The guide tells residents to identify the affected
   service, avoid exposed wires/standing water, contact the building desk during
   posted hours, avoid the elevator during power loss, and request a neighbor or
   desk accessibility check-in (`guide.md:L17-L29`, `L45-L64`). It explicitly
   withholds the utility provider, emergency number, restoration estimate, and
   after-hours contact (`L26-L29`).

4. **Pass — facts, assumptions, and unknowns are labeled.** The opening identifies
   the building and details as fictional (`guide.md:L10-L13`); the source record
   identifies supplied fixture claims and unresolved facts (`L690-L700`); the
   evidence section separates supplied, fictional-example, unresolved, and not-
   established status (`L644-L653`).

5. **Pass — runnable timed activity with follow-through purpose.** ACT-1 has a
   scenario choice and numbered participant actions (`guide.md:L66-L90`), while
   the host package provides a complete 60-minute run sheet (`L470-L521`). The
   resident section requires one action before leaving (`L168-L174`), and the
   host close records a catch-up route and review trigger (`L584-L597`).

6. **Pass — blank worksheet and completed fictional example.** English WS-1 is a
   writable form at `guide.md:L92-L145` followed by a clearly labeled fictional
   completed example at `L146-L166`; equivalent Spanish and Vietnamese forms and
   examples are at `L238-L312` and `L381-L456`.

7. **Pass — activity to next action to observable check.** WS-1 contains explicit
   action, check timing/event, and fallback fields (`guide.md:L136-L144`). The
   resident follow-through explains what can happen after the session
   (`L168-L174`), and the host closing records the next review event and unresolved
   facts (`L584-L597`).

8. **Pass — participant/host agreement.** The host points to ACT-1 and WS-1,
   specifies the same participant phases, privacy/safety behavior, and artifact
   checks (`guide.md:L510-L521`, `L632-L642`). The three-language read-aloud safety
   opening matches the resident boundary (`L523-L538`).

9. **Pass — agent checks separated from community-pilot learning.** Mechanical
   source, safety, parity, and coordination checks are separated at
   `guide.md:L601-L642`; the pilot asks about comprehension, reachability,
   accessibility, phone-free use, and catch-up (`L657-L686`). The guide states
   participant testing and translation approval are not established (`L644-L653`).

### Actionable findings

- **Publication gate:** obtain the competent Spanish/Vietnamese review and perform
  an actual phone/large-print rendered inspection before external publication;
  both are explicitly outstanding at `guide.md:L627-L630` and `L717-L728`.
- **Facilitation usability:** the detailed run sheet, debrief, and fallback
  instructions are English-only (`guide.md:L510-L597`). Provide translated host
  cue cards or confirm qualified interpretation for a host who cannot run those
  instructions clearly in all participant languages; the guide itself correctly
  says machine translation alone is insufficient (`L496-L498`).

## `rural-offline` — 9/9 pass

1. **Pass — loss of internet/cellular service is designed in.** The guide carries
   all four fixture channels and their limits: printed card, FM radio, phone tree,
   and optional in-person check (`guide.md:L20-L28`). The participant activity
   rehearses paper status plus a second channel and makes phone-tree use
   service-return-only (`L81-L100`); host materials and fallback handling are
   offline-capable (`L192-L199`).

2. **Pass — no universal device, vehicle, generator, or power assumption.** The
   guide explicitly names households without smartphones, cars, generators, or
   reliable indoor heating and makes the core action paper-based
   (`guide.md:L10-L14`, `L20-L28`). The scenario and host route work without a car,
   smartphone, continuous electricity, or travel to the grange hall (`L91-L99`,
   `L193-L199`).

3. **Pass — limits, gaps, privacy, consent, and unknowns are visible.** Channel
   limits are stated in the table (`guide.md:L22-L28`); the unverified schedule,
   reception, stock, access, consent, roles, inventory, and emergency route are
   enumerated at `L30-L40`. Worksheet sharing rules and the consent/privacy
   boundary are explicit at `L110-L113`, `L129-L137`, and `L181-L185`.

4. **Pass — runnable timed offline practice.** Module M-01 defines the capability
   and completion artifact, gives a 60-minute duration and materials, and walks
   through paper rehearsal, fallback testing, and review (`guide.md:L81-L100`).

5. **Pass — blank worksheet and fictional worked example.** W-01 has blank
   choices, status, practice, acceptance, and review fields (`guide.md:L110-L163`).
   The Pine Bend example is explicitly fictional and fills the corresponding
   fields, including fallback and review trigger (`L165-L186`).

6. **Pass — next action, observable check, and failed-channel follow-through.**
   Participants must record a next action and review trigger (`guide.md:L93-L100`,
   `L139-L148`). The worked example and host follow-through specify what to do if
   radio is not heard and what to ask at review (`L181-L186`, `L228-L241`).

7. **Pass — participant/host agreement.** Host preparation names the same paper,
   radio-optional, no-travel materials and fallbacks (`guide.md:L188-L199`). The
   90-minute run-of-show covers W-01, paper rehearsal, fallback test, acceptance,
   and close in the participant sequence (`L201-L213`), with explicit stuck/time
   fallbacks at `L219-L226`.

8. **Pass — agent checks separated from household pilot.** The guide labels agent
   checks as internal completeness only and lists the actual checks
   (`guide.md:L256-L266`). It separately states that no pilot has occurred and
   defines what a bounded household pilot must learn (`L268-L272`).

9. **Pass — no fabricated emergency guarantee or internet-dependent resource.**
   The package says it is not an emergency response or dispatch plan and that no
   coverage is guaranteed (`guide.md:L8-L14`). It supplies no external route,
   states that the fixture establishes none (`L30-L40`), records no external
   source use (`L243-L254`), and tells the host to leave emergency coverage blank
   rather than invent it (`L219-L226`).

### Actionable findings

- **Pre-publication gate:** verify WLV-88.4 schedule/reception and library
  porch-box/large-print capacity before calling this a local operating agreement;
  the guide correctly identifies both checks at `guide.md:L30-L35`, `L197`, and
  `L249-L252`.
- **Usability gate:** run the paper/large-print worksheet with households that have
  different mobility, heating, device, and radio situations. The output correctly
  says no household pilot has occurred (`guide.md:L268-L272`), so the practical
  writing space, safe status-location choice, and fallback comprehension remain
  unverified.

