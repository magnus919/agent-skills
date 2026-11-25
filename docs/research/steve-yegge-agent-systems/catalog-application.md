# Applying the research to agent-skills

Catalog baseline is upstream main at [05ea46ac](https://github.com/magnus919/agent-skills/commit/05ea46acf7becf418645197f21d0461324af1e44), verified November 25, 2026. This is an impact assessment and proposed qualification plan. [Thesis](research-brief.md) · [Sources](sources.md)

## Priorities

| Priority | Existing owner and baseline | Increment worth adding | Observable acceptance case |
|---|---|---|---|
| **First · qualify rule retirement** | [Harness engineering’s knowledge and invariants](../../../harness-engineering/references/instructions-and-knowledge.md) already distinguishes proposals from policy, versions rules and tests both outcomes. [AI governance’s protected controls](../../../ai-governance/references/protected-controls.md) and [production operations’ control integrity](../../../agent-production-operations/references/control-integrity.md) own maintenance authority, control incidents and restore evidence. | Add a worked example of overfencing followed by unsafe removal. Show when to simplify a workflow rule, how to exercise a retired rule in a resumed run, and how to prove release freezes and authorization still hold. [S11](sources.md#s11) · [S12](sources.md#s12) · [S13](sources.md#s13) | Legitimate work proceeds after the owner retires a redundant rule. The frozen release stays blocked on direct, queued and resumed paths. Superseded policy remains available for audit and absent from active guidance. |
| **First · choose session lifetime by work shape** | [Coordination ownership and flow](../../../multi-agent-coordination/references/ownership-and-flow.md) already separates seat, run, claim and credential. [Harness context and state](../../../harness-engineering/references/context-and-state.md) separates state by authority. [Topology](../../../multi-agent-coordination/references/decomposition-and-topology.md) already challenges unnecessary decomposition. | Compare a sequential task, a persistent project seat and a fresh worker per independent case. Show a small startup packet with current remit, task, authoritative references, claims and stop conditions, plus authoritative revalidation for effects. [S12](sources.md#s12) · [S14](sources.md#s14) · [S15](sources.md#s15) · [S17](sources.md#s17) · [X03](sources.md#x03) | An interrupted workstream resumes under current authority and late effects from the former occupant are rejected. Facts from customer A never enter customer B’s case. A tightly sequential task routes to one harness. |
| **First · pilot one coordination-only role** | [Technical project management](../../../technical-project-management/references/control-and-communication.md) owns single-project control. [Technical program management](../../../technical-program-management/SKILL.md) owns shared decisions across projects. [Chief of staff methodology](../../../chief-of-staff-methodology/SKILL.md) supports executive decisions and sets a high bar for recording commitments. | Add a sponsor-owned example using approved project artifacts and a weekly dependency-and-decision digest. Attribute evidence, surface absent owners and contradictory status, leave drafts with the sponsor, and keep a narrow urgent escalation route. [S13](sources.md#s13) · [S17](sources.md#s17) | A read-only agent identifies an unresolved dependency from conflicting records, labels the unconfirmed owner and proposes the next decision. Existing owners retain commitments, communication and data-access decisions. |
| **Next · qualify autonomy per intent** | [Earned autonomy](../../../ai-governance/references/earned-autonomy.md) owns authority changes. [Evaluation design](../../../agent-evals-and-observability/references/evaluation-design.md) and [judge stability](../../../agent-evals-and-observability/references/judge-stability.md) own measurement. [Operational design](../../../operational-design/references/decision-workflow.md) owns process and exception pathways. | Use two look-alike case types with asymmetric errors. Tie model, effort, prompt, policy and evidence revision to each authorized action. Include a manual route, independently adjudicated labels, drift checks, explicit demotion and an intent-to-effect handoff. Reuse local autonomy vocabulary. [S14](sources.md#s14) · [S15](sources.md#s15) | Aggregate accuracy rises while rare escalation recall drops. That intent holds at shadow or returns to the human path while the qualified routine intent continues. A judge’s agreement alone cannot promote either intent. |
| **Next · measure attention and wake costs** | [PR #859](https://github.com/magnus919/agent-skills/pull/859) already covers backpressure, delayed release exposure, delegated intake and cost per accepted outcome. [AI operating economics](../../../ai-operating-economics/references/task-economics-example.md) compares routing and cadence against acceptance, quality and review capacity. [Release engineering](../../../release-engineering/references/progressive-delivery.md) owns cohort exposure. | Instrument a real comparison that includes idle wake-ups, startup revalidation, interruptions, support or reviewer minutes, and waiting. Use event-driven wake or parking where evidence supports it. Cover continuity, starvation and urgent exceptions. [S12](sources.md#s12) · [S13](sources.md#s13) · [S16](sources.md#s16) · [S17](sources.md#s17) | Lower inference spend alongside poorer acceptance or more human work is visible. A routine digest is deferred when capacity is full and a time-critical exception still reaches its owner. |

## How the patterns travel across the catalog

| Catalog family | Transfer guidance |
|---|---|
| Workflow architect and agent-skills | Package bounded procedures with versioned inputs, outputs and evidence requirements. Keep role assignment, policy, credentials and run state in the host systems. Add a shared abstraction after two materially different workflows demonstrate the same need. |
| Agent council, code review, verification methodology and verified delivery | Spend independent scrutiny where judgment or consequences justify it. Compare a second reviewer and repeated passes against targeted deterministic checks and a single reviewer. Bind evidence to the artifact and version. Preserve effective release approvals when generated changes become easy. |
| Research methodology, research and vault, artifact pyramids and managing editor | Parallelize independent source work where the corpus warrants it. Assign final evidence acceptance and contradictions to the synthesis owner. Publish a current reading path backed by source records and superseded interpretations. |
| Product operations and governance, product adoption, conditional customer success and release engineering | Route feedback as a proposal to a product owner. Hold exposure to cohort and support capacity. Monitor outcomes in that cohort and investigate blind spots such as inactive or first-time users. Give human-facing coordination an explicit cadence and escalation route. |
| Operational skills such as GitHub runner, Linear, Jira and Slack | Keep implementation details with the tool owner. Preserve the current system of record, enforce tool-side authority and verify consequential writes. Use the existing task-store interface when it can represent the required lifecycle. |

## Proposed experiments

### A. Replay control simplification before deploying it

- Freeze the policy revision, protected-control inventory, expected denials and admissible work. Build a small local replay or shadow fixture with the authorized policy owner. Represent missing, stale and duplicated evidence explicitly.
- Compare existing rules with a consolidated candidate. Include an ordinary work item, release freeze, stale authority on a resumed run, alternate executor path and queued work in flight. Record the check, its reason, the revision it read and the observed downstream effect.
- Set hard invariants before the run. Any unauthorized effect or missed mandatory control blocks the change. A lower false-block count is secondary. If rollout is authorized later, stage it with restore criteria and verify the active revision from outside the agent.

### B. Compare role continuity and case isolation

- Hold model, effort, tools, permissions and validator constant. For equivalent interrupted project cases, compare the existing restart packet, a compact seat packet with on-demand references, and full history where it is an authorized baseline. For independent cases compare fresh workers and a persistent session using the same source of record.
- Include a missing document, superseded policy, revoked grant, reassignment, contradictory predecessor note and a similarly named case belonging to another customer. Measure accepted results, time to first correct action, boot and total tokens, repeated reads, human minutes and unauthorized effects.
- Advance the compact packet if acceptance and authority checks pass and total effort improves. Keep case isolation if continuity causes leakage or stale decisions. Use a short sequential job as a negative control for unnecessary handoffs.

### C. Run one read-only coordination pilot

- Pick a sponsor with a concrete recurring decision or dependency problem. Use approved project and meeting records in one workstream. Define recipient, reviewer, cadence, permitted inputs and a baseline for decision latency, rework and attention.
- Produce a brief with the decision needed, documented options or dependency, verified status and source date, accountable owner if known, next review and material unknowns. Flag proposed work and unconfirmed assignments. Keep commitments and external communications with existing owners.
- Compare with the sponsor’s ordinary process on equivalent cases. Track decisions changed in time to act, false or missed dependency findings, reviewer and interruption minutes and cost per accepted brief. Record zero accepted briefs explicitly. Stop on leakage, an attempted unauthorized mutation or sustained reviewer burden without decision benefit.

### D. Shadow one repeatable case type

- Use a well-defined intent and a confusable neighbor. Split authorized historical cases into tuning and untouched evaluation sets. Have domain reviewers label independently and adjudicate disagreements. Include rare high-impact cases, uncertain labels and ambiguous routing.
- Pin model, effort, instructions, tools and policy. Compare quality, error severity, calibration, abstention, cost and timeliness against human handling. Require direct evidence for consequential boundaries. Track judge performance against independent labels.
- If the workflow later earns write authority, put current eligibility, operation identity, audit, reconciliation and recovery at the executor. Verify duplicate delivery, crash after effect, failed compensation, stale policy and independent demotion before allowing writes. A successful shadow run qualifies the shadow comparison.

## Maintenance and rollout

The first documentation increment can add one worked case and one adversarial eval per owner, preserving existing eval IDs and contracts. Keep the affected skills within the repository’s paired-eval selection cap. Challenge each new assertion with a satisfying answer, a contradictory near miss and a response that omits evidence. Retain independent release evidence.

Treat the reported 14 fences, 40% code-health allocation, five review passes, subscription setup, frontier model selections, megabatch merging and build-versus-buy stance as historical choices or hypotheses. A catalog rule needs a durable problem, a scoped owner and observable acceptance. Compare on real work against the simpler process already in service.

## Catalog implementation

The follow-up adds the four worked examples to
[harness rule maintenance](../../../harness-engineering/references/instructions-and-knowledge.md),
[coordination topology](../../../multi-agent-coordination/references/decomposition-and-topology.md),
[project control](../../../technical-project-management/references/control-and-communication.md)
and [operational design](../../../operational-design/references/decision-workflow.md).
The topology example includes reviewer effort, interruptions and idle wake cost.
Supporting skills are linked from the owning examples. The
[eval challenge cases](catalog-eval-challenges.md) document the author review.
The examples and evals qualify guidance and reasoning. The real-world pilot,
control replay on a deployed host and shadow trial remain proposed experiments.
