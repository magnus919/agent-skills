# Usability Testing and Privacy

Usability work answers a bounded design question by observing authorized people attempt representative tasks. It does not manufacture customer truth, establish population prevalence, prove business outcomes, or replace accessibility conformance evaluation.

## Authorization Gate

Before recruiting, recording, or collecting any participant data, identify the responsible owner and confirm:

- the decision the work may inform and who has authority to act on it;
- participant characteristics grounded in actual users or affected roles;
- recruitment and compensation rules, including conflicts or power dynamics;
- accommodations and accessible participation paths;
- informed-consent information, voluntary participation, withdrawal, recording/transcription, and data use;
- collection minimization, access, storage, retention, deletion, and incident handling appropriate to policy and jurisdiction;
- whether legal, ethics, privacy, security, or institutional review is required.

An agent can draft materials and synthesize supplied authorized evidence. It cannot consent for a participant, invent a participant, impersonate research, or decide that policy and law do not apply.

## Plan From the Decision

Define:

1. research or design question;
2. behavior or decision the evidence could change;
3. participant characteristics and excluded populations, with rationale;
4. method and session context;
5. task starting state, realistic goal, completion evidence, and safety boundary;
6. prototype fidelity, unavailable behavior, and synthetic or approved data environment;
7. observation and note-taking method;
8. analysis plan and disagreement handling;
9. limitations and claims the study cannot support.

Choose participation scope based on decision risk, task and participant variation, accessibility needs, uncertainty, and the cost of missed failure. Do not use a universal participant count, time target, success threshold, or severity scale.

## Task and Facilitation Design

Write tasks as goals with enough context to act, not step-by-step instructions that reveal the interface. Avoid leading language and product terminology that the design is supposed to test. Include realistic interruption, permission, failure, or recovery only when the research question requires it and the environment can do so safely.

During moderated work, use neutral follow-ups about expectations, observations, and decisions. Distinguish what the participant did, what they said, what the facilitator inferred, and what the team decided. A preference statement is not automatically a task barrier; a completed task is not automatically free of confusion or risk.

## Safe Prototypes and Data

Use clearly synthetic fixtures such as `DEMO-CARD-NOT-VALID`, `workspace-demo-7`, or reserved `.example`/`.test` identifiers. Do not ask participants to enter real credentials, payment data, financial access, secrets, health data, or personal data into an unsafe prototype. When realistic data is necessary, use an approved environment and document safeguards, fidelity, retention, and deletion.

Do not claim a prototype performed a side effect it cannot perform. Mark simulated notifications, persistence, payments, approvals, or external-system changes as simulation and account for the fidelity gap in findings.

## Analysis and Reporting

Retain an audit trail from observation to implication:

| Layer | Example form |
|---|---|
| Observation | What occurred in the task and context |
| Participant interpretation | Quote or paraphrase only when actually recorded and authorized |
| Researcher inference | Why the behavior may have occurred, with alternatives |
| Design implication | Contract or hypothesis that might change |
| Decision | Accepted, rejected, deferred, or needs more evidence, with owner |

Group findings by task force, failure/recovery pattern, role, and context rather than only by screen. Preserve disagreement and negative cases. State whose behavior was not studied, which paths were simulated, where facilitator intervention changed the task, and what evidence would be needed to generalize.

A usability session reports observed barriers and successes within its tasks, participants, and environment. It does not establish WCAG conformance, accessibility across disability contexts, population prevalence, analytics performance, preference at scale, or product outcome. Use `templates/usability-study.md` for the plan and results, and route accessibility test design to [web-accessibility](../../web-accessibility/SKILL.md).
