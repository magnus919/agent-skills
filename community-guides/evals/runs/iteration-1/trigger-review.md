# Community-guides trigger review

This is an offline description-selection probe. Decisions below were made from
the `name` and `description` frontmatter of `community-guides/SKILL.md` and the
query strings in `community-guides/evals/trigger-queries.json`. The stored
`should_trigger` values were consulted only after making the independent
decisions.

## Skill boundary used

The skill applies to practical community guides involving locally grounded
activities, participant worksheets, facilitator instructions, or maintenance
plans, including neighborhood preparedness, mutual support, shared projects,
and community learning. It does not apply to travel guides, promotional
brochures, standalone policies, simple document formatting, or live incident
response.

## Per-query decisions

| # | Applies? | Expected | Match? | Boundary rationale |
|---:|:---:|:---:|:---:|---|
| 1 | Yes | Yes | Yes | A locally grounded outage guide for renters and volunteers, with a pilot, is community preparedness and includes participant-oriented validation. |
| 2 | Yes | Yes | Yes | An offline-first rural preparedness handout with household testing is a practical community preparedness guide with source and field-validation work. |
| 3 | Yes | Yes | Yes | A participatory resident workshop and feedback-driven guide revision fit community learning, facilitation, and locally grounded adaptation. |
| 4 | Yes | Yes | Yes | Shared seasonal garden tasks and observation-based maintenance fit shared projects and routine community stewardship; applicability is not limited to disaster response. |
| 5 | No | No | Yes | A generic solo backyard gardening article lacks the community, shared-project, participant, or facilitator scope required by the description. |
| 6 | No | No | Yes | An internal engineering credential-rotation runbook is operational engineering documentation, not a community guide; it also does not present the stated community-learning scope. |
| 7 | No | No | Yes | Immediate advice during a life-threatening emergency is live incident response, an explicit negative boundary, and the query expressly excludes the community-guide framing. |

## Comparison

- Queries evaluated: 7
- Independent decisions applying the skill: 4
- Independent decisions not applying the skill: 3
- Expected values matching: 7 of 7
- Expected values differing: 0

## Limitations

This review tests only semantic selection against one skill description and a
fixed set of query strings. It does not test runtime auto-discovery, evaluator
implementation, ranking among multiple applicable skills, full `SKILL.md`
instructions, references, or execution quality. The judgments are based on
the wording supplied in each query; a request with additional context could
cross a boundary (for example, a gardening request becoming a resident-led
shared project). No repository files were edited.
