# API Skill Enrichment: Agent Consumer Interfaces

**Review date:** 2026-10-04
**Scope:** `api-design-and-evolution` only.
**Status:** Methodology guidance and one synthetic output-quality case; no observed
agent performance claim.

## Gap and Change

The existing API skill handled API consumers, schemas, errors, pagination, lifecycle,
and compatibility well. Its workflow did not make an agent or automation's end-to-end
task path an explicit review object. That left several distinct questions implicit:
how the consumer discovers an operation, where its prerequisites and IDs come from,
whether one service's output can feed another, how to recover from specific tool
errors, how large outputs and artifacts are fetched, and how to distinguish accepted
work from completion.

This change adds a focused methodology reference and review template, routes from the
skill entrypoint and human README, and one eval case, `agent-consumer-interface-review`.
The scope remains API/interface design. It does not prescribe a gateway, MCP, a
search layer, or a single combined tool. Its key constraint is to test the intended
client because protocol support alone does not establish what the host exposes.

## Hypothesis

For a representative cross-service task, explicitly reviewing operation purpose and
discovery, identifier scope and prerequisites, actionable failure recovery, bounded
result/artifact retrieval, and safe composition may surface integration failures
that an endpoint/schema-only review misses. Discovery complexity should remain
proportional to the actual catalog and deployed client's behavior; small static
interfaces remain valid.

