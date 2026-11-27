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

For software-factory decision rights and meaningful human checkpoints, use `references/agentic-engineering-governance.md` and `templates/engineering-decision-rights.md` (paths relative to the skill root).

## Worked decision: a bounded maintenance merge class

This synthetic example fills the existing earned-autonomy decision record for
an export-fixture maintenance class. The service owner sets the ceiling. The
release authority owns approval, the repository control owner enforces it,
and the worker follows the resulting grant. A real decision would require
the corresponding evidence, approval and enforcement receipts.

| Mode | Capability, environment and action | Decision evidence and authority |
|---|---|---|
| Supervised execution | L2, disposable test environment, edit fixture and run checks under supervision | Observe representative successes and failure paths. Keep the maker and evidence roles distinguishable. |
| Verified queue | L3 within an approved branch and verification grant for this class | Workers run the permitted checks and hand over PRs. Human landing decisions remain reserved. Count all eligible opportunities, including holds, stale or wrong-target checks and escaped issues. |
| Scoped unattended landing | Proposed L3 grant M-17, allowlisted fixture-only changes in the example repository's default branch | Expand only after the owner accepts the predeclared evidence, the authority approves the class with an expiry, and the controller proves allow, deny, expiry, revocation and wrong-head behavior. Land only verified current candidates within the cap. Deployment, customer data, policy and entitlement changes remain separately governed. |

Example decision record M-17 revision 2 applies to the export-fixtures bot,
the allowlisted `fixtures/export/` paths, and the example repository's default
branch. Maximum unattended concurrency is one. Assume the supervised and
verified-queue grants remain active. The new unattended grant is HOLD because
proof of denial at expiry is incomplete. The release authority must review the
checker and controller receipts before setting an activation date and expiry.
In this example the service owner reviews evidence after the first observation
window and after material tool, repository, or policy changes. The controller
owner revokes the grant on a mandatory-check failure. A still-valid narrower
grant determines which verification may continue during the hold.

Before deciding expansion, compare opportunities in the same work class,
including false-ready results, missed escalations, reviewer minutes, and
rework. Agree the evidence window, sample sufficiency and thresholds before
seeing the result. An expired grant or stale mandatory verifier holds the
affected class. Cancel or drain inflight jobs under the approved policy
and reconcile any landing or effect already in motion. Restore the approved
state or reduce to the still-valid supervised grant. Resuming unattended
landing requires an owner decision, current evidence and a verified control
receipt. A reverted commit may leave downloaded data or a sent message behind.
Reconcile that effect using its authorized owner, even after source recovery.

See the [loop example](../../harness-engineering/templates/loop-contract.md#example-fixture-maintenance-with-scoped-landing),
[sampling example](agentic-engineering-governance.md#sample-the-approved-work-class),
[decision audit](../../agent-evals-and-observability/references/decision-audit-record.md#example-reconstruct-a-held-landing)
and [operator handoff](../../verified-delivery/references/interruption-handoff.md#example-brief-an-operator-after-a-scoped-hold).
