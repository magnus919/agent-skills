# neckbeard

An evidence-driven operating model for software delivery — not a "10x developer"
persona, but a disciplined workflow that helps an AI agent choose the smallest
*safe* intervention, prove it worked at the real delivery boundary, and leave an
audit trail a human can inspect.

## Why Install This Skill

Most "senior developer" prompts fail the same way: they make an agent emit short,
confident code and call it effectiveness. Scott Logic's critique of the Ponytail
benchmark showed that a static behavioral prompt plus a narrow, gameable metric
(lines of code) cannot substantiate any real claim about software engineering.
Swapping the persona for the three words "Follow YAGNI principles" nearly matched
its score.

neckbeard is the answer to that failure mode. Instead of performing a character,
it gives an agent a bounded, stage-aware spine: frame the change, discover the
real system before designing, pick the smallest intervention that is still safe,
execute by SDLC stage, record evidence, and stop or escalate when the evidence
runs out. Minimalism is treated as a *consequence of understanding*, not a reflex
— so the bundle does not win by reflexively deleting or compressing.

Install it when you want delivery discipline that is inspectable. Every
non-trivial run produces an evidence ledger: intent, inspected artifacts,
assumptions, rejected alternatives, files changed, checks run, observed outputs,
and the boundaries that were *not* verified. "Done" is prohibited unless the
declared verification target was actually exercised.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Thin umbrella that routes a request through the delivery spine and composes specialist catalog skills |
| `references/stages.md` | Entry conditions, required evidence, exit conditions, and escalation rules for each SDLC stage |
| `references/evidence-ledger.md` | The ledger schema and the rules for distinguishing a component check from a delivery-boundary check |
| `references/risk-authority-gates.md` | Stop and escalation rules; the gate before any mutation, deploy, merge, or destructive act |
| `references/routing-table.md` | "Use existing skill instead" table so the bundle composes the catalog rather than swallowing it |
| `references/evaluation.md` | Evaluation methodology: fixtures, baselines, rubrics, multi-run reporting, claims policy |
| `templates/` | Change contract, decision record, evidence ledger, verification plan, evaluation report |
| `eval/` | Versioned evaluation harness: task schema, scoring rubric, baseline protocol, fixtures, and a runner |

## Quick Start

Load the umbrella when a non-trivial change lands — read `SKILL.md` and follow
its core loop. For a bug, the agent frames a change contract, loads
`systematic-debugging` for root cause, makes the smallest safe fix, verifies at
the real boundary, and writes an evidence ledger. For a feature, it routes
discovery to `product-discovery` and specification to `spec-driven-development`
before writing code.

To run the evaluation suite against your harness:

```
python3 eval/run_eval.py --suite eval/fixtures --report out/report.md
```

## Triggers

- Asked to fix, build, refactor, review, verify, or release software where the work is non-trivial.
- A change needs a defensible "done" backed by evidence, not a claim.
- You want an inspectable record of what was inspected, assumed, changed, and left unverified.
- You need to evaluate whether a delivery skill actually improves outcomes.

Do not trigger for single factual questions, fully-specified one-line edits, or
tasks already owned end-to-end by a more specific skill.

## Requirements

- An agent harness with file read/write, terminal access, and skill loading.
- No network or runtime dependency in the bundle itself.
- The evaluation runner needs Python 3.9+ (standard library only).
- Recommended companion catalog skills (loaded on demand, not required):
  `product-discovery`, `spec-driven-development`, `software-architecture-analysis`,
  `systematic-debugging`, `technical-documentation`, `verification-methodology`.
