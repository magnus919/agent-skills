# Community Guides

Build practical guides that help people learn, plan, and act together.

## Why Install This Skill

A useful community guide needs to fit the people using it: their time, languages,
resources, relationships, and local circumstances. This skill helps your agent turn
that context into activities people can complete, with worksheets and clear next steps.

Use it to create a neighborhood preparedness workshop, organize shared garden care,
adapt a handbook for another community, or improve materials after participant feedback.
It produces participant and facilitator materials, identifies facts that need checking,
and leaves a plan for keeping the guide current.

## What You Get

| Contents | Provides |
|---|---|
| `SKILL.md` | A repeatable guide-building method |
| `references/` | Local research, activity design, review, and source attribution |
| `templates/` | Brief, module, worksheet, facilitator, and maintenance starters |
| `examples/` | An original fictional apartment-community workshop series |
| `scripts/` | An offline consistency checker and its tests |
| `evals/` | Eight evaluation scenarios, input material, and separate trigger probes |

## Quick Start

Ask your agent:

> Use community-guides to create a 45-minute workshop for our community garden.
> Help members agree on watering responsibilities and backups. Six people can
> attend; two need a paper copy afterward. We have no budget for new equipment.

Try the bundled example checker from the repository root:

```sh
python3 community-guides/scripts/validate_guide.py community-guides/examples/apartment-plan.json
```

Expect `valid: true` and a warning that the example's maintenance owner is proposed.
The checker verifies structure, file references, and timing; people still need to
review the content and try the activities.

## Triggers

- Create practical guides for shared community action or learning.
- Adapt existing materials to a different community.
- Revise activities and worksheets using participant feedback.

## Requirements

An agent that supports Agent Skills. Python 3.10+ for the optional checker; no API
key or third-party Python package is required. Current local research needs web
access or supplied sources. PDF/Word delivery needs suitable document tooling.

The method is informed by Ready Together, with original templates and examples;
see [attribution](references/source-pattern.md). No affiliation is implied.
