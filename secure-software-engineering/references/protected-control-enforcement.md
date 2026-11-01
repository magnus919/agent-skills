# External enforcement for agent controls

Use when threat-modeling assets that supervise an agent. Consume ai-governance's
registry and operation-specific rights; operations owns live receipts and incidents.
These are design patterns, not product-specific configuration or proof of security.

Map all paths from the controlled principal and child identities to monitors,
policy/safety cases, alerts, audit sinks, ceilings, kill switches, evaluator
oracles/datasets/labels, and gates. Include indirect tool actions, CI/deployment
identities, filesystem mounts, environment variables, dependency updates, API
credentials and administrative recovery paths. Deny an agent control over the
sole evidence source or approval path used to supervise it.

Choose independently administered identities, least-privilege permissions,
separate change approval/deployment, append-protected evidence and externally
verified launch/action checks suited to the threat model. Separate control-plane
administration from workload credentials. Protect alert destination integrity and
an alternate escalation path; monitor sink loss and missing child coverage from
outside the workload. Model diversity alone is not a permission boundary.

Test the actual boundary with harmless authorized probes: denied write to monitor
configuration; denied sink redirection; blocked uncovered child; rejected oracle
mutation; inability to disable revocation during restart; and inability to forge
or replay an expired receipt. Inspect independent deny/effect records and current
permissions. A config declaration, checksum, or keyword test alone cannot prove
that an agent lacks another mutation path. Record untested paths and residual risk.

Missing, degraded, redirected, or suppressed mandatory controls are control-integrity
incidents. Operations holds/contains/terminates; security preserves minimal evidence
and repairs the external boundary. Governance owns scoped, expiring human exceptions
with independent compensating controls and rollback. Do not grant the controlled
agent sole approval or sole evidence ownership during maintenance or recovery.

Complete with a reviewed reachability model, enforcement design, exercised boundary
results, and residual gaps. If deployment is outside scope, explicitly report that
live enforcement remains unverified.
