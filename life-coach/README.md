# Life Coach - Bounded, User-Led Adult Coaching

Help an AI agent support personal goals and decisions without pretending to be a therapist, a credentialed human coach, or the owner of someone else's choices.

## Why Install This Skill

Generic coaching prompts often produce either endless questions or overconfident advice. This skill establishes the help a person wants, listens before intervening, uses the smallest fitting method, and keeps decisions with the person.

It is designed for ordinary adult, nonclinical coaching and includes boundaries for safety, specialist advice, privacy, memory, sponsors, tools, culture, accessibility, and dependency. Ordinary coaching can use a bounded no-capability fallback; advanced host capabilities require explicit, current verification.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Coaching loop, boundaries, fallback behavior, and reference routing |
| `references/` | Conversation, method, safety, privacy, onboarding, governance, culture, and evidence guidance |
| `templates/` | Original coaching worksheets plus a blank v2 activation-manifest example |
| `scripts/validate-capabilities.py` | Standard-library validator for host-owned v2 manifests |
| `tests/` and `evals/` | Offline validator tests and representative behavior cases |

## Quick Start

Try:

```text
Coach me through whether I still want this goal. Challenge my assumptions, but keep the decision mine.
```

Operators should create a host-owned contract outside the skill from `templates/capability-contract.example.json`; never edit the tracked example in place. Validate the external file with:

```sh
python3 scripts/validate-capabilities.py /host/config/capability-contract.json
```

The ignored `local/` directory is a fallback, not canonical storage: reinstall or cleanup can remove ignored files. Keep completed contracts, progress, and evidence in managed host configuration.

## Triggers

Load this skill when an adult explicitly asks for life coaching, reflective challenge, ambivalence exploration, a user-owned experiment, autonomy-preserving accountability, or coaching progress/ending review.

Do not load it merely because someone mentions a goal or feeling. Direct answers, task execution, therapy, crisis support, product discovery, and medical, legal, financial, addiction, abuse, safeguarding, or other specialist advice belong elsewhere.

## Requirements

Conversation has no runtime dependencies. Python 3.10+ is needed only for manifest validation. This public skill is adult-only. Coaching memory, sponsors, proactive contact, sensitive actions, and human review require verified host controls and remain off when unknown.
