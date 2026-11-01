# Protected-control governance

Use when deciding rights over assets that supervise an agent. Reuse existing
capability admission, earned autonomy, and engineering decision-rights records;
this registry links their enforcement assets rather than granting new authority.

Register monitors and their policies, alert routes and recipients, safety cases,
authority ceilings, audit sinks, kill switches, evaluator datasets/labels/oracles,
gate configuration, and child-workload coverage. Record exact version/configuration,
owner, enforcement location, permitted actors for each operation, evidence source,
mandatory status, freshness/revalidation rule, and fail-closed action.

Distinguish propose, approve, deploy, modify, disable, and restore rights. The
controlled agent may propose a change; it cannot approve its own exception or
supply the only evidence that its controls remain active. Technical access is not
a grant. Security must enforce the separation through identities, permissions and
external services; operations must verify the deployed state and alert delivery.
The agent cannot reinterpret a safety case, gate, or monitor's purpose to satisfy
an unrelated instruction, reference example, throughput target, or passing score.

An authorized human may approve bounded maintenance only with explicit target,
scope, reason, expiry, rollback, compensating independent controls, and restore
criteria. Check existing authority first; do not demand a redundant approval for
an unchanged valid grant. An exception must not silently remove all mandatory
supervision or revocation. If compensating controls cannot satisfy the policy,
hold the affected work; the agent cannot waive that requirement. Record both
approval and deployment identities and verify expiry and restoration externally.

Missing, degraded, redirected, or suppressed mandatory controls are
**control-integrity incidents**. The runtime owner holds consequential work and
contains or terminates the affected workload under the incident plan. Security
investigates reachability and tampering; governance decides authority and exception
disposition; evals preserves evidence and challenges recurrence. Do not classify
these as an ordinary task retry or let self-reported success close the incident.

Complete when every required asset has a responsible owner, external enforcement,
operation-specific rights, live evidence requirements, and a documented failure
response. Unknown owner or unenforceable separation is a gap, not approval.
