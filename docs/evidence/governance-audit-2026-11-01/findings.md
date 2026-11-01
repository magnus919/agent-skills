# AI governance audit — #765

**Recommendation: no new skill expansion for the inspected scope.** Eight existing
representative tasks map to current owners, evidence records, gates and stop paths.
Both deterministic helper test modules passed. Protected-control integrity is
already covered by #759; duplicating it would obscure ownership. This does not
prove real governance effectiveness, legal applicability, live enforcement or
behavioral quality of generated outputs.

## Revision, corpus and prior art

Pinned source: `d284993fc6dc786d53496a3e9a7298de87292715`.
`execution.json` preserves all skill-file hashes, eight complete task fixtures,
exact test command, platform and raw test result. `protocol.md` records the bounded
helper execution and decision rule. Cases are authored reproducible fixtures,
not observed organizations or participant accounts.

Reviewed the entrypoint, README, reference/template inventory, risk/maturity helper
source and tests, regulatory currency flags, earned-autonomy and admission/update
contracts, engineering decision rights, protected registry, board-report and
third-party artifacts. No private commercial evidence was used or invented.

Completed issues checked live: [#485](https://github.com/magnus919/agent-skills/issues/485)
expanded the governance source basis; [#672](https://github.com/magnus919/agent-skills/issues/672)
scoped earned autonomy; [#673](https://github.com/magnus919/agent-skills/issues/673)
capability admission/update/retirement; [#721](https://github.com/magnus919/agent-skills/issues/721)
engineering decision rights. [#759](https://github.com/magnus919/agent-skills/issues/759)
landed independent protected-control ownership and incident classification. Their
current artifacts were reused as evidence of coverage, not proposed again.

## Task inspection outcomes

Rows are source/task inspection, not new model runs or human adjudication. Covered
means a concrete current artifact supplies the decision mechanism; it does not
mean that filling a template establishes a pass or permission.

| Case / decision | Current artifact and supported disposition | Evidence gap or limit |
|---|---|---|
| operating-model-design | Governance charter, operating-model reference, named roles/council/RACI and evidence ownership | Organization's actual authority and practices are not supplied; a proposed RACI cannot become an accepted delegation |
| use-case-risk-tiering | Intake and model-risk assessment, with deterministic helper as triage, then expert confirmation and controls | The helper's low/medium/high taxonomy is not a statutory legal classification or full risk assessment |
| six-level-governance-loop | Lifecycle and six-level references connect strategy, impact, implementation, acceptance, operations and learning | Six-Level Governance is the catalog's method, not a legal/ISO mandate or the separate earned-autonomy ladder |
| board-governance-reporting | Report identity/owner, evidence-backed summary, inventory/tiering, risks/incidents, third-party posture, exceptions and board decisions | The board summary needs underlying current records; it cannot manufacture management attestations, legal conclusions or source metrics |
| earned-autonomy-decision | Scoped grant table by capability/environment/action/resource, policy ceiling, counterevidence, independent approval, expiry/revocation and external activation receipt | Seven clean days do not justify L5 for every tool; no live grant or independent controller receipt was supplied |
| capability-configuration-update | Admission record pins both revision and effective configuration, affected grants, purpose/permissions, rollback and re-review | Unchanged MCP version does not approve expanded personnel roots; hold scope expansion pending real purpose/authorization/enforcement evidence |
| compromised-capability-update | Pre-approved containment, suspend/revoke affected grants, reconcile shared credentials/in-flight effects, retain evidence, verify restoration | Unproven read isolation is not a safe fallback; deleting the catalog entry does not prove old paths disabled |
| control-exception-not-self-approved | Protected registry separates propose/approve/deploy/modify/disable/restore, human scope/expiry/rollback/compensating controls and external evidence | Agent cannot be sole approver or evidence source. Delivery pressure is no exception; no actual control state was tested |

The retirement/update reference explicitly includes consumers, migration/fallback,
data/record retention, credential/grant revocation and completion receipts. That
closes the documented lifecycle route without claiming a real retirement occurred.
No repeated missing decision mechanism was demonstrated in these tasks.

## Executed helper evidence

Existing `test_governance_maturity.py` and `test_use_case_risk_tier.py` completed
**35 passed, 0 failed, 0 skipped**, exit 0, in 3.27 seconds on the recorded host.
Tests cover deterministic scoring/tiering, sensitivity and life/liberty overrides,
control lists, malformed/missing/range-invalid input, dry-run parity and CLI output.

These are the helpers' declared local algorithm/CLI contracts. A synthetic maturity
score is not observed organizational maturity; a valid tier is not legal eligibility;
controls listed are not controls installed or verified. No rubric, deployment,
policy, oracle or approval threshold was altered to improve results.

## Bounded regulatory currentness check

Checked 2026-11-01 against primary EU sources. The reference's flagged central
high-risk timing matches the Commission's current published timeline: Annex III
high-risk rules from 2 December 2027 and product-related Annex I rules from
2 August 2028, following entry into force of the Omnibus on 27 July 2026.
See [Commission policy page](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
and [Commission entry-into-force notice](https://digital-strategy.ec.europa.eu/en/news/ai-omnibus-enters-force).
The [amending regulation](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32026R1744)
is the primary legislative source for those amendments.

This verifies that specific timeline claim, not every regulatory sentence,
jurisdiction, exception, legal role or system's classification. US/UK/China and all
other obligations were not comprehensively reverified. Legal interpretation remains
with qualified legal authority/legal-strategy; governance records the resulting
control mapping. The reference's broad “authoritative on the current state” wording
must not override its own at-use verification caveats or the skill's legal boundary.
A legal sign-off or claim that all references are current would be unsupported.

## Coverage and remaining questions

- Intake/tier/lifecycle/board/third-party/admission/autonomy/retirement artifacts are
  present and route to accountable humans, rather than assigning decisions to agents.
- Decision rights include scope, expiry, activation, counterevidence and revocation;
  their actual implementability still needs a target system and independent tests.
- Security implementation remains with secure-software-engineering; runtime control
  deployment with agent-production-operations; evidence/graders with agent-evals;
  legal meaning with legal-strategy. The helper cannot erase those boundaries.
- Protected control integrity has an explicit registry, independent evidence and
  incident ownership from #759. No additional cross-skill control expansion is
  justified by this audit. The operations audit separately tracks contradictory
  runtime transition text; governance should supply the decision, not duplicate
  that repair here.
- Metadata already names governance programs, risk tiering, decision rights,
  lifecycle and board oversight; common admission/action questions have catalog
  routes. No live client activation was run, so no measured routing success or
  over-trigger rate is claimed.

## Rejected ideas and smallest next increment

Rejected: another earned-autonomy or admission bundle (duplicates #672/#673),
repeating #721/#759 protected rights, turning the triage score into a compliance or
release gate, importing competitor features without task failures, and treating
raw installs as unique-user demand or value. A blanket regulatory rewrite is not
justified by a timeline claim that matches current primary sources; unreviewed
jurisdictions remain an evidence gap, not confirmed-current.

**Smallest useful next increment: no methodology implementation now.** When a
maintainer has a real intake/authority/retirement or board decision, apply the
existing artifacts to authorized evidence and test where the handoff fails. Value:
resolve the remaining operational/behavioral uncertainty rather than add another
framework. Effort depends on the selected case and evidence access; no organization
or cost estimate is invented. Verification: exact source/configuration, accountable
human decision, independent activation/denial/expiry/revocation receipts, preserved
counterevidence and explicit unresolved obligations. Refresh only the jurisdictional
claims actually relied on at that decision, through qualified review. A demonstrated
repeated gap should become a separately approved follow-on.
