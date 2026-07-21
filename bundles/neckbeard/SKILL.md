---
name: neckbeard
description: >-
  Evidence-driven software delivery operating model. Routes a change request through
  framing, discovery, design, implementation, review, verification, delivery, and
  learning — choosing the smallest safe intervention, proving it at the real delivery
  boundary, and leaving an inspectable evidence ledger. Use when asked to fix, build,
  refactor, review, verify, or release software and the work is non-trivial. Composes
  specialist catalog skills rather than replacing them. Not a persona, not a "10x
  developer" prompt, and not a LOC-minimizer.
license: MIT
compatibility: Agent harness with file read/write, terminal, and skill loading. No network or runtime dependency required by the bundle itself.
metadata:
  spec-version: "1.0"
  tags: sdlc, delivery, evidence, verification, workflow
---

# neckbeard

A disciplined operating model for software delivery. It does not perform a
character. It makes an agent do six things reliably: frame the change, discover
the real system before designing, pick the smallest *safe* intervention, execute
by stage, record evidence, and stop or escalate when the evidence runs out.

The name is a joke about the "10x developer in a Markdown file" trope. The
substance is the opposite of that trope: effectiveness here is earned by
observable outcomes and scoped claims, never asserted by a persona.

## When to load this

Load neckbeard when a request is a non-trivial software change — a bug to
diagnose, a feature to build, a refactor, a review, a release to verify — and
you need a bounded, stage-aware way to carry it to a defensible "done."

Do **not** load it for:
- A single factual question or lookup (answer directly).
- A one-line edit whose contract is already fully specified (just do it, but
  still verify at the boundary).
- A task already owned end-to-end by a more specific skill (route there; see
  [references/routing-table.md](references/routing-table.md)).

## Core loop

Every run moves through the same spine. Each stage has entry conditions,
required evidence, exit conditions, and escalation rules detailed in
[references/stages.md](references/stages.md).

1. **Frame the change contract.** State the user-visible problem, constraints,
   system boundary, risks, and explicit non-goals. Distinguish *authority to
   explore* from *authority to modify, publish, deploy, or merge*. Stop early if
   no change is justified, and keep the evidence for that decision.
   Template: [templates/change-contract.md](templates/change-contract.md).

2. **Discover before designing.** Inspect the actual repository, contribution
   guidance, architecture, callers, tests, config, and recent changes *before*
   proposing a fix. Prefer primary evidence (code, tests, runtime output,
   project docs) over plausible architecture narratives. Make unverified
   assumptions and missing access explicit.

3. **Select the smallest safe intervention.** Reuse existing code and platform
   capabilities first; then the smallest implementation that satisfies the
   verified contract. Treat "smallest diff" as a *consequence of understanding*,
   not an optimization target. Never trade away trust-boundary validation, data
   safety, security, accessibility, observability, operational recovery, or
   explicitly requested behavior. Record any deliberate ceiling and its upgrade
   trigger.

4. **Execute by SDLC stage.** Route the work to the stage that owns it —
   discovery/requirements, design, implementation, verification, delivery,
   learning. Load the matching specialist skill where one exists rather than
   re-deriving its method (see routing table).

5. **Keep an evidence ledger.** Each non-trivial run emits a compact record:
   intent, inspected artifacts, assumptions, rejected alternatives, files
   changed, commands/checks run, observed outputs, unverified boundaries,
   rollback/follow-up triggers. Distinguish a component check from an
   end-to-end or production-boundary check. Format and rules:
   [references/evidence-ledger.md](references/evidence-ledger.md).
   Template: [templates/evidence-ledger.md](templates/evidence-ledger.md).

6. **Stop and escalate by rule.** Stop and report when the task has no verified
   need, a risk/authority boundary needs a human, or two materially different
   approaches have failed. Never trade persistence for privilege escalation,
   destructive recovery, or unbounded workaround churn. Rules:
   [references/risk-authority-gates.md](references/risk-authority-gates.md).

## The one rule that defines "done"

> "Done" is prohibited unless the declared verification target has actually been
> exercised. If it has not, report the unverified gap honestly instead of
> claiming completion.

A passing unit test is not the same as exercising the delivery boundary. A local
render is not production. State which boundary was checked and which was not.
Verification method: load the catalog skill `verification-methodology`.

## Minimalism, correctly

Minimalism in this bundle is a *conditional* design choice made **after**
real-flow understanding — not an unconditional "fewest lines wins" reflex. The
correct answer is sometimes a larger change, a new dependency, a process change,
or no code change at all. The evaluation fixtures include adversarial cases
specifically so the bundle cannot win by reflexively deleting or compressing.
See [references/stages.md](references/stages.md) §3.

## Routing: compose, don't swallow

neckbeard owns the *cross-stage contracts* — the change contract, evidence
ledger, stop rules, and evaluation protocol. It does **not** own domain method.
When a stage has a specialist skill, load it and follow it. The full table with
"use existing skill instead" conditions is
[references/routing-table.md](references/routing-table.md). Summary:

| Stage / need | Load this catalog skill instead of re-deriving |
|---|---|
| Stakeholder discovery, requirements, ACs | `product-discovery` |
| Formal specification, phase gates | `spec-driven-development` |
| Reverse-engineering an existing codebase | `software-architecture-analysis` |
| Root-cause debugging | `systematic-debugging` |
| Docs / README / API reference | `technical-documentation` |
| Verification verdicts and evidence | `verification-methodology` |

If a specialist skill is not installed, neckbeard's stage references provide a
minimal fallback method — but note in the ledger that the specialist was absent.

## Evaluation is a first-class deliverable

This bundle ships a versioned evaluation harness in [eval/](eval/). It measures
SDLC *outcomes* the bundle claims to improve — correctness, regression safety,
scope discipline, boundary verification, honest uncertainty — never LOC or
response brevity. Before claiming any improvement, run the public suite and
report holdout results through the maintainers' workflow. Methodology:
[references/evaluation.md](references/evaluation.md).

**Claims policy.** Scope every performance claim to the evaluated models,
harnesses, repositories, task classes, and dates. Do not use "10x developer,"
"always," "best," or any global performance claim without a published,
reproducible definition and evidence. LOC may appear only as diagnostic
metadata, never as a success proxy.

## File map

| Path | Loaded when |
|---|---|
| [references/stages.md](references/stages.md) | Entering any SDLC stage; defines entry/evidence/exit/escalation per stage |
| [references/evidence-ledger.md](references/evidence-ledger.md) | Building or auditing the ledger; defines required fields and boundary rules |
| [references/risk-authority-gates.md](references/risk-authority-gates.md) | Before any mutation, deploy, merge, or destructive act; and on stop/escalation |
| [references/routing-table.md](references/routing-table.md) | Deciding whether a specialist skill owns the current stage |
| [references/evaluation.md](references/evaluation.md) | Designing, running, or reporting an evaluation |
| [templates/](templates/) | Change contract, decision record, evidence ledger, verification plan, eval report |
| [eval/](eval/) | Task schema, rubric, baseline protocol, fixtures, runner |
