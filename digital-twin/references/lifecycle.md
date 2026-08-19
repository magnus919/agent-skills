# Digital Twin: lifecycle and retirement

## Lifecycle gates

1. **Frame:** intended use, affected parties, owner, harm boundary, decision rights, simpler alternatives.
2. **Discover:** authoritative sources, identity/time/event contracts, classifications, assumptions, gaps.
3. **Bootstrap:** read-only twin, reproducible ingestion, lineage, access controls, reconciliation.
4. **Calibrate:** independent truth comparison, VVUQ, uncertainty, critical-slice tests, security/privacy/agent tests.
5. **Shadow:** recommendations without effects; measure disagreement, false confidence, escalation, and value.
6. **Authorize:** explicit action scope, policy, credentials, approval, rollback, and observability.
7. **Operate:** freshness, drift, integrity, model/agent behavior, cost, security, privacy, and outcome monitoring.
8. **Change:** revalidate after material source/schema/model/agent/tool/policy/environment/authority changes.
9. **Retire:** revoke authority, migrate consumers, preserve justified evidence, dispose of data, check orphan calls.

Every gate produces `approve`, `conditional approve`, `hold`, or `block`. Keep the decision, evidence versions, owner, and expiry/review date.

## Maintenance triggers

Revalidate after source schema/API changes; event loss, reordering, or clock changes; ownership or jurisdiction changes; model, connector, prompt, tool, policy, or environment updates; unexplained residuals; calibration or critical-slice failure; security/privacy incidents; changed workload; or a new action capability.

## Incident response

1. Detect and declare from alerts, audits, reports, or linked-twin anomalies.
2. Contain by revoking action tokens, stopping schedules, quarantining connectors/memory/models, freezing propagation, and falling back to read-only/manual mode.
3. Preserve versions, policies, provenance, event order, approvals, tool calls, external effects, and clock state without unnecessary sensitive copying.
4. Assess affected twins, artifacts, deployments, people, customers, and downstream systems.
5. Recover by rotating credentials, removing poisoned state, rebuilding from trusted provenance, reconciling external reality, testing rollback, and restoring authority gradually.
6. Learn by adding regression/adversarial cases and revising gates and authority.

Distinguish represented-system, data/twin, model, platform, policy, and agent failures. Do not call a stale or corrupted twin failure “pre-existing” without evidence.

## Decommissioning

Retire when purpose disappears, ownership is lost, risk exceeds tolerance, evidence cannot be maintained, repeated validation fails, a source/provider becomes untrustworthy, cost exceeds value, or a verified successor replaces the capability.

The retirement packet records owner approval, reason, final dependency/version inventory, consumer migration, unresolved risks, retention/legal decisions, and successor or intentional absence. Then:

- freeze new authority grants;
- disable schedulers and action endpoints;
- revoke credentials, tokens, webhooks, and tool permissions;
- sever feedback/control paths;
- migrate and verify consumers;
- export required lineage and decisions;
- delete/archive data under policy and destroy unnecessary secrets/memory;
- mark registry/endpoints retired;
- monitor and reject orphan calls;
- independently verify no live policy, agent, workflow, or twin depends on it.

## Sources

- NISTIR 8356: https://csrc.nist.gov/pubs/ir/8356/final
- NIST AI RMF Manage: https://airc.nist.gov/airmf-resources/playbook/manage/
- NIST Incident Response SP 800-61 Rev. 3: https://csrc.nist.gov/pubs/sp/800/61/r3/final
- NASA-STD-7009: https://standards.nasa.gov/standard/NASA/NASA-STD-7009
- NIST Digital Twins for Advanced Manufacturing: https://www.nist.gov/programs-projects/digital-twins-advanced-manufacturing
