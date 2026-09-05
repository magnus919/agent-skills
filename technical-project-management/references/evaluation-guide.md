# Evaluation and validation guide

Use when assessing whether the skill improves real outputs. A schema-valid manifest
is not behavioral proof, and a fake-adapter CI pass is only a harness smoke test.

## Scenario coverage

The eval manifest covers a team without a PM, expert vendor-slippage analysis,
hardware/software hybrid work, misleading green status, shared-resource arithmetic,
fixed-constraint change, uncertain AI research, closure gaps, Scrum accountabilities,
case-transfer limits, regulatory/appetite conflict, and inherited baseline integrity.
Neighboring skills also test routing of ongoing project control to this skill.

## Behavioral protocol

Run selected cases in fresh contexts with the skill and without it. Supply the same
prompt and input files to both. Keep baseline contexts free of the skill's content;
do not describe its expected answer. Store outputs separately. Grade each observable
assertion against actual output evidence and retain failures. Record tested revision,
model/harness if available, input, actual output, grade, and limitations. Unknown
runtime metadata stays unknown, not invented.

Start with the expert slippage, no-PM, and resource-conflict cases. Expand to the
remaining cases after reviewing quality. A single paired run does not establish a
statistically reliable improvement. Avoid aggregate "world-class" or general
reliability claims. Changes that make the skill longer without improving decisions
should be reconsidered. Preserve case IDs when refining assertions.

## Separate trigger probes

These are manual trigger checks, not portable output-quality cases:

| Prompt | Expected routing |
|---|---|
| Help our team run this project; nobody is a PM | This skill |
| I need a sponsor decision about a slipped vendor milestone | This skill |
| How should we close and hand off this technical project? | This skill |
| Write the code to fix this API error | Engineering specialist |
| Diagnose our WIP limit and cycle time | Kanban guru |
| Turn this approved spec into a work breakdown | Implementation planning |
| Move a Jira issue to Done | Jira |

## Mechanical checks

From repository root, run skill-local tests, format/link validation, changed-skill
quality validation, eval schema validation and coverage ratchet, skill-test discovery,
and generated catalog checks. These prove structure and deterministic software
behavior, not the quality of every management recommendation.

Run the helper tests directly with:

```sh
python3 -m unittest discover -s technical-project-management/scripts -p 'test_*.py'
```

Complete evaluation reporting when actual checks and sampled outcomes are recorded,
failures have dispositions, and untested claims remain explicitly untested.

The initial sampled review and captured outputs live in `evals/sample-review.md`
and `evals/samples/` under the skill root. It documents no observed score advantage,
limited isolation, post-review refinements, and the cases not yet exercised.
