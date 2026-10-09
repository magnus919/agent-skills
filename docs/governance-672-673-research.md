# Joint research spike: capability admission and earned authority

Date: 2026-10-09. Scope: [#672](https://github.com/magnus919/agent-skills/issues/672) and [#673](https://github.com/magnus919/agent-skills/issues/673). Repository baseline: `c545c2b61d4d1e22377bd5db240843a25c1b5764`.

## Recommendation

Resolve the useful requirements through one bounded improvement to `ai-governance`; do not create either proposed skill/bundle. The main work is clearer routing and a small admission/update record linked to the existing earned-autonomy decision. Preserve security review, evaluation design, and runtime enforcement in their current owners.

This is a moderate-depth desk research spike, not implementation or human-value validation. Sources and source-level claims are preserved in the [evidence log](governance-672-673-evidence.md). No capability was installed, executed, granted authority, or security-certified. No issues were changed during this spike.

## What is already present

| Proposed requirement | Existing artifact | Residual work |
|---|---|---|
| Capability × environment × action authority, owner, expiry, positive/negative evidence, promotion/demotion | [Earned-autonomy procedure](../ai-governance/references/earned-autonomy.md) and [decision template](../ai-governance/templates/earned-autonomy-decision.md) | Improve discovery; make initial grant explicit alongside maintain/expand/reduce/suspend/revoke; add links to admitted capability revisions. Do not invent another autonomy ladder. |
| Registry, identity, data scope, versions, owners, review dates, individual operations | [Agentic control plane](../ai-governance/references/llm-and-agent-security.md) and [review worksheet, sections 2–4](../ai-governance/templates/agentic-governance-review.md) | Add a compact component-level record, not a new registry platform. The issue's claimed absence of lifecycle ownership is overstated. |
| Provenance, dependencies, sandboxed first use, material-update diff | [Third-party skill vetting](../agent-skills/references/vetting-third-party-skills.md) | Route Skills-format packages here; do not duplicate the checklist or pretend it audits MCP/A2A automatically. |
| Third-party ownership, evidence, inventory, monitoring, exit | [Due-diligence template](../ai-governance/templates/third-party-due-diligence.md) and [procurement/lifecycle reference](../ai-governance/references/procurement-third-party-and-board-oversight.md) | Offer a lightweight route for individual capabilities; a full vendor questionnaire is disproportionate for many public-data skills. |
| Deployment version, tools/policies, staged rollout, rollback | [Runtime control plan](../agent-production-operations/references/runtime-control-plan.md) | Link to the reviewed capability/configuration and authority records. No new runtime method is needed. |
| Disablement, expiry, negative enforcement tests, restoration | Earned-autonomy procedure plus [agent production operations](../agent-production-operations/SKILL.md) | Explicitly identify affected consumers/grants when a shared capability changes or is disabled. |
| Evaluation freshness and contradictory evidence | Earned-autonomy procedure plus [agent-evals-and-observability](../agent-evals-and-observability/SKILL.md) | Store evidence references and validity conditions; avoid a second evaluator or automatic trust score. |
| Functional duplication and trigger collisions | Skill descriptions/format guidance plus case-specific review | Add an explicit overlap decision: reuse, restrict routing, replace, or retain both with a boundary. Security scans do not answer this question. |

`ai-governance/SKILL.md` already has an earned-autonomy paragraph, but its description does not explicitly advertise capability admission, MCP/A2A review, or permission promotion/revocation. Its reference/template tables also omit the earned-autonomy files. This is a concrete discoverability defect. The folded description is approximately 901 characters, so revise it within the 1,024-character limit rather than appending an unrestricted list.

## The two decisions should remain distinct

1. **Admission/update:** May this particular component and configuration be available in this environment, subject to which restrictions? Example outcomes: admit, admit with restrictions, hold, reject; later disable/retire or approve a reviewed update.
2. **Authority:** May this particular agent/principal use particular operations on particular resources now? Reuse the existing grant procedure, owner, evidence, expiry, and maintain/expand/reduce/suspend/revoke decisions.

Link the records using capability ID, reviewed revision/configuration, admission decision ID, and grant decision ID. Admission is necessary where policy requires it but does not itself authorize invocation. A grant for an old configuration does not silently extend to additional operations, destinations, data classes, or delegated agents.

This distinction is an architectural recommendation, not a new standards claim. NIST's comment synthesis identifies delegation/accountability and evolving agent authorization standards, while MCP and A2A leave important enforcement duties to implementations. See E1–E4 in the evidence log.

The efficient design is **one review session, linked decisions, reusable evidence**. Do not require two committees, duplicate facts across several forms, or re-request permission for each low-risk call already covered by a valid grant. Never let a convenience shortcut bypass applicable approval policy.

## Three capability walkthroughs

These are analyst-designed scenarios grounded in real artifacts, not observed enterprise admissions, security audits, or baseline/candidate model trials. Deployment assumptions are hypothetical. They test whether the proposed additions expose distinct questions; they do not satisfy either issue's human-value gate.

| Actual capability and hypothetical use | Decision-relevant observation | Existing baseline vs. useful addition |
|---|---|---|
| Repository `openlibrary` skill used for public book lookup | Its inspected client sends GET queries, permits server configuration, and can include an optional contact email in the User-Agent. Public data retrieval still sends query/context information outward. | Existing vetting and egress guidance already catches the boundary. A short record can specify public queries only, permitted endpoint/configuration, no organizational secrets, and an internal owner. **No demonstrated new safety finding** from another bundle. |
| MCP reference filesystem server over a private project directory | Its documented directory scope may change dynamically through client roots; reads and writes are distinct available operations. A binary/version pin alone does not freeze effective data access. [Official README](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) | Existing tool registry and material-change guidance already applies. Add an explicit configuration/root snapshot, impacted consumers, and re-review trigger. Hypothetical disposition: restrict to named scope and permitted operations; hold expansion until enforcement evidence exists. This is not a claim of a server vulnerability. |
| Official GitHub MCP server for repository triage | Documentation permits individual-tool selection; read-only mode suppresses write tools. Lockdown mode filters some content but is explicitly not an authorization boundary. [Official README](https://github.com/github/github-mcp-server) | Existing authority rules already separate read, comment, and merge actions. The admission record links reviewed configuration to grants so a toolset change triggers review. Hypothetical promotion: bounded commenting only after representative evidence, approval and enforcement; no merge grant. Hypothetical demotion: suspend affected writes on an unreviewed scope change, with restoration by authorized review. No actual promotion evidence was supplied. |

The filesystem/GitHub behaviors are discoverable in their READMEs. This spike therefore **does not establish #673's claimed increment over normal documentation review**. The likely increment is reliably carrying those facts into owner, configuration, grant and disablement decisions. That must be tested with reviewers.

For an A2A agent, the same record must additionally ask about remote principal, advertised versus granted skills, downstream delegation, task lifetime and cancellation/containment evidence. A protocol/Agent Card declaration is not organizational approval. This type-specific mapping is based on A2A documentation, not a fourth real-deployment case. For ordinary libraries, route to dependency/security review; use agent governance only where the library adds a meaningful agent capability or authority boundary.

## Smallest implementation proposal

Keep the main change inside **one skill directory**. Suggested scope is seven core authored files, plus any generated catalog files affected by metadata changes:

1. **Edit `ai-governance/SKILL.md`:** concise natural-language triggers for “approve this agent to act,” “review this skill/MCP server/agent,” and “review an update or revoke access”; add both entry routes and missing earned-autonomy reference/template rows. Route ordinary skill authoring and vulnerability-only work to existing owners.
2. **Edit its README:** show those two user jobs and the resulting decisions in human language.
3. **Add `references/capability-admission-and-update.md`:** a short intake → compare → disposition → grant handoff → verify activation → revisit/disable procedure. Include a small type-specific table for Skills, MCP, A2A and ordinary dependencies. Refer to existing due diligence, vetting, evidence and runtime methods.
4. **Add `templates/capability-admission-record.md`:** identity/type/source/revision/configuration, purpose and overlap, owner/approver, operations and data/egress scope, evidence references/freshness/unknowns, disposition/restrictions/review date, affected consumers/grant IDs, update diff, disablement/rollback/retirement owner and receipt references. Optional vendor diligence by reference. No credentials or copied sensitive traces.
5. **Edit `references/earned-autonomy.md`:** admission-versus-grant distinction, initial grant path, and material changes invalidating affected evidence. Keep the existing ladder and decision rules.
6. **Edit `templates/earned-autonomy-decision.md`:** add admission/revision/configuration links and explicitly label counterevidence. Most required fields already exist.
7. **Update `evals/evals.json`:** preserve `earned-autonomy-decision`; add a small number of atomic, observable cases for admission/update and linked authority decisions.

Source citations should live in the new reference; update the existing source index if its indexing convention requires it. Avoid making a nominal file count an acceptance target.

Update the existing agentic-review worksheet only if needed to point to the lightweight record; do not copy its 287-line review into the new form. Do not modify several sibling skills merely for symmetrical links. Existing `ai-governance` routes already connect evaluation, SRE and production operations.

No workflow engine, scanner, new JSON schema, mandatory trust score, tool installer, new framework, or operational controller is justified by this spike. A Markdown record with stable IDs is sufficient until there is an identified machine consumer. If later automation consumes the record, define and test a versioned contract then.

## Acceptance and efficient validation

Validate discovery separately from output behavior. Trigger probes should include capability admission, MCP permission change and earned authority, plus near misses for skill authoring, operating a specific tool, and ordinary dependency scanning. A description change alone is not evidence of improved routing.

Behavioral cases should cover:

- Unknown provenance produces hold/explicit missing evidence, not fabricated trust.
- A public read query carrying confidential context is recognized as egress.
- A version-stable configuration/tool-list change triggers review of affected grants.
- A passing scan or recent success cannot authorize additional actions.
- Valid representative evidence supports a bounded promotion recommendation with human approval and enforcement prerequisites.
- Stale evidence, revoked approval or compromised update leads to an appropriate restriction and an explicit restoration path.
- Trigger duplication yields a reuse/routing decision rather than automatic installation.

Combine scenarios only where the underlying case remains realistic; keep independently checkable assertions separate. For revised assertions, retain satisfying, contradictory and missing-evidence examples. Model-only semantic judgments remain advisory. Run repository format, eval schema, coverage ratchet and generated catalog checks appropriate to the changed files; do not write executable scripts or tests just to validate prose.

For human value, compare the **current composed baseline** (ai-governance plus its actual routed specialists) against the candidate on the three capability types, including two authority decisions: scoped expansion and restriction/suspension. Use identical evidence per pair, record omissions, false alarms, disposition differences, reviewer corrections and time to a decision the owner can explain. Counterbalance review order or otherwise document learning effects. Keep at least one case unused during drafting.

If baseline and candidate reach the same sound decision, that is not a safety improvement; retain a change only for demonstrated usability, traceability or maintenance benefit. This spike establishes none of those comparative outcomes yet. A test scaffold or synthetic scenario does not complete the original issues' validation gates.

## Proposed issue resolution

- **#672:** supersede the new-bundle deliverable with governance routing, explicit grant linkage and focused examples/evals. Close as completed only if the issue is explicitly rescoped and its revised acceptance criteria are met; otherwise close the bundle proposal as not planned with a follow-up link.
- **#673:** rescope to capability admission/update within `ai-governance`, preserving the three contrasting review cases. Ongoing runtime disablement remains in production operations; governance records the decision, ownership and affected grants.
- Use one joint implementation PR after that scope decision. Do not mark either issue complete just because much of its desired content already exists, and do not claim measured value until comparison evidence exists.

## Confidence, limits and preservation

High confidence: repository overlap, existing owners and observed discovery omissions. Moderate confidence: the proposed small record is a sensible integration point. Unknown: whether it improves actual reviewer decisions/time or warrants all proposed fields.

Open questions: which internal role signs admission for each deployment; whether the current host can expose configuration and grant identifiers reliably; what safe restrictions are enforceable on remote capabilities; whether reviewers prefer extending an existing worksheet to a separate lightweight record. These do not require a new top-level skill to investigate.

Durable artifacts: this report preserves the recommendation, coverage map, scenarios and acceptance plan; the linked evidence log preserves dated sources, claims, exclusions and limitations. These research artifacts describe the spike findings; the subsequent implementation and its validation boundaries are recorded in [the validation note](governance-672-673-validation.md). Recheck moving upstream docs and pin the actual capability versions before any real admission.
