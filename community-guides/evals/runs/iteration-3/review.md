# Independent latest-output grading

Scope: current assertions and supplied fixtures for the two release cases, plus the separate transfer fixture/assertions when the transfer guide was present. I did not use prior outputs or reviews. Evidence line numbers refer to the graded guide files.

## Totals

| Check | Pass | Fail | Total |
|---|---:|---:|---:|
| `conflicting-outdated-sources` | 7 | 0 | 7 |
| `revision-from-participant-feedback` | 6 | 1 | 7 |
| Fresh transfer check | 3 | 2 | 5 |
| **Overall** | **16** | **3** | **19** |

## `conflicting-outdated-sources`

**Total: 7/7 pass.**

1. **PASS — identifies the conflict and preserves provenance.** Lines 12–16 retain the 2023 basement notice, 2026 building update, and March 2026 observations with dates; lines 31–35 preserve source IDs, dates, scopes, claims, and limits. Line 6 states that the packet is fictional and not emergency authority.
2. **PASS — gives the newer update appropriate but not conclusive weight.** Lines 22–25 call the 2026 update newer and treat the north gate as the reported replacement while stating that no source confirms current safety or access. Lines 37–39 explicitly reject silently blending the notices.
3. **PASS — treats the missing sign/fence report as a material gap and sets a hold.** Lines 14 and 24–27 describe the implementation concern without overstating it; lines 41–49 define route, sign, responsible-person, and accessibility verification and keep publication paused if unresolved.
4. **PASS — separates agent checks from the pilot.** Lines 51–60 identify completed source/provenance checks and their limits; lines 62–69 separately describe proposed comprehension and actual-condition checks.
5. **PASS — no internet, invented authority, or false consensus.** Line 6 disclaims emergency authority, line 58 records no internet or physical/administrative verification, and lines 27 and 35 avoid turning two observations into an all-times claim.
6. **PASS — stays a decision brief.** The output is a dated decision, source record, verification gate, pilot distinction, and release record (lines 18–27, 29–49, 51–77). It adds no workshop, worksheet, or second pilot.
7. **PASS — does not add unsupported resident-facing emergency/technical procedure.** Lines 12–16 explicitly withhold a current route and say the old route should not be republished; line 49 keeps the replacement unresolved rather than supplying a workaround. The verification imperatives in lines 45–47 match the fixture’s minimum-verification list.

## `revision-from-participant-feedback`

**Total: 6/7 pass.**

1. **PASS — makes a substantive revision for all three supported concerns.** Lines 11–15 replace the jargon and retain the desk-hours action; lines 16–20 address the night/after-hours gap without inventing a route; lines 22–27 retire the elevator rule and identify the accessibility gap.
2. **PASS — provides traceability and preserves the original.** Lines 51–62 map each feedback item to accepted, deferred, or rejected action. Lines 64–81 preserve version 0.1 provenance and the original content verbatim rather than overwriting it.
3. **PASS — preserves dissent and uncertainty.** Lines 53–54 record that the comments are not a representative vote and that R1 appears twice; lines 61–62 explain the visual preference deferral and unsupported repair-promise rejection; lines 115–120 reject universalizing the three comments.
4. **PASS — separates deterministic checks from a community re-pilot.** Lines 83–100 list agent-checkable properties and explicitly say they are not evidence that the card works; lines 102–120 define the resident re-test questions and follow-up record.
5. **PASS — has a bounded release gate without an arbitrary program.** Lines 3–7 mark the copy as targeted-pilot material and not validated; lines 102–120 state the checks required before validation and require recording the subsequent check, with no seven-session requirement.
6. **FAIL — adds an unsupported resident-facing workaround for the unresolved accessibility plan.** Line 27 tells residents who use a mobility aid to “request the confirmed plan from building management before relying on this card.” The fixture establishes only that an accessible check-in plan is needed and remains unconfirmed; it does not establish building management as the route or that a confirmed plan can be requested there. The guide correctly removes the elevator sentence (lines 24–26), but this new imperative should also remain unresolved rather than supplying a prudent-sounding actor/path.
7. **PASS — retains English and Spanish coverage with review status.** Lines 9–27 provide the English copy; lines 29–49 provide the corresponding Spanish copy and label it “draft pending competent language review.” Lines 94–95 repeat that the review is still required; they do not claim that review has happened.

## Fresh transfer check

The transfer guide was present, so I graded it against `/private/tmp/community-guides-transfer/task.md`, `fixture.json`, and `assertions.json`.

**Total: 3/5 pass.**

1. **FAIL — bilingual copy is present and comparable, but the required review label is missing.** Lines 3–41 contain actual English and French card text with matching Saturday, access, Friday, and acceptance meaning. However, neither language section says that the new/revised French translation awaits competent review; line 59 only says the cards were “updated ... in parallel.” Add the status label without implying that review has occurred.
2. **PASS — preserves the confirmed Saturday/Sam scope and does not confirm Friday collection.** Lines 7–11 preserve Saturday 10–12 desk recording and exclude collection/delivery; lines 16–18 mark Friday collection as proposed and unconfirmed; lines 48–50 explicitly retain Sam’s accepted recording-only role.
3. **PASS — keeps access and collection unresolved without inventing a service.** Lines 13–18 state that no ground-floor drop-off or helper is confirmed and that Friday collection is unconfirmed. Lines 51–55 confirm that no alternate location, helper, or Friday promise was invented.
4. **FAIL — feedback is mapped, but initial version provenance is not explicitly preserved.** Lines 43–60 map T1–T3 and state that the supplied fixture was the only evidence, and the title identifies draft 0.4. The guide never identifies or preserves the fixture’s initial version 0.3, so it does not fully satisfy the version-provenance requirement. Add an explicit statement that 0.4 revises and preserves the original 0.3 record.
5. **PASS — separates draft checks from resident testing and stays within card scope.** Lines 62–72 list checks available from the draft; lines 74–85 identify local access, volunteer-presence, recording/acceptance, and future-option checks for residents. There is no workshop, workbook, or arbitrary cadence.

## Actionable findings

- In the participant-feedback release, remove or rewrite the line-27 instruction to contact building management. Keep the accessible check-in plan as an unresolved replacement requirement; do not invent an actor or contact path.
- In the transfer card, label the French/newly revised language as awaiting competent language review. Do not state or imply that competent review already occurred.
- In the transfer change record, explicitly preserve the initial fixture version (`0.3`) and identify the card as revision `0.4` of that record.
