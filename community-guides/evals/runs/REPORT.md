# Community Guides — evaluation report

Date: 2026-09-15. This is supplemental qualitative evidence for a new skill,
not evidence of resident-tested effectiveness, verified local advice, or a
behavioral CI release gate. All communities and source packets are fictional.

## What was exercised

- Eight portable output-quality cases: multilingual renters, rural offline use,
  ordinary garden care, a 45-minute workshop, sparse intake, conflicting sources,
  participant-feedback revision, and absent-resident responsibilities.
- Two no-skill baselines using the same model, settings, prompt, and fixture.
- Fresh independent assertion reviews; a blind comparison of both baseline pairs.
- Seven separate semantic trigger probes, not actual runtime skill-loading tests.
- A second full round after refinement, two targeted later reruns, and a fresh
  bilingual mending-space transfer check after the original release cases had
  influenced tuning. Those original release cases are no longer untouched holdouts.

All generation and independent reviews used fresh non-forked `gpt-5.6-luna`
contexts with reasoning effort `high`. Generation did not receive assertions.
Per-run token/time telemetry was unavailable, so metadata records null rather
than estimated observations. See [methods and retained records](README.md).

## Baseline comparison was mixed

The blind reviewer preferred the skill output narrowly for a novice workshop
host, but preferred the baseline narrowly for ordinary garden use. Both baselines
already met the reviewer's literal assertions. More detail was not automatically
better: initial skill outputs were 3,412 versus 1,605 words for the workshop and
4,761 versus 3,269 for the garden. The second skill round reduced those to 2,096
and 3,563 respectively, without a fresh blind baseline comparison.

The initial reviewer passed garden instruction agreement despite finding a host
reference to nonexistent worksheet sections. The integrating author rejects
that pass: the referenced fields must actually exist. The workshop's incorrect
checkbox count was also retained as a defect. Both motivated an explicit
reference/count check in the skill. Do not infer universal uplift from two pairs.

## Failures drove general rules

| Observed failure | General correction |
|---|---|
| Sparse first response grew to 1,527 words | Bounded discovery, normally under 300 words and at most three essential questions |
| A source conflict expanded into a program | Narrow card/brief scope explicitly overrides the full-program handoff checklist |
| Revision added unsourced safety/interim advice | Audit resident-facing imperatives against supplied evidence; leave missing procedures unresolved |
| Revision dropped Spanish while promising later translation | Translation may express supported facts without adding facts; deliver each required language as reviewed or clearly unreviewed draft copy |
| Host references and worksheet labels disagreed | Resolve named/numbered references and checkbox counts against delivered artifacts |
| Responsibility checks omitted contradictory commitments | Check acceptance, availability overlaps, backup independence, and preservation of already accepted scope |

The original responsibility assertion was also corrected: forcing the literal
label “unavailable” was not a meaningful quality test when the fixture used
“declined.” The replacement tests consent, accepted scope, proposals, gaps, and
the ability to decline without giving reasons. Initial assertions are retained.

## Second full round

Generation used skill content associated with `5b71a61`; the conflict run started
earlier and reported that SHA at completion, so its exact loaded revision is not
atomic. Sparse/conflict were graded against the later strengthened assertions.

| Case | Independent assertion result | Integrating-author disposition |
|---|---:|---|
| Multilingual renters | 9/9 | Agent content checks passed; competent language review and rendered phone/large-print checks remain |
| Rural offline | 9/9 | Agent checks passed; actual reception, resources, access, and household pilot remain |
| Garden care | 9/9 | Named worksheet and timed host sequence present; actual garden pilot remains |
| 45-minute workshop | 5/5 | Exact 45-minute agenda, resident artifact, dissent and catch-up paths present |
| Sparse brief | 6/6 | 292 words, three questions; proportionate discovery |
| Conflicting sources | 6/7 | Rejected for an overbuilt brief; targeted rerun required |
| Participant revision | 6/7 | Rejected for omitted Spanish; also rejected unsupported interim reporting/emergency-process directions that the reviewer underweighted |
| Absent-resident responsibilities | 5/5 | Confirmed limited opt-in is distinguished from proposed expanded roles; private opt-in and gaps explicit |

