# Typed decision placement

Fill this before introducing a typed model decision into an existing harness.
Model schema and calibration details belong with the model integration owner;
this records how the decision connects to current state and an accepted task.

- **User outcome and acceptance boundary:**
- **Deployment decision target:**
- **System One model / version / question-config revision:**
- **Trusted input source and revision:**
- **Finite candidate source, IDs, and inventory revision:**
- **Eligibility/applicability rule:** What makes each candidate eligible? How is
  no-applicable-candidate distinguished from a winner among the offer?
- **Decision question:** What evidence in the supplied state can answer it?
- **Freshness binding:** Which goal, state, candidate, or policy changes invalidate
  the response before execution?
- **Deterministic policy and authorization boundary:**
- **Action effect evidence:** What observable before/after change is recorded?
- **Independent completion oracle:** What proves the user's outcome at the
  requested surface?

| Outcome | Required behavior | Owner / evidence |
|---|---|---|
| Selected eligible candidate | Revalidate request binding and policy, then execute only that candidate | |
| No eligible candidate | Skip, request new evidence, or escalate as specified | |
| Ambiguous or insufficient evidence | Preserve unknown; route to named review/retry/defer path | |
| Stale state or candidate inventory | Discard response and rebuild from current state | |
| Invalid response or provider unavailable | Fail closed for consequential action; apply bounded retry/fallback policy | |
| Policy denial | Do not execute; preserve denial reason and audit evidence | |
| Action failed or effect unknown | Do not report completion; reconcile before retrying a mutation | |

- **Representative cases and held-out task units:**
- **Near misses:** irrelevant top-ranked item, omitted best candidate, stale ID,
  misleading distribution, delayed/absent effect, and plausible false completion.
- **Measures:** candidate coverage, false applicability, selection errors,
  accepted outcomes, false stops, unknown/recovery lanes, human intervention,
  latency and full cost.
- **Baseline and comparison conditions:**
- **Rollback or disablement:**
- **Remaining unverified claims:**
