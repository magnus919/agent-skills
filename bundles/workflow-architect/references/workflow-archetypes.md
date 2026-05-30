# Workflow Archetypes Library

Common workflow patterns for convergence detection and question seeding.
The interviewer and observer match the user's answers against these archetypes
to accelerate convergence.

Each archetype includes:
- **Signature signals** — opening messages, tool choices, and patterns
- **Typical phases** — the stages this workflow tends to follow
- **Common branching points** — decisions that determine direction
- **Exit patterns** — how sessions naturally end in this archetype
- **Kanban affinity** — whether this workflow tends to benefit from kanban

---

## Morning Triage

### Signals
- First session of the day
- Opens with status checks, dashboards, task lists
- Asks "what's pending," "any updates," "what's new"
- References multiple threads or projects in the first 2-3 messages

### Typical Phases
1. **Inbox sweep** — check notifications, email, task assignments
2. **Prioritization** — decide what's urgent vs important
3. **Stale item handling** — clear or defer leftover tasks
4. **Deep work setup** — commit to a focus area for the day

### Branching Points
- Overdue items → firefighting mode vs defer and focus
- Urgent request from collaborator → context switch
- "Everything's quiet" → proactive work, backlog grooming

### Exit Patterns
- Natural pause after clearing the inbox
- Transition to a specific task ("ok, now I'm going to work on X")
- Explicit hand-off to deep work mode

### Kanban Affinity
High — this is the most kanban-compatible pattern. Phases are sequential
and easy to map to board lanes.

---

## Deep Work Sprint

### Signals
- Opens with a specific goal or deliverable
- Requests focused, single-threaded work
- Resists interruptions or context switches
- Uses language like "no distractions," "lock in," "just this"

### Typical Phases
1. **Setup** — gather context, relevant files, open issues
2. **Build / Write** — the main work, often in bursts
3. **Test / Review** — check output, catch errors
4. **Polish / Ship** — final pass, commit, deliver

### Branching Points
- Encounter unexpected complexity → research/downtool vs push through
- Test failure → debug loop vs return to building
- Interruption → context switch vs defer

### Exit Patterns
- Natural completion of the deliverable
- Exhaustion / diminishing returns ("I need a break")
- External interruption that breaks flow

### Kanban Affinity
Medium — kanban works for the phases but deep work is often non-linear
(research → build → research → build). Use simple lanes, no WIP.

---

## Bug Hunt / Debugging

### Signals
- Opens with error messages, stack traces, or "this is broken"
- Shares logs, reproduction steps, or screenshots
- References specific files, lines of code, or symptoms
- Uses language like "why does," "this shouldn't," "it worked before"

### Typical Phases
1. **Reproduce** — confirm the bug exists and find the trigger
2. **Narrow** — isolate the root cause through elimination
3. **Fix** — apply and verify the correction
4. **Test** — ensure fix doesn't break adjacent behavior

### Branching Points
- Cannot reproduce → ask for more context vs move on
- Root cause found → fix directly vs file issue for later
- Fix breaks something else → rollback vs iterative fix

