# Independent regression grading

Scope: the current manifest case `revision-from-participant-feedback` and
`community-guides/evals/files/participant-feedback.json`, plus the supplied
transfer task, fixture, and assertions. Evidence below is taken from those
inputs and the two candidate documents only. No external or human validation
is inferred.

## Totals

| Case | Result | Passed | Failed | Total |
|---|---:|---:|---:|---:|
| `revision-from-participant-feedback` | PASS | 7 | 0 | 7 |
| transfer assertions | PASS | 5 | 0 | 5 |

All assertion-level checks pass. The actionable items at the end are release
gates or wording hardening, not assertion failures.

## Case 1: `revision-from-participant-feedback`

Candidate: `/private/tmp/community-guides-final-regression/revision.md`

| # | Result | Actual evidence and audit |
|---|---|---|
| 1 | PASS | The substantive revision replaces the jargon with “power or water outage” (`revision.md:15`, `27`), keeps the night route explicitly unconfirmed (`17`, `29`), and removes the unsafe elevator instruction (`21`, `33`). The change record maps each concern: wording (`39`), night access (`40`), and safety/accessibility (`41`). |
| 2 | PASS | Provenance is explicit: “Previous version: v0.1,” “Revised version: v0.2 draft,” and the fixture path are identified (`5-9`). The candidate says v0.1 “is retained as the original supplied version” and separately records the accepted/deferred edits (`39-45`); it does not present the revision as an overwrite. |
| 3 | PASS | The candidate states that the fixture contains four comments from three residents, with R1 commenting twice, and “is not a representative vote or evidence of community consensus” (`7`). It preserves the comments separately and records limited/deferred dispositions rather than generalizing them (`39-45`). Remaining uncertainty is explicit (`47-53`). |
| 4 | PASS | Agent checks are separated from resident testing: document/source checks are listed at `55-67`, followed by a bounded community pilot at `69-80`. The pilot tests comprehension, desk-hours feasibility, accessibility, language equivalence, and format usability; the candidate expressly says document inspection is not participant-tested validation (`67`, `80`). |
| 5 | PASS | The release condition is bounded: v0.2 is “not yet validated for publication” and names the open review/pilot gates (`91`). The candidate does not require seven sessions or another arbitrary cadence. |
| 6 | PASS | The old sentence is quoted as removed (`41`, `60`), no replacement elevator procedure is supplied (`21`, `50`, `61`), and authoritative accessibility/safety guidance is identified as still needed (`41`, `50`, `91`). |
| 7 | PASS | Both resident-facing language copies are present (`13-33`). The Spanish section is labeled “draft translation — awaiting competent review” (`23`), and the candidate repeats that no translation review evidence was supplied (`9`, `52`). |

### Active resident imperative audit

The only active English resident action is: “write down the affected unit and
notify the building desk during desk hours” (`15`). The fixture supports the
same action: “document the affected unit and notify the building desk during
desk hours” (`participant-feedback.json:7`). The wording change is supported by
R1’s request for “power or water outage” (`participant-feedback.json:14`).

The only corresponding Spanish action is “anote la unidad afectada y avise al
mostrador del edificio durante el horario de atención” (`revision.md:27`),
which the candidate identifies as a translation of that same supplied action
and labels as draft (`86-87`). The remaining active-copy sentences are
unresolved-status or scope statements, not new instructions (`17-21`, `29-33`,
`89`). No imperative was added for the unconfirmed after-hours route,
accessibility plan, elevator procedure, color, or repair time.

### Required-language, label, version, and proportion audit

- English and Spanish are both retained; Spanish is explicitly awaiting
  competent review (`9`, `23`, `52`).
- Version trace runs from supplied v0.1 to draft v0.2, with the original
  provenance retained (`5-9`, `44`).
- The four comments/three-resident proportion and R1’s duplicate participation
  are stated; no consensus claim is made (`7`, `39`, `42`, `45`).
