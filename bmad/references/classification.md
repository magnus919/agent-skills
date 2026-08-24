# Work Classification: Route to the Smallest Safe Path

The first decision in every BMad-style run. The goal is never to maximize ceremony —
it is to spend the minimum process that keeps the work safe. Classify, then choose.

## The three classes

| Class | Shape | Blast radius | Process |
|---|---|---|---|
| **Direct** | Goal clear, change local, existing patterns well established | Small | Minimal clarification, then implement. No contract file needed. |
| **Bounded** | Coherent change, some choices to make, spans a few files/modules | Medium | Five-field intent contract (or lightweight spec), short plan, implement, review. |
| **Initiative** | Cross-component, multi-story, high-risk, or strategically uncertain | Large / durable | Analysis → planning → solutioning → implementation → learning. Intent contract plus architecture plus stories. |

## Direct-work tests

Use the direct path when all of these hold:

- The goal is clear to the requester and to the agent after one pass.
- The change is local to one area with established patterns.
- No major product or architectural choices are involved.
- Acceptance can be expressed with focused tests or simple observations.
- The blast radius is small enough that a wrong guess is cheap to undo.

A typo fix, a documented one-file bug, a rename following an existing convention — all
direct. Forcing a planning ceremony onto these is exactly the overhead BMad rejects.

## Bounded-work tests

Use the bounded path when:

- The change is coherent but spans enough surface that assumptions matter.
- Several reasonable approaches exist and the choice affects the result.
- The work will be reviewed by another agent or a human checkpoint.
- The work may be resumed later or delegated — a written contract earns its keep.

The contract can be five bullets in conversation for the smallest bounded work; write
it to a file when the work outlives one session or crosses an agent boundary.

## Initiative tests

Use the full path when any of these hold:

- Several components or systems must coordinate.
- The problem statement is still uncertain.
- Meaningful UX, security, privacy, data, or operational choices exist.
- Multiple stories may be implemented by different agents.
- The work will create durable architectural consequences.
- The human needs a written contract for later review or delegation.
- You cannot state a coherent intent contract after one pass.

Initiative work from a vague chat request is an explicit stop condition: do not
implement it directly. Compress intent, get approval, then decompose.

## The one-question rule

- Inspect the repository, artifacts, config, and tests before asking anything.
- Ask at most one high-leverage question at a time.
- When a choice is needed, provide a recommended answer and the trade-off.
- Keep questions about choices, not facts you could retrieve.

## Stop conditions

Stop and report instead of proceeding when:

- The intent contract cannot be stated coherently.
- The request is initiative-scale and no contract has been approved.
- The repository state is unsafe to modify (uncommitted work you did not create,
  a shared checkout in use, a dirty tree you cannot restore).
- Acceptance cannot be expressed observably.
- Required capability or credentials are missing.
- A destructive or irreversible action was not explicitly authorized.

## Routing a tripped loop

If work keeps failing or expanding, do not extend the boundary mid-loop. Route back to
classification:

- Failure because scope was unclear → re-compress intent (bounded contract).
- Failure because the problem was unvalidated → route to `product-discovery`.
- Failure because the bet was never shaped → route to `product-shaping`.
- Failure because the delivery flow has its own gates → route to `neckbeard`.
