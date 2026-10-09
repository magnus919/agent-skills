# Earned autonomy under accountable human governance

Use for promotion/demotion thresholds and authority review. This is a local decision framework, not an industry certification or the separate Six-Level Governance framework. Accountable humans determine acceptable risk and grant, maintain, expand, reduce, suspend or revoke authority. An agent may assemble evidence and recommendations; it cannot sign its own grant, alter ceilings or self-promote.

| Level | Meaning for a specific capability/environment/action class |
|---|---|
| L1 | AI-assisted: humans select and execute actions |
| L2 | Delegated execution with human review under explicit approval gates |
| L3 | Autonomy within verified boundaries and externally enforced grants |
| L4 | Mostly autonomous operation within the grant, with tested escalation |
| L5 | Sustained autonomous operation supported by continuing evidence and revocable controls |

Different rows for diagnosis, mutation, rollback, paging, closure and expansion may have different levels. Level 5 is optional; higher levels never imply unrestricted resources, self-directed authority expansion or removal of mandatory human gates. An L4 mutation grant does not remove SRE's human incident-closure requirement. The effective authority is the intersection of the approved grant and all applicable host, organizational, environment and action policies. Resolve conflicting policy precedence through authorized policy owners; until resolved, no broader effect may execute.

## Decision procedure

1. For an initial grant, record current authority as none and choose **grant** or **hold** pending missing evidence; do not pretend an existing grant exists. Link the capability admission ID, source revision and effective configuration. Admission alone confers no authority. Identify accountable service/risk owner and independent approval authority. Inventory exact capability, environment, tenant/resource, tool/effect and maximum permitted level. Describe prohibited actions and human-only decisions.
2. Agree thresholds before reviewing the candidate's score. Require local representative evidence: incident/noise mix, severity, action opportunities and denominators, near misses, confidence/uncertainty, held-out replay/fault runs, customer-boundary recovery, rollback and policy enforcement tests. Specify sample sufficiency, freshness, observation period and missing-data behavior. Seven clean days, a vendor benchmark or agent confidence alone is insufficient.
3. Balance speed, time and cost against harm: bad mutations, missed escalation, false closure, data loss/exposure, unnecessary paging, review minutes, rework and alert fatigue. Record risk acceptance with owner and expiry. Low escalation rates can reflect suppressed escalation; appropriate handoff is not a failure.
4. For an established grant, choose explicitly: **maintain** current scope; **expand** only the proven capability; **reduce** limits; **suspend** temporarily pending evidence; **revoke** the grant. Define operational stop/reduction triggers for telemetry loss, drift, incident severity, control failure and policy changes. Pre-approved protective restrictions may be enforced immediately; they do not grant new authority.
5. Hand the approved decision to the external policy/control-plane owner. Require enforcement receipts and negative tests before activation: revoked/expired grants, alternate tool paths, children, conflicting policies and controller failure. Keep credentials, grant issuance and ceilings beyond agent modification. Readiness/eval passage is an input, not permission.
6. Publish independently attributable approval, revision, expiry, review date, revocation owner, in-flight cancellation behavior and restoration criteria. SRE enforces the limits and returns evidence; restoration after suspension/revocation requires a new authorized decision. If authority cannot be proven at runtime, use the existing human-approved default.

Use `templates/earned-autonomy-decision.md` from the skill root. Operational evidence comes from site-reliability-engineering; evaluation design from agent-evals-and-observability; the authorized runtime plan from agent-production-operations. These documents do not implement their described controller.

Material changes to component revision, effective tools, credentials, data destinations, roots,
model, delegation or enforcement invalidate affected evidence until reviewed. Trace admission
records to consuming grants; hold expansion and use pre-approved protective restrictions for
unsafe existing scope. An unrelated grant may continue only with evidence that its boundary
remains valid. Record counterevidence explicitly, including missing or stale observations.
Complete with a scoped decision, owner, expiry, evidence links and enforcement handoff; if
required evidence is absent, deliver a bounded hold/restriction and name what would resolve it.
