# Life Coach — Bounded, Evidence-Aware Personal Coaching

Help an AI agent coach without pretending to be a therapist, a credentialed human coach, or the owner of someone else's decisions.

## Why Install This Skill

Most generic “life coach” prompts swing between two bad extremes: endless questions that withhold useful information, or confident advice that takes the person's choices away from them. This skill gives an agent a disciplined middle path. It establishes what kind of help the person wants, listens before intervening, chooses the smallest fitting technique, and keeps goals and decisions with the person.

The skill is built for ordinary adult, nonclinical goals, decisions, transitions, habits, accountability, and progress review. It includes explicit boundaries for therapy, crisis, regulated advice, privacy, sponsors, tools, cultural context, and dependency. Its methods and original templates are evidence-labeled rather than marketed as universal solutions.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Thin operating contract, routing rules, compact coaching loop, and conditional reference map |
| `references/` | Expert guidance for conversations, methods, safety, culture, privacy, governance, evidence, and rights |
| `templates/` | Original agreements and worksheets for session focus, goals, ambivalence, experiments, review, referral, closure, sponsors, and host capabilities |
| `scripts/validate-capabilities.py` | Standard-library structural validator for a deployment capability contract |
| `tests/` | Offline tests for the capability-contract validator |
| `evals/evals.json` | Output-quality cases covering ordinary coaching and critical boundaries |
| `evals/trigger-queries.json` | Separate positive and near-miss routing probes |

## Quick Start

Install the `life-coach` directory in your agent's skills location, then try:

```text
Coach me through whether I still want this goal. Challenge my assumptions, but keep the decision mine.
```

Or:

```text
I want accountability without guilt or escalating reminders. Help me design an experiment and a review point.
```

A service operator can validate a completed host capability contract with:

```sh
python3 scripts/validate-capabilities.py path/to/capability-contract.json
```

This validates declared structure and activation rules. It does not prove that the host actually implements its claims.

## Triggers

Load this skill when a person explicitly asks for:

- life coaching or “coach me through this”;
- reflective challenge around a personal decision or transition;
- help examining ambivalence, an externally pressured goal, or a recurring nonclinical pattern;
- user-owned goal design, a behavioral experiment, or autonomy-preserving accountability;
- progress, alliance, unwanted-effects, or ending review for an existing coaching engagement.

Do not load it merely because someone mentions a goal, feeling, habit, or problem. Direct factual questions, task execution, planning after a decision, day-to-day AI capability discovery, product requirements interviews, therapy, crisis support, and specialist advice belong elsewhere.

## Requirements

The conversational skill has no runtime dependencies. Python 3.9 or newer is required only for the optional capability-contract validator. Minor use is outside this public skill. Sponsor-funded deployments, durable memory, proactive contact, safeguarding workflows, human review, and tool actions require verified host-level controls beyond this skill.