This is an unvalidated hypothesis. The talk “Dashboards Are Dead”
by Sarah Simionescu / Composio (user-provided
[video](https://www.youtube.com/watch?v=YiFqcu9YA38)) prompted the question of
agent-facing task completion. The video's demo is a mockup and its comparisons are
early and unreleased. No comparative result, superiority claim,
or claim that dashboards are obsolete is used as evidence here. Vendor-authored
guidance is likewise design input, not independent validation.

## Source and Claim Map

All live documentation below was checked 2026-10-04. Stable protocol semantics are
separated from platform-specific examples and vendor-reported results.

| Claim used in the guidance | Evidence and limit | Where applied |
|---|---|---|
| MCP distinguishes model-controlled tools from application-controlled resources; tool/resource lists are paginated, resources are URI-read, and clients choose how resources are presented. | [MCP Tools, 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/tools); [MCP Resources, 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/resources). Resource links in tool results are not guaranteed to appear in `resources/list`; listing/read mechanics do not guarantee cursor durability, snapshot consistency, cross-service authorization, artifact lifecycle, or task completeness. | Avoid assuming a returned link is discoverable/fetchable; require explicit contract guarantees and client/server integration evidence for durability, completeness, and access. |
| MCP differentiates protocol errors from execution errors; execution errors can expose actionable correction context, while clients should pass them to the model. Tool annotations are untrusted unless the server is trusted. | [MCP Tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools), error and security sections. This specifies protocol guidance, not business error taxonomy. | Preserve protocol/operation failure distinction and safe recovery; separately define domain-specific errors and authorization. |
| OpenAI function tools use task names/descriptions and JSON Schema; strict mode has schema constraints and is API-specific. | [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling). Do not generalize the strict-mode rules to other platforms. | Mention machine-readable contracts as useful for parseability, not proof of correctness. |
| Search/deferred loading can load a subset of a larger tool set, with explicit availability constraints in the current API. | [OpenAI Tool Search](https://developers.openai.com/api/docs/guides/tools-tool-search). It is a particular provider/model mechanism, not an architecture mandate. | State static lists and ordinary API docs are appropriate when sufficient; gate dynamic discovery on measured need and client support. |
| Code execution can reduce repeated intermediate context and compose data processing. | [Anthropic, Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp); [OpenAI Code Interpreter](https://developers.openai.com/api/docs/guides/tools-code-interpreter). Both are provider-specific implementation examples; sandbox configuration, access, and limits vary. | Keep composition a design choice (code, workflow, or agent planning); do not prescribe code execution. |
| Clear purpose, descriptive parameters, scoped tools, concise outputs, actionable validation feedback, and realistic evaluations are plausible design practices. | [Anthropic, Writing Effective Tools for AI Agents](https://www.anthropic.com/engineering/writing-tools-for-agents), published 2025-09-11; provider-reported experience, not independent general proof. | Inform the checklist while requiring real traces and baseline comparisons before claiming uplift. |

## Frozen Eval Rubric and Challenge Examples

The case is synthetic output-quality guidance, not a behavioral run. Its stable ID is
`agent-consumer-interface-review`. The rubric below states the observable evidence
needed for each assertion and three challenge snippets: a satisfying response, a
contradictory near miss, and an omission. Equivalent wording is acceptable when the
same fact is explicit. “Not shown” must not be treated as a pass.

| Assertion (verbatim) | Satisfying example | Contradictory near miss | Omitted-evidence example |
|---|---|---|---|
| The review traces the close task across Billing and ERP operations and names the owner and authority boundary for each | “Billing owns invoice search under tenant billing-read; ERP owns payment lookup under finance-ledger-read.” | “A central gateway owns both services and all finance authority.” | “Search and match invoices/payments.” |
| The review identifies prerequisite dependencies between operations in the close task | “Search returns invoice IDs; match each ID through the documented Billing-to-ERP mapping before ERP lookup.” | “Send the Billing invoice ID directly as the ERP payment ID.” | “Call Billing, then ERP.” |
| The discovery approach is justified against the catalog size and target client's actual capability without requiring dynamic tool search as a universal pattern | “With 30 and 8 operations, documented names/tags may suffice if the client can inspect them; verify discoverability in that client before adding search.” | “Every interface must use dynamic semantic tool search.” | “Improve discoverability.” |
| The review distinguishes tenant-scoped Billing invoice identifiers from ERP payment identifiers and requires an explicit supported mapping before cross-service use | “Invoice ID is tenant-scoped; ERP payment ID is a separate namespace, so resolve via the supported mapping.” | “IDs are opaque, so the same ID can be reused across both APIs.” | “Use stable IDs.” |
| The error contract distinguishes invalid date input from denied payment access and gives a safe, corrective next step without exposing sensitive details | “For invalid date, say the accepted format/range; for denied payment access, report permission required and route to an authorized finance user without confirming record existence.” | “Return `not found` for both errors so the agent can retry random IDs.” | “Use consistent errors.” |
| The collection contract bounds default and maximum results and defines continuation and a signal that results are incomplete | “Default to 50, cap at 200, return `next_cursor`, and set `has_more` when additional matches remain.” | “Return every row; if too large, silently truncate.” | “Support pagination.” |
| The receipt result defines an authorized retrieval path and usable artifact metadata or lifecycle | “Return a scoped artifact reference, `application/pdf`, size limit, and expiry; retrieve it with the authorized receipt-read operation.” | “Return an undocumented signed URL that never expires.” | “Include receipt access.” |
| The close flow distinguishes acceptance from terminal completion | “A 202 response returns an operation ID and status lookup; only a terminal succeeded state means close completed.” | “Treat 202 as completed because the server accepted the request.” | “Support async work.” |
| The close flow preserves finance user approval before finalizing | “Prepare a summary for finance approval; invoke finalization only after approval.” | “Finalize automatically after the agent prepares the summary.” | “Keep a human involved.” |

The case prompt and assertion text are the versioned contract in
`api-design-and-evolution/evals/evals.json`. The table documents challenge behavior;
it is not a deterministic grader binding and has not been run against real task
outputs. Keep this rubric frozen for a comparable first baseline; change it only with
a stated failure hypothesis and a recorded revision.

## Validation Plan and Limits

1. Validate the eval manifest's schema/semantics and run the repository skill format
   checks for changed paths.
2. Have reviewers inspect every challenge triad for the distinguishability of met,
   not met, and not shown; revise assertions if a grader cannot observe the evidence.
3. For behavioral evidence, run the same representative close tasks against the
   current and revised guidance with the intended agent and client. Preserve tool
   traces, outputs, IDs passed between services, errors, result sizes, artifact
   retrievals, human approval point, success/failure, and latency/call count. Include
   invalid and unauthorized cases; check for unintended actions and false completion.
4. Use additional held-out tasks before claiming improvement. A synthetic prompt,
   reviewer opinion, protocol conformance result, generated schema, or vendor demo
   cannot establish task success in deployment.

Limitations: the provided scenario is constructed for discrimination; no Billing/ERP
API, host integration, agent trace, or customer task corpus was supplied. MCP feature
availability and provider APIs may evolve. Security, permissions, tenant isolation,
and approval enforcement require the applicable security and deployed-boundary
reviews; prose in this methodology cannot prove implementation behavior.
