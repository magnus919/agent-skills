# Allocate models and effort in a factory

Load when a director chooses worker models or escalation tiers. Sources S8 and S10 motivate separating capability, concrete model and inference effort; no portable low/medium/high capability standard exists.

Record per role: required modalities, tools, context, structured-output support, reasoning/creative demands, risk, latency target, allowed providers/data boundary and evaluation population. Keep a provider-neutral capability request separate from the actual model ID/revision, effort setting and runtime mapping. Resolve against the host's currently supported options; missing capability means route/escalate, never silently downgrade.

Start with the smallest configuration that meets the role's measured acceptance boundary. Escalate on defined failures or unresolved difficulty within the original budget; cap attempts and retain failed outputs. High consequence can warrant stronger verification rather than merely a bigger maker model. Never treat model confidence or a tier label as permission or correctness.

Compare candidate mappings on identical tasks and versions, including tool calls, retries, integration, review and end-to-end acceptance. RouteLLM's response-routing results do not validate routing long-running tool-using workers. Route semantic evaluation to agent-evals-and-observability and full costs to ai-operating-economics. No cost saving is established by choosing a cheaper model on paper.

Use the model allocation fields in templates/factory-role.md. Host settings belong to the matching framework/tool skill. Test what happens when a requested model is unavailable, budget is exhausted, a fallback lacks a modality or an effort setting is unsupported. Record explicit fallback/stop behavior and data-egress constraints.
