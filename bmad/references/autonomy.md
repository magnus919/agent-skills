# Autonomy: BMad Build Auto

Build Auto is not a second implementation methodology. It is an unattended execution
wrapper around the canonical Build loop — one iteration per run: clarify intent,
create or resume a spec, implement, review, write a machine-readable terminal status.

## The autonomy gate

Autonomous execution is allowed only when **all** of these hold:

- the intent contract is coherent;
- acceptance is observable;
- the working boundary is explicit;
- the repository state is safe to modify;
- tests or evaluations can run;
- the agent can write a durable status;
- escalation behavior is defined.

If any condition is missing, do not run unattended. Run supervised instead, or report
the missing condition.

## Operating rules during autonomous work

- Make one coherent change at a time.
- Do not expand scope because you noticed unrelated improvements — record them as
  deferred findings.
- Do not merge, deploy, or change external systems unless explicitly authorized.
- Make local commits if the repository convention allows; never push without
  authorization.
- Stop on: intent gaps, missing capabilities, destructive ambiguity, failed
  verification, or non-convergent repair.
- Treat `blocked` as a routing signal for the orchestrator or human.
- Preserve evidence of what was attempted and why it stopped.

## Deferred findings

If review finds a real issue outside the current story, record it as deferred. The
implementer does not decide what happens to it — the orchestrator decides whether to
create a ticket, deduplicate it, escalate it, or ignore it. This is the control-plane
boundary: **Build Auto owns the implementation run and its spec artifact; the
higher-level orchestrator owns backlog policy.**

## Blocked is a routing signal

`blocked` normally means a higher-level orchestrator, another workflow, or a human
must take over. When a run reports `blocked`, the report should say what was
attempted, what stopped it, and what decision or capability is required to continue.

## Dark-factory fit

BMad provides the planning, context, implementation, review, and learning patterns. A
full dark factory still needs, around it: a work queue; scheduling and dispatch;
repository isolation; dependency and credential controls; deterministic tests; product
and domain evaluations; policy gates; merge and deployment rules; observability; retry
and escalation behavior; cost and time budgets. Build Auto can be one execution
primitive inside that larger system — it is not the whole system.

## Escalation behavior to define before starting

Before any autonomous run, write down:

- What triggers escalation (blocked, failed verification, new intent gap, cost cap).
- Who or what receives the escalation (orchestrator, queue, human channel).
- What evidence accompanies the escalation.
- What the default is when escalation is unreachable (stop safely, never guess).

## Stop before you fake convergence

If each fix to a machine-generated finding produces the next finding, the work is not
converging — the mechanism is. Change the mechanism (fresh context, different
evaluator, better spec) or bound the loop and report. Never report `done` while a
required gate is unresolved.
