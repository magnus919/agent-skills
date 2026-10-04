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

## Interpretation limits

The two added v1 eval cases are output-quality prompts for design advice. They do not run adapters, exercise external services, establish behavior on a production task distribution, or prove a performance uplift. Synthetic fixtures, a model-generated plan, or a vendor benchmark can screen a hypothesis but cannot establish integration success, real-user benefit, or a release gate. The plan prepared elsewhere for an old/candidate five-prompt Luna task-response screen should be interpreted only as a synthetic design-output screen; task-response generation does not test live tools or the downstream artifact lifecycle.

The generic skill comparison guidance remains the statistical foundation; this document adds mechanism-specific controls and adverse cases only. No change to Jev rubric, confidence threshold, gate contract, or grader machinery is proposed. A production claim would require matched real or faithful integration tasks, observed tool/service outcomes, explicit denominators and missingness, and costs/latency from their authoritative measurement sources.

