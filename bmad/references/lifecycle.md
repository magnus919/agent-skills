# Lifecycle and the Artifact Chain

For initiative work, BMad describes four phases plus a learning closeout. The phases
are a vocabulary for choosing the right depth of thinking, not a demand that every
change visit every phase. Direct work enters implementation immediately.

## The four phases

### Phase 1: Analysis (optional by default)

Purpose: explore the problem and validate the idea before committing to a plan.

Typical workflows: brainstorming, idea forging or pressure-testing, deep research,
product brief, PRFAQ or working-backwards challenge.

Use analysis when the problem, user, market, domain, or feasibility is unclear.
Skip or compress it when the request is already well understood. The useful principle:
do not write a precise spec on top of an unexamined idea.

### Phase 2: Planning

Purpose: define what should be built and for whom.

Typical workflows: PRD creation/update/validation; UX design when user experience is
material; SPEC creation as the concise machine contract.

The PRD is the stakeholder-facing description; the SPEC is the tighter execution
contract. They can coexist.

### Phase 3: Solutioning

Purpose: decide how to build the thing and divide it into implementable work.

Typical workflows: architecture; epics and stories; sprint planning and
implementation-readiness review.

The readiness gate asks whether a developer could implement the planned work without
inventing decisions that are not recorded. Vocabulary: PASS, CONCERNS, FAIL.

### Phase 4: Implementation

Purpose: turn direct intent or planned work into implemented, reviewed code.

The implementation path converges on the canonical Build loop: compress intent →
route to the smallest safe path → run longer with less supervision → diagnose failure
at the right layer → bring the human back only when needed. A direct small change and
a fully planned story enter the same loop; the difference is the strength and amount
of context available to it.

### Learning

After a meaningful epic, compare implementation with the original intent, review seams
between stories, record defects that isolation hid, reconcile contract drift, and
update durable context only when a lesson is expensive to rediscover. Create follow-up
work explicitly rather than letting it leak into the next task.

## The artifact chain

Artifacts are the connective tissue — the state that lets an agent resume, another
agent continue, an orchestrator route, and a human review.

| Stage | Typical artifact | What it stabilizes |
|---|---|---|
| Analysis | Research report, product brief, PRFAQ, brainstorm/forge report | Problem reality, customer value, alternatives, assumptions |
| Planning | PRD, UX design, SPEC | What to build, for whom, under which constraints |
| Solutioning | Architecture spine, ADRs, epics, stories | How to build it and how to divide the work |
| Readiness | PASS / CONCERNS / FAIL plus sprint status | Whether a developer can proceed without inventing decisions |
| Implementation | Story spec, implementation notes, code, tests | What was built and how it was verified |
| Review | Review trail, findings, patches, deferred items | Whether the result is correct, relevant, and safe to accept |
| Learning | Retrospective and action items | What the whole epic revealed that individual stories could not |

## Architecture as coordination

In a human team, architecture documentation aligns developers. In an agentic team it
prevents multiple agents from independently inventing incompatible solutions: one agent
choosing REST while another chooses GraphQL, one snake_case while another camelCase,
one Redux while another uses React Context.

An architecture artifact should record: the important decision; the context that made
it important; options considered; the selected option; the reasons for selection;
accepted consequences; the boundaries future agents must preserve.

The right amount of architecture is proportional to coordination risk. A local change
in a stable code path may need none. A cross-system initiative or multi-agent epic
normally needs it. Record consequential decisions as ADRs (see `adr-authoring`).

## Dividing work into stories

- Each story is a bounded, dispatchable work unit with its own acceptance criteria.
- Prefer vertical slices (end-to-end capability) over horizontal layers when possible.
- Sequence scariest-first: validate the risky approach early, not at the end.
- Do not pre-shred a pitch into disconnected tasks; decompose only downhill work that
  is already well understood.
- If an epic resists decomposition because nobody can define done, that is an unshaped
  project — route back to `product-shaping` rather than force-splitting it.

## Completion and exit conditions

A phase is complete when its artifact is written and its gate is passed (or
deliberately skipped for a trivial change). The whole run is complete when the final
checkpoint produces an accept decision and deferred work is tracked explicitly. If a
required capability is missing, evidence conflicts, review exposes an intent gap, or
the run stops for any reason, report the stop with evidence — never claim completion
without the checkpoint.