- The pilot remains bounded and focused; no arbitrary seven-session process is
  introduced (`69-80`).

## Case 2: transfer assertions

Candidate: `/private/tmp/community-guides-final-regression/transfer.md`

| # | Result | Actual evidence and audit |
|---|---|---|
| 1 | PASS | English card text is present (`8-12`) and French card text is present (`14-18`) with the same Saturday window, desk-recording action, and unresolved limitations. French is labeled “traduction provisoire; révision linguistique compétente à prévoir” (`14`), and the candidate says no review evidence was supplied (`26`, `45`). |
| 2 | PASS | Saturday 10–12 and desk recording are retained in both languages (`12`, `18`). The candidate preserves the confirmed scope—recording only, not collection or delivery (`22`)—and states Friday collection is not confirmed (`12`, `18`, `24`). Sam’s accepted role is not erased or expanded. |
| 3 | PASS | Ground-floor drop-off and Friday collection are both explicitly unresolved (`12`, `18`, `23-24`). The candidate names no alternate location, helper, or service and confirms that no such unsupported item is named (`44`). |
| 4 | PASS | The source version 0.3 and draft revision 0.4 are traced (`1-4`, `26`). T1, T2, and T3 each receive an edit or deferral (`22-26`, `41-42`). No consensus claim is made from the three feedback items; they remain individually identified. |
| 5 | PASS | Draft checks are separated from the smallest resident re-test (`28-49`). The re-test covers physical usability and whether desk recording meets the resident’s need, without adding a workshop, workbook, or arbitrary cadence. The candidate makes no participant-usability or community-approval claim (`49-51`). |

### Active resident imperative audit

The English card has two active imperatives: “Bring your item to Thread Room on
Saturday from 10 to 12” and “Ask the desk volunteer to record it” (`12`). The
fixture supplies both actions in `card.en` (`fixture.json:7`), and the confirmed
commitment supports Saturday 10–12 desk recording (`fixture.json:10`).

The French card has the corresponding two imperatives: “Apportez votre objet à
Thread Room samedi de 10 h à 12 h” and “Demandez à la personne bénévole à
l’accueil de l’enregistrer” (`18`). They correspond to `card.fr`
(`fixture.json:8`) and the same confirmed commitment (`fixture.json:10`).

The statements that no other time, ground-floor drop-off, Friday collection, or
acceptance-before-leaving guarantee is confirmed are factual limitations, not
new service instructions (`12`, `18`). The line telling a resident to verify
physical usability (`49`) belongs to the bounded re-test, not the active card,
and does not assert that an alternate service exists.

### Required-language, label, version, and proportion audit

- English and French card copies are both present and materially parallel
  (`8-18`, `41-45`).
- French is explicitly provisional and awaiting competent linguistic review
  (`14`, `26`, `45`).
- The source version 0.3 is retained and the new 0.4 label is identified as a
  draft (`3-4`, `26`).
- T1, T2, and T3 remain separate feedback items; there is no claim that three
  comments establish consensus (`22-26`).
- The response stays a small card revision plus a small resident re-test; it
  does not grow into a program (`47-51`).

## Actionable findings

No assertion-level failure was found.

1. For the Maple Court card, do not release as validated until the after-hours
   route is confirmed, authoritative accessibility/safety guidance is obtained,
   the Spanish copy receives competent review, and the bounded pilot is run;
   these are already correctly identified as open gates in `revision.md:47-53`
   and `69-91`.
2. For the Thread Room card, confirm any ground-floor arrangement, Friday
   collection, or acceptance workflow with the responsible person before adding
   an active instruction. The current candidate correctly keeps all three
   unresolved (`transfer.md:22-26`, `39-51`).
3. For maximum release clarity, label “revision 0.4” in the Thread Room title
   as “proposed draft 0.4”; the body already calls it a draft (`transfer.md:26`),
   so this is wording hardening rather than a grading failure.
