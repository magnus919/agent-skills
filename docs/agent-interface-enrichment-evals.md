# Agent Interface Enrichment Evaluation Design

**Prepared:** 2026-10-04
**Purpose:** Focused evaluation design for changes to tool discovery, bulk-result delivery, cross-service consumption, delegation, and recurrence across fresh sessions.

## Evidence and source-to-claim map

| Source | Checked | Source supports | It does not establish |
|---|---|---|---|
| Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), published 2026-01-09 | 2026-10-04 | Agent trials can vary; tasks, graders, and trajectories should be explicit; combine outcome and transcript evidence; use production monitoring and other evidence alongside offline evals. | A particular sample size, generic release threshold, or that this interface change improves a live system. |
| Anthropic, [Code execution with MCP: building more efficient AI agents](https://www.anthropic.com/engineering/code-execution-with-mcp), published 2025-11-04 | 2026-10-04 | Code execution and selective access to MCP tools/results are design mechanisms intended to reduce context use and improve efficiency. | That artifact or code-mediated transport is cheaper, faster, safer, or more successful for a different product. |
| Anthropic, [Introducing advanced tool use on the Claude Developer Platform](https://www.anthropic.com/engineering/advanced-tool-use), published 2025-11-24 | 2026-10-04 | On-demand tool search can reduce upfront definitions; it adds a search step, has tradeoffs, and may be useful for large libraries. It reports vendor-specific internal measurements. | That reported token or accuracy deltas transfer to another model, harness, task population, or deployment. They are hypotheses for local tests only. |

These sources are vendor primary material. Their product descriptions and internal measurements are not independent production evidence for this repository's target system. The evaluation protocol below is a proposed local method derived from the task requirements and general paired-eval practice; it is not a claim that a live integration was exercised.

## Comparison design

Pre-register a mechanism-specific failure hypothesis: for example, task-relevant discovery reduces irrelevant definitions without increasing missed prerequisites; artifact delivery lets an authorized downstream service consume bulk data while reducing context; or a fresh session can recover the correct prior result without leaking across identities. Record the predicted benefit, plausible harm, and what evidence would falsify the hypothesis.

Pair baseline and candidate on identical realistic tasks, model/runtime, tool and service versions, starting state, permissions, identity, resource limits, and result handling. Change discovery and artifact handling independently where possible. If both change together, include factorial/ablation comparisons or report the result only as a bundle. Preserve trials, trace/tool-call failures, timeouts, denials, missingness, and stochastic repeats. Do not compare a clean candidate run with a baseline that omits equivalent retries or recovery.

Use separate evidence for (1) task completion and end state, (2) discovery and prerequisite sequence, (3) artifact integrity/access and actual downstream consumption, and (4) recurring retrieval in a new session. Track task-level and slice outcomes, incorrect/unnecessary calls, context size, latency distribution, and total monetary plus orchestration/storage/transfer/cleanup costs when the measurement source supports them. Mark uninstrumented measures unavailable; tokens are not a proxy for total cost. Preserve safety and authorization failures as categorical adverse outcomes instead of averaging them into quality.

## Proposed behavioral cases

| Case | Passing evidence | Challenge / contradictory near miss |
|---|---|---|
| Task-relevant discovery | Agent discovers the needed tool and its prerequisite, then completes the task with authorized arguments. Trace and end state agree. | Similar tool names, irrelevant request, empty or ambiguous search, missing prerequisite, or permission-filtered result causes a wrong call or unsupported claim. |
| Bulk artifact delivery | A different authorized service or delegated agent retrieves and uses complete, provenance-bearing output; task outcome is verified. | Missing/expired pointer, wrong identity, access revocation, partial pagination, duplicate delivery, stale data, or incompatible consumer. Agent must report incomplete work and recover/escalate. |
| Fresh-session recurrence | New session finds the intended artifact from explicit durable identifiers and verifies identity, permission, freshness, completeness, and provenance before continuing. | Ambiguous/stale match, changed permission, identity mismatch, expired artifact, duplicate result, or hidden reliance on old session history. |
| Delegation | Downstream result returns with source identity, status, and completeness; requester verifies it before acting. | Denied or partially complete delegation, missing provenance, duplicate result, or silent loss at service boundary. |

For each semantic assertion, review a satisfying output, a contradictory near miss, and an output that omits evidence. Prose assertions remain `manual_review` under the current paired-eval grader; do not interpret `passed=true` or a Jev `met` suggestion as a semantic pass. A deterministic check can validate fixture structure, while service-level execution or human review is required to establish actual cross-service access and side effects.

## Assertion challenge examples

These snippets are challenge fixtures for the two new output-quality cases. “Met” means the proposed response contains the evidence criterion; “not met” gives a contradictory response; “not shown” omits the evidence. They test whether a reviewer can classify the design advice. They do not prove that any described execution occurred. Assertion text is abbreviated by stable case ID and leading phrase so the examples stay scannable.

| Case / assertion focus | Met example | Not met example | Not shown example |
|---|---|---|---|
| `agent-interface-discovery-ablation` — mechanism hypothesis / separation | “Hypothesis: JIT discovery reduces irrelevant definitions. Test artifact transport separately; if inseparable, use a 2×2 ablation.” | “Enable both together; any improvement proves both helped.” | “Compare before and after.” |
| Same — same tasks | “Replay each frozen task in baseline and candidate.” | “Run different tasks for each arm.” | “Use a task set.” |
| Same — model/runtime | “Pin the same model and runtime settings in both arms.” | “Use the newest model in candidate only.” | “Record the model.” |
| Same — tool/service versions | “Pin the same tool schemas and service builds in each pair.” | “Upgrade service schemas only in candidate.” | “Record versions.” |
| Same — identity/permissions | “Use the same principal and permission snapshot for both runs.” | “Give candidate broader access.” | “Record the account.” |
| Same — state/output handling | “Reset both arms to the same state and grade results through the same output path.” | “Candidate starts with cached artifacts and gets a different grader.” | “Keep setup similar.” |
| Same — task outcome/prerequisite evidence | “Check end state and trace that the required ID lookup preceded the dependent call.” | “Accept a final answer that names the right customer even though no ID was resolved.” | “Check success and prerequisites.” |
| Same — authorized cross-service consumer | “Require the receiving service's access log and verified output state under the authorized principal.” | “Treat the agent's statement ‘the other service used it’ as proof.” | “Check the artifact.” |
| Same — missing artifact | “A missing handle must produce an explicit incomplete result and recovery/escalation.” | “If the handle is missing, report the expected distribution anyway.” | “Consider artifact errors.” |
| Same — expired artifact | “Expire the handle mid-resume; require refresh/recovery or explicit failure.” | “Assume handles never expire.” | “Test resume.” |
| Same — partial result | “Drop a later page; require completeness detection before reporting totals.” | “Report page-one totals as the cohort total.” | “Check pagination.” |
| Same — duplicate delivery | “Duplicate one page; require deduplication or surfaced duplicate accounting.” | “Count repeated IDs twice without disclosure.” | “Check duplicates.” |
| Same — inaccessible artifact | “Deny the consumer; require no data claim and a surfaced access failure.” | “Use a different user's handle to bypass denial.” | “Test access.” |
| Same — permission change | “Revoke permission before retrieval; require denial to stop use and be reported.” | “Continue with cached authorization after revocation.” | “Check permissions.” |
| Same — context measurement | “Record measured input/context tokens per task; otherwise mark unavailable.” | “Infer token savings from shorter answers.” | “Discuss context.” |
| Same — latency measurement | “Report measured end-to-end latency distribution; otherwise mark unavailable.” | “Call it faster because fewer tools were loaded.” | “Mention speed.” |
| Same — monetary cost | “Use billing/usage records for cost; mark cost unavailable without them.” | “Convert token count directly into total cost without rates or services.” | “Mention cost.” |
| Same — orchestration/storage overhead | “Measure search, transfer, storage, and cleanup charges/usage where instrumented; mark gaps.” | “Ignore artifact storage and orchestration overhead.” | “Mention overhead.” |
| Same — evidence limits | “Treat vendor results as a hypothesis and synthetic plans as design evidence only.” | “Anthropic's benchmark proves this system will improve.” | “Cite a benchmark.” |
| `agent-interface-fresh-session-recurrence` — fresh session | “Start a new session with no prior transcript or hidden memory.” | “Resume in the original session with the handle already in context.” | “Repeat the task later.” |
| Same — intended identity | “Compare artifact owner, tenant, and requested task key before use.” | “Use the first artifact with a similar title.” | “Check artifact identity.” |
| Same — current authorization | “Verify access under the current principal immediately before retrieval.” | “Reuse the creator's permission after it was revoked.” | “Check access.” |
| Same — freshness | “Check artifact timestamp/version against the task's freshness requirement.” | “Use a stale export as current.” | “Check whether it is recent.” |
| Same — completeness | “Verify all expected pages/IDs are present before continuing.” | “Treat page one as a complete export.” | “Check completeness.” |
| Same — provenance | “Verify source service, query/run ID, and transformation lineage.” | “Accept an artifact with no source or run metadata.” | “Check provenance.” |
| Same — ambiguous recurrence | “Two matching artifacts trigger clarification or disambiguation by stable ID.” | “Select either matching artifact silently.” | “Test ambiguity.” |
| Same — stale recurrence | “A stale artifact is rejected or refreshed before use.” | “Use the stale artifact without noting age.” | “Test staleness.” |
| Same — duplicate result | “Duplicate delivery is detected and does not double-count.” | “Count a repeated result twice.” | “Test repeats.” |
| Same — partial recurrence | “A partial result is labeled incomplete and the missing portion is recovered or escalated.” | “Present the partial result as complete.” | “Test partial results.” |
| Same — inaccessible recurrence | “A permission denial is surfaced; no alternate identity is used to bypass it.” | “Fetch using another tenant's credentials.” | “Test accessibility.” |
| Same — identity mismatch | “A tenant/owner mismatch blocks retrieval and is recorded.” | “Continue across the identity mismatch.” | “Check identity.” |
| Same — observable downstream consumption | “Require downstream service audit evidence and a verified resulting state.” | “The agent says it was consumed, so count success.” | “Verify consumption.” |
| Same — incomplete/denied recovery | “Surface denial or incompleteness, retry only within policy, then escalate if unresolved.” | “Claim completion after a denied or partial read.” | “Describe recovery.” |
| Same — equivalent paired trials | “Pair fresh-session cases with the same task, config, identity, and permissions.” | “Change task and access level between arms.” | “Compare both versions.” |
| Same — evidence-bounded conclusion | “Conclude only that the synthetic design response specifies checks; live behavior remains untested.” | “The written plan proves production recurrence works.” | “State a conclusion.” |

Use each row as three candidate response fragments: a complete response that includes the met fragment, one containing the contradictory fragment, and one that omits the criterion. If a generated answer mixes evidence, contradiction, and omission, label that assertion unresolved for human review rather than force-fitting a verdict. A response fragment cannot stand in for the service/environment artifact named by its own proposed evidence criterion.

## Interpretation limits

The two added v1 eval cases are output-quality prompts for design advice. They do not run adapters, exercise external services, establish behavior on a production task distribution, or prove a performance uplift. The separately frozen five-prompt Luna screen gives old and candidate skills identical design tasks, output budget, and available skill resources, with no internet or external mutation. It captures responses and available run data for advisory model review. This is a synthetic test of whether guidance changes task responses; it does not test live tools or the downstream artifact lifecycle. Its findings cannot establish integration success, real-user benefit, or a release gate. Model verdicts are not human labels or calibrated accuracy. Synthetic fixtures, a model-generated plan, and vendor benchmarks can screen hypotheses only.

The frozen prompts make several concrete challenge families available for later execution evals: discovery with 240 tools, invalid identifiers, stale search and denied capabilities; 80,000 paginated cohort IDs, cross-app identity mapping, duplicates, and handle expiry; an ambiguous customer and an export timeout after effect; and delegated work interrupted by authorization revocation after one service has acted. These are proposed behavioral cases, not observed failures or results. Execute them against actual integrations before making claims about completion, recovery, or uplift.

The generic skill comparison guidance remains the statistical foundation; this document adds mechanism-specific controls and adverse cases only. No change to Jev rubric, confidence threshold, gate contract, or grader machinery is proposed. A production claim would require matched real or faithful integration tasks, observed tool/service outcomes, explicit denominators and missingness, and costs/latency from their authoritative measurement sources.
