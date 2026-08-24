# Adoption: Incremental Protocol, Then Automation

Do not begin by converting every project to a full BMad installation. Begin with a
small protocol trial and add autonomy only after acceptance is testable.

## Step 1: Establish a project-context boundary

Create or audit AGENTS.md. Keep only: repository policies; non-obvious commands;
conventions that differ from defaults; cross-component invariants; known, observed
pitfalls; pointers to authoritative documents. Do not use AGENTS.md as a generated
encyclopedia. See [project-context.md](project-context.md).

## Step 2: Require an intent contract for meaningful work

Before implementation, capture Why, Capabilities, Constraints, Non-goals, and Success
signal. For trivial changes this can be five short bullets in the agent conversation.
For a larger initiative it becomes a versioned spec file. See
[spec.md](spec.md) and the templates.

## Step 3: Route by complexity and coordination risk

- Tiny and obvious → direct implementation.
- Bounded but non-trivial → intent contract, short plan, implementation, review.
- Cross-component or multi-story → analysis, PRD or SPEC, architecture, stories,
  readiness gate, sequential implementation.
- High-risk or regulated → add explicit human and independent evaluation gates.

## Step 4: Add autonomy only after acceptance is testable

Do not start with unattended execution. First make sure:

- the story boundary is coherent;
- acceptance criteria are observable;
- tests and evaluations exist;
- the agent can report status;
- blocked work can be escalated;
- unrelated findings can be deferred;
- repository isolation and rollback work.

See [autonomy.md](autonomy.md).

## Step 5: Close the loop

After an epic or substantial change:

- compare the result with the original intent;
- review seams between stories;
- record defects that isolation hid;
- reconcile any contract drift;
- update context only when a lesson is expensive to rediscover;
- create follow-up work explicitly rather than letting it leak into the next task.

## Mapping to a dark-factory system

| BMad concept | Likely implementation |
|---|---|
| Named agent | Role-specific skill, prompt, or subagent profile |
| Workflow skill | Reusable protocol with explicit inputs, outputs, and gates |
| Product brief / PRD / SPEC | Versioned Markdown contracts |
| Architecture spine | ADRs, C4 context, interface contracts, system invariants |
| Epics and stories | Dispatchable work units |
| Sprint status | Machine-readable state file or database row |
| Build | The implementation harness |
| Build Auto | A controlled autonomous runner |
| Code review | Independent reviewer and repair loop |
| Retrospective | Evidence-based evaluation and learning update |
| Project context | AGENTS.md plus carefully curated repository rules |
| Party Mode | A deliberation protocol with selectable single-model or independent-agent modes |

The strongest combination with a dark-factory architecture:

1. Human states an objective.
2. Analyst/PM-style workflow compresses it into an intent contract.
3. Human approves the contract and important trade-offs.
4. Architect-style workflow establishes boundaries and invariants.
5. Story sharder creates bounded work units.
6. Orchestrator dispatches one unit at a time.
7. Developer agent implements in an isolated worktree.
8. Automated tests and domain evaluations run.
9. Independent review agent triages findings.
10. The orchestrator routes done, blocked, deferred, or rework.
11. Human reviews the final product at the appropriate checkpoint.
12. Retrospective updates the process and only the durable project context.

Division of labor: BMad-style workflows own understanding and handoff quality; the
factory orchestrator owns scheduling and policy; the implementation agent owns local
code changes; evaluators own evidence; the human owns intent, authority, and
acceptance.

## Known limitations to keep honest

- **Role-play is not independence** — use actual subagents, independent model calls,
  or an external evaluator when independence matters.
- **Better documents do not guarantee better decisions** — human judgment and evidence
  remain necessary.
- **Documentation can become a tax** — strongest when artifacts preserve load-bearing
  decisions; counterproductive when every minor change produces ceremony or stale
  plans compete with the code.
- **A self-reviewing agent can miss its own blind spots** — add independent checks for
  high-risk work.
- **Autonomy can amplify bad intent** — the more capable the execution loop, the more
  important it is to freeze the right intent before it runs.
- **Version drift is real** — BMad is actively evolving; when installing official
  tooling, pin versions and follow current docs.
- **Not a complete dark factory** — the method supplies the control plane; you still
  need the queue, dispatch, isolation, policy, observability, and budget layers.
