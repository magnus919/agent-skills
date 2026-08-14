# Evidence Ledger

The ledger is the inspectable record of a run. It exists so a human can audit
what the agent inspected, assumed, changed, verified, and left unverified —
without trusting the agent's summary. Every non-trivial run emits one.

A ledger is not a victory lap. Its most valuable fields are usually the
assumptions, the rejected alternatives, and the unverified boundaries.

## Required fields

| Field | Content |
|---|---|
| **Intent** | The user-visible problem and the change contract in one or two sentences. |
| **Authority** | Explore / modify / publish / deploy / merge — which was granted. |
| **Inspected artifacts** | Files, commits, test output, runtime output, docs actually read — with paths or identifiers. |
| **Assumptions** | Each unverified assumption, stated explicitly. |
| **Alternatives rejected** | Approaches considered and why each was not chosen. |
| **Files changed** | Every file modified, created, or deleted. |
| **Commands / checks run** | The exact commands or checks executed. |
| **Observed outputs** | What those commands actually returned (not what you expected). |
| **Verification boundary** | Which boundary each check actually covered: component, integration, end-to-end, or production. |
| **Unverified boundaries** | What was *not* checked, and why. |
| **Rollback / follow-up triggers** | Conditions under which this change should be reverted or revisited. |

Template: [../templates/evidence-ledger.md](../templates/evidence-ledger.md).

## The boundary rule

> A component-level check is not an end-to-end check. An end-to-end check is not
> a production check. State which boundary each check covered. Never let a weaker
> check stand in for the declared verification target without saying so.

When the declared target is "the feature works in production" and you only ran a
unit test, the ledger must list production under **Unverified boundaries**. That
is a correct, honest ledger. Claiming "done" from it is not.

## Observed outputs are not ground truth

Record what a tool returned, but remember a tool verdict is evidence, not proof.
Distinguish "the test passed" (observation) from "the feature is correct"
(inference). If you infer, mark it as inference and say what would confirm it.

## Minimal but complete

The ledger is compact — a few lines per field, not a transcript. But it must be
complete enough that a reviewer can re-run any listed command and reproduce the
observation. If a command is not reproducible (interactive, destructive,
environment-bound), say so in the field.

## When not to write one

Skip the ledger for: a single factual answer, a fully-specified one-line edit
verified at its boundary, or a pure read. If in doubt, write it — the cost is
small and the audit value is high.
