# Human Systems, Learning, and Sustainable SRE

Reliability work is cognitive and social work as well as technical work. Use this reference when designing on-call, incident training, postmortem learning, documentation, team health, or operational policies that affect people.

## Source anchors

This reference synthesizes *Seeking SRE*, “Do Docs Better,” “Active Teaching and Learning,” “Psychological Safety in SRE,” “SRE Cognitive Work,” “Beyond Burnout,” and “Against On-Call: A Polemic,” with the practical on-call, incident, and postmortem chapters of *The Site Reliability Workbook*. These sources include opinion and experience as well as general practice. Treat claims about health, accommodation, and employment as context for humane design, not medical or legal advice.

## Design for cognitive work

During an incident, operators are not interchangeable sensors. They interpret incomplete signals, form and revise hypotheses, coordinate across boundaries, and choose actions under time pressure. Reduce avoidable cognitive load:

- provide a small set of trusted dashboards and a current service map;
- make dependencies, recent changes, and rollback paths easy to find;
- separate incident command from deep technical investigation;
- record decisions and hypotheses so responders do not repeatedly reconstruct context;
- prefer reversible actions and observe their effects;
- make escalation normal and fast;
- preserve a quiet channel for coordination when the main channel is noisy.

Automation should remove repetitive work while keeping the operator's decision boundary visible. A system that acts automatically must expose what it observed, what it changed, and how to stop or reverse it.

## On-call is a system property

Do not judge an on-call rotation only by whether pages are answered. Review:

- page volume, actionability, urgency, and repeat rate;
- time spent on pages, tickets, handoffs, and recovery;
- interruptions outside shifts and the quality of escalation;
- whether responders have current runbooks, access, context, and training;
- whether the service can be operated without heroic individual knowledge;
- recovery time and post-incident cognitive load;
- whether the rotation leaves time for engineering that reduces future load.

A rotation that relies on exhausted people, undocumented exceptions, or constant escalation is not reliable even when uptime looks acceptable. If the service cannot support a sustainable rotation, reduce scope, improve automation, change the service, or stop carrying the pager until the risk is acknowledged.

## Psychological safety in reliability work

Effective teams make it safe to report uncertainty, challenge a plan, ask for help, and surface a risk raised by a junior responder. Psychological safety is not permission to skip accountability. It is a condition for receiving the information needed for accountability.

Make it observable:

- the incident commander explicitly invites dissent and clarifying questions;
- a responder can pause a rollout or mitigation when a stated safety condition is violated;
- postmortems analyze system conditions rather than assign personal fault;
- leaders respond to bad news with investigation and support, not punishment;
- action items improve interfaces, defaults, tests, access, or training rather than merely reminding people to be careful.

A blameless culture still names decisions, conditions, and owners. “No blame” must not become “no learning” or “no follow-through.”

## Documentation as an operational control

Documentation is part of the service's reliability surface. A document should have:

- a named audience and task;
- prerequisites and access requirements;
- observable symptoms and scope boundaries;
- safe first actions and explicit stop conditions;
- verification after each consequential action;
- escalation path and rollback or recovery path;
- owner, review date, and links to source configuration or dashboards.

Keep documentation in the engineering workflow. Update it when a runbook is used, an incident exposes a gap, a configuration changes, or a new operator is trained. Stale documentation should be treated as an operational defect, not as a writing problem deferred indefinitely.

## Practice before production

Incident command and mitigation are skills. Use bounded, low-risk practice:

- scenario exercises with realistic but synthetic failures;
- game days and disaster-recovery drills;
- tabletop exercises for third-party and communication failures;
- shadow shifts and graduated on-call access;
- short drills that rehearse one capability, such as rollback or traffic shedding.

After an exercise, record what participants could and could not find, decide, or execute. The learning objective is not theatrical realism. It is to expose missing context, unsafe defaults, confusing roles, and untested recovery paths before a real incident.

## Learning loops

A postmortem is useful only when it changes future capability. Link each action to:

- the failure condition it addresses;
- an owner with authority and time;
- a due date or review checkpoint;
- an observable completion criterion;
- a later verification that the change reduced risk or toil.

Track recurring triggers across incidents. A single incident may be local; a pattern across services may justify a platform, design, training, or organizational intervention. Do not optimize for a rising closure count if the actions are vague or unverified.

## Inclusion and sustainable work

Design for different working styles and access needs without requiring people to disclose private medical information to participate safely. Practical safeguards include written incident roles, asynchronous handoff records, predictable escalation paths, quiet channels, clear interruption expectations, and multiple ways to contribute during reviews and exercises.

Do not diagnose, infer, or prescribe. Ask what working arrangement or interface makes the task safe and effective, follow applicable organizational processes, and keep private information out of operational artifacts.

## When on-call should be redesigned

Treat these as design signals, not individual failure:

- persistent high page volume or repeated non-actionable pages;
- responders cannot complete engineering work;
- incidents depend on one person or one undocumented procedure;
- escalation is delayed because people fear being judged;
- frequent sleep disruption, burnout, or unsafe fatigue;
- the service has no credible degraded mode or recovery test;
- the team cannot staff the rotation without coercion.

The response may be alert reduction, service simplification, ownership change, scope reduction, a dedicated operations function, or retiring the service. “Try harder” is not a reliability strategy.

## Agent procedure

When asked to improve on-call or incident learning, load this reference with `oncall-best-practices.md`, `incident-command-system.md`, and `postmortem-culture.md`. Include both service metrics and human-work metrics. Distinguish observed evidence, team-reported experience, and proposed safeguards.
