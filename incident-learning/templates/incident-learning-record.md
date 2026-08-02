# Incident-Learning Record

Use this template to structure an incident into a learning record. The record separates observed facts from causal hypotheses and unresolved uncertainty, maps escaped-from gaps, and links to the follow-up work map.

## Incident identifier

| Field | Value |
|---|---|
| **Incident ID** | |
| **Title** | |
| **Date** | |
| **Duration** | |
| **Severity** | |
| **Systems affected** | |
| **Services affected** | |
| **User impact** | |
| **Detection method** | (alert, user report, manual observation, exercise finding) |
| **Postmortem reference** | (link to the blameless postmortem, if one exists) |

## Observed facts

*What happened — backed by telemetry, logs, direct observation, or reproducible measurement. Every fact must have a named source. No interpretation, no inference, no blame.*

| # | Fact | Source | Timestamp / time range |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

## Causal hypotheses

*Inferences about why the incident occurred. Each hypothesis must be labeled with confidence and at least one alternative explanation.*

| # | Hypothesis | Supporting evidence (fact #s) | Confidence | Alternative explanations | Testability |
|---|---|---|---|---|---|
| 1 | | | (high/medium/low) | | |
| 2 | | | | | |

**Confidence level guide:**
- **High**: supported by multiple independent evidence sources; alternatives ruled out; causal mechanism well-understood.
- **Medium**: supported by some evidence; alternatives plausible but less consistent.
- **Low**: consistent with evidence but not strongly supported; alternatives equally plausible; mechanism speculative.

## Contributing conditions

*System states, process gaps, environmental factors that enabled or amplified the incident — without necessarily causing it.*

| # | Condition | How it contributed | Related hypotheses |
|---|---|---|---|
| 1 | | | |
| 2 | | | |

## Unresolved uncertainty

*Open questions, competing hypotheses, missing data, and unknowns. Every uncertainty must state why it matters and what would resolve it.*

| # | Uncertainty | Why it matters | What would resolve it | Status |
|---|---|---|---|---|
| 1 | | | | (open / investigating / cannot resolve) |
| 2 | | | | |

## Escaped-from mapping

*What gap allowed this incident to reach production or users? Map each gap to one or more categories.*

| # | Gap description | Escaped-from category | How it contributed | Follow-up domain |
|---|---|---|---|---|
| 1 | | (escaped requirement / missing monitoring / unsafe authority / migration gap / adoption consequence) | | (product / code / tests / evals / operations / governance) |
| 2 | | | | |

**Escaped-from categories:**
- **Escaped requirement**: A needed requirement was absent, incomplete, or incorrectly specified.
- **Missing monitoring or observability**: No signal existed to detect the condition.
- **Unsafe authority or access**: Insufficient guardrails on who could act or what actions were permitted.
- **Migration gap**: A transition introduced or exposed the condition.
- **Adoption consequence**: User or operator behavior contributed to the incident.

## Follow-up work map

*Link to the follow-up work map. Every significant finding maps to at least one follow-up item with an owner, domain, and verification method.*

**Follow-up work map reference:** (link or reference to the follow-up work map document)

| Finding | Domain | Description | Owner | Target date | Verification method | Status |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |

## Verification and closure summary

| Follow-up ID | Status | Implementation evidence | Verification evidence | Effect evidence | Closure date |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |

**Closure states:** Verified closed / Verified closed — effect pending / Rejected / Superseded / Open

## Record metadata

| Field | Value |
|---|---|
| **Record author** | |
| **Record date** | |
| **Last updated** | |
| **Reviewers** | |
| **No-blame attestation** | This record contains no blame assignment. Findings describe system outcomes, not individual failures. |
