# Product design and UX: external-agent interaction enrichment

## Gap and hypothesis

**Gap observed (2026-10-04):** `product-design-and-ux` already addresses generic AI control, authorization boundaries, tool side effects, human escalation, interruption, and recovery. Its task-flow guidance also follows work across roles. It did not explicitly route or give a reusable contract for the particular journey where a person delegates from their own agent app outside the product, an integration acts on product data, and the person returns to inspect or intervene. That left identity attribution, the authority relationship between a human request and product authorization, cross-app evidence continuity, and cancellation semantics implicit.

**Hypothesis:** a narrow reference plus a fillable cross-app handoff contract will prompt designers to trace the full user outcome and distinguish human, agent-host, integration, and product identities; to require product-side evidence for completion; and to specify human intervention and recovery without assuming the product owns or observes the external agent. It should supplement, not repeat, generic AI uncertainty and side-effect guidance.

**Scope:** `product-design-and-ux` only, plus this review note. No protocol implementation, security architecture, model evaluation, or dashboard replacement recommendation is proposed.

## Source check and claim mapping

Primary sources were checked on 2026-10-04. The specifications and guidebooks are evidence for their stated protocol or design scope; the UX recommendations below are synthesis, not new protocol requirements.

| Source and checked status | Supported claim | Design field / wording informed | Limit |
|---|---|---|---|
| [Microsoft HAX Toolkit](https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/) (maintained official toolkit; describes 18 research-synthesized guidelines) | Human-AI interaction guidance is organized around initial engagement, during interaction, when wrong, and over time. | Inspectable control, correction, dismissal, intervention, and recovery should be considered across the journey. | The toolkit does not directly validate this specific cross-app pattern or require every guideline in every product. |
| [Google People + AI Guidebook, Feedback + Control](https://pair.withgoogle.com/guidebook-v2/chapter/feedback-controls/) (official rolling design guide) | It discusses control, opt-out, user attention, and aligning promised feedback effects/timing with actual behavior. | Preserve human control, explain scope of delegated actions, and consider app switching and attention. | This source concerns AI product design generally; it is not evidence of outcomes for this product. |
| [MCP Authorization, 2026-07-28 specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) | MCP authorization is target-resource-specific and has protocol-defined validation rules. | Ask what product resource and principal are actually authenticated; do not equate a user request with product authorization. | MCP-specific. It does not establish that the product or a named agent supports MCP, or how identity mapping works. |
| [MCP Tools, 2026-07-28 specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) | Tools expose descriptions and input/output contracts; results and errors have protocol semantics; tool annotations are untrusted unless from trusted servers. | Define supported actions and observable evidence, and avoid treating tool metadata/call text as proof of safe authorization or a usable human interface. | Protocol contracts are not a UX guarantee or proof of product side effects. |
| [MCP Tasks Extension](https://tasks.extensions.modelcontextprotocol.io/) (official extension documentation) | Task states can include working, input_required, completed, failed, and cancelled; cancellation is cooperative and may not be honored. | Model cancellation request separately from confirmed stop; define race behavior, partial effects, and product-side reconciliation. | Only applies if the product uses this extension; do not imply its status semantics exist elsewhere. |
| Sarah Simionescu, [“Dashboards Are Dead” (Composio)](https://www.youtube.com/watch?v=YiFqcu9YA38) (user-supplied; title/link checked 2026-10-04) | Used only as orientation for examining agent-mediated interaction as a design question. | Scope the investigation to agent app ↔ product transitions. | The talk is not cited as evidence that dashboards are obsolete, agent interaction is preferred, or a pattern has proven value. Its argument was not used to set a design requirement. |

The existing sources already support keeping users in control, defining authorization boundaries, planning interruption, and verifying task completion. The delta is the explicit external-app route, separate principal mapping, and continuity of product evidence when no single interface owns the whole journey.

## Change plan

1. Route users of the skill to a focused reference and contract template only when a human delegates through an external agent surface.
2. Keep the human as goal owner and decision-maker; represent the agent, host/client, product account, and integration principal as distinct identities where evidence permits. Do not anthropomorphize the agent or assign it human accountability.
3. Require evidence for the product integration path and the product-side state; label unknown identity, permission, status, and cancellation behavior as an open decision.
4. Trace return, inspectability, human intervention, interruption, revocation, partial results, duplicate-effect risk, retry, and re-entry across the surfaces actually available.
5. Add one output-quality eval while preserving every existing case ID. Keep assertions individually reviewable and prose-based; no new grader prefix or gate is implied.

## Frozen behavioral case and challenge examples

Case: `external-agent-cross-app-delegation` in `product-design-and-ux/evals/evals.json`. Prompt and rubric are frozen for this candidate comparison; do not tune wording to fit one generated answer. These examples are synthetic response fragments showing the evidence required for a manual reviewer to distinguish met, not met, and not shown. They are not empirical performance results.

| Assertion focus | Satisfying response fragment | Contradictory near miss | Omitted-evidence response |
|---|---|---|---|
| Human and integration identities | “Maya is the goal owner. Verify the product account and separately identify which integration principal is authenticated; the agent-app request alone does not establish that mapping.” | “The agent is the customer, so attribute the update to the agent.” | “Maya asks her agent to update records.” |
| Unknown facts | “Account mapping and whether cancellation stops in-flight work are not specified; verify both before promising the flow.” | “The agent app automatically uses the customer’s permissions and cancel always stops it.” | “Check authentication and cancellation.” |
| Authority scope and boundary | “List records A–C and the allowed field changes; product authorization must cover this integration and a fresh confirmation is required if target or payload changes.” | “Grant the agent full workspace access so it can finish.” | “Ask the user to approve the update.” |
| Product-side outcome evidence | “On return, compare the three records in product state and show which saved, with timestamps and a link to inspect each.” | “Show the agent’s ‘done’ message as proof the records changed.” | “Show a completion status.” |
| Human intervention | “Let the person review/edit the proposed changes and use supported pause/revoke controls; if the product exposes no cancel endpoint, disclose that and link to manual support/reconciliation.” | “After the agent starts, the user cannot intervene or use the product manually.” | “Users can manage the task.” |
| Cancellation semantics | “Cancel requests no further work; state remains ‘stop requested’ until confirmed, and already saved changes remain listed for reconciliation.” | “Mark cancelled as soon as the client closes the agent window.” | “Include a cancel button.” |
| Partial result and re-entry | “Report two confirmed updates and one unknown; require product-state reconciliation before retry to avoid duplicate notifications; save a task reference so re-entry after a disconnect resumes from confirmed state.” | “Retry the whole batch after reconnect, regardless of which records changed.” | “Support errors and retries.” |

The satisfying fragment provides the distinct observable detail named by the assertion. The contradictory fragment proposes an incompatible behavior or unsupported inference. The omitted fragment uses related terminology but does not show whether the required property is met. A reviewer should choose **not shown**, not infer success from a keyword.

## Limitations and follow-up

- No real product, integration, target account, user research, or external-agent host was supplied. The handoff template deliberately marks those as evidence inputs rather than inventing a supported flow.
- No usability study or model run was performed. The new eval is a versioned prompt/rubric contract, not proof of behavioral uplift, real-world quality, grader performance, or release readiness.
- MCP is an example protocol boundary. Product and provider support, authenticated identity semantics, authorization scope, retention, cancellation, audit evidence, and recovery still require live verification for any implementation.
- The user-supplied talk informed the topic selection only; its title does not justify claims about dashboard usage or product direction.
