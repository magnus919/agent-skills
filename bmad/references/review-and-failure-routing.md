# Review as Triage, and Failure Routing by Layer

A review that reports every possible issue becomes a second source of noise. BMad
treats review as **triage**: findings causally related to the current change are
addressed; unrelated-but-real findings are deferred; the workflow does not turn one
focused change into an uncontrolled cleanup project.

## Review focus

The review pass examines, in order:

1. **Correctness** — does the change do what the contract says?
2. **Scope** — did the change stay inside its boundary, or did it expand?
3. **Security** — did the change introduce or widen a security problem?
4. **Regressions** — did the change break existing behavior?
5. **Maintainability** — is the change consistent with the codebase's actual patterns?

## Triage rules

- Findings causally related to this change → address now.
- Findings unrelated but real → defer explicitly (tracked item, not a silent drop).
- Findings that are style preferences without contract backing → note, do not block.
- A finding that contradicts the approved contract → flag the contract conflict, do
  not silently re-decide the contract.

## The final human checkpoint

Organize the review around intent and risk first, then provide file and line
references. Never ask a human to review an unexplained file list. Present:

- original intent in one sentence;
- implemented behavior;
- files and systems affected;
- highest-risk decisions;
- tests and manual observations performed;
- review findings and their disposition;
- residual risks and deferred work;
- a clear accept / rework / investigate choice.

## Failure routing: diagnose the layer, not the symptom

| Failure | Route | Wrong reaction |
|---|---|---|
| Wrong outcome or wrong problem | Intent / analysis | Patching code to fit the wrong goal |
| Missing or contradictory requirement | Contract / planning | Implementing a guess as a requirement |
| Conflicting technical approach | Architecture | Hiding the conflict in local instructions |
| Incorrect local code | Implementation | Rewriting the spec to match buggy code |
| Insufficient test or evaluation | Verification | Re-running the same weak test until green |
| Unrelated pre-existing issue | Defer explicitly | Ballooning the change to fix everything |
| Unsafe ambiguity | Block and ask | Continuing on the most convenient interpretation |

The key discipline: **do not keep patching code when the specification is the real
problem.** If intent was wrong, patching the implementation only institutionalizes the
error. A mature agentic system moves backward to the layer where ambiguity entered.

## Non-convergence

If review and repair loop without the severity improving, stop and change the
mechanism:

- Bound the loop: cap fix/review rounds before starting.
- Use a severity gate: stop when the worst finding class stops shrinking.
- Apply a regression veto: a fix that introduces an equal-or-worse defect counts
  double.
- Prefer a fresh context restart over iterating in a polluted context.
- Report the residue and give the human the merge decision.

## Independence caveat

A self-reviewing agent can miss its own blind spots — the same model family may share
assumptions across planning, implementation, and review. For high-risk work, add
independent tests, a separate evaluator, security or privacy review, production-like
integration tests, human review of the highest-blast-radius decisions, and explicit
evaluation harnesses. Never describe persona separation as independent review unless
the reasoning paths are actually independent.
