# Digital Twin: governance and authority

## Govern the twin as a control system

Register every twin, model, connector, agent, policy, and executable capability with represented original, intended decisions, owner, authoritative sources, update contract, limitations, evaluation evidence, data classification, retention, allowed actions, blast radius, stop authority, dependencies, and retirement plan.

Keep local authority with domain owners. Use a federated catalog for discovery and compatibility. Platform operators own synchronization and availability; data owners own collection/access; model and agent owners own validity and behavior; security/privacy owners own trust boundaries; named humans accept consequential residual risk.

## Capability separation

| Capability | Default | Required control |
|---|---|---|
| Observe/query | Allowed within purpose/data scope | Identity, least privilege, freshness and provenance |
| Infer/simulate | Approved domain only | Pinned inputs/model, uncertainty, reproducible trace |
| Recommend | After evaluation gate | Evidence packet, alternatives, abstention |
| Approve | Not an agent power for consequential changes | Named human or independent policy authority |
| Execute reversible low-impact action | Earned, bounded grant | Policy gateway, scoped credentials, idempotency, rollback |
| Execute high-impact action | Human-approved exception or prohibited | Preview, independent validation, close-to-execution approval |
| Stop/quarantine/rollback | Pre-authorized safety path | Fail-safe design and audit trail |

Confidence is not authority. Approval expires when material inputs, code, model, environment, or policy changes. Human oversight must include the exact proposed action, affected systems, state age, validity domain, evidence, uncertainty, alternatives, expected blast radius, policy result, and tested rollback.

## Earned autonomy

Promote per action class and environment:

1. read-only inventory and explanation;
2. isolated simulation;
3. shadow recommendation while humans act independently;
4. immediate human-approved execution;
5. bounded, reversible, low-blast-radius autonomy;
6. expanded autonomy after sustained normal, boundary, adversarial, incident-replay, and recovery evidence.

Demote automatically on integrity loss, expired evidence, drift, authorization bypass, critical incident, exhausted error budget, missing telemetry, or ownership loss. Reinstatement requires a new gate.

## Security

Use unique human/workload identities, short-lived scoped credentials, downstream authorization, signed/hashed events and artifacts, schema/sequence/timestamp/replay checks, tenant and environment isolation, denied-by-default execution/egress, supply-chain inventory, bounded retries/concurrency/cost, and independent action-result reconciliation. Treat repositories, agent messages, memory, models, plugins, and linked twins as separate trust domains.

NISTIR 8356 specifically calls out massive instrumentation, centralized measurements, manipulated representations, remote control, linked-twin propagation, integrity/authenticity, encryption, MFA, data governance, organizational authorization, fault tolerance, and zero-trust planning.

## Privacy

The twin may concentrate source code, secrets, vulnerabilities, employee signals, communications, prompts, tool payloads, and customer data. Record purpose, classification, owner, consumers, residency, retention, and deletion for each field/trace. Prefer structured decision metadata, hashes, and redacted references over raw conversations, credentials, or chain-of-thought. Test deletion through indexes, caches, backups, embeddings, logs, and derived features. Access to a twin does not imply access to every source.

## Sources

- NISTIR 8356: https://csrc.nist.gov/pubs/ir/8356/final
- NIST AI RMF: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- NIST AI RMF Manage playbook: https://airc.nist.gov/airmf-resources/playbook/manage/
- NIST Zero Trust Architecture: https://csrc.nist.gov/pubs/sp/800/207/final
- NIST SSDF: https://csrc.nist.gov/pubs/sp/800/218/final
- NIST Privacy Framework: https://www.nist.gov/privacy-framework
- OWASP AI Agent Security: https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
- OWASP Excessive Agency: https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
