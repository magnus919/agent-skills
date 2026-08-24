# bmad

Turn human intent into bounded, inspectable, resumable agent work — the BMad method
(Breakthrough Method of Agile AI-Driven Development) as a protocol any agent harness
can follow, no official installer required.

## Why Install This Skill

Most agent failures are not coding failures. The agent implemented the wrong thing
because intent was never compressed into a contract; it re-asked questions it could
have answered by reading the repository; a review produced a wall of noise instead of
a triage; or an autonomous run kept going past the point where the boundary stopped
being safe. BMad was built to fix exactly these problems: clarify intent first, route
each piece of work to the smallest process it deserves, carry decisions in durable
artifacts, and make autonomy conditional on observable acceptance.

This skill installs that discipline as a **harness-agnostic protocol**. You do not
need the BMad npm installer, a specific IDE, or a particular agent brand. Any agent —
Claude Code, Cursor, Hermes, Devin, OpenHands, or your own harness — can follow the
protocol with plain Markdown contracts, a five-field intent contract, and a
machine-readable status vocabulary (`draft` → `ready-for-dev` → `in-progress` → `in-review` → `done`, with `blocked` as a resumable routing signal and rework paths back to earlier states).

After installing, an agent can take a vague change request and return a one-paragraph
intent contract instead of guessing; take a cross-system initiative and sequence it
through analysis, planning, and solutioning before a single line of code; run a review
that defers unrelated findings instead of ballooning scope; and run unattended builds
that stop safely and report `blocked` when a human decision is genuinely required.

## What You Get

| Directory | What it provides |
|-----------|-----------------|
| [`SKILL.md`](SKILL.md) | The protocol core: classification, five-field contract, status vocabulary, failure routing, autonomy gate, routing |
| [`references/protocol.md`](references/protocol.md) | The full paste-ready operating protocol for an agent |
| [`references/classification.md`](references/classification.md) | Direct / bounded / initiative decision table, one-question rule, stop conditions |
| [`references/spec.md`](references/spec.md) | SPEC authoring, status semantics, PRD coexistence, readiness |
| [`references/lifecycle.md`](references/lifecycle.md) | The four-phase lifecycle and the artifact chain |
| [`references/project-context.md`](references/project-context.md) | Conservative AGENTS.md rules: persist only what is expensive to rediscover |
| [`references/review-and-failure-routing.md`](references/review-and-failure-routing.md) | Review as triage; routing failure to the layer where ambiguity entered |
| [`references/autonomy.md`](references/autonomy.md) | Autonomous execution (Build Auto) conditions, stop rules, blocked as routing |
| [`references/party-mode.md`](references/party-mode.md) | Multi-persona deliberation with honest independence caveats |
| [`references/adoption.md`](references/adoption.md) | Five-step incremental adoption and dark-factory mapping |
| [`templates/SPEC.md`](templates/SPEC.md) | Versioned machine contract for bounded/initiative work |
| [`templates/INTENT.md`](templates/INTENT.md) | Lightweight five-field contract for bounded work |
| [`templates/STORY.md`](templates/STORY.md) | One bounded, dispatchable work unit |
| [`templates/REVIEW.md`](templates/REVIEW.md) | Final human checkpoint review |
| [`scripts/check-spec.py`](scripts/check-spec.py) | Deterministic spec validation: five fields + status vocabulary (stdlib only) |
| [`evals/evals.json`](evals/evals.json) | Output-quality evaluation cases |

## Quick Start

No setup needed. The protocol works with plain Markdown files in your repository.

- Say *"this request needs an intent contract before implementation"* — fill in
  `templates/INTENT.md` or `templates/SPEC.md`.
- Say *"classify this work"* — load `references/classification.md` for the decision
  table.
- Say *"run this build autonomously, bounded"* — load `references/autonomy.md` and set
  the status vocabulary.
- After writing a spec, validate it:

```bash
python3 bmad/scripts/check-spec.py path/to/SPEC.md
```

It prints `PASS`/`FAIL` per file and exits non-zero on invalid specs; add `--json` for
machine-readable output.

## Triggers

Load this skill when:

- A change request, feature, or bug report needs intent capture before implementation
- You must decide how much planning ceremony a piece of work deserves
- Delegating a build to an agent: boundary, acceptance, and stop conditions
- Work must be resumable across sessions or agents (durable artifacts, status)
- A review is producing noise instead of triage
- An autonomous run needs to know when to stop and escalate (`blocked`)
- A multi-agent epic needs shared architecture and story decomposition
- You are standing up a dark-factory-style delivery system and need the control plane

## Requirements

No software dependencies or credentials. `scripts/check-spec.py` uses the Python
standard library only (Python 3.8+). The method is agent-harness-agnostic; templates
and status files are plain Markdown.

## Attribution

Method adapted from BMad / BMAD-METHOD™ (trademarks of BMad Code, LLC; official
repository: bmadcode/bmad-method), distilled from official documentation and an
independent research synthesis into an original harness-agnostic operating protocol.
This skill is not the official BMad tooling and does not include its installer.