### Exit Patterns
- Bug fixed and verified
- Filed as a tracked issue for later resolution
- Punted (can't reproduce, insufficient context)

### Kanban Affinity
Low — bug hunting is inherently non-linear and exploratory.
Lane-based tracking adds friction, not clarity.

---

## Research Synthesis

### Signals
- Opens with a topic question, not a task
- Requests information gathering, analysis, or comparison
- Asks "what do we know about X" or "research Y"
- References papers, articles, documentation

### Typical Phases
1. **Scoping** — define what you're trying to learn
2. **Gathering** — collect sources, clip, extract
3. **Synthesis** — connect findings, identify patterns
4. **Capture** — write summary, vault notes, or article

### Branching Points
- Found conflicting sources → need to reconcile vs present both
- Scope creep → broaden vs narrow
- Serendipitous find → follow the thread vs save for later

### Exit Patterns
- A written deliverable (note, article, summary)
- Key question answered
- Decided the topic doesn't warrant deeper investigation

### Kanban Affinity
Low — research is emergent. The process is real but each session
looks different. Kanban doesn't add value.

---

## Creative Drafting

### Signals
- Opens with a concept, not a question
- Uses language like "what if," "imagine," "draft something"
- References style, tone, audience
- Iterates on output rather than analyzing it

### Typical Phases
1. **Inspiration** — gather references, mood, constraints
2. **Draft** — produce the first version
3. **Edit** — refine, restructure, tighten
4. **Polish** — final pass, formatting, delivery

### Branching Points
- Blocked on direction → try a different angle vs take a break
- First draft is weak → revise vs start fresh
- User dislikes direction → pivot vs push through

### Exit Patterns
- A finished piece (article, script, design)
- Published or delivered to destination
- Saved as draft for later

### Kanban Affinity
Medium — phases are sequential but the loop (draft → edit → draft) is
common. Kanban with "Draft" and "Polish" lanes works if WIP limit is 1
(items shouldn't pile up in Draft).

---

## Kanban Pipeline

### Signals
- Opens with "what's on the board," "move this task," "status"
- References specific task IDs, lanes, or tickets
- Asks about progress, blockers, or next steps
- Uses language like "ready for review," "in progress," "done"

### Typical Phases
1. **Inbox / Triage** — new items, assign, prioritize
2. **In Progress** — active work
3. **Review** — code review, approval, feedback
4. **Done** — completed, verified

### Branching Points
- Item rejected in review → return to In Progress vs discard
- Blocked → flag vs work around
- Priority change → reprioritize board vs continue

### Exit Patterns
- Board is up to date
- All items in appropriate lanes
- Next items are queued and ready

### Kanban Affinity
Very High — this workflow already uses kanban. The bundle should
include board definitions and lane rules.

---

## Firefighting / Incident Response

### Signals
- Urgent language ("this is down," "blocked," "critical")
- References production, users, or live systems
- Short, direct messages — no preamble
- Multiple rapid iterations

### Typical Phases
1. **Triage** — assess severity, declare incident
2. **Response** — stabilize, mitigate, restore
3. **Root cause** — investigate what happened
4. **Remediation** — permanent fix
5. **Post-mortem** — document what was learned

### Branching Points
- Cannot reproduce → different analysis path
- Fix requires deploy → expedited vs standard
- Incident is actually nothing → stand down

### Exit Patterns
- Service restored
- Fix applied and verified
- Post-mortem written

### Kanban Affinity
Low-to-medium — incident response has a clear process but it's
too time-sensitive for kanban tracking. Post-mortem tracking can
use kanban.

---

## On-Call Rotation

### Signals
- Opens with status checks, alerts, or monitoring dashboards
- References pagers, escalations, or rotation schedules
- Shifts between long idle periods and high-intensity bursts

### Typical Phases
1. **Handover** — review what happened since last shift
2. **Monitoring** — watch dashboards, wait for alerts
3. **Response** — handle incidents as they arise
4. **Documentation** — log what happened for next shift

### Branching Points
- Alert → respond vs acknowledge (no action needed)
- Escalation → handle vs pass to senior
- Quiet period → proactive work vs rest

### Exit Patterns
- Shift end — handover written and delivered
- All active incidents resolved or escalated

### Kanban Affinity
Low — on-call is reactive and event-driven. Kanban doesn't help
with incident frequency.

---

## Cross-Archetype Matching

A user's workflow may blend multiple archetypes. Common combinations:

| Combination | What it looks like |
|-------------|-------------------|
| Triage → Deep Work | Checks tasks, then settles into building |
| Bug Hunt → Kanban | Debugs, then tracks the fix on a board |
| Research → Creative Draft | Gathers sources, then writes from them |
| Firefighting → Post-mortem | Responds, then documents learnings |
| Morning Triage → Firefighting | Starts calm, shifts to urgent response |

When matching, note the primary archetype and list secondary blends.
The bundle should reflect the workflow as it actually flows, not force-fit
a single archetype.

---

## Archetype Summary Table

| Archetype | Kanban Fit | Bundle Bias |
|-----------|------------|-------------|
| Morning Triage | High | Clear phases, predictable transitions |
| Deep Work Sprint | Medium | Phase-based with loop allowance |
| Bug Hunt | Low | Tooling and diagnostics, not process |
| Research Synthesis | Low | Reference management, not phases |
| Creative Drafting | Medium | WIP limit of 1 on Draft lane |
| Kanban Pipeline | Very High | Full board definition |
| Firefighting | Low–Medium | Post-mortem tracking only |
| On-Call | Low | Handover documentation |
