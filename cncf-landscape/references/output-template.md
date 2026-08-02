# CNCF Landscape decision artifact

Use this structure for a substantial comparison. For a small question, keep the same evidence distinctions in a shorter response.

```markdown
# Technology shortlist: [capability]

## Decision context
- Outcome:
- Workload and interfaces:
- Deployment boundary:
- Team and operational ownership:
- Hard constraints:
- Preferences:
- Evidence date:

## Query evidence
- Source endpoint(s):
- Retrieval time / response metadata:
- Filters applied:
- Records considered:
- Important API limitations:

## Candidate comparison

| Candidate | Capability fit | Operational fit | Lifecycle/governance | Repository/license evidence | Unknowns |
|---|---|---|---|---|---|
| [name] | [observed + judgment] | [observed + judgment] | [observed + judgment] | [observed + judgment] | [gaps] |

## Recommendation

**Conditional preference:** [candidate and the constraints that make it fit]

**Alternative:** [candidate and the condition that would make it preferable]

**Excluded or deferred:** [candidate — concrete reason]

## Risks and trade-offs

- [risk] — [impact] — [mitigation or owner]

## Disproof and validation plan

1. [source check or bounded experiment]
2. [representative workload and failure-mode test]
3. [security, license, upgrade, rollback, and operations review]

## Evidence boundaries

- **Observed:** [direct API or authoritative-source facts]
- **Inferred:** [reasoned conclusions]
- **Unknown:** [questions the evidence does not answer]

## Sources

- [Landscape endpoint]
- [Project documentation]
- [Source repository]
- [License/security/governance sources]
```

Keep the raw query result available when the decision may be revisited. Do not preserve unneeded raw enrichment data from `/data/full.json`.
