# Product Experimentation

Run end-to-end product experiments — from assumption to decision — with the right method, explicit guardrails, and outcomes that update your roadmap.

## Why Install This Skill

Product teams waste months building features nobody wants, or they A/B test changes that a five-minute customer interview would have invalidated. Experimentation is fragmented: opportunity-solution trees help you find the right problem, data science handles the statistics, release engineering manages the flags, but nobody owns the complete experiment workflow from assumption to learning.

This skill gives your agent the ability to run a disciplined experiment end-to-end. It starts where your assumptions live, helps pick the lightest-weight method that can actually answer the question (from a $0 interview through a full A/B test), and ensures you never ship a "statistically significant" result that quietly broke your error budget or crossed an ethical line. Every experiment ends with a readout that changes something concrete — a roadmap item, a backlog priority, or a decision record.

If you already use other product skills (product-methodology, data-scientist, release-engineering), this skill connects them into a coherent workflow. If you are just getting started with experimentation, it gives you a complete, safe starting point.

## What You Get

| Directory | Contents |
|-----------|----------|
| `SKILL.md` | Core workflow: assumption mapping, method selection (interview to A/B), guardrails and ethics, decision criteria, and readout recording |
| `references/discovery-brief.md` | Where experimentation concepts live in other skills and what this skill owns vs routes |
| `references/method-selection.md` | Decision framework for choosing qualitative, prototype, operational, and quantitative methods |
| `references/guardrails-and-ethics.md` | Guardrail design, ethical boundaries, stopping rules, and decision ownership |
| `references/experiment-readout.md` | How to produce a decision-impact readout that updates the roadmap or decision log |
| `templates/experiment-brief.md` | Fillable experiment brief: hypothesis, method, metrics, sample, decision criteria |
| `templates/assumption-map.md` | Structured assumption map with risk, evidence, and testability dimensions |
| `templates/guardrail-and-decision-rule.md` | Guardrail metrics, stopping rules, and decision-authority record |
| `templates/readout-learning-entry.md` | Experiment outcome and roadmap/decision-log update template |
| `evals/evals.json` | Five output-quality eval cases covering prototype, feature-flag, underpowered, guardrail omission, and no-ship scenarios |

## Quick Start

1. Map your assumptions with [templates/assumption-map.md](templates/assumption-map.md).
2. Write an experiment brief for the riskiest assumption using [templates/experiment-brief.md](templates/experiment-brief.md).
3. Select the lightest method that works — do not default to A/B testing.
4. Record guardrails, stopping rules, and decision ownership with [templates/guardrail-and-decision-rule.md](templates/guardrail-and-decision-rule.md).
5. Run the experiment. Route statistical design to `data-scientist` and rollout to `release-engineering`.
6. Decide using multiple criteria (never p-value alone). Record the readout with [templates/readout-learning-entry.md](templates/readout-learning-entry.md).

## Triggers

Load this skill when you need to:

- Design and run a product experiment from scratch
- Choose between qualitative interviews, prototypes, concierge tests, fake doors, feature flags, and A/B tests
- Test assumptions before committing engineering effort
- Define guardrails, stopping rules, and decision criteria for an experiment
- Interpret experiment results and make a defensible ship/no-ship decision
- Record experiment outcomes that update your product roadmap or decision log

## Requirements

- No API keys, external services, or runtime dependencies required.
- Works with any agent framework supporting the Agent Skills format.
- For statistical design, the `data-scientist` skill should be available. For rollout mechanics, the `release-engineering` skill should be available.
- For measurement contracts, product-analytics-and-measurement should be available.
