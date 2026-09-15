# Independent code/content review: `community-guides`

Reviewed committed diff `origin/main..HEAD` at:

`5b71a61eb4910b2e4c8d389e00403bd6addb0ace`

The repository itself was not edited. The worktree is not clean: 15 untracked
files exist under `community-guides/evals/runs/iteration-1/`; they are evaluation
artifacts, not part of the committed diff.

## Findings

### P1 — Source-only technical boundary is not held at the resident-facing output boundary

**File/lines:** `community-guides/SKILL.md:73-77`; evidence in the working-tree
run artifacts `community-guides/evals/runs/iteration-1/revision-from-participant-feedback/with-skill.md:30-40`
and `community-guides/evals/runs/iteration-1/conflicting-outdated-sources/with-skill.md:23-31`.

The skill correctly says that supplied-source-only work must not invent a new
technical procedure. However, the revision output presents elevator operation,
emergency-communication, and area-emergency-number instructions as resident-facing
copy even though the supplied fixture contains no authoritative replacement. The
source-conflict output similarly adds “follow current directions ... by emergency
responders,” which is not in the supplied source packet. Calling the latter
“proposed interim wording” does not make the unsourced safety instruction source-only.

Fix by making the boundary operational: quarantine unsupported safety prose outside
the resident card/decision brief, label it explicitly as an approval-dependent
placeholder, and state that the resident-facing artifact must say the replacement is
unresolved until an authoritative source is supplied. Add the same negative
assertion to the source-conflict eval.

### P1 — Narrow-request scope still conflicts with the unconditional handoff workflow

**File/lines:** `community-guides/SKILL.md:48-52` versus `community-guides/SKILL.md:159-164`.

The new rule says a narrow revision or source conflict should produce only the
requested edited card/decision brief plus concise change and verification notes,
without a workshop, new worksheets, or multiple pilots unless explicitly needed.
The later handoff section still unconditionally requires sources/adaptation notes,
a maintenance record, unresolved-fact/role accounting, an owner, and a review date.
That is a contradictory default and explains the observed overproduction: the sparse
run is 195 lines/1,527 words and the source-conflict run is 226 lines/2,586 words,
including organizer/facilitator material, maintenance material, and pilot machinery.

Fix precedence explicitly: the narrow-deliverable rule must override the full
program handoff checklist. Require maintenance/ownership artifacts only when the
requested artifact or an existing package calls for them; otherwise keep concise
verification notes with the requested card or brief.

### P2 — The new sparse/source-conflict limits are not protected by the portable eval contract

**File/lines:** `community-guides/evals/evals.json:82-107`, relative to the scope
rules in `community-guides/SKILL.md:40-52`.

The sparse case asserts only that the output is “concise” and proportionate; it does
not assert the documented approximately-300-word/at-most-three-question discovery
shape or prohibit a workbook, facilitation manual, repeated unknowns tables, or
publication process. The source-conflict case asserts provenance and a verification
hold, but does not assert the new edited-card/decision-brief shape or prohibit
unrequested workshops, worksheets, or extra pilots. A future output can therefore
violate the new scope contract while the manifest remains fully passing.

Add observable assertions for the bounded discovery shape and narrow source-conflict
deliverable, including the source-only prohibition on unsourced technical procedures.
Keep qualitative usability assertions separate from the mechanical size/count checks.

## Checker contract and packaging

No checker-contract discrepancy was found. `references/guide-plan.md` agrees with
`scripts/validate_guide.py` on required fields, positive integer timing, empty-list
rules, ID/reference checks, relative paths, symlink containment, date/status values,
JSON diagnostics, and exit codes. The checker is intentionally structural and does
not claim to validate prose, translations, source currency, host agreement, or
participant usability.

Catalog and packaging checks passed: `validate-skills.rb`, reference validation,
Claude marketplace freshness, Codex plugin freshness, `llms.txt` freshness, test
naming coverage, eval-manifest validation, and artifact consistency.

## Cold facilitator walkthrough

**Result: pass for the bundled fictional exercise, with explicit limits.** Using
only `examples/apartment-guide.md`, `examples/apartment-facilitator.md`, and
`examples/apartment-plan.json`, a new facilitator can identify the three modules,
the W1/W2/W3 references, preparation, participant steps, exact 40-minute agendas,
fallbacks, closing decisions, and catch-up path. The guide contains the referenced
worked examples and blank fields. The plan checker returns `valid: true` with the
documented warning that maintenance ownership is proposed.

The example is deliberately not a completed bilingual guide: it says reviewed
Spanish material and hosting are still required before a bilingual session. No
participant pilot or rendered-document inspection was performed. The checker does
not prove prose agreement, translation quality, or real-world usability. The
untracked evaluation-run outputs were treated as evidence of current behavior only;
they are not committed deliverables.

## Focused verification

- `python3 -m unittest discover -s scripts -p 'test_*.py'` from `community-guides`: 9 passed.
- `python3 scripts/validate_guide.py examples/apartment-plan.json`: valid; one proposed-owner warning.
- `python3 scripts/validate-evals.py community-guides/evals/evals.json`: passed.
- Repository skill, catalog, reference, generated-artifact, and test-registration checks: passed.
