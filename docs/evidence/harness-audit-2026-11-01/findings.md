# Harness engineering audit — #767

**Recommendation: no additional harness methodology implementation for the
inspected scope.** Eight representative tasks have explicit current contract,
recovery, control and owner routes. Factory/contract tests passed without claiming
behavioral or release acceptance. Generalization of the director/factory patterns
outside their motivating examples remains unproved and is the next empirical
question, not evidence that another layer of guidance is needed.

## Pin, inventory, prior work

Source: `d284993fc6dc786d53496a3e9a7298de87292715`.
`execution.json` preserves every tracked skill-file hash, eight complete existing
case fixtures, exact test command/platform/stdout/stderr/exit. `protocol.md` bounds
the helper run before execution. All fixtures are authored, not observed user runs.

Reviewed the entrypoint, current scripts/tests, subsystem and catalog routing,
state/recovery, verification/experimentation, factory supervision, current protected
supervision and eval inventory. Source identity and structure are separate from
behavior; this is not a full new semantic run over every catalog case.

Prior completed scopes checked:

- [#656](https://github.com/magnus919/agent-skills/issues/656): tool-discovery
  prerequisites, bounded bulk artifacts and cross-service evidence continuity.
- [#717](https://github.com/magnus919/agent-skills/issues/717): factory assurance,
  dependency drift, protected terms, authority and meaningful oversight.
- [#727](https://github.com/magnus919/agent-skills/issues/727): sanitized lessons,
  reviewed patches and recurrence evidence rather than automatic policy promotion.
- [#749](https://github.com/magnus919/agent-skills/issues/749): recurring software
  production, director/worker roles, steering, host constraints and controlled evolution.
- Recent code-review work (#750–#754 in current history) owns change review and
  evidence-backed verdicts; the harness should route there rather than recreate it.
- Catalog discoverability #755 and protected supervision #759 already have merged
  artifacts. Neither requires another harness or supervisor bundle.

## Representative task matrix

Rows are source/task inspection, not fresh generated responses or actual side
effects. The fixture prompts and source hash roster make the inspection repeatable.

| Case / failure | Existing mechanism and supported next action | Evidence limit |
|---|---|---|
| restart-recovery: ticket created before checkpoint | context-and-state side-effect recovery: query authoritative operation/resource state, reconcile existing effect, persist ID/evidence before completion pointer | No real ticket or process-death recovery executed; in-memory checkpoint cannot prove durability |
| false-verification: text contains def test but pytest collects none | Verification workflow requires actual behavioral boundary; no tests/stub/exit-zero placeholder can authorize completion | Declaration truth or a string hit is insufficient; actual test collection/results are required |
| context-overload: 1,400-line instruction file and all docs loaded | Progressive context selection, source ownership, measured stage/context budget and one bounded intervention | No real retrieval/compaction comparison was run; shorter instructions alone are not quality improvement |
| tool-discovery-dependency-order: 420 tools with hidden prerequisites | Tool discovery reference records session/workspace prerequisites, affordances, status/errors and smallest appropriate tool set | No actual integration authentication or live tool execution; schema availability alone is not readiness |
| factory-supervisor-dependency-drift: v2 source, stale artifacts, expired lease, exhausted repair budget | Factory snapshot/reconciliation marks transitive impact, artifact version, acknowledgement, lease and budget dispositions; preserve unaffected candidate | CLI screens declarations only. Runtime fencing and effect reconciliation still need authoritative integration evidence |
| factory-role-and-host-boundary: host cannot interrupt workers or stay responsive | Role/host contract records actual capabilities and bounded synchronous fallback; do not promise an always-available director unsupported by host | No host adapter was operated; design cannot manufacture interrupt/resume capability |
| parallel-descendant-budget: concurrent reservations exceed one parent budget | Shared ledger/reservation contract, attenuated current grants, atomic admission, retry and descendant charges included | No real concurrent runtime or payment was exercised; prompt budgets do not enforce shared limits |
| uncovered-child-launch: parent monitored, child has no receipt | Protected-supervision path blocks uncovered launch and requires independent child identity/scope coverage | No actual child launch or control mutation occurred; missing receipt cannot be replaced by parent reassurance |

The mechanisms already route model quality to evals, evaluated-agent production to
operations, application behavior to its engineering owner, process/staffing to
operational-design/economics, and authority to governance/security enforcement.
No repeated new harness-owned mechanism gap was demonstrated in this task set.

## Executed declaration checks

Existing `test_factory.py` and `test_contracts.py` completed **46 passed**, with
**66 subtests passed**, exit 0, in 0.26 seconds. Do not count subtests as another 66
independent user tasks. The result covers declared dependency impact, stale artifact
and acknowledgement/lease handling, canceled dependencies, budget exhaustion and
invalid values, shape/cycle rejection, no input mutation, current-revision evidence,
unknown/failed evidence refusal, and optional bounded intervention-event contracts.

Tests explicitly preserve `behavior: not_assessed` and release acceptance as
unassessed. A complete declaration can be structurally valid while evidence truth
is unknown. No actual worker dispatch, kill switch, service twin, permission denial,
remote transaction, browser, model effectiveness or field acceptance was verified.

## Scope answers and primary comparison

- Instructions/tools/environment/state/feedback failures have current routes and
  discriminating probes. Finding files absent is not causal attribution.
- Long-running resumption uses current artifacts/revisions, operation IDs, evidence
  invalidation, expiry/revocation and fencing. Source guidance is testable; it is not
  proof that a target runtime implements those mechanisms.
- Control integrity is covered by #759, not by a self-editable verifier or manager
  declaration. The controlled agent must not be its sole approver/evidence source.
- Director/worker patterns have motivating fixtures and host boundaries. No new
  cross-domain effectiveness comparison was performed here; claiming universal
  throughput or autonomy improvement would exceed the evidence.
- Context and tools remain measurable hypotheses. Do not add graph nodes, resets,
  memory stores, or hierarchy merely because the catalog can describe them.
- Trigger metadata already covers harness diagnosis, runtime design, cross-session
  drift, factory steering and bounded loops. Catalog routes improve navigation; no
  client activation or search-ranking measure was run in this audit.

Primary sources checked 2026-11-01:

- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) motivates initializer/worker continuity and evidence across sessions. Its observed setup is not a universal filesystem recipe or permission grant.
- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents) distinguishes composable workflows and agents and weighs complexity against cost/latency. The article flags its older tooling discussion; no current vendor SDK contract is inferred from it.

Current catalog guidance already preserves those limits and specialist ownership.
The comparison supplies rationale, not new model efficacy or deployment evidence.

## Rejected ideas and smallest next increment

Rejected as duplicate: another durable-state checklist, software-factory umbrella,
manager-agent hierarchy, bulk-artifact mechanism or lesson store. Rejected as
speculative: more context resets, automatic cheap-model allocation, self-modifying
supervision, or a new framework adapter without a failing real task. Rejected as
unsupported: treating test declarations, service-twin results or raw install growth
as successful real work, unique-user demand, runtime safety or product value.

**Smallest useful next increment: no methodology implementation now.** Select one
maintainer-approved recurring delivery task outside the factory's motivating
examples. Pin model/host/tools/authority/budgets, compare the current minimal harness
with the proposed intervention, exercise interruption and resume, and retain exact
end-to-end acceptance plus effect evidence. Expected value: determine whether the
remaining uncertainty is host/model/application/organization or harness method.
Effort: a bounded task and one matched comparison with owner-defined limits, not an
invented cost estimate or open-ended optimizer. Verification: actual trajectories,
current control receipts, full attempts/cost/interventions, held-out regressions,
resolved user outcome and explicit abstentions. A demonstrated repeated failure
should become a separately approved repair. These existing fixture passes alone
do not justify an expansion or behavioral improvement claim.
