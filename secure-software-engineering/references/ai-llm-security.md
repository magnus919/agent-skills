# AI And LLM Security

## Make The Decision Now

Define the AI system's boundaries before choosing prompts or models: who may invoke it, which data it may retrieve, which tools it may propose or invoke, what outputs can cause material effects, and where a human approval is required. The OWASP LLM release tag `2024`, titled `2025`, and MITRE ATLAS help elicit risks; neither is exhaustive.

## Treat The System As A Set Of Boundaries

- Treat user prompts, documents, retrieval results, model output, tool output, and external content as untrusted. Prompt instructions do not authorize access or execution.
- Enforce tool authorization server-side for every action with the requesting user, tenant, resource, purpose, and capability. Use narrow schemas, least privilege, rate and spend limits, and bounded data access.
- Require explicit human confirmation for material, irreversible, external, or high-impact actions unless a documented policy and risk acceptance justifies automation.
- Keep retrieval scoped to authorized data. Verify ingestion provenance, access labels, update behavior, and response citations where they affect decisions.
- Validate outputs before rendering, storing, sending, or executing them. Apply ordinary input/output controls to generated text, structured arguments, code, URLs, and files.
- Version and evaluate model, system policy, prompt templates, retrieval, tools, and guardrails. Log decisions and tool outcomes without retaining more prompt or customer data than needed.

## Evidence And Verification

Test prompt injection attempts, poisoned or irrelevant retrieval, cross-tenant retrieval, tool parameter manipulation, unauthorized tool calls, unsafe output contexts, approval bypass, rate exhaustion, and model or provider failure. Map relevant observed techniques to ATLAS when it improves communication, while recording the actual system-specific preconditions and mitigations.

## Misuse To Avoid

- Using a prompt as an access-control boundary.
- Giving a general-purpose agent broad credentials and trusting it to self-limit.
- Treating a model provider's safety claim, an evaluation score, or an LLM risk list as proof of safe deployment.

See [authentication-authorization.md](authentication-authorization.md), [input-validation-data-handling.md](input-validation-data-handling.md), [secure-logging-audit.md](secure-logging-audit.md), [dependency-supply-chain.md](dependency-supply-chain.md), [release-evidence.md](release-evidence.md), and [secure-code-review.md](secure-code-review.md) for the corresponding controls.