The reviewers' 55/57 aggregate is not an acceptance score: the author's additional
source-boundary objection remains visible rather than being averaged away.
The initial code reviewer also cited historical iteration-1 failures as current;
the follow-up corrects that evidence boundary. Raw reports are preserved, not
silently repaired. A reviewer is another fallible check, not proof of correctness.

## Latest targeted checks

The two targeted reruns and the fresh transfer check use `012933a`. They do not
constitute a third full-suite run. See `iteration-3/` and `transfer-check/` for the
actual outputs and independent review.

| Targeted case | Result | Disposition |
|---|---:|---|
| Source conflict | 7/7 | Concise enough for the requested decision, no invented route |
| Participant revision | 6/7 | Spanish restored, but an unsupported resident instruction to request a plan from building management remained |
| Fresh mending-space transfer | 3/5 | Preserved limited commitment and both languages; omitted competent-translation-review label and previous version identifier |

Those failures drove the compact revision template at `b0dd0dd`: each active
resident imperative needs a supplied-source evidence cell, every new translated
copy needs its review-status label, and the original version must be explicit.
The transfer case is therefore no longer an untouched holdout after this point.
This is another targeted regression round, not evidence of a new full-suite pass.

The final independent [regression review](final-regression/review.md) passed the
participant revision **7/7** and the now-familiar transfer case **5/5**. The
integrating author also checked the active card instructions: only supplied
actions remain, language copies are present with draft-review labels, and prior
versions are named. The review's suggested title hardening is non-blocking because
the transfer body already says draft. Raw outputs remain unedited.

There is no new all-eight run at `b0dd0dd`: the last six unaffected case results
come from the second full round, source conflict from `012933a`, and revision
from this final targeted run. These are revision-specific observations, not a
single final-revision 100% score or a reliability estimate.

## Structural and visual verification

The optional standard-library checker passed its nine focused tests, including
invalid types, timing/reference consistency, path containment, and malformed input.
The bundled plan validates with the intentional proposed-maintainer warning.
Repository skill-format, changed-skill quality, eval-manifest, eval-coverage,
test-registration, and generated catalog checks passed during development.
The normal skill-local pytest invocation uses CI's override of the repository's
core-coverage defaults; the first unoverridden attempt passed nine tests but failed
the unrelated core coverage threshold. This is not reported as a passing command.
The first full artifact-check attempt was blocked by the local sandbox preventing
existing unrelated tests from binding localhost mock servers. The same command
passed after that restriction was lifted (exit 0); no product changes were made
to accommodate that environment restriction.
Authored-file whitespace checks pass when excluding raw run evidence. The raw
Markdown retains original hard-break spaces and trailing blank lines, so an
unfiltered `git diff --check` reports those; evidence was not silently normalized.
The first PR CI run caught the test's bare local-module import as an undeclared
dependency. The test now loads the sibling checker by explicit file location,
matching existing skill-local tests; checker behavior is unchanged. Both focused
test runners still pass nine tests. The dependency check uses the repository
virtual environment because the system Python does not have `deptry` installed.

A fresh agent cold-walked the original apartment example and host notes: the
three 40-minute agendas, preparation, W1/W2/W3 references, fallbacks, and catch-up
route were runnable on paper. The integrating author also rendered the actual
two Markdown files to local HTML with `marked` and inspected the opening, worksheet
areas, and host sections in the browser. Those inspected regions were legible
without clipping. This was desktop HTML inspection, not PDF pagination, full
mobile/large-print certification, or a participant pilot. The PDF renderer lacked
a native library; no completed PDF is claimed or bundled.

## Release interpretation and remaining limits

This ships a methodology, original templates/example, structural checker, and
reproducible evaluation inputs with retained behavioral evidence. It does not ship
a verified guide for any real place. The skill's output still requires the named
human/content checks, especially for translations and safety-relevant claims.

Single runs on one model cannot establish reliability rates or predict another
model's behavior. Longer outputs can burden hosts. The bilingual worked example
is explicitly an English source example awaiting Spanish support, not a completed
bilingual edition. No residents participated, no language professional approved
translations, and no real service or route was verified. Runtime skill discovery,
automated grader bindings, freshness, and behavioral release gating were not tested.
