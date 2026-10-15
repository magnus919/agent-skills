# SPEC Authoring and the Status Vocabulary

The SPEC is the machine contract of a BMad-style run: the artifact that lets an agent
resume, another agent continue, an orchestrator route, and a human review. It is
deliberately concise — five core fields plus verification sections.

## The five core fields

| Field | What it stabilizes | Common failure if missing |
|---|---|---|
| **Why** | The outcome and why it matters; the reason the work exists | Agents optimize for a plausible-but-wrong goal |
| **Capabilities** | What the system must be able to do, observably | Vague scope; every implementer guesses differently |
| **Constraints** | Technical, operational, legal, security, privacy, time, cost, organizational boundaries | Implementations violate boundaries nobody wrote down |
| **Non-goals** | What is explicitly out of scope | Scope creep; "while I'm here" expansion |
| **Success signal** | How we know the result works and is acceptable | No definition of done; endless review |

A good test for each field: could another agent or a fresh session continue from this
file alone without inventing a material decision? If not, the field is under-specified.

## SPEC versus PRD

- The **PRD** is the stakeholder-facing description of the problem and desired
  behavior — richer product context, audience, and rationale.
- The **SPEC** is a tighter execution contract — the boundary within which
  implementation is allowed to act.
- They coexist: the PRD holds the why-for-humans; the SPEC holds the
  what-and-within-what-bounds for implementation. Do not collapse one into the other
  when both audiences exist.

## Status vocabulary

| Status | Meaning | Allowed next |
|---|---|---|
| `draft` | Spec exists but is not ready | `ready-for-dev`, `blocked`, `draft` |
| `ready-for-dev` | Passed readiness; ready to implement | `in-progress` |
| `in-progress` | Implementation is underway | `in-review`, `blocked` |
| `in-review` | Review or triage is underway | `done`, `in-progress` (rework), `blocked` |
| `done` | The workflow completed successfully | — |
| `blocked` | Cannot safely continue unattended | `ready-for-dev`, `in-progress`, `draft` |

`blocked` is not failure. It is a routing signal meaning a higher-level orchestrator,
another workflow, or a human must take over. A run that reports `blocked` with evidence
of what was attempted and why is a successful handoff, not a failed run.

## Readiness

Before a spec moves to `ready-for-dev`, ask: could a developer implement the planned
work without inventing decisions that are not recorded?

- **PASS** — proceed.
- **CONCERNS** — proceed with named conditions or questions attached to specific
  stories.
- **FAIL** — do not proceed; the missing decisions must be recorded first.

Missing documentation is not automatically a problem. It matters only if the stories
depend on that information. A local, well-understood change may pass readiness with a
very thin spec; a cross-system initiative will not.

## Writing order and depth

1. Draft the five fields from the clarified intent (one question at a time).
2. Record consequential architecture decisions (or link to ADRs).
3. Split into implementation slices (stories) — each coherent and independently
   finishable.
4. Write acceptance criteria per story as observable, binary outcomes.
5. Add verification: tests, manual observations, independent review needed.
6. List residual risks and deferred work explicitly.

For trivial changes, this entire process is five bullets in conversation and the spec
file may never exist. For initiative work, the spec file is the contract the whole run
revolves around.

## Deterministic validation

After writing or editing a spec, run the bundled checker:

```sh
python3 bmad/scripts/check-spec.py path/to/SPEC.md
python3 bmad/scripts/check-spec.py --json path/to/SPEC.md   # machine-readable
```

It verifies the five required sections are present and the frontmatter `status` is in
the vocabulary. See [scripts/check-spec.py](../scripts/check-spec.py).

## Provisional choices and formal assumptions

For a formal pipeline, use SDD's [assumptions ledger](../../spec-driven-development/templates/SPEC.md)
and [review records](../../spec-driven-development/references/review-records.md).
Carry stable assumption IDs into affected stories, with decision owner,
consequence/reversibility, provisional status, latest safe point, and decision
evidence. Low-risk reversible choices may be batched at milestones within existing
authority. Consequential unresolved choices block dependent merge/release or other
effects before their safe boundary, even when milestone review comes later.
Rejection or material change invalidates affected tasks and derived evidence,
including transitive dependents; repair/reverify before restoring approval.
This records authority; it does not enlarge the autonomous work boundary.
