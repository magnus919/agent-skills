# Semantic Spacetime

Model meaning over time with Mark Burgess's Semantic Spacetime: a discrete graph method for designing shared semantic ground between agents, diagnosing semantic drift, and building coordination that converges on intended meaning.

## Why Install This Skill

Multi-agent systems keep failing on meaning: two agents start from the same instructions and quietly diverge, nobody notices that a shared term no longer means the same thing to each side, and the system dead-ends in a state where information stops flowing. This skill gives your agent a working method for that problem — model the space of meaning as a graph, treat every local change as a unit of time, and measure where interpretations drift apart instead of guessing.

After installing, your agent can map a team of agents onto a semantic spacetime with typed events, things, and concepts, trace how intent propagates through promises and acceptances, diagnose drift and divergence with a bounded procedure, and write an analysis report with concrete interventions and a verification plan. The method is grounded in Burgess's arXiv series (2014-2025) and his earlier Promise Theory, and it is honest about what is verified, what is not, and what is extrapolation.

## What You Get

| Contents | Provides |
|---|---|
| `SKILL.md` | When to use Semantic Spacetime, when not to, and what to load for the task at hand |
| `references/foundations.md` | The academic core: definitions, the γ(3,4) formalism, proper time, causality, the promise substrate, and adjacent fields |
| `references/glossary.md` | Heading-led definitions of every term the skill uses |
| `references/bibliography.md` | Annotated primary sources with URLs, organized by area |
| `templates/` | The `sst-model.yaml.tmpl` model format (agents, nodes, edges, acceptances, trajectories, observations) and the `sst-analysis.md.tmpl` report skeleton |
| `evals/` | Output-quality evals for the skill |
| `LICENSE` | MIT license |

## Quick Start

1. Copy `templates/sst-model.yaml.tmpl` to a working file (for example `sst-model.yaml`).
2. Fill in your system: agents with roles and promises, semantic nodes typed as events, things, or concepts, edges with link values from -3 to 3, plus acceptances, trajectories, and observations. Every field has an inline comment explaining it; the delimited example block shows a complete model.
3. Copy `templates/sst-analysis.md.tmpl` to a working file (for example `sst-analysis.md`).
4. Fill the report skeleton: system description, the semantic spacetime map, drift/divergence/absorbing-state findings, interventions, and a verification/measurement plan.

## Triggers

- Designing or analyzing shared semantic ground between agents
- Modeling intent or meaning changing over time (trajectories, drift, convergence)
- Designing convergent, self-healing coordination where state is measured against desired meaning
- Diagnosing semantic drift, divergence, or dead-ends (absorbing states)
- Mapping promises onto spacetime (trajectories, propagation, causality)
- Analyzing temporal blindness in agents (state tracking, event ordering, causality)

## Requirements

Nothing to install. The skill is Markdown, YAML templates, and JSON evals; the bundled model format is versioned (`sst-model-v1`) and documented in the template itself. Works with any agent client that loads Agent Skills.
