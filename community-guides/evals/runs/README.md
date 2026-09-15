# Behavioral run evidence

These are retained agent outputs and reviews, including failures. They are evaluation
artifacts, **not community advice or publication-ready guides**. Local facts are
fictional. In particular, initial outputs contain unsupported safety wording that
the author rejected; do not reuse it as an instruction.

## Method

Generation and independent review used `gpt-5.6-luna`, reasoning effort `high`, with
fresh, non-forked subagent contexts. Generation agents received the case prompt and
raw fixture, plus the skill only for with-skill runs. They were instructed not to
read the manifest/assertions, other outputs, or retained runs. No web research or
external mutation was permitted. Skill agents could read relevant templates and
references; baseline agents used ordinary capabilities. Outputs were written in
isolated temporary directories and copied here without editing their content.

The available subagent API did not expose per-run token usage or elapsed execution
time in completion results; those metrics are unavailable. Run IDs identify actual
subagent executions. Single samples are qualitative evidence, not statistical estimates.

## Reading the records

- Start with [the evaluation report](REPORT.md) for the integrating author's
  acceptance decisions and limitations; raw reviewer scores are not the verdict.
- `iteration-1/manifest.json` preserves the initial assertions before refinement.
- `iteration-1/<case>/with-skill.md` contains the eight original skill outputs.
- Two cases also have `baseline.md`, using the same prompts and model settings.
- `iteration-1/*-review.md` preserves independent reviewer findings, including
  judgments the integrating author later challenged. A reviewer pass is not final
  acceptance when the cited evidence contradicts it.
- Blind comparison labels A and B map to baseline and with-skill respectively in
  both cases. Reviewers saw anonymized filenames without this mapping.
- Review paths referring to `/private/tmp/community-guides-evidence/<case>/with-skill/guide.md`
  map to `iteration-1/<case>/with-skill.md`; the rural output originally omitted
  the `with-skill` directory. Blind `A.md` and `B.md` map as above.

This is supplemental evidence. It does not implement a repository v1 grader-binding,
freshness, or release-gate contract and is not an automated CI behavioral gate.
The routing review is an offline semantic-selection probe, not runtime discovery.
No real resident pilot, qualified language review, or local service verification occurred.

The second full round is in `iteration-2/`; its generation content was based on
`5b71a61` (with the conflict-run revision uncertainty noted in its metadata).
Its manifest snapshot includes subsequently strengthened sparse/conflict assertions.
`iteration-3/` contains targeted revision/conflict reruns at `012933a`, not another
full-suite run. `transfer-check/` is a fresh supplemental case authored after
tuning, with its original prompt, fixture, assertions, and unedited output.
`intermediate/` retains two exploratory outputs between the full rounds.

Raw paths under `/private/tmp/community-guides-final/<case>/guide.md` map to
`iteration-2/<case>/with-skill.md`; `/private/tmp/community-guides-release/` maps
to `iteration-3/`; `/private/tmp/community-guides-transfer/` maps to
`transfer-check/`. The subsequent targeted reruns at `b0dd0dd` are in
`final-regression/` and map from `/private/tmp/community-guides-final-regression/`.
These are historical execution paths, not dependencies.
