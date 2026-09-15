# Follow-up independent review: `community-guides`

## Review identity and evidence boundary

Current committed HEAD:

`5b71a61eb4910b2e4c8d389e00403bd6addb0ace`

This is not a final-head review: the relevant fixes are currently uncommitted.
The worktree has modified `community-guides/SKILL.md` and
`community-guides/evals/evals.json`, plus untracked evaluation-run artifacts under
`community-guides/evals/runs/iteration-1/`. The candidate outputs reviewed here are
outside the repository at `/private/tmp/community-guides-final/{case}/guide.md`.

I excluded iteration-1 behavioral failures from the current verdict. They are
historical evidence only and are not treated as failures of the current candidates.

## P1 reassessment

### Source-only technical boundary: resolved in current evidence

The uncommitted skill change now explicitly requires unsupported safety prose to stay
out of resident-facing copy and says that replacements remain unresolved until an
authoritative source is supplied (`community-guides/SKILL.md:73-80`). The current
conflict candidate follows this: it calls itself a hold notice, says the packet has
no verified interim destination or route procedure, and records that no outside
emergency procedure was added (`/private/tmp/community-guides-final/conflicting-outdated-sources/guide.md:41-43`, `:95-108`).

The current revision candidate likewise keeps the resident card limited to confirmed
or unresolved Maple Court facts. It does not define elevator, emergency, or
accessibility procedures; it refers to the building's established process without
inventing one and states that Spanish copy still needs review
(`/private/tmp/community-guides-final/revision-from-participant-feedback/guide.md:1-28`, `:55-65`).

Verdict: the previous source-quarantine P1 does not persist. The source-conflict eval
now also has an explicit negative assertion for unsupported technical/emergency
procedures (`community-guides/evals/evals.json:109-110`).

### Narrow-scope precedence: broad P1 resolved, one current P2 remains

The uncommitted skill change now makes the precedence explicit: the narrow
card/decision-brief rule overrides the full-program checklist, and maintenance or
ownership records are conditional (`community-guides/SKILL.md:172-177`). The sparse
candidate is 292 words with exactly three essential questions and no delivered
workbook/facilitation manual (`/private/tmp/community-guides-final/sparse-brief/guide.md:1-42`).
The revision candidate is a focused card, change record, provenance record, checks,
pilot questions, and open questions; it adds no workshop, new worksheet, or multiple
pilot (`/private/tmp/community-guides-final/revision-from-participant-feedback/guide.md:1-81`).

The current conflict candidate is materially improved and does not reproduce the
historical 2,586-word/overbuilt artifact. Its requested decision brief, verification
record, and one pilot distinction are defensible. However, it still adds a standalone
“Maintenance and ownership” section even though the source packet does not provide a
guide owner or review-date request (`/private/tmp/community-guides-final/conflicting-outdated-sources/guide.md:111-151`, `:153-163`). That conflicts with the current rule to add maintenance/ownership
records only when requested or required by an existing package.

Verdict: the previous broad P1 does not persist as a contract contradiction, and it
does not justify carrying forward the historical overproduction finding. A narrower
P2 remains for the current conflict candidate: omit the maintenance/ownership section
or label it as an optional follow-up outside the requested decision brief.

## Current contract/eval check

The sparse and conflict assertions now encode the accepted scope changes:

- sparse: 300-word and three-question limit, with explicit exclusions for workbook,
  facilitation manual, repeated unknowns tables, and publication process
  (`community-guides/evals/evals.json:92`);
- conflict: decision-brief/concise-notes shape and prohibition on unrequested
  workshops, worksheets, and multiple pilots (`community-guides/evals/evals.json:109`);
- conflict: no unsupported technical or emergency procedures in resident-facing copy
  (`community-guides/evals/evals.json:110`).

The current manifest validates successfully. The remaining P2 is an output-level
scope mismatch in the current conflict candidate, not a missing portable assertion.

## Focused verification

- `python3 scripts/validate-evals.py community-guides/evals/evals.json`: passed.
- `python3 -m unittest discover -s scripts -p 'test_*.py'` from `community-guides`: 9 passed.
- `python3 scripts/validate_guide.py examples/apartment-plan.json`: valid, with the documented proposed-maintenance warning.

No repository files were edited by this review. A later review should repeat the
scope/source checks after the modified skill and eval manifest are committed, and
should record the new commit SHA rather than using this current HEAD as final.
