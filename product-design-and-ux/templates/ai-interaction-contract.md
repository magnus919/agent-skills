# AI Interaction Contract

Use alongside `interface-contract.md`. Describe observable behavior and link every consequential choice to approved evidence or an explicit assumption.

## Identity and authority

- Contract ID, surface, linked outcome/task:
- Roles, entry conditions, decision owner:
- Evidence and assumptions:
- AI role: assist / draft / recommend / rank / predict / route / execute:
- Human review or approval boundary:
- Prohibited or out-of-scope side effects:
- System/model/prompt/retrieval/tool version:

## Context and grounding

| Input or source | Owner and permission | Freshness/availability | Missing, stale, or conflicting behavior | What the person can inspect |
|---|---|---|---|---|
|  |  |  |  |  |

## Output and control

| State or output | What is shown | User action and validation | Persistence/side effect | Recovery, fallback, or escalation |
|---|---|---|---|---|
| Pending/streaming |  |  |  |  |
| Partial |  |  |  |  |
| Complete |  |  |  |  |
| Unsupported/uncertain |  |  |  |  |
| Failed/blocked |  |  |  |  |
| Escalated/corrected/committed |  |  |  |  |

## Feedback and handoff

- Optional alternate or opt-out path and what changes:
- Escalation trigger, destination, status, and transferred context:
- Feedback signal and purpose:
- User notice/consent, minimization, retention, and owner:
- How preference, task completion, and correctness are distinguished:
- Triage, evaluation, and release trigger:

## Change acceptance fixtures

| Fixture/scenario and provenance | Version/change under test | Expected observable behavior | Evidence/result | Verdict | Limitation or follow-up |
|---|---|---|---|---|---|
| Normal input |  |  |  |  |  |
| Ambiguous or unsupported input |  |  |  |  |  |
| Stale/conflicting context |  |  |  |  |  |
| Permission/privacy/unsafe case |  |  |  |  |  |
| Interruption/partial action/re-entry |  |  |  |  |  |

Use one verdict per fixture: passed, failed, blocked, inconclusive, or not-applicable. Record the reason and missing evidence; an unrun or blocked fixture cannot pass.

## Open decisions

| Decision | Alternatives and tradeoff | Owner | Resolution/revisit gate |
|---|---|---|---|
|  |  |  |  |

Route WCAG/ARIA and conformance evidence to `web-accessibility`; route model-quality and statistical thresholds to `agent-evals-and-observability` or `data-scientist`; route telemetry implementation and privacy controls to the owning specialists.
