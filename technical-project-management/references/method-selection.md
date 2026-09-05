# Select and tailor the approach

Use when choosing a method or when delivery pain suggests the current method no
longer fits. Basis: S01's fit-for-purpose argument and S06's distinction among
delivery approaches. This decision procedure is a practical synthesis, not a
certification decision tree or a ranking of methodologies.

## Diagnose before prescribing

Inspect six things: requirement stability, technical uncertainty, ability to
release partial value, cost of reversing a decision, external timing constraints,
and actual team autonomy/capacity. Also identify mandatory governance. A team
calling its work agile does not prove these conditions hold.

Default to the team's existing adequate approach. Change it only to address an
observed problem. Do not use a weighted score to hide a veto condition such as an
unavailable safety approver or impossible vendor lead time.

| Conditions | Candidate | First check | Failure signal / response |
|---|---|---|---|
| Known deliverable, stable interfaces, expensive irreversible steps | Predictive with staged decisions | Is the dependency plan feasible with actual resources? | Repeated late changes: shorten planning horizon and add discovery |
| Need to learn what works through feedback | Iterative | Who evaluates the experiment and when? | No feedback access: resolve it before committing more cycles |
| Useful components can be accepted separately | Incremental | Does each increment work end to end? | Layer-only milestones: redefine around usable capability |
| Cohesive team, clear product authority, regular inspect/adapt cycle | Scrum | Can the team protect a goal and meet a shared quality bar? | Many unrelated interruptions: fix intake/capacity, consider flow |
| Variable arrival, support work, aging queues | Flow-based/Kanban | Are start/finish and capacity policies explicit? | WIP growth: investigate bottleneck before adding work |
| Scarce resources repeatedly delay otherwise independent work | Critical-chain lens | Are resource contention and readiness visible? | Treating buffers as hidden padding: make them explicit and owned |
| Bounded product opportunity, discretionary scope, protected capacity | Appetite-based/Shape Up | Can leadership actually protect the bet? | Mandatory scope exceeds appetite: reshape or choose a different model |
| Hardware/vendor stages plus evolving software | Hybrid | Who accepts the cross-method interfaces? | Two conflicting plans: establish one milestone/decision record |

Predictive is a planning approach; Scrum is a framework; critical path and critical
chain are scheduling techniques; PRINCE2 is a project management method; Kanban
manages flow. They are not interchangeable alternatives at one abstraction level.
Stage governance can coexist with iterative delivery. Iterative learning does not
necessarily produce a releasable increment; incremental delivery need not entail
high uncertainty. Do not call all of these "agile" without qualification.

## Make the choice actionable

Write an approach decision: observed conditions, selected approach, nearest rejected
alternative, who decides scope and dates, cadence, required evidence, and revisit
trigger. Define the first inspection point. Explain only the tradeoff the user
needs, rather than reciting the whole matrix.

Example (hypothetical): a device project has a long-lead board order and uncertain
calibration software. Use a staged procurement decision for hardware and short
software learning cycles, tied to an integrated prototype acceptance milestone.
Do not let software sprint completion imply the device is ready for certification.

## Edge cases and exit

Mandatory organizational methods constrain tailoring: surface a justified exception
request rather than quietly replacing the method. A small team does not need
separate meetings for every practice. A multi-project program may need an additional
benefits and governance owner; expose that need instead of promising this skill
replaces enterprise program management.

Complete when one approach and its adaptations address the diagnosed conditions,
its coordination contract is explicit, and a review trigger exists.
