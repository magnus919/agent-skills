# Evolution, Fitness Functions, And Drift

Treat architecture as a sequence of decisions exposed to change. For each important decision, identify the characteristic it protects, the boundary where violation can be observed, the evidence type, cadence, owner, threshold rationale, exception path, and retirement condition.

## Fitness evidence

Use structural checks for dependency direction or forbidden relationships, scenario tests for recovery or isolation, runtime evidence for latency or saturation, and human review for intent that cannot be mechanized. A check is not proof outside its scope. Record denominator, exclusions, missing-data behavior, and known false-positive or false-negative paths.

`adr-authoring` owns the durable decision and its link to confirmation. The project test, CI, telemetry, runtime, or governance system owns execution. Load `adr-authoring` for the ADR and fitness-function record.

## Drift loop

1. Detect a deviation or changed driver.
2. Classify it as defect, intentional exception, changed requirement, stale rule, or unknown.
3. Record impact, affected scenarios, owner, and expiry or review date.
4. Choose repair, accepted exception, decision revision, or retirement.
5. Re-run evidence and update the decision record.

Avoid metrics that can improve while architecture intent worsens. Review tails, exclusions, boundary shifts, and gaming paths. Route portfolio governance to `technology-radar` and operational telemetry to its specialist owner.

## Evolution slices

Prefer increments that preserve a selectable path, create evidence, and keep recovery legible. State what becomes irreversible, what must coexist, and what observation closes the slice. This is architecture sequencing, not migration execution.
