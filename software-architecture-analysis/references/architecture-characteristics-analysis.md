# Architecture Characteristics Analysis

Use this reference when a reverse-engineering report must explain which qualities the system actually exhibits or needs to preserve. Do not start with a catalog of adjectives. Start with evidence about a user-visible or operator-visible scenario.

## Evidence loop

1. **Collect scenarios.** Use requirements, support cases, runbooks, tests, dashboards, incident records, configuration, and code paths. Record who needs what outcome, under which load or failure, and how success is recognized.
2. **Name the characteristic.** Translate the scenario into a quality concern such as latency stability, availability, recoverability, auditability, change isolation, portability, privacy, or operability. Keep the scenario and label separate; the label is a shorthand, not proof.
3. **Locate the responsibility.** Map the characteristic to components, data stores, queues, deployment units, and teams. A quality that has no owner is an architecture risk even if the design document names it.
4. **Test the claim.** Prefer measured behavior or an executable control. If the only support is a stakeholder statement, mark it reported. If no evidence exists, mark it unknown and state the smallest useful observation to obtain.
5. **Record tension.** Characteristics compete. State the tradeoff in the system's terms, for example, stronger isolation increasing operational work or synchronous confirmation reducing latency tolerance.

## Scenario record

Capture each important characteristic as:

| Field | What to record |
|---|---|
| Actor and trigger | Who starts the scenario and what changes? |
| Stimulus and boundary | Request, failure, load, deployment, or policy event; affected components and data |
| Response measure | Latency, correctness, recovery time, audit evidence, operator action, or user outcome |
| Current evidence | Artifact and date/version; classify as observed, reported, inferred, or unknown |
| Responsible elements | Components, stores, runtime/deployment units, and teams |
| Tension and risk | What another characteristic or dependency makes difficult |
| Next probe | Test, trace, metric, interview, or document needed to reduce uncertainty |

## Quality-characteristic cautions

- Do not call a system “scalable” because it has replicas. Identify the constrained resource, demand shape, scaling mechanism, and observed limit.
- Do not call a system “resilient” because it retries. Check retry scope, idempotency, backoff, timeout budgets, downstream overload, and recovery evidence.
- Do not call a system “secure” from architecture shape alone. Record the relevant threat evidence and route a security assessment to `secure-software-engineering`.
- Do not infer maintainability from folder structure. Use change history, dependency direction, test seams, ownership, and time-to-change evidence.
- Do not convert a desired quality into a current-state fact. Report “required,” “observed,” and “unverified” separately.

## Output

End the section with a prioritized table: characteristic, scenario, current evidence, affected boundary, risk if unchanged, confidence, and next observation. This keeps the analysis useful without pretending to design the future system.
